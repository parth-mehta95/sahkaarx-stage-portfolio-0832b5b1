"""
Core system HTTP views, service discovery, and health inspection endpoints.
"""

from typing import Dict, Any
from django.http import JsonResponse
from django.db import connection
from django.utils import timezone
from utils.constants import HttpStatusCodes
from utils.helpers import format_iso_timestamp


def root_index_view(request) -> JsonResponse:
    """
    Root discovery endpoint providing service overview and available endpoints.
    """
    payload: Dict[str, Any] = {
        "service": "capstone-stage-backend",
        "description": "Standardized Django Backend Service with Modular Architecture",
        "version": "1.0.0",
        "timestamp": format_iso_timestamp(),
        "endpoints": {
            "root": "/",
            "health": "/health/",
            "ping": "/ping/",
            "tasks_api": "/api/tasks/",
            "admin": "/admin/",
        },
        "documentation": "https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1",
    }
    return JsonResponse(payload, status=HttpStatusCodes.OK)


def health_check_view(request) -> JsonResponse:
    """
    Comprehensive health check probing database readiness and runtime status.
    Used by load balancers, Kubernetes liveness probes, and CI/CD smoke tests.
    """
    db_status = "healthy"
    db_latency_ms = 0.0

    try:
        start_time = timezone.now()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        duration = timezone.now() - start_time
        db_latency_ms = round(duration.total_seconds() * 1000, 2)
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    is_healthy = db_status == "healthy"
    status_code = HttpStatusCodes.OK if is_healthy else HttpStatusCodes.INTERNAL_SERVER_ERROR

    response_payload = {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": format_iso_timestamp(),
        "checks": {
            "database": {
                "status": db_status,
                "latency_ms": db_latency_ms,
            },
            "service": "operational",
        },
    }
    return JsonResponse(response_payload, status=status_code)


def ping_view(request) -> JsonResponse:
    """
    Ultra-lightweight ping probe for fast availability checks.
    """
    return JsonResponse({"status": "pong", "timestamp": format_iso_timestamp()}, status=HttpStatusCodes.OK)
