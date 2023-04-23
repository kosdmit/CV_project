import django
from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Profile(models.Model):
    GENDERS = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    birthday_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=6, blank=True, null=True, choices=GENDERS)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def get_gender(self):
        return dict(self.GENDERS).get(self.gender)


class SocialLinks(models.Model):
    profile = models.OneToOneField('Profile', on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    twitter = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    linked_in = models.URLField(blank=True, null=True)
    vk = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    hh = models.URLField(blank=True, null=True)
    git_hub = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Social Links"
        verbose_name_plural = "Social Links"