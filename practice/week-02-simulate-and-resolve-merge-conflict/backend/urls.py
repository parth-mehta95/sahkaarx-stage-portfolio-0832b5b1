"""
Root URL configuration for backend project.

Exposes administrative, root index, task endpoints, and conflict-resolution services.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def root_service_index(request):
    """Discovery index endpoint detailing available services and conflict resolution status."""
    return JsonResponse({
        "status": "healthy",
        "service": "sahkaarx-task-manager-api",
        "version": "2.1.0",
        "milestone": "week-02-simulate-and-resolve-merge-conflict",
        "merge_status": {
            "conflict_resolved": True,
            "branches_merged": [
                "feature/task-notifications",
                "feature/task-activity-audit"
            ],
            "target_branch": "main",
            "resolution_strategy": "harmonious-integration-keep-both"
        },
        "endpoints": {
            "admin": "/admin/",
            "tasks": "/api/tasks/",
            "categories": "/api/tasks/categories/",
            "transitions": "/api/tasks/<id>/transition/",
            "notifications": "/api/tasks/notifications/",
            "audit_logs": "/api/tasks/audit-logs/",
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_service_index, name='root-index'),
    path('api/tasks/', include('tasks.urls', namespace='tasks')),
]
