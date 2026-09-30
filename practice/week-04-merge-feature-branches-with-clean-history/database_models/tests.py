"""
Unit tests for domain database models, validations, and constraints.
"""

from datetime import date, timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Workspace, Project, ProjectTag, ProjectAuditRecord


class DatabaseModelTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(
            name='Alpha Corp',
            slug='alpha-corp',
            description='Primary enterprise workspace'
        )

    def test_workspace_creation_and_auto_slug(self):
        ws = Workspace.objects.create(name='Beta Labs')
        self.assertEqual(ws.slug, 'beta-labs')
        self.assertTrue(ws.is_active)
        self.assertEqual(str(ws), 'Beta Labs')

    def test_workspace_duplicate_slug_integrity_error(self):
        with self.assertRaises(IntegrityError):
            Workspace.objects.create(name='Alpha Corp Duplicate', slug='alpha-corp')

    def test_project_creation_and_defaults(self):
        proj = Project.objects.create(
            title='Core API Migration',
            workspace=self.workspace,
            description='Migrating services to Django REST framework',
            budget=25000.00
        )
        self.assertEqual(proj.slug, 'core-api-migration')
        self.assertEqual(proj.status, Project.StatusChoices.DRAFT)
        self.assertEqual(proj.priority, Project.PriorityChoices.MEDIUM)
        self.assertFalse(proj.is_deleted)
        self.assertEqual(str(proj), 'Core API Migration [DRAFT]')

    def test_project_date_validation_rejects_inverted_dates(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        with self.assertRaises(ValidationError):
            Project.objects.create(
                title='Invalid Schedule',
                workspace=self.workspace,
                start_date=today,
                target_date=yesterday
            )

    def test_project_tag_and_assignment(self):
        tag = ProjectTag.objects.create(
            name='Backend',
            slug='backend',
            color_hex='#10B981',
            workspace=self.workspace
        )
        proj = Project.objects.create(
            title='Feature Service',
            workspace=self.workspace
        )
        proj.tags.add(tag)
        self.assertEqual(proj.tags.count(), 1)
        self.assertEqual(proj.tags.first().name, 'Backend')

    def test_tag_invalid_hex_color_validation(self):
        with self.assertRaises(ValidationError):
            tag = ProjectTag(
                name='Invalid Tag',
                slug='invalid-tag',
                color_hex='not-a-hex',
                workspace=self.workspace
            )
            tag.full_clean()

    def test_project_audit_record(self):
        proj = Project.objects.create(title='Audit Project', workspace=self.workspace)
        audit = ProjectAuditRecord.objects.create(
            project=proj,
            action=ProjectAuditRecord.Action.CREATE,
            actor_username='lead_dev',
            summary='Project created via API'
        )
        self.assertEqual(audit.action, 'CREATE')
        self.assertEqual(audit.actor_username, 'lead_dev')
        self.assertIn('CREATE', str(audit))
