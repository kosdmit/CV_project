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

        obj_set = self.model.objects.filter(resume=self.resume).all()

        self.assertEqual(response.status_code, 302)
        self.assertIn(f'modal_id={obj_set.first().pk}', response.url)
        self.assertEqual(obj_set.count(), 1)

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


class ResumeItemUpdateViewTestMixin:
    def setUp(self, url_name, *args, **kwargs):
        super().setUp()
        self.object = self.model.objects.create(resume=self.resume, **kwargs)
        self.url = reverse(url_name, kwargs={'pk': self.object.pk,
                                             'username': self.user1.username,
                                             'slug': self.resume.slug})

        self.referer = reverse('resume', kwargs={'username': self.user1.username,
                                                 'slug': self.resume.slug}) \
            + '?modal_id=' + str(self.object.pk)

    def test_with_owner(self):
        self.client.login(username=self.user1.username, password='testpassword')
        response = self.client.post(self.url, self.data, HTTP_REFERER=self.referer)
        self.object.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('modal_id=', response.url)
        for key in self.data:
            self.assertEqual(self.object.__getattribute__(key), self.data[key])

    def test_with_guest(self):
        self.client.login(username=self.user2.username, password='testpassword')
        response = self.client.post(self.url, self.data, HTTP_REFERER=self.referer)

        self.assertEqual(response.status_code, 403)


class ResumeItemDeleteViewTestMixin:
    def setUp(self, url_name, **kwargs):
        super().setUp()

        self.object = self.model.objects.create(resume=self.resume, **kwargs)
        for _ in range(3):
            self.model.objects.create(resume=self.resume, title=str(uuid4())[:4], **kwargs)

        self.url = reverse(url_name, kwargs={'pk': self.object.pk,
                                             'username': self.user1.username,
                                             'slug': self.resume.slug})

        self.referer = reverse('resume', kwargs={'username': self.user1.username,
                                                 'slug': self.resume.slug})
        self.data = {}



    def test_model(self):
        self.assertEqual(self.view.model, self.model)

    def test_with_owner(self):
        self.client.login(username=self.user1.username, password='testpassword')

        obj_count_before = self.model.objects.count()
        response = self.client.post(self.url, self.data, HTTP_REFERER=self.referer)
        obj_count_after = self.model.objects.count()

        self.assertEqual(response.status_code, 302)
        self.assertNotIn('modal_id=', response.url)
        self.assertEqual(obj_count_before - obj_count_after, 1)
        with self.assertRaises(self.model.DoesNotExist):
            self.model.objects.get(resume=self.resume, title='New Object')


    def test_updates_rating(self):
        self.client.login(username=self.user1.username, password='testpassword')
        initial_rating = self.resume.rating
        response = self.client.post(self.url, self.data, HTTP_REFERER=self.referer)
        self.resume.refresh_from_db()

        self.assertLess(self.resume.rating, initial_rating)

    def test_with_guest(self):
        self.client.login(username=self.user2.username, password='testpassword')
        response = self.client.post(self.url, self.data, HTTP_REFERER=self.referer)

        self.assertEqual(response.status_code, 403)
