from django.test import Client
from django.urls import reverse

from app_social.forms import CommentForm
from app_social.models import Comment


class BaseSetUpMixin:
    def setUp(self):
        self.client = Client()
        self.user = self.create_user(username='kosdmit')
        self.resume = self.create_resume()
        self.initial_resume_rating = self.resume.rating


class CommentTestMixin:
    def setUp(self, url_name):
        super().setUp()

        self.object = Comment.objects.create(uuid_key=self.resume.pk,
                                             user=self.user,
                                             owner_id=self.user.pk,
                                             message='This message is created in setUp Mixin')

        self.url = reverse(url_name, kwargs={'pk': self.object.pk})
        self.referer = reverse('resume_list') + '?modal_id=comments-' + str(self.resume.pk)

    def test_with_authenticated_user(self):
        self.client.login(username=self.user.username, password='testpassword')

        self.response = self.client.post(self.url, self.data, HTTP_REFERER=self.referer)

        self.assertEqual(self.response.status_code, 302)
        self.assertIn(f'modal_id=comments-{self.resume.pk}', self.response.url)

    def test_with_anonymous_user(self, url_name):
        self.object = Comment.objects.create(owner_id=self.client.session._session_key,
                                             uuid_key=self.resume.pk,
                                             message='Anon_comment',
                                             is_approved=True)

        self.resume.refresh_from_db()
        self.initial_resume_rating = self.resume.rating

        self.response = self.client.post(reverse(url_name, kwargs={'pk': self.object.pk}),
                                         self.data,
                                         HTTP_REFERER=self.referer)

        self.assertEqual(self.response.status_code, 302)
        self.assertIn(f'modal_id=comments-{self.resume.pk}', self.response.url)

    def test_with_wrong_anonymous_user(self, url_name):
        comment = Comment.objects.create(owner_id=self.client.session._session_key,
                                         uuid_key=self.resume.pk,
                                         message='Anon_comment',
                                         is_approved=True)

        self.resume.refresh_from_db()
        initial_resume_rating = self.resume.rating

        self.client = Client()

        response = self.client.post(reverse(url_name, kwargs={'pk': comment.pk}),
                                    self.data,
                                    HTTP_REFERER=self.referer)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=comment.pk, message='Anon_comment').exists())

        # Check that the resume rating was not updated
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.rating, initial_resume_rating)

    def test_with_wrong_authenticated_user(self, url_name):
        # Create another user
        other_user = self.create_user(username='otheruser')

        self.client.login(username=other_user.username, password='testpassword')
        initial_resume_rating = self.resume.rating

        response = self.client.post(reverse(url_name, kwargs={'pk': self.object.pk}),
                                    self.data,
                                    HTTP_REFERER=self.referer)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(
            pk=self.object.pk,
            message='This message is created in setUp Mixin'
        ).exists())

        # Check that the resume rating was not updated
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.rating, initial_resume_rating)


class ListViewTestMixin:
    def test_without_search_query(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        # Check the context data
        self.assertIsInstance(response.context['comment_form'], CommentForm)
        self.assertEqual(response.context['title'], self.title)

        # Check the queryset
        self.assertQuerysetEqual(
            sorted(response.context['object_list'], key=lambda x: x.pk),
            sorted([self.object1, self.object2, self.matching_object], key=lambda x: x.pk)
        )

    def test_with_search_query(self):
        response = self.client.get(self.url, self.url_params)

        self.assertEqual(response.status_code, 200)

        # Check the context data
        self.assertIsInstance(response.context['comment_form'], CommentForm)
        self.assertEqual(response.context['title'], self.title_with_query)

        # Check the queryset
        self.assertQuerysetEqual(response.context['object_list'], [self.matching_object])

    def test_without_search_query_authorized_user(self):
        self.client.login(username=self.user.username, password='testpassword')
        self.test_without_search_query()

    def test_with_search_query_authorized_user(self):
        self.client.login(username=self.user.username, password='testpassword')
        self.test_with_search_query()
