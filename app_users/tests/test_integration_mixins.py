from django.contrib.auth import get_user_model
from django.urls import reverse
from selenium.webdriver.common.by import By

from app_users.tests import test_data


class CommonSetUpMethodsMixin:
    def login(self):
        self.user = get_user_model().objects.create_user(
            username=test_data.USERNAME,
            password=test_data.PASSWORD)

        self.browser.get(self.live_server_url + reverse('login'))
        self.username = self.browser.find_element(By.ID, 'id_username')
        self.password = self.browser.find_element(By.ID, 'id_password')
        self.submit_button = self.browser.find_element(By.CSS_SELECTOR, '#login_form button')

        for key, value in test_data.LOGIN_CORRECT_DATA.items():
            self.__getattribute__(key).send_keys(value)

        self.submit_button.click()

    def send_form(self, data):
        for key, value in data.items():
            self.__getattribute__(key).clear()
            self.__getattribute__(key).send_keys(value)
        self.submit_button.click()


class CommonAssertMethodsMixin:
    def assert_authorized(self, username=test_data.LOGIN_CORRECT_DATA['username']):
        user_button_set = self.browser.find_elements(By.LINK_TEXT, username)
        self.assertGreater(len(user_button_set), 0)

    def assert_not_authorized(self, username=test_data.LOGIN_INVALID_DATA['username']):
        user_button_set = self.browser.find_elements(By.LINK_TEXT, username)
        self.assertEqual(user_button_set, [])

    def assert_messages(self):
        messages = self.browser.find_elements(By.CSS_SELECTOR, '.messages-block div')
        self.assertGreater(len(messages), 0)

    def assert_object_not_exists(self):
        object = self.model.objects.filter(**self.data).first()
        self.assertIsNone(object)