"""
Pattern Recognition Engine

Tracks recurring phrases, temporal patterns, and context factors.
Stores emotional embeddings in vector database for pattern detection.

ARCHITECTURE: Combines immediate text analysis with historical
pattern retrieval from vector database.

CLINICAL_VALIDATION_REQUIRED: Pattern significance thresholds
and clinical interpretations need psychologist input.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from hope.domain.models.clinical_output import TriggerAnalysis
from hope.infrastructure.vector_db.client import VectorDBClient, VectorSearchResult
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class PatternMatch:
    """
    A detected pattern match from history.
    
    Attributes:
        pattern_type: Type of pattern (phrase, temporal, context)
        description: What was matched
        frequency: How often this pattern occurs
        last_occurrence: When pattern was last seen
        confidence: Match confidence
        clinical_relevance: Relevance to panic triggers
    """
    
    pattern_type: str
    description: str
    frequency: int = 1
    last_occurrence: Optional[datetime] = None
    confidence: float = 0.0
    clinical_relevance: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "type": self.pattern_type,
            "description": self.description,
            "frequency": self.frequency,
            "confidence": round(self.confidence, 3),
        }


@dataclass
class TemporalPattern:
    """
    Time-based pattern in panic occurrences.
    
    Attributes:
        pattern_name: Name of pattern (e.g., "morning_anxiety")
        time_window: Time range this pattern covers
        occurrence_count: Times pattern observed
        average_severity: Average severity during pattern
    """
    
    pattern_name: str
    time_window: str
    occurrence_count: int = 0
    average_severity: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "name": self.pattern_name,
            "window": self.time_window,
            "occurrences": self.occurrence_count,
            "avg_severity": round(self.average_severity, 3),
        }


class PatternRecognitionEngine:
    """
    Pattern recognition for panic triggers and recurring contexts.
    
    Capabilities:
    1. Immediate phrase/keyword pattern matching
    2. Historical pattern retrieval from vector DB
    3. Temporal pattern analysis (time-of-day, day-of-week)
    4. Context factor identification
    
    ARCHITECTURE: This engine bridges real-time analysis with
    historical data stored in the vector database.
    
    Usage:
        engine = PatternRecognitionEngine(vector_client)
        await engine.initialize()
        analysis = await engine.analyze(
            text="I'm panicking about work again",
            user_id=user_id,
            embeddings=[...],
        )
    """
    
    # Trigger phrase patterns
    # CLINICAL_VALIDATION_REQUIRED
    TRIGGER_PHRASES: dict[str, list[str]] = {
        "work_stress": [
            "work", "job", "boss", "deadline", "meeting",
            "fired", "presentation", "workload",
            "عمل", "وظيفة",  # Arabic: work, job
        ],
        "health_anxiety": [
            "heart attack", "dying", "cancer", "sick",
            "disease", "symptoms", "doctor",
            "مرض", "قلب",  # Arabic: disease, heart
        ],
        "social_anxiety": [
            "people", "crowd", "judging", "embarrass",
            "social", "party", "public speaking",
            "ناس", "خجل",  # Arabic: people, shame
        ],
        "relationship": [
            "partner", "relationship", "breakup", "divorce",
            "argument", "fight", "cheating",
            "علاقة", "شريك",  # Arabic: relationship, partner
        ],
        "financial": [
            "money", "debt", "bills", "afford", "rent",
            "bankrupt", "job loss", "savings",
            "مال", "ديون",  # Arabic: money, debt
        ],
        "trauma_related": [
            "nightmare", "flashback", "memory", "abuse",
            "accident", "trauma", "ptsd",
            "كابوس", "صدمة",  # Arabic: nightmare, trauma
        ],
        "existential": [
            "meaning", "purpose", "existence", "alone",
            "lost", "empty", "void",
            "معنى", "وحدة",  # Arabic: meaning, loneliness
        ],
    }
    
    # Temporal patterns to detect
    TEMPORAL_WINDOWS: dict[str, tuple[int, int]] = {
        "early_morning": (4, 7),    # 4 AM - 7 AM
        "morning": (7, 12),          # 7 AM - 12 PM
        "afternoon": (12, 17),       # 12 PM - 5 PM
        "evening": (17, 21),         # 5 PM - 9 PM
        "night": (21, 24),           # 9 PM - 12 AM
        "late_night": (0, 4),        # 12 AM - 4 AM
    }
    
    # How far back to look for patterns
    HISTORY_WINDOW_DAYS: int = 30
    
    # Minimum similarity for vector search matches
    SIMILARITY_THRESHOLD: float = 0.75
    
    def __init__(
        self,
        vector_client: Optional[VectorDBClient] = None,
    ) -> None:
        """
        Initialize pattern recognition engine.
        
        Args:
            vector_client: Vector database client for history
        """
        self._vector_client = vector_client
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize engine and vector client."""
        if self._vector_client:
            await self._vector_client.initialize()
        self._initialized = True
    
    async def analyze(
        self,
        text: str,
        user_id: UUID,
        embeddings: Optional[list[float]] = None,
        timestamp: Optional[datetime] = None,
    ) -> TriggerAnalysis:
        """
        Analyze text for patterns and triggers.
        
        Args:
            text: Input text
            user_id: User ID for history lookup
            embeddings: Text embeddings for similarity search
            timestamp: Time of message (for temporal patterns)
            
        Returns:
            TriggerAnalysis with detected patterns
        """
        timestamp = timestamp or datetime.utcnow()
        
        # Step 1: Immediate trigger detection
        immediate_triggers = self._detect_immediate_triggers(text)
        
        # Step 2: Historical pattern lookup (if vector client available)
        historical_triggers = []
        if self._vector_client and embeddings:
            historical_triggers = await self._find_historical_patterns(
                user_id, embeddings
            )
        
        # Step 3: Temporal pattern analysis
        temporal_patterns = self._detect_temporal_patterns(timestamp)
        
        # Step 4: Context factor extraction
        context_factors = self._extract_context_factors(text)
        
        analysis = TriggerAnalysis(
            immediate_triggers=immediate_triggers,
            historical_triggers=historical_triggers,
            temporal_patterns=temporal_patterns,
            context_factors=context_factors,
        )
        
        logger.debug(
            "Pattern analysis complete",
            immediate_count=len(immediate_triggers),
            historical_count=len(historical_triggers),
        )
        
        return analysis
    
    def _detect_immediate_triggers(self, text: str) -> list[str]:
        """
        Detect triggers in current text.
        
        Returns list of trigger categories found.
        """
        text_lower = text.lower()
        detected = []
        
        for category, phrases in self.TRIGGER_PHRASES.items():
            if any(phrase in text_lower for phrase in phrases):
                detected.append(category)
        
        return detected
    
    async def _find_historical_patterns(
        self,
        user_id: UUID,
        embeddings: list[float],
    ) -> list[str]:
        """
        Find similar patterns from user's history.
        
        Uses vector similarity search to find past
        similar emotional states.
        """
        if not self._vector_client:
            return []
        
        try:
            results = await self._vector_client.search(
                vector=embeddings,
                top_k=10,
                filter={"user_id": str(user_id)},
            )
            
            # Extract trigger categories from similar past events
            historical = []
            for result in results:
                if result.score >= self.SIMILARITY_THRESHOLD:
                    # Get triggers from metadata
                    triggers = result.metadata.get("triggers", [])
                    historical.extend(triggers)
            
            # Deduplicate
            return list(set(historical))
            
        except Exception as e:
            logger.error(f"Historical pattern lookup failed: {e}")
            return []
    
    def _detect_temporal_patterns(
        self,
        timestamp: datetime,
    ) -> list[str]:
        """
        Detect time-based patterns.
        
        Returns list of temporal pattern names.
        """
        hour = timestamp.hour
        patterns = []
        
        # Check time windows
        for window_name, (start, end) in self.TEMPORAL_WINDOWS.items():
            if start <= end:
                if start <= hour < end:
                    patterns.append(window_name)
            else:  # Wraps around midnight
                if hour >= start or hour < end:
                    patterns.append(window_name)
        
        # Check day of week
        day = timestamp.weekday()
        if day == 0:
            patterns.append("monday")  # Monday anxiety
        elif day == 6:
            patterns.append("sunday")  # Sunday scaries
        
        return patterns
    
    def _extract_context_factors(self, text: str) -> list[str]:
        """
        Extract contextual factors from text.
        
        Identifies situational context that may be relevant.
        """
        factors = []
        text_lower = text.lower()
        
        # Location context
        location_markers = {
            "at_home": ["home", "house", "apartment", "room", "bed"],
            "at_work": ["office", "desk", "workplace", "cubicle"],
            "in_public": ["outside", "street", "mall", "store", "restaurant"],
            "in_transit": ["car", "bus", "train", "plane", "driving"],
        }
        
        for context, markers in location_markers.items():
            if any(m in text_lower for m in markers):
                factors.append(context)
        
        # Social context
        if any(w in text_lower for w in ["alone", "by myself", "nobody"]):
            factors.append("alone")
        elif any(w in text_lower for w in ["with", "people", "someone"]):
            factors.append("with_others")
        
        # Activity context
        if any(w in text_lower for w in ["woke up", "waking", "morning"]):
            factors.append("upon_waking")
        elif any(w in text_lower for w in ["sleep", "bed", "night"]):
            factors.append("before_sleep")
        
        return factors
    
    async def store_pattern(
        self,
        user_id: UUID,
        embeddings: list[float],
        triggers: list[str],
        severity: str,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """
        Store pattern in vector database for future matching.
        
        Args:
            user_id: User ID
            embeddings: Emotional embeddings
            triggers: Detected trigger categories
            severity: Severity classification
            timestamp: Time of event
            
        Returns:
            True if stored successfully
        """
        if not self._vector_client:
            logger.warning("No vector client, pattern not stored")
            return False
        
        timestamp = timestamp or datetime.utcnow()
        
        # Generate unique ID
        id_string = f"{user_id}:{timestamp.isoformat()}"
        pattern_id = hashlib.md5(id_string.encode()).hexdigest()
        
        metadata = {
            "user_id": str(user_id),
            "triggers": triggers,
            "severity": severity,
            "timestamp": timestamp.isoformat(),
            "hour": timestamp.hour,
            "day_of_week": timestamp.weekday(),
        }
        
        try:
            success = await self._vector_client.upsert(
                id=pattern_id,
                vector=embeddings,
                metadata=metadata,
            )
            
            if success:
                logger.debug(
                    "Pattern stored",
                    pattern_id=pattern_id,
                    triggers=triggers,
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to store pattern: {e}")
            return False
    
    async def get_user_pattern_summary(
        self,
        user_id: UUID,
    ) -> dict:
        """
        Get summary of user's historical patterns.
        
        Returns aggregated pattern information.
        
        CLINICAL_VALIDATION_REQUIRED: Summary interpretation
        needs clinical guidance.
        """
        # This would query vector DB for user's history
        # and aggregate patterns
        
        # Placeholder implementation
        return {
            "most_common_triggers": [],
            "peak_times": [],
            "average_severity": 0.0,
            "total_events": 0,
        }
