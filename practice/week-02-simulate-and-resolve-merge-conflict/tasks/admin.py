"""
Django administration registration for tasks application models.
"""

from django.contrib import admin
from tasks.models import Task, Category, NotificationLog, AuditLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_hex', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'status', 'priority', 'assignee_email', 'completed_at', 'due_date')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description', 'assignee_email')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'recipient', 'channel', 'status', 'created_at')
    list_filter = ('channel', 'status', 'created_at')
    search_fields = ('recipient', 'subject', 'message')
    readonly_fields = ('created_at',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'actor', 'action', 'previous_status', 'new_status', 'checksum', 'created_at')
    list_filter = ('action', 'actor', 'created_at')
    search_fields = ('actor', 'checksum', 'ip_address')
    readonly_fields = ('created_at', 'checksum')
