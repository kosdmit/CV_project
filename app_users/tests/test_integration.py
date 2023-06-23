import time
from copy import copy

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import url_contains
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from app_resume.models import Resume
from app_users.models import Profile, SocialLinks
from app_users.tests import test_data
from app_users.tests.test_integration_mixins import CommonSetUpMethodsMixin, \
    CommonAssertMethodsMixin, TearDownMixin, TestGetWithAuthorizedUserMixin, \
    TestGetWithAnonymousUserMixin

from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')


class SignUpPageTest(CommonAssertMethodsMixin,
                     CommonSetUpMethodsMixin,
                     TearDownMixin,
                     TestGetWithAnonymousUserMixin,
                     LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.url_name = 'signup'

    def test_post_correct_data_with_anonymous_user(self):
        self.signup()

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('create_profile'))
        self.assert_authorized(username=test_data.SIGNUP_CORRECT_DATA['username'])

    def test_post_invalid_data_with_anonymous_user(self):
        self.signup(data=test_data.SIGNUP_INVALID_DATA)

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse(self.url_name))
        self.assert_messages()
        self.assert_not_authorized(username=test_data.SIGNUP_INVALID_DATA['username'])


class UserUpdatePageTest(CommonAssertMethodsMixin,
                         CommonSetUpMethodsMixin,
                         TearDownMixin,
                         TestGetWithAuthorizedUserMixin,
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
        self.url_name = 'user_update'

    def test_post_correct_data_with_authorized_user(self):
        data = test_data.USER_UPDATE_CORRECT_DATA
        self.send_form(data=data)

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('create_profile'))
        object = self.model.objects.filter(**data).first()
        self.assertIsNotNone(object)

    def test_post_invalid_data_with_authorized_user(self):
        data = test_data.USER_UPDATE_INVALID_DATA
        self.send_form(data=data)

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse(self.url_name))
        self.assert_object_not_exists(data=data)


class LoginPageTest(CommonAssertMethodsMixin,
                    CommonSetUpMethodsMixin,
                    TearDownMixin,
                    TestGetWithAnonymousUserMixin,
                    LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()

        self.url_name = 'login'
        self.model = get_user_model()

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
                        TearDownMixin,
                        TestGetWithAuthorizedUserMixin,
                        LiveServerTestCase):
    def setUp(self):
        self.model = Profile
        self.url_name = 'create_profile'
        self.browser = webdriver.Chrome()
        self.signup()

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


class ProfilePageTest(CommonAssertMethodsMixin,
                      CommonSetUpMethodsMixin,
                      TearDownMixin,
                      TestGetWithAuthorizedUserMixin,
                      LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.implicitly_wait(10)
        self.signup()
        self.create_profile()
        self.model = Resume

    def test_get_with_authorized_user(self):
        self.check_header_for_authorized_user()
        self.check_breadcrumbs()
        self.check_footer_for_authorized_user()

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

    def test_social_link_add(self):
        vk_button = self.browser.find_element(By.CSS_SELECTOR, 'button.social-link.vk')
        vk_button.click()
        vk_url_input = self.browser.find_element(By.ID, 'id_vk')
        vk_url_input.send_keys(test_data.VK_URL)
        vk_url_input.submit()

        github_button = self.browser.find_element(By.CSS_SELECTOR, 'button.social-link.github')
        github_button.click()
        github_url_input = self.browser.find_element(By.ID, 'id_git_hub')
        github_url_input.send_keys(test_data.GITHUB_URL)
        github_url_input.submit()

        object = SocialLinks.objects.filter(user__username=test_data.SIGNUP_CORRECT_DATA['username']).first()
        self.assertEqual(object.vk, test_data.VK_URL)
        self.assertEqual(object.git_hub, test_data.GITHUB_URL)

        social_links = self.browser.find_elements(By.CSS_SELECTOR, 'div.sharebuttons a.btn')
        social_links_hrefs = [link.get_attribute('href') for link in social_links]
        self.assertIn(test_data.VK_URL, social_links_hrefs)
        self.assertIn(test_data.GITHUB_URL, social_links_hrefs)

    def test_primary_resume_update(self):
        # Checking resume list
        for i in range(3):
            data = copy(test_data.CREATE_RESUME_DATA)
            data['position'] = data['position'] + ' ' + str(i+1)
            self.create_resume(data=data)
            self.browser.get(self.live_server_url + reverse('profile'))
        resume_list = self.browser.find_element(By.ID, 'resume_list')
        primary_resumes = resume_list.find_elements(By.CSS_SELECTOR, 'a.list-group-item.active')
        self.assertEqual(len(primary_resumes), 1)
        resumes = resume_list.find_elements(By.CSS_SELECTOR, 'a.list-group-item')
        self.assertEqual(len(resumes), i+1)

        last_resume = resumes[-1]
        self.assertNotIn('active', last_resume.get_attribute('class'))
        radio_button = last_resume.find_element(By.TAG_NAME, 'input')
        radio_button.click()

        primary_resume = self.browser.find_element(By.CSS_SELECTOR, '#resume_list a.list-group-item.active')
        self.assertIn('active', primary_resume.get_attribute('class'))
        self.assertIn(test_data.CREATE_RESUME_DATA['position'] + ' ' + str(i+1), primary_resume.text)

        object = self.model.objects.filter(
            position=test_data.CREATE_RESUME_DATA['position'] + ' ' + str(i+1),
            is_primary=True
        )
        self.assertIsNotNone(object)


class ProfileUpdatePageTest(CommonAssertMethodsMixin,
                            CommonSetUpMethodsMixin,
                            TearDownMixin,
                            TestGetWithAuthorizedUserMixin,
                            LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)
        self.signup()
        self.create_profile()
        self.browser.get(self.live_server_url + reverse('profile_update'))
        self.model = Profile
        self.url_name = 'profile_update'

    def test_post_correct_data(self):
        data = copy(test_data.CREATE_PROFILE_CORRECT_DATA)
        data['phone_number'] = '+79111111111'
        self.create_profile(data=data)

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('profile'))

        profile_info_block = self.browser.find_element(By.CSS_SELECTOR, 'div.profile-info')
        self.assertIn(data['phone_number'], profile_info_block.text)

        object_set = self.model.objects.all()
        self.assertEqual(len(object_set), 1)

    def test_post_invalid_data(self):
        data = copy(test_data.CREATE_PROFILE_CORRECT_DATA)
        data['phone_number'] = '+7'
        self.create_profile(data=data)

        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('profile_update'))

        object_set = self.model.objects.all()
        self.assertEqual(len(object_set), 1)

        object = self.model.objects.filter(user__username=test_data.SIGNUP_CORRECT_DATA['username'],
                                           phone_number=data['phone_number']).first()
        self.assertIsNone(object)

        self.assert_messages()

    def test_get_with_authorized_user(self):
        self.url_name = 'create_profile'
        super().test_get_with_authorized_user()


class LogoutTest(CommonAssertMethodsMixin,
                 CommonSetUpMethodsMixin,
                 TearDownMixin,
                 LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.signup()

    def test(self):
        dropdown_button = self.browser.find_element(By.CSS_SELECTOR, 'header #user_dropdown_button')
        dropdown_button.click()

        logout_link = self.browser.find_element(By.CSS_SELECTOR, 'header #logout_link')
        logout_link.click()

        self.assert_not_authorized()
