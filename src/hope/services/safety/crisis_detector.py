"""
Crisis Detector

Detects suicide and self-harm risk signals.
Combines linguistic, emotional, and behavioral analysis.

SAFETY-CRITICAL: This module handles life-safety concerns.
No single signal triggers escalation. Multi-signal confirmation required.

LEGAL_REVIEW_REQUIRED: Detection patterns and escalation logic
have significant legal and clinical implications.
"""

import re
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from hope.domain.models.clinical_output import ClinicalAssessment, EmotionCategory
from hope.domain.enums.panic_severity import PanicSeverity
from hope.domain.models.risk_models import RiskSignal, RiskSignalType
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class CrisisSignal:
    """
    A detected crisis signal.
    
    SAFETY_NOTE: Individual signals should NEVER trigger
    escalation alone. Signals must be combined.
    """
    
    signal_name: str
    description: str
    category: str  # linguistic, emotional, behavioral, contextual
    weight: float
    confidence: float
    pattern_matched: str = ""
    
    def to_dict(self) -> dict:
        return {
            "name": self.signal_name,
            "category": self.category,
            "weight": round(self.weight, 3),
            "confidence": round(self.confidence, 3),
        }


@dataclass
class CrisisDetectionResult:
    """
    Result of crisis detection analysis.
    
    ARCHITECTURE: This result feeds into the RiskScoringEngine.
    It does not make escalation decisions directly.
    
    Attributes:
        has_crisis_signals: Whether any crisis signals detected
        signals: List of detected signals
        linguistic_signal_count: Count of language-based signals
        emotional_signal_count: Count of emotion-based signals
        combined_crisis_score: Combined score (0.0-1.0)
        meets_multi_signal_requirement: Whether multiple types present
    """
    
    has_crisis_signals: bool = False
    signals: list[CrisisSignal] = field(default_factory=list)
    linguistic_signal_count: int = 0
    emotional_signal_count: int = 0
    behavioral_signal_count: int = 0
    combined_crisis_score: float = 0.0
    meets_multi_signal_requirement: bool = False
    
    def __post_init__(self) -> None:
        self.linguistic_signal_count = sum(
            1 for s in self.signals if s.category == "linguistic"
        )
        self.emotional_signal_count = sum(
            1 for s in self.signals if s.category == "emotional"
        )
        self.behavioral_signal_count = sum(
            1 for s in self.signals if s.category == "behavioral"
        )
        
        # Multi-signal requirement: At least 2 different categories
        categories = set(s.category for s in self.signals)
        self.meets_multi_signal_requirement = len(categories) >= 2
    
    def to_risk_signals(self) -> list[RiskSignal]:
        """Convert to RiskSignal format for risk engine."""
        return [
            RiskSignal(
                signal_type=RiskSignalType.LINGUISTIC if s.category == "linguistic"
                else RiskSignalType.EMOTIONAL if s.category == "emotional"
                else RiskSignalType.BEHAVIORAL,
                signal_name=s.signal_name,
                description=s.description,
                weight=s.weight,
                confidence=s.confidence,
                source="crisis_detector",
            )
            for s in self.signals
        ]


