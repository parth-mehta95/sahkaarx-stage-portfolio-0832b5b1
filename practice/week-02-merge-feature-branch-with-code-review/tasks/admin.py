"""
Django administration configuration for tasks application.
"""

from django.contrib import admin
from .models import Task, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color_hex", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "priority", "status", "due_date", "is_completed", "completed_at")
    list_filter = ("status", "priority", "category", "due_date")
    search_fields = ("title", "description")
    readonly_fields = ("completed_at", "created_at", "updated_at")
    fieldsets = (
        ("Basic Information", {
            "fields": ("title", "description", "category")
        }),
        ("Lifecycle & Priority", {
            "fields": ("status", "priority", "due_date", "completed_at")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
