"""
Data models for the Tasks domain application.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import TimeStampedModel
from utils.constants import TaskStatus, TaskPriority
from utils.helpers import generate_reference_id
from utils.validators import validate_task_title


class TaskCategory(TimeStampedModel):
    """
    Categorization taxonomy for grouping related tasks (e.g., Engineering, Bug, Ops).
    """
    name = models.CharField(max_length=100, unique=True, help_text="Category name.")
    slug = models.SlugField(max_length=120, unique=True, help_text="Unique URL slug.")
    description = models.TextField(blank=True, default="", help_text="Category overview.")

    class Meta:
        verbose_name = "Task Category"
        verbose_name_plural = "Task Categories"
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Task(TimeStampedModel):
    """
    Core domain entity representing a work item or pipeline action.
    """
    reference_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        default=generate_reference_id,
        help_text="Globally unique human-readable identifier (e.g. TSK-4F8A12BC)."
    )
    title = models.CharField(
        max_length=200,
        validators=[validate_task_title],
        help_text="Concise title summarizing the task."
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Detailed specifications or reproduction steps."
    )
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        help_text="Optional category assignment."
    )
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices(),
        default=TaskStatus.PENDING.value,
        help_text="Current state in task lifecycle."
    )
    priority = models.CharField(
        max_length=20,
        choices=TaskPriority.choices(),
        default=TaskPriority.MEDIUM.value,
        help_text="Urgency level for triage."
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        help_text="Team member responsible for this task."
    )
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Target completion deadline."
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when task was marked completed."
    )

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['reference_id']),
        ]

    def __str__(self) -> str:
        return f"[{self.reference_id}] {self.title} ({self.status})"

    def mark_completed(self) -> None:
        """Helper method to transition task to completed with timestamp."""
        self.status = TaskStatus.COMPLETED.value
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    def to_dict(self):
        """Serialize task object into basic dictionary representation."""
        return {
            "id": self.id,
            "reference_id": self.reference_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.name if self.category else None,
            "status": self.status,
            "priority": self.priority,
            "assigned_to": self.assigned_to.username if self.assigned_to else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
