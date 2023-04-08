from django.contrib import admin
from django.urls import path

from .views import ProfileView, SignUpView, CreateProfileView

urlpatterns = [
    path('profile/', ProfileView.as_view()),
    path('signup/', SignUpView.as_view()),
    path('create_profile/', CreateProfileView.as_view(), name='create_profile'),
]