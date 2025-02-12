from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("user_managements.urls")),
    path("", include("url_managements.urls")),
    path("", include("redirects.urls")),
]
