from django.urls import path

from .views import redirect_url_list, redirect_url_detail

app_name = "url_managements"

urlpatterns = [
    path("url/", redirect_url_list, name="redirect_rule_list"),
    path("url/<uuid:pk>/", redirect_url_detail, name="redirect_rule_detail"),
]
