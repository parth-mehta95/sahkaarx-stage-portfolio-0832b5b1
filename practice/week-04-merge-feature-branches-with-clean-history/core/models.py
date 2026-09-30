"""
Foundational abstract base models and metadata models.
"""

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    created_at and updated_at fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class ServiceHealth(models.Model):
    """
    Tracks service runtime health and deployment status.
    """
    service_name = models.CharField(max_length=120, default='capstone-backend')
    version = models.CharField(max_length=32, default='1.0.0')
    status = models.CharField(max_length=32, default='healthy')
    checked_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.service_name} v{self.version} - {self.status}"
