"""
SpotRepository - Repository for PontoTuristico database operations.

Implements data access layer for tourist spots with filtering and pagination.
"""

from typing import List, Optional
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from src.models.ponto_turistico import PontoTuristico
from src.repositories.base import BaseRepository


class SpotRepository(BaseRepository):
    """Repository for tourist spot operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(PontoTuristico, db)
    
    async def get_by_id(self, id: int) -> Optional[PontoTuristico]:
        """
        Get tourist spot by ID (only active, not soft-deleted).
        
        Args:
            id: Spot ID.
        
        Returns:
            PontoTuristico if found and active, None otherwise.
        """
        result = await self.db.execute(
            select(PontoTuristico).where(
                and_(
                    PontoTuristico.id == id,
                    PontoTuristico.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        cidade: Optional[str] = None,
        estado: Optional[str] = None,
        pais: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[PontoTuristico]:
        """
        Get all tourist spots with filters and pagination.
        
        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            cidade: Filter by city name.
            estado: Filter by state name.
            pais: Filter by country name.
            search: Search in name and description.
        
        Returns:
            List of tourist spots matching filters.
        """
        query = select(PontoTuristico).where(PontoTuristico.deleted_at.is_(None))
        
        # Apply filters
        if cidade:
            query = query.where(PontoTuristico.cidade.ilike(f"%{cidade}%"))
        if estado:
            query = query.where(PontoTuristico.estado.ilike(f"%{estado}%"))
        if pais:
            query = query.where(PontoTuristico.pais.ilike(f"%{pais}%"))
        if search:
            query = query.where(
                or_(
                    PontoTuristico.nome.ilike(f"%{search}%"),
                    PontoTuristico.descricao.ilike(f"%{search}%"),
                )
            )
        
        # Order by creation date (newest first)
        query = query.order_by(PontoTuristico.created_at.desc())
        
        # Pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_all(
        self,
        cidade: Optional[str] = None,
        estado: Optional[str] = None,
        pais: Optional[str] = None,
        search: Optional[str] = None,
    ) -> int:
        """
        Count total spots matching filters.
        
        Args:
            cidade: Filter by city name.
            estado: Filter by state name.
            pais: Filter by country name.
            search: Search in name and description.
        
        Returns:
            Total count of spots.
        """
        query = select(func.count(PontoTuristico.id)).where(
            PontoTuristico.deleted_at.is_(None)
        )
        
        # Apply same filters as get_all
        if cidade:
            query = query.where(PontoTuristico.cidade.ilike(f"%{cidade}%"))
        if estado:
            query = query.where(PontoTuristico.estado.ilike(f"%{estado}%"))
        if pais:
            query = query.where(PontoTuristico.pais.ilike(f"%{pais}%"))
        if search:
            query = query.where(
                or_(
                    PontoTuristico.nome.ilike(f"%{search}%"),
                    PontoTuristico.descricao.ilike(f"%{search}%"),
                )
            )
        
        result = await self.db.execute(query)
        return result.scalar_one()
    
    async def create(self, obj_in: dict) -> PontoTuristico:
        """Create new tourist spot."""
        spot = PontoTuristico(**obj_in)
        self.db.add(spot)
        await self.db.flush()
        await self.db.refresh(spot)
        return spot
    
    async def update(self, id: int, obj_in: dict) -> Optional[PontoTuristico]:
        """Update existing tourist spot."""
        spot = await self.get_by_id(id)
        if not spot:
            return None
        
        for key, value in obj_in.items():
            setattr(spot, key, value)
        
        await self.db.flush()
        await self.db.refresh(spot)
        return spot
    
    async def delete(self, id: int) -> bool:
        """Soft delete tourist spot (set deleted_at timestamp)."""
        spot = await self.get_by_id(id)
        if not spot:
            return False
        
        from datetime import datetime
        spot.deleted_at = datetime.utcnow()
        await self.db.flush()
        return True
    
    async def get_by_location(
        self, latitude: Decimal, longitude: Decimal, radius_km: float = 10.0
    ) -> List[PontoTuristico]:
        """
        Get spots near a location (simple bounding box, not true geodesic).
        
        Args:
            latitude: Center latitude.
            longitude: Center longitude.
            radius_km: Search radius in kilometers.
        
        Returns:
            List of nearby tourist spots.
        """
        # Approximate degrees per km (simplified)
        lat_delta = Decimal(radius_km / 111.0)  # 1 degree lat ≈ 111 km
        lon_delta = Decimal(radius_km / (111.0 * float(abs(latitude))))
        
        query = select(PontoTuristico).where(
            and_(
                PontoTuristico.deleted_at.is_(None),
                PontoTuristico.latitude.between(latitude - lat_delta, latitude + lat_delta),
                PontoTuristico.longitude.between(longitude - lon_delta, longitude + lon_delta),
            )
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
