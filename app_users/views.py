from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, CreateView
from app_users.models import Profile, SocialLinks
from .forms import SignUpUserForm, CreateProfileForm
from django.contrib.auth.models import User

from django.shortcuts import render, redirect


# Create your views here.
class SignUpView(CreateView):
    form_class = SignUpUserForm
    success_url = reverse_lazy('create_profile')
    template_name = 'app_users/signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        breadcrumbs = [
            ('Пользователь', 'users/'),
            ('Регистрация', 'users/signup/'),
        ]
        context['breadcrumbs'] = breadcrumbs

        return context


class CreateProfileView(CreateView):
    form_class = CreateProfileForm
    success_url = reverse_lazy('profile')
    template_name = 'app_users/create_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        breadcrumbs = [
            ('Пользователь', 'users/'),
            ('Создание профиля', 'users/create_profile/'),
        ]
        context['breadcrumbs'] = breadcrumbs

        return context

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class ProfileView(TemplateView):
    model = User
    template_name = 'app_users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        breadcrumbs = [
            ('Пользователь', 'users/'),
            ('Профиль', 'users/profile/'),
        ]
        context['breadcrumbs'] = breadcrumbs

        if self.request.user.is_authenticated:
            username = self.request.user.username
            user = User.objects.get(username=username)
            context['user'] = user

            profile = Profile.objects.filter(user=self.request.user).first()
            context['profile'] = profile

            social_links = SocialLinks.objects.filter(profile=profile)
            context['social_links'] = social_links

        return context