class CrisisDetector:
    """
    Suicide and self-harm crisis detection.
    
    SAFETY-CRITICAL: This detector identifies potential
    crisis situations including suicide and self-harm risk.
    
    Key Principles:
    1. NO SINGLE SIGNAL triggers escalation
    2. Multi-signal confirmation required from different categories
    3. False negatives are WORSE than false positives
    4. When in doubt, escalate
    
    Signal Categories:
    - Linguistic: Language patterns suggesting crisis
    - Emotional: Emotional trajectory patterns
    - Behavioral: Escalating panic, sustained distress
    - Contextual: Time patterns, triggers
    
    LEGAL_REVIEW_REQUIRED: All detection patterns and
    threshold logic require clinical and legal review.
    """
    
    # Linguistic patterns for crisis signals
    # CLINICAL_VALIDATION_REQUIRED
    # Patterns are phrases/contexts, not single words
    LINGUISTIC_PATTERNS: list[tuple[str, re.Pattern, float]] = [
        # Direct expressions (highest weight)
        (
            "direct_self_harm_intent",
            re.compile(
                r"(want|going|plan|thinking about|considering)\s+(to\s+)?"
                r"(hurt|harm|kill|end)\s+(myself|my life|it all)",
                re.IGNORECASE
            ),
            0.40,
        ),
        (
            "suicide_ideation",
            re.compile(
                r"(want|wish|rather)\s+(to\s+)?(be\s+)?dead|"
                r"(don't|do not)\s+want\s+to\s+(live|be here|exist)|"
                r"wish\s+i\s+(was|were)\s+(never\s+)?born",
                re.IGNORECASE
            ),
            0.35,
        ),
        # Method references (high weight)
        (
            "method_reference",
            re.compile(
                r"(pills|overdose|cut|cutting|jump|jumping|hanging|gun|weapon)",
                re.IGNORECASE
            ),
            0.25,
        ),
        # Hopelessness patterns
        (
            "hopelessness_expression",
            re.compile(
                r"(no\s+(way\s+out|hope|point|reason)|"
                r"never\s+get\s+better|"
                r"can't\s+(go\s+on|take\s+(it|this)\s+anymore)|"
                r"give\s+up)",
                re.IGNORECASE
            ),
            0.20,
        ),
        # Goodbye/farewell patterns
        (
            "farewell_language",
            re.compile(
                r"(goodbye\s+forever|"
                r"won't\s+be\s+(here|around|a\s+problem)|"
                r"better\s+off\s+without\s+me|"
                r"saying\s+goodbye)",
                re.IGNORECASE
            ),
            0.30,
        ),
        # Burden to others
        (
            "burden_expression",
            re.compile(
                r"(burden|bother|problem)\s+(to|for)\s+(everyone|you|them|others)|"
                r"everyone.*better.*without\s+me",
                re.IGNORECASE
            ),
            0.20,
        ),
    ]
    
    # Minimum requirements for escalation
    MIN_SIGNALS_FOR_CONCERN: int = 2
    MIN_CATEGORIES_FOR_ESCALATION: int = 2
    
    def __init__(self) -> None:
        """Initialize crisis detector."""
        pass
    
    def detect(
        self,
        clinical: ClinicalAssessment,
        message_text_hash: Optional[str] = None,
    ) -> CrisisDetectionResult:
        """
        Detect crisis signals from clinical assessment.
        
        ARCHITECTURE: Uses only structured clinical data.
        Linguistic analysis must happen in clinical pipeline.
        This method evaluates signals, not raw text.
        
        Args:
            clinical: Clinical assessment
            message_text_hash: Hash of message (for audit only)
            
        Returns:
            CrisisDetectionResult with detected signals
        """
        signals: list[CrisisSignal] = []
        
        # Step 1: Analyze emotional signals
        signals.extend(self._analyze_emotions(clinical))
        
        # Step 2: Analyze behavioral signals
        signals.extend(self._analyze_behavioral(clinical))
        
        # Step 3: Check distress trajectory
        signals.extend(self._analyze_distress(clinical))
        
        # Step 4: Check crisis protocol flag
        if clinical.requires_crisis_protocol:
            signals.append(CrisisSignal(
                signal_name="crisis_protocol_flag",
                description="Clinical pipeline flagged crisis",
                category="behavioral",
                weight=0.35,
                confidence=1.0,
            ))
        
        # Step 5: Calculate combined score
        combined_score = self._calculate_combined_score(signals)
        
        # Step 6: Determine if crisis signals present
        has_signals = len(signals) >= self.MIN_SIGNALS_FOR_CONCERN
        
        result = CrisisDetectionResult(
            has_crisis_signals=has_signals,
            signals=signals,
            combined_crisis_score=combined_score,
        )
        
        if has_signals:
            logger.warning(
                "Crisis signals detected",
                signal_count=len(signals),
                meets_multi_signal=result.meets_multi_signal_requirement,
                combined_score=round(combined_score, 3),
            )
        
        return result
    
    def _analyze_emotions(
        self,
        clinical: ClinicalAssessment,
    ) -> list[CrisisSignal]:
        """Analyze emotional profile for crisis signals."""
        signals = []
        profile = clinical.emotion_profile
        
        # High dread with high intensity
        dread_score = profile.get_emotion_score(EmotionCategory.DREAD)
        if dread_score > 0.7:
            signals.append(CrisisSignal(
                signal_name="severe_dread",
                description="Severe dread/impending doom detected",
                category="emotional",
                weight=0.25,
                confidence=dread_score,
            ))
        
        # Dissociation
        dissoc_score = profile.get_emotion_score(EmotionCategory.DISSOCIATION)
        if dissoc_score > 0.6:
            signals.append(CrisisSignal(
                signal_name="dissociation",
                description="Significant dissociation detected",
                category="emotional",
                weight=0.20,
                confidence=dissoc_score,
            ))
        
        # Helplessness
        helpless_score = profile.get_emotion_score(EmotionCategory.HELPLESSNESS)
        if helpless_score > 0.7:
            signals.append(CrisisSignal(
                signal_name="severe_helplessness",
                description="Severe helplessness detected",
                category="emotional",
                weight=0.25,
                confidence=helpless_score,
            ))
        
        # Emotional shutdown (no emotions detected at high severity)
        if clinical.severity.predicted_severity >= PanicSeverity.SEVERE:
            if not profile.emotions:
                signals.append(CrisisSignal(
                    signal_name="emotional_shutdown",
                    description="Emotional shutdown at high severity",
                    category="emotional",
                    weight=0.20,
                    confidence=0.7,
                ))
        
        return signals
    
    def _analyze_behavioral(
        self,
        clinical: ClinicalAssessment,
    ) -> list[CrisisSignal]:
        """Analyze behavioral signals."""
        signals = []
        
        # Critical severity
        if clinical.severity.predicted_severity >= PanicSeverity.CRITICAL:
            signals.append(CrisisSignal(
                signal_name="critical_severity",
                description="Critical panic severity level",
                category="behavioral",
                weight=0.30,
                confidence=clinical.severity.confidence,
            ))
        
        return signals
    
    def _analyze_distress(
        self,
        clinical: ClinicalAssessment,
    ) -> list[CrisisSignal]:
        """Analyze distress indicators."""
        signals = []
        distress = clinical.distress_indicators
        
        # Very high distress
        if distress.overall_distress_level > 0.8:
            signals.append(CrisisSignal(
                signal_name="extreme_distress",
                description="Extreme overall distress level",
                category="behavioral",
                weight=0.25,
                confidence=distress.overall_distress_level,
            ))
        
        # Multiple distress types
        if distress.indicator_count() >= 4:
            signals.append(CrisisSignal(
                signal_name="multi_domain_distress",
                description="Distress across multiple domains",
                category="behavioral",
                weight=0.15,
                confidence=0.8,
            ))
        
        return signals
    
    def _calculate_combined_score(
        self,
        signals: list[CrisisSignal],
    ) -> float:
        """Calculate combined crisis score."""
        if not signals:
            return 0.0
        
        # Weighted sum with confidence
        total = sum(s.weight * s.confidence for s in signals)
        
        # Cap at 1.0
        return min(1.0, total)


