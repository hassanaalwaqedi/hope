"""
Clinical Pipeline

Orchestrates all clinical analysis components to produce
a single ClinicalAssessment output.

ARCHITECTURE: This is the main entry point for clinical analysis.
All components flow through here to produce the contract output.

The ClinicalAssessment produced by this pipeline is the ONLY
input allowed to the Decision Engine.
"""

import hashlib
from typing import Optional
from uuid import UUID

from hope.domain.models.clinical_output import (
    ClinicalAssessment,
    SeverityClassification,
    EmotionProfile,
    DistressIndicators,
    DistressIndicator,
    DistressType,
    TriggerAnalysis,
)
from hope.domain.enums.panic_severity import PanicSeverity, UrgencyLevel
from hope.services.clinical.panic_classifier import PanicSeverityClassifier
from hope.services.clinical.emotion_detector import EmotionDetector
from hope.services.clinical.pattern_engine import PatternRecognitionEngine
from hope.services.clinical.session_analyzer import SessionAnalyzer, SessionAnalyzerRegistry
from hope.services.detection.text_analyzer import TextAnalyzer
from hope.services.detection.ml_model_interface import SentenceEmbeddingModel
from hope.infrastructure.vector_db.client import VectorDBClient
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


class ClinicalPipeline:
    """
    Clinical Intelligence Pipeline.
    
    Orchestrates all clinical analysis components:
    1. Panic Severity Classification (ML)
    2. Emotion Detection (ML)
    3. Distress Indicator Extraction
    4. Pattern Recognition
    5. Session Analysis
    
    Produces a ClinicalAssessment that is the ONLY input
    to the Decision Engine.
    
    Usage:
        pipeline = ClinicalPipeline()
        await pipeline.initialize()
        assessment = await pipeline.analyze(
            text="I'm having a severe panic attack",
            user_id=user_id,
            session_id=session_id,
        )
    
    ARCHITECTURE: This pipeline enforces the contract between
    clinical analysis and decision making. No raw text or
    intermediate results leak to the Decision Engine.
    """
    
    # Model versions for tracking
    PIPELINE_VERSION = "2.0.0"
    
    def __init__(
        self,
        severity_classifier: Optional[PanicSeverityClassifier] = None,
        emotion_detector: Optional[EmotionDetector] = None,
        pattern_engine: Optional[PatternRecognitionEngine] = None,
        embedding_model: Optional[SentenceEmbeddingModel] = None,
        vector_client: Optional[VectorDBClient] = None,
    ) -> None:
        """
        Initialize clinical pipeline.
        
        Args:
            severity_classifier: Panic severity classifier
            emotion_detector: Emotion detection model
            pattern_engine: Pattern recognition engine
            embedding_model: Text embedding model
            vector_client: Vector database client
        """
        self._classifier = severity_classifier or PanicSeverityClassifier()
        self._emotion = emotion_detector or EmotionDetector()
        self._patterns = pattern_engine or PatternRecognitionEngine(vector_client)
        self._embeddings = embedding_model or SentenceEmbeddingModel()
        self._text_analyzer = TextAnalyzer()
        self._vector_client = vector_client
        
        self._initialized = False
    
    async def initialize(self) -> None:
        """
        Initialize all pipeline components.
        
        Should be called during application startup.
        """
        if self._initialized:
            return
        
        logger.info("Initializing clinical pipeline")
        
        # Load ML models
        await self._classifier.load()
        await self._emotion.load()
        await self._embeddings.load()
        
        # Initialize pattern engine
        await self._patterns.initialize()
        
        self._initialized = True
        logger.info("Clinical pipeline initialized")
    
    async def shutdown(self) -> None:
        """Shutdown and unload models."""
        await self._classifier.unload()
        await self._emotion.unload()
        await self._embeddings.unload()
        self._initialized = False
    
    async def analyze(
        self,
        text: str,
        user_id: UUID,
        session_id: Optional[UUID] = None,
        message_id: Optional[UUID] = None,
    ) -> ClinicalAssessment:
        """
        Perform complete clinical analysis.
        
        This is the main entry point. Runs all analysis
        components and produces the ClinicalAssessment.
        
        Args:
            text: User input text
            user_id: User ID
            session_id: Session ID (if in session)
            message_id: Message ID (for tracking)
            
        Returns:
            ClinicalAssessment contract output
        """
        if not self._initialized:
            await self.initialize()
        
        # Handle empty input
        if not text or not text.strip():
            return self._create_empty_assessment(user_id, session_id, message_id)
        
        logger.debug(
            "Starting clinical analysis",
            user_id=str(user_id),
            text_length=len(text),
        )
        
        # Step 1: Rule-based text analysis (for distress indicators)
        text_analysis = self._text_analyzer.analyze(text)
        
        # Step 2: Check for immediate crisis
        if text_analysis.requires_immediate_attention:
            return await self._create_crisis_assessment(
                text, user_id, session_id, message_id, text_analysis
            )
        
        # Step 3: Generate embeddings (for pattern matching and storage)
        embeddings = await self._embeddings.get_embeddings(text)
        
        # Step 4: Severity classification (ML)
        severity = await self._classifier.predict(text)
        
        # Step 5: Emotion detection (ML)
        emotion_profile = await self._emotion.detect(text)
        
        # Step 6: Extract distress indicators
        distress = self._extract_distress_indicators(text_analysis)
        
        # Step 7: Pattern recognition
        triggers = await self._patterns.analyze(
            text=text,
            user_id=user_id,
            embeddings=embeddings,
        )
        
        # Step 8: Update session analyzer (if in session)
        if session_id:
            analyzer = SessionAnalyzerRegistry.get_or_create(session_id, user_id)
            analyzer.record_message(
                intensity=severity.confidence,
                severity=severity.predicted_severity,
            )
        
        # Step 9: Determine crisis protocol
        requires_crisis = self._should_activate_crisis_protocol(
            severity, emotion_profile, text_analysis
        )
        
        # Step 10: Calculate overall confidence
        confidence = self._calculate_overall_confidence(
            severity, emotion_profile
        )
        
        # Step 11: Gather uncertainty flags
        uncertainty_flags = self._gather_uncertainty_flags(
            severity, emotion_profile, triggers
        )
        
        # Step 12: Build assessment
        assessment = ClinicalAssessment(
            user_id=user_id,
            session_id=session_id,
            message_id=message_id,
            severity=severity,
            emotion_profile=emotion_profile,
            distress_indicators=distress,
            trigger_analysis=triggers,
            requires_crisis_protocol=requires_crisis,
            confidence_score=confidence,
            uncertainty_flags=uncertainty_flags,
            raw_text_hash=self._hash_text(text),
            model_versions=self._get_model_versions(),
            embeddings=embeddings,
        )
        
        # Step 13: Store pattern for future matching
        if self._vector_client and embeddings:
            await self._patterns.store_pattern(
                user_id=user_id,
                embeddings=embeddings,
                triggers=triggers.immediate_triggers,
                severity=severity.predicted_severity.name,
            )
        
        logger.info(
            "Clinical analysis complete",
            severity=severity.predicted_severity.name,
            confidence=round(confidence, 3),
            crisis=requires_crisis,
        )
        
        return assessment
    
    def _create_empty_assessment(
        self,
        user_id: UUID,
        session_id: Optional[UUID],
        message_id: Optional[UUID],
    ) -> ClinicalAssessment:
        """Create assessment for empty input."""
        return ClinicalAssessment(
            user_id=user_id,
            session_id=session_id,
            message_id=message_id,
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.NONE,
                confidence=1.0,
            ),
            confidence_score=1.0,
        )
    
    async def _create_crisis_assessment(
        self,
        text: str,
        user_id: UUID,
        session_id: Optional[UUID],
        message_id: Optional[UUID],
        text_analysis,
    ) -> ClinicalAssessment:
        """
        Create crisis-level assessment.
        
        SAFETY_CRITICAL: This is triggered by crisis indicators.
        Always returns maximum severity.
        """
        logger.warning(
            "Crisis indicators detected",
            user_id=str(user_id),
            indicators=text_analysis.crisis_indicators,
        )
        
        # Get embeddings for crisis event storage
        embeddings = await self._embeddings.get_embeddings(text)
        
        # Update session if active
        if session_id:
            analyzer = SessionAnalyzerRegistry.get_or_create(session_id, user_id)
            analyzer.record_message(
                intensity=1.0,
                severity=PanicSeverity.CRITICAL,
            )
        
        return ClinicalAssessment(
            user_id=user_id,
            session_id=session_id,
            message_id=message_id,
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.CRITICAL,
                probabilities={PanicSeverity.CRITICAL: 1.0},
                confidence=1.0,
            ),
            urgency=UrgencyLevel.EMERGENCY,
            requires_crisis_protocol=True,
            requires_human_review=True,
            confidence_score=1.0,
            uncertainty_flags=["crisis_indicators_detected"],
            raw_text_hash=self._hash_text(text),
            model_versions=self._get_model_versions(),
            embeddings=embeddings,
        )
    
    def _extract_distress_indicators(
        self,
        text_analysis,
    ) -> DistressIndicators:
        """Extract structured distress indicators from text analysis."""
        distress = DistressIndicators()
        
        # Physiological indicators
        for symptom in text_analysis.physiological_mentions:
            distress.physiological.append(DistressIndicator(
                indicator_type=DistressType.PHYSIOLOGICAL,
                description=symptom,
                severity=0.6,  # Base severity
                source_text=symptom,
            ))
        
        # Cognitive indicators
        for pattern in text_analysis.cognitive_patterns:
            distress.cognitive.append(DistressIndicator(
                indicator_type=DistressType.COGNITIVE,
                description=pattern,
                severity=0.5,
            ))
        
        # Calculate overall distress
        all_indicators = distress.all_indicators()
        if all_indicators:
            distress.overall_distress_level = (
                sum(i.severity for i in all_indicators) / len(all_indicators)
            )
        
        return distress
    
    def _should_activate_crisis_protocol(
        self,
        severity: SeverityClassification,
        emotion_profile: EmotionProfile,
        text_analysis,
    ) -> bool:
        """Determine if crisis protocol should be activated."""
        # Crisis indicators always trigger protocol
        if text_analysis.crisis_indicators:
            return True
        
        # Critical severity triggers protocol
        if severity.predicted_severity >= PanicSeverity.CRITICAL:
            return True
        
        # Severe + high dissociation triggers protocol
        if severity.predicted_severity >= PanicSeverity.SEVERE:
            from hope.domain.models.clinical_output import EmotionCategory
            dissociation = emotion_profile.get_emotion_score(
                EmotionCategory.DISSOCIATION
            )
            if dissociation > 0.7:
                return True
        
        return False
    
    def _calculate_overall_confidence(
        self,
        severity: SeverityClassification,
        emotion_profile: EmotionProfile,
    ) -> float:
        """Calculate overall assessment confidence."""
        # Weighted average of component confidences
        severity_confidence = severity.confidence
        
        emotion_confidence = 0.5  # Default if no emotions
        if emotion_profile.emotions:
            emotion_confidence = max(e.confidence for e in emotion_profile.emotions)
        
        # Weight severity more heavily
        return severity_confidence * 0.6 + emotion_confidence * 0.4
    
    def _gather_uncertainty_flags(
        self,
        severity: SeverityClassification,
        emotion_profile: EmotionProfile,
        triggers: TriggerAnalysis,
    ) -> list[str]:
        """Gather all uncertainty flags from components."""
        flags = []
        
        if severity.uncertainty_flag:
            flags.append("severity_uncertain")
        
        if not emotion_profile.has_high_confidence():
            flags.append("emotion_low_confidence")
        
        if emotion_profile.emotional_volatility > 0.7:
            flags.append("high_emotional_volatility")
        
        if not triggers.immediate_triggers and not triggers.historical_triggers:
            flags.append("no_triggers_identified")
        
        return flags
    
    def _hash_text(self, text: str) -> str:
        """Create hash of text for audit trail."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    def _get_model_versions(self) -> dict[str, str]:
        """Get versions of all models used."""
        return {
            "pipeline": self.PIPELINE_VERSION,
            "severity_classifier": self._classifier.config.version,
            "emotion_detector": self._emotion.config.version,
        }
    
    def get_session_metrics(self, session_id: UUID) -> Optional[dict]:
        """
        Get metrics for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session metrics or None
        """
        analyzer = SessionAnalyzerRegistry.get(session_id)
        if analyzer:
            return analyzer.get_summary()
        return None
    
    def finalize_session(self, session_id: UUID) -> Optional[dict]:
        """
        Finalize and remove session analyzer.
        
        Args:
            session_id: Session ID
            
        Returns:
            Final session metrics or None
        """
        analyzer = SessionAnalyzerRegistry.remove(session_id)
        if analyzer:
            metrics = analyzer.finalize()
            return metrics.to_dict()
        return None
