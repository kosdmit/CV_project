import time

from django.contrib.auth import get_user_model
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.common.exceptions import InvalidElementStateException
from selenium.webdriver.support.select import Select

from app_users.tests import test_data


class CommonSetUpMethodsMixin:
    def signup(self, data=test_data.SIGNUP_CORRECT_DATA):
        self.browser.get(self.live_server_url + reverse('signup'))
        self.username = self.browser.find_element(By.ID, 'id_username')
        self.email = self.browser.find_element(By.ID, 'id_email')
        self.password1 = self.browser.find_element(By.ID, 'password1_field')
        self.password2 = self.browser.find_element(By.ID, 'password2_field')
        self.first_name = self.browser.find_element(By.ID, 'id_first_name')
        self.last_name = self.browser.find_element(By.ID, 'id_last_name')
        self.submit_button = self.browser.find_element(By.CSS_SELECTOR, '#signup_form button')

        self.send_form(data=data)

    def create_profile(self, data=test_data.CREATE_PROFILE_CORRECT_DATA):
        self.birthday_date = self.browser.find_element(By.ID, 'id_birthday_date')
        self.gender = Select(self.browser.find_element(By.ID, 'id_gender'))
        self.phone_number = self.browser.find_element(By.ID, 'id_phone_number')
        self.image = self.browser.find_element(By.ID, 'id_image')
        self.submit_button = self.browser.find_element(By.CSS_SELECTOR, '#create_profile_form button')

        self.send_form(data=data)

    def create_resume(self, data=test_data.CREATE_RESUME_DATA):
        self.position = self.browser.find_element(By.ID, 'id_position')
        self.submit_button = self.browser.find_element(By.CSS_SELECTOR, '#create_resume_form button')
        self.send_form(data=data)

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
            try:
                self.__getattribute__(key).clear()
                self.__getattribute__(key).send_keys(value)
            except AttributeError:
                self.__getattribute__(key).select_by_value(value)

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

    def assert_object_not_exists(self, data):
        object = self.model.objects.filter(**data).first()
        self.assertIsNone(object)

    def assert_object_exists(self, data):
        object = self.model.objects.filter(**data).first()
        self.assertIsNotNone(object)


class TearDownMixin:
    def tearDown(self):
        self.browser.quit()