"""
Test suite validating project structure, directory layout conventions, and component separation.
"""

from pathlib import Path
from django.test import TestCase


class ProjectStructureTestCase(TestCase):
    """
    Validates that the repository adheres to professional Django architectural standards,
    including separate configs, domain apps, utilities, and development scaffolding.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.root_dir = Path(__file__).resolve().parent.parent

    def test_root_scaffold_files_exist(self):
        """Verify presence of essential root repository files."""
        expected_files = [
            "manage.py",
            "requirements.txt",
            ".gitignore",
            ".env.example",
            "README.md",
            "BRANCHING_STRATEGY.md",
            "commit_history.txt",
        ]
        for filename in expected_files:
            target = self.root_dir / filename
            self.assertTrue(target.exists(), f"Missing required root file: {filename}")

    def test_backend_config_package_structure(self):
        """Verify presence of Django configuration files in backend/."""
        backend_dir = self.root_dir / "backend"
        self.assertTrue(backend_dir.is_dir(), "backend/ directory does not exist.")
        expected_modules = ["__init__.py", "settings.py", "urls.py", "asgi.py", "wsgi.py"]
        for mod in expected_modules:
            self.assertTrue((backend_dir / mod).exists(), f"Missing backend configuration module: {mod}")

    def test_core_app_structure(self):
        """Verify structure of foundational core application."""
        core_dir = self.root_dir / "core"
        self.assertTrue(core_dir.is_dir(), "core/ directory does not exist.")
        expected_modules = ["__init__.py", "apps.py", "models.py", "views.py", "urls.py", "admin.py", "tests.py"]
        for mod in expected_modules:
            self.assertTrue((core_dir / mod).exists(), f"Missing core app module: {mod}")

    def test_tasks_app_structure(self):
        """Verify structure of tasks domain application with service layer."""
        tasks_dir = self.root_dir / "tasks"
        self.assertTrue(tasks_dir.is_dir(), "tasks/ directory does not exist.")
        expected_modules = [
            "__init__.py",
            "apps.py",
            "models.py",
            "serializers.py",
            "services.py",
            "views.py",
            "urls.py",
            "admin.py",
            "tests.py",
        ]
        for mod in expected_modules:
            self.assertTrue((tasks_dir / mod).exists(), f"Missing tasks app module: {mod}")

    def test_utils_package_structure(self):
        """Verify structure of centralized utilities package."""
        utils_dir = self.root_dir / "utils"
        self.assertTrue(utils_dir.is_dir(), "utils/ directory does not exist.")
        expected_modules = [
            "__init__.py",
            "constants.py",
            "validators.py",
            "pagination.py",
            "exceptions.py",
            "helpers.py",
        ]
        for mod in expected_modules:
            self.assertTrue((utils_dir / mod).exists(), f"Missing utils module: {mod}")
