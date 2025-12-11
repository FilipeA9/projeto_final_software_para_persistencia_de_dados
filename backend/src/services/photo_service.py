"""
PhotoService - Business logic for photo operations.

Handles photo retrieval and URL generation.
"""

from typing import List, Dict, Any
from src.repositories.photo_repository import PhotoRepository


class PhotoService:
    """Service layer for photo business logic."""
    
    def __init__(self):
        self.photo_repo = PhotoRepository()
    
    async def get_photos_by_spot(self, spot_id: int) -> List[Dict[str, Any]]:
        """
        Get all photos for a tourist spot with formatted URLs.
        
        Args:
            spot_id: Tourist spot ID.
        
        Returns:
            List of photo dictionaries with URLs.
        """
        photos = await self.photo_repo.get_by_spot_id(spot_id)
        
        return [
            {
                "id": str(photo["_id"]),
                "titulo": photo.get("titulo", ""),
                "filename": photo["filename"],
                "url": f"/uploads/{photo['path']}",
                "thumbnail_url": f"/uploads/{photo.get('thumbnailPath', photo['path'])}",
                "uploaded_by": photo["usuarioId"],
                "created_at": photo["createdAt"].isoformat(),
            }
            for photo in photos
        ]
    
    async def get_photo_by_id(self, photo_id: str) -> Dict[str, Any] | None:
        """
        Get photo by ID.
        
        Args:
            photo_id: Photo MongoDB ObjectId.
        
        Returns:
            Photo dictionary or None.
        """
        photo = await self.photo_repo.get_by_id(photo_id)
        if not photo:
            return None
        
        return {
            "id": str(photo["_id"]),
            "ponto_id": photo["pontoId"],
            "titulo": photo.get("titulo", ""),
            "filename": photo["filename"],
            "url": f"/uploads/{photo['path']}",
            "thumbnail_url": f"/uploads/{photo.get('thumbnailPath', photo['path'])}",
            "uploaded_by": photo["usuarioId"],
            "created_at": photo["createdAt"].isoformat(),
        }
