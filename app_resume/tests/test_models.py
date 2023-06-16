from django.test import TestCase

from app_resume.models import Resume, Institution, MainEducation
from app_resume.tests.test_mixins import CreateMethodsMixin


class ResumeModelTestCase(CreateMethodsMixin, TestCase):
    def setUp(self):
        self.user, self.profile, self.social_links = \
            self.create_user(username='kosdmit', return_set=True)

        self.object1 = Resume.objects.create(profile=self.profile,
                                             user=self.user,
                                             position='Python Developer',
                                             is_primary=True)

        self.object2 = Resume.objects.create(profile=self.profile,
                                             user=self.user,
                                             position='Python Developer',
                                             is_primary=True)

    def test_unique_slug(self):
        self.assertNotEqual(self.object1.slug, self.object2.slug)

    def test_primary_setting(self):
        self.object1.refresh_from_db()

        self.assertFalse(self.object1.is_primary)
        self.assertTrue(self.object2.is_primary)


class InstitutionModelTestCase(CreateMethodsMixin, TestCase):
    def setUp(self):
        self.user, self.profile, self.social_links = \
            self.create_user(username='kosdmit', return_set=True)

        self.resume = self.create_resume()
        self.main_education = MainEducation.objects.create(resume=self.resume)

    def test_primary_setting(self):
        self.object1 = Institution.objects.create(resume=self.resume,
                                                  main_education=self.main_education,
                                                  is_primary=True)

        self.object2 = Institution.objects.create(resume=self.resume,
                                                  main_education=self.main_education,
                                                  is_primary=True)

        self.object1.refresh_from_db()

        self.assertFalse(self.object1.is_primary)
        self.assertTrue(self.object2.is_primary)




