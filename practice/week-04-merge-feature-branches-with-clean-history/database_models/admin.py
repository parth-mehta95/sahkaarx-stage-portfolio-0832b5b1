"""
Django admin registration for domain database models.
"""

from django.contrib import admin
from .models import Workspace, Project, ProjectTag, ProjectAuditRecord


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    search_fields = ('name', 'slug')
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProjectTag)
class ProjectTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_hex', 'workspace')
    search_fields = ('name', 'slug', 'workspace__name')
    list_filter = ('workspace',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'workspace', 'status', 'priority', 'budget', 'created_at')
    search_fields = ('title', 'description', 'workspace__name')
    list_filter = ('status', 'priority', 'workspace', 'is_deleted')
    filter_horizontal = ('tags',)


@admin.register(ProjectAuditRecord)
class ProjectAuditRecordAdmin(admin.ModelAdmin):
    list_display = ('project', 'action', 'actor_username', 'recorded_at')
    search_fields = ('project__title', 'actor_username', 'summary')
    list_filter = ('action',)
    readonly_fields = ('recorded_at',)
