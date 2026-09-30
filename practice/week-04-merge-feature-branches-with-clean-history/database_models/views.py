"""
Introspection and metadata endpoints for database models.
"""

from django.http import JsonResponse
from .models import Workspace, Project, ProjectTag


def model_schema_info(request):
    """
    Returns registered database models, field definitions, and model counts.
    """
    return JsonResponse({
        'models': {
            'Workspace': {
                'count': Workspace.objects.count(),
                'fields': ['name', 'slug', 'description', 'is_active', 'created_at'],
            },
            'Project': {
                'count': Project.objects.count(),
                'fields': ['title', 'slug', 'status', 'priority', 'budget', 'start_date', 'target_date'],
                'statuses': [s[0] for s in Project.StatusChoices.choices],
                'priorities': [p[0] for p in Project.PriorityChoices.choices],
            },
            'ProjectTag': {
                'count': ProjectTag.objects.count(),
                'fields': ['name', 'slug', 'color_hex'],
            }
        }
    })
