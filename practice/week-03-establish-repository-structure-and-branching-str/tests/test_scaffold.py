"""
Test suite validating Django settings, application registration, and manage.py integration.
"""

from django.test import TestCase
from django.conf import settings
from django.urls import reverse, resolve


class ScaffoldSanityTestCase(TestCase):
    """
    Validates Django framework initialization and registered components.
    """

    def test_installed_apps_configured(self):
        """Verify core and tasks apps are registered in INSTALLED_APPS."""
        self.assertIn('core.apps.CoreConfig', settings.INSTALLED_APPS)
        self.assertIn('tasks.apps.TasksConfig', settings.INSTALLED_APPS)
        self.assertIn('rest_framework', settings.INSTALLED_APPS)

    def test_rest_framework_settings(self):
        """Verify DRF custom pagination and exception handling settings."""
        rf_settings = getattr(settings, 'REST_FRAMEWORK', {})
        self.assertEqual(rf_settings.get('EXCEPTION_HANDLER'), 'utils.exceptions.custom_exception_handler')
        self.assertEqual(rf_settings.get('DEFAULT_PAGINATION_CLASS'), 'utils.pagination.StandardResultsSetPagination')

    def test_url_resolutions(self):
        """Verify core and tasks endpoint routing resolutions."""
        self.assertEqual(resolve('/').view_name, 'root-discovery')
        self.assertEqual(resolve('/health/').view_name, 'health-check')
        self.assertEqual(resolve('/ping/').view_name, 'liveness-ping')
        self.assertEqual(resolve('/api/tasks/').view_name, 'task-list-create')
