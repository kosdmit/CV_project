import uuid

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from app_social.model_mixins import CompressImageBeforeSaveMixin


# Create your models here.
class Like(models.Model):
    owner_id = models.CharField(max_length=40)
    uuid_key = models.UUIDField()

    def __str__(self):
        return f"Like {self.id} by {self.user.username}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, editable=False)
    owner_id = models.CharField(max_length=40, editable=False)
    uuid_key = models.UUIDField(editable=False)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    message = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        if self.user:
            return f"Comment by {self.user.username}"
        else:
            return f"Comment by unknown user"


class Post(CompressImageBeforeSaveMixin, models.Model):
    def __init__(self, *args, **kwargs):
        self.image_width = 642
        self.image_name_suffix = 'post_image'
        super().__init__(*args, **kwargs)

    resume = models.ForeignKey('app_resume.Resume', on_delete=models.CASCADE, editable=False)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    message = models.TextField()
    image = models.ImageField(upload_to='files/post_images/', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True)

@receiver(post_delete, sender=Post)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(save=False)

