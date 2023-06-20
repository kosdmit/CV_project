from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from app_users.tests import test_data


class SignUpTest(LiveServerTestCase):
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
        for key, value in test_data.SIGNUP_CORRECT_DATA.items():
            self.__getattribute__(key).send_keys(value)

        self.submit_button.click()

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('create_profile'))

        # Check user authorization
        user_button_set = self.browser.find_elements(By.LINK_TEXT, test_data.SIGNUP_CORRECT_DATA['username'])
        self.assertGreater(len(user_button_set), 0)

    def test_post_invalid_data_with_anonymous_user(self):
        for key, value in test_data.SIGNUP_INVALID_DATA.items():
            self.__getattribute__(key).send_keys(value)

        self.submit_button.click()

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('signup'))
        messages = self.browser.find_elements(By.CSS_SELECTOR, '.messages-block div')
        self.assertGreater(len(messages), 0)

        # Check user is not authorized
        user_button_set = self.browser.find_elements(By.LINK_TEXT, test_data.SIGNUP_CORRECT_DATA['username'])
        self.assertEqual(user_button_set, [])