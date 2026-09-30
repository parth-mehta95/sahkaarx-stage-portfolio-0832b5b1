"""
Authentication configuration settings, token lifetimes, and security policies.
"""

from datetime import timedelta
from django.conf import settings

# Default security parameters
AUTH_COOKIE_NAME = 'auth_token'
TOKEN_PREFIX = 'Bearer'
TOKEN_ALGORITHM = getattr(settings, 'JWT_AUTH', {}).get('ALGORITHM', 'HS256')
SECRET_KEY = getattr(settings, 'JWT_AUTH', {}).get('SECRET_KEY', 'default-auth-secret-key-12345')

# Token Lifetimes
ACCESS_TOKEN_LIFETIME = timedelta(
    minutes=getattr(settings, 'JWT_AUTH', {}).get('ACCESS_TOKEN_LIFETIME_MINUTES', 60)
)
REFRESH_TOKEN_LIFETIME = timedelta(
    days=getattr(settings, 'JWT_AUTH', {}).get('REFRESH_TOKEN_LIFETIME_DAYS', 7)
)

# Password Policy Requirements
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPER = True
PASSWORD_REQUIRE_DIGIT = True
