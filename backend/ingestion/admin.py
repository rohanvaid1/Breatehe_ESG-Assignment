from django.contrib import admin

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


@admin.register(SourceSystem)
class SourceSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'is_active')
    list_filter = ('source_type', 'is_active')


@admin.register(UploadBatch)
class UploadBatchAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'source_system', 'status', 'total_rows', 'created_at')
    list_filter = ('status', 'source_system')


@admin.register(RawRecord)
class RawRecordAdmin(admin.ModelAdmin):
    list_display = ('upload_batch', 'row_number', 'status')
    list_filter = ('status',)


@admin.register(NormalizedRecord)
class NormalizedRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_system', 'emission_scope', 'status', 'is_anomalous')
    list_filter = ('status', 'emission_scope', 'is_anomalous')


@admin.register(AnomalyFlag)
class AnomalyFlagAdmin(admin.ModelAdmin):
    list_display = ('record', 'code', 'severity', 'created_at')
    list_filter = ('severity', 'code')


admin.site.register(EmissionCategory)
admin.site.register(UnitConversion)
admin.site.register(PlantLookup)
admin.site.register(AirportLookup)
