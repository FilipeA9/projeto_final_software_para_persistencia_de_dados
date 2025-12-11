"""
RatingRepository - Repository for Avaliacao database operations.

Handles rating/review storage and aggregation calculations.
"""

from typing import List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.avaliacao import Avaliacao
from src.repositories.base import BaseRepository


class RatingRepository(BaseRepository):
    """Repository for rating operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Avaliacao, db)
    
    async def get_by_id(self, id: int) -> Optional[Avaliacao]:
        """Get rating by ID."""
        result = await self.db.execute(
            select(Avaliacao).where(Avaliacao.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Avaliacao]:
        """Get all ratings with pagination."""
        result = await self.db.execute(
            select(Avaliacao)
            .order_by(Avaliacao.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_spot_id(
        self, ponto_id: int, skip: int = 0, limit: int = 50
    ) -> List[Avaliacao]:
        """
        Get ratings for a specific tourist spot.
        
        Args:
            ponto_id: Tourist spot ID.
            skip: Number of records to skip.
            limit: Maximum number of records.
        
        Returns:
            List of ratings ordered by most recent.
        """
        result = await self.db.execute(
            select(Avaliacao)
            .where(Avaliacao.ponto_id == ponto_id)
            .order_by(Avaliacao.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_user_and_spot(
        self, usuario_id: int, ponto_id: int
    ) -> Optional[Avaliacao]:
        """
        Get rating by user and spot (unique constraint check).
        
        Args:
            usuario_id: User ID.
            ponto_id: Tourist spot ID.
        
        Returns:
            Existing rating or None.
        """
        result = await self.db.execute(
            select(Avaliacao).where(
                and_(
                    Avaliacao.usuario_id == usuario_id,
                    Avaliacao.ponto_id == ponto_id,
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_average_rating(self, ponto_id: int) -> Optional[float]:
        """
        Calculate average rating for a tourist spot.
        
        Args:
            ponto_id: Tourist spot ID.
        
        Returns:
            Average rating (1.0-5.0) or None if no ratings.
        """
        result = await self.db.execute(
            select(func.avg(Avaliacao.nota)).where(Avaliacao.ponto_id == ponto_id)
        )
        avg = result.scalar_one()
        return float(avg) if avg is not None else None
    
    async def count_by_spot_id(self, ponto_id: int) -> int:
        """
        Count total ratings for a tourist spot.
        
        Args:
            ponto_id: Tourist spot ID.
        
        Returns:
            Number of ratings.
        """
        result = await self.db.execute(
            select(func.count(Avaliacao.id)).where(Avaliacao.ponto_id == ponto_id)
        )
        return result.scalar_one()
    
    async def get_rating_distribution(self, ponto_id: int) -> dict:
        """
        Get rating distribution (count per star rating).
        
        Args:
            ponto_id: Tourist spot ID.
        
        Returns:
            Dictionary with star counts: {1: count, 2: count, ...}
        """
        result = await self.db.execute(
            select(Avaliacao.nota, func.count(Avaliacao.id))
            .where(Avaliacao.ponto_id == ponto_id)
            .group_by(Avaliacao.nota)
        )
        
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for nota, count in result.all():
            distribution[nota] = count
        
        return distribution
    
    async def create(self, obj_in: dict) -> Avaliacao:
        """Create new rating."""
        rating = Avaliacao(**obj_in)
        self.db.add(rating)
        await self.db.flush()
        await self.db.refresh(rating)
        return rating
    
    async def update(self, id: int, obj_in: dict) -> Optional[Avaliacao]:
        """Update existing rating."""
        rating = await self.get_by_id(id)
        if not rating:
            return None
        
        for key, value in obj_in.items():
            setattr(rating, key, value)
        
        await self.db.flush()
        await self.db.refresh(rating)
        return rating
    
    async def delete(self, id: int) -> bool:
        """Delete rating."""
        rating = await self.get_by_id(id)
        if not rating:
            return False
        
        await self.db.delete(rating)
        await self.db.flush()
        return True
