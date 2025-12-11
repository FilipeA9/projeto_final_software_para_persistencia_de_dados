"""
Comments API endpoints - Comment management for tourist spots.

Implements GET, POST endpoints for viewing and creating comments (MongoDB).
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.mongodb import get_mongodb
from src.config.postgres import get_db
from src.repositories.comment_repository import CommentRepository
from src.repositories.spot_repository import SpotRepository
from src.services.comment_service import CommentService
from src.schemas.spot import CommentResponse, CreateCommentRequest, CommentListResponse
from src.dependencies.auth import get_current_user
from src.models.usuario import Usuario

router = APIRouter()


@router.get("/spots/{spot_id}/comments", response_model=CommentListResponse)
async def get_spot_comments(
    spot_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    ordenacao: str = Query("recentes", regex="^(recentes|antigas|mais_curtidos)$", description="Sort order"),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    """
    Get comments for a tourist spot.
    
    **Public endpoint** - No authentication required.
    
    **Query Parameters:**
    - `page`: Page number (starts at 1, default: 1)
    - `per_page`: Items per page (1-100, default: 20)
    - `ordenacao`: Sort order
      - `recentes`: Most recent first (default)
      - `antigas`: Oldest first
      - `mais_curtidos`: Most liked first
    
    **Returns:**
    - List of comments with pagination metadata
    - Each comment includes user login, text, likes, creation date
    
    **Response format:**
    ```json
    {
        "comments": [...],
        "pagination": {
            "page": 1,
            "perPage": 20,
            "total": 45
        }
    }
    ```
    """
    comment_repo = CommentRepository(mongo_db)
    
    # Note: We don't validate spot existence for GET (allows viewing comments even if spot is soft-deleted)
    result = await comment_repo.get_by_spot_id(
        ponto_id=spot_id,
        skip=(page - 1) * per_page,
        limit=per_page,
        ordenacao=ordenacao
    )
    
    total = await comment_repo.count_by_spot_id(spot_id)
    
    return {
        "comments": result,
        "pagination": {
            "page": page,
            "perPage": per_page,
            "total": total
        }
    }


@router.post("/spots/{spot_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    spot_id: int,
    comment_data: CreateCommentRequest,
    current_user: Usuario = Depends(get_current_user),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongodb),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new comment for a tourist spot.
    
    **Authentication required.**
    
    **Request Body:**
    - `texto`: Comment text (1-2000 characters, required)
    
    **Business Rules:**
    - Text cannot be empty or only whitespace
    - Maximum 2000 characters
    - Basic profanity filter applied
    - Spot must exist
    
    **Returns:**
    - Created comment with MongoDB _id
    - Includes metadata (likes: 0, reports: 0)
    
    **Error Responses:**
    - 400: Validation error or inappropriate content
    - 401: Unauthorized (no valid JWT token)
    - 404: Tourist spot not found
    """
    comment_repo = CommentRepository(mongo_db)
    spot_repo = SpotRepository(db)
    comment_service = CommentService(comment_repo, spot_repo)
    
    comment = await comment_service.create_comment(
        ponto_id=spot_id,
        usuario_id=current_user.id,
        texto=comment_data.texto
    )
    
    return comment


@router.post("/comments/{comment_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def like_comment(
    comment_id: str,
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    """
    Increment likes counter for a comment.
    
    **Public endpoint** - No authentication required (simple like system).
    
    **Note:** This is a simplified like system without user tracking.
    For production, consider implementing user-specific likes tracking.
    
    **Returns:**
    - 204 No Content on success
    
    **Error Responses:**
    - 404: Comment not found
    """
    comment_repo = CommentRepository(mongo_db)
    
    # Check if comment exists
    comment = await comment_repo.get_by_id(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not Found", "message": "Comment not found", "code": "COMMENT_002"}
        )
    
    await comment_repo.add_like(comment_id)
    
    return None


@router.post("/comments/{comment_id}/report", status_code=status.HTTP_204_NO_CONTENT)
async def report_comment(
    comment_id: str,
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    """
    Report a comment for moderation.
    
    **Public endpoint** - No authentication required.
    
    **Business Logic:**
    - Increments report counter
    - Comments with high report count can be reviewed by admins
    
    **Returns:**
    - 204 No Content on success
    
    **Error Responses:**
    - 404: Comment not found
    """
    comment_repo = CommentRepository(mongo_db)
    
    # Check if comment exists
    comment = await comment_repo.get_by_id(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not Found", "message": "Comment not found", "code": "COMMENT_002"}
        )
    
    await comment_repo.add_report(comment_id)
    
    return None
