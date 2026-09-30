"""
Authentication models: UserProfile and AuthAuditLog.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """
    Extends standard Django User with role-based access control and profile metadata.
    """
    class RoleChoices(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        DEVELOPER = 'DEVELOPER', 'Developer'
        VIEWER = 'VIEWER', 'Viewer'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.DEVELOPER)
    department = models.CharField(max_length=100, blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class AuthAuditLog(models.Model):
    """
    Audit log capturing authentication events for compliance and security forensics.
    """
    class ActionChoices(models.TextChoices):
        LOGIN_SUCCESS = 'LOGIN_SUCCESS', 'Login Success'
        LOGIN_FAILED = 'LOGIN_FAILED', 'Login Failed'
        LOGOUT = 'LOGOUT', 'Logout'
        TOKEN_REFRESH = 'TOKEN_REFRESH', 'Token Refresh'
        REGISTER = 'REGISTER', 'User Registered'

    username = models.CharField(max_length=150)
    action = models.CharField(max_length=32, choices=ActionChoices.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, default='')
    timestamp = models.DateTimeField(default=timezone.now)
    success = models.BooleanField(default=True)
    details = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.username} - {self.action} ({'Success' if self.success else 'Failed'})"
