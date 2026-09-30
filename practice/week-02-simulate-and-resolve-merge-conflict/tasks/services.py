"""
Service layer for tasks application.

================================================================================
MERGE CONFLICT RESOLUTION RECORD
================================================================================
File: tasks/services.py
Conflicted Branches:
  - Branch 1 (HEAD): feature/task-notifications (Developer Alice)
  - Branch 2 (Incoming): feature/task-activity-audit (Developer Bob)

Conflict Cause:
  Both developers modified the core `process_task_status_transition` function
  at the same line range to hook into task lifecycle state transitions:
    - Alice added stakeholder alerts and external webhook dispatch.
    - Bob added compliance audit trails with cryptographic checksums.

Resolution Strategy:
  Harmonious Dual-Feature Integration ("Keep Both"):
    1. Validate input parameters and state transition legitimacy.
    2. Update and persist the task state (including auto `completed_at` timestamps).
    3. Execute Security Audit Logging (Bob's feature) first to ensure an immutable
       audit record is established before any external side effects occur.
    4. Execute Notification Dispatch (Alice's feature) second, notifying assignees
       and dispatching webhooks with non-blocking error handling.
    5. Cleanly removed all Git conflict markers (<<<<<<< HEAD, =======, >>>>>>>).
================================================================================
"""

import logging
import hashlib
from typing import Dict, Any, Optional, Tuple
from django.db import transaction
from django.utils import timezone
from tasks.models import Task, NotificationLog, AuditLog

logger = logging.getLogger(__name__)


class TaskTransitionError(ValueError):
    """Raised when an invalid task status transition is attempted."""
    pass


def validate_status_transition(current_status: str, new_status: str) -> bool:
    """
    Validate that status change follows permissible workflow transitions.
    """
    if current_status == new_status:
        return True

    allowed_transitions = {
        Task.Status.BACKLOG: [Task.Status.TODO, Task.Status.CANCELLED],
        Task.Status.TODO: [Task.Status.IN_PROGRESS, Task.Status.CANCELLED],
        Task.Status.IN_PROGRESS: [Task.Status.IN_REVIEW, Task.Status.TODO, Task.Status.CANCELLED],
        Task.Status.IN_REVIEW: [Task.Status.DONE, Task.Status.IN_PROGRESS, Task.Status.CANCELLED],
        Task.Status.DONE: [Task.Status.IN_PROGRESS, Task.Status.TODO],  # Re-opening
        Task.Status.CANCELLED: [Task.Status.TODO, Task.Status.BACKLOG],
    }

    permissible = allowed_transitions.get(current_status, [])
    return new_status in permissible


def dispatch_task_notifications(
    task: Task,
    previous_status: str,
    new_status: str,
    actor: str,
    custom_message: Optional[str] = None
) -> Tuple[Optional[NotificationLog], Optional[NotificationLog]]:
    """
    Developer Alice's Feature: feature/task-notifications
    Dispatches email and webhook alerts when task status transitions occur.
    """
    email_log = None
    webhook_log = None
    subject = f"[Task #{task.id}] Status Changed to {new_status}"
    message = (
        custom_message or
        f"Task '{task.title}' was transitioned from '{previous_status}' "
        f"to '{new_status}' by {actor} at {timezone.now().isoformat()}."
    )

    # 1. Email notification to assignee
    recipient_email = task.assignee_email or "unassigned-team@example.com"
    try:
        email_log = NotificationLog.objects.create(
            task=task,
            recipient=recipient_email,
            channel=NotificationLog.Channel.EMAIL,
            subject=subject,
            message=message,
            status=NotificationLog.Status.SENT,
            payload_snapshot={
                "task_id": task.id,
                "title": task.title,
                "previous_status": previous_status,
                "new_status": new_status,
                "actor": actor,
            }
        )
    except Exception as exc:
        logger.error("Failed to persist email notification: %s", exc)
        email_log = NotificationLog.objects.create(
            task=task,
            recipient=recipient_email,
            channel=NotificationLog.Channel.EMAIL,
            subject=subject,
            message=message,
            status=NotificationLog.Status.FAILED,
            error_message=str(exc)
        )

    # 2. Webhook notification to integration subscriber
    webhook_target = "https://hooks.internal.net/tasks/lifecycle-events"
    try:
        webhook_log = NotificationLog.objects.create(
            task=task,
            recipient=webhook_target,
            channel=NotificationLog.Channel.WEBHOOK,
            subject=subject,
            message=message,
            status=NotificationLog.Status.SENT,
            payload_snapshot={
                "event": "task.status_changed",
                "task_id": task.id,
                "title": task.title,
                "old_state": previous_status,
                "new_state": new_status,
                "actor": actor,
                "timestamp": timezone.now().isoformat(),
            }
        )
    except Exception as exc:
        logger.error("Failed to persist webhook notification: %s", exc)

    return email_log, webhook_log


