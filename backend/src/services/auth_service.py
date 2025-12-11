"""
AuthService - Business logic for authentication and user management.

Handles registration, login, logout, and session management with Redis.
"""

from typing import Optional, Dict, Any
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.usuario_repository import UsuarioRepository
from src.utils.security import hash_password, verify_password
from src.utils.jwt import create_access_token
from src.config.redis import cache_set, cache_get, cache_delete
from src.config.settings import settings
from src.models.usuario import Usuario, UserRole


class AuthService:
    """Service layer for authentication business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.usuario_repo = UsuarioRepository(db)
    
    async def register_user(
        self, login: str, email: str, password: str, role: UserRole = UserRole.USER
    ) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            login: Username (must be unique).
            email: Email address (must be unique).
            password: Plain text password (will be hashed).
            role: User role (default: USER).
        
        Returns:
            Dictionary with user info and access token.
        
        Raises:
            ValueError: If login or email already exists.
        """
        # Check if login already exists
        if await self.usuario_repo.login_exists(login):
            raise ValueError(f"Login '{login}' already exists")
        
        # Check if email already exists
        if await self.usuario_repo.email_exists(email):
            raise ValueError(f"Email '{email}' already registered")
        
        # Hash password
        senha_hash = hash_password(password)
        
        # Create user
        user_data = {
            "login": login,
            "email": email,
            "senha_hash": senha_hash,
            "role": role,
        }
        
        user = await self.usuario_repo.create(user_data)
        await self.db.commit()
        
        # Generate access token
        token = create_access_token(
            data={"sub": user.login, "user_id": user.id, "role": user.role.value}
        )
        
        # Store session in Redis
        await self._store_session(user.id, token)
        
        return {
            "user": {
                "id": user.id,
                "login": user.login,
                "email": user.email,
                "role": user.role.value,
                "created_at": user.created_at.isoformat(),
            },
            "access_token": token,
            "token_type": "bearer",
        }
    
    async def login(self, login: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and generate access token.
        
        Args:
            login: Username or email.
            password: Plain text password.
        
        Returns:
            Dictionary with user info and access token.
        
        Raises:
            ValueError: If credentials are invalid.
        """
        # Try to find user by login or email
        user = await self.usuario_repo.get_by_login(login)
        if not user:
            user = await self.usuario_repo.get_by_email(login)
        
        if not user:
            raise ValueError("Invalid credentials")
        
        # Verify password
        if not verify_password(password, user.senha_hash):
            raise ValueError("Invalid credentials")
        
        # Generate access token
        token = create_access_token(
            data={"sub": user.login, "user_id": user.id, "role": user.role.value}
        )
        
        # Store session in Redis
        await self._store_session(user.id, token)
        
        return {
            "user": {
                "id": user.id,
                "login": user.login,
                "email": user.email,
                "role": user.role.value,
                "created_at": user.created_at.isoformat(),
            },
            "access_token": token,
            "token_type": "bearer",
        }
    
    async def logout(self, user_id: int, token: str) -> bool:
        """
        Logout user by invalidating session.
        
        Args:
            user_id: User ID.
            token: Access token to invalidate.
        
        Returns:
            True if logout successful.
        """
        # Remove session from Redis
        session_key = f"session:{user_id}"
        await cache_delete(session_key)
        
        # Blacklist token (optional - for extra security)
        blacklist_key = f"token:blacklist:{token}"
        await cache_set(
            blacklist_key,
            {"user_id": user_id, "invalidated": True},
            ttl=settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        )
        
        return True
    
    async def get_current_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get current user information.
        
        Args:
            user_id: User ID.
        
        Returns:
            User info dictionary or None.
        """
        user = await self.usuario_repo.get_by_id(user_id)
        if not user:
            return None
        
        return {
            "id": user.id,
            "login": user.login,
            "email": user.email,
            "role": user.role.value,
            "created_at": user.created_at.isoformat(),
        }
    
    async def is_token_valid(self, token: str) -> bool:
        """
        Check if token is valid and not blacklisted.
        
        Args:
            token: Access token.
        
        Returns:
            True if token is valid, False otherwise.
        """
        # Check blacklist
        blacklist_key = f"token:blacklist:{token}"
        blacklisted = await cache_get(blacklist_key)
        
        return blacklisted is None
    
    async def _store_session(self, user_id: int, token: str) -> None:
        """
        Store user session in Redis.
        
        Args:
            user_id: User ID.
            token: Access token.
        """
        session_key = f"session:{user_id}"
        session_data = {
            "user_id": user_id,
            "token": token,
            "active": True,
        }
        
        # Store with same TTL as access token
        await cache_set(
            session_key,
            session_data,
            ttl=settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        )
