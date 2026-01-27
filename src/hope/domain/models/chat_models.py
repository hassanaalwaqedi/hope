"""
Chat Domain Models

Defines data structures for chat sessions, messages, and responses.
Used throughout the chat service layer.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class MessageRole(Enum):
    """Role of a message in a chat conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatLanguage(Enum):
    """Supported chat languages."""
    ENGLISH = "en"
    FRENCH = "fr"
    SPANISH = "es"
    ARABIC = "ar"
    TURKISH = "tr"
    GERMAN = "de"
    ITALIAN = "it"
    SWEDISH = "sv"
    KOREAN = "ko"
    JAPANESE = "ja"


@dataclass
class ChatMessage:
    """
    A single message in a chat conversation.
    
    Attributes:
        id: Unique message identifier
        session_id: Parent session ID
        role: Who sent the message (user/assistant)
        content: Text content of the message
        image_data: Optional base64 image data
        timestamp: When the message was sent
        safety_flags: Safety flags detected in message
        detected_language: Language detected for this message (e.g. 'fr')
    """
    id: UUID = field(default_factory=uuid4)
    session_id: UUID = field(default_factory=uuid4)
    role: MessageRole = MessageRole.USER
    content: str = ""
    image_data: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    safety_flags: list[str] = field(default_factory=list)
    detected_language: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "role": self.role.value,
            "content": self.content,
            "has_image": self.image_data is not None,
            "timestamp": self.timestamp.isoformat(),
            "safety_flags": self.safety_flags,
            "detected_language": self.detected_language,
        }


@dataclass
class ChatSession:
    """
    A chat session containing multiple messages.
    
    Attributes:
        id: Unique session identifier
        user_id: Optional user identifier (for anonymous users, may be None)
        language: Preferred language for responses
        created_at: When the session started
        updated_at: Last activity timestamp
        messages: List of messages in the session
        is_crisis_mode: Whether crisis mode was triggered
    """
    id: UUID = field(default_factory=uuid4)
    user_id: Optional[str] = None
    language: ChatLanguage = ChatLanguage.ENGLISH
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    messages: list[ChatMessage] = field(default_factory=list)
    is_crisis_mode: bool = False
    
    def add_message(self, message: ChatMessage) -> None:
        """Add a message to the session."""
        message.session_id = self.id
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "language": self.language.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "message_count": len(self.messages),
            "is_crisis_mode": self.is_crisis_mode,
        }
    
    def get_history_summary(self, max_messages: int = 5) -> str:
        """Get recent message history as context string."""
        recent = self.messages[-max_messages:] if self.messages else []
        lines = []
        for msg in recent:
            role = "User" if msg.role == MessageRole.USER else "HOPE"
            lines.append(f"{role}: {msg.content[:200]}")
        return "\n".join(lines)


@dataclass
class ChatResponse:
    """
    Response from the AI chat service.
    
    Attributes:
        text_answer: The AI-generated response text
        safety_flags: Safety concerns detected
        confidence_score: Confidence in the response (0.0-1.0)
        escalated: Whether crisis escalation was triggered
        session_id: The session this response belongs to
        message_id: ID of the response message
        latency_ms: Response generation time
        ai_called: Flag proving AI was actually called
    """
    text_answer: str
    safety_flags: list[str] = field(default_factory=list)
    confidence_score: float = 0.85
    escalated: bool = False
    session_id: Optional[UUID] = None
    message_id: Optional[UUID] = None
    latency_ms: int = 0
    ai_called: bool = True  # Audit flag proving AI was called
    
    def to_dict(self) -> dict:
        return {
            "text_answer": self.text_answer,
            "safety_flags": self.safety_flags,
            "confidence_score": self.confidence_score,
            "escalated": self.escalated,
            "session_id": str(self.session_id) if self.session_id else None,
            "message_id": str(self.message_id) if self.message_id else None,
            "latency_ms": self.latency_ms,
            "ai_called": self.ai_called,
        }
