from uuid import uuid4

from django.contrib.auth.models import User

from django.test import Client
from django.urls import reverse

from app_resume.models import Resume
from app_users.models import Profile, SocialLinks


class CreateMethodsMixin:
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


class BaseSetUpMixin:
    def setUp(self, slug='python-developer'):
        self.client = Client()
        self.user1 = self.create_user(username='kosdmit')
        self.user2 = self.create_user(username='otheruser')
        self.resume = self.create_resume(user=self.user1, slug=slug)


class ResumeItemCreateViewTestMixin:
    def setUp(self, url_name):
        super().setUp()

        self.url = reverse(url_name, kwargs={'username': self.user1.username,
                                             'slug': self.resume.slug})

        self.referer = reverse('resume', kwargs={'username': self.user1.username,
                                                 'slug': self.resume.slug})
        self.data = {}

    def test_with_owner(self):
        self.client.login(username=self.user1.username, password='testpassword')
        response = self.client.post(self.url, self.data, HTTP_REFERER=self.referer)

        obj = self.model.objects.filter(resume=self.resume).all()

        self.assertEqual(response.status_code, 302)
        self.assertIn(f'modal_id={obj.first().pk}', response.url)
        self.assertEqual(obj.count(), 1)

    def test_with_guest(self):
        self.client.login(username=self.user2.username, password='testpassword')
        response = self.client.post(self.url, self.data, HTTP_REFERER=self.referer)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.model.objects.count(), 0)

    def test_open_modal_if_success(self):
        self.client.login(username=self.user1.username, password='testpassword')
        response = self.client.post(self.url, self.data, HTTP_REFERER=self.referer)

        obj = self.model.objects.filter(resume=self.resume).first()

        self.assertEqual(response.status_code, 302)
        self.assertIn(f'modal_id={obj.pk}', response.url)
        self.assertIn(self.referer, response.url)

    def test_updates_rating(self):
        initial_rating = self.resume.rating
        self.client.login(username=self.user1.username, password='testpassword')
        response = self.client.post(self.url, self.data, HTTP_REFERER=self.referer)
        self.resume.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertGreater(self.resume.rating, initial_rating)