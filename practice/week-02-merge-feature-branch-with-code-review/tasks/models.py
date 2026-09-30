"""
Data models for tasks application.

Implements Task and Category models with lifecycle automation and review fixes.
"""

from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    """Category grouping for tasks (e.g., Engineering, Marketing, Operations)."""

    name = models.CharField(max_length=100, unique=True, help_text="Category display name")
    slug = models.SlugField(max_length=120, unique=True, blank=True, help_text="URL-friendly identifier")
    description = models.TextField(blank=True, default="", help_text="Optional description of the category")
    color_hex = models.CharField(max_length=7, default="#3B82F6", help_text="Hex color code for UI badges")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def to_dict(self):
        """Serialize category instance to JSON-compatible dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "color_hex": self.color_hex,
            "task_count": self.tasks.count(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Task(models.Model):
    """
    Core Task model with lifecycle status tracking, priority, and category relation.
    
    Includes automated timestamp management and state validation incorporated
    from team lead code review feedback.
    """

    class Status(models.TextChoices):
        BACKLOG = "BACKLOG", "Backlog"
        TODO = "TODO", "To Do"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        IN_REVIEW = "IN_REVIEW", "In Review"
        DONE = "DONE", "Done"
        CANCELLED = "CANCELLED", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        URGENT = "URGENT", "Urgent"

    title = models.CharField(max_length=255, help_text="Brief summary of the task")
    description = models.TextField(blank=True, default="", help_text="Detailed task specification")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        help_text="Optional category assignment"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
        help_text="Current task lifecycle status"
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        help_text="Urgency and impact priority"
    )
    due_date = models.DateField(null=True, blank=True, help_text="Target completion date")
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when task was marked as DONE (automatically populated)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["-priority", "due_date", "-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["due_date"]),
        ]

    def save(self, *args, **kwargs):
        """
        Custom save logic addressed from Team Lead Review Comment #1:
        Automatically sets `completed_at` timestamp when status transitions to `DONE`.
        Clears `completed_at` if moved back to an active state.
        """
        if self.status == self.Status.DONE:
            if not self.completed_at:
                self.completed_at = timezone.now()
        else:
            # If transitioned away from DONE, reset completed_at
            if self.completed_at is not None:
                self.completed_at = None

        super().save(*args, **kwargs)

    @property
    def is_completed(self):
        """Helper indicating whether the task is in a finished state."""
        return self.status == self.Status.DONE

    def __str__(self):
        return f"[{self.get_priority_display()} | {self.get_status_display()}] {self.title}"

    def to_dict(self):
        """Serialize task instance to JSON-compatible dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category.to_dict() if self.category else None,
            "status": self.status,
            "status_display": self.get_status_display(),
            "priority": self.priority,
            "priority_display": self.get_priority_display(),
            "is_completed": self.is_completed,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
