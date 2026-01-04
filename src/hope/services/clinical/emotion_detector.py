"""
Emotion Detector

Multi-label emotion classification for panic-relevant emotions.
Detects fear, dread, loss of control, dissociation, and more.

ARCHITECTURE: Pure ML component with no business logic.
Supports multilingual input (Arabic + English).

CLINICAL_VALIDATION_REQUIRED: Emotion categories and intensity
mapping need clinical validation.
"""

import asyncio
from dataclasses import dataclass
from typing import Optional

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from hope.domain.models.clinical_output import (
    EmotionCategory,
    EmotionScore,
    EmotionProfile,
)
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class EmotionDetectorConfig:
    """
    Configuration for emotion detector.
    """
    
    # Using multilingual emotion model
    # This model supports emotion classification in multiple languages
    model_name: str = "j-hartmann/emotion-english-distilroberta-base"
    
    # For Arabic-specific, would use Arabic-BERT based model
    # arabic_model_name: str = "CAMeL-Lab/bert-base-arabic-camelbert-msa-sentiment"
    
    # Map generic emotions to panic-relevant categories
    max_length: int = 256
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    version: str = "1.0.0"
    
    # Intensity thresholds
    # CLINICAL_VALIDATION_REQUIRED
    high_intensity_threshold: float = 0.7
    volatility_threshold: float = 0.5


