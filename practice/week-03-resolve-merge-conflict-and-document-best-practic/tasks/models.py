"""
Data models for the tasks application.

Incorporates domain entities:
- Category: Taxonomy and organization.
- Task: Core domain model with state machine and priority levels.
- RateLimitLog: Claire's feature (feature/task-rate-limiting) tracking throughput and quota metrics.
- RetryPolicyLog: Dave's feature (feature/task-retry-policy) capturing exponential backoff and dead-letter queue records.
"""

from django.db import models
from django.utils import timezone


class Category(models.Model):
    """Category classification for organizing tasks."""

    name = models.CharField(max_length=100, unique=True, help_text="Category name (e.g. Engineering, Operations)")
    slug = models.SlugField(max_length=120, unique=True, help_text="URL-safe unique identifier")
    description = models.TextField(blank=True, default="", help_text="Optional category description")
    is_active = models.BooleanField(default=True, help_text="Designates whether this category is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Task(models.Model):
    """Core domain model representing a trackable unit of work."""

    STATUS_PENDING = 'PENDING'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_FAILED = 'FAILED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_FAILED, 'Failed'),
    ]

    PRIORITY_LOW = 'LOW'
    PRIORITY_MEDIUM = 'MEDIUM'
    PRIORITY_HIGH = 'HIGH'
    PRIORITY_CRITICAL = 'CRITICAL'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
        (PRIORITY_CRITICAL, 'Critical'),
    ]

    title = models.CharField(max_length=255, help_text="Short descriptive title of the task")
    description = models.TextField(blank=True, default="", help_text="Detailed task specification and context")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
        help_text="Current lifecycle state",
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
        db_index=True,
        help_text="Relative urgency and impact level",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        help_text="Optional category relationship",
    )
    assigned_to = models.CharField(
        max_length=150,
        blank=True,
        default="",
        help_text="Email or handle of the assignee",
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Target completion date",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when status transitioned to COMPLETED",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["assigned_to"]),
        ]

    def __str__(self):
        return f"[{self.priority}] {self.title} ({self.status})"

    def save(self, *args, **kwargs):
        # Auto-set or clear completed_at timestamp based on status transition
        if self.status == self.STATUS_COMPLETED and self.completed_at is None:
            self.completed_at = timezone.now()
        elif self.status != self.STATUS_COMPLETED and self.completed_at is not None:
            self.completed_at = None
        super().save(*args, **kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "category": self.category.to_dict() if self.category else None,
            "assigned_to": self.assigned_to,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class RateLimitLog(models.Model):
    """
    Feature: Task Rate Limiting & Throttling (Claire's Branch: feature/task-rate-limiting)
    Tracks client request volume and token bucket quotas to protect system availability.
    """

    client_identifier = models.CharField(
        max_length=255,
        db_index=True,
        help_text="User ID, API key, or IP address triggering pipeline execution",
    )
    endpoint = models.CharField(
        max_length=255,
        default="/api/tasks/pipeline/execute/",
        help_text="API endpoint evaluated for rate limiting",
    )
    requests_count = models.PositiveIntegerField(
        default=1,
        help_text="Number of requests recorded in the current sliding window",
    )
    window_limit = models.PositiveIntegerField(
        default=60,
        help_text="Maximum allowed requests in the sliding time window",
    )
    is_throttled = models.BooleanField(
        default=False,
        help_text="True if request exceeded quota and was rejected (HTTP 429)",
    )
    window_start = models.DateTimeField(
        default=timezone.now,
        help_text="Start timestamp of the current rate limit evaluation window",
    )
    reset_at = models.DateTimeField(
        help_text="Timestamp when client quota will be fully replenished",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["client_identifier", "created_at"]),
        ]

    def __str__(self):
        status = "THROTTLED" if self.is_throttled else "ALLOWED"
        return f"RateLimit[{status}] client={self.client_identifier} count={self.requests_count}/{self.window_limit}"

    def to_dict(self):
        return {
            "id": self.id,
            "client_identifier": self.client_identifier,
            "endpoint": self.endpoint,
            "requests_count": self.requests_count,
            "window_limit": self.window_limit,
            "is_throttled": self.is_throttled,
            "window_start": self.window_start.isoformat() if self.window_start else None,
            "reset_at": self.reset_at.isoformat() if self.reset_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class RetryPolicyLog(models.Model):
    """
    Feature: Exponential Backoff & Retry Policy (Dave's Branch: feature/task-retry-policy)
    Records resilient retry attempts, backoff delays, and dead-letter fallback routing.
    """

    STATUS_SUCCESS = "SUCCESS"
    STATUS_RETRYING = "RETRYING"
    STATUS_DEAD_LETTER = "DEAD_LETTER"
    STATUS_CIRCUIT_OPEN = "CIRCUIT_OPEN"

    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Success"),
        (STATUS_RETRYING, "Retrying"),
        (STATUS_DEAD_LETTER, "Dead Letter Routed"),
        (STATUS_CIRCUIT_OPEN, "Circuit Breaker Open"),
    ]

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="retry_logs",
        null=True,
        blank=True,
        help_text="Task subject to retry execution",
    )
    action = models.CharField(
        max_length=100,
        default="execute_pipeline",
        help_text="Action being executed under retry protection",
    )
    attempt_number = models.PositiveIntegerField(
        default=1,
        help_text="Current attempt counter (1 to max_attempts)",
    )
    max_attempts = models.PositiveIntegerField(
        default=3,
        help_text="Configured maximum retry attempts before dead-letter routing",
    )
    backoff_delay_ms = models.PositiveIntegerField(
        default=0,
        help_text="Calculated backoff delay in milliseconds for this attempt",
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_SUCCESS,
        help_text="Outcome of the retry step",
    )
    error_message = models.TextField(
        blank=True,
        default="",
        help_text="Diagnostic failure details if attempt failed",
    )
    executed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-executed_at"]
        indexes = [
            models.Index(fields=["task", "attempt_number"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"RetryLog[{self.status}] task_id={self.task_id} attempt={self.attempt_number}/{self.max_attempts}"

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "action": self.action,
            "attempt_number": self.attempt_number,
            "max_attempts": self.max_attempts,
            "backoff_delay_ms": self.backoff_delay_ms,
            "status": self.status,
            "error_message": self.error_message,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
        }
