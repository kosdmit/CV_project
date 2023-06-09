from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver

from app_social.model_mixins import CompressImageBeforeSaveMixin
from app_users.validators import phone_number_validator


# Create your models here.
class Profile(CompressImageBeforeSaveMixin, models.Model):
    def __init__(self, *args, **kwargs):
        self.image_width = 250
        self.image_name_suffix = 'user_image'
        super().__init__(*args, **kwargs)

    GENDERS = [
        ('M', 'Муж'),
        ('F', 'Жен'),
        ('O', 'Другой'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)

    birthday_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=6, blank=True, null=True, choices=GENDERS)
    phone_number = models.CharField(max_length=15, blank=True, null=True, validators=[phone_number_validator,])
    image = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def get_gender(self):
        return dict(self.GENDERS).get(self.gender)

    def __str__(self):
        return f'{self.user.username}`s Profile object'

    def delete(self, *args, **kwargs):
        self.image.delete(save=False)
        super().delete(*args, **kwargs)


class SocialLinks(models.Model):
    profile = models.OneToOneField('Profile', on_delete=models.CASCADE, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)

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

    def __str__(self):
        return f'{self.user.username}`s SocialLinks object'