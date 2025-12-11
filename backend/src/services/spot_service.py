"""
SpotService - Business logic for tourist spot operations.

Coordinates between repositories and implements caching strategy.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.spot_repository import SpotRepository
from src.repositories.rating_repository import RatingRepository
from src.repositories.photo_repository import PhotoRepository
from src.config.redis import cache_get, cache_set, cache_delete, cache_clear_pattern
from src.config.settings import settings
from src.models.ponto_turistico import PontoTuristico


class SpotService:
    """Service layer for tourist spot business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.spot_repo = SpotRepository(db)
        self.rating_repo = RatingRepository(db)
        self.photo_repo = PhotoRepository()
    
    async def get_spot_by_id(self, spot_id: int) -> Optional[Dict[str, Any]]:
        """
        Get tourist spot with enriched data (ratings, photo count).
        Uses Redis caching.
        
        Args:
            spot_id: Tourist spot ID.
        
        Returns:
            Enriched spot dictionary or None.
        """
        # Try cache first
        cache_key = f"spot:{spot_id}"
        cached = await cache_get(cache_key)
        if cached:
            return cached
        
        # Get from database
        spot = await self.spot_repo.get_by_id(spot_id)
        if not spot:
            return None
        
        # Enrich with rating data
        avg_rating = await self.rating_repo.get_average_rating(spot_id)
        rating_count = await self.rating_repo.count_by_spot_id(spot_id)
        photo_count = await self.photo_repo.count_by_spot_id(spot_id)
        
        result = {
            "id": spot.id,
            "nome": spot.nome,
            "descricao": spot.descricao,
            "cidade": spot.cidade,
            "estado": spot.estado,
            "pais": spot.pais,
            "latitude": float(spot.latitude),
            "longitude": float(spot.longitude),
            "endereco": spot.endereco,
            "criado_por": spot.criado_por,
            "created_at": spot.created_at.isoformat(),
            "avg_rating": round(avg_rating, 2) if avg_rating else None,
            "rating_count": rating_count,
            "photo_count": photo_count,
        }
        
        # Cache for 5 minutes
        await cache_set(cache_key, result, ttl=settings.CACHE_SPOT_DETAILS_TTL)
        
        return result
    
    async def list_spots(
        self,
        skip: int = 0,
        limit: int = 20,
        cidade: Optional[str] = None,
        estado: Optional[str] = None,
        pais: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List tourist spots with filters and pagination.
        
        Args:
            skip: Records to skip.
            limit: Max records to return.
            cidade: Filter by city.
            estado: Filter by state.
            pais: Filter by country.
            search: Search query.
        
        Returns:
            Dictionary with spots, total count, and pagination info.
        """
        # Build cache key from filters
        cache_key = f"spots:list:{skip}:{limit}:{cidade}:{estado}:{pais}:{search}"
        cached = await cache_get(cache_key)
        if cached:
            return cached
        
        # Get spots and count
        spots = await self.spot_repo.get_all(
            skip=skip, limit=limit, cidade=cidade, estado=estado, pais=pais, search=search
        )
        total = await self.spot_repo.count_all(
            cidade=cidade, estado=estado, pais=pais, search=search
        )
        
        # Enrich each spot with basic stats
        enriched_spots = []
        for spot in spots:
            avg_rating = await self.rating_repo.get_average_rating(spot.id)
            rating_count = await self.rating_repo.count_by_spot_id(spot.id)
            
            enriched_spots.append({
                "id": spot.id,
                "nome": spot.nome,
                "descricao": spot.descricao[:200] + "..." if len(spot.descricao) > 200 else spot.descricao,
                "cidade": spot.cidade,
                "estado": spot.estado,
                "pais": spot.pais,
                "avg_rating": round(avg_rating, 2) if avg_rating else None,
                "rating_count": rating_count,
            })
        
        result = {
            "spots": enriched_spots,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total,
        }
        
        # Cache for 1 minute (shorter than details)
        await cache_set(cache_key, result, ttl=settings.CACHE_SPOT_LIST_TTL)
        
        return result
    
    async def invalidate_spot_cache(self, spot_id: int) -> None:
        """
        Invalidate all cache entries for a spot.
        
        Args:
            spot_id: Tourist spot ID.
        """
        await cache_delete(f"spot:{spot_id}")
        await cache_clear_pattern("spots:list:*")
