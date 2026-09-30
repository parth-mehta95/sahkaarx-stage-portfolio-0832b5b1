"""
Standardized error formatting and custom exception handling.
"""

from typing import Any, Dict, Optional
import logging
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError

logger = logging.getLogger(__name__)


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Optional[Response]:
    """
    Custom exception handler providing uniform error payloads:
    {
        "success": false,
        "status_code": 400,
        "error_code": "VALIDATION_ERROR",
        "message": "Human readable message",
        "details": {...}
    }
    """
    # Transform Django ValidationError into DRF format if raised in service layer
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            exc = DRFValidationError(detail=exc.message_dict)
        else:
            exc = DRFValidationError(detail=exc.messages)

    response = exception_handler(exc, context)

    if response is not None:
        error_code = getattr(exc, 'default_code', 'API_ERROR').upper()
        if isinstance(exc, Http404):
            error_code = 'NOT_FOUND'

        custom_data = {
            "success": False,
            "status_code": response.status_code,
            "error_code": error_code,
            "message": str(exc) if hasattr(exc, 'detail') is False else "Request validation or processing failed.",
            "details": response.data,
        }
        response.data = custom_data
    else:
        # Unhandled server errors (500)
        logger.exception("Unhandled server exception: %s", exc)
        custom_data = {
            "success": False,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred while processing your request.",
            "details": None,
        }
        response = Response(custom_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
