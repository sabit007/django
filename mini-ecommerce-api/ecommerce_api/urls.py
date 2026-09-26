from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("shop.urls")),
    # POST username + password here to receive an auth token
    path("api/login/", obtain_auth_token, name="api-login"),
]
