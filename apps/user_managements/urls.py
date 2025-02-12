from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView

app_name = "user_managements"

urlpatterns = [
    path("retrieve-token/", TokenObtainPairView.as_view()),
]
