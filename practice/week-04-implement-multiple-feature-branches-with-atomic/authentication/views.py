"""
Authentication REST views for register, login, refresh, profile, and logout.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    TokenRefreshSerializer,
    UserProfileSerializer
)
from .tokens import generate_auth_token_pair, decode_jwt_token
from .models import AuthAuditLog, UserProfile
from .permissions import HasValidJWTToken


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = generate_auth_token_pair(user.id, user.username, user.email)

            AuthAuditLog.objects.create(
                username=user.username,
                action=AuthAuditLog.ActionChoices.REGISTER,
                ip_address=_get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=True,
                details="User registered successfully"
            )

            return Response({
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = generate_auth_token_pair(user.id, user.username, user.email)

            AuthAuditLog.objects.create(
                username=user.username,
                action=AuthAuditLog.ActionChoices.LOGIN_SUCCESS,
                ip_address=_get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=True,
                details="Login authenticated"
            )

            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': getattr(user.profile, 'role', 'DEVELOPER'),
                },
                'tokens': tokens
            }, status=status.HTTP_200_OK)

        # Log failed attempt
        username = request.data.get('username', 'anonymous')
        AuthAuditLog.objects.create(
            username=username,
            action=AuthAuditLog.ActionChoices.LOGIN_FAILED,
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=False,
            details="Invalid credentials supplied"
        )
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class TokenRefreshView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        refresh_token = serializer.validated_data['refresh_token']
        payload = decode_jwt_token(refresh_token)

        if not payload or payload.get('token_type') != 'refresh':
            return Response({'error': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = payload.get('user_id')
        try:
            user = User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            return Response({'error': 'User not found or inactive'}, status=status.HTTP_404_NOT_FOUND)

        new_tokens = generate_auth_token_pair(user.id, user.username, user.email)
        AuthAuditLog.objects.create(
            username=user.username,
            action=AuthAuditLog.ActionChoices.TOKEN_REFRESH,
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=True,
            details="Token refreshed successfully"
        )

        return Response(new_tokens, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [HasValidJWTToken]

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            profile = UserProfile.objects.create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            profile = UserProfile.objects.create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [HasValidJWTToken]

    def post(self, request):
        AuthAuditLog.objects.create(
            username=request.user.username,
            action=AuthAuditLog.ActionChoices.LOGOUT,
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=True,
            details="User logged out"
        )
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
