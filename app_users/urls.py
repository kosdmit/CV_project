from django.contrib import admin
from django.urls import path

from .views import ProfileView, SignUpView

urlpatterns = [
    path('profile/', ProfileView.as_view()),
    path('signup/', SignUpView.as_view())
]