from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from app_users.tests import test_data
from app_users.tests.test_integration_mixins import CommonSetUpMethodsMixin, \
    CommonAssertMethodsMixin


class SignUpTest(CommonAssertMethodsMixin,
                 CommonSetUpMethodsMixin,
                 LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.get(self.live_server_url + reverse('signup'))
        self.username = self.browser.find_element(By.ID, 'id_username')
        self.email = self.browser.find_element(By.ID, 'id_email')
        self.password1 = self.browser.find_element(By.ID, 'password1_field')
        self.password2 = self.browser.find_element(By.ID, 'password2_field')
        self.first_name = self.browser.find_element(By.ID, 'id_first_name')
        self.last_name = self.browser.find_element(By.ID, 'id_last_name')
        self.submit_button = self.browser.find_element(By.CSS_SELECTOR, '#signup_form button')


    def tearDown(self):
        self.browser.quit()

    def test_post_correct_data_with_anonymous_user(self):
        self.send_form(data=test_data.SIGNUP_CORRECT_DATA)

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('create_profile'))
        self.assert_authorized(username=test_data.SIGNUP_CORRECT_DATA['username'])

    def test_post_invalid_data_with_anonymous_user(self):
        self.send_form(data=test_data.SIGNUP_INVALID_DATA)

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('signup'))
        self.assert_messages()
        self.assert_not_authorized(username=test_data.SIGNUP_INVALID_DATA['username'])


class UserUpdateTest(CommonAssertMethodsMixin,
                     CommonSetUpMethodsMixin,
                     LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.login()
        self.browser.get(self.live_server_url + reverse('user_update'))

        self.username = self.browser.find_element(By.ID, 'id_username')
        self.first_name = self.browser.find_element(By.ID, 'id_first_name')
        self.last_name = self.browser.find_element(By.ID, 'id_last_name')
        self.email = self.browser.find_element(By.ID, 'id_email')
        self.submit_button = self.browser.find_element(By.CSS_SELECTOR, '#user_update_form button')

        self.model = get_user_model()
        self.data = None


    def tearDown(self):
        self.browser.quit()

    def test_post_correct_data_with_authorized_user(self):
        self.data = test_data.USER_UPDATE_CORRECT_DATA
        self.send_form(data=self.data)

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('create_profile'))
        object = self.model.objects.filter(**self.data).first()
        self.assertIsNotNone(object)

    def test_post_invalid_data_with_authorized_user(self):
        self.data = test_data.USER_UPDATE_INVALID_DATA
        self.send_form(data=self.data)

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('user_update'))
        self.assert_object_not_exists()


class LoginTest(CommonAssertMethodsMixin,
                CommonSetUpMethodsMixin,
                LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_post_correct_data_with_anonymous_user(self):
        self.login()
        self.assert_authorized()

    def test_post_invalid_data_with_anonymous_user(self):
        self.browser.get(self.live_server_url + reverse('login'))
        self.username = self.browser.find_element(By.ID, 'id_username')
        self.password = self.browser.find_element(By.ID, 'id_password')
        self.submit_button = self.browser.find_element(By.CSS_SELECTOR, '#login_form button')

        self.send_form(data=test_data.LOGIN_INVALID_DATA)

        self.assert_not_authorized()
        self.assert_messages()



