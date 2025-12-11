"""
Authentication dependencies for FastAPI.

Provides dependency injection for JWT token validation and user authentication.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.postgres import get_db
from src.utils.jwt import decode_access_token
from src.models.usuario import Usuario, UserRole

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Authorization header with Bearer token.
        db: Database session.
    
    Returns:
        Usuario: Authenticated user object.
    
    Raises:
        HTTPException: 401 if token is invalid or user not found.
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: Usuario = Depends(get_current_user)):
            return {"user_id": user.id}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    
    # Query user from database
    from sqlalchemy import select
    result = await db.execute(select(Usuario).where(Usuario.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    """
    Get current active user (additional checks can be added here).
    
    Args:
        current_user: Current authenticated user.
    
    Returns:
        Usuario: Active user object.
    
    Usage:
        @app.get("/profile")
        async def get_profile(user: Usuario = Depends(get_current_active_user)):
            return {"login": user.login}
    """
    # Future: Add account status checks (e.g., is_active, is_banned)
    return current_user


async def get_current_admin_user(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    """
    Get current user and verify admin role.
    
    Args:
        current_user: Current authenticated user.
    
    Returns:
        Usuario: Admin user object.
    
    Raises:
        HTTPException: 403 if user is not an admin.
    
    Usage:
        @app.delete("/spots/{id}")
        async def delete_spot(id: int, admin: Usuario = Depends(get_current_admin_user)):
            ...
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


# Optional dependency - returns None if no token provided
async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db),
) -> Optional[Usuario]:
    """
    Get current user if authenticated, None otherwise (no error raised).
    
    Useful for endpoints that work differently for authenticated vs anonymous users.
    
    Args:
        credentials: Optional HTTP Authorization header.
        db: Database session.
    
    Returns:
        Usuario if authenticated, None otherwise.
    
    Usage:
        @app.get("/spots")
        async def list_spots(user: Optional[Usuario] = Depends(get_optional_current_user)):
            # Show different data based on authentication
            if user:
                # Include user-specific data
                ...
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        return None
    
    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        return None
    
    from sqlalchemy import select
    result = await db.execute(select(Usuario).where(Usuario.id == user_id))
    return result.scalar_one_or_none()
