"""
backend URL Configuration for Week 02 Feature Branch & Code Review.

The `urlpatterns` list routes URLs to views.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def root_service_index(request):
    """Root discovery endpoint detailing service status, feature branch, and review resolution."""
    return JsonResponse({
        "service": "Collaborative Django Service - Stage 2",
        "status": "online",
        "version": "1.1.0",
        "description": "Django Backend Service with Task Categories, Priority Matrix & Code Review Resolutions",
        "feature_branch": "feature/task-priority-and-review-feedback",
        "target_branch": "main",
        "pr_number": 2,
        "pr_status": "merged",
        "review_feedback_addressed": [
            "Automatic completed_at timestamp tracking on DONE status transition",
            "Category slug resolution with explicit 400 error handling on invalid slugs",
            "Pagination clamping (max 100 items) to prevent DoS query exhaustion",
            "Dedicated unit and integration tests verifying all review comments"
        ],
        "endpoints": {
            "root": "/",
            "admin": "/admin/",
            "tasks_list": "/api/tasks/",
            "tasks_health": "/api/tasks/health/",
            "categories_list": "/api/tasks/categories/",
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_service_index, name='root-index'),
    path('api/tasks/', include('tasks.urls', namespace='tasks')),
]
