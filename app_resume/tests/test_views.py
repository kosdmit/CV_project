from unittest import expectedFailure
from unittest.mock import patch, Mock
from uuid import uuid4

from django.http import HttpResponseRedirect
from django.test import TestCase, RequestFactory, Client

from django.contrib.auth.models import User
from django.urls import reverse

from app_resume.models import Resume, MainEducation, Institution, \
    AdditionalEducation, ElectronicCertificate, Skill, WorkExpSection, Job
from app_resume.tests.test_mixins import CreateMethodsMixin, BaseSetUpMixin, \
    ResumeItemCreateViewTestMixin, ResumeItemUpdateViewTestMixin, \
    ResumeItemDeleteViewTestMixin
from app_resume.views import MainView, ResumeView, InstitutionDeleteView, \
    AdditionalEducationDeleteView, ElectronicCertificateDeleteView, \
    SkillDeleteView, WorkExpSectionDeleteView, JobDeleteView
from app_users.models import Profile, SocialLinks


class MainViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = MainView()
        self.user = User.objects.create_user(username=self.view.USER_TO_REDIRECT, password='testpassword')
        self.profile = Profile.objects.create(user=self.user)

    def test_redirect_when_resume_exists(self):
        Resume.objects.create(user=self.user, profile=self.profile, is_primary=True)
        request = self.factory.get('/')
        self.view.request = request

        response = self.view.dispatch(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse('primary_resume', kwargs={'username': self.view.USER_TO_REDIRECT}), response.url)

    def test_redirect_when_multiple_resumes(self):
        Resume.objects.create(user=self.user, profile=self.profile, is_primary=True, position='Python Developer')
        Resume.objects.create(user=self.user, profile=self.profile, is_primary=True, position='Java Developer')
        request = self.factory.get('/')
        self.view.request = request

        response = self.view.dispatch(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse('primary_resume', kwargs={'username': self.view.USER_TO_REDIRECT}), response.url)

    def test_redirect_when_no_resume(self):
        request = self.factory.get('/')
        self.view.request = request

        response = self.view.dispatch(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse('login'), response.url)

    def test_url_parameters(self):
        Resume.objects.create(user=self.user, profile=self.profile, is_primary=True)
        request = self.factory.get('/?param1=value1&param2=value2')
        self.view.request = request

        response = self.view.dispatch(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('primary_resume', kwargs={'username': self.view.USER_TO_REDIRECT}), response.url)
        self.assertIn('param1=value1', response.url)
        self.assertIn('param2=value2', response.url)


