from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Organization, User


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'industry', 'country', 'is_active')
    search_fields = ('name', 'slug')


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'organization', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Organization', {'fields': ('organization', 'role')}),
    )
