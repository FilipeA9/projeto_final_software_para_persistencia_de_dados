"""
HospedagemService - Business logic for accommodations.

Handles accommodation operations with validation and error handling.
"""

from typing import Optional, List
from fastapi import HTTPException, status
from decimal import Decimal

from src.repositories.hospedagem_repository import HospedagemRepository
from src.repositories.spot_repository import SpotRepository
from src.models.hospedagem import Hospedagem, TipoHospedagem


class HospedagemService:
    """Service for accommodation business logic."""
    
    def __init__(self, hospedagem_repo: HospedagemRepository, spot_repo: SpotRepository):
        """
        Initialize HospedagemService.
        
        Args:
            hospedagem_repo: Accommodation repository.
            spot_repo: Spot repository.
        """
        self.hospedagem_repo = hospedagem_repo
        self.spot_repo = spot_repo
    
    async def create_accommodation(
        self,
        ponto_id: int,
        nome: str,
        endereco: str,
        tipo: str,
        telefone: Optional[str] = None,
        preco_medio: Optional[float] = None,
        link_reserva: Optional[str] = None
    ) -> Hospedagem:
        """
        Create a new accommodation.
        
        Args:
            ponto_id: Tourist spot ID.
            nome: Accommodation name.
            endereco: Full address.
            tipo: Accommodation type (hotel, pousada, hostel).
            telefone: Contact phone number.
            preco_medio: Average price per night.
            link_reserva: Booking URL.
            
        Returns:
            Created Hospedagem instance.
            
        Raises:
            HTTPException: If spot not found or validation fails.
        """
        # Validate tourist spot exists
        spot = await self.spot_repo.get_by_id(ponto_id)
        if not spot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tourist spot with ID {ponto_id} not found"
            )
        
        # Validate tipo
        try:
            tipo_enum = TipoHospedagem(tipo)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid accommodation type: {tipo}. Must be one of: hotel, pousada, hostel"
            )
        
        # Validate price
        if preco_medio is not None and preco_medio < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Average price must be non-negative"
            )
        
        # Create accommodation
        hospedagem = Hospedagem(
            ponto_id=ponto_id,
            nome=nome,
            endereco=endereco,
            tipo=tipo_enum,
            telefone=telefone,
            preco_medio=Decimal(str(preco_medio)) if preco_medio is not None else None,
            link_reserva=link_reserva
        )
        
        return await self.hospedagem_repo.create(hospedagem)
    
    async def get_accommodation(self, accommodation_id: int) -> Hospedagem:
        """
        Get accommodation by ID.
        
        Args:
            accommodation_id: Accommodation ID.
            
        Returns:
            Hospedagem instance.
            
        Raises:
            HTTPException: If accommodation not found.
        """
        accommodation = await self.hospedagem_repo.get_by_id(accommodation_id)
        if not accommodation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Accommodation with ID {accommodation_id} not found"
            )
        return accommodation
    
    async def get_accommodations_for_spot(
        self,
        ponto_id: int,
        tipo: Optional[str] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None
    ) -> List[Hospedagem]:
        """
        Get all accommodations for a tourist spot with filters.
        
        Args:
            ponto_id: Tourist spot ID.
            tipo: Filter by accommodation type.
            max_price: Maximum average price.
            min_price: Minimum average price.
            
        Returns:
            List of Hospedagem instances.
            
        Raises:
            HTTPException: If spot not found.
        """
        # Validate spot exists
        spot = await self.spot_repo.get_by_id(ponto_id)
        if not spot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tourist spot with ID {ponto_id} not found"
            )
        
        return await self.hospedagem_repo.get_by_ponto_id(
            ponto_id=ponto_id,
            tipo=tipo,
            max_price=max_price,
            min_price=min_price
        )
    
    async def update_accommodation(
        self,
        accommodation_id: int,
        nome: Optional[str] = None,
        endereco: Optional[str] = None,
        tipo: Optional[str] = None,
        telefone: Optional[str] = None,
        preco_medio: Optional[float] = None,
        link_reserva: Optional[str] = None
    ) -> Hospedagem:
        """
        Update accommodation details.
        
        Args:
            accommodation_id: Accommodation ID.
            nome: New name.
            endereco: New address.
            tipo: New type.
            telefone: New phone.
            preco_medio: New average price.
            link_reserva: New booking URL.
            
        Returns:
            Updated Hospedagem instance.
            
        Raises:
            HTTPException: If accommodation not found or validation fails.
        """
        accommodation = await self.get_accommodation(accommodation_id)
        
        if nome is not None:
            accommodation.nome = nome
        
        if endereco is not None:
            accommodation.endereco = endereco
        
        if tipo is not None:
            try:
                accommodation.tipo = TipoHospedagem(tipo)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid accommodation type: {tipo}"
                )
        
        if telefone is not None:
            accommodation.telefone = telefone
        
        if preco_medio is not None:
            if preco_medio < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Average price must be non-negative"
                )
            accommodation.preco_medio = Decimal(str(preco_medio))
        
        if link_reserva is not None:
            accommodation.link_reserva = link_reserva
        
        return await self.hospedagem_repo.update(accommodation)
    
    async def delete_accommodation(self, accommodation_id: int) -> None:
        """
        Delete an accommodation.
        
        Args:
            accommodation_id: Accommodation ID.
            
        Raises:
            HTTPException: If accommodation not found.
        """
        accommodation = await self.get_accommodation(accommodation_id)
        await self.hospedagem_repo.delete(accommodation.id)
    
    async def get_statistics(self, ponto_id: int) -> dict:
        """
        Get accommodation statistics for a tourist spot.
        
        Args:
            ponto_id: Tourist spot ID.
            
        Returns:
            Statistics dictionary.
            
        Raises:
            HTTPException: If spot not found.
        """
        spot = await self.spot_repo.get_by_id(ponto_id)
        if not spot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tourist spot with ID {ponto_id} not found"
            )
        
        return await self.hospedagem_repo.get_statistics(ponto_id)
