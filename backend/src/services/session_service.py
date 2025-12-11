"""
SessionService - Redis session management.

Handles active user sessions and session validation.
"""

from typing import Optional, Dict, Any
from src.config.redis import cache_get, cache_set, cache_delete
from src.config.settings import settings


class SessionService:
    """Service for managing user sessions in Redis."""
    
    @staticmethod
    async def create_session(user_id: int, token: str, user_data: Dict[str, Any]) -> None:
        """
        Create a new user session.
        
        Args:
            user_id: User ID.
            token: Access token.
            user_data: Additional user data to store in session.
        """
        session_key = f"session:{user_id}"
        session_data = {
            "user_id": user_id,
            "token": token,
            "user": user_data,
            "active": True,
        }
        
        await cache_set(
            session_key,
            session_data,
            ttl=settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        )
    
    @staticmethod
    async def get_session(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user session data.
        
        Args:
            user_id: User ID.
        
        Returns:
            Session data or None if not found.
        """
        session_key = f"session:{user_id}"
        return await cache_get(session_key)
    
    @staticmethod
    async def delete_session(user_id: int) -> bool:
        """
        Delete user session.
        
        Args:
            user_id: User ID.
        
        Returns:
            True if deleted successfully.
        """
        session_key = f"session:{user_id}"
        return await cache_delete(session_key)
    
    @staticmethod
    async def is_session_active(user_id: int) -> bool:
        """
        Check if user has an active session.
        
        Args:
            user_id: User ID.
        
        Returns:
            True if session is active, False otherwise.
        """
        session = await SessionService.get_session(user_id)
        return session is not None and session.get("active", False)
    
    @staticmethod
    async def refresh_session(user_id: int) -> bool:
        """
        Refresh session TTL (extend expiration).
        
        Args:
            user_id: User ID.
        
        Returns:
            True if refreshed successfully.
        """
        session = await SessionService.get_session(user_id)
        if not session:
            return False
        
        # Re-set with new TTL
        session_key = f"session:{user_id}"
        await cache_set(
            session_key,
            session,
            ttl=settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        )
        
        return True
