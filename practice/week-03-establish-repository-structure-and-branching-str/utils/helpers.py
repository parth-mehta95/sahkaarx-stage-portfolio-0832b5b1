"""
Reusable utility helpers for strings, identifiers, and datetime manipulation.
"""

import uuid
import re
from datetime import datetime, timezone
from typing import Optional


def generate_reference_id(prefix: str = "TSK") -> str:
    """
    Generate an alphanumeric reference identifier with standard prefix.
    Example: TSK-8F3B91AC
    """
    token = uuid.uuid4().hex[:8].upper()
    return f"{prefix}-{token}"


def slugify_text(text: str) -> str:
    """
    Normalize string into URL-safe slug.
    """
    cleaned = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', cleaned)


def format_iso_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime into ISO 8601 UTC string.
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
