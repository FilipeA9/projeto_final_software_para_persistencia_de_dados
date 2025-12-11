"""
Favorites API endpoints.

Provides REST API for managing user favorites.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.postgres import get_db
from src.dependencies.auth import get_current_user
from src.repositories.favorito_repository import FavoritoRepository
from src.repositories.spot_repository import SpotRepository
from src.services.favoritos_service import FavoritosService
from src.models.usuario import Usuario


router = APIRouter(prefix="/api", tags=["favorites"])


def get_favoritos_service(db: AsyncSession = Depends(get_db)) -> FavoritosService:
    """Dependency to get FavoritosService instance."""
    favorito_repo = FavoritoRepository(db)
    spot_repo = SpotRepository(db)
    return FavoritosService(favorito_repo, spot_repo)


@router.get(
    "/favorites",
    response_model=List[Dict[str, Any]],
    summary="Get user's favorites",
    description="Get all favorite tourist spots for the authenticated user."
)
async def get_my_favorites(
    current_user: Usuario = Depends(get_current_user),
    service: FavoritosService = Depends(get_favoritos_service)
):
    """
    Get authenticated user's favorites.
    
    Args:
        current_user: Current authenticated user.
        service: Favoritos service dependency.
        
    Returns:
        List of favorites with spot details.
    """
    return await service.get_user_favorites(current_user.id)


@router.post(
    "/spots/{spot_id}/favorite",
    status_code=status.HTTP_201_CREATED,
    summary="Add spot to favorites",
    description="Add a tourist spot to user's favorites."
)
async def add_favorite(
    spot_id: int,
    current_user: Usuario = Depends(get_current_user),
    service: FavoritosService = Depends(get_favoritos_service)
):
    """
    Add spot to favorites.
    
    Args:
        spot_id: Tourist spot ID.
        current_user: Current authenticated user.
        service: Favoritos service dependency.
        
    Returns:
        Created favorite information.
    """
    favorite = await service.add_favorite(current_user.id, spot_id)
    return {
        "id": favorite.id,
        "spot_id": favorite.ponto_id,
        "user_id": favorite.usuario_id,
        "created_at": favorite.created_at.isoformat(),
        "message": "Added to favorites"
    }


@router.delete(
    "/spots/{spot_id}/favorite",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove spot from favorites",
    description="Remove a tourist spot from user's favorites."
)
async def remove_favorite(
    spot_id: int,
    current_user: Usuario = Depends(get_current_user),
    service: FavoritosService = Depends(get_favoritos_service)
):
    """
    Remove spot from favorites.
    
    Args:
        spot_id: Tourist spot ID.
        current_user: Current authenticated user.
        service: Favoritos service dependency.
        
    Returns:
        No content on success.
    """
    await service.remove_favorite(current_user.id, spot_id)
    return None


@router.post(
    "/spots/{spot_id}/favorite/toggle",
    summary="Toggle favorite status",
    description="Toggle favorite status for a spot (add if not favorited, remove if already favorited)."
)
async def toggle_favorite(
    spot_id: int,
    current_user: Usuario = Depends(get_current_user),
    service: FavoritosService = Depends(get_favoritos_service)
):
    """
    Toggle favorite status for a spot.
    
    Args:
        spot_id: Tourist spot ID.
        current_user: Current authenticated user.
        service: Favoritos service dependency.
        
    Returns:
        Action taken and new status.
    """
    return await service.toggle_favorite(current_user.id, spot_id)


@router.get(
    "/spots/{spot_id}/favorite/status",
    summary="Check favorite status",
    description="Check if a spot is in user's favorites."
)
async def check_favorite_status(
    spot_id: int,
    current_user: Usuario = Depends(get_current_user),
    service: FavoritosService = Depends(get_favoritos_service)
):
    """
    Check if spot is favorited by user.
    
    Args:
        spot_id: Tourist spot ID.
        current_user: Current authenticated user.
        service: Favoritos service dependency.
        
    Returns:
        Favorite status.
    """
    is_favorited = await service.is_favorited(current_user.id, spot_id)
    return {
        "spot_id": spot_id,
        "is_favorited": is_favorited
    }
