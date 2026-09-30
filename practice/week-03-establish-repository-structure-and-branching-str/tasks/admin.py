"""
Django Admin configurations for Tasks domain models.
"""

from django.contrib import admin
from .models import Task, TaskCategory


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'title', 'category', 'status', 'priority', 'assigned_to', 'due_date', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description', 'reference_id')
    readonly_fields = ('reference_id', 'created_at', 'updated_at', 'completed_at')
