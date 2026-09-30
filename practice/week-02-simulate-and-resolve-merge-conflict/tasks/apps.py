"""
Application configuration for tasks app.
"""

from django.apps import AppConfig


class TasksConfig(AppConfig):
    """Configuration class for the tasks Django app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
    verbose_name = 'Task & Workflow Management'
