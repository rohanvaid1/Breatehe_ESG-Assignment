from rest_framework import viewsets

from tenancy.permissions import IsAnalystOrAdmin, IsViewerOrAbove

from .models import AnalystReview, AuditLog
from .serializers import AnalystReviewSerializer, AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsViewerOrAbove]
    filterset_fields = ('action', 'record', 'organization')
    search_fields = ('note',)
    ordering_fields = ('created_at',)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return AuditLog.objects.all().order_by('-created_at')
        return AuditLog.objects.filter(organization=user.organization).order_by('-created_at')


class AnalystReviewViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AnalystReviewSerializer
    permission_classes = [IsAnalystOrAdmin]
    filterset_fields = ('status', 'record', 'organization')
    search_fields = ('comment',)
    ordering_fields = ('created_at',)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return AnalystReview.objects.all().order_by('-created_at')
        return AnalystReview.objects.filter(organization=user.organization).order_by('-created_at')
