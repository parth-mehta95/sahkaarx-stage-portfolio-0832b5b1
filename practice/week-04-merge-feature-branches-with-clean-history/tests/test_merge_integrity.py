"""
End-to-End System Integration Tests validating the clean convergence of all 3 feature branches:
1. Authentication (JWT token issuance, auth audit log, user profile)
2. Database Models (Workspace, Project, ProjectTag, ProjectAuditRecord)
3. API Endpoints (REST APIs, pagination envelopes, filtering, statistics)
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from authentication.tokens import generate_auth_token_pair
from database_models.models import Workspace, Project, ProjectTag


class MergedSystemIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Create User and Workspace
        self.user = User.objects.create_user(
            username='merge_admin',
            email='admin@ttpl.ind.in',
            password='ComplexPassword123!'
        )
        self.tokens = generate_auth_token_pair(self.user.id, self.user.username, self.user.email)
        self.auth_headers = {'HTTP_AUTHORIZATION': f"Bearer {self.tokens['access_token']}"}

        self.workspace = Workspace.objects.create(
            name='Enterprise Cloud Suite',
            slug='enterprise-cloud-suite',
            description='Production enterprise workspace'
        )

        self.tag = ProjectTag.objects.create(
            name='Cloud Migration',
            slug='cloud-migration',
            color_hex='#2563EB',
            workspace=self.workspace
        )

        self.project = Project.objects.create(
            title='Zero-Downtime DB Sharding',
            slug='zero-downtime-db-sharding',
            workspace=self.workspace,
            status=Project.StatusChoices.ACTIVE,
            priority=Project.PriorityChoices.CRITICAL,
            budget=75000.00
        )
        self.project.tags.add(self.tag)

    def test_discovery_reports_all_features_merged(self):
        """Verify discovery endpoint reports clean merged state for all 3 feature branches."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'online')
        self.assertEqual(data['architecture']['merge_status'], 'all_merged_clean_history')
        self.assertEqual(len(data['architecture']['merged_pull_requests']), 3)

    def test_authenticated_profile_and_db_models_interop(self):
        """Verify JWT authorization works alongside database models."""
        response = self.client.get('/api/auth/profile/', **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], 'merge_admin')

    def test_rest_api_projects_and_models_interop(self):
        """Verify REST API layer seamlessly serves Database Models with pagination and filters."""
        # Query list
        response = self.client.get('/api/v1/projects/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['pagination']['count'], 1)
        self.assertEqual(data['results'][0]['title'], 'Zero-Downtime DB Sharding')
        self.assertEqual(data['results'][0]['workspace_name'], 'Enterprise Cloud Suite')
        self.assertEqual(len(data['results'][0]['tags']), 1)
        self.assertEqual(data['results'][0]['tags'][0]['name'], 'Cloud Migration')

    def test_project_stats_with_data(self):
        """Verify aggregated analytics across merged database records."""
        response = self.client.get('/api/v1/projects/stats/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['total_projects'], 1)
        self.assertEqual(data['by_status'].get('ACTIVE'), 1)
        self.assertEqual(data['by_priority'].get('CRITICAL'), 1)
