"""
Django Admin site registrations for core models.
"""

from django.contrib import admin
from .models import ServiceMetadata


@admin.register(ServiceMetadata)
class ServiceMetadataAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'version', 'environment', 'is_healthy', 'updated_at')
    list_filter = ('environment', 'is_healthy')
    search_fields = ('service_name', 'version')
    readonly_fields = ('created_at', 'updated_at')
