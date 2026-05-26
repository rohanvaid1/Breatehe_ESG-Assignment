import csv
import io
import logging

from celery import shared_task
from django.utils import timezone

from audits.models import AuditLog

from .anomaly import detect_utility_anomalies
from .models import (
    AirportLookup,
    AnomalyFlag,
    EmissionCategory,
    NormalizedRecord,
    RawRecord,
    SourceType,
    UploadBatch,
)
from .normalization import normalize_sap_row, normalize_travel_row, normalize_utility_row
from .utils import hash_row

logger = logging.getLogger(__name__)


def _get_emission_category(category_key, scope):
    defaults = {
        'name': category_key.replace('_', ' ').title(),
        'scope': scope,
        'description': '',
    }
    category, _ = EmissionCategory.objects.get_or_create(key=category_key, defaults=defaults)
    return category


def _create_anomalies(record, anomalies):
    for code, message, severity in anomalies:
        AnomalyFlag.objects.create(record=record, code=code, message=message, severity=severity)
    if anomalies:
        record.is_anomalous = True
        record.save(update_fields=['is_anomalous'])


@shared_task
def process_upload_batch(batch_id):
    try:
        batch = UploadBatch.objects.select_related('source_system', 'organization').get(id=batch_id)
    except UploadBatch.DoesNotExist:
        logger.error('UploadBatch %s not found', batch_id)
        return

    batch.status = UploadBatch.Status.PROCESSING
    batch.started_at = timezone.now()
    batch.save(update_fields=['status', 'started_at'])

    try:
        _run_ingestion(batch)
    except Exception as exc:
        logger.exception('Ingestion failed for batch %s: %s', batch_id, exc)
        batch.status = UploadBatch.Status.FAILED
        batch.completed_at = timezone.now()
        batch.save(update_fields=['status', 'completed_at'])
        raise


def _run_ingestion(batch):
    airport_map = {
        airport.code: {
            'latitude': airport.latitude,
            'longitude': airport.longitude,
        }
        for airport in AirportLookup.objects.all()
    }

    total_rows = 0
    success_rows = 0
    failed_rows = 0
    created_records = []
    seen_hashes = set()

    # Open as binary then wrap with TextIOWrapper so we can specify encoding.
    # FieldFile.open() does not accept an encoding kwarg.
    batch.file.open('rb')
    try:
        text_stream = io.TextIOWrapper(batch.file, encoding='utf-8-sig', errors='replace')
        reader = csv.DictReader(text_stream)

        for row_number, row in enumerate(reader, start=1):
            total_rows += 1
            raw_hash = hash_row(row)
            is_duplicate = raw_hash in seen_hashes
            seen_hashes.add(raw_hash)

            raw_record = RawRecord.objects.create(
                organization=batch.organization,
                source_system=batch.source_system,
                upload_batch=batch,
                row_number=row_number,
                raw_data=dict(row),
                raw_hash=raw_hash,
            )

            try:
                if batch.source_system.source_type == SourceType.SAP:
                    normalized = normalize_sap_row(row)
                elif batch.source_system.source_type == SourceType.UTILITY:
                    normalized = normalize_utility_row(row)
                else:
                    normalized = normalize_travel_row(row, airport_map)
            except Exception as row_exc:
                logger.warning('Row %d normalization error: %s', row_number, row_exc)
                failed_rows += 1
                raw_record.status = RawRecord.Status.FAILED
                raw_record.errors = {'error': str(row_exc)}
                raw_record.save(update_fields=['status', 'errors'])
                continue

            emission_scope = normalized['emission_scope']
            category = _get_emission_category(normalized['emission_category_key'], emission_scope)

            normalized_record = NormalizedRecord.objects.create(
                organization=batch.organization,
                source_system=batch.source_system,
                upload_batch=batch,
                raw_record=raw_record,
                emission_category=category,
                emission_scope=emission_scope,
                activity_quantity=normalized['activity_quantity'],
                activity_unit=normalized['activity_unit'] or '',
                normalized_quantity=normalized['normalized_quantity'],
                normalized_unit=normalized['normalized_unit'] or '',
                emission_factor=normalized['emission_factor'],
                estimated_emissions=normalized['estimated_emissions'],
                currency=normalized['currency'] or '',
                cost=None,
                data=normalized['data'],
                conversion_metadata=normalized['conversion_metadata'],
                source_row_hash=raw_hash,
            )
            created_records.append(normalized_record)

            if normalized['activity_quantity'] is None:
                failed_rows += 1
                raw_record.status = RawRecord.Status.FAILED
                raw_record.errors = {'error': 'Missing quantity'}
                raw_record.save(update_fields=['status', 'errors'])
            else:
                success_rows += 1

            _create_anomalies(normalized_record, normalized['anomalies'])

            if is_duplicate:
                AnomalyFlag.objects.create(
                    record=normalized_record,
                    code='duplicate_row',
                    message='Duplicate row detected in upload batch.',
                    severity=AnomalyFlag.Severity.MEDIUM,
                )
                normalized_record.is_anomalous = True
                normalized_record.save(update_fields=['is_anomalous'])

            AuditLog.objects.create(
                organization=batch.organization,
                record=normalized_record,
                action=AuditLog.Action.NORMALIZE,
                performed_by=batch.uploaded_by,
                previous_value=None,
                new_value=normalized_record.data,
                note='Row normalized via ingestion pipeline.',
            )
    finally:
        batch.file.close()

    # Cross-row anomaly detection for utility batches
    if batch.source_system.source_type == SourceType.UTILITY:
        for record, code, message, severity in detect_utility_anomalies(created_records):
            AnomalyFlag.objects.create(record=record, code=code, message=message, severity=severity)
            record.is_anomalous = True
            record.save(update_fields=['is_anomalous'])

    batch.total_rows = total_rows
    batch.success_rows = success_rows
    batch.failed_rows = failed_rows
    batch.status = UploadBatch.Status.COMPLETED
    batch.completed_at = timezone.now()
    batch.save(update_fields=['total_rows', 'success_rows', 'failed_rows', 'status', 'completed_at'])

    logger.info(
        'Batch %s completed: %d total, %d success, %d failed',
        batch.id, total_rows, success_rows, failed_rows,
    )
