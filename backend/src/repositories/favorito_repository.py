"""
FavoritoRepository - Data access layer for favorites.

Provides operations for managing user favorites.
"""

from typing import Optional, List
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.favorito import Favorito
from src.repositories.base import BaseRepository


class FavoritoRepository(BaseRepository[Favorito]):
    """Repository for favorite data access."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize FavoritoRepository.
        
        Args:
            db: Async database session.
        """
        super().__init__(Favorito, db)
    
    async def get_by_user_and_spot(self, usuario_id: int, ponto_id: int) -> Optional[Favorito]:
        """
        Get favorite by user ID and spot ID.
        
        Args:
            usuario_id: User ID.
            ponto_id: Tourist spot ID.
            
        Returns:
            Favorito instance if exists, None otherwise.
        """
        query = select(Favorito).where(
            and_(
                Favorito.usuario_id == usuario_id,
                Favorito.ponto_id == ponto_id
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_favorites(self, usuario_id: int) -> List[Favorito]:
        """
        Get all favorites for a user.
        
        Args:
            usuario_id: User ID.
            
        Returns:
            List of Favorito instances ordered by creation date (newest first).
        """
        query = (
            select(Favorito)
            .where(Favorito.usuario_id == usuario_id)
            .order_by(Favorito.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_spot_favorites_count(self, ponto_id: int) -> int:
        """
        Get count of favorites for a specific spot.
        
        Args:
            ponto_id: Tourist spot ID.
            
        Returns:
            Number of users who favorited this spot.
        """
        query = select(Favorito).where(Favorito.ponto_id == ponto_id)
        result = await self.db.execute(query)
        return len(list(result.scalars().all()))
    
    async def delete_by_user_and_spot(self, usuario_id: int, ponto_id: int) -> bool:
        """
        Delete a favorite by user ID and spot ID.
        
        Args:
            usuario_id: User ID.
            ponto_id: Tourist spot ID.
            
        Returns:
            True if deleted, False if not found.
        """
        favorite = await self.get_by_user_and_spot(usuario_id, ponto_id)
        if favorite:
            await self.delete(favorite.id)
            return True
        return False
    
    async def is_favorited(self, usuario_id: int, ponto_id: int) -> bool:
        """
        Check if a spot is favorited by a user.
        
        Args:
            usuario_id: User ID.
            ponto_id: Tourist spot ID.
            
        Returns:
            True if favorited, False otherwise.
        """
        favorite = await self.get_by_user_and_spot(usuario_id, ponto_id)
        return favorite is not None
    
    async def get_user_favorite_spot_ids(self, usuario_id: int) -> List[int]:
        """
        Get list of spot IDs favorited by a user.
        
        Args:
            usuario_id: User ID.
            
        Returns:
            List of spot IDs.
        """
        favorites = await self.get_user_favorites(usuario_id)
        return [fav.ponto_id for fav in favorites]
