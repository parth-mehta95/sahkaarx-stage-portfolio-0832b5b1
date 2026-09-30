"""
Unit tests for core application endpoints and models.
"""

from django.test import TestCase, Client
from django.urls import reverse
from .models import ServiceMetadata


class CoreEndpointsTestCase(TestCase):
    """Test suite verifying core health check and service discovery routes."""

    def setUp(self):
        self.client = Client()

    def test_root_discovery_endpoint(self):
        """Verify root endpoint returns HTTP 200 with service metadata and endpoints."""
        response = self.client.get(reverse('root-discovery'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('service'), 'capstone-stage-backend')
        self.assertIn('endpoints', data)
        self.assertIn('health', data['endpoints'])

    def test_health_check_endpoint(self):
        """Verify health check endpoint returns HTTP 200 with database check details."""
        response = self.client.get(reverse('health-check'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'healthy')
        self.assertIn('checks', data)
        self.assertIn('database', data['checks'])

    def test_ping_endpoint(self):
        """Verify liveness probe returns pong."""
        response = self.client.get(reverse('liveness-ping'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'pong')

    def test_service_metadata_model(self):
        """Verify ServiceMetadata model creation and string representation."""
        metadata = ServiceMetadata.objects.create(
            service_name="test-service",
            environment="testing",
            version="1.0.0",
            is_healthy=True
        )
        self.assertTrue(str(metadata).startswith("test-service v1.0.0"))
        self.assertIsNotNone(metadata.created_at)
        self.assertIsNotNone(metadata.updated_at)
