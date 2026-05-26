import uuid

from django.conf import settings
from django.db import models

from tenancy.models import Organization, TimeStampedModel


class SourceType(models.TextChoices):
    SAP = 'sap', 'SAP Fuel & Procurement'
    UTILITY = 'utility', 'Utility Electricity'
    TRAVEL = 'travel', 'Corporate Travel'


class SourceSystem(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=32, choices=SourceType.choices)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.source_type})"


class UploadBatch(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='upload_batches')
    source_system = models.ForeignKey(SourceSystem, on_delete=models.PROTECT, related_name='upload_batches')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='uploads'
    )
    file = models.FileField(upload_to='uploads/%Y/%m/')
    original_filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_rows = models.PositiveIntegerField(default=0)
    success_rows = models.PositiveIntegerField(default=0)
    failed_rows = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.source_system} - {self.original_filename}"


class RawRecord(TimeStampedModel):
    class Status(models.TextChoices):
        PARSED = 'parsed', 'Parsed'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='raw_records')
    source_system = models.ForeignKey(SourceSystem, on_delete=models.PROTECT, related_name='raw_records')
    upload_batch = models.ForeignKey(UploadBatch, on_delete=models.CASCADE, related_name='raw_records')
    row_number = models.PositiveIntegerField()
    raw_data = models.JSONField()
    raw_hash = models.CharField(max_length=64)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PARSED)
    errors = models.JSONField(null=True, blank=True)

    class Meta:
        unique_together = ('upload_batch', 'row_number')


class EmissionCategory(TimeStampedModel):
    class Scope(models.TextChoices):
        SCOPE_1 = 'scope_1', 'Scope 1'
        SCOPE_2 = 'scope_2', 'Scope 2'
        SCOPE_3 = 'scope_3', 'Scope 3'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=60, unique=True)
    name = models.CharField(max_length=255)
    scope = models.CharField(max_length=20, choices=Scope.choices)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.scope})"


class UnitConversion(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_unit = models.CharField(max_length=40)
    to_unit = models.CharField(max_length=40)
    multiplier = models.DecimalField(max_digits=18, decimal_places=6)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('from_unit', 'to_unit')


class PlantLookup(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='plants')
    plant_code = models.CharField(max_length=40)
    plant_name = models.CharField(max_length=255)
    region = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)

    class Meta:
        unique_together = ('organization', 'plant_code')


class AirportLookup(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=5, unique=True)
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=120)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)


class NormalizedRecord(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='normalized_records')
    source_system = models.ForeignKey(SourceSystem, on_delete=models.PROTECT, related_name='normalized_records')
    upload_batch = models.ForeignKey(UploadBatch, on_delete=models.CASCADE, related_name='normalized_records')
    raw_record = models.OneToOneField(RawRecord, on_delete=models.CASCADE, related_name='normalized_record')
    emission_category = models.ForeignKey(
        EmissionCategory, on_delete=models.SET_NULL, null=True, related_name='records'
    )
    emission_scope = models.CharField(max_length=20, choices=EmissionCategory.Scope.choices)
    activity_quantity = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    activity_unit = models.CharField(max_length=20, blank=True)
    normalized_quantity = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    normalized_unit = models.CharField(max_length=20, blank=True)
    emission_factor = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    estimated_emissions = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    currency = models.CharField(max_length=10, blank=True)
    cost = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    data = models.JSONField(default=dict)
    conversion_metadata = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    is_anomalous = models.BooleanField(default=False)
    source_row_hash = models.CharField(max_length=64, blank=True)
    locked_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    last_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='edits'
    )
    last_edited_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.source_system} - {self.id}"


class AnomalyFlag(TimeStampedModel):
    class Severity(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(NormalizedRecord, on_delete=models.CASCADE, related_name='anomalies')
    code = models.CharField(max_length=60)
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM)
