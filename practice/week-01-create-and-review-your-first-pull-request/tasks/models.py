"""
Data models for the tasks application.
"""

from django.db import models


class Task(models.Model):
    """
    Represents a task item created within the application.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    title = models.CharField(max_length=200, help_text="Title of the task")
    description = models.TextField(blank=True, default='', help_text="Detailed description of the task")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField(null=True, blank=True, help_text="Optional target completion date")
    is_completed = models.BooleanField(default=False, help_text="Flag indicating task completion")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self) -> str:
        return f"{self.title} [{self.status}]"

    def mark_completed(self) -> None:
        """Mark task as completed."""
        self.status = 'completed'
        self.is_completed = True
        self.save()
