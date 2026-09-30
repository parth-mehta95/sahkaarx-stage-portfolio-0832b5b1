"""
Django admin site registration for core models.
"""
from django.contrib import admin
from .models import ServiceMetadata

admin.site.site_header = "Capstone Backend Service Admin"
admin.site.site_title = "Capstone Backend Portal"
admin.site.index_title = "Capstone Administration & Model Management"


@admin.register(ServiceMetadata)
class ServiceMetadataAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'environment', 'is_active', 'created_at', 'updated_at')
    list_filter = ('environment', 'is_active')
    search_fields = ('service_name', 'description')
