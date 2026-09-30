"""
Data models for the core application.
"""
from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model providing self-updating created_at and updated_at fields.
    Reusable across all capstone backend domain models.
    """
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp of creation")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp of last update")

    class Meta:
        abstract = True


class ServiceMetadata(TimeStampedModel):
    """
    Model recording service operational status and health metrics.
    """
    service_name = models.CharField(max_length=100, default="capstone-backend")
    environment = models.CharField(max_length=50, default="development")
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, default="Capstone backend core service scaffold")

    class Meta:
        verbose_name = "Service Metadata"
        verbose_name_plural = "Service Metadata Records"

    def __str__(self) -> str:
        return f"{self.service_name} ({self.environment}) - Active: {self.is_active}"
