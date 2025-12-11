"""
PhotoRepository - Repository for MongoDB photo metadata operations.

Handles photo document storage and retrieval from MongoDB.
"""

from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from src.config.mongodb import get_mongo_db


class PhotoRepository:
    """Repository for photo metadata operations (MongoDB)."""
    
    def __init__(self):
        self.db = get_mongo_db()
        self.collection = self.db.fotos
    
    async def get_by_id(self, photo_id: str) -> Optional[dict]:
        """
        Get photo by MongoDB ObjectId.
        
        Args:
            photo_id: Photo ObjectId as string.
        
        Returns:
            Photo document or None.
        """
        try:
            return await self.collection.find_one({"_id": ObjectId(photo_id)})
        except Exception:
            return None
    
    async def get_by_spot_id(self, ponto_id: int) -> List[dict]:
        """
        Get all photos for a tourist spot.
        
        Args:
            ponto_id: Tourist spot ID.
        
        Returns:
            List of photo documents.
        """
        cursor = self.collection.find({"pontoId": ponto_id}).sort("createdAt", -1)
        return await cursor.to_list(length=None)
    
    async def count_by_spot_id(self, ponto_id: int) -> int:
        """
        Count photos for a tourist spot.
        
        Args:
            ponto_id: Tourist spot ID.
        
        Returns:
            Number of photos.
        """
        return await self.collection.count_documents({"pontoId": ponto_id})
    
    async def create(self, photo_data: dict) -> dict:
        """
        Create new photo document.
        
        Args:
            photo_data: Photo metadata (pontoId, usuarioId, filename, path, etc).
        
        Returns:
            Created photo document with _id.
        """
        photo_data["createdAt"] = datetime.utcnow()
        result = await self.collection.insert_one(photo_data)
        photo_data["_id"] = result.inserted_id
        return photo_data
    
    async def delete(self, photo_id: str) -> bool:
        """
        Delete photo document by ID.
        
        Args:
            photo_id: Photo ObjectId as string.
        
        Returns:
            True if deleted, False otherwise.
        """
        try:
            result = await self.collection.delete_one({"_id": ObjectId(photo_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    async def delete_by_spot_id(self, ponto_id: int) -> int:
        """
        Delete all photos for a tourist spot.
        
        Args:
            ponto_id: Tourist spot ID.
        
        Returns:
            Number of photos deleted.
        """
        result = await self.collection.delete_many({"pontoId": ponto_id})
        return result.deleted_count
    
    async def get_by_user_id(self, usuario_id: int, skip: int = 0, limit: int = 50) -> List[dict]:
        """
        Get photos uploaded by a user.
        
        Args:
            usuario_id: User ID.
            skip: Number of records to skip.
            limit: Maximum number of records.
        
        Returns:
            List of photo documents.
        """
        cursor = (
            self.collection.find({"usuarioId": usuario_id})
            .sort("createdAt", -1)
            .skip(skip)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)
