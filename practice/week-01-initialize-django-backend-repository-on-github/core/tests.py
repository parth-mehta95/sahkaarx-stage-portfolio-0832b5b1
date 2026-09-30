"""
Unit tests for core application endpoints, models, and administration.
"""
from django.test import Client, TestCase
from django.urls import reverse
from .models import ServiceMetadata


class CoreEndpointsTestCase(TestCase):
    """Test suite validating core application HTTP endpoints."""

    def setUp(self):
        self.client = Client()

    def test_root_index_endpoint(self):
        """Verify root endpoint returns 200 OK with valid service schema."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'online')
        self.assertEqual(data.get('service'), 'Capstone Django Backend API')
        self.assertIn('endpoints', data)
        self.assertIn('health', data['endpoints'])

    def test_health_check_endpoint(self):
        """Verify health check endpoint returns 200 OK and healthy status."""
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'healthy')
        self.assertEqual(data.get('check'), 'ok')

    def test_service_metadata_model(self):
        """Verify ServiceMetadata model creation and string representation."""
        record = ServiceMetadata.objects.create(
            service_name="capstone-test-service",
            environment="testing",
            is_active=True,
            description="Testing service metadata record."
        )
        self.assertIsNotNone(record.id)
        self.assertEqual(record.service_name, "capstone-test-service")
        self.assertIn("capstone-test-service (testing) - Active: True", str(record))
