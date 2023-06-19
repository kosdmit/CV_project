from types import NoneType
from unittest import expectedFailure

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from app_resume.models import Resume
from app_users.forms import SignUpUserForm, UserUpdateForm, CreateProfileForm, \
    CreateResumeForm, CustomAuthenticationForm
from app_users.models import Profile, SocialLinks
from app_users.tests.test_mixins import BaseTestMixin


class SignUpViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('signup')
        self.model = get_user_model()
        self.title = 'Регистрация пользователя'
        self.breadcrumbs_title = 'Регистрация'


    def test_get_with_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertIsInstance(response.context['form'], SignUpUserForm)

        self.assertEqual(response.context['title'], self.title)
        self.assertEqual(response.context['breadcrumbs'], [(self.breadcrumbs_title, self.url)])

    def test_post_correct_data_with_anonymous_user(self):
        data = {'username': 'newuser',
                'email': 'kosdmit@hotmail.com',
                'password1': 'testpassword',
                'password2': 'testpassword'}

        response = self.client.post(self.url, data=data)
        user = self.model.objects.filter(username=data['username']).first()

        self.assertIsNotNone(user)

        # Test that the user is authenticated
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

        # Test that the user was redirected to the success_url
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('create_profile'))

    def test_post_invalid_data_with_anonymous_user(self):
        data = {'username': 'newuser',
                'email': 'kosdmit@hotmail.com',
                'password1': 't',
                'password2': 't'}

        response = self.client.post(self.url, data=data, follow=True)
        user = self.model.objects.filter(username=data['username']).first()


        self.assertIsNone(user)

        # Test that the user is not authenticated
        self.assertNotIn('_auth_user_id', self.client.session)

        # Test that the form is invalid and the page wasn't redirected
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertTrue(response.context['form'].errors)


class UserUpdateViewTest(BaseTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('user_update')
        self.referer = reverse('profile')
        self.model = get_user_model()
        self.title = 'Редактирование учетной записи пользователя'
        self.breadcrumbs_title = 'Редактирование учетной записи'
        self.form = UserUpdateForm
        self.user = get_user_model().objects.create_user(username='kosdmit', password='testpassword')
        self.correct_data = {'username': 'updateduser',
                             'first_name': 'updatedname',
                             'last_name': 'updatedname',
                             'email': 'updated@email.com',
                             }

        self.invalid_data = {'username': '',
                             'first_name': 'updatedname',
                             'last_name': 'updatedname',
                             'email': 'updated@email.com',
                             }


class CreateProfileViewTest(BaseTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('create_profile')
        self.referer = reverse('signup')
        self.model = Profile
        self.title = 'Добавление профиля пользователя'
        self.breadcrumbs_title = 'Создание профиля'
        self.form = CreateProfileForm
        self.user = get_user_model().objects.create_user(username='kosdmit', password='testpassword')
        self.correct_data = {'gender': 'F',
                             'phone_number': '+79277535560'}

        self.invalid_data = {'gender': 'A',
                             'phone_number': '9277535560'}


class ProfileUpdateViewTest(BaseTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('profile_update')
        self.referer = reverse('profile')
        self.model = Profile
        self.title = 'Редактирование профиля пользователя'
        self.breadcrumbs_title = 'Редактирование профиля'
        self.form = CreateProfileForm
        self.user = get_user_model().objects.create_user(username='kosdmit', password='testpassword')
        self.correct_data = {'gender': 'F',
                             'phone_number': '+79277535560'}

        self.invalid_data = {'gender': 'A',
                             'phone_number': '9277535560'}

        self.object = self.model.objects.create(user=self.user)


class ProfileViewTest(BaseTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('profile')
        self.referer = reverse('main')
        self.model = Resume
        self.title = 'Профиль'
        self.form = CreateResumeForm
        self.user = get_user_model().objects.create_user(username='kosdmit', password='testpassword')
        self.breadcrumbs_title = self.user.username
        self.correct_data = {'position': 'Python Developer'}

        self.invalid_data = {'position': ''}

        self.profile = Profile.objects.create(user=self.user)
        social_links = SocialLinks.objects.create(user=self.user, profile=self.profile)
        self.object = self.model.objects.create(user=self.user, profile=self.profile, position='init_position')

    def test_get_without_profile_authorized_user(self):
        self.profile.delete()
        self.client.login(username=self.user.username, password='testpassword')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('create_profile'))

    def test_post_without_profile_authorized_user(self):
        self.profile.delete()
        self.client.login(username=self.user.username, password='testpassword')

        response = self.client.post(self.url, self.correct_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('create_profile'))


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login')
        self.title = 'Вход на сайт'
        self.breadcrumbs_title = 'Авторизация'

    def test_get_with_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_users/login.html')
        self.assertListEqual(response.context_data['breadcrumbs'], [('Авторизация', self.url)])
        self.assertEqual(response.context_data['title'], self.title)
        self.assertEqual(response.context_data['form'].__class__, CustomAuthenticationForm)

    def test_post_invalid_data_with_anonymous_user(self):
        response = self.client.post(self.url, {'username': 'wronguser', 'password': 'wrongpass'})
        messages = list(response.context['messages'])
        self.assertGreater(len(messages), 0)
        self.assertEqual(str(messages[0]), 'Неверное имя пользователя или пароль.')
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        user = get_user_model().objects.create_user(username='kosdmit', password='testpassword')
        response = self.client.post(self.url, {'username': user.username, 'password': 'testpassword'})
        self.assertRedirects(response, reverse('profile'), fetch_redirect_response=False)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)


class SocialLinksUpdateViewTest(BaseTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('social_links_update')
        self.referer = reverse('profile')
        self.model = SocialLinks
        self.title = None
        self.form = None
        self.user = get_user_model().objects.create_user(username='kosdmit', password='testpassword')
        self.breadcrumbs_title = None
        self.correct_data = {'vk': 'https://vk.com/kosdmit',
                             'git_hub': 'https://github.com/kosdmit'}

        self.invalid_data = {'vk': 'vkcom/kosdmit',
                             'git_hub': 'githubcom/kosdmit'}

        self.profile = Profile.objects.create(user=self.user)
        self.object = SocialLinks.objects.create(user=self.user, profile=self.profile)

    def test_get_with_authorized_user(self):
        self.client.login(username=self.user.username, password='testpassword')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    @expectedFailure
    def test_post_invalid_data_with_authenticated_user(self):
        super().test_post_invalid_data_with_authenticated_user()




