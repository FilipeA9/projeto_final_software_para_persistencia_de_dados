"""
CommentService - Business logic for comment operations.

Handles comment creation, moderation, and validation.
"""

from typing import List, Optional, Dict
from fastapi import HTTPException, status

from src.repositories.comment_repository import CommentRepository
from src.repositories.spot_repository import SpotRepository


class CommentService:
    """Service for comment business logic."""
    
    def __init__(self, comment_repo: CommentRepository, spot_repo: SpotRepository):
        """
        Initialize comment service.
        
        Args:
            comment_repo: Comment repository instance.
            spot_repo: Spot repository instance (for validation).
        """
        self.comment_repo = comment_repo
        self.spot_repo = spot_repo
    
    async def create_comment(
        self, ponto_id: int, usuario_id: int, texto: str
    ) -> dict:
        """
        Create a new comment for a tourist spot.
        
        Args:
            ponto_id: Tourist spot ID.
            usuario_id: User ID.
            texto: Comment text.
        
        Returns:
            Created comment.
        
        Raises:
            HTTPException: If spot doesn't exist or validation fails.
        """
        # Validate spot exists
        spot = await self.spot_repo.get_by_id(ponto_id)
        if not spot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Not Found", "message": "Tourist spot not found", "code": "SPOT_001"}
            )
        
        # Validate comment text
        if not texto or len(texto.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Validation error",
                    "message": "Comment text is required",
                    "code": "VAL_005"
                }
            )
        
        if len(texto) > 2000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Validation error",
                    "message": "Comment text cannot exceed 2000 characters",
                    "code": "VAL_004"
                }
            )
        
        # Apply content moderation (basic profanity filter)
        if self._contains_inappropriate_content(texto):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Moderation error",
                    "message": "Comment contains inappropriate content",
                    "code": "COMMENT_001"
                }
            )
        
        # Create comment
        comment_data = {
            "pontoId": ponto_id,
            "usuarioId": usuario_id,
            "texto": texto.strip()
        }
        
        comment = await self.comment_repo.create(comment_data)
        
        return comment
    
    async def get_comments_for_spot(
        self,
        ponto_id: int,
        page: int = 1,
        per_page: int = 20,
        ordenacao: str = "recentes"
    ) -> Dict:
        """
        Get comments for a tourist spot with pagination.
        
        Args:
            ponto_id: Tourist spot ID.
            page: Page number (starts at 1).
            per_page: Items per page.
            ordenacao: Sort order (recentes, antigas, mais_curtidos).
        
        Returns:
            Dictionary with comments and pagination info.
        """
        # Validate pagination
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        # Calculate skip
        skip = (page - 1) * per_page
        
        # Get comments
        comments = await self.comment_repo.get_by_spot_id(
            ponto_id, skip=skip, limit=per_page, ordenacao=ordenacao
        )
        
        # Get total count
        total = await self.comment_repo.count_by_spot_id(ponto_id)
        
        return {
            "comments": comments,
            "pagination": {
                "page": page,
                "perPage": per_page,
                "total": total
            }
        }
    
    async def update_comment(
        self, comment_id: str, usuario_id: int, texto: str
    ) -> dict:
        """
        Update an existing comment.
        
        Args:
            comment_id: Comment ID.
            usuario_id: User ID (for ownership validation).
            texto: New comment text.
        
        Returns:
            Updated comment.
        
        Raises:
            HTTPException: If comment doesn't exist or user doesn't own it.
        """
        # Get existing comment
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Not Found", "message": "Comment not found", "code": "COMMENT_002"}
            )
        
        # Verify ownership
        if comment["usuarioId"] != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Forbidden",
                    "message": "You can only edit your own comments",
                    "code": "COMMENT_003"
                }
            )
        
        # Validate new text
        if not texto or len(texto.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Validation error",
                    "message": "Comment text is required",
                    "code": "VAL_005"
                }
            )
        
        if len(texto) > 2000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Validation error",
                    "message": "Comment text cannot exceed 2000 characters",
                    "code": "VAL_004"
                }
            )
        
        # Apply content moderation
        if self._contains_inappropriate_content(texto):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Moderation error",
                    "message": "Comment contains inappropriate content",
                    "code": "COMMENT_001"
                }
            )
        
        # Update comment
        updated_comment = await self.comment_repo.update(
            comment_id, {"texto": texto.strip()}
        )
        
        return updated_comment
    
    async def delete_comment(
        self, comment_id: str, usuario_id: int, is_admin: bool = False
    ) -> bool:
        """
        Delete a comment.
        
        Args:
            comment_id: Comment ID.
            usuario_id: User ID (for ownership validation).
            is_admin: Whether user has admin privileges.
        
        Returns:
            True if deleted successfully.
        
        Raises:
            HTTPException: If comment doesn't exist or user doesn't own it.
        """
        # Get existing comment
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Not Found", "message": "Comment not found", "code": "COMMENT_002"}
            )
        
        # Verify ownership (admins can delete any comment)
        if not is_admin and comment["usuarioId"] != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Forbidden",
                    "message": "You can only delete your own comments",
                    "code": "COMMENT_004"
                }
            )
        
        # Delete comment
        success = await self.comment_repo.delete(comment_id)
        
        return success
    
    async def like_comment(self, comment_id: str) -> bool:
        """
        Increment likes counter for a comment.
        
        Args:
            comment_id: Comment ID.
        
        Returns:
            True if successful.
        
        Raises:
            HTTPException: If comment doesn't exist.
        """
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Not Found", "message": "Comment not found", "code": "COMMENT_002"}
            )
        
        return await self.comment_repo.add_like(comment_id)
    
    async def report_comment(self, comment_id: str) -> bool:
        """
        Report a comment for moderation.
        
        Args:
            comment_id: Comment ID.
        
        Returns:
            True if successful.
        
        Raises:
            HTTPException: If comment doesn't exist.
        """
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Not Found", "message": "Comment not found", "code": "COMMENT_002"}
            )
        
        return await self.comment_repo.add_report(comment_id)
    
    async def get_reported_comments(self, threshold: int = 5) -> List[dict]:
        """
        Get comments with high report count (for admin moderation).
        
        Args:
            threshold: Minimum number of reports.
        
        Returns:
            List of reported comments.
        """
        return await self.comment_repo.get_reported_comments(threshold)
    
    def _contains_inappropriate_content(self, text: str) -> bool:
        """
        Basic profanity filter for content moderation.
        
        Args:
            text: Text to check.
        
        Returns:
            True if text contains inappropriate content.
        """
        # Basic profanity list (extend as needed)
        profanity_list = [
            "spam", "scam", "viagra", "casino"
        ]
        
        text_lower = text.lower()
        for word in profanity_list:
            if word in text_lower:
                return True
        
        return False
