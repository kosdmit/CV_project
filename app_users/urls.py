from django.contrib import admin
from django.urls import path

from .views import ProfileView, SignUpView, CreateProfileView, Login, Logout, ProfileUpdateView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('create_profile/', CreateProfileView.as_view(), name='create_profile'),
    path('profile_update/', ProfileUpdateView.as_view(), name='profile_update')
]