"""
User Repository

Data access layer for user entities with specialized queries.
"""

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from hope.infrastructure.database.models.user_model import UserModel
from hope.infrastructure.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    """
    Repository for user data access.
    
    Provides user-specific queries beyond basic CRUD.
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize with user model."""
        super().__init__(UserModel, session)
    
    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """
        Get user by email address.
        
        Args:
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        result = await self._session.execute(
            select(UserModel).where(
                UserModel.email == email,
                UserModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()
    
    async def get_active_users(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[UserModel]:
        """
        Get all active (non-deleted, non-deactivated) users.
        
        Args:
            skip: Pagination offset
            limit: Maximum results
            
        Returns:
            List of active users
        """
        result = await self._session.execute(
            select(UserModel)
            .where(
                UserModel.is_active.is_(True),
                UserModel.deleted_at.is_(None),
            )
            .offset(skip)
            .limit(limit)
            .order_by(UserModel.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_users_needing_consent(
        self,
        required_version: str,
    ) -> Sequence[UserModel]:
        """
        Get users who haven't accepted the required consent version.
        
        Args:
            required_version: Required consent version string
            
        Returns:
            Users needing consent update
        """
        result = await self._session.execute(
            select(UserModel)
            .where(
                UserModel.is_active.is_(True),
                UserModel.deleted_at.is_(None),
                or_(
                    UserModel.consent_version.is_(None),
                    UserModel.consent_version < required_version,
                ),
            )
        )
        return result.scalars().all()
    
    async def soft_delete(self, user_id: UUID) -> bool:
        """
        Soft delete a user (set deleted_at timestamp).
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if user was soft deleted
        """
        from datetime import datetime
        
        user = await self.get_by_id(user_id)
        if user and user.deleted_at is None:
            user.deleted_at = datetime.utcnow()
            user.is_active = False
            await self._session.flush()
            return True
        return False
    
    async def search_users(
        self,
        query: str,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> Sequence[UserModel]:
        """
        Search users by email (partial match).
        
        Args:
            query: Search query string
            skip: Pagination offset
            limit: Maximum results
            
        Returns:
            Matching users
        """
        result = await self._session.execute(
            select(UserModel)
            .where(
                UserModel.email.ilike(f"%{query}%"),
                UserModel.deleted_at.is_(None),
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
