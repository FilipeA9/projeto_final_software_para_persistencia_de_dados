"""
FavoritosService - Business logic for user favorites.

Handles favorite operations with validation and error handling.
"""

from typing import List, Dict, Any
from fastapi import HTTPException, status

from src.repositories.favorito_repository import FavoritoRepository
from src.repositories.spot_repository import SpotRepository
from src.models.favorito import Favorito


class FavoritosService:
    """Service for favorites business logic."""
    
    def __init__(self, favorito_repo: FavoritoRepository, spot_repo: SpotRepository):
        """
        Initialize FavoritosService.
        
        Args:
            favorito_repo: Favorite repository.
            spot_repo: Spot repository.
        """
        self.favorito_repo = favorito_repo
        self.spot_repo = spot_repo
    
    async def add_favorite(self, usuario_id: int, ponto_id: int) -> Favorito:
        """
        Add a spot to user's favorites.
        
        Args:
            usuario_id: User ID.
            ponto_id: Tourist spot ID.
            
        Returns:
            Created Favorito instance.
            
        Raises:
            HTTPException: If spot not found or already favorited.
        """
        # Validate spot exists
        spot = await self.spot_repo.get_by_id(ponto_id)
        if not spot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tourist spot with ID {ponto_id} not found"
            )
        
        # Check if already favorited
        existing = await self.favorito_repo.get_by_user_and_spot(usuario_id, ponto_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This spot is already in your favorites"
            )
        
        # Create favorite
        favorito = Favorito(usuario_id=usuario_id, ponto_id=ponto_id)
        return await self.favorito_repo.create(favorito)
    
    async def remove_favorite(self, usuario_id: int, ponto_id: int) -> None:
        """
        Remove a spot from user's favorites.
        
        Args:
            usuario_id: User ID.
            ponto_id: Tourist spot ID.
            
        Raises:
            HTTPException: If favorite not found.
        """
        deleted = await self.favorito_repo.delete_by_user_and_spot(usuario_id, ponto_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Favorite not found"
            )
    
    async def get_user_favorites(self, usuario_id: int) -> List[Dict[str, Any]]:
        """
        Get all favorites for a user with spot details.
        
        Args:
            usuario_id: User ID.
            
        Returns:
            List of dictionaries with favorite and spot information.
        """
        favorites = await self.favorito_repo.get_user_favorites(usuario_id)
        
        result = []
        for favorite in favorites:
            spot = await self.spot_repo.get_by_id(favorite.ponto_id)
            if spot:
                result.append({
                    "favorite_id": favorite.id,
                    "spot_id": spot.id,
                    "spot_nome": spot.nome,
                    "spot_cidade": spot.cidade,
                    "spot_estado": spot.estado,
                    "spot_pais": spot.pais,
                    "spot_avg_rating": float(spot.avg_rating) if spot.avg_rating else None,
                    "spot_rating_count": spot.rating_count,
                    "favorited_at": favorite.created_at.isoformat()
                })
        
        return result
    
    async def is_favorited(self, usuario_id: int, ponto_id: int) -> bool:
        """
        Check if a spot is in user's favorites.
        
        Args:
            usuario_id: User ID.
            ponto_id: Tourist spot ID.
            
        Returns:
            True if favorited, False otherwise.
        """
        return await self.favorito_repo.is_favorited(usuario_id, ponto_id)
    
    async def get_favorite_spot_ids(self, usuario_id: int) -> List[int]:
        """
        Get list of spot IDs in user's favorites.
        
        Args:
            usuario_id: User ID.
            
        Returns:
            List of spot IDs.
        """
        return await self.favorito_repo.get_user_favorite_spot_ids(usuario_id)
    
    async def toggle_favorite(self, usuario_id: int, ponto_id: int) -> Dict[str, Any]:
        """
        Toggle favorite status for a spot.
        
        Args:
            usuario_id: User ID.
            ponto_id: Tourist spot ID.
            
        Returns:
            Dictionary with action taken and new status.
        """
        is_favorited = await self.is_favorited(usuario_id, ponto_id)
        
        if is_favorited:
            await self.remove_favorite(usuario_id, ponto_id)
            return {
                "action": "removed",
                "is_favorited": False,
                "message": "Removed from favorites"
            }
        else:
            await self.add_favorite(usuario_id, ponto_id)
            return {
                "action": "added",
                "is_favorited": True,
                "message": "Added to favorites"
            }
