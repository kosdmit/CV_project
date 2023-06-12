from uuid import uuid4
from django.test import TestCase, RequestFactory

from django.contrib.auth.models import User
from django.urls import reverse

from app_resume.models import Resume
from app_resume.views import MainView, ResumeView
from app_users.models import Profile, SocialLinks


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


class ResumeViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='kosdmit', password='testpassword')
        self.profile = Profile.objects.create(user=self.user)
        self.social_links = SocialLinks.objects.create(user=self.user, profile=self.profile)
        self.view = ResumeView.as_view()

    def setUpOwner(self):
        pass

    def setUpGuest(self):
        pass

    def create_resume(self, *args, **kwargs):
        resume = Resume.objects.create(user=self.user, profile=self.profile, slug=str(uuid4())[:4], position=str(uuid4())[:4])
        for key, value in kwargs.items():
            resume.__setattr__(key, value)

        resume.save()
        return resume

    def test_context_for_owner_with_slug(self):
        slug = 'test_slug'

        resume = self.create_resume(slug=slug)
        for _ in range(3):
            self.create_resume()

        request = self.factory.get(f'/{self.user.username}/{slug}/')
        request.user = self.user

        response = self.view(request, slug=slug, username=self.user.username)
        context = response.context_data

        self.assertEqual(context['owner'], self.user)
        self.assertEqual(context['resume'], resume)
        self.assertTrue('resume_position_form' in context)
        self.assertFalse('job_update_form' in context)
        self.assertEqual(context['breadcrumbs'][0][1], reverse('profile'))

    def test_context_for_guest_with_slug(self):
        slug = 'test_slug'

        resume = self.create_resume(slug=slug)
        for _ in range(3):
            self.create_resume()

        request = self.factory.get(f'/{self.user.username}/{slug}/')

        guest = User.objects.create(username='guest', password='testpassword')
        request.user = guest

        response = self.view(request, slug=slug, username=self.user.username)
        context = response.context_data

        self.assertEqual(context['owner'], self.user)
        self.assertEqual(context['resume'], resume)
        self.assertTrue('resume_position_form' not in context)
        self.assertFalse('job_update_form' in context)
        self.assertEqual(context['breadcrumbs'][0][1], None)
