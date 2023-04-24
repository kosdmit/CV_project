import re
import uuid

from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from app_resume.validators import percentage_validator, years_interval_validator


# Create your models here.
class Resume(models.Model):
    profile = models.ForeignKey('app_users.Profile', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    slug = AutoSlugField(populate_from='position')
    position = models.CharField(max_length=150)
    about_me = models.TextField(blank=True, null=True)
    soft_skills = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_primary:
            try:
                temp = Resume.objects.get(is_primary=True, user=self.user)
                if self != temp:
                    temp.is_primary = False
                    temp.save()
            except Resume.DoesNotExist:
                pass
        super(Resume, self).save(*args, **kwargs)


class MainEducation(models.Model):
    EDUCATION_LEVELS = [
        ('Basic General', 'Основное общее образование'),
        ('Secondary General', 'Cреднее (полное) общее образование'),
        ('Vocational education', 'Cреднее профессиональное образование'),
        ('Higher education', 'Высшее образование'),
    ]

    DEGREES = [
        ('Other', 'Другое'),
        ('Bachelor', 'Бакалавр'),
        ('Specialist', 'Специалист'),
        ('Master', 'Магистр'),
    ]

    resume = models.OneToOneField('Resume', on_delete=models.CASCADE)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    level = models.CharField(max_length=25, choices=EDUCATION_LEVELS)
    degree = models.CharField(max_length=10, choices=DEGREES, blank=True, null=True)

    def get_level(self):
        return dict(self.EDUCATION_LEVELS).get(self.level)

    def get_degree(self):
        return dict(self.DEGREES).get(self.degree)


class Institution(models.Model):
    main_education = models.ForeignKey('MainEducation', on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    diploma = models.FileField(upload_to='files/main_diplomas/', blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)


class AdditionalEducation(models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    diploma = models.FileField(upload_to='files/additional_diplomas/', blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)


class ElectronicCertificate(models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    slug = AutoSlugField(populate_from='title')
    title = models.CharField(max_length=150)
    certificate_url = models.URLField(blank=True, null=True)
    certificate = models.FileField(upload_to='files/certificates/', blank=True, null=True)
    completion_percentage = models.IntegerField(blank=True, null=True, validators=[percentage_validator])
    completion_date = models.DateField(blank=True, null=True)


class Skill(models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=45)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class WorkExpSection(models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=150)
    start_date = models.DateField(blank=True, null=True)
    finish_date = models.DateField(blank=True, null=True)


class Job(models.Model):
    work_exp_section = models.ForeignKey('WorkExpSection', on_delete=models.CASCADE)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    project_url = models.URLField(blank=True, null=True)
    git_url = models.URLField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    finish_date = models.DateField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    position = models.CharField(max_length=150, blank=True, null=True)
    company = models.CharField(max_length=150, blank=True, null=True)
    company_url = models.URLField(blank=True, null=True)
