"""
Emotional Context Domain Model

Represents emotional state embeddings for vector database storage.
Used for retrieving relevant historical context to personalize
responses.

PRIVACY: Emotional context contains sensitive personal data.
Storage and retrieval must respect user consent for emotional
history storage.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID, uuid4


class EmotionalState(StrEnum):
    """
    High-level emotional state classifications.
    
    Used for quick filtering before vector similarity search.
    
    CLINICAL_REVIEW_REQUIRED: These categories should be
    validated against established emotional frameworks.
    """
    
    CALM = "calm"
    """Relaxed, peaceful state."""
    
    ANXIOUS = "anxious"
    """Worried, nervous, or uneasy."""
    
    PANICKING = "panicking"
    """Active panic or severe anxiety."""
    
    RECOVERING = "recovering"
    """Post-crisis, calming down."""
    
    DISTRESSED = "distressed"
    """General emotional distress."""
    
    OVERWHELMED = "overwhelmed"
    """Feeling of being unable to cope."""
    
    HOPEFUL = "hopeful"
    """Positive outlook, feeling better."""
    
    NEUTRAL = "neutral"
    """No strong emotional state detected."""


@dataclass
class EmotionalContext:
    """
    Emotional context snapshot for vector storage.
    
    Captures a moment's emotional state with embeddings
    for similarity search and context retrieval.
    
    Attributes:
        id: Unique context identifier
        user_id: Associated user ID
        session_id: Associated session ID
        timestamp: When context was captured
        emotional_state: High-level state classification
        intensity: Emotional intensity (0.0-1.0)
        embedding: Vector embedding of emotional context
        source_text: Original text that generated context
        panic_severity: Associated panic severity if applicable
        interventions_effective: What helped (for pattern learning)
        metadata: Additional context data
    """
    
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    session_id: Optional[UUID] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Emotional classification
    emotional_state: EmotionalState = EmotionalState.NEUTRAL
    intensity: float = 0.0  # 0.0-1.0
    
    # Vector embedding
    embedding: Optional[list[float]] = None
    embedding_model: str = ""  # Model used to generate embedding
    embedding_dimension: int = 0
    
    # Source and context
    source_text: str = ""  # The text that generated this context
    source_text_hash: str = ""  # Hash for deduplication
    
    # Associated panic data
    panic_severity: Optional[int] = None
    interventions_effective: list[str] = field(default_factory=list)
    
    # Metadata
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate fields."""
        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError(f"Intensity must be 0.0-1.0, got {self.intensity}")
        
        if self.embedding:
            self.embedding_dimension = len(self.embedding)
    
    def set_embedding(self, embedding: list[float], model: str) -> None:
        """
        Set the vector embedding.
        
        Args:
            embedding: Vector embedding values
            model: Model identifier that generated the embedding
        """
        self.embedding = embedding
        self.embedding_model = model
        self.embedding_dimension = len(embedding)
    
    @property
    def has_embedding(self) -> bool:
        """Check if embedding has been generated."""
        return self.embedding is not None and len(self.embedding) > 0
    
    def to_vector_metadata(self) -> dict:
        """
        Generate metadata dict for vector database storage.
        
        Returns:
            Metadata dict suitable for Pinecone/Weaviate
        """
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "session_id": str(self.session_id) if self.session_id else "",
            "timestamp": self.timestamp.isoformat(),
            "emotional_state": self.emotional_state.value,
            "intensity": self.intensity,
            "panic_severity": self.panic_severity or 0,
        }
    
    def to_dict(self) -> dict:
        """Serialize to dictionary (excluding embedding for size)."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "session_id": str(self.session_id) if self.session_id else None,
            "timestamp": self.timestamp.isoformat(),
            "emotional_state": self.emotional_state.value,
            "intensity": self.intensity,
            "has_embedding": self.has_embedding,
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dimension,
            "panic_severity": self.panic_severity,
            "interventions_effective": self.interventions_effective,
        }


@dataclass
class EmotionalPattern:
    """
    Detected emotional pattern over time.
    
    Aggregates emotional contexts to identify recurring
    patterns that may inform intervention strategies.
    
    CLINICAL_REVIEW_REQUIRED: Pattern detection thresholds
    and interpretation should be validated clinically.
    """
    
    user_id: UUID
    pattern_type: str  # e.g., "recurring_trigger", "time_based", "escalation"
    description: str
    confidence: float
    first_detected: datetime
    last_observed: datetime
    context_ids: list[UUID] = field(default_factory=list)
    recommended_interventions: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "user_id": str(self.user_id),
            "pattern_type": self.pattern_type,
            "description": self.description,
            "confidence": self.confidence,
            "first_detected": self.first_detected.isoformat(),
            "last_observed": self.last_observed.isoformat(),
            "context_count": len(self.context_ids),
            "recommended_interventions": self.recommended_interventions,
        }
