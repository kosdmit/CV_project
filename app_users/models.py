import django
from django.db import models


# Create your models here.
class Profile(models.Model):
    birthday_date = models.DateField(blank=True)
    gender = models.CharField(max_length=6, blank=True, choices=[('male', 'male'),
                                                                 ('female', 'female'),
                                                                 ])
    phone_number = models.CharField(max_length=15, blank=True)

    social_links = models.OneToOneField('SocialLinks', on_delete=models.CASCADE)
    user = models.OneToOneField(django.contrib.auth.models.User, on_delete=models.CASCADE)


class SocialLinks(models.Model):
    twitter = models.CharField(max_length=150, blank=True)
    facebook = models.CharField(max_length=150, blank=True)
    linked_in = models.CharField(max_length=150, blank=True)
    vk = models.CharField(max_length=150, blank=True)
    instagram = models.CharField(max_length=150, blank=True)
    hh = models.CharField(max_length=150, blank=True)
