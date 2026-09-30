"""
Data models for tasks application.

Implements Task, Category, and the merged feature models:
- NotificationLog: Real-time stakeholder alerts (from feature/task-notifications)
- AuditLog: Security compliance activity tracking (from feature/task-activity-audit)
"""

import hashlib
import json
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
    assignee_email = models.EmailField(
        blank=True,
        default="",
        help_text="Primary assignee notification recipient"
    )
    due_date = models.DateField(null=True, blank=True, help_text="Target completion date")
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when task was marked as DONE"
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
        Lifecycle timestamp automation:
        Stamps completed_at when status is DONE; resets if reopened.
        """
        if self.status == self.Status.DONE:
            if not self.completed_at:
                self.completed_at = timezone.now()
        else:
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
            "assignee_email": self.assignee_email,
            "is_completed": self.is_completed,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class NotificationLog(models.Model):
    """
    Delivered as part of feature/task-notifications (Developer Alice).
    Records stakeholder alerts and webhook deliveries dispatched upon task transitions.
    """

    class Channel(models.TextChoices):
        EMAIL = "EMAIL", "Email"
        WEBHOOK = "WEBHOOK", "Webhook"
        IN_APP = "IN_APP", "In-App Notification"

    class Status(models.TextChoices):
        QUEUED = "QUEUED", "Queued"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="notification_logs",
        help_text="Related task instance"
    )
    recipient = models.CharField(max_length=255, help_text="Destination email or webhook URL")
    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        default=Channel.EMAIL,
        help_text="Notification medium"
    )
    subject = models.CharField(max_length=255, help_text="Notification subject headline")
    message = models.TextField(help_text="Notification body content")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SENT,
        help_text="Delivery transmission status"
    )
    payload_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON payload dispatched to endpoint"
    )
    error_message = models.TextField(blank=True, default="", help_text="Error reason if transmission failed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification Log"
        verbose_name_plural = "Notification Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["task", "channel"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"[{self.get_channel_display()} - {self.status}] {self.recipient} ({self.task.title})"

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "task_title": self.task.title,
            "recipient": self.recipient,
            "channel": self.channel,
            "channel_display": self.get_channel_display(),
            "subject": self.subject,
            "message": self.message,
            "status": self.status,
            "payload_snapshot": self.payload_snapshot,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AuditLog(models.Model):
    """
    Delivered as part of feature/task-activity-audit (Developer Bob).
    Provides tamper-evident compliance audit logging for security and governance.
    """

    class Action(models.TextChoices):
        STATUS_TRANSITION = "STATUS_TRANSITION", "Status Transition"
        TASK_CREATED = "TASK_CREATED", "Task Created"
        TASK_UPDATED = "TASK_UPDATED", "Task Updated"
        TASK_DELETED = "TASK_DELETED", "Task Deleted"

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="audit_logs",
        help_text="Related task instance"
    )
    actor = models.CharField(
        max_length=150,
        default="system",
        help_text="User, worker, or service identifier triggering the action"
    )
    action = models.CharField(
        max_length=30,
        choices=Action.choices,
        default=Action.STATUS_TRANSITION,
        help_text="Classification of event"
    )
    previous_status = models.CharField(max_length=20, blank=True, default="")
    new_status = models.CharField(max_length=20, blank=True, default="")
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        default="127.0.0.1",
        help_text="Client IP address"
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        default="internal-service/1.0",
        help_text="Client User-Agent header"
    )
    checksum = models.CharField(
        max_length=64,
        blank=True,
        help_text="Cryptographic SHA-256 integrity checksum"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Contextual details of the transaction"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["task", "action"]),
            models.Index(fields=["actor"]),
            models.Index(fields=["created_at"]),
        ]

    def generate_checksum(self):
        """Compute SHA-256 hash across critical transaction attributes to guarantee tamper evidence."""
        raw_payload = f"{self.task_id}|{self.actor}|{self.action}|{self.previous_status}|{self.new_status}|{self.ip_address}"
        return hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        if not self.checksum:
            self.checksum = self.generate_checksum()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[Audit: {self.action}] Task #{self.task_id} by {self.actor} ({self.previous_status} -> {self.new_status})"

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "task_title": self.task.title,
            "actor": self.actor,
            "action": self.action,
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "ip_address": str(self.ip_address) if self.ip_address else None,
            "user_agent": self.user_agent,
            "checksum": self.checksum,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
