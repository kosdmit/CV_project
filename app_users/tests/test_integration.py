import time
from copy import copy

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from app_resume.models import Resume
from app_users.models import Profile
from app_users.tests import test_data
from app_users.tests.test_integration_mixins import CommonSetUpMethodsMixin, \
    CommonAssertMethodsMixin


class SignUpTest(CommonAssertMethodsMixin,
                 CommonSetUpMethodsMixin,
                 LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_post_correct_data_with_anonymous_user(self):
        self.signup()

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('create_profile'))
        self.assert_authorized(username=test_data.SIGNUP_CORRECT_DATA['username'])

    def test_post_invalid_data_with_anonymous_user(self):
        self.signup(data=test_data.SIGNUP_INVALID_DATA)

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


    def tearDown(self):
        self.browser.quit()

    def test_post_correct_data_with_authorized_user(self):
        data = test_data.USER_UPDATE_CORRECT_DATA
        self.send_form(data=data)

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('create_profile'))
        object = self.model.objects.filter(**data).first()
        self.assertIsNotNone(object)

    def test_post_invalid_data_with_authorized_user(self):
        data = test_data.USER_UPDATE_INVALID_DATA
        self.send_form(data=data)

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('user_update'))
        self.assert_object_not_exists(data=data)


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


class CreateProfileTest(CommonSetUpMethodsMixin,
                        CommonAssertMethodsMixin,
                        LiveServerTestCase):
    def setUp(self):
        self.model = Profile
        self.browser = webdriver.Chrome()
        self.signup()

    def tearDown(self):
        self.browser.quit()

    def test_post_correct_data_with_authorized_user(self):
        data = test_data.CREATE_PROFILE_CORRECT_DATA
        self.create_profile(data=data)

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('profile'))
        self.assert_object_exists(data={'user__username': test_data.SIGNUP_CORRECT_DATA['username'],
                                        'phone_number': data['phone_number']})

    def test_post_invalid_data_with_authorized_user(self):
        data = test_data.CREATE_PROFILE_INVALID_DATA
        self.create_profile(data=data)

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('create_profile'))
        self.assert_object_not_exists(data={'user__username': test_data.SIGNUP_CORRECT_DATA['username'],
                                            'phone_number': data['phone_number']})
        self.assert_messages()


class ProfileTest(CommonAssertMethodsMixin,
                  CommonSetUpMethodsMixin,
                  LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.signup()
        self.create_profile()
        self.model = Resume

    def tearDown(self):
        self.browser.quit()

    def test_get_with_authorized_user(self):
        breadcrumbs = self.browser.find_element(By.CSS_SELECTOR, 'ol.breadcrumb')
        user_link = breadcrumbs.find_element(By.LINK_TEXT, test_data.SIGNUP_CORRECT_DATA['username'])
        self.assertIsNotNone(user_link)

        user_avatar = self.browser.find_element(By.CSS_SELECTOR, 'div.avatar-container img')
        self.assertIsNotNone(user_avatar)

        contacts_block = self.browser.find_element(By.CSS_SELECTOR, 'div.my-contacts')
        self.assertIn(test_data.SIGNUP_CORRECT_DATA['username'], contacts_block.text)
        self.assertIn(test_data.SIGNUP_CORRECT_DATA['email'], contacts_block.text)
        self.assertIn(test_data.CREATE_PROFILE_CORRECT_DATA['phone_number'], contacts_block.text)

        profile_info_block = self.browser.find_element(By.CSS_SELECTOR, 'div.profile-info')
        self.assertIn(test_data.CREATE_PROFILE_CORRECT_DATA['phone_number'], profile_info_block.text)

        user_update_href = self.browser.find_element(By.ID, 'user_update_link').get_attribute('href')
        self.assertEqual(user_update_href, self.live_server_url + reverse('user_update'))

        # Checking resume list
        for i in range(3):
            data = copy(test_data.CREATE_RESUME_DATA)
            data['position'] = data['position'] + ' ' + str(i+1)
            self.create_resume(data=data)
            self.browser.get(self.live_server_url + reverse('profile'))
            WebDriverWait(self.browser, timeout=10).until(
                lambda b: b.find_element(By.ID, 'resume_list')
            )
        resume_list = self.browser.find_element(By.ID, 'resume_list')
        primary_resumes = resume_list.find_elements(By.CSS_SELECTOR, 'a.list-group-item.active')
        self.assertEqual(len(primary_resumes), 1)
        resumes = resume_list.find_elements(By.CSS_SELECTOR, 'a.list-group-item')
        self.assertEqual(len(resumes), i+1)

        profile_update_href = self.browser.find_element(By.CSS_SELECTOR, 'div.profile-info a.btn').get_attribute('href')
        self.assertEqual(profile_update_href, self.live_server_url + reverse('profile_update'))

    def test_create_resume_with_correct_data(self):
        data = test_data.CREATE_RESUME_DATA
        self.create_resume(data=data)

        self.assert_object_exists(data=data)
        object = self.model.objects.filter(user__username=test_data.SIGNUP_CORRECT_DATA['username'],
                                           position=data['position']).first()
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + reverse('resume', kwargs={'username': test_data.SIGNUP_CORRECT_DATA['username'],
                                                             'slug': object.slug})
        )

    def test_create_resume_with_invalid_data(self):
        data = copy(test_data.CREATE_RESUME_DATA)
        data['position'] = ''
        self.create_resume(data=data)

        self.assert_object_not_exists(data=data)
        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('profile'))
