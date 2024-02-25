from django import template
from django.http import HttpRequest
from ..models import BusIdea, BusIdeaLikes, BusIdeaCom

register = template.Library()


@register.simple_tag(takes_context=True)
def i_liked_idea(context: str, idea_pk: str) -> int:
    try:
        request: HttpRequest = context["request"]
        idea = BusIdea.objects.get(id=int(idea_pk))
        ratings = BusIdeaLikes.objects.filter(idea=idea, author=request.user)
        if len(ratings) < 1:
            return 0
        else:
            rating = ratings[0]
            if rating.is_liked:
                return 1
            return -1
    except Exception as error:
        print("error simple_tag i_liked_idea: ", error)
        return 0