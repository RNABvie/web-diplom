import re
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.cache import caches
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
import requests
from bs4 import BeautifulSoup
from . import models, serializers, tasks
import openpyxl


RamCache = caches["default"]


def tg_products():
    tasks.tgbot_products.delay()


def home(request: HttpRequest) -> HttpResponse:
    news_list = RamCache.get(f"news_list")
    if news_list is None:
        news_list = parse_news()
        RamCache.set(f"news_list", news_list, timeout=15*60)

    return render(request, "my1/home.html", {'news_list': news_list, "rooms": models.Room.objects.all()})


@swagger_auto_schema(
    method="GET",
    responses={200: 'Successful Responded-200'},
)
@login_required(login_url="log_in")
@api_view(http_method_names=["GET"])
def users(request: HttpRequest) -> HttpResponse:
    if request.user.groups.filter(name='Модераторство').exists() or request.user.is_superuser:
        if request.method == "GET":
            us_list = models.User.objects.all()
            data = serializers.UserSerializer(us_list, many=True).data
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            return Response(data={"message": "HTTP_405_METHOD_NOT_ALLOWED"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return render(request, "comps/error.html")


@login_required(login_url="log_in")
def log_out(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(reverse("home"))


def log_in(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return render(request, "my1/login.html")
    elif request.method == "POST":
        username = request.POST.get("userLog", None)
        password = request.POST.get("pwdLog", None)
        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, "my1/login.html", {"error": "Не правильные данные !"})
        login(request, user)
        return redirect(reverse("home"))
    else:
        raise ValueError("Invalid method")


def register(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return render(request, "my1/register.html")
    elif request.method == "POST":
        username = request.POST.get("userReg", None).strip()
        password = request.POST.get("pwdReg", None).strip()
        vld_name = re.match(r"[A-Za-z0-9]", username)
        vld_pwd = re.match(r"^.*(?=.{8,})(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=!.]).*$", password)
        errorname = ""
        errorpwd = ""
        if vld_pwd is None or vld_name is None:
            if vld_pwd is None:
                errorpwd = "Invalid Password format"
            if vld_name is None:
                errorname = "Invalid Username format"
            generror = "Invalid Format !"
            return render(request, "my1/register.html",
                          context={"error": str(generror), "errorName": str(errorname), "errorPwd": str(errorpwd)})

        try:
            user = User.objects.create(username=username, password=make_password(password))
        except Exception as error:
            return render(request, "my1/register.html", context={"error": str(error)})
        user = authenticate(request, username=username, password=password)
        login(request, user)
        return redirect(reverse("home"))
    else:
        raise ValueError("Invalid method")


@swagger_auto_schema(
    method="POST",
    responses={200: 'Successful Responded-200'},
    request_body=serializers.UserSerializer,
)
@login_required(login_url="log_in")
@api_view(http_method_names=["POST"])
def users_create(request: HttpRequest) -> HttpResponse:
    if request.user.groups.filter(name='Модераторство').exists() or request.user.is_superuser:
        if request.method == "POST":
            try:
                new = models.User.objects.create(
                    username=request.data['username'],
                    email=request.data['email'],
                    first_name=request.data['first_name'].capitalize(),
                    last_name=request.data['last_name'].capitalize(),
                    password=make_password('changeme+')
                )
                return Response(data={"message": "Successfully created"}, status=status.HTTP_201_CREATED)
            except Exception as error:
                return JsonResponse(data={"error": error})
        else:
            return Response(data={"message": "HTTP_405_METHOD_NOT_ALLOWED"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return render(request, "my1/error.html")


@login_required(login_url="log_in")
def vacan_create(request: HttpRequest) -> HttpResponse:
    if request.user.groups.filter(name='HR').exists() or request.user.is_superuser:
        if request.method == "GET":
            return render(request, "my1/vacan_create.html", context={"rooms": models.Room.objects.all()})
        if request.method == "POST":
            try:
                job = request.POST.get('job')
                descr = request.POST.get('description')
                contacts = request.POST.get('contacts')
                file = request.FILES.get('file', None)

                new = models.Vacan.objects.create(
                    job=job,
                    description=descr,
                    contacts=contacts,
                    file=file,
                )
                return redirect(reverse("vacancy"))
            except Exception as error:
                return render(request, "my1/vacan_create.html", context={"error": error})
        else:
            return redirect(reverse('home'))
    else:
        return redirect(reverse('home'))


@swagger_auto_schema(
    methods=["PUT", "DELETE"],
    responses={200: 'Successful Responded-200'},
    request_body=serializers.UserSerializer,
)
@login_required(login_url="log_in")
@api_view(http_method_names=["GET", "PUT", "DELETE"])
def users_pk(request: HttpRequest, pk: str) -> HttpResponse:
    if request.user.groups.filter(name='Модераторство').exists() or request.user.is_superuser:
        if request.method == "GET":
            us_obj = models.User.objects.get(id=int(pk))
            us_json = serializers.UserSerializer(us_obj, many=False).data
            return Response(data=us_json, status=status.HTTP_200_OK)
        elif request.method == "PUT":
            us_obj = models.User.objects.get(id=int(pk))
            username = str(request.data.get("username", ""))
            if username:
                us_obj.username = username

            first_name = str(request.data.get("first_name", ""))
            if first_name:
                us_obj.first_name = first_name

            last_name = str(request.data.get("last_name", ""))
            if last_name:
                us_obj.last_name = last_name

            email = str(request.data.get("email", ""))
            if email:
                us_obj.email = email

            us_obj.save()
            return Response(data={"message": "Successfully changed data"}, status=status.HTTP_200_OK)
        elif request.method == "DELETE":
            models.User.objects.get(id=int(pk)).delete()
            return Response(data={"message": "Successfully deleted"}, status=status.HTTP_200_OK)
        else:
            return Response(data={"message": "HTTP_405_METHOD_NOT_ALLOWED"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return render(request, "my1/error.html")


@login_required(login_url="log_in")
def busid(request: HttpRequest) -> HttpResponse:
    ideas = models.BusIdea.objects.filter(is_active=True)
    selected_page = request.GET.get(key="page", default=1)
    limit_post_by_page = 2
    paginator = Paginator(ideas, limit_post_by_page)
    current_page = paginator.get_page(selected_page)
    return render(request, "my1/businesIdea.html", context={"current_page": current_page, "rooms": models.Room.objects.all()})

@login_required(login_url="log_in")
def busid_create(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return render(request, "my1/idea_create.html", context={"rooms": models.Room.objects.all()})
    elif request.method == "POST":
        title = request.POST.get('title')
        descr = request.POST.get('descr')
        file = request.FILES.get('file')
        image = request.FILES.get('image')
        try:
            new = models.BusIdea.objects.create(
                author=request.user,
                title=title,
                description=descr,
                file=file,
                image=image
            )
            return redirect(reverse("business_ideas"))
        except Exception as error:
            return render(request, "my1/idea_create.html", context={"error": error})
    else:
        return redirect(reverse("busid_create"))

@login_required(login_url="log_in")
def busid_pk(request: HttpRequest, pk: str) -> HttpResponse:
    idea = RamCache.get(f"idea_{pk}")
    if idea is None:
        idea = models.BusIdea.objects.get(id=pk)
        RamCache.set(f"idea_{pk}", idea, timeout=30)
    com = models.BusIdeaCom.objects.filter(idea=idea)
    likes = models.BusIdeaLikes.objects.filter(idea=idea)
    likes = {
        "like": likes.filter(is_liked=True).count(),
        "dislike": likes.filter(is_liked=False).count(),
        "total": likes.filter(is_liked=True).count() - likes.filter(is_liked=False).count(),
    }

    return render(request, "my1/idea_detail.html",
                  context={"idea": idea, "comments": com, "likes": likes, "rooms": models.Room.objects.all()})


@login_required(login_url="log_in")
def vacan(request: HttpRequest) -> HttpResponse:
    vacancy = models.Vacan.objects.filter(is_active=True)
    return render(request, "my1/vacan.html", context={"vacancy": vacancy, "rooms": models.Room.objects.all()})


@login_required(login_url="log_in")
def vacan_pk(request: HttpRequest, pk: str) -> HttpResponse:
    vacancy_pk = RamCache.get(f"vacancy_{pk}")
    if vacancy_pk is None:
        vacancy_pk = models.Vacan.objects.get(id=pk)
        RamCache.set(f"vacancy_{pk}", vacancy_pk, timeout=300)

    return render(request, "my1/vacancy_detail.html", context={"vacan": vacancy_pk, "rooms": models.Room.objects.all()})


@login_required(login_url="log_in")
def idea_rating(request: HttpRequest, pk: str, is_like: str) -> HttpResponse:
    idea = models.BusIdea.objects.get(id=int(pk))
    is_like = True if str(is_like).lower().strip() == "лайк" else False

    ratings = models.BusIdeaLikes.objects.filter(idea=idea, author=request.user)
    if len(ratings) < 1:
        models.BusIdeaLikes.objects.create(idea=idea, author=request.user, is_liked=is_like)
    else:
        rating = ratings[0]
        if is_like is True and rating.is_liked is True:
            rating.delete()
        elif is_like is False and rating.is_liked is False:
            rating.delete()
        else:
            rating.is_liked = is_like
            rating.save()

    return redirect(reverse("business_ideas_pk", args=(pk,)))


def parse_news():
    url = 'https://www.aol.com/'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_titles = soup.select('.article-copy h3')

        return [title.text for title in news_titles]
    else:
        return []


@login_required(login_url="log_in")
def room(request, slug):
    room_obj = models.Room.objects.get(slug=slug)
    messages = models.Message.objects.filter(room=room_obj)[::-1]
    return render(
        request,
        "my1/room.html",
        context={"room": room_obj, "messages": messages}
    )


def excel_to_db(file):
    e_file = openpyxl.open(file, read_only=True)
    sheet = e_file.active
    e_list = [models.Products(product=f"{sheet[i][0].value}", amount=f"{sheet[i][2].value}") for i in range(3, 5)]
    o = models.Products.objects.bulk_create(e_list)


# excel_to_db('excel1C.xlsx')

