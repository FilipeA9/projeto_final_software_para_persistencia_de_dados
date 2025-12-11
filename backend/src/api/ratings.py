"""
Ratings API endpoints - Rating management for tourist spots.

Implements GET, POST, PUT endpoints for viewing and managing ratings.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.postgres import get_db
from src.repositories.rating_repository import RatingRepository
from src.repositories.spot_repository import SpotRepository
from src.services.rating_service import RatingService
from src.schemas.spot import (
    RatingResponse,
    RatingDistributionResponse,
    CreateRatingRequest,
    UpdateRatingRequest
)
from src.dependencies.auth import get_current_user
from src.models.usuario import Usuario

router = APIRouter()


@router.get("/spots/{spot_id}/ratings", response_model=list[RatingResponse])
async def get_spot_ratings(
    spot_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all ratings for a tourist spot.
    
    **Returns:**
    - List of ratings ordered by most recent
    - Rating value (1-5 stars)
    - Optional comment/review text
    - User ID and timestamp
    
    **Pagination:**
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Max records to return (1-100, default: 50)
    
    **Response includes:**
    - `nota`: Star rating (1-5)
    - `comentario`: Optional review text
    - `usuario_id`: User who submitted the rating
    - `created_at`: Submission timestamp
    
    **Note:** Returns empty list if spot has no ratings.
    """
    rating_repo = RatingRepository(db)
    ratings = await rating_repo.get_by_spot_id(spot_id, skip=skip, limit=limit)
    return ratings


@router.get("/spots/{spot_id}/ratings/stats", response_model=RatingDistributionResponse)
async def get_spot_rating_stats(
    spot_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get rating statistics and distribution for a tourist spot.
    
    **Returns:**
    - Count of ratings per star level (1-5)
    - Average rating
    - Total rating count
    
    **Response format:**
    ```json
    {
        "1": 5,      // 5 one-star ratings
        "2": 10,     // 10 two-star ratings
        "3": 20,     // 20 three-star ratings
        "4": 35,     // 35 four-star ratings
        "5": 30,     // 30 five-star ratings
        "average": 3.75,
        "total": 100
    }
    ```
    
    **Use case:** Display rating histogram and average score.
    """
    rating_repo = RatingRepository(db)
    
    # Get distribution
    distribution = await rating_repo.get_rating_distribution(spot_id)
    
    # Get average and total
    avg_rating = await rating_repo.get_average_rating(spot_id)
    total = await rating_repo.count_by_spot_id(spot_id)
    
    return {
        "1": distribution[1],
        "2": distribution[2],
        "3": distribution[3],
        "4": distribution[4],
        "5": distribution[5],
        "average": round(avg_rating, 2) if avg_rating else None,
        "total": total,
    }


@router.post("/spots/{spot_id}/ratings", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def create_rating(
    spot_id: int,
    rating_data: CreateRatingRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new rating for a tourist spot.
    
    **Authentication required.**
    
    **Request Body:**
    - `nota`: Rating value (1-5 stars, required)
    - `comentario`: Optional review comment (max 1000 chars)
    
    **Business Rules:**
    - One rating per user per spot (unique constraint)
    - Rating must be between 1 and 5
    - Spot must exist
    
    **Returns:**
    - Created rating with ID and timestamp
    
    **Error Responses:**
    - 401: Unauthorized (no valid JWT token)
    - 404: Tourist spot not found
    - 409: User already rated this spot
    """
    rating_repo = RatingRepository(db)
    spot_repo = SpotRepository(db)
    rating_service = RatingService(rating_repo, spot_repo)
    
    rating = await rating_service.create_rating(
        ponto_id=spot_id,
        usuario_id=current_user.id,
        nota=rating_data.nota,
        comentario=rating_data.comentario
    )
    
    await db.commit()
    
    return rating


@router.put("/ratings/{rating_id}", response_model=RatingResponse)
async def update_rating(
    rating_id: int,
    rating_data: UpdateRatingRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing rating.
    
    **Authentication required.**
    
    **Request Body:**
    - `nota`: New rating value (1-5 stars, optional)
    - `comentario`: New review comment (optional)
    
    **Business Rules:**
    - User can only update their own ratings
    - At least one field must be provided
    - Rating must be between 1 and 5
    
    **Returns:**
    - Updated rating
    
    **Error Responses:**
    - 401: Unauthorized (no valid JWT token)
    - 403: Cannot edit another user's rating
    - 404: Rating not found
    """
    rating_repo = RatingRepository(db)
    spot_repo = SpotRepository(db)
    rating_service = RatingService(rating_repo, spot_repo)
    
    rating = await rating_service.update_rating(
        rating_id=rating_id,
        usuario_id=current_user.id,
        nota=rating_data.nota,
        comentario=rating_data.comentario
    )
    
    await db.commit()
    
    return rating
