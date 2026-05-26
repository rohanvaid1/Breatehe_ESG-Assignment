import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Organization(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    industry = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)
    timezone = models.CharField(max_length=64, default='UTC')
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        ANALYST = 'analyst', 'Analyst'
        VIEWER = 'viewer', 'Viewer'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='users', null=True, blank=True
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ANALYST)
    email = models.EmailField(unique=True)

    def __str__(self) -> str:
        return f"{self.username} ({self.organization_id})"
