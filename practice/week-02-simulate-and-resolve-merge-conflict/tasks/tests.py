"""
Automated unit and integration test suite for tasks application.

Validates models, service transition coordination, dual-feature integration,
and REST endpoints resulting from the resolved merge conflict.
"""

import json
from django.test import TestCase, Client
from django.utils import timezone
from tasks.models import Task, Category, NotificationLog, AuditLog
from tasks.services import (
    process_task_status_transition,
    validate_status_transition,
    TaskTransitionError,
    record_task_activity_audit,
    dispatch_task_notifications,
)


class TaskModelLifecycleTests(TestCase):
    """Unit tests for Task model attributes, state transitions, and helpers."""

    def test_task_creation_with_defaults(self):
        task = Task.objects.create(title="Setup CI pipeline")
        self.assertEqual(task.status, Task.Status.TODO)
        self.assertEqual(task.priority, Task.Priority.MEDIUM)
        self.assertFalse(task.is_completed)
        self.assertIsNone(task.completed_at)

    def test_transition_to_done_sets_completed_at(self):
        task = Task.objects.create(title="Implement OAuth", status=Task.Status.IN_PROGRESS)
        task.status = Task.Status.DONE
        task.save()
        self.assertTrue(task.is_completed)
        self.assertIsNotNone(task.completed_at)

    def test_transition_away_from_done_clears_completed_at(self):
        task = Task.objects.create(title="Refactor queries", status=Task.Status.DONE)
        self.assertIsNotNone(task.completed_at)
        task.status = Task.Status.IN_PROGRESS
        task.save()
        self.assertFalse(task.is_completed)
        self.assertIsNone(task.completed_at)


class CategoryModelTests(TestCase):
    """Unit tests for Category slug generation and serialization."""

    def test_category_slug_auto_generation(self):
        category = Category.objects.create(name="Platform Infrastructure")
        self.assertEqual(category.slug, "platform-infrastructure")

    def test_category_serialization(self):
        category = Category.objects.create(name="Security Audits", color_hex="#10B981")
        data = category.to_dict()
        self.assertEqual(data["name"], "Security Audits")
        self.assertEqual(data["slug"], "security-audits")
        self.assertEqual(data["color_hex"], "#10B981")


class AuditLogModelTests(TestCase):
    """Unit tests for Developer Bob's compliance audit logging feature."""

    def test_audit_log_checksum_generation(self):
        task = Task.objects.create(title="Audit target task")
        audit_log = record_task_activity_audit(
            task=task,
            previous_status=Task.Status.TODO,
            new_status=Task.Status.IN_PROGRESS,
            actor="engineer-bob",
            ip_address="192.168.1.50"
        )
        self.assertIsNotNone(audit_log.checksum)
        self.assertEqual(len(audit_log.checksum), 64)  # SHA-256 length
        # Checksum must match recomputation
        expected_checksum = audit_log.generate_checksum()
        self.assertEqual(audit_log.checksum, expected_checksum)


class NotificationLogModelTests(TestCase):
    """Unit tests for Developer Alice's notification dispatching feature."""

    def test_notification_dispatch_creates_email_and_webhook_logs(self):
        task = Task.objects.create(
            title="Deploy release v2",
            assignee_email="alice@example.com",
            status=Task.Status.IN_PROGRESS
        )
        email_log, webhook_log = dispatch_task_notifications(
            task=task,
            previous_status=Task.Status.TODO,
            new_status=Task.Status.IN_PROGRESS,
            actor="engineer-alice"
        )
        self.assertIsNotNone(email_log)
        self.assertEqual(email_log.recipient, "alice@example.com")
        self.assertEqual(email_log.channel, NotificationLog.Channel.EMAIL)

        self.assertIsNotNone(webhook_log)
        self.assertEqual(webhook_log.channel, NotificationLog.Channel.WEBHOOK)
        self.assertEqual(webhook_log.payload_snapshot["old_state"], Task.Status.TODO)
        self.assertEqual(webhook_log.payload_snapshot["new_state"], Task.Status.IN_PROGRESS)


class ResolvedMergeConflictServiceIntegrationTests(TestCase):
    """
    Tests proving that the resolved service layer harmoniously integrates
    BOTH Developer Alice's notifications AND Developer Bob's audit logs.
    """

    def test_valid_transition_triggers_both_audit_and_notification(self):
        task = Task.objects.create(
            title="Integrate merge conflict resolution",
            assignee_email="team@example.com",
            status=Task.Status.TODO
        )

        result = process_task_status_transition(
            task=task,
            new_status=Task.Status.IN_PROGRESS,
            actor="tech-lead-parth",
            ip_address="10.0.0.1",
            user_agent="pytest/7.4.0"
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["previous_status"], Task.Status.TODO)
        self.assertEqual(result["new_status"], Task.Status.IN_PROGRESS)

        # Check Bob's audit log
        self.assertIn("audit_record", result)
        self.assertEqual(result["audit_record"]["actor"], "tech-lead-parth")
        self.assertTrue(AuditLog.objects.filter(task=task, new_status=Task.Status.IN_PROGRESS).exists())

        # Check Alice's notifications
        self.assertIn("notifications", result)
        self.assertTrue(result["notifications"]["email_sent"])
        self.assertTrue(NotificationLog.objects.filter(task=task).exists())

    def test_invalid_transition_raises_error_without_modifying_state(self):
        task = Task.objects.create(title="Strict state machine task", status=Task.Status.BACKLOG)

        # BACKLOG cannot jump directly to DONE
        with self.assertRaises(TaskTransitionError):
            process_task_status_transition(task=task, new_status=Task.Status.DONE, actor="hacker")

        task.refresh_from_db()
        self.assertEqual(task.status, Task.Status.BACKLOG)
        self.assertEqual(AuditLog.objects.filter(task=task).count(), 0)
        self.assertEqual(NotificationLog.objects.filter(task=task).count(), 0)


class TaskAPIVerificationTests(TestCase):
    """Integration tests verifying the REST endpoints."""

    def setUp(self):
        self.client = Client()

    def test_root_index_reports_conflict_resolved(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["merge_status"]["conflict_resolved"])
        self.assertEqual(data["merge_status"]["resolution_strategy"], "harmonious-integration-keep-both")

    def test_task_creation_and_transition_via_api(self):
        # Create
        create_res = self.client.post(
            "/api/tasks/",
            data=json.dumps({"title": "Fix merge conflict", "assignee_email": "dev@example.com"}),
            content_type="application/json"
        )
        self.assertEqual(create_res.status_code, 201)
        task_id = create_res.json()["id"]

        # Transition
        trans_res = self.client.post(
            f"/api/tasks/{task_id}/transition/",
            data=json.dumps({
                "new_status": "IN_PROGRESS",
                "actor": "lead-reviewer",
                "message": "Starting conflict resolution task"
            }),
            content_type="application/json"
        )
        self.assertEqual(trans_res.status_code, 200)
        trans_data = trans_res.json()
        self.assertEqual(trans_data["new_status"], "IN_PROGRESS")
        self.assertTrue(trans_data["notifications"]["email_sent"])

        # Check audit log endpoint
        audit_res = self.client.get(f"/api/tasks/audit-logs/?task_id={task_id}")
        self.assertEqual(audit_res.status_code, 200)
        self.assertGreaterEqual(audit_res.json()["count"], 1)

        # Check notification log endpoint
        notif_res = self.client.get(f"/api/tasks/notifications/?task_id={task_id}")
        self.assertEqual(notif_res.status_code, 200)
        self.assertGreaterEqual(notif_res.json()["count"], 1)
