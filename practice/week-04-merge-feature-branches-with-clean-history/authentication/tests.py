"""
Comprehensive unit and integration test suite for authentication flows.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import UserProfile, AuthAuditLog
from .tokens import generate_auth_token_pair, decode_jwt_token, generate_jwt_token
import time


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_payload = {
            'username': 'testdev',
            'email': 'testdev@example.com',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
            'role': 'DEVELOPER',
            'department': 'Engineering'
        }

    def test_user_registration_success(self):
        response = self.client.post(
            '/api/auth/register/',
            data=self.register_payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn('tokens', data)
        self.assertIn('access_token', data['tokens'])
        self.assertEqual(data['user']['username'], 'testdev')

        # Verify DB records
        user = User.objects.get(username='testdev')
        self.assertEqual(user.email, 'testdev@example.com')
        self.assertEqual(user.profile.role, 'DEVELOPER')
        self.assertEqual(user.profile.department, 'Engineering')

    def test_registration_password_mismatch_fails(self):
        payload = self.register_payload.copy()
        payload['confirm_password'] = 'MismatchPassword123!'
        response = self.client.post(
            '/api/auth/register/',
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('confirm_password', response.json())

    def test_user_login_success(self):
        # Register user first
        self.client.post('/api/auth/register/', data=self.register_payload, content_type='application/json')

        login_payload = {
            'username': 'testdev',
            'password': 'SecurePassword123!'
        }
        response = self.client.post('/api/auth/login/', data=login_payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('tokens', data)
        self.assertIn('access_token', data['tokens'])
        self.assertEqual(data['user']['role'], 'DEVELOPER')

    def test_user_login_invalid_credentials_fails(self):
        self.client.post('/api/auth/register/', data=self.register_payload, content_type='application/json')

        login_payload = {
            'username': 'testdev',
            'password': 'WrongPassword!'
        }
        response = self.client.post('/api/auth/login/', data=login_payload, content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_jwt_token_decoding_and_expiry(self):
        pair = generate_auth_token_pair(99, 'tokenuser', 'token@example.com')
        decoded = decode_jwt_token(pair['access_token'])
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded['username'], 'tokenuser')
        self.assertEqual(decoded['token_type'], 'access')

        # Test expired token
        expired_payload = {
            'user_id': 99,
            'exp': int(time.time()) - 100
        }
        expired_token = generate_jwt_token(expired_payload)
        self.assertIsNone(decode_jwt_token(expired_token))

    def test_protected_profile_endpoint_requires_token(self):
        # Without token -> 401 / 403
        response = self.client.get('/api/auth/profile/')
        self.assertIn(response.status_code, [401, 403])

        # With valid token
        reg_resp = self.client.post('/api/auth/register/', data=self.register_payload, content_type='application/json')
        token = reg_resp.json()['tokens']['access_token']

        auth_response = self.client.get(
            '/api/auth/profile/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(auth_response.status_code, 200)
        self.assertEqual(auth_response.json()['username'], 'testdev')
