"""
Custom domain model validators for slugs, colors, and date consistency.
"""

import re
from django.core.exceptions import ValidationError


def validate_slug_format(value: str):
    """
    Validates that a slug contains only lowercase alphanumeric characters and hyphens.
    """
    if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', value):
        raise ValidationError(
            f"'{value}' is not a valid slug. Must contain only lowercase alphanumeric characters and single hyphens."
        )


def validate_hex_color(value: str):
    """
    Validates standard 3 or 6 digit hex color representation (e.g. #3B82F6).
    """
    if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', value):
        raise ValidationError(
            f"'{value}' is not a valid hex color code. Expected format: #RGB or #RRGGBB."
        )
