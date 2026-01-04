"""
Panic Detection Service

Core service for detecting panic attacks from text input.
Combines rule-based analysis with ML model inference.

ARCHITECTURE: This is the entry point for the detection pipeline.
All text input passes through here before reaching the decision engine.

CLINICAL_REVIEW_REQUIRED: Detection thresholds and severity
classification logic require clinical validation.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from hope.domain.enums.panic_severity import PanicSeverity, UrgencyLevel
from hope.domain.models.panic_event import PanicEvent, PanicTrigger
from hope.services.detection.text_analyzer import TextAnalyzer, TextAnalysisResult
from hope.services.detection.ml_model_interface import (
    MLModelInterface,
    ModelPrediction,
    HuggingFaceEmotionModel,
    SentenceEmbeddingModel,
)
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class DetectionResult:
    """
    Complete panic detection result.
    
    Attributes:
        detected: Whether panic was detected
        severity: Classified severity level
        urgency: Response urgency level
        confidence: Overall detection confidence
        text_analysis: Rule-based analysis results
        ml_prediction: ML model prediction (if available)
        suggested_triggers: Inferred trigger categories
        embeddings: Text embeddings for vector storage
        requires_escalation: Whether to escalate to crisis
    """
    
    detected: bool
    severity: PanicSeverity
    urgency: UrgencyLevel
    confidence: float
    text_analysis: TextAnalysisResult
    ml_prediction: Optional[ModelPrediction] = None
    suggested_triggers: list[PanicTrigger] = None
    embeddings: Optional[list[float]] = None
    requires_escalation: bool = False
    
    def __post_init__(self) -> None:
        if self.suggested_triggers is None:
            self.suggested_triggers = []
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "detected": self.detected,
            "severity": self.severity.name,
            "urgency": self.urgency.value,
            "confidence": self.confidence,
            "requires_escalation": self.requires_escalation,
            "text_analysis": self.text_analysis.to_dict(),
            "suggested_triggers": [t.value for t in self.suggested_triggers],
            "has_embeddings": self.embeddings is not None,
        }


class PanicDetectionService:
    """
    Panic detection service combining rule-based and ML analysis.
    
    This service is the primary entry point for analyzing user
    input for signs of panic attacks or crisis.
    
    Pipeline:
    1. Text normalization and rule-based analysis
    2. ML model inference (emotion detection)
    3. Embedding generation (for vector storage)
    4. Severity classification
    5. Urgency determination
    
    SAFETY: Crisis indicators always trigger immediate escalation
    regardless of model predictions.
    """
    
    # Severity thresholds
    # CLINICAL_REVIEW_REQUIRED: These thresholds need clinical validation
    SEVERITY_THRESHOLDS: dict[str, tuple[float, float]] = {
        "critical": (0.85, 1.0),
        "severe": (0.65, 0.85),
        "moderate": (0.40, 0.65),
        "mild": (0.20, 0.40),
        "none": (0.0, 0.20),
    }
    
    def __init__(
        self,
        emotion_model: Optional[MLModelInterface] = None,
        embedding_model: Optional[MLModelInterface] = None,
        enable_ml: bool = True,
    ) -> None:
        """
        Initialize panic detection service.
        
        Args:
            emotion_model: ML model for emotion detection
            embedding_model: Model for generating embeddings
            enable_ml: Whether to use ML models (can be disabled)
        """
        self._text_analyzer = TextAnalyzer()
        self._emotion_model = emotion_model or HuggingFaceEmotionModel()
        self._embedding_model = embedding_model or SentenceEmbeddingModel()
        self._enable_ml = enable_ml
        self._models_loaded = False
    
    async def load_models(self) -> None:
        """
        Load ML models into memory.
        
        Should be called during application startup.
        """
        if self._models_loaded or not self._enable_ml:
            return
        
        logger.info("Loading panic detection ML models")
        await self._emotion_model.load()
        await self._embedding_model.load()
        self._models_loaded = True
        logger.info("Panic detection models loaded successfully")
    
    async def unload_models(self) -> None:
        """Unload ML models to free memory."""
        if self._emotion_model:
            await self._emotion_model.unload()
        if self._embedding_model:
            await self._embedding_model.unload()
        self._models_loaded = False
    
    async def detect(
        self,
        text: str,
        user_id: Optional[UUID] = None,
        session_id: Optional[UUID] = None,
        include_embeddings: bool = True,
    ) -> DetectionResult:
        """
        Analyze text for panic indicators.
        
        Main entry point for panic detection. Combines rule-based
        analysis with ML inference for robust detection.
        
        Args:
            text: User input text to analyze
            user_id: Optional user ID for context
            session_id: Optional session ID for context
            include_embeddings: Whether to generate embeddings
            
        Returns:
            DetectionResult with severity classification and analysis
        """
        if not text or not text.strip():
            return DetectionResult(
                detected=False,
                severity=PanicSeverity.NONE,
                urgency=UrgencyLevel.ROUTINE,
                confidence=1.0,
                text_analysis=TextAnalysisResult(raw_text=text),
            )
        
        # Step 1: Rule-based text analysis
        text_analysis = self._text_analyzer.analyze(text)
        
        # Step 2: Check for crisis indicators (immediate escalation)
        if text_analysis.crisis_indicators:
            logger.warning(
                "Crisis indicators detected",
                user_id=str(user_id) if user_id else None,
                indicators=text_analysis.crisis_indicators,
            )
            return await self._create_crisis_result(text_analysis, user_id, session_id)
        
        # Step 3: ML model inference (if enabled)
        ml_prediction = None
        if self._enable_ml:
            try:
                if not self._models_loaded:
                    await self.load_models()
                ml_prediction = await self._emotion_model.predict(text)
            except Exception as e:
                logger.error("ML model inference failed", error=str(e))
                # Continue with rule-based only
        
        # Step 4: Generate embeddings (if requested)
        embeddings = None
        if include_embeddings and self._enable_ml:
            try:
                if not self._models_loaded:
                    await self.load_models()
                embeddings = await self._embedding_model.get_embeddings(text)
            except Exception as e:
                logger.error("Embedding generation failed", error=str(e))
        
        # Step 5: Combine scores and classify severity
        combined_score = self._calculate_combined_score(
            text_analysis,
            ml_prediction,
        )
        severity = self._classify_severity(combined_score)
        urgency = UrgencyLevel.from_severity(severity)
        
        # Step 6: Infer triggers
        suggested_triggers = self._infer_triggers(text_analysis)
        
        # Step 7: Determine if panic is detected
        detected = severity > PanicSeverity.NONE
        
        logger.debug(
            "Panic detection completed",
            detected=detected,
            severity=severity.name,
            score=combined_score,
            user_id=str(user_id) if user_id else None,
        )
        
        return DetectionResult(
            detected=detected,
            severity=severity,
            urgency=urgency,
            confidence=combined_score,
            text_analysis=text_analysis,
            ml_prediction=ml_prediction,
            suggested_triggers=suggested_triggers,
            embeddings=embeddings,
            requires_escalation=severity >= PanicSeverity.CRITICAL,
        )
    
    async def _create_crisis_result(
        self,
        text_analysis: TextAnalysisResult,
        user_id: Optional[UUID],
        session_id: Optional[UUID],
    ) -> DetectionResult:
        """
        Create result for crisis-level detection.
        
        SAFETY_CRITICAL: This path is for serious crisis indicators.
        Always returns maximum severity and escalation flag.
        """
        embeddings = None
        if self._enable_ml:
            try:
                if not self._models_loaded:
                    await self.load_models()
                embeddings = await self._embedding_model.get_embeddings(
                    text_analysis.raw_text
                )
            except Exception:
                pass  # Don't fail crisis detection on embedding failure
        
        return DetectionResult(
            detected=True,
            severity=PanicSeverity.CRITICAL,
            urgency=UrgencyLevel.EMERGENCY,
            confidence=1.0,
            text_analysis=text_analysis,
            embeddings=embeddings,
            requires_escalation=True,  # ALWAYS escalate for crisis
        )
    
    def _calculate_combined_score(
        self,
        text_analysis: TextAnalysisResult,
        ml_prediction: Optional[ModelPrediction],
    ) -> float:
        """
        Combine rule-based and ML scores.
        
        CLINICAL_REVIEW_REQUIRED: Weighting between rule-based
        and ML scores should be clinically validated.
        
        Args:
            text_analysis: Rule-based analysis result
            ml_prediction: ML model prediction (if available)
            
        Returns:
            Combined confidence score (0.0-1.0)
        """
        # Base score from rule-based analysis
        rule_score = text_analysis.risk_score
        
        if ml_prediction is None:
            return rule_score
        
        # Get ML score - weight by emotion severity
        ml_score = ml_prediction.confidence
        severity_weight = ml_prediction.metadata.get("severity_weight", 0.5)
        ml_adjusted = ml_score * severity_weight
        
        # Combine scores (weighted average)
        # CLINICAL_REVIEW_REQUIRED: Weight ratio
        RULE_WEIGHT = 0.4
        ML_WEIGHT = 0.6
        
        combined = (rule_score * RULE_WEIGHT) + (ml_adjusted * ML_WEIGHT)
        
        # Boost if both agree on high risk
        if rule_score > 0.5 and ml_adjusted > 0.5:
            combined = min(1.0, combined * 1.2)
        
        return min(1.0, combined)
    
    def _classify_severity(self, score: float) -> PanicSeverity:
        """
        Classify panic severity from score.
        
        Args:
            score: Combined confidence score
            
        Returns:
            PanicSeverity level
        """
        if score >= self.SEVERITY_THRESHOLDS["critical"][0]:
            return PanicSeverity.CRITICAL
        elif score >= self.SEVERITY_THRESHOLDS["severe"][0]:
            return PanicSeverity.SEVERE
        elif score >= self.SEVERITY_THRESHOLDS["moderate"][0]:
            return PanicSeverity.MODERATE
        elif score >= self.SEVERITY_THRESHOLDS["mild"][0]:
            return PanicSeverity.MILD
        else:
            return PanicSeverity.NONE
    
    def _infer_triggers(
        self,
        text_analysis: TextAnalysisResult,
    ) -> list[PanicTrigger]:
        """
        Infer potential triggers from text analysis.
        
        CLINICAL_REVIEW_REQUIRED: Trigger inference patterns
        
        Args:
            text_analysis: Text analysis result
            
        Returns:
            List of suggested trigger categories
        """
        triggers = []
        text_lower = text_analysis.normalized_text.lower()
        
        # Pattern-based trigger inference
        trigger_patterns = {
            PanicTrigger.HEALTH_ANXIETY: [
                "heart", "disease", "cancer", "sick", "dying",
                "symptoms", "medical", "doctor",
            ],
            PanicTrigger.SOCIAL: [
                "people", "crowd", "meeting", "presentation",
                "judging", "embarrass", "public",
            ],
            PanicTrigger.WORK_STRESS: [
                "work", "job", "boss", "deadline", "fired",
                "project", "office", "career",
            ],
            PanicTrigger.RELATIONSHIP: [
                "partner", "relationship", "breakup", "divorce",
                "love", "marriage", "boyfriend", "girlfriend",
            ],
            PanicTrigger.FINANCIAL: [
                "money", "debt", "bills", "afford", "rent",
                "mortgage", "bankrupt", "poor",
            ],
            PanicTrigger.CROWDED_SPACE: [
                "crowded", "trapped", "enclosed", "elevator",
                "subway", "airplane", "claustrophob",
            ],
        }
        
        for trigger, patterns in trigger_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                triggers.append(trigger)
        
        # Default to unknown if none found
        if not triggers and text_analysis.risk_score > 0.2:
            triggers.append(PanicTrigger.UNKNOWN)
        
        return triggers
    
    def create_panic_event(
        self,
        detection_result: DetectionResult,
        user_id: UUID,
        session_id: Optional[UUID] = None,
    ) -> PanicEvent:
        """
        Create a PanicEvent from detection result.
        
        Convenience method for creating domain event from detection.
        
        Args:
            detection_result: Detection result
            user_id: User ID
            session_id: Optional session ID
            
        Returns:
            PanicEvent domain object
        """
        return PanicEvent(
            user_id=user_id,
            session_id=session_id,
            severity=detection_result.severity,
            urgency=detection_result.urgency,
            confidence_score=detection_result.confidence,
            triggers=detection_result.suggested_triggers,
            symptoms_reported=[],  # To be filled from user input
            escalated=detection_result.requires_escalation,
        )
