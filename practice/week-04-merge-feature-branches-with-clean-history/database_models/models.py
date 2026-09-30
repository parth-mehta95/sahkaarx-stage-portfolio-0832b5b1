"""
Domain database models for Workspaces, Projects, Tags, and Audit Records.
"""

from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from core.models import TimeStampedModel
from .validators import validate_slug_format, validate_hex_color


class Workspace(TimeStampedModel):
    """
    Represents an isolated organizational workspace / tenant.
    """
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, validators=[validate_slug_format])
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Workspace'
        verbose_name_plural = 'Workspaces'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProjectTag(TimeStampedModel):
    """
    Categorization tags applied to projects for filtering and grouping.
    """
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, validators=[validate_slug_format])
    color_hex = models.CharField(max_length=7, default='#3B82F6', validators=[validate_hex_color])
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='tags')

    class Meta:
        unique_together = ('slug', 'workspace')
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.workspace.name})"


class Project(TimeStampedModel):
    """
    Core project management domain entity.
    """
    class StatusChoices(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        ACTIVE = 'ACTIVE', 'Active'
        ON_HOLD = 'ON_HOLD', 'On Hold'
        COMPLETED = 'COMPLETED', 'Completed'
        ARCHIVED = 'ARCHIVED', 'Archived'

    class PriorityChoices(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, validators=[validate_slug_format])
    description = models.TextField(blank=True, default='')
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='projects')
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.DRAFT, db_index=True)
    priority = models.CharField(max_length=20, choices=PriorityChoices.choices, default=PriorityChoices.MEDIUM, db_index=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    start_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    tags = models.ManyToManyField(ProjectTag, blank=True, related_name='projects')
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = ('slug', 'workspace')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', 'status']),
            models.Index(fields=['status', 'priority']),
        ]

    def clean(self):
        if self.start_date and self.target_date and self.target_date < self.start_date:
            raise ValidationError({'target_date': 'Target date cannot precede start date.'})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} [{self.status}]"


class ProjectAuditRecord(models.Model):
    """
    Immutable audit history record capturing changes to project state.
    """
    class Action(models.TextChoices):
        CREATE = 'CREATE', 'Created'
        UPDATE = 'UPDATE', 'Updated'
        DELETE = 'DELETE', 'Deleted'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='audit_records', null=True, blank=True)
    action = models.CharField(max_length=20, choices=Action.choices)
    actor_username = models.CharField(max_length=150, default='system')
    summary = models.CharField(max_length=255)
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"[{self.recorded_at}] {self.action}: {self.summary}"
