"""
Base repository pattern interface.

Provides abstract base class for repository implementations with common CRUD operations.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession

# Generic type for model
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Abstract base repository for database operations.
    
    Provides common CRUD operations that can be implemented by specific repositories.
    Uses Repository pattern to abstract database access from business logic.
    """
    
    def __init__(self, model: type[ModelType], db: AsyncSession):
        """
        Initialize repository with model and database session.
        
        Args:
            model: SQLAlchemy model class.
            db: Async database session.
        """
        self.model = model
        self.db = db
    
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get all entities with pagination."""
        pass
    
    @abstractmethod
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create new entity."""
        pass
    
    @abstractmethod
    async def update(
        self, id: int, obj_in: UpdateSchemaType
    ) -> Optional[ModelType]:
        """Update existing entity."""
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        pass
    
    async def commit(self) -> None:
        """Commit current transaction."""
        await self.db.commit()
    
    async def refresh(self, instance: ModelType) -> None:
        """Refresh entity instance from database."""
        await self.db.refresh(instance)
