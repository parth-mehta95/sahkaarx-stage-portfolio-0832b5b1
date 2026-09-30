"""
test_scaffold.py - Validates repository layout, manage.py, WSGI/ASGI configurations,
and Django project initialization.
"""

import os
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestDjangoScaffold(unittest.TestCase):
    """Verifies that all required files and configurations for the Django project exist."""

    def test_manage_py_exists_and_executable(self):
        """manage.py must exist in the project root."""
        manage_path = PROJECT_ROOT / "manage.py"
        self.assertTrue(manage_path.is_file(), "manage.py does not exist in root directory")
        with open(manage_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("DJANGO_SETTINGS_MODULE", content)
        self.assertIn("execute_from_command_line", content)

    def test_backend_package_structure(self):
        """backend package must contain settings, urls, wsgi, and asgi."""
        backend_dir = PROJECT_ROOT / "backend"
        self.assertTrue(backend_dir.is_dir(), "backend directory is missing")

        expected_files = ["__init__.py", "settings.py", "urls.py", "wsgi.py", "asgi.py"]
        for filename in expected_files:
            file_path = backend_dir / filename
            self.assertTrue(file_path.is_file(), f"backend/{filename} is missing")

    def test_core_app_structure(self):
        """core app directory must contain standard Django app modules."""
        core_dir = PROJECT_ROOT / "core"
        self.assertTrue(core_dir.is_dir(), "core directory is missing")

        expected_files = ["__init__.py", "apps.py", "models.py", "views.py", "urls.py", "admin.py", "tests.py"]
        for filename in expected_files:
            file_path = core_dir / filename
            self.assertTrue(file_path.is_file(), f"core/{filename} is missing")

    def test_settings_configuration(self):
        """backend.settings must define BASE_DIR, INSTALLED_APPS, ROOT_URLCONF, and DATABASES."""
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
        from backend import settings

        self.assertTrue(hasattr(settings, "BASE_DIR"))
        self.assertTrue(hasattr(settings, "SECRET_KEY"))
        self.assertTrue(hasattr(settings, "INSTALLED_APPS"))
        self.assertIn("core.apps.CoreConfig", settings.INSTALLED_APPS)
        self.assertEqual(settings.ROOT_URLCONF, "backend.urls")
        self.assertIn("default", settings.DATABASES)

    def test_wsgi_and_asgi_applications(self):
        """WSGI and ASGI applications should be callable objects."""
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
        from backend.wsgi import application as wsgi_app
        from backend.asgi import application as asgi_app

        self.assertTrue(callable(wsgi_app))
        self.assertTrue(callable(asgi_app))

    def test_documentation_and_environment_files(self):
        """Repository must provide README.md, requirements.txt, .gitignore, and .env.example."""
        required_artifacts = [
            PROJECT_ROOT / "README.md",
            PROJECT_ROOT / "requirements.txt",
            PROJECT_ROOT / ".gitignore",
            PROJECT_ROOT / ".env.example",
            PROJECT_ROOT / "commit_history.txt",
        ]
        for artifact in required_artifacts:
            self.assertTrue(artifact.is_file(), f"{artifact.name} is missing")


if __name__ == "__main__":
    unittest.main()
