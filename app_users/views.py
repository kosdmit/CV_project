import uuid

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, CreateView, UpdateView

import app_users
from app_resume.models import Resume
from app_users.models import Profile, SocialLinks
from .forms import SignUpUserForm, CreateProfileForm, CustomAuthenticationForm, CreateResumeForm, \
    PrimaryResumeSelectForm, UserUpdateForm, SocialLinksForm
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


class UserUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm
    success_url = reverse_lazy('profile')
    template_name = 'app_users/user_update.html'

    def get(self, request, *args, **kwargs):
        self.object = User.objects.get(pk=self.request.user.pk)
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = User.objects.get(pk=self.request.user.pk)
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['page_title'] = 'Редактирование учетной записи пользователя'
        context['page_description'] = 'Вы можете изменить имя пользователя, адрес электронной почты или личные данные.'

        breadcrumbs = [
            ('Пользователь', '/users/'),
            ('Редактирование учетной записи', '/users/user_update/'),
        ]
        context['breadcrumbs'] = breadcrumbs

        return context


class CreateProfileView(CreateView):
    form_class = CreateProfileForm
    success_url = reverse_lazy('profile')
    template_name = 'app_users/create_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['page_title'] = 'Добавление профиля пользователя'
        context['page_description'] = 'Перед тем как перейти к созданию резюме, расскажите немного о себе.'

        breadcrumbs = [
            ('Пользователь', '/users/'),
            ('Создание профиля', '/users/create_profile/'),
        ]
        context['breadcrumbs'] = breadcrumbs

        return context

    def form_valid(self, form):
        # Bound user and save Profile object
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        # create SocialLink object
        social_links_form = SocialLinksForm()
        social_links = social_links_form.save(commit=False)
        social_links.profile = self.object
        social_links.user = self.request.user
        social_links.save()

        return super().form_valid(form)


class ProfileUpdateView(UpdateView):
    model = Profile
    form_class = CreateProfileForm
    success_url = reverse_lazy('profile')
    template_name = 'app_users/create_profile.html'

    def get(self, request, *args, **kwargs):
        self.object = Profile.objects.get(user=self.request.user)
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = Profile.objects.get(user=self.request.user)
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['page_title'] = 'Редактирование профиля пользователя'
        context['page_description'] = 'Добавьте недостающие данные профиля.'

        breadcrumbs = [
            ('Пользователь', '/users/'),
            ('Редактирование профиля', '/users/profile_update/'),
        ]
        context['breadcrumbs'] = breadcrumbs

        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    model = User
    template_name = 'app_users/profile.html'
    login_url = '/users/login/'

    def dispatch(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return redirect('create_profile')

        return super().dispatch(request, *args, **kwargs)


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

            social_links = SocialLinks.objects.filter(profile=profile).first()
            context['social_links'] = social_links

            social_links_form = SocialLinksForm(instance=social_links)
            context['social_links_form'] = social_links_form

            resume_list = Resume.objects.filter(profile=profile)
            context['resume_list'] = resume_list

            primary_resume_instance = Resume.objects.filter(user=self.request.user, is_primary=True).first()
            primary_resume_select_form = PrimaryResumeSelectForm(
                user=self.request.user,
                instance=primary_resume_instance,
            )
            context['primary_resume_select_form'] = primary_resume_select_form

            create_resume_form = CreateResumeForm()
            context['form'] = create_resume_form

        return context

    def post(self, request, *args, **kwargs):
        create_resume_form = CreateResumeForm(request.POST)
        if create_resume_form.is_valid():
            resume = create_resume_form.save(commit=False)
            resume.profile_id = Profile.objects.get(user=self.request.user).id
            resume.user_id = self.request.user.id
            if not Resume.objects.filter(user=self.request.user, is_primary=True).first():
                resume.is_primary = True
            resume.save()
            return redirect('profile')
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = create_resume_form
            return render(request, self.template_name, context)


class Login(LoginView):
    template_name = 'app_users/login.html'
    next_page = 'profile'
    form_class = CustomAuthenticationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        breadcrumbs = [
            ('Пользователь', 'users/'),
            ('Вход', 'users/login/'),
        ]
        context['breadcrumbs'] = breadcrumbs

        return context


class Logout(LogoutView):
    next_page = 'main'


class SocialLinksUpdateView(UpdateView):
    model = SocialLinks
    fields = ['twitter', 'facebook', 'linked_in', 'vk', 'instagram', 'hh', 'git_hub']

    def post(self, request, *args, **kwargs):
        self.success_url = self.request.META['HTTP_REFERER']

        self.object = SocialLinks.objects.get(user=self.request.user)

        for key in self.request.POST:
            if key in self.fields:
                setattr(self.object, key, self.request.POST[key])
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())





