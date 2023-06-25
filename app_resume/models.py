import uuid

from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.db import models

from app_resume.validators import percentage_validator


class RepresentationForResumesObjectMixin:
    def __str__(self):
        return f'{type(self).__name__} object for {self.resume.position}' \
               f' resume by {self.resume.user.username}'


# Create your models here.
class Resume(models.Model):
    profile = models.ForeignKey('app_users.Profile', on_delete=models.CASCADE, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    slug = AutoSlugField(populate_from='position', unique_with='user')
    position = models.CharField(max_length=150)
    about_me = models.TextField(blank=True, null=True)
    soft_skills = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_primary = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)

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

    def __str__(self):
        return f'Resume object for {self.position} position by {self.user.username}'


class MainEducation(RepresentationForResumesObjectMixin, models.Model):
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

    resume = models.OneToOneField('Resume', on_delete=models.CASCADE, editable=False)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    level = models.CharField(max_length=25, choices=EDUCATION_LEVELS, default='Basic General')
    degree = models.CharField(max_length=10, choices=DEGREES, blank=True, null=True)

    def get_level(self):
        return dict(self.EDUCATION_LEVELS).get(self.level)

    def get_degree(self):
        return dict(self.DEGREES).get(self.degree)


class Institution(RepresentationForResumesObjectMixin, models.Model):
    main_education = models.ForeignKey('MainEducation', on_delete=models.CASCADE, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, editable=False)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=150, blank=True, null=False, default='New Object')
    description = models.TextField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    diploma = models.FileField(upload_to='files/main_diplomas/', blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_primary:
            try:
                temp = Institution.objects.get(is_primary=True, resume=self.resume)
                if self != temp:
                    temp.is_primary = False
                    temp.save()
            except Institution.DoesNotExist:
                pass
        super().save(*args, **kwargs)


class AdditionalEducation(RepresentationForResumesObjectMixin, models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE, editable=False)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=150, blank=True, null=False, default='New Object')
    description = models.TextField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    diploma = models.FileField(upload_to='files/additional_diplomas/', blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)


class ElectronicCertificate(RepresentationForResumesObjectMixin, models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE, editable=False)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    slug = AutoSlugField(populate_from='title', unique_with='resume')
    title = models.CharField(max_length=150, blank=True, null=False, default='New Object')
    certificate_url = models.URLField(blank=True, null=True)
    certificate = models.FileField(upload_to='files/certificates/', blank=True, null=True)
    completion_percentage = models.IntegerField(blank=True, null=True, validators=[percentage_validator])
    completion_date = models.DateField(blank=True, null=True)


class Skill(RepresentationForResumesObjectMixin, models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE, editable=False)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=45)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class WorkExpSection(RepresentationForResumesObjectMixin, models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE, editable=False)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=150, blank=True, null=False, default='New Object')
    start_date = models.DateField(blank=True, null=True)
    finish_date = models.DateField(blank=True, null=True)


class Job(models.Model):
    work_exp_section = models.ForeignKey('WorkExpSection', on_delete=models.CASCADE, editable=False)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=150, blank=True, null=False, default='New Object')
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

    def __str__(self):
        return f'{type(self).__name__} object for {self.work_exp_section.resume.position}' \
               f' resume by {self.work_exp_section.resume.user.username}'