def record_task_activity_audit(
    task: Task,
    previous_status: str,
    new_status: str,
    actor: str,
    ip_address: Optional[str] = "127.0.0.1",
    user_agent: Optional[str] = "internal-service/1.0",
    metadata: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """
    Developer Bob's Feature: feature/task-activity-audit
    Creates tamper-evident compliance audit trail with cryptographic SHA-256 checksum.
    """
    meta = metadata or {}
    meta.update({
        "task_title": task.title,
        "priority": task.priority,
        "category": task.category.name if task.category else None,
    })

    audit_entry = AuditLog(
        task=task,
        actor=actor or "system",
        action=AuditLog.Action.STATUS_TRANSITION,
        previous_status=previous_status,
        new_status=new_status,
        ip_address=ip_address or "127.0.0.1",
        user_agent=user_agent or "internal-service/1.0",
        metadata=meta
    )
    # Checksum auto-computed in model save() or explicitly:
    audit_entry.checksum = audit_entry.generate_checksum()
    audit_entry.save()
    return audit_entry


# ==============================================================================
# RESOLVED FUNCTION (Formerly Contested Merge Conflict)
# ==============================================================================
@transaction.atomic
def process_task_status_transition(
    task: Task,
    new_status: str,
    actor: str = "system",
    ip_address: Optional[str] = "127.0.0.1",
    user_agent: Optional[str] = "internal-service/1.0",
    notification_message: Optional[str] = None,
    additional_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Primary workflow transition coordinator.

    Resolves the merge conflict between:
      - feature/task-notifications (dispatches user & webhook alerts)
      - feature/task-activity-audit (records compliance audit log & checksum)

    Order of execution:
      1. Validation of transition logic.
      2. Task status modification & persistence.
      3. Compliance audit logging (Developer Bob).
      4. Stakeholder notifications (Developer Alice).
    """
    previous_status = task.status

    # Validate transition
    if not validate_status_transition(previous_status, new_status):
        raise TaskTransitionError(
            f"Invalid status transition from '{previous_status}' to '{new_status}' for Task #{task.id}."
        )

    # 1. Update task status and persist
    task.status = new_status
    task.save()

    # 2. Bob's Feature: Record Compliance Audit Log
    audit_log = record_task_activity_audit(
        task=task,
        previous_status=previous_status,
        new_status=new_status,
        actor=actor,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata=additional_metadata
    )

    # 3. Alice's Feature: Dispatch Real-Time Stakeholder Notifications
    email_log, webhook_log = dispatch_task_notifications(
        task=task,
        previous_status=previous_status,
        new_status=new_status,
        actor=actor,
        custom_message=notification_message
    )

    return {
        "success": True,
        "task_id": task.id,
        "title": task.title,
        "previous_status": previous_status,
        "new_status": new_status,
        "is_completed": task.is_completed,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "audit_record": {
            "id": audit_log.id,
            "actor": audit_log.actor,
            "checksum": audit_log.checksum,
            "action": audit_log.action,
        },
        "notifications": {
            "email_sent": email_log is not None and email_log.status == NotificationLog.Status.SENT,
            "webhook_sent": webhook_log is not None and webhook_log.status == NotificationLog.Status.SENT,
            "logs_count": task.notification_logs.count(),
        },
    }