class ResumeViewTest(CreateMethodsMixin, TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = ResumeView.as_view()

        self.user = self.create_user()
        self.slug = 'test_slug'
        self.resume_with_slug = self.create_resume(slug=self.slug)
        self.resume_primary = self.create_resume(is_primary=True)
        for _ in range(3):
            self.create_resume()

    def test_context_for_owner_with_slug(self):
        request = self.factory.get(f'/{self.user.username}/{self.slug}/')
        request.user = self.user

        response = self.view(request, slug=self.slug, username=self.user.username)
        context = response.context_data


        self.assertEqual(context['owner'], self.user)
        self.assertEqual(context['resume'], self.resume_with_slug)
        self.assertTrue('resume_position_form' in context)

        self.assertFalse('institution_create_form' in context)
        self.assertFalse('job_create_form' in context)

        self.assertEqual(context['breadcrumbs'][0][1], reverse('profile'))

    def test_context_for_guest_with_slug(self):
        request = self.factory.get(f'/{self.user.username}/{self.slug}/')

        guest = User.objects.create(username='guest', password='testpassword')
        request.user = guest

        response = self.view(request, slug=self.slug, username=self.user.username)
        context = response.context_data


        self.assertEqual(context['owner'], self.user)
        self.assertEqual(context['resume'], self.resume_with_slug)
        self.assertTrue('resume_position_form' not in context)

        self.assertFalse('institution_create_form' in context)
        self.assertFalse('job_create_form' in context)

        self.assertEqual(context['breadcrumbs'][0][1], None)

    def test_context_for_owner_without_slug(self):
        request = self.factory.get(f'/{self.user.username}/')
        request.user = self.user

        response = self.view(request, username=self.user.username)
        context = response.context_data


        self.assertEqual(context['owner'], self.user)
        self.assertEqual(context['resume'], self.resume_primary)
        self.assertTrue('resume_position_form' in context)

        self.assertFalse('institution_create_form' in context)
        self.assertFalse('job_create_form' in context)

        self.assertEqual(context['breadcrumbs'][0][1], reverse('profile'))

    def test_context_for_guest_without_slug(self):
        request = self.factory.get(f'/{self.user.username}/')

        guest = User.objects.create(username='guest', password='testpassword')
        request.user = guest

        response = self.view(request, username=self.user.username)
        context = response.context_data


        self.assertEqual(context['owner'], self.user)
        self.assertEqual(context['resume'], self.resume_primary)
        self.assertTrue('resume_position_form' not in context)

        self.assertFalse('institution_create_form' in context)
        self.assertFalse('job_create_form' in context)

        self.assertEqual(context['breadcrumbs'][0][1], None)

    @expectedFailure
    def test_context_data_with_wrong_slug(self):
        slug = 'wrong-slug'
        request = self.factory.get(f'/{self.user.username}/{slug}/')
        response = self.view(request, username=self.user.username, slug=slug)

        self.assertEqual(response.status_code, '404')


class ResumeUpdateViewTest(BaseSetUpMixin, CreateMethodsMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.resume = self.create_resume(user=self.user1, position='Position1',
                                         about_me='AboutMe1')

    def test_form_valid_with_owner(self):
        self.client.login(username='kosdmit', password='testpassword')
        response = self.client.post(
            reverse('resume_update', kwargs={'username': self.user1.username,
                                             'slug': self.resume.slug}),
            {'position': 'New Position'},
            HTTP_REFERER=reverse('resume', kwargs={'username': self.user1.username,
                                                   'slug': self.resume.slug})
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Resume.objects.get(pk=self.resume.pk).position, 'New Position')
        self.assertEqual(Resume.objects.get(pk=self.resume.pk).about_me, 'AboutMe1')

    def test_form_valid_with_not_owner(self):
        self.client.login(username='otheruser', password='testpassword')
        response = self.client.post(
            reverse('resume_update', kwargs={'username': self.user1.username,
                                             'slug': self.resume.slug}),
            {'position': 'New Position'},
            HTTP_REFERER=reverse('resume', kwargs={'username': self.user1.username,
                                                   'slug': self.resume.slug})
        )

        self.assertEqual(response.status_code, 403)  # Permission Denied
        self.assertEqual(Resume.objects.get(pk=self.resume.pk).position, 'Position1')

    def test_get_success_url(self):
        self.client.login(username='kosdmit', password='testpassword')
        response = self.client.post(
            reverse('resume_update', kwargs={'username': self.user1.username,
                                                      'slug': self.resume.slug}),
            {'position': 'New Position'},
            HTTP_REFERER=reverse('resume', kwargs={'username': self.user1.username,
                                                   'slug': self.resume.slug}) + '?modal_id=123'
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('resume', kwargs={'username': self.user1.username,
                                                   'slug': self.resume.slug}))


class ResumeIsPrimaryUpdateViewTest(BaseSetUpMixin, CreateMethodsMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.resume1 = self.create_resume(user=self.user1, is_primary=True)
        self.resume2 = self.create_resume(user=self.user1, is_primary=False)

        self.url = reverse('resume_is_primary_update', kwargs={'username': self.user1.username})


    def test_with_owner(self):
        self.client.login(username='kosdmit', password='testpassword')
        response = self.client.post(self.url, {'is_primary': self.resume2.pk},
                                    HTTP_REFERER=reverse('profile'))

        self.resume1.refresh_from_db()
        self.resume2.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.resume1.is_primary, False)
        self.assertEqual(self.resume2.is_primary, True)

    def test_with_guest(self):
        self.client.login(username='otheruser', password='testpassword')
        response = self.client.post(self.url, {'is_primary': self.resume2.pk},
                                    HTTP_REFERER=reverse('profile'))

        self.resume1.refresh_from_db()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.resume1.is_primary, True)
        self.assertEqual(self.resume2.is_primary, False)

    def test_with_invalid_resume_id(self):
        self.client.login(username='kosdmit', password='testpassword')
        response = self.client.post(self.url, {'is_primary': 'invalid_id'})

        self.assertEqual(response.status_code, 404)


class MainEducationCreateViewTest(ResumeItemCreateViewTestMixin,
                                  BaseSetUpMixin,
                                  CreateMethodsMixin,
                                  TestCase):
    def setUp(self):
        super().setUp(url_name='main_education_create')
        self.model = MainEducation


class MainEducationUpdateViewTest(ResumeItemUpdateViewTestMixin,
                                  BaseSetUpMixin,
                                  CreateMethodsMixin,
                                  TestCase):
    def setUp(self):
        self.model = MainEducation
        self.data = {
            'level': 'Higher education',
            'degree': 'Master'
        }
        super().setUp(url_name='main_education_update')


class InstitutionCreateViewTest(ResumeItemCreateViewTestMixin,
                                BaseSetUpMixin,
                                CreateMethodsMixin,
                                TestCase):
    def setUp(self):
        super().setUp('institution_create')
        self.main_education1 = MainEducation.objects.create(resume=self.resume)
        self.model = Institution


class InstitutionUpdateViewTest(BaseSetUpMixin,
                                ResumeItemUpdateViewTestMixin,
                                CreateMethodsMixin,
                                TestCase):
    def setUp(self):
        self.model = Institution
        self.data = {
            'title': 'New title',
            'description': 'New description'
        }
        super().setUp()
        main_education = MainEducation.objects.create(resume=self.resume)
        ResumeItemUpdateViewTestMixin.setUp(self, url_name='institution_update', main_education=main_education)


class InstitutionDeleteViewTest(BaseSetUpMixin,
                                ResumeItemDeleteViewTestMixin,
                                CreateMethodsMixin,
                                TestCase):
    def setUp(self):
        self.model = Institution
        self.view = InstitutionDeleteView()

        super().setUp()
        main_education = MainEducation.objects.create(resume=self.resume)
        ResumeItemDeleteViewTestMixin.setUp(self,
                                            url_name='institution_delete',
                                            main_education=main_education)


class AdditionalEducationCreateViewTest(ResumeItemCreateViewTestMixin,
                                        BaseSetUpMixin,
                                        CreateMethodsMixin,
                                        TestCase):
    def setUp(self):
        super().setUp('additional_education_create')
        self.model = AdditionalEducation


class AdditionalEducationUpdateViewTest(BaseSetUpMixin,
                                        ResumeItemUpdateViewTestMixin,
                                        CreateMethodsMixin,
                                        TestCase):
    def setUp(self):
        self.model = AdditionalEducation
        self.data = {
            'title': 'New title',
            'description': 'New description'
        }
        super().setUp()
        ResumeItemUpdateViewTestMixin.setUp(self, url_name='additional_education_update')


class AdditionalEducationDeleteViewTest(BaseSetUpMixin,
                                        ResumeItemDeleteViewTestMixin,
                                        CreateMethodsMixin,
                                        TestCase):
    def setUp(self):
        self.model = AdditionalEducation
        self.view = AdditionalEducationDeleteView()

        super().setUp()
        ResumeItemDeleteViewTestMixin.setUp(self, url_name='additional_education_delete')


class ElectronicCertificateCreateViewTest(ResumeItemCreateViewTestMixin,
                                          BaseSetUpMixin,
                                          CreateMethodsMixin,
                                          TestCase):
    def setUp(self):
        super().setUp('electronic_certificate_create')
        self.model = ElectronicCertificate


class ElectronicCertificateUpdateViewTest(BaseSetUpMixin,
                                          ResumeItemUpdateViewTestMixin,
                                          CreateMethodsMixin,
                                          TestCase):
    def setUp(self):
        self.model = ElectronicCertificate
        self.data = {
            'title': 'New title',
            'completion_percentage': 90
        }
        super().setUp()
        ResumeItemUpdateViewTestMixin.setUp(self, url_name='electronic_certificate_update')


class ElectronicCertificateDeleteViewTest(BaseSetUpMixin,
                                          ResumeItemDeleteViewTestMixin,
                                          CreateMethodsMixin,
                                          TestCase):
    def setUp(self):
        self.model = ElectronicCertificate
        self.view = ElectronicCertificateDeleteView()

        super().setUp()
        ResumeItemDeleteViewTestMixin.setUp(self, url_name='electronic_certificate_delete')


class SkillCreateViewTest(ResumeItemCreateViewTestMixin,
                          BaseSetUpMixin,
                          CreateMethodsMixin,
                          TestCase):
    def setUp(self):
        super().setUp('skill_create')
        self.model = Skill
        self.data = {'title': 'New Skill'}

    def test_with_owner(self):
        self.client.login(username=self.user1.username, password='testpassword')
        response = self.client.post(self.url, self.data, HTTP_REFERER=self.referer)

        obj_set = self.model.objects.filter(resume=self.resume).all()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(obj_set.count(), 1)
        self.assertEqual(obj_set.first().title, self.data['title'])

    @expectedFailure
    def test_open_modal_if_success(self):
        super().test_open_modal_if_success()


class SkillDeleteViewTest(BaseSetUpMixin,
                          ResumeItemDeleteViewTestMixin,
                          CreateMethodsMixin,
                          TestCase):
    def setUp(self):
        self.model = Skill
        self.view = SkillDeleteView()

        super().setUp()
        ResumeItemDeleteViewTestMixin.setUp(self, url_name='electronic_certificate_delete')
        self.url = reverse('skill_delete', kwargs={'pk': self.object.pk})


class WorkExpSectionCreateViewTest(ResumeItemCreateViewTestMixin,
                                   BaseSetUpMixin,
                                   CreateMethodsMixin,
                                   TestCase):
    def setUp(self):
        super().setUp('work_exp_section_create')
        self.model = WorkExpSection
        self.data = {'title': 'New Section'}

    @expectedFailure
    def test_updates_rating(self):
        super().test_updates_rating()


class WorkExpSectionUpdateViewTest(BaseSetUpMixin,
                                   ResumeItemUpdateViewTestMixin,
                                   CreateMethodsMixin,
                                   TestCase):
    def setUp(self):
        self.model = WorkExpSection
        self.data = {
            'title': 'New title',
        }
        super().setUp()
        ResumeItemUpdateViewTestMixin.setUp(self, url_name='work_exp_section_update')


class WorkExpSectionDeleteViewTest(BaseSetUpMixin,
                                   ResumeItemDeleteViewTestMixin,
                                   CreateMethodsMixin,
                                   TestCase):
    def setUp(self):
        self.model = WorkExpSection
        self.view = WorkExpSectionDeleteView()

        super().setUp()
        ResumeItemDeleteViewTestMixin.setUp(self, url_name='work_exp_section_delete')

    @expectedFailure
    def test_updates_rating(self):
        super().test_updates_rating()


class JobCreateViewTest(ResumeItemCreateViewTestMixin,
                        BaseSetUpMixin,
                        CreateMethodsMixin,
                        TestCase):
    def setUp(self):
        super().setUp(url_name='work_exp_section_create')
        self.work_exp_section = WorkExpSection.objects.create(resume=self.resume)
        self.url = reverse('job_create', kwargs={'username': self.user1.username,
                                                 'slug': self.resume.slug,
                                                 'section': self.work_exp_section.pk})
        self.model = Job

    def test_open_modal_if_success(self):
        self.client.login(username=self.user1.username, password='testpassword')
        response = self.client.post(self.url, self.data, HTTP_REFERER=self.referer)

        obj = self.model.objects.filter(work_exp_section=self.work_exp_section).first()

        self.assertEqual(response.status_code, 302)
        self.assertIn(f'modal_id={obj.pk}', response.url)
        self.assertIn(self.referer, response.url)

    def test_with_owner(self):
        self.client.login(username=self.user1.username, password='testpassword')
        response = self.client.post(self.url, self.data, HTTP_REFERER=self.referer)

        obj_set = self.model.objects.filter(work_exp_section=self.work_exp_section).all()

        self.assertEqual(response.status_code, 302)
        self.assertIn(f'modal_id={obj_set.first().pk}', response.url)
        self.assertEqual(obj_set.count(), 1)


class JobUpdateViewTest(BaseSetUpMixin,
                        ResumeItemUpdateViewTestMixin,
                        CreateMethodsMixin,
                        TestCase):
    def setUp(self):
        super().setUp()
        self.model = Job
        self.data = {
            'title': 'New title',
            'description': 'New description'
        }
        self.work_exp_section = WorkExpSection.objects.create(resume=self.resume)
        self.object = self.model.objects.create(work_exp_section=self.work_exp_section)
        self.url = reverse('job_update', kwargs={'pk': self.object.pk,
                                                 'username': self.user1.username,
                                                 'slug': self.resume.slug,
                                                 'section': self.work_exp_section.pk})

        self.referer = reverse('resume', kwargs={'username': self.user1.username,
                                                 'slug': self.resume.slug}) \
            + '?modal_id=' + str(self.object.pk)


class JobDeleteViewTest(BaseSetUpMixin,
                        ResumeItemDeleteViewTestMixin,
                        CreateMethodsMixin,
                        TestCase):
    def setUp(self):
        super().setUp()
        self.model = Job
        self.view = JobDeleteView
        self.work_exp_section = WorkExpSection.objects.create(resume=self.resume)

        self.object = self.model.objects.create(work_exp_section=self.work_exp_section)
        for _ in range(3):
            self.model.objects.create(work_exp_section=self.work_exp_section, title=str(uuid4())[:4])

        self.url = reverse('job_delete', kwargs={'pk': self.object.pk,
                                                 'username': self.user1.username,
                                                 'slug': self.resume.slug,
                                                 'section': self.work_exp_section.pk})

        self.referer = reverse('resume', kwargs={'username': self.user1.username,
                                                 'slug': self.resume.slug})
        self.data = {}

    def test_with_owner(self):
        self.client.login(username=self.user1.username, password='testpassword')

        obj_count_before = self.model.objects.count()
        response = self.client.post(self.url, self.data, HTTP_REFERER=self.referer)
        obj_count_after = self.model.objects.count()

        self.assertEqual(response.status_code, 302)
        self.assertNotIn('modal_id=', response.url)
        self.assertEqual(obj_count_before - obj_count_after, 1)
        with self.assertRaises(self.model.DoesNotExist):
            self.model.objects.get(work_exp_section=self.work_exp_section, title='New Object')