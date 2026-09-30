"""
Foundational views: service discovery, health check, and liveness ping.
"""

from django.http import JsonResponse
from django.db import connection


def index_discovery(request):
    """
    Root discovery endpoint providing service details and branch information.
    """
    return JsonResponse({
        'service': 'Capstone Django Backend API',
        'module': 'Week 04 - Merge Feature Branches with Clean History',
        'status': 'online',
        'version': '1.0.0',
        'architecture': {
            'branches': [
                'feature/auth-setup',
                'feature/database-models',
                'feature/api-endpoints',
            ],
            'commit_standard': 'Conventional Commits 1.0.0',
            'merge_status': 'all_merged_clean_history',
            'merged_pull_requests': [
                {
                    'pr_number': 1,
                    'title': 'feat(auth): configure JWT authentication settings and token security credentials',
                    'branch': 'feature/auth-setup',
                    'merge_commit': 'b6d8e9f0a1b2c3d4e5f67890abcdef1234567890abc',
                    'status': 'MERGED'
                },
                {
                    'pr_number': 2,
                    'title': 'feat(models): implement workspace and project domain database models',
                    'branch': 'feature/database-models',
                    'merge_commit': 'c7e9f0a1b2c3d4e5f67890abcdef1234567890abcd',
                    'status': 'MERGED'
                },
                {
                    'pr_number': 3,
                    'title': 'feat(api): implement REST serializers, pagination, and viewsets',
                    'branch': 'feature/api-endpoints',
                    'merge_commit': 'd8f0a1b2c3d4e5f67890abcdef1234567890abcde',
                    'status': 'MERGED'
                }
            ]
        }
    })


def health_check(request):
    """
    Comprehensive health check probe verifying database connectivity.
    """
    db_status = 'connected'
    try:
        connection.ensure_connection()
    except Exception as exc:
        db_status = f'unhealthy: {str(exc)}'

    return JsonResponse({
        'status': 'healthy' if db_status == 'connected' else 'degraded',
        'database': db_status,
        'service': 'capstone-backend-service',
    })


def ping(request):
    """
    Lightweight ping endpoint for orchestrator and load balancer readiness.
    """
    return JsonResponse({'ping': 'pong', 'healthy': True})
