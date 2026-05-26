from rest_framework import serializers

from tenancy.serializers import UserSerializer

from .models import AnalystReview, AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    performed_by = UserSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            'id',
            'organization',
            'record',
            'action',
            'performed_by',
            'previous_value',
            'new_value',
            'note',
            'created_at',
        )


class AnalystReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)

    class Meta:
        model = AnalystReview
        fields = (
            'id',
            'organization',
            'record',
            'reviewer',
            'status',
            'comment',
            'previous_value',
            'new_value',
            'created_at',
        )
