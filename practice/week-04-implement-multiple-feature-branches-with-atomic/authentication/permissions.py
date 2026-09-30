"""
Authentication permission classes for custom token verification and RBAC.
"""

from rest_framework.permissions import BasePermission
from django.contrib.auth.models import User
from .tokens import decode_jwt_token


class HasValidJWTToken(BasePermission):
    """
    Validates custom JWT Bearer token in Authorization header.
    """
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False

        token = auth_header.split(' ')[1].strip()
        payload = decode_jwt_token(token)
        if not payload or payload.get('token_type') != 'access':
            return False

        user_id = payload.get('user_id')
        try:
            request.user = User.objects.get(pk=user_id, is_active=True)
            return True
        except User.DoesNotExist:
            return False


class IsAdminUserRole(BasePermission):
    """
    Allows access only to users with the ADMIN role.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, 'profile', None)
        return profile and profile.role == 'ADMIN'
