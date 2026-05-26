import uuid

from django.conf import settings
from django.db import models

from tenancy.models import Organization, TimeStampedModel


class AuditLog(TimeStampedModel):
    class Action(models.TextChoices):
        UPLOAD = 'upload', 'Upload'
        NORMALIZE = 'normalize', 'Normalize'
        UPDATE = 'update', 'Update'
        APPROVE = 'approve', 'Approve'
        REJECT = 'reject', 'Reject'
        COMMENT = 'comment', 'Comment'
        LOCK = 'lock', 'Lock'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='audit_logs')
    record = models.ForeignKey(
        'ingestion.NormalizedRecord', on_delete=models.CASCADE, related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='audit_actions'
    )
    previous_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    note = models.TextField(blank=True)


class AnalystReview(TimeStampedModel):
    class Status(models.TextChoices):
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        EDITED = 'edited', 'Edited'
        COMMENTED = 'commented', 'Commented'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='analyst_reviews')
    record = models.ForeignKey(
        'ingestion.NormalizedRecord', on_delete=models.CASCADE, related_name='reviews'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='analyst_reviews'
    )
    status = models.CharField(max_length=20, choices=Status.choices)
    comment = models.TextField(blank=True)
    previous_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
