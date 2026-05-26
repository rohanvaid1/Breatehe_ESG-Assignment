from django.contrib import admin

from .models import AnalystReview, AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('record', 'action', 'performed_by', 'created_at')
    list_filter = ('action',)


@admin.register(AnalystReview)
class AnalystReviewAdmin(admin.ModelAdmin):
    list_display = ('record', 'status', 'reviewer', 'created_at')
    list_filter = ('status',)
