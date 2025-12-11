"""
RatingService - Business logic for rating operations.

Handles rating creation, updates, and validation with spot aggregation.
"""

from typing import List, Optional, Dict
from fastapi import HTTPException, status

from src.repositories.rating_repository import RatingRepository
from src.repositories.spot_repository import SpotRepository


class RatingService:
    """Service for rating business logic."""
    
    def __init__(self, rating_repo: RatingRepository, spot_repo: SpotRepository):
        """
        Initialize rating service.
        
        Args:
            rating_repo: Rating repository instance.
            spot_repo: Spot repository instance (for validation).
        """
        self.rating_repo = rating_repo
        self.spot_repo = spot_repo
    
    async def create_rating(
        self, ponto_id: int, usuario_id: int, nota: int, comentario: Optional[str] = None
    ) -> dict:
        """
        Create a new rating for a tourist spot.
        
        Args:
            ponto_id: Tourist spot ID.
            usuario_id: User ID.
            nota: Rating value (1-5).
            comentario: Optional review comment.
        
        Returns:
            Created rating.
        
        Raises:
            HTTPException: If spot doesn't exist or user already rated.
        """
        # Validate spot exists
        spot = await self.spot_repo.get_by_id(ponto_id)
        if not spot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Not Found", "message": "Tourist spot not found", "code": "SPOT_001"}
            )
        
        # Check if user already rated this spot
        existing_rating = await self.rating_repo.get_by_user_and_spot(usuario_id, ponto_id)
        if existing_rating:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Conflict",
                    "message": "You have already rated this tourist spot",
                    "code": "RATING_001"
                }
            )
        
        # Validate rating value
        if nota < 1 or nota > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Validation error",
                    "message": "Rating must be between 1 and 5",
                    "code": "VAL_003"
                }
            )
        
        # Create rating
        rating_data = {
            "ponto_id": ponto_id,
            "usuario_id": usuario_id,
            "nota": nota,
            "comentario": comentario
        }
        
        rating = await self.rating_repo.create(rating_data)
        
        # Update spot's aggregated rating
        await self._update_spot_rating_aggregation(ponto_id)
        
        return rating
    
    async def update_rating(
        self, rating_id: int, usuario_id: int, nota: Optional[int] = None, comentario: Optional[str] = None
    ) -> dict:
        """
        Update an existing rating.
        
        Args:
            rating_id: Rating ID.
            usuario_id: User ID (for ownership validation).
            nota: New rating value (1-5).
            comentario: New review comment.
        
        Returns:
            Updated rating.
        
        Raises:
            HTTPException: If rating doesn't exist or user doesn't own it.
        """
        # Get existing rating
        rating = await self.rating_repo.get_by_id(rating_id)
        if not rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Not Found", "message": "Rating not found", "code": "RATING_003"}
            )
        
        # Verify ownership
        if rating.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Forbidden",
                    "message": "You can only edit your own ratings",
                    "code": "RATING_002"
                }
            )
        
        # Validate new rating value if provided
        if nota is not None and (nota < 1 or nota > 5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Validation error",
                    "message": "Rating must be between 1 and 5",
                    "code": "VAL_003"
                }
            )
        
        # Prepare update data
        update_data = {}
        if nota is not None:
            update_data["nota"] = nota
        if comentario is not None:
            update_data["comentario"] = comentario
        
        if not update_data:
            # No changes requested
            return rating
        
        # Update rating
        updated_rating = await self.rating_repo.update(rating_id, update_data)
        
        # Update spot's aggregated rating if nota changed
        if nota is not None:
            await self._update_spot_rating_aggregation(rating.ponto_id)
        
        return updated_rating
    
    async def delete_rating(self, rating_id: int, usuario_id: int, is_admin: bool = False) -> bool:
        """
        Delete a rating.
        
        Args:
            rating_id: Rating ID.
            usuario_id: User ID (for ownership validation).
            is_admin: Whether user has admin privileges.
        
        Returns:
            True if deleted successfully.
        
        Raises:
            HTTPException: If rating doesn't exist or user doesn't own it.
        """
        # Get existing rating
        rating = await self.rating_repo.get_by_id(rating_id)
        if not rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Not Found", "message": "Rating not found", "code": "RATING_003"}
            )
        
        # Verify ownership (admins can delete any rating)
        if not is_admin and rating.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Forbidden",
                    "message": "You can only delete your own ratings",
                    "code": "RATING_004"
                }
            )
        
        # Delete rating
        ponto_id = rating.ponto_id
        success = await self.rating_repo.delete(rating_id)
        
        # Update spot's aggregated rating
        if success:
            await self._update_spot_rating_aggregation(ponto_id)
        
        return success
    
    async def get_rating_statistics(self, ponto_id: int) -> Dict:
        """
        Get rating statistics for a tourist spot.
        
        Args:
            ponto_id: Tourist spot ID.
        
        Returns:
            Dictionary with average, total, and distribution.
        """
        distribution = await self.rating_repo.get_rating_distribution(ponto_id)
        avg_rating = await self.rating_repo.get_average_rating(ponto_id)
        total = await self.rating_repo.count_by_spot_id(ponto_id)
        
        return {
            "media": round(avg_rating, 2) if avg_rating else None,
            "total": total,
            "distribuicao": distribution
        }
    
    async def _update_spot_rating_aggregation(self, ponto_id: int):
        """
        Update spot's cached rating aggregation.
        
        This is an internal method to keep spot rating statistics up-to-date.
        
        Args:
            ponto_id: Tourist spot ID.
        """
        # Calculate new average and count
        avg_rating = await self.rating_repo.get_average_rating(ponto_id)
        rating_count = await self.rating_repo.count_by_spot_id(ponto_id)
        
        # Update spot record (if spot repository supports it)
        # This would require extending SpotRepository with an update method
        # For now, aggregation is calculated on-demand via queries
        pass
