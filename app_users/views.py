from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView

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
            ('Регистрация', reverse_lazy('signup')),
        ]
        context['breadcrumbs'] = breadcrumbs

        context['title'] = 'Регистрация пользователя'

        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, user=self.object)

        return response


class UserUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm
    success_url = reverse_lazy('profile')
    template_name = 'app_users/user_update.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.object = self.request.user
            return self.render_to_response(self.get_context_data())
        else:
            raise PermissionDenied

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.object = self.request.user
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = 'Редактирование учетной записи пользователя'
        context['page_description'] = 'Вы можете изменить имя пользователя, адрес электронной почты или личные данные.'

        breadcrumbs = [
            (self.request.user.username, reverse_lazy('profile')),
            ('Редактирование учетной записи', reverse_lazy('user_update')),
        ]
        context['breadcrumbs'] = breadcrumbs

        return context


class CreateProfileView(CreateView):
    form_class = CreateProfileForm
    success_url = reverse_lazy('profile')
    template_name = 'app_users/create_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = 'Добавление профиля пользователя'

        breadcrumbs = [
            (self.request.user.username, reverse_lazy('profile')),
            ('Создание профиля', reverse_lazy('create_profile')),
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
        self.object = self.request.user.profile
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.request.user.profile
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
            (self.request.user.username, reverse_lazy('profile')),
            ('Редактирование профиля', reverse_lazy('profile_update')),
        ]
        context['breadcrumbs'] = breadcrumbs

        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    model = User
    template_name = 'app_users/profile.html'
    login_url = '/users/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        try:
            profile = Profile.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return redirect('create_profile')

        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            username = self.request.user.username
            user = User.objects.get(username=username)
            context['user'] = user
            context['owner'] = user

            social_links_form = SocialLinksForm(instance=user.profile.sociallinks)
            context['social_links_form'] = social_links_form

            primary_resume_instance = Resume.objects.filter(user=self.request.user, is_primary=True).first()
            primary_resume_select_form = PrimaryResumeSelectForm(
                user=self.request.user,
                instance=primary_resume_instance,
            )
            context['primary_resume_select_form'] = primary_resume_select_form

            context['form'] = CreateResumeForm()

            breadcrumbs = [
                (username, '/users/profile/'),
            ]
            context['breadcrumbs'] = breadcrumbs

            context['title'] = 'Профиль'

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
            ('Авторизация', reverse_lazy('login')),
        ]
        context['breadcrumbs'] = breadcrumbs

        context['title'] = 'Вход на сайт'

        return context

    def form_invalid(self, form):
        messages.warning(self.request, 'Неверное имя пользователя или пароль.')
        return super().form_invalid(form)


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





