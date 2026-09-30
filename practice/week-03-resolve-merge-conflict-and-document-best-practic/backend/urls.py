"""
backend URL Configuration for Week 03 Practice Module.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def root_health_check(request):
    """System health check endpoint for monitoring and CI probes."""
    return JsonResponse(
        {
            "status": "healthy",
            "module": "week-03-resolve-merge-conflict-and-document-best-practic",
            "framework": "Django 4.2",
            "api_version": "v1",
            "endpoints": [
                "/api/tasks/",
                "/api/tasks/pipeline/execute/",
                "/api/tasks/rate-limits/",
                "/api/tasks/retry-logs/",
                "/admin/",
            ],
        }
    )


urlpatterns = [
    path('', root_health_check, name='root_health'),
    path('admin/', admin.site.urls),
    path('api/', include('tasks.urls', namespace='tasks')),
]
