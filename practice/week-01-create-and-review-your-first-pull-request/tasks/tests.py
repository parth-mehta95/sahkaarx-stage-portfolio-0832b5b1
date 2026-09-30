"""
Unit and integration tests for the tasks application.
"""

from django.test import TestCase, Client
from django.urls import reverse
from tasks.models import Task
import json


class TaskModelTestCase(TestCase):
    """Test suite for Task model functionality."""

    def setUp(self):
        self.task = Task.objects.create(
            title="Setup Continuous Integration",
            description="Configure GitHub Actions CI pipeline for Django checks",
            priority="high",
            status="pending"
        )

    def test_task_creation(self):
        """Verify task attributes are set accurately."""
        self.assertEqual(self.task.title, "Setup Continuous Integration")
        self.assertEqual(self.task.priority, "high")
        self.assertEqual(self.task.status, "pending")
        self.assertFalse(self.task.is_completed)

    def test_task_str_representation(self):
        """Verify __str__ returns title and status."""
        self.assertEqual(str(self.task), "Setup Continuous Integration [pending]")

    def test_mark_completed_method(self):
        """Verify mark_completed updates status and flag."""
        self.task.mark_completed()
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "completed")
        self.assertTrue(self.task.is_completed)


class TaskViewsTestCase(TestCase):
    """Test suite for tasks views and API endpoints."""

    def setUp(self):
        self.client = Client()
        self.task = Task.objects.create(
            title="Review Pull Request",
            description="Peer review feature branch changes before merge",
            priority="urgent",
            status="in_progress"
        )

    def test_health_check_endpoint(self):
        """Verify /api/tasks/health/ endpoint returns 200 and ready status."""
        response = self.client.get(reverse('tasks:tasks-health'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["app"], "tasks")

    def test_task_list_get(self):
        """Verify GET /api/tasks/ returns list of tasks."""
        response = self.client.get(reverse('tasks:task-list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(data["count"], 1)

    def test_task_create_post(self):
        """Verify POST /api/tasks/ creates a new task."""
        payload = {
            "title": "Merge Feature Branch",
            "description": "Fast-forward merge feature branch into main",
            "priority": "high",
            "status": "pending"
        }
        response = self.client.post(
            reverse('tasks:task-list'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "created")
        self.assertEqual(data["task"]["title"], "Merge Feature Branch")

    def test_task_create_missing_title(self):
        """Verify POST /api/tasks/ without title returns 400 Bad Request."""
        payload = {"description": "Task without title"}
        response = self.client.post(
            reverse('tasks:task-list'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)

    def test_task_detail_get(self):
        """Verify GET /api/tasks/<id>/ retrieves task details."""
        response = self.client.get(reverse('tasks:task-detail', kwargs={'task_id': self.task.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Review Pull Request")
        self.assertEqual(data["status"], "in_progress")

    def test_task_detail_put_update(self):
        """Verify PUT /api/tasks/<id>/ updates task details."""
        payload = {"status": "completed", "priority": "low"}
        response = self.client.put(
            reverse('tasks:task-detail', kwargs={'task_id': self.task.id}),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "completed")
        self.assertTrue(self.task.is_completed)

    def test_task_detail_delete(self):
        """Verify DELETE /api/tasks/<id>/ deletes the task."""
        task_id = self.task.id
        response = self.client.delete(reverse('tasks:task-detail', kwargs={'task_id': task_id}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(id=task_id).exists())

    def test_task_detail_not_found(self):
        """Verify 404 for nonexistent task ID."""
        response = self.client.get(reverse('tasks:task-detail', kwargs={'task_id': 99999}))
        self.assertEqual(response.status_code, 404)
