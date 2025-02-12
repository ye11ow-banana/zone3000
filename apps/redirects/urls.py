from django.urls import path

from .views import access_redirect

app_name = "redirects"

urlpatterns = [
    path(
        "<str:access>/<str:redirect_identifier>/",
        access_redirect,
        name="access_redirect",
    ),
]
