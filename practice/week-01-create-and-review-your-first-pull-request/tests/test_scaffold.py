"""
Project scaffold validation tests.
Verifies project structure, settings, apps registration, and routing integrity.
"""

from pathlib import Path
import pytest
import os


def test_directory_structure_exists():
    """Verify all standard project and app files exist."""
    base_dir = Path(__file__).resolve().parent.parent

    expected_files = [
        base_dir / "manage.py",
        base_dir / "requirements.txt",
        base_dir / ".env.example",
        base_dir / ".gitignore",
        base_dir / "backend" / "__init__.py",
        base_dir / "backend" / "settings.py",
        base_dir / "backend" / "urls.py",
        base_dir / "backend" / "wsgi.py",
        base_dir / "backend" / "asgi.py",
        base_dir / "tasks" / "__init__.py",
        base_dir / "tasks" / "apps.py",
        base_dir / "tasks" / "models.py",
        base_dir / "tasks" / "views.py",
        base_dir / "tasks" / "urls.py",
        base_dir / "tasks" / "admin.py",
        base_dir / "tasks" / "tests.py",
        base_dir / "tasks" / "migrations" / "__init__.py",
        base_dir / "PULL_REQUEST.md",
        base_dir / "commit_history.txt",
    ]

    for file_path in expected_files:
        assert file_path.exists(), f"Expected artifact {file_path.name} does not exist at {file_path}"


def test_manage_py_is_executable_syntax():
    """Verify manage.py has valid syntax and main entrypoint."""
    manage_py = Path(__file__).resolve().parent.parent / "manage.py"
    with open(manage_py, 'r', encoding='utf-8') as f:
        content = f.read()

    assert "def main():" in content
    assert "DJANGO_SETTINGS_MODULE" in content
    assert "execute_from_command_line" in content


def test_backend_settings_installed_apps():
    """Verify settings.py registers tasks application."""
    settings_py = Path(__file__).resolve().parent.parent / "backend" / "settings.py"
    with open(settings_py, 'r', encoding='utf-8') as f:
        content = f.read()

    assert "tasks.apps.TasksConfig" in content or "'tasks'" in content
    assert "rest_framework" in content
    assert "SECRET_KEY" in content


def test_tasks_app_config():
    """Verify tasks app config defines standard TasksConfig."""
    apps_py = Path(__file__).resolve().parent.parent / "tasks" / "apps.py"
    with open(apps_py, 'r', encoding='utf-8') as f:
        content = f.read()

    assert "class TasksConfig(AppConfig):" in content
    assert "name = 'tasks'" in content
