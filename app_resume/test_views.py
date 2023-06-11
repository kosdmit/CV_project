from django.test import TestCase, RequestFactory

from django.contrib.auth.models import User
from django.urls import reverse

from app_resume.models import Resume
from app_resume.views import MainView
from app_users.models import Profile


class MainViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = MainView()
        self.user = User.objects.create_user(username=self.view.USER_TO_REDIRECT, password='testpassword')
        self.profile = Profile.objects.create(user=self.user)

    def test_redirect_when_resume_exists(self):
        Resume.objects.create(user=self.user, profile=self.profile, is_primary=True)
        request = self.factory.get('/')
        self.view.request = request

        response = self.view.dispatch(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse('primary_resume', kwargs={'username': self.view.USER_TO_REDIRECT}), response.url)

    def test_redirect_when_multiple_resumes(self):
        Resume.objects.create(user=self.user, profile=self.profile, is_primary=True, position='Python Developer')
        Resume.objects.create(user=self.user, profile=self.profile, is_primary=True, position='Java Developer')
        request = self.factory.get('/')
        self.view.request = request

        response = self.view.dispatch(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse('primary_resume', kwargs={'username': self.view.USER_TO_REDIRECT}), response.url)

    def test_redirect_when_no_resume(self):
        request = self.factory.get('/')
        self.view.request = request

        response = self.view.dispatch(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse('login'), response.url)

    def test_url_parameters(self):
        Resume.objects.create(user=self.user, profile=self.profile, is_primary=True)
        request = self.factory.get('/?param1=value1&param2=value2')
        self.view.request = request

        response = self.view.dispatch(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('primary_resume', kwargs={'username': self.view.USER_TO_REDIRECT}), response.url)
        self.assertIn('param1=value1', response.url)
        self.assertIn('param2=value2', response.url)