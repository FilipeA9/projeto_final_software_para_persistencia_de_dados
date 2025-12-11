"""
Spots API endpoints - Tourist spot discovery and management.

Implements GET, POST, PUT, DELETE endpoints for tourist spots.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.postgres import get_db
from src.services.spot_service import SpotService
from src.schemas.spot import SpotListResponse, SpotDetail, CreateSpotRequest, UpdateSpotRequest
from src.dependencies.auth import get_current_admin_user
from src.models.usuario import Usuario

router = APIRouter()


@router.get("/spots", response_model=SpotListResponse)
async def list_spots(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    cidade: Optional[str] = Query(None, description="Filter by city name"),
    estado: Optional[str] = Query(None, description="Filter by state name"),
    pais: Optional[str] = Query(None, description="Filter by country name"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    db: AsyncSession = Depends(get_db),
):
    """
    List tourist spots with filters and pagination.
    
    **Filters:**
    - `cidade`: Filter by city name (case-insensitive partial match)
    - `estado`: Filter by state name (case-insensitive partial match)
    - `pais`: Filter by country name (case-insensitive partial match)
    - `search`: Search in spot name and description
    
    **Pagination:**
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Max records to return (1-100, default: 20)
    
    **Response includes:**
    - List of spots with summary data
    - Total count matching filters
    - Pagination info (has_more flag)
    - Average rating and rating count per spot
    
    **Caching:** Results are cached for 60 seconds in Redis.
    """
    service = SpotService(db)
    result = await service.list_spots(
        skip=skip,
        limit=limit,
        cidade=cidade,
        estado=estado,
        pais=pais,
        search=search,
    )
    return result


@router.get("/spots/{spot_id}", response_model=SpotDetail)
async def get_spot(
    spot_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a tourist spot.
    
    **Returns:**
    - Full spot details (name, description, location)
    - Geographic coordinates (latitude, longitude)
    - Average rating and total rating count
    - Total photo count
    - Creation metadata
    
    **Caching:** Result is cached for 300 seconds (5 minutes) in Redis.
    
    **Errors:**
    - 404: Spot not found or has been deleted
    """
    service = SpotService(db)
    spot = await service.get_spot_by_id(spot_id)
    
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tourist spot with ID {spot_id} not found",
        )
    
    return spot


@router.post("/spots", response_model=SpotDetail, status_code=status.HTTP_201_CREATED)
async def create_spot(
    spot_data: CreateSpotRequest,
    admin: Usuario = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new tourist spot (Admin only).
    
    **Authentication required:** Admin role.
    
    **Request Body:**
    - `nome`: Spot name (required, 1-255 chars)
    - `descricao`: Description (required)
    - `cidade`: City name (required, 1-100 chars)
    - `estado`: State name (required, 1-100 chars)
    - `pais`: Country name (required, 1-100 chars)
    - `latitude`: Latitude (-90 to 90, required)
    - `longitude`: Longitude (-180 to 180, required)
    - `endereco`: Full address (required)
    
    **Returns:**
    - Created spot with full details and ID
    
    **Error Responses:**
    - 401: Unauthorized (no valid JWT token)
    - 403: Forbidden (non-admin user)
    - 400: Invalid input data
    """
    from src.repositories.spot_repository import SpotRepository
    spot_repo = SpotRepository(db)
    
    # Create spot
    spot_dict = spot_data.model_dump()
    spot_dict["criado_por"] = admin.id
    
    spot = await spot_repo.create(spot_dict)
    await db.commit()
    await db.refresh(spot)
    
    # Format response
    return {
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
        "avg_rating": None,
        "rating_count": 0,
        "photo_count": 0,
    }


@router.put("/spots/{spot_id}", response_model=SpotDetail)
async def update_spot(
    spot_id: int,
    spot_data: UpdateSpotRequest,
    admin: Usuario = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing tourist spot (Admin only).
    
    **Authentication required:** Admin role.
    
    **Request Body:** (all fields optional)
    - `nome`: New spot name (1-255 chars)
    - `descricao`: New description
    - `cidade`: New city name (1-100 chars)
    - `estado`: New state name (1-100 chars)
    - `pais`: New country name (1-100 chars)
    - `latitude`: New latitude (-90 to 90)
    - `longitude`: New longitude (-180 to 180)
    - `endereco`: New full address
    
    **Returns:**
    - Updated spot with full details
    
    **Error Responses:**
    - 401: Unauthorized (no valid JWT token)
    - 403: Forbidden (non-admin user)
    - 404: Spot not found
    - 400: Invalid input data
    """
    from src.repositories.spot_repository import SpotRepository
    spot_repo = SpotRepository(db)
    
    # Check if spot exists
    spot = await spot_repo.get_by_id(spot_id)
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tourist spot with ID {spot_id} not found",
        )
    
    # Update spot (only provided fields)
    update_data = spot_data.model_dump(exclude_unset=True)
    if not update_data:
        # No fields to update
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )
    
    updated_spot = await spot_repo.update(spot_id, update_data)
    await db.commit()
    await db.refresh(updated_spot)
    
    # Get rating stats
    from src.repositories.rating_repository import RatingRepository
    rating_repo = RatingRepository(db)
    avg_rating = await rating_repo.get_average_rating(spot_id)
    rating_count = await rating_repo.count_by_spot_id(spot_id)
    
    # Get photo count (from MongoDB - simplified for now)
    photo_count = 0  # TODO: Query MongoDB
    
    return {
        "id": updated_spot.id,
        "nome": updated_spot.nome,
        "descricao": updated_spot.descricao,
        "cidade": updated_spot.cidade,
        "estado": updated_spot.estado,
        "pais": updated_spot.pais,
        "latitude": float(updated_spot.latitude),
        "longitude": float(updated_spot.longitude),
        "endereco": updated_spot.endereco,
        "criado_por": updated_spot.criado_por,
        "created_at": updated_spot.created_at.isoformat(),
        "avg_rating": round(avg_rating, 2) if avg_rating else None,
        "rating_count": rating_count,
        "photo_count": photo_count,
    }


@router.delete("/spots/{spot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_spot(
    spot_id: int,
    admin: Usuario = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a tourist spot (Admin only - soft delete).
    
    **Authentication required:** Admin role.
    
    **Note:** This performs a soft delete (sets deleted_at timestamp).
    The spot will no longer appear in public listings but data is preserved.
    
    **Returns:**
    - 204 No Content on success
    
    **Error Responses:**
    - 401: Unauthorized (no valid JWT token)
    - 403: Forbidden (non-admin user)
    - 404: Spot not found
    """
    from src.repositories.spot_repository import SpotRepository
    spot_repo = SpotRepository(db)
    
    # Check if spot exists
    spot = await spot_repo.get_by_id(spot_id)
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tourist spot with ID {spot_id} not found",
        )
    
    # Soft delete
    await spot_repo.delete(spot_id)
    await db.commit()
    
    return None
