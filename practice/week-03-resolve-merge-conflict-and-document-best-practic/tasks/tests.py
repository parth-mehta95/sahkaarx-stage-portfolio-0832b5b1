"""
Unit and Integration Tests for Tasks Domain, Rate Limiting, Retry Policy, and Conflict Resolution.
"""

from datetime import date
from django.test import TestCase
from django.utils import timezone

from tasks.models import Task, Category, RateLimitLog, RetryPolicyLog
from tasks.services import (
    check_rate_limit,
    calculate_exponential_backoff,
    execute_with_retry_policy,
    execute_task_pipeline,
)


class TasksDomainModelTests(TestCase):
    """Verifies baseline CRUD operations on Task and Category models."""

    def setUp(self):
        self.category = Category.objects.create(
            name="Infrastructure",
            slug="infrastructure",
            description="Core systems and pipelines",
        )

    def test_task_creation_and_auto_completion_timestamp(self):
        task = Task.objects.create(
            title="Deploy distributed workers",
            category=self.category,
            priority=Task.PRIORITY_HIGH,
            status=Task.STATUS_PENDING,
        )
        self.assertIsNone(task.completed_at)

        # Transition status to completed
        task.status = Task.STATUS_COMPLETED
        task.save()
        self.assertIsNotNone(task.completed_at)

        # Transition back to in-progress
        task.status = Task.STATUS_IN_PROGRESS
        task.save()
        self.assertIsNone(task.completed_at)


class RateLimitingFeatureTests(TestCase):
    """Tests Claire's feature (feature/task-rate-limiting)."""

    def test_rate_limiting_quota_allow_and_throttle(self):
        client_id = "test-worker-client-01"

        # First request allowed
        is_allowed, info, log = check_rate_limit(
            client_identifier=client_id,
            max_requests=2,
            window_seconds=60,
        )
        self.assertTrue(is_allowed)
        self.assertFalse(info["is_throttled"])
        self.assertEqual(info["requests_count"], 1)

        # Second request allowed
        is_allowed2, info2, log2 = check_rate_limit(
            client_identifier=client_id,
            max_requests=2,
            window_seconds=60,
        )
        self.assertTrue(is_allowed2)
        self.assertFalse(info2["is_throttled"])
        self.assertEqual(info2["requests_count"], 2)

        # Third request throttled
        is_allowed3, info3, log3 = check_rate_limit(
            client_identifier=client_id,
            max_requests=2,
            window_seconds=60,
        )
        self.assertFalse(is_allowed3)
        self.assertTrue(info3["is_throttled"])
        self.assertTrue(log3.is_throttled)


class RetryPolicyFeatureTests(TestCase):
    """Tests Dave's feature (feature/task-retry-policy)."""

    def setUp(self):
        self.task = Task.objects.create(title="Retry test task")

    def test_exponential_backoff_calculation(self):
        self.assertEqual(calculate_exponential_backoff(1, base_delay_ms=100), 100)
        self.assertEqual(calculate_exponential_backoff(2, base_delay_ms=100), 200)
        self.assertEqual(calculate_exponential_backoff(3, base_delay_ms=100), 400)
        self.assertEqual(calculate_exponential_backoff(4, base_delay_ms=100), 800)

    def test_retry_policy_success_on_first_try(self):
        success, result, logs = execute_with_retry_policy(
            task=self.task,
            action_func=lambda t: {"status": "ok"},
            max_attempts=3,
        )
        self.assertTrue(success)
        self.assertEqual(result["outcome"], "SUCCESS")
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].status, RetryPolicyLog.STATUS_SUCCESS)

    def test_retry_policy_exhaustion_dead_letter(self):
        def always_fail(t):
            raise ValueError("Persistent downstream service fault")

        success, result, logs = execute_with_retry_policy(
            task=self.task,
            action_func=always_fail,
            max_attempts=3,
        )
        self.assertFalse(success)
        self.assertEqual(result["outcome"], "DEAD_LETTER")
        self.assertEqual(len(logs), 3)
        self.assertEqual(logs[0].status, RetryPolicyLog.STATUS_RETRYING)
        self.assertEqual(logs[1].status, RetryPolicyLog.STATUS_RETRYING)
        self.assertEqual(logs[2].status, RetryPolicyLog.STATUS_DEAD_LETTER)


class ResolvedConflictPipelineIntegrationTests(TestCase):
    """
    Tests the harmoniously merged execute_task_pipeline function,
    confirming both Claire's rate limiting and Dave's retry logic cooperate flawlessly.
    """

    def setUp(self):
        self.task = Task.objects.create(title="Integrated Pipeline Task")

    def test_pipeline_execution_success(self):
        result = execute_task_pipeline(
            task=self.task,
            client_identifier="ci-worker",
            max_rate_limit=10,
            max_retries=3,
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 200)
        self.assertIn("rate_limit", result)
        self.assertIn("retry_policy", result)
        self.assertFalse(result["rate_limit"]["is_throttled"])
        self.assertEqual(result["retry_policy"]["outcome"], "SUCCESS")

        # Refreshed task state
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.STATUS_COMPLETED)

    def test_pipeline_rate_limit_rejection_fast_fails(self):
        # Exceed rate limit
        for _ in range(3):
            check_rate_limit("throttled-client", max_requests=2)

        result = execute_task_pipeline(
            task=self.task,
            client_identifier="throttled-client",
            max_rate_limit=2,
        )
        self.assertFalse(result["success"])
        self.assertEqual(result["status_code"], 429)
        self.assertEqual(result["reason"], "RATE_LIMIT_EXCEEDED")
        self.assertIsNone(result["retry_policy"])  # Protected from execution
