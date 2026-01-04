"""
Base Repository Pattern

Provides generic async CRUD operations for all repositories.
Implements the Repository pattern for clean separation between
domain logic and data access.
"""

from typing import Any, Generic, Optional, Sequence, Type, TypeVar
from uuid import UUID

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from hope.infrastructure.database.connection import Base

# Type variable for model types
ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    Generic base repository with async CRUD operations.
    
    Provides common database operations for all entity types.
    Subclass and specify the model type for entity-specific repositories.
    
    Usage:
        class UserRepository(BaseRepository[UserModel]):
            pass
            
        repo = UserRepository(UserModel, session)
        user = await repo.get_by_id(user_id)
    """
    
    def __init__(self, model: Type[ModelT], session: AsyncSession) -> None:
        """
        Initialize repository with model class and session.
        
        Args:
            model: SQLAlchemy model class
            session: Async database session
        """
        self._model = model
        self._session = session
    
    async def get_by_id(self, id: UUID) -> Optional[ModelT]:
        """
        Get entity by primary key ID.
        
        Args:
            id: Entity UUID
            
        Returns:
            Entity if found, None otherwise
        """
        result = await self._session.execute(
            select(self._model).where(self._model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
    ) -> Sequence[ModelT]:
        """
        Get all entities with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            order_by: Optional column name to order by
            
        Returns:
            List of entities
        """
        query = select(self._model).offset(skip).limit(limit)
        
        if order_by and hasattr(self._model, order_by):
            query = query.order_by(getattr(self._model, order_by))
        
        result = await self._session.execute(query)
        return result.scalars().all()
    
    async def create(self, entity: ModelT) -> ModelT:
        """
        Create a new entity.
        
        Args:
            entity: Entity instance to create
            
        Returns:
            Created entity with ID
        """
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
    
    async def update(self, entity: ModelT) -> ModelT:
        """
        Update an existing entity.
        
        Args:
            entity: Entity instance with updates
            
        Returns:
            Updated entity
        """
        await self._session.merge(entity)
        await self._session.flush()
        return entity
    
    async def delete(self, id: UUID) -> bool:
        """
        Delete entity by ID.
        
        Args:
            id: Entity UUID
            
        Returns:
            True if deleted, False if not found
        """
        result = await self._session.execute(
            delete(self._model).where(self._model.id == id)
        )
        return result.rowcount > 0
    
    async def count(self) -> int:
        """
        Count all entities.
        
        Returns:
            Total entity count
        """
        result = await self._session.execute(
            select(func.count()).select_from(self._model)
        )
        return result.scalar_one()
    
    async def exists(self, id: UUID) -> bool:
        """
        Check if entity exists by ID.
        
        Args:
            id: Entity UUID
            
        Returns:
            True if exists
        """
        result = await self._session.execute(
            select(func.count()).where(self._model.id == id)
        )
        return result.scalar_one() > 0
    
    async def bulk_create(self, entities: Sequence[ModelT]) -> Sequence[ModelT]:
        """
        Create multiple entities in batch.
        
        Args:
            entities: List of entities to create
            
        Returns:
            Created entities with IDs
        """
        self._session.add_all(entities)
        await self._session.flush()
        for entity in entities:
            await self._session.refresh(entity)
        return entities
