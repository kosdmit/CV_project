from unittest import expectedFailure
from unittest.mock import patch
from uuid import uuid4

from django.http import HttpResponseRedirect
from django.test import TestCase, RequestFactory, Client

from django.contrib.auth.models import User
from django.urls import reverse

from app_resume.models import Resume, MainEducation
from app_resume.views import MainView, ResumeView
from app_users.models import Profile, SocialLinks


def create_resume(self, *args, **kwargs):
    resume = Resume.objects.create(user=self.user, profile=self.profile,
                                   slug=str(uuid4())[:4],
                                   position=str(uuid4())[:4])
    for key, value in kwargs.items():
        resume.__setattr__(key, value)

    resume.save()
    return resume


def create_user(self, *args, **kwargs):
    self.user = User.objects.create_user(username=str(uuid4())[:4], password='testpassword')
    self.profile = Profile.objects.create(user=self.user)
    self.social_links = SocialLinks.objects.create(user=self.user, profile=self.profile)

    for key, value in kwargs.items():
        self.user.__setattr__(key, value)

    self.user.save()
    return self.user


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
        self.view = ResumeView.as_view()

        self.user = create_user(self)
        self.slug = 'test_slug'
        self.resume_with_slug = create_resume(self, slug=self.slug)
        self.resume_primary = create_resume(self, is_primary=True)
        for _ in range(3):
            create_resume(self)

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


class ResumeUpdateViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create objects
        self.user1 = create_user(self, username='kosdmit')
        self.user2 = create_user(self, username='otheruser')
        self.resume = create_resume(self,
                                    user=self.user1,
                                    position='Position1',
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


class ResumeIsPrimaryUpdateViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create objects
        self.user1 = create_user(self, username='kosdmit')
        self.user2 = create_user(self, username='otheruser')
        self.resume1 = create_resume(self, user=self.user1, is_primary=True)
        self.resume2 = create_resume(self, user=self.user1, is_primary=False)

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

        self.assertEqual(response.status_code, 404)  # Not Found


class MainEducationCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Objects
        self.user1 = create_user(self, username='kosdmit')
        self.user2 = create_user(self, username='otheruser')
        self.resume = create_resume(self, user=self.user1, slug='python-developer')

        self.url = reverse('main_education_create', kwargs={'username': self.user1.username,
                                                            'slug': self.resume.slug})
        self.referer = reverse('resume', kwargs={'username': self.user1.username,
                                                 'slug': self.resume.slug})

    @patch('django.views.generic.edit.CreateView.form_valid')
    def test_open_modal_if_success(self, mock_form_valid):
        self.client.login(username=self.user1.username, password='testpassword')
        mock_form_valid.return_value = HttpResponseRedirect(self.referer)
        response = self.client.post(self.url, {}, HTTP_REFERER=self.referer)

        self.assertEqual(response.status_code, 302)
        self.assertIn(f'?modal_id={self.resume.maineducation.pk}', response.url)
        self.assertIn(self.referer, response.url)

    def test_with_owner(self):
        self.client.login(username=self.user1.username, password='testpassword')
        response = self.client.post(self.url, {}, HTTP_REFERER=self.referer)

        main_education = MainEducation.objects.filter(resume=self.resume).all()

        self.assertEqual(response.status_code, 302)
        self.assertIn(f'?modal_id={main_education.first().pk}', response.url)
        self.assertEqual(main_education.count(), 1)

    @patch('django.views.generic.edit.CreateView.form_valid')
    def test_with_guest(self, mock_form_valid):
        self.client.login(username=self.user2.username, password='testpassword')
        mock_form_valid.return_value = HttpResponseRedirect(self.referer)
        response = self.client.post(self.url, {}, HTTP_REFERER=self.referer)

        self.assertEqual(response.status_code, 403)

    def test_updates_rating(self):
        initial_rating = self.resume.rating
        self.client.login(username=self.user1.username, password='testpassword')
        response = self.client.post(self.url, {}, HTTP_REFERER=self.referer)
        self.resume.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertGreater(self.resume.rating, initial_rating)
