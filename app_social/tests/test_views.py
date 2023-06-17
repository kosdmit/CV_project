from django.contrib.messages import get_messages
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from CV_project.settings import RATING_SETTINGS
from app_resume.tests.test_mixins import CreateMethodsMixin
from app_social.models import Like, Comment


class ClickLikeViewTests(CreateMethodsMixin, TestCase):
    def setUp(self):
        self.client = Client()

        self.user = self.create_user(username='kosdmit')
        self.resume = self.create_resume()

        self.data = {'pk': self.resume.pk}


    def test_like_not_exist_with_authenticated_user(self):
        self.client.login(username='kosdmit', password='testpassword')

        initial_likes_count = Like.objects.filter(uuid_key=self.data['pk']).count()

        response = self.client.post(reverse('click_like'),
                                    self.data,
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Like.objects.filter(owner_id=self.user.pk, uuid_key=self.data['pk']).exists())

        # Check the response data
        response_data = response.json()
        self.assertEqual(response_data['is_liked'], True)
        self.assertEqual(response_data['likes_count'] - initial_likes_count, 1)

    def test_like_exist_with_authenticated_user(self):
        self.client.login(username='kosdmit', password='testpassword')
        Like.objects.create(owner_id=self.user.pk, uuid_key=self.data['pk'])

        initial_likes_count = Like.objects.filter(uuid_key=self.data['pk']).count()

        response = self.client.post(reverse('click_like'),
                                    self.data,
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Like.objects.filter(owner_id=self.user.pk, uuid_key=self.data['pk']).exists())

        # Check the response data
        response_data = response.json()
        self.assertEqual(response_data['is_liked'], False)
        self.assertEqual(response_data['likes_count'] - initial_likes_count, -1)

    def test_like_not_exist_with_anonymous_user(self):
        session_id = self.client.session._session_key
        initial_likes_count = Like.objects.filter(uuid_key=self.data['pk']).count()
        response = self.client.post(reverse('click_like'),
                                    self.data,
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Like.objects.filter(owner_id=session_id, uuid_key=self.data['pk']).exists())

        # Check the response data
        response_data = response.json()
        self.assertEqual(response_data['is_liked'], True)
        self.assertEqual(response_data['likes_count'] - initial_likes_count, 1)

    def test_like_exist_with_anonymous_user(self):
        session_id = self.client.session._session_key
        Like.objects.create(owner_id=session_id, uuid_key=self.data['pk'])
        initial_likes_count = Like.objects.filter(uuid_key=self.data['pk']).count()
        response = self.client.post(reverse('click_like'),
                                    self.data,
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)


        self.assertFalse(Like.objects.filter(owner_id=session_id, uuid_key=self.data['pk']).exists())

        # Check the response data
        response_data = response.json()
        self.assertEqual(response_data['is_liked'], False)
        self.assertEqual(response_data['likes_count'] - initial_likes_count, -1)


class CommentCreateViewTests(CreateMethodsMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.user = self.create_user(username='kosdmit')
        self.resume = self.create_resume()
        self.data = {'message': 'This is a test comment'}
        self.referer = reverse('resume_list')

    def test_with_authenticated_user(self):
        self.client.login(username='kosdmit', password='testpassword')

        initial_resume_rating = self.resume.rating
        response = self.client.post(reverse('comment_create', kwargs={'pk': self.resume.pk}),
                                    self.data,
                                    HTTP_REFERER=self.referer)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(owner_id=self.user.pk,
                                               uuid_key=self.resume.pk,
                                               message='This is a test comment',
                                               is_approved=True).exists())

        self.assertIn(f'modal_id=comments-{self.resume.pk}', response.url)

        # Check that the resume rating was updated
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.rating - initial_resume_rating, RATING_SETTINGS['comment'])

    def test_with_anonymous_user(self):
        initial_resume_rating = self.resume.rating
        session_id = self.client.session._session_key
        response = self.client.post(reverse('comment_create', kwargs={'pk': self.resume.pk}),
                                    self.data,
                                    HTTP_REFERER=self.referer)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(owner_id=session_id,
                                               uuid_key=self.resume.pk,
                                               message='This is a test comment',
                                               is_approved=False).exists())

        self.assertIn(f'modal_id=comments-{self.resume.pk}', response.url)

        # Check that the resume rating was updated
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.rating - initial_resume_rating, RATING_SETTINGS['comment'])

        # Check the messages
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Ваше сообщение появится после проверки администратором.'
                                            f' <a href="{reverse("signup")}">Зарегистрируйтесь</a>, чтобы сообщения появлялись сразу.')