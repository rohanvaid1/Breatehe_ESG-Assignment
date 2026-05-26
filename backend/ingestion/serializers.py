from rest_framework import serializers

from audits.models import AnalystReview
from tenancy.serializers import UserSerializer

from .models import (
    AirportLookup,
    AnomalyFlag,
    EmissionCategory,
    NormalizedRecord,
    PlantLookup,
    RawRecord,
    SourceSystem,
    UnitConversion,
    UploadBatch,
)


class SourceSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceSystem
        fields = ('id', 'name', 'source_type', 'description', 'is_active', 'created_at', 'updated_at')


class UploadBatchSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    source_system = SourceSystemSerializer(read_only=True)

    class Meta:
        model = UploadBatch
        fields = (
            'id',
            'organization',
            'source_system',
            'uploaded_by',
            'file',
            'original_filename',
            'status',
            'total_rows',
            'success_rows',
            'failed_rows',
            'started_at',
            'completed_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'status',
            'total_rows',
            'success_rows',
            'failed_rows',
            'started_at',
            'completed_at',
            'created_at',
            'updated_at',
        )


class UploadBatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadBatch
        fields = ('id', 'organization', 'source_system', 'file', 'original_filename')
        extra_kwargs = {'organization': {'read_only': True}, 'original_filename': {'required': False}}


class RawRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawRecord
        fields = (
            'id',
            'upload_batch',
            'row_number',
            'raw_data',
            'raw_hash',
            'status',
            'errors',
            'created_at',
        )


class AnomalyFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnomalyFlag
        fields = ('id', 'code', 'message', 'severity', 'created_at')


class NormalizedRecordSerializer(serializers.ModelSerializer):
    anomalies = AnomalyFlagSerializer(many=True, read_only=True)
    reviewed_by = UserSerializer(read_only=True)
    source_system = SourceSystemSerializer(read_only=True)

    class Meta:
        model = NormalizedRecord
        fields = (
            'id',
            'organization',
            'source_system',
            'upload_batch',
            'raw_record',
            'emission_category',
            'emission_scope',
            'activity_quantity',
            'activity_unit',
            'normalized_quantity',
            'normalized_unit',
            'emission_factor',
            'estimated_emissions',
            'currency',
            'cost',
            'data',
            'conversion_metadata',
            'status',
            'is_anomalous',
            'locked_at',
            'reviewed_by',
            'reviewed_at',
            'last_edited_by',
            'last_edited_at',
            'source_row_hash',
            'anomalies',
            'created_at',
            'updated_at',
        )


class NormalizedRecordUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormalizedRecord
        fields = (
            'activity_quantity',
            'activity_unit',
            'normalized_quantity',
            'normalized_unit',
            'emission_factor',
            'estimated_emissions',
            'currency',
            'cost',
            'data',
        )


class EmissionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionCategory
        fields = ('id', 'key', 'name', 'scope', 'description')


class UnitConversionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitConversion
        fields = ('id', 'from_unit', 'to_unit', 'multiplier', 'notes')


class PlantLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantLookup
        fields = ('id', 'organization', 'plant_code', 'plant_name', 'region', 'country')


class AirportLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirportLookup
        fields = ('id', 'code', 'city', 'country', 'latitude', 'longitude')


class AnalystReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)

    class Meta:
        model = AnalystReview
        fields = (
            'id',
            'record',
            'reviewer',
            'status',
            'comment',
            'previous_value',
            'new_value',
            'created_at',
        )
