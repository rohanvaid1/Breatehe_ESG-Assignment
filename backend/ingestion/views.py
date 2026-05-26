from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.conf import settings
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from audits.models import AnalystReview, AuditLog
from tenancy.permissions import IsAnalystOrAdmin, IsOrgAdmin, IsViewerOrAbove, ReadOnlyUnlessAdmin

from .models import (
    AirportLookup,
    AnomalyFlag,
    EmissionCategory,
    NormalizedRecord,
    PlantLookup,
    SourceSystem,
    UnitConversion,
    UploadBatch,
)
from .serializers import (
    AirportLookupSerializer,
    AnomalyFlagSerializer,
    EmissionCategorySerializer,
    NormalizedRecordSerializer,
    NormalizedRecordUpdateSerializer,
    PlantLookupSerializer,
    SourceSystemSerializer,
    UnitConversionSerializer,
    UploadBatchCreateSerializer,
    UploadBatchSerializer,
)
from .tasks import process_upload_batch


class OrganizationScopedViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return queryset
        if hasattr(queryset.model, 'organization'):
            return queryset.filter(organization=user.organization)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(serializer.Meta.model, 'organization') and not user.is_superuser:
            serializer.save(organization=user.organization)
        else:
            serializer.save()


class SourceSystemViewSet(OrganizationScopedViewSet):
    queryset = SourceSystem.objects.all().order_by('name')
    serializer_class = SourceSystemSerializer
    permission_classes = [ReadOnlyUnlessAdmin]
    filterset_fields = ('source_type', 'is_active')
    search_fields = ('name',)


class UploadBatchViewSet(OrganizationScopedViewSet):
    queryset = UploadBatch.objects.select_related('source_system', 'uploaded_by').all().order_by('-created_at')
    permission_classes = [IsAnalystOrAdmin]
    filterset_fields = ('status', 'source_system')
    search_fields = ('original_filename',)
    ordering_fields = ('created_at', 'status')

    def get_serializer_class(self):
        if self.action == 'create':
            return UploadBatchCreateSerializer
        return UploadBatchSerializer

    def perform_create(self, serializer):
        user = self.request.user
        file_obj = self.request.data.get('file')
        if not file_obj:
            raise ValidationError({'file': 'CSV file is required.'})
        if not str(file_obj.name).lower().endswith('.csv'):
            raise ValidationError({'file': 'Only CSV files are supported.'})
        if file_obj.size and file_obj.size > settings.DATA_UPLOAD_MAX_MEMORY_SIZE:
            raise ValidationError({'file': 'File exceeds upload size limit.'})
        batch = serializer.save(
            organization=user.organization,
            uploaded_by=user,
            original_filename=getattr(file_obj, 'name', 'upload.csv'),
        )
        # Try async via Celery; fall back to synchronous processing if broker unavailable
        try:
            process_upload_batch.delay(str(batch.id))
        except Exception:
            process_upload_batch(str(batch.id))


