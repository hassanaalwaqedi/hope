"""
Session Domain Model

Represents a therapy session in the HOPE system.
Sessions track the conversation context and state for
a single user interaction period.

PRIVACY: Message content may contain sensitive information
and should be encrypted at rest.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID, uuid4


class SessionState(StrEnum):
    """
    Session lifecycle states.
    
    Tracks the current state of a therapy session
    for proper context management.
    """
    
    CREATED = "created"
    """Session initialized but not started."""
    
    ACTIVE = "active"
    """Session in progress with active interaction."""
    
    PAUSED = "paused"
    """Session temporarily paused (user away)."""
    
    COMPLETED = "completed"
    """Session ended normally."""
    
    ESCALATED = "escalated"
    """
    Session escalated to crisis resources.
    
    SAFETY_NOTE: This state indicates the user was
    referred to emergency/professional resources.
    """
    
    ABANDONED = "abandoned"
    """Session timed out without completion."""


@dataclass
class SessionMessage:
    """
    A single message in a session.
    
    Represents either user input or system response.
    
    Attributes:
        id: Unique message identifier
        role: Message author role (user/assistant/system)
        content: Message text content
        timestamp: When message was created
        metadata: Additional message context (e.g., panic scores)
    """
    
    id: UUID = field(default_factory=uuid4)
    role: str = "user"  # user, assistant, system
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Serialize message to dictionary."""
        return {
            "id": str(self.id),
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SessionMessage":
        """Create message from dictionary."""
        return cls(
            id=UUID(data["id"]) if "id" in data else uuid4(),
            role=data.get("role", "user"),
            content=data.get("content", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.utcnow(),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Session:
    """
    Therapy session entity.
    
    Represents a single conversation session between
    a user and the HOPE system. Sessions maintain
    conversation context and state.
    
    Attributes:
        id: Unique session identifier
        user_id: Associated user ID
        state: Current session state
        messages: Conversation history
        created_at: Session start time
        updated_at: Last activity time
        ended_at: Session end time (if completed)
        summary: Session summary (generated after completion)
        escalation_reason: Reason for escalation (if applicable)
        metadata: Additional session context
    """
    
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    state: SessionState = SessionState.CREATED
    messages: list[SessionMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    summary: Optional[str] = None
    escalation_reason: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    
    # Session configuration
    max_messages: int = 100  # Limit for context window management
    
    def add_message(self, role: str, content: str, metadata: Optional[dict] = None) -> SessionMessage:
        """
        Add a message to the session.
        
        Args:
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Optional additional context
            
        Returns:
            The created message
        """
        message = SessionMessage(
            role=role,
            content=content,
            metadata=metadata or {},
        )
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
        
        # Activate session on first user message
        if self.state == SessionState.CREATED and role == "user":
            self.state = SessionState.ACTIVE
        
        return message
    
    def get_recent_messages(self, count: int = 10) -> list[SessionMessage]:
        """
        Get most recent messages for context.
        
        Args:
            count: Number of messages to retrieve
            
        Returns:
            List of recent messages
        """
        return self.messages[-count:] if self.messages else []
    
    def get_conversation_context(self) -> list[dict]:
        """
        Get messages formatted for LLM context.
        
        Returns:
            List of message dicts with role and content
        """
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.get_recent_messages(self.max_messages)
        ]
    
    def complete(self, summary: Optional[str] = None) -> None:
        """
        Mark session as completed.
        
        Args:
            summary: Optional session summary
        """
        self.state = SessionState.COMPLETED
        self.ended_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.summary = summary
    
    def escalate(self, reason: str) -> None:
        """
        Mark session as escalated to crisis resources.
        
        Args:
            reason: Reason for escalation
            
        SAFETY_NOTE: This should trigger notification
        of crisis resources to the user.
        """
        self.state = SessionState.ESCALATED
        self.escalation_reason = reason
        self.updated_at = datetime.utcnow()
    
    def pause(self) -> None:
        """Pause the session."""
        if self.state == SessionState.ACTIVE:
            self.state = SessionState.PAUSED
            self.updated_at = datetime.utcnow()
    
    def resume(self) -> None:
        """Resume a paused session."""
        if self.state == SessionState.PAUSED:
            self.state = SessionState.ACTIVE
            self.updated_at = datetime.utcnow()
    
    @property
    def message_count(self) -> int:
        """Get total message count."""
        return len(self.messages)
    
    @property
    def duration_seconds(self) -> int:
        """Get session duration in seconds."""
        end = self.ended_at or datetime.utcnow()
        return int((end - self.created_at).total_seconds())
    
    def to_dict(self) -> dict:
        """Serialize session to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "state": self.state.value,
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "summary": self.summary,
            "escalation_reason": self.escalation_reason,
            "duration_seconds": self.duration_seconds,
        }
