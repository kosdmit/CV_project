import uuid

from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Like(models.Model):
    owner_id = models.CharField(max_length=40)
    uuid_key = models.UUIDField()

    def __str__(self):
        return f"Like {self.id} by {self.user.username}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid_key = models.UUIDField()

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    message = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

