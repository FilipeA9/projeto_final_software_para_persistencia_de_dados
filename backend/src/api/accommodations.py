"""
Accommodations API endpoints.

Provides REST API for managing accommodations near tourist spots.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.postgres import get_db
from src.dependencies.auth import get_current_user, get_current_admin_user
from src.repositories.hospedagem_repository import HospedagemRepository
from src.repositories.spot_repository import SpotRepository
from src.services.hospedagem_service import HospedagemService
from src.schemas.spot import (
    CreateAccommodationRequest,
    UpdateAccommodationRequest,
    AccommodationResponse,
    AccommodationListResponse,
    AccommodationStatisticsResponse
)
from src.models.usuario import Usuario


router = APIRouter(prefix="/api", tags=["accommodations"])


def get_hospedagem_service(db: AsyncSession = Depends(get_db)) -> HospedagemService:
    """Dependency to get HospedagemService instance."""
    hospedagem_repo = HospedagemRepository(db)
    spot_repo = SpotRepository(db)
    return HospedagemService(hospedagem_repo, spot_repo)


@router.get(
    "/spots/{spot_id}/accommodations",
    response_model=AccommodationListResponse,
    summary="List accommodations for a tourist spot",
    description="Get all accommodations near a specific tourist spot with optional filters."
)
async def get_spot_accommodations(
    spot_id: int,
    tipo: Optional[str] = None,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
    service: HospedagemService = Depends(get_hospedagem_service)
):
    """
    List accommodations for a tourist spot.
    
    Args:
        spot_id: Tourist spot ID.
        tipo: Filter by accommodation type (hotel, pousada, hostel).
        max_price: Maximum average price filter.
        min_price: Minimum average price filter.
        service: Hospedagem service dependency.
        
    Returns:
        AccommodationListResponse with accommodations and total count.
    """
    accommodations = await service.get_accommodations_for_spot(
        ponto_id=spot_id,
        tipo=tipo,
        max_price=max_price,
        min_price=min_price
    )
    
    return AccommodationListResponse(
        accommodations=[
            AccommodationResponse(
                id=acc.id,
                ponto_id=acc.ponto_id,
                nome=acc.nome,
                endereco=acc.endereco,
                telefone=acc.telefone,
                preco_medio=float(acc.preco_medio) if acc.preco_medio else None,
                tipo=acc.tipo.value if hasattr(acc.tipo, 'value') else acc.tipo,
                link_reserva=acc.link_reserva
            )
            for acc in accommodations
        ],
        total=len(accommodations)
    )


@router.get(
    "/spots/{spot_id}/accommodations/statistics",
    response_model=AccommodationStatisticsResponse,
    summary="Get accommodation statistics",
    description="Get accommodation statistics for a tourist spot (count, prices, types)."
)
async def get_spot_accommodation_statistics(
    spot_id: int,
    service: HospedagemService = Depends(get_hospedagem_service)
):
    """
    Get accommodation statistics for a tourist spot.
    
    Args:
        spot_id: Tourist spot ID.
        service: Hospedagem service dependency.
        
    Returns:
        AccommodationStatisticsResponse with statistics.
    """
    stats = await service.get_statistics(spot_id)
    return AccommodationStatisticsResponse(**stats)


@router.get(
    "/accommodations/{accommodation_id}",
    response_model=AccommodationResponse,
    summary="Get accommodation details",
    description="Get detailed information about a specific accommodation."
)
async def get_accommodation(
    accommodation_id: int,
    service: HospedagemService = Depends(get_hospedagem_service)
):
    """
    Get accommodation by ID.
    
    Args:
        accommodation_id: Accommodation ID.
        service: Hospedagem service dependency.
        
    Returns:
        AccommodationResponse with accommodation details.
    """
    accommodation = await service.get_accommodation(accommodation_id)
    
    return AccommodationResponse(
        id=accommodation.id,
        ponto_id=accommodation.ponto_id,
        nome=accommodation.nome,
        endereco=accommodation.endereco,
        telefone=accommodation.telefone,
        preco_medio=float(accommodation.preco_medio) if accommodation.preco_medio else None,
        tipo=accommodation.tipo.value if hasattr(accommodation.tipo, 'value') else accommodation.tipo,
        link_reserva=accommodation.link_reserva
    )


@router.post(
    "/accommodations",
    response_model=AccommodationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create accommodation (Admin only)",
    description="Create a new accommodation near a tourist spot. Requires admin privileges."
)
async def create_accommodation(
    request: CreateAccommodationRequest,
    current_user: Usuario = Depends(get_current_admin_user),
    service: HospedagemService = Depends(get_hospedagem_service)
):
    """
    Create a new accommodation.
    
    Args:
        request: Accommodation creation data.
        current_user: Current authenticated admin user.
        service: Hospedagem service dependency.
        
    Returns:
        AccommodationResponse with created accommodation.
    """
    accommodation = await service.create_accommodation(
        ponto_id=request.ponto_id,
        nome=request.nome,
        endereco=request.endereco,
        tipo=request.tipo,
        telefone=request.telefone,
        preco_medio=request.preco_medio,
        link_reserva=request.link_reserva
    )
    
    return AccommodationResponse(
        id=accommodation.id,
        ponto_id=accommodation.ponto_id,
        nome=accommodation.nome,
        endereco=accommodation.endereco,
        telefone=accommodation.telefone,
        preco_medio=float(accommodation.preco_medio) if accommodation.preco_medio else None,
        tipo=accommodation.tipo.value if hasattr(accommodation.tipo, 'value') else accommodation.tipo,
        link_reserva=accommodation.link_reserva
    )


@router.put(
    "/accommodations/{accommodation_id}",
    response_model=AccommodationResponse,
    summary="Update accommodation (Admin only)",
    description="Update an existing accommodation. Requires admin privileges."
)
async def update_accommodation(
    accommodation_id: int,
    request: UpdateAccommodationRequest,
    current_user: Usuario = Depends(get_current_admin_user),
    service: HospedagemService = Depends(get_hospedagem_service)
):
    """
    Update an accommodation.
    
    Args:
        accommodation_id: Accommodation ID.
        request: Accommodation update data.
        current_user: Current authenticated admin user.
        service: Hospedagem service dependency.
        
    Returns:
        AccommodationResponse with updated accommodation.
    """
    accommodation = await service.update_accommodation(
        accommodation_id=accommodation_id,
        nome=request.nome,
        endereco=request.endereco,
        tipo=request.tipo,
        telefone=request.telefone,
        preco_medio=request.preco_medio,
        link_reserva=request.link_reserva
    )
    
    return AccommodationResponse(
        id=accommodation.id,
        ponto_id=accommodation.ponto_id,
        nome=accommodation.nome,
        endereco=accommodation.endereco,
        telefone=accommodation.telefone,
        preco_medio=float(accommodation.preco_medio) if accommodation.preco_medio else None,
        tipo=accommodation.tipo.value if hasattr(accommodation.tipo, 'value') else accommodation.tipo,
        link_reserva=accommodation.link_reserva
    )


@router.delete(
    "/accommodations/{accommodation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete accommodation (Admin only)",
    description="Delete an accommodation. Requires admin privileges."
)
async def delete_accommodation(
    accommodation_id: int,
    current_user: Usuario = Depends(get_current_admin_user),
    service: HospedagemService = Depends(get_hospedagem_service)
):
    """
    Delete an accommodation.
    
    Args:
        accommodation_id: Accommodation ID.
        current_user: Current authenticated admin user.
        service: Hospedagem service dependency.
        
    Returns:
        No content on success.
    """
    await service.delete_accommodation(accommodation_id)
    return None