class EmotionDetector:
    """
    Multi-label emotion detector for panic-relevant emotions.
    
    Detects and maps emotions to clinical categories:
    - Fear → FEAR
    - Anger → (contributes to volatility)
    - Disgust → (contributes to dissociation markers)
    - Sadness → HELPLESSNESS
    - Joy → (inverse indicator)
    - Surprise → HYPERVIGILANCE
    
    CLINICAL_VALIDATION_REQUIRED: Emotion-to-category mapping
    needs clinical validation for panic attack context.
    
    Usage:
        detector = EmotionDetector()
        await detector.load()
        profile = await detector.detect("I feel like I'm going to die")
    """
    
    # Mapping from generic emotions to panic-relevant categories
    # CLINICAL_VALIDATION_REQUIRED
    EMOTION_MAPPING: dict[str, list[EmotionCategory]] = {
        "fear": [EmotionCategory.FEAR, EmotionCategory.DREAD],
        "anger": [EmotionCategory.LOSS_OF_CONTROL],
        "disgust": [EmotionCategory.DISSOCIATION],
        "sadness": [EmotionCategory.HELPLESSNESS],
        "surprise": [EmotionCategory.HYPERVIGILANCE],
        "neutral": [],
        "joy": [],  # Inverse indicator - reduces concern
    }
    
    # Keywords that boost specific emotion detection
    # CLINICAL_VALIDATION_REQUIRED
    PANIC_EMOTION_KEYWORDS: dict[EmotionCategory, list[str]] = {
        EmotionCategory.FEAR: [
            "scared", "afraid", "terrified", "frightened",
            "خائف", "مرعوب", "خوف",  # Arabic: afraid, terrified, fear
        ],
        EmotionCategory.DREAD: [
            "doom", "dread", "die", "dying", "death",
            "something terrible", "impending",
            "موت", "هلاك",  # Arabic: death, doom
        ],
        EmotionCategory.LOSS_OF_CONTROL: [
            "can't control", "losing control", "out of control",
            "going crazy", "losing my mind", "insane",
            "فقدان السيطرة", "جنون",  # Arabic: loss of control, madness
        ],
        EmotionCategory.DISSOCIATION: [
            "unreal", "detached", "floating", "watching myself",
            "not real", "dream", "fog", "numb",
            "غير حقيقي", "منفصل",  # Arabic: unreal, detached
        ],
        EmotionCategory.HELPLESSNESS: [
            "can't cope", "helpless", "hopeless", "stuck",
            "no way out", "trapped",
            "عاجز", "يائس",  # Arabic: helpless, hopeless
        ],
        EmotionCategory.HYPERVIGILANCE: [
            "alert", "watching", "scanning", "on edge",
            "jumpy", "startled",
            "متيقظ", "حذر",  # Arabic: alert, cautious
        ],
    }
    
    def __init__(
        self,
        config: Optional[EmotionDetectorConfig] = None,
    ) -> None:
        """Initialize emotion detector."""
        self.config = config or EmotionDetectorConfig()
        self._tokenizer: Optional[AutoTokenizer] = None
        self._model: Optional[AutoModelForSequenceClassification] = None
        self._loaded = False
    
    async def load(self) -> None:
        """Load emotion detection model."""
        if self._loaded:
            return
        
        logger.info(
            "Loading emotion detector",
            model=self.config.model_name,
        )
        
        loop = asyncio.get_event_loop()
        
        def _load():
            tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
            model = AutoModelForSequenceClassification.from_pretrained(
                self.config.model_name
            )
            model.to(self.config.device)
            model.eval()
            return tokenizer, model
        
        self._tokenizer, self._model = await loop.run_in_executor(None, _load)
        self._loaded = True
        logger.info("Emotion detector loaded")
    
    async def unload(self) -> None:
        """Unload model."""
        self._tokenizer = None
        self._model = None
        self._loaded = False
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    async def detect(self, text: str) -> EmotionProfile:
        """
        Detect emotions in text.
        
        Args:
            text: Input text (Arabic or English)
            
        Returns:
            EmotionProfile with detected emotions
        """
        if not self._loaded:
            await self.load()
        
        if not text or not text.strip():
            return EmotionProfile()
        
        # Get base emotion predictions
        base_predictions = await self._get_base_predictions(text)
        
        # Map to panic-relevant categories
        panic_emotions = self._map_to_panic_emotions(
            base_predictions, text
        )
        
        # Calculate volatility
        volatility = self._calculate_volatility(base_predictions)
        
        # Build profile
        emotion_scores = [
            EmotionScore(
                category=category,
                confidence=score,
                intensity=self._estimate_intensity(score, text, category),
            )
            for category, score in panic_emotions.items()
            if score > 0.1  # Filter low-confidence
        ]
        
        # Sort by confidence
        emotion_scores.sort(key=lambda e: e.confidence, reverse=True)
        
        return EmotionProfile(
            emotions=emotion_scores,
            emotional_volatility=volatility,
        )
    
    async def _get_base_predictions(
        self, text: str
    ) -> dict[str, float]:
        """Get predictions from base emotion model."""
        loop = asyncio.get_event_loop()
        
        def _inference():
            inputs = self._tokenizer(
                text,
                max_length=self.config.max_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )
            inputs = {k: v.to(self.config.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self._model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)
            
            return probs.cpu().numpy()[0]
        
        probs = await loop.run_in_executor(None, _inference)
        
        # Get label names from model config
        id2label = self._model.config.id2label
        
        return {
            id2label[i].lower(): float(probs[i])
            for i in range(len(probs))
        }
    
    def _map_to_panic_emotions(
        self,
        base_predictions: dict[str, float],
        text: str,
    ) -> dict[EmotionCategory, float]:
        """
        Map base emotions to panic-relevant categories.
        
        Combines model predictions with keyword analysis
        for more accurate panic-specific detection.
        """
        panic_scores: dict[EmotionCategory, float] = {
            category: 0.0 for category in EmotionCategory
        }
        
        # Apply base emotion mapping
        for base_emotion, score in base_predictions.items():
            mapped_categories = self.EMOTION_MAPPING.get(base_emotion, [])
            for category in mapped_categories:
                # Take max if multiple sources
                panic_scores[category] = max(
                    panic_scores[category],
                    score
                )
        
        # Boost with keyword detection
        text_lower = text.lower()
        for category, keywords in self.PANIC_EMOTION_KEYWORDS.items():
            keyword_found = any(kw in text_lower for kw in keywords)
            if keyword_found:
                # Boost existing score or set minimum
                current = panic_scores[category]
                panic_scores[category] = max(current + 0.2, 0.5)
        
        # Normalize to [0, 1]
        max_score = max(panic_scores.values()) if panic_scores else 1.0
        if max_score > 1.0:
            panic_scores = {
                k: v / max_score for k, v in panic_scores.items()
            }
        
        return panic_scores
    
    def _estimate_intensity(
        self,
        confidence: float,
        text: str,
        category: EmotionCategory,
    ) -> float:
        """
        Estimate emotional intensity.
        
        Considers confidence, text intensity markers,
        and category-specific patterns.
        
        CLINICAL_VALIDATION_REQUIRED: Intensity estimation
        methodology needs clinical validation.
        """
        base_intensity = confidence
        
        # Intensity markers
        intensity_markers = [
            "extremely", "very", "so", "really", "incredibly",
            "terribly", "absolutely", "completely", "totally",
            "جداً", "للغاية",  # Arabic: very, extremely
        ]
        
        text_lower = text.lower()
        
        # Boost for intensity markers
        if any(marker in text_lower for marker in intensity_markers):
            base_intensity = min(1.0, base_intensity * 1.3)
        
        # Boost for exclamation marks (urgency indicator)
        exclamation_count = text.count("!")
        if exclamation_count > 0:
            base_intensity = min(1.0, base_intensity + 0.05 * exclamation_count)
        
        # Boost for ALL CAPS
        words = text.split()
        caps_ratio = sum(1 for w in words if w.isupper()) / max(len(words), 1)
        if caps_ratio > 0.3:
            base_intensity = min(1.0, base_intensity * 1.2)
        
        return min(1.0, base_intensity)
    
    def _calculate_volatility(
        self,
        base_predictions: dict[str, float],
    ) -> float:
        """
        Calculate emotional volatility.
        
        High volatility indicates unstable emotional state,
        common during panic attacks.
        
        Returns:
            Volatility score (0.0-1.0)
        """
        scores = list(base_predictions.values())
        if not scores:
            return 0.0
        
        # Volatility = variance of emotion scores
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        
        # Normalize to [0, 1] range
        # Max variance for uniform [0,1] is 0.25
        volatility = min(1.0, variance * 4)
        
        return volatility
    
    def is_loaded(self) -> bool:
        return self._loaded
