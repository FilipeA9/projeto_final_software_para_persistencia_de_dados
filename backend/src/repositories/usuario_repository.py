"""
UsuarioRepository - Repository for Usuario database operations.

Handles user CRUD operations and authentication queries.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.usuario import Usuario, UserRole
from src.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository):
    """Repository for user operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Usuario, db)
    
    async def get_by_id(self, id: int) -> Optional[Usuario]:
        """Get user by ID."""
        result = await self.db.execute(
            select(Usuario).where(Usuario.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[Usuario]:
        """
        Get user by email address.
        
        Args:
            email: User email.
        
        Returns:
            Usuario if found, None otherwise.
        """
        result = await self.db.execute(
            select(Usuario).where(Usuario.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_login(self, login: str) -> Optional[Usuario]:
        """
        Get user by login username.
        
        Args:
            login: Username.
        
        Returns:
            Usuario if found, None otherwise.
        """
        result = await self.db.execute(
            select(Usuario).where(Usuario.login == login)
        )
        return result.scalar_one_or_none()
    
    async def email_exists(self, email: str) -> bool:
        """
        Check if email is already registered.
        
        Args:
            email: Email to check.
        
        Returns:
            True if email exists, False otherwise.
        """
        user = await self.get_by_email(email)
        return user is not None
    
    async def login_exists(self, login: str) -> bool:
        """
        Check if login username is already taken.
        
        Args:
            login: Username to check.
        
        Returns:
            True if login exists, False otherwise.
        """
        user = await self.get_by_login(login)
        return user is not None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Usuario]:
        """Get all users with pagination."""
        result = await self.db.execute(
            select(Usuario)
            .order_by(Usuario.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, obj_in: dict) -> Usuario:
        """
        Create new user.
        
        Args:
            obj_in: User data dict (login, email, senha_hash, role).
        
        Returns:
            Created Usuario instance.
        """
        user = Usuario(**obj_in)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def update(self, id: int, obj_in: dict) -> Optional[Usuario]:
        """Update existing user."""
        user = await self.get_by_id(id)
        if not user:
            return None
        
        for key, value in obj_in.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def delete(self, id: int) -> bool:
        """Delete user (hard delete)."""
        user = await self.get_by_id(id)
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.flush()
        return True
