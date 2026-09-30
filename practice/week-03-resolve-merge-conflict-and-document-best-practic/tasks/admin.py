from django.contrib import admin
from tasks.models import Task, Category, RateLimitLog, RetryPolicyLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'category', 'assigned_to', 'due_date', 'completed_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description', 'assigned_to')


@admin.register(RateLimitLog)
class RateLimitLogAdmin(admin.ModelAdmin):
    list_display = ('client_identifier', 'endpoint', 'requests_count', 'window_limit', 'is_throttled', 'reset_at')
    list_filter = ('is_throttled', 'endpoint')
    search_fields = ('client_identifier',)


@admin.register(RetryPolicyLog)
class RetryPolicyLogAdmin(admin.ModelAdmin):
    list_display = ('task', 'action', 'attempt_number', 'max_attempts', 'backoff_delay_ms', 'status', 'executed_at')
    list_filter = ('status', 'action')
    search_fields = ('task__title', 'error_message')
