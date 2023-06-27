import time
from copy import copy

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.common import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from app_resume.models import Resume, MainEducation, Institution, \
    AdditionalEducation, ElectronicCertificate, \
    WorkExpSection, Job, Skill
from app_social.models import Post, Comment, Like
from app_users.models import Profile, SocialLinks
from app_users.tests import test_data
from app_users.tests.test_integration import UserUpdatePageTest, ProfilePageTest
from app_users.tests.test_integration_mixins import CommonSetUpMethodsMixin, \
    CommonAssertMethodsMixin, TearDownMixin, TestGetWithAuthorizedUserMixin, \
    TestGetWithAnonymousUserMixin

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')


class ResumePageTest(CommonAssertMethodsMixin,
                     CommonSetUpMethodsMixin,
                     TearDownMixin,
                     LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)
        self.wait = WebDriverWait(self.browser, timeout=10)
        self.signup()
        self.create_profile()
        self.create_resume()

        self.url = self.browser.current_url
        self.model = Resume
        self.url_name = 'resume'
        self.data = {'username': test_data.USERNAME,
                     'first_name': test_data.FIRST_NAME,
                     'last_name': test_data.LAST_NAME,
                     'email': test_data.EMAIL}
        self.object = self.model.objects.filter(user__username=self.data['username'],
                                                position=test_data.CREATE_RESUME_DATA['position']).first()

    def test_with_owner(self):
        # Test Base
        TestGetWithAuthorizedUserMixin.check_header_for_authorized_user(self)
        TestGetWithAuthorizedUserMixin.check_breadcrumbs(self)
        TestGetWithAuthorizedUserMixin.check_footer_for_authorized_user(self)

        # Test user update link
        user_update_link = self.browser.find_element(By.CSS_SELECTOR, 'div.user-card div.hero a')
        self.assertEqual(
            user_update_link.get_attribute('href'),
            self.live_server_url + reverse('user_update') + '?next=/resume/kosdmit/python-developer/'
        )
        user_update_link.click()

        UserUpdatePageTest.find_form_elements(self)
        CommonSetUpMethodsMixin.send_form(self, data=self.data)

        self.assertEqual(self.browser.current_url, self.url)
        full_name = self.browser.find_element(By.CSS_SELECTOR, 'div.user-card div.hero h1')
        self.assertEqual(full_name.text,
                         test_data.USER_UPDATE_CORRECT_DATA['first_name'].upper() + \
                         '\n' + test_data.USER_UPDATE_CORRECT_DATA['last_name'].upper())

        # Test position item
        position_item = self.browser.find_element(By.CSS_SELECTOR, 'div.user-card div.hero div.resume-position-item')
        position_text = position_item.find_element(By.CSS_SELECTOR, 'p strong').text
        self.assertEqual(position_text, test_data.CREATE_RESUME_DATA['position'].upper())

        update_position_button = position_item.find_element(By.CSS_SELECTOR, 'button')
        update_position_button.click()
        self.send_update_modal_form(prefix='position-update-')
        position_text = self.browser.find_element(By.CSS_SELECTOR, 'div.resume-position-item p strong').text
        self.assertEqual(position_text, test_data.CREATE_RESUME_DATA['position'].upper() + '1')

        # Test about_me item
        self.check_resume_field(field_name='about_me')

        # Check contacts block
        contacts_block = self.browser.find_element(By.CSS_SELECTOR, 'div.my-contacts')
        email = contacts_block.find_element(By.LINK_TEXT, test_data.SIGNUP_CORRECT_DATA['email'])
        self.assertEqual(email.get_attribute('href'), 'mailto:' + test_data.SIGNUP_CORRECT_DATA['email'])
        phone_number = contacts_block.find_element(By.LINK_TEXT,
                                                   test_data.CREATE_PROFILE_CORRECT_DATA['phone_number'])
        self.assertEqual(phone_number.get_attribute('href'),
                         'tel:' + test_data.CREATE_PROFILE_CORRECT_DATA['phone_number'])
        ProfilePageTest.test_social_link_add(self)

        # Test soft_skills item
        self.check_resume_field(field_name='soft_skills')

        # Test blog
        # Post Creating test
        field_name = 'message'
        name = 'post'
        object = self.create_resume_object_with_input(model=Post, field_name=field_name)
        update_modal = self.check_update_modal_is_opened(model=Post, field_name=field_name)
        self.close_modal(update_modal)
        item = self.get_item_by_object(object, name=name)
        self.assertIn(test_data.USER_UPDATE_CORRECT_DATA['first_name'], item.text)
        self.check_comment_modal(object, item)

        # Main Education Create test
        self.create_resume_object_without_input(model=MainEducation, name='main_education')

        # Institution Create test
        name = 'institution'
        object = self.create_resume_object_without_input(model=Institution, name=name)
        item = self.get_item_by_object(object, name=name)
        self.check_comment_modal(object, item)

        # Additional Education Create test
        name = 'additional_education'
        object = self.create_resume_object_without_input(model=AdditionalEducation, name=name)
        item = self.get_item_by_object(object, name=name)
        self.check_comment_modal(object, item)

        # Electronic Certificate Create test
        name = 'electronic_certificate'
        object = self.create_resume_object_without_input(model=ElectronicCertificate, name=name)
        item = self.get_item_by_object(object, name=name)
        self.check_comment_modal(object, item)

        # Skill Create test
        def get_item_by_object(object, name=name):
            items = self.browser.find_elements(By.CSS_SELECTOR, 'button.skill-item')

            self.wait.until(expected_conditions.visibility_of(items[0]))
            for item in items:
                if str(object.pk) == item.get_attribute('id'):
                    self.check_text_in_item(object, item)
                    return item
            raise NoSuchElementException(
                msg=f'Item for {object} has not been founded')

        name = 'skill'
        object = self.create_resume_object_with_input(model=Skill, field_name=name)
        self.check_resume_objects_count(name='skill', count=1)
        item = get_item_by_object(object, name=name)
        self.check_comment_modal(object, item)

        # Work Exp Section Create test
        self.create_resume_object_without_input(model=WorkExpSection, name='work_exp_section')

        # Job Create test
        name = 'job'
        object = self.create_resume_object_without_input(model=Job, name='job')
        item = self.get_item_by_object(object, name=name)
        self.check_comment_modal(object, item)


    def send_update_modal_form(self, prefix=''):
        update_modal = self.browser.find_element(By.ID, prefix + str(self.object.pk))
        self.wait.until(expected_conditions.visibility_of(update_modal))
        self.assertIn('show', update_modal.get_attribute('class'))

        update_input = update_modal.find_element(By.CSS_SELECTOR, '.form-control')
        update_input.send_keys('1')
        update_input.submit()

    def check_resume_field(self, field_name):
        class_name = field_name.replace('_', '-')

        self.create_resume_field_with_input(field_name=field_name)
        item = self.browser.find_element(By.CSS_SELECTOR, f'div.resume-{class_name}-item p')
        self.assertEqual(item.text, test_data.RESUME_DATA[field_name])

        update_field_button = self.browser.find_element(By.CSS_SELECTOR, f'div.resume-{class_name}-item button')
        try:
            update_field_button.click()
        except ElementClickInterceptedException as e:
            self.browser.execute_script("arguments[0].click();", update_field_button)
            print(e)
        self.send_update_modal_form(prefix=f'{class_name}-update-')
        about_me_item = self.browser.find_element(By.CSS_SELECTOR, f'div.resume-{class_name}-item p')
        self.assertEqual(about_me_item.text, test_data.RESUME_DATA[field_name] + '1')

    def create_resume_field_with_input(self, field_name):
        input_field = self.browser.find_element(By.ID, 'id_' + field_name)
        input_field.send_keys(test_data.RESUME_DATA[field_name])
        input_field.submit()

    def create_resume_object_with_input(self, model, field_name):
        self.create_resume_field_with_input(field_name)
        return self.get_resume_object(model, field_name)

    def check_update_modal_is_opened(self, model, field_name=None):
        if model == Job:
            object = model.objects.get(title='New Object')
        elif field_name:
            object = model.objects.get(resume__user__username=test_data.SIGNUP_CORRECT_DATA['username'],
                                       **{field_name: test_data.RESUME_DATA[field_name]})
        else:
            object = model.objects.get(resume__user__username=test_data.SIGNUP_CORRECT_DATA['username'])
        return self.get_modal_window(object)

    def get_modal_window(self, object, id_prefix=''):
        modal = self.browser.find_element(By.ID, id_prefix + str(object.pk))
        self.wait.until(expected_conditions.visibility_of(modal))
        self.assertIn('show', modal.get_attribute('class'))
        return modal

    def close_modal(self, modal):
        close_button = modal.find_element(By.CSS_SELECTOR, 'div.modal-header button')
        close_button.click()
        self.assertNotIn('show', modal.get_attribute('class'))

    def create_resume_object_without_input(self, model, name):
        button = self.browser.find_element(By.ID, f'{name}_create_button')
        try:
            button.click()
        except ElementClickInterceptedException as e:
            self.browser.execute_script("arguments[0].click();", button)
            print(e)
        update_modal = self.check_update_modal_is_opened(model=model)
        self.close_modal(update_modal)

        return self.get_resume_object(model)

    def get_resume_object(self, model, field_name=None):
        if model == MainEducation:
            object = model.objects.get(resume=self.object)
        elif model == Job:
            object = model.objects.get(work_exp_section__resume=self.object)
        elif model == Post:
            object = model.objects.get(resume=self.object,
                                       message=test_data.RESUME_DATA[field_name])
        elif model == Skill:
            object = model.objects.get(resume=self.object,
                                       title=test_data.RESUME_DATA[field_name])
        else:
            object = model.objects.get(resume=self.object, title='New Object')

        return object

    def check_resume_objects_count(self, name, count=1):
        # TODO Refactoring needed for variables setting item`s classes in resume template
        items = self.browser.find_elements(By.CSS_SELECTOR, f'.{name.replace("_", "-")}-item')
        self.assertEqual(len(items), count)

    def get_item_by_object(self, object, name):
        items = self.browser.find_elements(By.CSS_SELECTOR, f'ul.{name.replace("_", "-")}-list .clickable-item')
        self.wait.until(expected_conditions.visibility_of(items[0]))
        for item in items:
            if str(object.pk) == item.get_attribute('data-id'):
                self.check_text_in_item(object, item)
                return item
        raise NoSuchElementException(msg=f'Item for {object} has not been founded')

    def get_comment_item(self, items, object):
        for item in items:
            like_button = item.find_element(By.CSS_SELECTOR, 'button.like-button')
            item_id = like_button.get_attribute('id').replace('like-', '')
            if item_id == str(object.pk):
                return item
        raise NoSuchElementException(f'Item for {object} has not been founded')

    def send_comment(self, comments_modal, message='Test comment'):
        comment_input = comments_modal.find_element(By.ID, 'comment_create_input')
        comment_input.send_keys(message)
        comment_input.submit()

    def check_comment_item(self, comments_modal, object, message='Test comment'):
        comment_object = Comment.objects.get(owner_id=self.object.user.pk,
                                             message=message,
                                             uuid_key=object.pk)
        comments_modal = self.get_modal_window(object, id_prefix='comments-')
        comment_items = comments_modal.find_elements(By.CSS_SELECTOR, 'div.comment-item')
        comment_item = self.get_comment_item(comment_items, comment_object)
        self.assertIn('Test comment', comment_item.text)
        self.assertIn(self.object.user.username.upper(), comment_item.text)
        return comment_item

    def check_comment_updating(self, object):
        comments_modal = self.get_modal_window(object, id_prefix='comments-')
        self.send_comment(comments_modal, message='Test comment #2')
        comment_item = self.check_comment_item(comments_modal, object, message='Test comment #2')
        comment_edit_form = comment_item.find_element(By.CSS_SELECTOR, 'form.edit-form')
        self.assertIn('display: none;', comment_edit_form.get_attribute('style'))
        edit_button = comment_item.find_element(By.CSS_SELECTOR, 'button.edit-button')
        edit_button.click()
        self.assertIn('display: block;', comment_edit_form.get_attribute('style'))
        comment_edit_input = comment_edit_form.find_element(By.CSS_SELECTOR, '.form-control')
        comment_edit_input.send_keys('_updated')
        comment_edit_input.submit()
        comments_modal = self.get_modal_window(object, id_prefix='comments-')
        self.check_comment_item(comments_modal, object, message='Test comment #2_updated')

    def check_comment_deleting(self, object, message):
        comments_modal = self.get_modal_window(object, id_prefix='comments-')
        comment_item = self.check_comment_item(comments_modal, object, message=message)
        comment_delete_button = comment_item.find_element(By.CSS_SELECTOR, 'button.delete-button')
        comment_delete_button.click()
        with self.assertRaises(Comment.DoesNotExist):
            comment_object = Comment.objects.get(owner_id=self.object.user.pk,
                                                 message=message,
                                                 uuid_key=object.pk)

        comments_modal = self.get_modal_window(object, id_prefix='comments-')
        comments_list = comments_modal.find_element(By.CSS_SELECTOR, 'ul.comments-list')
        self.assertNotIn(message, comments_list.text)

    def check_comment_liking(self, object, message):
        comments_modal = self.get_modal_window(object, id_prefix='comments-')
        comment_object = Comment.objects.get(owner_id=self.object.user.pk,
                                             message=message,
                                             uuid_key=object.pk)
        comment_item = self.check_comment_item(comments_modal, object, message=message)
        self.check_object_liking(object=comment_object, item=comment_item)

    def check_object_liking(self, object, item):
        like_button = item.find_element(By.CSS_SELECTOR, 'button.like-button')
        like_count = int(like_button.text)
        like_button.click()
        time.sleep(1)
        new_like_count = int(like_button.text)
        self.assertEqual(new_like_count - like_count, 1)
        like_object = Like.objects.get(owner_id=self.object.user.pk, uuid_key=object.pk)
        like_button.click()
        time.sleep(1)
        new_like_count = int(like_button.text)
        self.assertEqual(new_like_count - like_count, 0)
        with self.assertRaises(Like.DoesNotExist):
            like_object = Like.objects.get(owner_id=self.object.user.pk,
                                           uuid_key=object.pk)

    def check_comment_modal(self, object, item):
        try:
            item.click()
        except ElementClickInterceptedException as e:
            self.browser.execute_script("arguments[0].click();", item)
            print(e)
        comments_modal = self.get_modal_window(object, id_prefix='comments-')
        in_modal_item = comments_modal.find_element(By.CSS_SELECTOR, '.item-in-modal')
        self.check_text_in_item(object, in_modal_item)
        if object.__class__ == Post:
            self.assertIn(test_data.USER_UPDATE_CORRECT_DATA['first_name'], in_modal_item.text)
        comments_modal = self.get_modal_window(object, id_prefix='comments-')
        self.check_object_liking(object, in_modal_item)
        self.send_comment(comments_modal)
        self.check_comment_item(comments_modal, object)
        self.check_comment_updating(object)
        self.check_comment_deleting(object, message='Test comment #2_updated')
        self.check_comment_liking(object, message='Test comment')

        comments_modal = self.get_modal_window(object, id_prefix='comments-')
        self.close_modal(comments_modal)

    def check_text_in_item(self, object, item):
        # TODO: bring the attributes of objects to a single standard
        if object.__class__ == Post:
            self.assertIn(object.message.lower(), item.text.lower())
        else:
            self.assertIn(object.title.lower(), item.text.lower())
