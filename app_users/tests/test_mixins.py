from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse


class BaseTestMixin:
    def test_get_with_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login') + f'?next={self.url}', fetch_redirect_response=False)

    def test_get_with_authorized_user(self):
        user = User.objects.create_user(username='kosdmit', password='testpassword')
        self.client.login(username=user.username, password='testpassword')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], self.form)
        self.assertEqual(response.context['title'], self.title)

    def test_post_correct_data_with_anonymous_user(self):
        response = self.client.post(self.url, data=self.correct_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login') + f'?next={self.url}', fetch_redirect_response=False)

        object = self.model.objects.filter(**self.correct_data).first()
        self.assertIsNone(object)

    def test_post_correct_data_with_authorized_user(self):
        user = User.objects.create_user(username='kosdmit', password='testpassword')
        self.client.login(username=user.username, password='testpassword')

        response = self.client.post(self.url, data=self.correct_data)

        object = self.model.objects.filter(**self.correct_data).first()
        self.assertIsNotNone(object)

        # Test that the user was redirected to the success_url
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'), fetch_redirect_response=False)

    def test_post_invalid_data_with_authenticated_user(self):
        user = get_user_model().objects.create_user(username='kosdmit', password='testpassword')
        self.client.login(username=user.username, password='testpassword')

        response = self.client.post(self.url, data=self.invalid_data, follow=True)

        object = self.model.objects.filter(**self.invalid_data).first()
        self.assertIsNone(object)

        # Test that the form is invalid and the page wasn't redirected
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertTrue(response.context['form'].errors)