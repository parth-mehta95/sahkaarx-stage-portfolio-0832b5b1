"""
Integration test suite for REST API endpoints.
"""

from django.test import TestCase, Client
from database_models.models import Workspace, Project, ProjectTag


class ProjectApiEndpointTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.workspace = Workspace.objects.create(name='Dev Workspace', slug='dev-workspace')
        self.tag = ProjectTag.objects.create(
            name='Backend API', slug='backend-api', color_hex='#10B981', workspace=self.workspace
        )
        self.project1 = Project.objects.create(
            title='Project Alpha',
            slug='project-alpha',
            workspace=self.workspace,
            status=Project.StatusChoices.ACTIVE,
            priority=Project.PriorityChoices.HIGH,
            budget=15000.00
        )
        self.project2 = Project.objects.create(
            title='Project Beta',
            slug='project-beta',
            workspace=self.workspace,
            status=Project.StatusChoices.DRAFT,
            priority=Project.PriorityChoices.LOW,
            budget=5000.00
        )

    def test_workspace_list_endpoint(self):
        response = self.client.get('/api/v1/workspaces/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Dev Workspace')

    def test_project_list_with_pagination(self):
        response = self.client.get('/api/v1/projects/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('pagination', data)
        self.assertIn('results', data)
        self.assertEqual(data['pagination']['count'], 2)

    def test_project_filtering_by_status(self):
        response = self.client.get('/api/v1/projects/?status=ACTIVE')
        self.assertEqual(response.status_code, 200)
        results = response.json()['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Project Alpha')

    def test_project_detail_retrieval(self):
        response = self.client.get(f'/api/v1/projects/{self.project1.id}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['title'], 'Project Alpha')
        self.assertEqual(data['priority'], 'HIGH')

    def test_project_creation_endpoint(self):
        payload = {
            'title': 'Project Gamma',
            'workspace_id': self.workspace.id,
            'description': 'Brand new API project',
            'status': 'ACTIVE',
            'priority': 'CRITICAL',
            'budget': '32000.00'
        }
        response = self.client.post('/api/v1/projects/', data=payload, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['title'], 'Project Gamma')
        self.assertEqual(data['priority'], 'CRITICAL')

    def test_project_soft_delete(self):
        response = self.client.delete(f'/api/v1/projects/{self.project2.id}/')
        self.assertEqual(response.status_code, 200)
        self.project2.refresh_from_db()
        self.assertTrue(self.project2.is_deleted)

        # Confirm it no longer shows in active listing
        list_resp = self.client.get('/api/v1/projects/')
        results = list_resp.json()['results']
        ids = [p['id'] for p in results]
        self.assertNotIn(self.project2.id, ids)

    def test_project_stats_endpoint(self):
        response = self.client.get('/api/v1/projects/stats/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('total_projects', data)
        self.assertIn('by_status', data)
        self.assertIn('by_priority', data)
