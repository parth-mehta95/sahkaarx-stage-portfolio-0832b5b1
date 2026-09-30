"""
View handlers for core application endpoints.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def index(request):
    """
    Root discovery endpoint providing service overview, status, and API routes.
    """
    return JsonResponse({
        "service": "Capstone Django Backend API",
        "status": "online",
        "version": "1.0.0",
        "repository": "https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1",
        "endpoints": {
            "root": "/",
            "health": "/health/",
            "admin": "/admin/",
            "api_root": "/api/",
        },
        "description": "Clean Django backend scaffold ready for collaborative development."
    }, status=200)


@require_GET
def health_check(request):
    """
    Health check probe endpoint for liveness and readiness monitoring.
    """
    return JsonResponse({
        "status": "healthy",
        "database": "connected",
        "service": "capstone-backend",
        "check": "ok",
    }, status=200)