# Module-level linguistic analyzer for text-based detection
# This should be called BEFORE clinical pipeline in special cases
class LinguisticCrisisAnalyzer:
    """
    Direct linguistic analysis for crisis patterns.
    
    SAFETY_NOTE: This analyzer runs on raw text and should
    be used as an ADDITIONAL safety check, not primary.
    The crisis detector above uses structured clinical data.
    
    Use cases:
    - Pre-screening before full clinical analysis
    - Cross-validation of ML predictions
    - Fallback when ML is unavailable
    """
    
    # Same patterns as CrisisDetector but for raw text
    PATTERNS = CrisisDetector.LINGUISTIC_PATTERNS
    
    @classmethod
    def analyze_text(cls, text: str) -> list[CrisisSignal]:
        """
        Analyze raw text for crisis patterns.
        
        Args:
            text: Raw user input
            
        Returns:
            List of detected crisis signals
        """
        if not text or not text.strip():
            return []
        
        signals = []
        
        for signal_name, pattern, weight in cls.PATTERNS:
            match = pattern.search(text)
            if match:
                signals.append(CrisisSignal(
                    signal_name=signal_name,
                    description=f"Matched pattern: {signal_name}",
                    category="linguistic",
                    weight=weight,
                    confidence=0.9,  # High confidence for explicit patterns
                    pattern_matched=match.group(0),
                ))
        
        return signals
