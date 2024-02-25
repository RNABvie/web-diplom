from django.urls import path, re_path
from . import views, views_aws
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView, TokenRefreshView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

websocket_urlpatterns = [
    path('ws/<slug:room_name>/', views_aws.ChatConsumer.as_asgi()),
]

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.IsAuthenticated,),
)

urlpatterns = [
    path("api/swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("api/swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),

    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/users/', views.users, name="users"),
    path('api/users/create/', views.users_create, name="users_create"),
    re_path(r'^api/users/(?P<pk>\d+)/$', views.users_pk, name="user_pk"),

    path("", views.home, name="home"),
    path("login/", views.log_in, name="log_in"),
    path("logout/", views.log_out, name="log_out"),
    path("register/", views.register, name="register"),
    path('business_ideas/', views.busid, name="business_ideas"),
    re_path(r'^business_ideas/(?P<pk>\d+)/$', views.busid_pk, name="business_ideas_pk"),
    re_path(r'^business_ideas/create/$', views.busid_create, name="busid_create"),
    path("business_ideas/<str:pk>/<str:is_like>/", views.idea_rating, name="idea_rating"),#########
    path('vacancy/', views.vacan, name="vacancy"),
    path('vacancy/create/', views.vacan_create, name="vacan_create"),
    re_path(r'^vacancy/(?P<pk>\d+)/$', views.vacan_pk, name="vacancy_pk"),

    path('<slug:slug>/', views.room, name="room"),
]
