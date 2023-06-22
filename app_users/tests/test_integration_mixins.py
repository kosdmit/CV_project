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


class CommonMethodsForGetTests:
    def check_breadcrumbs(self):
        breadcrumb_links = self.browser.find_elements(By.CSS_SELECTOR, 'li.breadcrumb-item a')
        breadcrumb_hrefs = [link.get_attribute('href') for link in breadcrumb_links]
        self.assertIn(self.live_server_url + reverse('main'), breadcrumb_hrefs)
        self.assertIn(self.browser.current_url, breadcrumb_hrefs)

    def check_form_page_content(self):
        page_header = self.browser.find_element(By.ID, 'page_header')
        self.assertIsNotNone(page_header)
        form = self.browser.find_element(By.ID, self.url_name + '_form')
        self.assertIsNotNone(form)


class TestGetWithAnonymousUserMixin(CommonMethodsForGetTests):
    def test_get_with_anonymous_user(self):
        self.browser.get(self.live_server_url + reverse(self.url_name))
        self.check_header_for_anonymous_user()
        self.check_breadcrumbs()
        self.check_form_page_content()
        self.check_footer_for_anonymous_user()

    def check_header_for_anonymous_user(self):
        logo = self.browser.find_element(By.CSS_SELECTOR, 'header a.navbar-brand')
        self.assertEqual(logo.text, 'CV Project')
        self.assertEqual(logo.get_attribute('href'), self.live_server_url + reverse('main'))

        your_resume_link = self.browser.find_element(By.ID, 'your_resume_header_link')
        self.assertIn('disabled', your_resume_link.get_attribute('class'))
        self.assertIsNone(your_resume_link.get_attribute('href'))

        search_form = self.browser.find_element(By.CSS_SELECTOR, 'header form')
        self.assertEqual(search_form.get_attribute('action'), self.live_server_url + reverse('resume_list'))

        search_field = self.browser.find_element(By.ID, 'id_search_query')
        self.assertFalse(search_field.get_attribute('value'))

        login_link = self.browser.find_element(By.ID, 'login_link')
        self.assertEqual(login_link.get_attribute('href'), self.live_server_url + reverse('login'))

        signup_link = self.browser.find_element(By.ID, 'signup_link')
        self.assertEqual(signup_link.get_attribute('href'), self.live_server_url + reverse('signup'))


    def check_footer_for_anonymous_user(self):
        your_resume_link = self.browser.find_element(By.ID, 'your_resume_footer_link')
        self.assertIn('disabled', your_resume_link.get_attribute('class'))
        self.assertIsNone(your_resume_link.get_attribute('href'))

        your_profile_link = self.browser.find_element(By.ID, 'your_profile_footer_link')
        self.assertIn('disabled', your_resume_link.get_attribute('class'))
        self.assertIsNone(your_resume_link.get_attribute('href'))


class TestGetWithAuthorizedUserMixin(CommonMethodsForGetTests):
    def test_get_with_authorized_user(self):
        self.check_header_for_authorized_user()
        self.check_breadcrumbs()
        self.check_form_page_content()
        self.check_footer_for_authorized_user()

    def check_footer_for_authorized_user(self):
        your_resume_link = self.browser.find_element(By.ID, 'your_resume_footer_link')
        # TODO add checking for resume does not exist for authorized user
        # self.assertNotIn('disabled', your_resume_link.get_attribute('class'))
        # self.assertIsNotNone(your_resume_link.get_attribute('href'))

        your_profile_link = self.browser.find_element(By.ID, 'your_profile_footer_link')
        # TODO add checking for profile does not exist for authorized user
        # self.assertNotIn('disabled', your_resume_link.get_attribute('class'))
        # self.assertIsNotNone(your_resume_link.get_attribute('href'))

    def check_header_for_authorized_user(self):
        logo = self.browser.find_element(By.CSS_SELECTOR, 'header a.navbar-brand')
        self.assertEqual(logo.text, 'CV Project')
        self.assertEqual(logo.get_attribute('href'), self.live_server_url + reverse('main'))

        your_resume_link = self.browser.find_element(By.ID, 'your_resume_header_link')
        # TODO add checking for resume does not exist for authorized user
        # self.assertNotIn('disabled', your_resume_link.get_attribute('class'))
        # self.assertIsNotNone(your_resume_link.get_attribute('href'))

        search_form = self.browser.find_element(By.CSS_SELECTOR, 'header form')
        self.assertEqual(search_form.get_attribute('action'), self.live_server_url + reverse('resume_list'))

        search_field = self.browser.find_element(By.ID, 'id_search_query')
        self.assertFalse(search_field.get_attribute('value'))

        dropdown_button = self.browser.find_element(By.CSS_SELECTOR, 'header #user_dropdown_button')
        self.assertEqual(dropdown_button.text, test_data.USERNAME)
