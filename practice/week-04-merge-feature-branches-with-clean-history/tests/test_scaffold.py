"""
Automated scaffold tests validating Week 04 project structure, modularity, and merged branch integrity.
"""

from django.test import TestCase
from django.conf import settings
from pathlib import Path


class ScaffoldIntegrityTests(TestCase):
    def test_settings_configuration(self):
        self.assertTrue(hasattr(settings, 'SECRET_KEY'))
        self.assertTrue(hasattr(settings, 'INSTALLED_APPS'))
        self.assertIn('core.apps.CoreConfig', settings.INSTALLED_APPS)
        self.assertIn('authentication.apps.AuthenticationConfig', settings.INSTALLED_APPS)
        self.assertIn('database_models.apps.DatabaseModelsConfig', settings.INSTALLED_APPS)
        self.assertIn('api_endpoints.apps.ApiEndpointsConfig', settings.INSTALLED_APPS)

    def test_project_directory_structure(self):
        base_dir = Path(settings.BASE_DIR)
        self.assertTrue((base_dir / 'manage.py').exists())
        self.assertTrue((base_dir / 'requirements.txt').exists())
        self.assertTrue((base_dir / '.env.example').exists())
        self.assertTrue((base_dir / '.gitignore').exists())
        self.assertTrue((base_dir / 'backend' / 'settings.py').exists())
        self.assertTrue((base_dir / 'backend' / 'urls.py').exists())
        self.assertTrue((base_dir / 'core' / 'models.py').exists())
        self.assertTrue((base_dir / 'core' / 'views.py').exists())
        self.assertTrue((base_dir / 'authentication' / 'models.py').exists())
        self.assertTrue((base_dir / 'database_models' / 'models.py').exists())
        self.assertTrue((base_dir / 'api_endpoints' / 'views.py').exists())
