"""
Scaffold and integrity verification tests for Week 03 repository structure.
"""

from pathlib import Path
import unittest


class ScaffoldIntegrityTest(unittest.TestCase):
    """Verifies that all required project files, modules, and directories exist."""

    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent

    def test_essential_files_exist(self):
        expected_files = [
            "manage.py",
            "requirements.txt",
            ".gitignore",
            ".env.example",
            "CONTRIBUTING.md",
            "CONFLICT_SIMULATION.md",
            "commit_history.txt",
            "README.md",
            "backend/__init__.py",
            "backend/settings.py",
            "backend/urls.py",
            "backend/wsgi.py",
            "backend/asgi.py",
            "tasks/__init__.py",
            "tasks/apps.py",
            "tasks/models.py",
            "tasks/services.py",
            "tasks/views.py",
            "tasks/urls.py",
            "tasks/admin.py",
            "tasks/tests.py",
            "tasks/migrations/__init__.py",
            "tasks/migrations/0001_initial.py",
            "tests/__init__.py",
            "tests/test_scaffold.py",
            "tests/test_conflict_resolution.py",
        ]
        for rel_path in expected_files:
            file_path = self.base_dir / rel_path
            self.assertTrue(file_path.exists(), f"Missing required file: {rel_path}")

    def test_requirements_file_has_dependencies(self):
        req_file = self.base_dir / "requirements.txt"
        self.assertTrue(req_file.exists())
        content = req_file.read_text(encoding="utf-8")
        self.assertIn("Django", content)
        self.assertIn("djangorestframework", content)


if __name__ == '__main__':
    unittest.main()
