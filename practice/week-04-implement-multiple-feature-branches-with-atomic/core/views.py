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
        'module': 'Week 04 - Implement Multiple Feature Branches with Atomic Commits',
        'status': 'online',
        'version': '1.0.0',
        'architecture': {
            'branches': [
                'feature/auth-setup',
                'feature/database-models',
                'feature/api-endpoints',
            ],
            'commit_standard': 'Conventional Commits 1.0.0',
            'merge_status': 'clean_ready'
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
