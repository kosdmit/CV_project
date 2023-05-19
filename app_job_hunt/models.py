import uuid

from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    raw_contact = models.CharField(max_length=150, null=True)
    company = models.CharField(max_length=150, blank=True, null=True)
    position = models.CharField(max_length=150, blank=True, null=True)
    name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)

