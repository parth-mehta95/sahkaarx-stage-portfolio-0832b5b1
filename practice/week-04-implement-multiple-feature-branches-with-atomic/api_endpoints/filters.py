"""
Filtering logic for project resources by status, priority, and query strings.
"""

from django.db.models import Q


def filter_projects_queryset(queryset, query_params):
    """
    Applies query parameters filtering to Project queryset.
    """
    status_param = query_params.get('status')
    if status_param:
        queryset = queryset.filter(status__iexact=status_param)

    priority_param = query_params.get('priority')
    if priority_param:
        queryset = queryset.filter(priority__iexact=priority_param)

    workspace_param = query_params.get('workspace_id')
    if workspace_param:
        queryset = queryset.filter(workspace_id=workspace_param)

    search_param = query_params.get('search')
    if search_param:
        queryset = queryset.filter(
            Q(title__icontains=search_param) | Q(description__icontains=search_param)
        )

    return queryset
