"""
Unit and integration tests for the Tasks domain application.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Task, TaskCategory
from .services import TaskService
from utils.constants import TaskStatus, TaskPriority, HttpStatusCodes


class TaskDomainTestCase(TestCase):
    """Test suite covering Task models, services, and API endpoints."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testdev", password="password123")
        self.category = TaskCategory.objects.create(name="Backend Infrastructure", slug="backend-infra")

    def test_create_task_via_service(self):
        """Verify TaskService creates a valid task with reference ID."""
        task = TaskService.create_task(
            title="Refactor repository directory structure",
            description="Organize apps, configs, and utilities logically.",
            category=self.category,
            priority=TaskPriority.HIGH.value,
            assigned_to=self.user,
        )
        self.assertIsNotNone(task.id)
        self.assertTrue(task.reference_id.startswith("TSK-"))
        self.assertEqual(task.status, TaskStatus.PENDING.value)
        self.assertEqual(task.priority, TaskPriority.HIGH.value)

    def test_status_transition_to_completed(self):
        """Verify status update sets completed_at timestamp."""
        task = TaskService.create_task(title="Deploy staging health probe")
        self.assertIsNone(task.completed_at)

        updated = TaskService.update_task_status(task, TaskStatus.COMPLETED.value)
        self.assertEqual(updated.status, TaskStatus.COMPLETED.value)
        self.assertIsNotNone(updated.completed_at)

    def test_api_task_list_and_create(self):
        """Verify GET /api/tasks/ and POST /api/tasks/."""
        # Create via API
        payload = {
            "title": "Implement centralized custom exception handler",
            "description": "Standardize JSON API error envelopes across all endpoints.",
            "priority": "high",
        }
        post_response = self.client.post(
            reverse('task-list-create'),
            data=payload,
            content_type="application/json"
        )
        self.assertEqual(post_response.status_code, HttpStatusCodes.CREATED)
        res_data = post_response.json()
        self.assertTrue(res_data["success"])
        ref_id = res_data["data"]["reference_id"]

        # List via API
        list_response = self.client.get(reverse('task-list-create'))
        self.assertEqual(list_response.status_code, HttpStatusCodes.OK)
        list_data = list_response.json()
        self.assertEqual(list_data["pagination"]["count"], 1)
        self.assertEqual(list_data["results"][0]["reference_id"], ref_id)

    def test_api_task_validation_rejection(self):
        """Verify API rejects empty or placeholder task titles."""
        payload = {"title": "asdf"}
        response = self.client.post(
            reverse('task-list-create'),
            data=payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, HttpStatusCodes.BAD_REQUEST)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error_code"], "VALIDATION_FAILED")

    def test_task_metrics_endpoint(self):
        """Verify GET /api/tasks/metrics/ aggregates counts accurately."""
        TaskService.create_task(title="Task One")
        task_two = TaskService.create_task(title="Task Two")
        TaskService.update_task_status(task_two, TaskStatus.COMPLETED.value)

        response = self.client.get(reverse('task-metrics'))
        self.assertEqual(response.status_code, HttpStatusCodes.OK)
        data = response.json()
        self.assertTrue(data["success"])
        metrics = data["data"]
        self.assertEqual(metrics["total_tasks"], 2)
        self.assertEqual(metrics["status_breakdown"]["pending"], 1)
        self.assertEqual(metrics["status_breakdown"]["completed"], 1)
        self.assertEqual(metrics["completion_rate_percentage"], 50.0)
