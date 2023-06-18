from django.contrib.messages import get_messages
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from CV_project.settings import RATING_SETTINGS
from app_resume.tests.test_mixins import CreateMethodsMixin
from app_social.forms import CommentForm
from app_social.models import Like, Comment, Post
from app_social.tests.test_mixins import BaseSetUpMixin, CommentTestMixin, \
    ListViewTestMixin


class ClickLikeViewTests(BaseSetUpMixin, CreateMethodsMixin, TestCase):
    def setUp(self):
        super().setUp()
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


class CommentCreateViewTests(BaseSetUpMixin, CreateMethodsMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('comment_create', kwargs={'pk': self.resume.pk})
        self.referer = reverse('resume_list')
        self.data = {'message': 'This is a test comment'}

    def test_with_authenticated_user(self):
        self.client.login(username=self.user.username, password='testpassword')

        self.response = self.client.post(self.url, self.data,
                                         HTTP_REFERER=self.referer)

        self.assertEqual(self.response.status_code, 302)
        self.assertIn(f'modal_id=comments-{self.resume.pk}', self.response.url)

        # Check that the resume rating was updated
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.rating - self.initial_resume_rating, RATING_SETTINGS['comment'])

        self.assertTrue(Comment.objects.filter(owner_id=self.user.pk,
                                               uuid_key=self.resume.pk,
                                               message='This is a test comment',
                                               is_approved=True).exists())

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


class CommentDeleteViewTests(CommentTestMixin,
                             BaseSetUpMixin,
                             CreateMethodsMixin,
                             TestCase):
    def setUp(self):
        super().setUp(url_name='comment_delete')
        self.data = {}

    def test_with_authenticated_user(self):
        super().test_with_authenticated_user()

        # Check that the resume rating was updated
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.rating - self.initial_resume_rating, -RATING_SETTINGS['comment'])

        self.assertFalse(Comment.objects.filter(pk=self.object.pk).exists())
        self.assertRedirects(self.response, self.referer, fetch_redirect_response=False)

    def test_with_anonymous_user(self):
        super().test_with_anonymous_user(url_name='comment_delete')

        # Check that the resume rating was updated
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.rating - self.initial_resume_rating, -RATING_SETTINGS['comment'])

        self.assertFalse(Comment.objects.filter(pk=self.object.pk).exists())

    def test_with_wrong_anonymous_user(self):
        super().test_with_wrong_anonymous_user(url_name='comment_delete')

    def test_with_wrong_authenticated_user(self):
        super().test_with_wrong_authenticated_user(url_name='comment_delete')


class CommentUpdateViewTests(CommentTestMixin,
                             BaseSetUpMixin,
                             CreateMethodsMixin,
                             TestCase):
    def setUp(self):
        super().setUp(url_name='comment_update')
        self.data = {'message': 'This is an updated message'}

    def test_with_authenticated_user(self):
        super().test_with_authenticated_user()
        self.assertTrue(Comment.objects.filter(owner_id=self.user.pk,
                                               uuid_key=self.resume.pk,
                                               message='This is an updated message').exists())

    def test_with_anonymous_user(self):
        super().test_with_anonymous_user(url_name='comment_update')

        self.assertTrue(Comment.objects.filter(owner_id=self.client.session._session_key,
                                               uuid_key=self.resume.pk,
                                               message='This is an updated message').exists())

    def test_with_wrong_anonymous_user(self):
        super().test_with_wrong_anonymous_user(url_name='comment_update')

    def test_with_wrong_authenticated_user(self):
        super().test_with_wrong_authenticated_user(url_name='comment_update')


class ResumeListViewTests(ListViewTestMixin,
                          BaseSetUpMixin,
                          CreateMethodsMixin,
                          TestCase):
    def setUp(self):
        super().setUp()
        self.object1 = self.resume
        self.object2 = self.create_resume()
        self.matching_object = self.create_resume(position='Matching test')

        self.url = reverse('resume_list')
        self.url_params = {'search_query': 'Matching'}
        self.title = 'Обзор'
        self.title_with_query = 'Поиск по резюме'


class PostListViewTests(ListViewTestMixin,
                        BaseSetUpMixin,
                        CreateMethodsMixin,
                        TestCase):
    def setUp(self):
        super().setUp()
        self.matching_object = Post.objects.create(resume=self.resume, message='Matching object')
        self.user2 = User.objects.create(username='otheruser', password='testpassword')
        self.resume2 = self.create_resume(user=self.user2)
        self.object1 = Post.objects.create(resume=self.resume2, message='Test object')
        self.object2 = Post.objects.create(resume=self.resume2, message='Test object')

        self.url = reverse('post_list')
        self.url_params = {'username_search_query': self.user.username}
        self.title = 'Блоги'
        self.title_with_query = 'Новости пользователя'




