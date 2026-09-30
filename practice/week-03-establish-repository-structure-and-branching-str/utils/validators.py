"""
Reusable validation logic for domain models, serializers, and query parameters.
"""

import re
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_task_title(value: str) -> None:
    """
    Validate that task titles are non-empty, reasonably concise,
    and do not contain malicious characters or placeholder values.
    """
    if not value or not value.strip():
        raise ValidationError("Task title cannot be empty or purely whitespace.")
    
    clean_val = value.strip()
    if len(clean_val) < 3:
        raise ValidationError("Task title must be at least 3 characters long.")
    
    if len(clean_val) > 200:
        raise ValidationError("Task title cannot exceed 200 characters.")

    placeholder_patterns = [r'^test\b', r'^untitled\b', r'^temp\b', r'^asdf\b']
    for pattern in placeholder_patterns:
        if re.search(pattern, clean_val, re.IGNORECASE):
            raise ValidationError(
                f"Task title '{clean_val}' appears to be a temporary placeholder. Please provide a descriptive title."
            )


def validate_future_date(value) -> None:
    """
    Validate that a given date or datetime is not set in the past.
    """
    if value and value < timezone.now():
        raise ValidationError("Due date cannot be set in the past.")


def validate_priority_level(value: str) -> None:
    """
    Validate that the provided priority level belongs to allowed choices.
    """
    valid_priorities = {'low', 'medium', 'high', 'critical'}
    if value.lower() not in valid_priorities:
        raise ValidationError(f"Invalid priority '{value}'. Must be one of: {', '.join(sorted(valid_priorities))}.")
