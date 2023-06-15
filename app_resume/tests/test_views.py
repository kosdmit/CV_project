from unittest import expectedFailure
from unittest.mock import patch, Mock
from uuid import uuid4

from django.http import HttpResponseRedirect
from django.test import TestCase, RequestFactory, Client

from django.contrib.auth.models import User
from django.urls import reverse

from app_resume.models import Resume, MainEducation, Institution
from app_resume.tests.test_mixins import CreateMethodsMixin, BaseSetUpMixin, \
    ResumeItemCreateViewTestMixin, ResumeItemUpdateViewTestMixin
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


class ResumeViewTest(CreateMethodsMixin, TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = ResumeView.as_view()

        self.user = self.create_user()
        self.slug = 'test_slug'
        self.resume_with_slug = self.create_resume(slug=self.slug)
        self.resume_primary = self.create_resume(is_primary=True)
        for _ in range(3):
            self.create_resume()

    def test_context_for_owner_with_slug(self):
        request = self.factory.get(f'/{self.user.username}/{self.slug}/')
        request.user = self.user

        response = self.view(request, slug=self.slug, username=self.user.username)
        context = response.context_data


        self.assertEqual(context['owner'], self.user)
        self.assertEqual(context['resume'], self.resume_with_slug)
        self.assertTrue('resume_position_form' in context)

        self.assertFalse('institution_create_form' in context)
        self.assertFalse('job_create_form' in context)

        self.assertEqual(context['breadcrumbs'][0][1], reverse('profile'))

    def test_context_for_guest_with_slug(self):
        request = self.factory.get(f'/{self.user.username}/{self.slug}/')

        guest = User.objects.create(username='guest', password='testpassword')
        request.user = guest

        response = self.view(request, slug=self.slug, username=self.user.username)
        context = response.context_data


        self.assertEqual(context['owner'], self.user)
        self.assertEqual(context['resume'], self.resume_with_slug)
        self.assertTrue('resume_position_form' not in context)

        self.assertFalse('institution_create_form' in context)
        self.assertFalse('job_create_form' in context)

        self.assertEqual(context['breadcrumbs'][0][1], None)

    def test_context_for_owner_without_slug(self):
        request = self.factory.get(f'/{self.user.username}/')
        request.user = self.user

        response = self.view(request, username=self.user.username)
        context = response.context_data


        self.assertEqual(context['owner'], self.user)
        self.assertEqual(context['resume'], self.resume_primary)
        self.assertTrue('resume_position_form' in context)

        self.assertFalse('institution_create_form' in context)
        self.assertFalse('job_create_form' in context)

        self.assertEqual(context['breadcrumbs'][0][1], reverse('profile'))

    def test_context_for_guest_without_slug(self):
        request = self.factory.get(f'/{self.user.username}/')

        guest = User.objects.create(username='guest', password='testpassword')
        request.user = guest

        response = self.view(request, username=self.user.username)
        context = response.context_data


        self.assertEqual(context['owner'], self.user)
        self.assertEqual(context['resume'], self.resume_primary)
        self.assertTrue('resume_position_form' not in context)

        self.assertFalse('institution_create_form' in context)
        self.assertFalse('job_create_form' in context)

        self.assertEqual(context['breadcrumbs'][0][1], None)

    @expectedFailure
    def test_context_data_with_wrong_slug(self):
        slug = 'wrong-slug'
        request = self.factory.get(f'/{self.user.username}/{slug}/')
        response = self.view(request, username=self.user.username, slug=slug)

        self.assertEqual(response.status_code, '404')


class ResumeUpdateViewTest(BaseSetUpMixin, CreateMethodsMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.resume = self.create_resume(user=self.user1, position='Position1',
                                         about_me='AboutMe1')

    def test_form_valid_with_owner(self):
        self.client.login(username='kosdmit', password='testpassword')
        response = self.client.post(
            reverse('resume_update', kwargs={'username': self.user1.username,
                                             'slug': self.resume.slug}),
            {'position': 'New Position'},
            HTTP_REFERER=reverse('resume', kwargs={'username': self.user1.username,
                                                   'slug': self.resume.slug})
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Resume.objects.get(pk=self.resume.pk).position, 'New Position')
        self.assertEqual(Resume.objects.get(pk=self.resume.pk).about_me, 'AboutMe1')

    def test_form_valid_with_not_owner(self):
        self.client.login(username='otheruser', password='testpassword')
        response = self.client.post(
            reverse('resume_update', kwargs={'username': self.user1.username,
                                             'slug': self.resume.slug}),
            {'position': 'New Position'},
            HTTP_REFERER=reverse('resume', kwargs={'username': self.user1.username,
                                                   'slug': self.resume.slug})
        )

        self.assertEqual(response.status_code, 403)  # Permission Denied
        self.assertEqual(Resume.objects.get(pk=self.resume.pk).position, 'Position1')

    def test_get_success_url(self):
        self.client.login(username='kosdmit', password='testpassword')
        response = self.client.post(
            reverse('resume_update', kwargs={'username': self.user1.username,
                                                      'slug': self.resume.slug}),
            {'position': 'New Position'},
            HTTP_REFERER=reverse('resume', kwargs={'username': self.user1.username,
                                                   'slug': self.resume.slug}) + '?modal_id=123'
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('resume', kwargs={'username': self.user1.username,
                                                   'slug': self.resume.slug}))


class ResumeIsPrimaryUpdateViewTest(BaseSetUpMixin, CreateMethodsMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.resume1 = self.create_resume(user=self.user1, is_primary=True)
        self.resume2 = self.create_resume(user=self.user1, is_primary=False)

        self.url = reverse('resume_is_primary_update', kwargs={'username': self.user1.username})


    def test_with_owner(self):
        self.client.login(username='kosdmit', password='testpassword')
        response = self.client.post(self.url, {'is_primary': self.resume2.pk},
                                    HTTP_REFERER=reverse('profile'))

        self.resume1.refresh_from_db()
        self.resume2.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.resume1.is_primary, False)
        self.assertEqual(self.resume2.is_primary, True)

    def test_with_guest(self):
        self.client.login(username='otheruser', password='testpassword')
        response = self.client.post(self.url, {'is_primary': self.resume2.pk},
                                    HTTP_REFERER=reverse('profile'))

        self.resume1.refresh_from_db()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.resume1.is_primary, True)
        self.assertEqual(self.resume2.is_primary, False)

    def test_with_invalid_resume_id(self):
        self.client.login(username='kosdmit', password='testpassword')
        response = self.client.post(self.url, {'is_primary': 'invalid_id'})

        self.assertEqual(response.status_code, 404)


class MainEducationCreateViewTest(ResumeItemCreateViewTestMixin,
                                  BaseSetUpMixin,
                                  CreateMethodsMixin,
                                  TestCase):
    def setUp(self):
        super().setUp(url_name='main_education_create')
        self.model = MainEducation


class MainEducationUpdateViewTest(ResumeItemUpdateViewTestMixin,
                                  BaseSetUpMixin,
                                  CreateMethodsMixin,
                                  TestCase):
    def setUp(self):
        self.model = MainEducation
        self.data = {
            'level': 'Higher education',
            'degree': 'Master'
        }
        super().setUp(url_name='main_education_update')


class TestInstitutionCreateView(ResumeItemCreateViewTestMixin,
                                BaseSetUpMixin,
                                CreateMethodsMixin,
                                TestCase):
    def setUp(self):
        super().setUp('institution_create')
        self.main_education1 = MainEducation.objects.create(resume=self.resume)
        self.model = Institution


class InstitutionUpdateViewTest(BaseSetUpMixin,
                                ResumeItemUpdateViewTestMixin,
                                CreateMethodsMixin,
                                TestCase):
    def setUp(self):
        self.model = Institution
        self.data = {
            'title': 'New title',
            'description': 'New description'
        }
        super().setUp()
        main_education = MainEducation.objects.create(resume=self.resume)
        ResumeItemUpdateViewTestMixin.setUp(self, url_name='institution_update', main_education=main_education)
