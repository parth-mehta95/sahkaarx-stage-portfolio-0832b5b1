"""
Foundational and abstract models for the backend service.
"""

from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model providing self-updating created_at and updated_at fields.
    Inherited by domain models across all applications to ensure consistent audit trails.
    """
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the record was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the record was last modified.")

    class Meta:
        abstract = True
        ordering = ['-created_at']


class ServiceMetadata(TimeStampedModel):
    """
    Persistent system status and versioning metadata model.
    """
    service_name = models.CharField(max_length=100, default="capstone-stage-backend")
    environment = models.CharField(max_length=50, default="development")
    version = models.CharField(max_length=20, default="1.0.0")
    is_healthy = models.BooleanField(default=True)
    description = models.TextField(blank=True, default="Standardized Django backend service foundation.")

    class Meta:
        verbose_name = "Service Metadata"
        verbose_name_plural = "Service Metadata"

    def __str__(self) -> str:
        return f"{self.service_name} v{self.version} [{self.environment}] - Healthy: {self.is_healthy}"
