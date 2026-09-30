"""
backend URL Configuration

The `urlpatterns` list routes URLs to views.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def root_service_index(request):
    """Root endpoint detailing service status and available feature routes."""
    return JsonResponse({
        "service": "Collaborative Django Service",
        "status": "online",
        "version": "1.0.0",
        "description": "Django Backend Scaffold featuring Tasks App integrated via Pull Request",
        "feature_branch": "feature/add-basic-django-app",
        "pr_status": "merged",
        "endpoints": {
            "root": "/",
            "admin": "/admin/",
            "tasks_list": "/api/tasks/",
            "tasks_health": "/api/tasks/health/",
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_service_index, name='root-index'),
    path('api/tasks/', include('tasks.urls', namespace='tasks')),
]
