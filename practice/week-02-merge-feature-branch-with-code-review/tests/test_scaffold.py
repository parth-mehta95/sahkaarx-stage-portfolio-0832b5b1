"""
Scaffold and integrity verification tests for week-02 repository structure.
"""

from pathlib import Path
import unittest


class Week02ScaffoldIntegrityTest(unittest.TestCase):
    """Verifies that all required files, configurations, and apps exist."""

    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent

    def test_required_root_files_exist(self):
        required_files = [
            "manage.py",
            "requirements.txt",
            ".env.example",
            ".gitignore",
            "README.md",
            "PULL_REQUEST.md",
            "CODE_REVIEW.md",
            "commit_history.txt",
        ]
        for filename in required_files:
            file_path = self.base_dir / filename
            self.assertTrue(file_path.exists(), f"Missing required file: {filename}")

    def test_backend_scaffold_files_exist(self):
        backend_files = [
            "backend/__init__.py",
            "backend/settings.py",
            "backend/urls.py",
            "backend/wsgi.py",
            "backend/asgi.py",
        ]
        for filename in backend_files:
            file_path = self.base_dir / filename
            self.assertTrue(file_path.exists(), f"Missing backend scaffold file: {filename}")

    def test_tasks_app_files_exist(self):
        task_files = [
            "tasks/__init__.py",
            "tasks/apps.py",
            "tasks/models.py",
            "tasks/views.py",
            "tasks/urls.py",
            "tasks/admin.py",
            "tasks/tests.py",
            "tasks/migrations/0001_initial.py",
        ]
        for filename in task_files:
            file_path = self.base_dir / filename
            self.assertTrue(file_path.exists(), f"Missing tasks app file: {filename}")


if __name__ == '__main__':
    unittest.main()
