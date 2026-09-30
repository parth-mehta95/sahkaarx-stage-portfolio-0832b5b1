"""
Unit tests for core infrastructure, service health, and discovery endpoints.
"""

from django.test import TestCase, Client
from django.urls import reverse
from .models import ServiceHealth


class CoreEndpointTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_discovery_returns_200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'online')
        self.assertIn('architecture', data)
        self.assertEqual(data['architecture']['merge_status'], 'all_merged_clean_history')
        self.assertEqual(len(data['architecture']['merged_pull_requests']), 3)

    def test_health_check_returns_healthy(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['database'], 'connected')

    def test_ping_returns_pong(self):
        response = self.client.get('/ping/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['ping'], 'pong')
        self.assertTrue(data['healthy'])

    def test_service_health_model(self):
        record = ServiceHealth.objects.create(
            service_name='capstone-auth-db-api',
            version='1.0.0',
            status='operational'
        )
        self.assertEqual(str(record), 'capstone-auth-db-api v1.0.0 - operational')
