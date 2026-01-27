"""
Session Repository

Async database operations for therapy sessions.
Full CRUD with message history persistence.
"""

from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from hope.infrastructure.database.models.session_model import SessionModel
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


class SessionRepository:
    """
    Repository for session persistence.
    
    Provides async CRUD operations for SessionModel.
    All sessions are persisted in PostgreSQL.
    
    Usage:
        repo = SessionRepository(session)
        session = await repo.create(user_id=user_id)
        await repo.add_message(session_id, message)
    """
    
    def __init__(self, db_session: AsyncSession) -> None:
        """
        Initialize repository with database session.
        
        Args:
            db_session: SQLAlchemy async session
        """
        self._session = db_session
    
    async def create(
        self,
        user_id: UUID,
        state: str = "created",
        metadata: Optional[dict] = None,
    ) -> SessionModel:
        """
        Create a new therapy session.
        
        Args:
            user_id: User's UUID
            state: Initial session state
            metadata: Optional session metadata
            
        Returns:
            Created SessionModel
        """
        session = SessionModel(
            user_id=user_id,
            state=state,
            messages=[],
            session_metadata=metadata or {},
        )
        
        self._session.add(session)
        await self._session.flush()
        await self._session.refresh(session)
        
        logger.info(
            "Session created",
            session_id=str(session.id),
            user_id=str(user_id),
        )
        
        return session
    
    async def get_by_id(self, session_id: UUID) -> Optional[SessionModel]:
        """
        Get session by ID.
        
        Args:
            session_id: Session UUID
            
        Returns:
            SessionModel if found, None otherwise
        """
        result = await self._session.execute(
            select(SessionModel).where(SessionModel.id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_sessions(
        self,
        user_id: UUID,
        limit: int = 50,
        include_completed: bool = True,
    ) -> List[SessionModel]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: User's UUID
            limit: Maximum sessions to return
            include_completed: Include completed/abandoned sessions
            
        Returns:
            List of SessionModel
        """
        query = select(SessionModel).where(SessionModel.user_id == user_id)
        
        if not include_completed:
            query = query.where(
                ~SessionModel.state.in_(["completed", "abandoned"])
            )
        
        query = query.order_by(SessionModel.created_at.desc()).limit(limit)
        
        result = await self._session.execute(query)
        return list(result.scalars().all())
    
    async def update_state(
        self,
        session_id: UUID,
        state: str,
        ended_at: Optional[datetime] = None,
    ) -> bool:
        """
        Update session state.
        
        Args:
            session_id: Session UUID
            state: New state
            ended_at: Optional end timestamp
            
        Returns:
            True if updated, False if not found
        """
        update_data = {"state": state}
        if ended_at:
            update_data["ended_at"] = ended_at
        
        result = await self._session.execute(
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(**update_data)
        )
        
        if result.rowcount > 0:
            logger.info(
                "Session state updated",
                session_id=str(session_id),
                state=state,
            )
            return True
        return False
    
    async def add_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Add a message to session history.
        
        Args:
            session_id: Session UUID
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            True if added, False if session not found
        """
        session = await self.get_by_id(session_id)
        if not session:
            return False
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        
        # Append to messages array
        messages = list(session.messages) if session.messages else []
        messages.append(message)
        
        await self._session.execute(
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(messages=messages, state="active")
        )
        
        return True
    
    async def get_messages(
        self,
        session_id: UUID,
        limit: Optional[int] = None,
    ) -> List[dict]:
        """
        Get messages from a session.
        
        Args:
            session_id: Session UUID
            limit: Optional max messages (from most recent)
            
        Returns:
            List of message dicts
        """
        session = await self.get_by_id(session_id)
        if not session or not session.messages:
            return []
        
        messages = list(session.messages)
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    async def complete_session(
        self,
        session_id: UUID,
        summary: Optional[str] = None,
    ) -> bool:
        """
        Mark session as completed.
        
        Args:
            session_id: Session UUID
            summary: Optional session summary
            
        Returns:
            True if completed, False if not found
        """
        update_data = {
            "state": "completed",
            "ended_at": datetime.now(timezone.utc),
        }
        if summary:
            update_data["summary"] = summary
        
        result = await self._session.execute(
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(**update_data)
        )
        
        if result.rowcount > 0:
            logger.info("Session completed", session_id=str(session_id))
            return True
        return False
    
    async def set_escalation(
        self,
        session_id: UUID,
        reason: str,
    ) -> bool:
        """
        Mark session as escalated.
        
        Args:
            session_id: Session UUID
            reason: Escalation reason
            
        Returns:
            True if escalated, False if not found
        """
        result = await self._session.execute(
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(
                state="escalated",
                escalation_reason=reason,
            )
        )
        
        if result.rowcount > 0:
            logger.warning(
                "Session escalated",
                session_id=str(session_id),
                reason=reason,
            )
            return True
        return False
    
    async def get_active_session(self, user_id: UUID) -> Optional[SessionModel]:
        """
        Get user's most recent active session.
        
        Args:
            user_id: User's UUID
            
        Returns:
            Active SessionModel if exists
        """
        result = await self._session.execute(
            select(SessionModel)
            .where(
                and_(
                    SessionModel.user_id == user_id,
                    SessionModel.state.in_(["created", "active", "paused"]),
                )
            )
            .order_by(SessionModel.updated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
