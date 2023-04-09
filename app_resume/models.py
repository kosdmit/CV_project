import re

from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.


def interval_validator(value):
    pattern = '^\d{4} - \d{4}$'
    if not re.match(pattern, value):
        raise ValidationError(
            message=f"{value} does not mathc the pattern for years interval",
            params={'value': value,
                    'pattern': pattern,
                    }
        )


class Resume(models.Model):
    profile = models.ForeignKey('app_users.Profile', on_delete=models.CASCADE)

    id = models.UUIDField(primary_key=True, editable=False)
    position = models.CharField(max_length=150)
    about_me = models.TextField(blank=True, null=True)
    soft_skills = models.TextField(blank=True, null=True)


class MainEducation(models.Model):
    EDUCATION_LEVELS = [
        ('Basic General', 'Основное общее образование'),
        ('Secondary General', 'Cреднее (полное) общее образование'),
        ('Vocational education', 'Cреднее профессиональное образование'),
        ('Higher education', 'Высшее образование'),
    ]

    DEGREES = [
        ('Bachelor', 'Бакалавр'),
        ('Specialist', 'Специалист'),
        ('Master', 'Магистр'),
    ]

    resume = models.OneToOneField('Resume', on_delete=models.CASCADE)

    level = models.CharField(max_length=25, choices=EDUCATION_LEVELS)
    degree = models.CharField(max_length=10, choices=DEGREES, blank=True, null=True)


class Institution(models.Model):
    main_education = models.ForeignKey('MainEducation', on_delete=models.CASCADE)

    id = models.UUIDField(primary_key=True, editable=False)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    diploma = models.FileField(upload_to='files/main_diplomas/', blank=True, null=True)


class AdditionalEducation(models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE)

    id = models.UUIDField(primary_key=True, editable=False)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    diploma = models.FileField(upload_to='files/additional_diplomas/', blank=True, null=True)


class ElectronicCertificate(models.Model):
    @staticmethod
    def percentage_validator(value):
        if value > 100 or value < 0:
            raise ValidationError(
                message=f"{value} must be in 0 - 100 interval",
                params={'value': value}
            )

    resume = models.ForeignKey('Resume', on_delete=models.CASCADE)

    id = models.UUIDField(primary_key=True, editable=False)
    title = models.CharField(max_length=150)
    certificate_url = models.URLField(blank=True, null=True)
    certificate = models.FileField(upload_to='files/certificates/', blank=True, null=True)
    completion_percentage = models.IntegerField(blank=True, null=True, validators=[percentage_validator])


class Skill(models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE)

    id = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=45)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class WorkExpSection(models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE)

    title = models.CharField(max_length=150)
    years_interval = models.CharField(max_length=11, validators=[interval_validator], blank=True, null=True)


class Job(models.Model):
    work_exp_section = models.ForeignKey('WorkExpSection', on_delete=models.CASCADE)

    id = models.UUIDField(primary_key=True, editable=False)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    project_url = models.URLField(blank=True, null=True)
    git_url = models.URLField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    finish_date = models.DateField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    position = models.CharField(max_length=150)
    company = models.CharField(max_length=150)
    years_interval = models.CharField(max_length=11, validators=[interval_validator], blank=True, null=True)
