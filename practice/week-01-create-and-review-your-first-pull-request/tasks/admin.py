"""
Admin site registrations for tasks application.
"""

from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'priority', 'is_completed', 'created_at')
    list_filter = ('status', 'priority', 'is_completed')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
