from django.contrib.messages import get_messages
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from app_users.forms import SignUpUserForm, UserUpdateForm


class SignUpViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('signup')
        self.model = get_user_model()
        self.title = 'Регистрация пользователя'
        self.breadcrumbs_title = 'Регистрация'


    def test_get_with_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertIsInstance(response.context['form'], SignUpUserForm)

        self.assertEqual(response.context['title'], self.title)
        self.assertEqual(response.context['breadcrumbs'], [(self.breadcrumbs_title, self.url)])

    def test_post_correct_data_with_anonymous_user(self):
        data = {'username': 'newuser',
                'email': 'kosdmit@hotmail.com',
                'password1': 'testpassword',
                'password2': 'testpassword'}

        response = self.client.post(self.url, data=data)
        user = self.model.objects.filter(username=data['username']).first()

        self.assertIsNotNone(user)

        # Test that the user is authenticated
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

        # Test that the user was redirected to the success_url
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('create_profile'))

    def test_post_invalid_data_with_anonymous_user(self):
        data = {'username': 'newuser',
                'email': 'kosdmit@hotmail.com',
                'password1': 't',
                'password2': 't'}

        response = self.client.post(self.url, data=data, follow=True)
        user = self.model.objects.filter(username=data['username']).first()


        self.assertIsNone(user)

        # Test that the user is not authenticated
        self.assertNotIn('_auth_user_id', self.client.session)

        # Test that the form is invalid and the page wasn't redirected
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertTrue(response.context['form'].errors)


class UserUpdateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('user_update')
        self.model = get_user_model()
        self.title = 'Редактирование учетной записи пользователя'
        self.breadcrumbs_title = 'Редактирование учетной записи'

    def test_get_with_anonymous_user(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_get_with_authorized_user(self):
        user = self.model.objects.create_user(username='kosdmit',password='testpassword')
        self.client.login(username=user.username, password='testpassword')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], UserUpdateForm)
        self.assertEqual(response.context['title'], self.title)

    def test_post_correct_data_with_anonymous_user(self):
        data = {'username': 'updateduser',
                'email': 'updated@email.com'}

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 403)

        user = self.model.objects.filter(username=data['username']).first()
        self.assertIsNone(user)

    def test_post_correct_data_with_authorized_user(self):
        data = {'username': 'updateduser',
                'first_name': 'updatedname',
                'last_name': 'updatedname',
                'email': 'updated@email.com',
                }

        user = self.model.objects.create_user(username='kosdmit', password='testpassword')
        self.client.login(username=user.username, password='testpassword')

        response = self.client.post(self.url, data=data)
        user.refresh_from_db()

        self.assertEqual(user.username, data['username'])

        # Test that the user was redirected to the success_url
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'), fetch_redirect_response=False)

    def test_post_invalid_data_with_authenticated_user(self):
        data = {'username': '',
                'first_name': 'updatedname',
                'last_name': 'updatedname',
                'email': 'updated@email.com',
                }

        user = self.model.objects.create_user(username='kosdmit', password='testpassword')
        self.client.login(username=user.username, password='testpassword')

        response = self.client.post(self.url, data=data, follow=True)

        user = self.model.objects.filter(username=data['username']).first()
        self.assertIsNone(user)

        # Test that the form is invalid and the page wasn't redirected
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertTrue(response.context['form'].errors)





