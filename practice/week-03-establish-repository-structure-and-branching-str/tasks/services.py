"""
Service layer encapsulating domain business logic for Task management.
Decouples business workflows from HTTP views and serializers.
"""

from typing import Optional, Dict, Any
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Task, TaskCategory
from utils.constants import TaskStatus, TaskPriority


class TaskService:
    """
    Centralized domain service executing business rules, state transitions,
    and workflow metrics for Tasks.
    """

    @staticmethod
    def create_task(
        title: str,
        description: str = "",
        category: Optional[TaskCategory] = None,
        priority: str = TaskPriority.MEDIUM.value,
        assigned_to: Optional[User] = None,
        due_date: Optional[timezone.datetime] = None,
    ) -> Task:
        """Create and persist a validated task instance."""
        task = Task(
            title=title.strip(),
            description=description.strip(),
            category=category,
            priority=priority,
            assigned_to=assigned_to,
            due_date=due_date,
            status=TaskStatus.PENDING.value,
        )
        task.full_clean()
        task.save()
        return task

    @staticmethod
    def update_task_status(task: Task, new_status: str) -> Task:
        """
        Transition task to a new lifecycle state with auditing rules.
        """
        valid_statuses = [s.value for s in TaskStatus]
        if new_status not in valid_statuses:
            raise ValidationError(f"Invalid status '{new_status}'. Allowed: {', '.join(valid_statuses)}")

        # Enforce transition rules
        if task.status == TaskStatus.CANCELLED.value and new_status != TaskStatus.PENDING.value:
            raise ValidationError("Cancelled tasks cannot be moved directly to in-progress or completed; reset to pending first.")

        task.status = new_status
        if new_status == TaskStatus.COMPLETED.value:
            task.completed_at = timezone.now()
        elif task.completed_at is not None:
            task.completed_at = None

        task.save()
        return task

    @staticmethod
    def assign_task(task: Task, user: Optional[User]) -> Task:
        """Assign or reassign task to a team member."""
        task.assigned_to = user
        task.save(update_fields=['assigned_to', 'updated_at'])
        return task

    @staticmethod
    def get_task_metrics() -> Dict[str, Any]:
        """Compute aggregated task operational metrics."""
        now = timezone.now()
        counts = Task.objects.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status=TaskStatus.PENDING.value)),
            in_progress=Count('id', filter=Q(status=TaskStatus.IN_PROGRESS.value)),
            completed=Count('id', filter=Q(status=TaskStatus.COMPLETED.value)),
            blocked=Count('id', filter=Q(status=TaskStatus.BLOCKED.value)),
            overdue=Count('id', filter=Q(due_date__lt=now, status__in=[TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value])),
        )
        total = counts['total'] or 0
        completed = counts['completed'] or 0
        completion_rate = round((completed / total * 100), 2) if total > 0 else 0.0

        return {
            "total_tasks": total,
            "status_breakdown": {
                "pending": counts['pending'] or 0,
                "in_progress": counts['in_progress'] or 0,
                "completed": completed,
                "blocked": counts['blocked'] or 0,
                "overdue": counts['overdue'] or 0,
            },
            "completion_rate_percentage": completion_rate,
        }
