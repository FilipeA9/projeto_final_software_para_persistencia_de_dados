"""
JWT token generation and validation utilities.

Handles access token creation and verification for authentication.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import JWTError, jwt

from src.config.settings import settings


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary payload to encode in token (typically user info).
        expires_delta: Optional custom expiration time delta.
    
    Returns:
        Encoded JWT token string.
    
    Example:
        >>> token = create_access_token({"sub": "user@example.com", "user_id": 1})
        >>> len(token) > 100
        True
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token string to decode.
    
    Returns:
        Decoded token payload as dictionary, or None if invalid.
    
    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> payload = decode_access_token(token)
        >>> payload["sub"]
        'user@example.com'
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def extract_user_id_from_token(token: str) -> Optional[int]:
    """
    Extract user ID from JWT token.
    
    Args:
        token: JWT token string.
    
    Returns:
        User ID if token is valid and contains user_id, None otherwise.
    
    Example:
        >>> token = create_access_token({"user_id": 42})
        >>> extract_user_id_from_token(token)
        42
    """
    payload = decode_access_token(token)
    if payload and "user_id" in payload:
        return payload["user_id"]
    return None


def extract_username_from_token(token: str) -> Optional[str]:
    """
    Extract username (sub claim) from JWT token.
    
    Args:
        token: JWT token string.
    
    Returns:
        Username if token is valid and contains sub claim, None otherwise.
    
    Example:
        >>> token = create_access_token({"sub": "johndoe"})
        >>> extract_username_from_token(token)
        'johndoe'
    """
    payload = decode_access_token(token)
    if payload and "sub" in payload:
        return payload["sub"]
    return None
