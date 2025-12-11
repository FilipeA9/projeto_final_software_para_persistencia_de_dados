"""
HospedagemRepository - Data access layer for accommodations.

Provides CRUD operations for the Hospedagem model.
"""

from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.hospedagem import Hospedagem, TipoHospedagem
from src.repositories.base import BaseRepository


class HospedagemRepository(BaseRepository[Hospedagem]):
    """Repository for accommodation data access."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize HospedagemRepository.
        
        Args:
            db: Async database session.
        """
        super().__init__(Hospedagem, db)
    
    async def get_by_ponto_id(
        self,
        ponto_id: int,
        tipo: Optional[str] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None
    ) -> List[Hospedagem]:
        """
        Get all accommodations for a tourist spot with optional filters.
        
        Args:
            ponto_id: Tourist spot ID.
            tipo: Filter by accommodation type (hotel, pousada, hostel).
            max_price: Maximum average price filter.
            min_price: Minimum average price filter.
            
        Returns:
            List of Hospedagem instances.
        """
        conditions = [Hospedagem.ponto_id == ponto_id]
        
        if tipo:
            conditions.append(Hospedagem.tipo == tipo)
        
        if max_price is not None:
            conditions.append(Hospedagem.preco_medio <= max_price)
        
        if min_price is not None:
            conditions.append(Hospedagem.preco_medio >= min_price)
        
        query = select(Hospedagem).where(and_(*conditions)).order_by(Hospedagem.preco_medio.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_tipo(self, tipo: TipoHospedagem) -> List[Hospedagem]:
        """
        Get all accommodations of a specific type.
        
        Args:
            tipo: Accommodation type.
            
        Returns:
            List of Hospedagem instances.
        """
        query = select(Hospedagem).where(Hospedagem.tipo == tipo).order_by(Hospedagem.nome)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def search_by_name(self, search_term: str, ponto_id: Optional[int] = None) -> List[Hospedagem]:
        """
        Search accommodations by name.
        
        Args:
            search_term: Search term to match against accommodation names.
            ponto_id: Optional tourist spot ID filter.
            
        Returns:
            List of matching Hospedagem instances.
        """
        conditions = [Hospedagem.nome.ilike(f"%{search_term}%")]
        
        if ponto_id:
            conditions.append(Hospedagem.ponto_id == ponto_id)
        
        query = select(Hospedagem).where(and_(*conditions)).order_by(Hospedagem.nome)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_statistics(self, ponto_id: int) -> dict:
        """
        Get accommodation statistics for a tourist spot.
        
        Args:
            ponto_id: Tourist spot ID.
            
        Returns:
            Dictionary with statistics (count, avg_price, types).
        """
        accommodations = await self.get_by_ponto_id(ponto_id)
        
        if not accommodations:
            return {
                "total": 0,
                "avg_price": 0.0,
                "min_price": 0.0,
                "max_price": 0.0,
                "types": {}
            }
        
        prices = [float(h.preco_medio) for h in accommodations if h.preco_medio]
        types_count = {}
        
        for accommodation in accommodations:
            tipo = accommodation.tipo.value if hasattr(accommodation.tipo, 'value') else accommodation.tipo
            types_count[tipo] = types_count.get(tipo, 0) + 1
        
        return {
            "total": len(accommodations),
            "avg_price": sum(prices) / len(prices) if prices else 0.0,
            "min_price": min(prices) if prices else 0.0,
            "max_price": max(prices) if prices else 0.0,
            "types": types_count
        }
