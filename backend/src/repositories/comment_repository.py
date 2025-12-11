"""
CommentRepository - Repository for MongoDB comment operations.

Handles comment storage, retrieval, and basic moderation features.
"""

from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId


class CommentRepository:
    """Repository for comment operations in MongoDB."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize comment repository.
        
        Args:
            db: MongoDB database instance.
        """
        self.db = db
        self.collection = db.comentarios
    
    async def create(self, comment_data: dict) -> dict:
        """
        Create a new comment.
        
        Args:
            comment_data: Comment data dictionary.
        
        Returns:
            Created comment with _id.
        """
        comment_doc = {
            "pontoId": comment_data["pontoId"],
            "usuarioId": comment_data["usuarioId"],
            "texto": comment_data["texto"],
            "createdAt": datetime.utcnow(),
            "metadata": {
                "likes": 0,
                "reports": 0
            },
            "respostas": []
        }
        
        result = await self.collection.insert_one(comment_doc)
        comment_doc["_id"] = str(result.inserted_id)
        
        return comment_doc
    
    async def get_by_id(self, comment_id: str) -> Optional[dict]:
        """
        Get comment by ID.
        
        Args:
            comment_id: MongoDB ObjectId as string.
        
        Returns:
            Comment document or None.
        """
        try:
            doc = await self.collection.find_one({"_id": ObjectId(comment_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception:
            return None
    
    async def get_by_spot_id(
        self,
        ponto_id: int,
        skip: int = 0,
        limit: int = 20,
        ordenacao: str = "recentes"
    ) -> List[dict]:
        """
        Get comments for a specific tourist spot.
        
        Args:
            ponto_id: Tourist spot ID.
            skip: Number of records to skip.
            limit: Maximum number of records.
            ordenacao: Sort order (recentes, antigas, mais_curtidos).
        
        Returns:
            List of comments.
        """
        # Determine sort order
        sort_field = "createdAt"
        sort_direction = -1  # Descending (most recent first)
        
        if ordenacao == "antigas":
            sort_direction = 1  # Ascending (oldest first)
        elif ordenacao == "mais_curtidos":
            sort_field = "metadata.likes"
            sort_direction = -1
        
        cursor = self.collection.find(
            {"pontoId": ponto_id}
        ).sort(sort_field, sort_direction).skip(skip).limit(limit)
        
        comments = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            comments.append(doc)
        
        return comments
    
    async def count_by_spot_id(self, ponto_id: int) -> int:
        """
        Count comments for a tourist spot.
        
        Args:
            ponto_id: Tourist spot ID.
        
        Returns:
            Number of comments.
        """
        return await self.collection.count_documents({"pontoId": ponto_id})
    
    async def update(self, comment_id: str, update_data: dict) -> Optional[dict]:
        """
        Update a comment.
        
        Args:
            comment_id: MongoDB ObjectId as string.
            update_data: Fields to update.
        
        Returns:
            Updated comment or None.
        """
        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(comment_id)},
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                result["_id"] = str(result["_id"])
            return result
        except Exception:
            return None
    
    async def delete(self, comment_id: str) -> bool:
        """
        Delete a comment.
        
        Args:
            comment_id: MongoDB ObjectId as string.
        
        Returns:
            True if deleted, False otherwise.
        """
        try:
            result = await self.collection.delete_one({"_id": ObjectId(comment_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    async def add_like(self, comment_id: str) -> bool:
        """
        Increment likes counter.
        
        Args:
            comment_id: MongoDB ObjectId as string.
        
        Returns:
            True if successful.
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(comment_id)},
                {"$inc": {"metadata.likes": 1}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def add_report(self, comment_id: str) -> bool:
        """
        Increment reports counter.
        
        Args:
            comment_id: MongoDB ObjectId as string.
        
        Returns:
            True if successful.
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(comment_id)},
                {"$inc": {"metadata.reports": 1}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def get_reported_comments(self, threshold: int = 5) -> List[dict]:
        """
        Get comments with high report count (for moderation).
        
        Args:
            threshold: Minimum number of reports.
        
        Returns:
            List of reported comments.
        """
        cursor = self.collection.find(
            {"metadata.reports": {"$gte": threshold}}
        ).sort("metadata.reports", -1)
        
        comments = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            comments.append(doc)
        
        return comments
