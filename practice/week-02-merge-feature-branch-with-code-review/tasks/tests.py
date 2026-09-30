"""
Unit and integration tests for tasks application.

Specifically tests feature additions and verifies resolutions for all
Team Lead Code Review feedback comments.
"""

import json
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Task, Category


class CategoryModelTest(TestCase):
    """Test Category model functionality."""

    def test_create_category_with_auto_slug(self):
        cat = Category.objects.create(name="Backend Engineering", description="Core backend systems")
        self.assertEqual(cat.slug, "backend-engineering")
        self.assertEqual(str(cat), "Backend Engineering")
        self.assertEqual(cat.color_hex, "#3B82F6")

    def test_category_serialization(self):
        cat = Category.objects.create(name="Frontend Design")
        data = cat.to_dict()
        self.assertEqual(data["name"], "Frontend Design")
        self.assertEqual(data["slug"], "frontend-design")
        self.assertEqual(data["task_count"], 0)


class TaskModelLifecycleReviewTest(TestCase):
    """
    Validates Team Lead Code Review Comment #1:
    Automatic completed_at timestamp tracking on DONE status transition.
    """

    def setUp(self):
        self.category = Category.objects.create(name="DevOps")
        self.task = Task.objects.create(
            title="Configure Production CI/CD Pipeline",
            description="GitHub Actions deployment workflow",
            category=self.category,
            priority=Task.Priority.HIGH,
            status=Task.Status.TODO
        )

    def test_initial_state_not_completed(self):
        self.assertFalse(self.task.is_completed)
        self.assertIsNone(self.task.completed_at)

    def test_transition_to_done_sets_completed_at(self):
        """Review Comment #1 Verification: Transitioning to DONE sets completed_at."""
        self.task.status = Task.Status.DONE
        self.task.save()

        self.assertTrue(self.task.is_completed)
        self.assertIsNotNone(self.task.completed_at)
        self.assertLessEqual((timezone.now() - self.task.completed_at).total_seconds(), 5)

    def test_transition_away_from_done_clears_completed_at(self):
        """Review Comment #1 Verification: Moving task back to active clears completed_at."""
        self.task.status = Task.Status.DONE
        self.task.save()
        self.assertIsNotNone(self.task.completed_at)

        # Transition back to IN_PROGRESS
        self.task.status = Task.Status.IN_PROGRESS
        self.task.save()

        self.assertFalse(self.task.is_completed)
        self.assertIsNone(self.task.completed_at)


class TaskAPIExtendedReviewTest(TestCase):
    """
    Integration tests covering endpoints and Team Lead Review Comments #2 & #3:
    - Review Comment #2: Invalid category slug handling (HTTP 400 Bad Request)
    - Review Comment #3: Pagination clamping to MAX_PAGE_SIZE (100)
    """

    def setUp(self):
        self.client = Client()
        self.cat1 = Category.objects.create(name="Security", slug="security")
        self.cat2 = Category.objects.create(name="Database", slug="database")

        self.t1 = Task.objects.create(
            title="Implement Rate Limiting",
            category=self.cat1,
            status=Task.Status.IN_PROGRESS,
            priority=Task.Priority.URGENT,
            due_date=date(2026, 10, 15)
        )
        self.t2 = Task.objects.create(
            title="Optimize Query Indexes",
            category=self.cat2,
            status=Task.Status.DONE,
            priority=Task.Priority.HIGH,
            due_date=date(2026, 10, 10)
        )

    def test_list_tasks_success(self):
        response = self.client.get(reverse("tasks:task-list-create"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 2)
        self.assertEqual(len(data["results"]), 2)

    def test_filter_by_status_and_priority(self):
        response = self.client.get(reverse("tasks:task-list-create") + "?status=DONE")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["title"], "Optimize Query Indexes")

    def test_filter_by_valid_category_slug(self):
        response = self.client.get(reverse("tasks:task-list-create") + "?category=security")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["title"], "Implement Rate Limiting")

    def test_review_comment_2_invalid_category_returns_400(self):
        """Review Comment #2 Verification: Non-existent category filter returns 400 Bad Request."""
        response = self.client.get(reverse("tasks:task-list-create") + "?category=nonexistent-category-slug")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error"], "Invalid category")
        self.assertEqual(data["code"], "CATEGORY_NOT_FOUND")

    def test_review_comment_3_pagination_clamping(self):
        """Review Comment #3 Verification: Requested page_size is clamped to MAX_PAGE_SIZE (100)."""
        response = self.client.get(reverse("tasks:task-list-create") + "?page_size=99999")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["page_size"], 100)

    def test_create_task_post_success(self):
        payload = {
            "title": "Add OAuth2 authentication provider",
            "description": "Support GitHub and Google OAuth login",
            "category_slug": "security",
            "priority": "HIGH",
            "status": "TODO"
        }
        response = self.client.post(
            reverse("tasks:task-list-create"),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["task"]["title"], "Add OAuth2 authentication provider")
        self.assertEqual(data["task"]["category"]["slug"], "security")

    def test_create_task_missing_title_returns_400(self):
        payload = {"description": "Task without title"}
        response = self.client.post(
            reverse("tasks:task-list-create"),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("title", data["field_errors"])

    def test_update_task_status_via_api_stamps_completed_at(self):
        """Review Comment #1 Verification via API PUT."""
        url = reverse("tasks:task-detail", kwargs={"task_id": self.t1.id})
        update_payload = {"status": "DONE"}
        response = self.client.put(
            url,
            data=json.dumps(update_payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["task"]["status"], "DONE")
        self.assertTrue(data["task"]["is_completed"])
        self.assertIsNotNone(data["task"]["completed_at"])

    def test_task_health_check(self):
        response = self.client.get(reverse("tasks:task-health"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["total_tasks"], 2)
