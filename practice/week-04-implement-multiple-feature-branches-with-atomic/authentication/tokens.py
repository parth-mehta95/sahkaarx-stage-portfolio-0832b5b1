"""
JWT Token management utilities for encoding, decoding, and signature validation.
"""

import base64
import hashlib
import hmac
import json
import time
from typing import Dict, Any, Optional
from .config import SECRET_KEY, ACCESS_TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')


def _base64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4)) if (len(data) % 4) != 0 else ''
    return base64.urlsafe_b64decode((data + padding).encode('utf-8'))


def generate_jwt_token(payload: Dict[str, Any], secret: str = SECRET_KEY) -> str:
    """
    Generates a secure HMAC-SHA256 signed JSON Web Token.
    """
    header = {"alg": "HS256", "typ": "JWT"}
    encoded_header = _base64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))

    signing_input = f"{encoded_header}.{encoded_payload}".encode('utf-8')
    signature = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
    encoded_signature = _base64url_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def decode_jwt_token(token: str, secret: str = SECRET_KEY) -> Optional[Dict[str, Any]]:
    """
    Decodes and validates a JSON Web Token against secret signature and expiry timestamp.
    Returns decoded dictionary payload on success, None on invalid signature or expiry.
    """
    parts = token.split('.')
    if len(parts) != 3:
        return None

    encoded_header, encoded_payload, encoded_signature = parts
    try:
        signing_input = f"{encoded_header}.{encoded_payload}".encode('utf-8')
        expected_sig = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
        provided_sig = _base64url_decode(encoded_signature)

        if not hmac.compare_digest(expected_sig, provided_sig):
            return None

        payload_bytes = _base64url_decode(encoded_payload)
        payload = json.loads(payload_bytes.decode('utf-8'))

        # Check expiry
        exp = payload.get('exp')
        if exp and exp < time.time():
            return None

        return payload
    except Exception:
        return None


def generate_auth_token_pair(user_id: int, username: str, email: str) -> Dict[str, Any]:
    """
    Generates an access token and refresh token pair for authenticated user session.
    """
    current_time = int(time.time())
    access_exp = current_time + int(ACCESS_TOKEN_LIFETIME.total_seconds())
    refresh_exp = current_time + int(REFRESH_TOKEN_LIFETIME.total_seconds())

    access_payload = {
        'token_type': 'access',
        'user_id': user_id,
        'username': username,
        'email': email,
        'iat': current_time,
        'exp': access_exp,
    }

    refresh_payload = {
        'token_type': 'refresh',
        'user_id': user_id,
        'iat': current_time,
        'exp': refresh_exp,
    }

    return {
        'access_token': generate_jwt_token(access_payload),
        'refresh_token': generate_jwt_token(refresh_payload),
        'token_type': 'Bearer',
        'expires_in': int(ACCESS_TOKEN_LIFETIME.total_seconds()),
    }