class NormalizedRecordViewSet(OrganizationScopedViewSet):
    queryset = NormalizedRecord.objects.select_related(
        'source_system', 'upload_batch', 'emission_category'
    ).prefetch_related('anomalies')
    serializer_class = NormalizedRecordSerializer
    permission_classes = [IsViewerOrAbove]
    filterset_fields = ('status', 'emission_scope', 'source_system', 'is_anomalous', 'upload_batch')
    search_fields = ('source_system__name', 'emission_scope', 'status')
    ordering_fields = ('created_at', 'estimated_emissions')

    def get_permissions(self):
        if self.action in {'approve', 'reject', 'comment', 'update', 'partial_update', 'bulk_approve'}:
            return [IsAnalystOrAdmin()]
        return [IsViewerOrAbove()]

    def get_serializer_class(self):
        if self.action in {'update', 'partial_update'}:
            return NormalizedRecordUpdateSerializer
        return NormalizedRecordSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        record = self.get_object()
        if record.locked_at:
            return Response({'detail': 'Record is locked after approval.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(record, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        previous_value = NormalizedRecordSerializer(record).data
        updated = serializer.save(last_edited_by=request.user, last_edited_at=timezone.now())
        AnalystReview.objects.create(
            organization=record.organization,
            record=record,
            reviewer=request.user,
            status=AnalystReview.Status.EDITED,
            comment='Normalized values edited.',
            previous_value=previous_value,
            new_value=NormalizedRecordSerializer(updated).data,
        )
        AuditLog.objects.create(
            organization=record.organization,
            record=record,
            action=AuditLog.Action.UPDATE,
            performed_by=request.user,
            previous_value=previous_value,
            new_value=NormalizedRecordSerializer(updated).data,
            note='Normalized values edited.',
        )
        return Response(NormalizedRecordSerializer(updated).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        record = self.get_object()
        if record.locked_at:
            return Response({'detail': 'Record already locked.'}, status=status.HTTP_400_BAD_REQUEST)
        record.status = NormalizedRecord.Status.APPROVED
        record.locked_at = timezone.now()
        record.reviewed_by = request.user
        record.reviewed_at = timezone.now()
        record.save(update_fields=['status', 'locked_at', 'reviewed_by', 'reviewed_at'])
        AnalystReview.objects.create(
            organization=record.organization,
            record=record,
            reviewer=request.user,
            status=AnalystReview.Status.APPROVED,
            comment=request.data.get('comment', ''),
        )
        AuditLog.objects.create(
            organization=record.organization,
            record=record,
            action=AuditLog.Action.APPROVE,
            performed_by=request.user,
            note='Record approved.',
        )
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        record = self.get_object()
        if record.locked_at:
            return Response({'detail': 'Record already locked.'}, status=status.HTTP_400_BAD_REQUEST)
        record.status = NormalizedRecord.Status.REJECTED
        record.reviewed_by = request.user
        record.reviewed_at = timezone.now()
        record.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])
        AnalystReview.objects.create(
            organization=record.organization,
            record=record,
            reviewer=request.user,
            status=AnalystReview.Status.REJECTED,
            comment=request.data.get('comment', ''),
        )
        AuditLog.objects.create(
            organization=record.organization,
            record=record,
            action=AuditLog.Action.REJECT,
            performed_by=request.user,
            note='Record rejected.',
        )
        return Response({'status': 'rejected'})

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        record = self.get_object()
        AnalystReview.objects.create(
            organization=record.organization,
            record=record,
            reviewer=request.user,
            status=AnalystReview.Status.COMMENTED,
            comment=request.data.get('comment', ''),
        )
        AuditLog.objects.create(
            organization=record.organization,
            record=record,
            action=AuditLog.Action.COMMENT,
            performed_by=request.user,
            note=request.data.get('comment', ''),
        )
        return Response({'status': 'commented'})

    @action(detail=False, methods=['post'])
    def bulk_approve(self, request):
        ids = request.data.get('ids', [])
        records = self.get_queryset().filter(id__in=ids, locked_at__isnull=True)
        for record in records:
            record.status = NormalizedRecord.Status.APPROVED
            record.locked_at = timezone.now()
            record.reviewed_by = request.user
            record.reviewed_at = timezone.now()
            record.save(update_fields=['status', 'locked_at', 'reviewed_by', 'reviewed_at'])
            AnalystReview.objects.create(
                organization=record.organization,
                record=record,
                reviewer=request.user,
                status=AnalystReview.Status.APPROVED,
                comment='Bulk approval.',
            )
            AuditLog.objects.create(
                organization=record.organization,
                record=record,
                action=AuditLog.Action.APPROVE,
                performed_by=request.user,
                note='Record approved in bulk.',
            )
        return Response({'approved': records.count()})


class AnomalyFlagViewSet(OrganizationScopedViewSet):
    queryset = AnomalyFlag.objects.select_related('record').all().order_by('-created_at')
    serializer_class = AnomalyFlagSerializer
    permission_classes = [IsViewerOrAbove]
    filterset_fields = ('code', 'severity', 'record')


class EmissionCategoryViewSet(OrganizationScopedViewSet):
    queryset = EmissionCategory.objects.all().order_by('scope')
    serializer_class = EmissionCategorySerializer
    permission_classes = [ReadOnlyUnlessAdmin]


class UnitConversionViewSet(OrganizationScopedViewSet):
    queryset = UnitConversion.objects.all()
    serializer_class = UnitConversionSerializer
    permission_classes = [ReadOnlyUnlessAdmin]


class PlantLookupViewSet(OrganizationScopedViewSet):
    queryset = PlantLookup.objects.all()
    serializer_class = PlantLookupSerializer
    permission_classes = [ReadOnlyUnlessAdmin]
    filterset_fields = ('plant_code',)


class AirportLookupViewSet(OrganizationScopedViewSet):
    queryset = AirportLookup.objects.all()
    serializer_class = AirportLookupSerializer
    permission_classes = [ReadOnlyUnlessAdmin]
    search_fields = ('code', 'city', 'country')


class DashboardMetricsView(APIView):
    permission_classes = [IsViewerOrAbove]

    def get(self, request):
        user = request.user
        records = NormalizedRecord.objects.all()
        if not user.is_superuser:
            records = records.filter(organization=user.organization)

        cards = {
            'total_uploaded_rows': records.count(),
            'anomaly_count': records.filter(is_anomalous=True).count(),
            'approval_pending': records.filter(status=NormalizedRecord.Status.PENDING).count(),
            'approved_rows': records.filter(status=NormalizedRecord.Status.APPROVED).count(),
            'rejected_rows': records.filter(status=NormalizedRecord.Status.REJECTED).count(),
        }

        by_source = (
            records.values('source_system__source_type')
            .annotate(emissions=Sum('estimated_emissions'), count=Count('id'))
            .order_by('source_system__source_type')
        )
        by_scope = (
            records.values('emission_scope')
            .annotate(emissions=Sum('estimated_emissions'), count=Count('id'))
            .order_by('emission_scope')
        )
        monthly_raw = (
            records.annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(emissions=Sum('estimated_emissions'))
            .order_by('month')
        )
        monthly = [
            {
                'month': row['month'].strftime('%b %Y') if row['month'] else '',
                'emissions': row['emissions'],
            }
            for row in monthly_raw
        ]

        # Serialize Decimal fields to float for JSON
        def _to_float(val):
            try:
                return float(val) if val is not None else None
            except (TypeError, ValueError):
                return None

        by_source_clean = [
            {**row, 'emissions': _to_float(row['emissions'])}
            for row in by_source
        ]
        by_scope_clean = [
            {**row, 'emissions': _to_float(row['emissions'])}
            for row in by_scope
        ]
        monthly_clean = [
            {**row, 'emissions': _to_float(row['emissions'])}
            for row in monthly
        ]

        return Response(
            {
                'cards': cards,
                'emissions_by_source': by_source_clean,
                'emissions_by_scope': by_scope_clean,
                'monthly_trends': monthly_clean,
            }
        )


class HealthCheckView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({'status': 'ok'})
