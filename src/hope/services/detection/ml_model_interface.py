"""
ML Model Interface

Abstract interface for ML model inference.
Supports HuggingFace Transformers and future custom models (LLaMA fine-tuned).

ARCHITECTURE: This interface allows swapping models without changing
service layer code. Critical for transitioning from external APIs
to self-hosted fine-tuned models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

import torch
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification


@dataclass
class ModelPrediction:
    """
    Prediction result from ML model.
    
    Attributes:
        label: Predicted class label
        confidence: Prediction confidence (0.0-1.0)
        probabilities: Class probability distribution
        embeddings: Optional embedding vector
        metadata: Additional model-specific data
    """
    
    label: str
    confidence: float
    probabilities: dict[str, float]
    embeddings: Optional[list[float]] = None
    metadata: dict[str, Any] = None
    
    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class MLModelInterface(ABC):
    """
    Abstract interface for ML model inference.
    
    Implement this interface for each model type (HuggingFace,
    custom PyTorch, ONNX, etc.) to enable model swapping.
    """
    
    @abstractmethod
    async def predict(self, text: str) -> ModelPrediction:
        """
        Run inference on input text.
        
        Args:
            text: Input text to classify
            
        Returns:
            ModelPrediction with label and confidence
        """
        pass
    
    @abstractmethod
    async def get_embeddings(self, text: str) -> list[float]:
        """
        Generate embeddings for input text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        pass
    
    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if model is loaded and ready."""
        pass
    
    @abstractmethod
    async def load(self) -> None:
        """Load model into memory."""
        pass
    
    @abstractmethod
    async def unload(self) -> None:
        """Unload model from memory."""
        pass


class HuggingFaceEmotionModel(MLModelInterface):
    """
    HuggingFace Transformers implementation for emotion detection.
    
    Uses distilbert-base-uncased-emotion or similar model
    for detecting emotional states in text.
    
    CLINICAL_REVIEW_REQUIRED: Model selection and threshold
    calibration should be validated against clinical benchmarks.
    """
    
    # Emotion to severity mapping
    EMOTION_SEVERITY_MAP: dict[str, tuple[str, float]] = {
        "fear": ("high_risk", 0.8),
        "anger": ("moderate_risk", 0.5),
        "sadness": ("moderate_risk", 0.5),
        "surprise": ("low_risk", 0.3),
        "joy": ("no_risk", 0.0),
        "love": ("no_risk", 0.0),
    }
    
    def __init__(
        self,
        model_name: str = "j-hartmann/emotion-english-distilroberta-base",
        device: Optional[str] = None,
    ) -> None:
        """
        Initialize emotion detection model.
        
        Args:
            model_name: HuggingFace model identifier
            device: Device to run on (cuda/cpu/auto)
        """
        self._model_name = model_name
        self._device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._model: Optional[AutoModelForSequenceClassification] = None
        self._tokenizer: Optional[AutoTokenizer] = None
        self._loaded = False
    
    async def load(self) -> None:
        """Load model and tokenizer."""
        if self._loaded:
            return
        
        self._tokenizer = AutoTokenizer.from_pretrained(self._model_name)
        self._model = AutoModelForSequenceClassification.from_pretrained(
            self._model_name
        ).to(self._device)
        self._model.eval()
        self._loaded = True
    
    async def unload(self) -> None:
        """Unload model from memory."""
        self._model = None
        self._tokenizer = None
        self._loaded = False
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._loaded and self._model is not None
    
    async def predict(self, text: str) -> ModelPrediction:
        """
        Predict emotion from text.
        
        Args:
            text: Input text
            
        Returns:
            ModelPrediction with emotion label and confidence
        """
        if not self.is_loaded():
            await self.load()
        
        # Tokenize input
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        ).to(self._device)
        
        # Run inference
        with torch.no_grad():
            outputs = self._model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Get prediction
        probs = probabilities[0].cpu().numpy()
        predicted_idx = probs.argmax()
        labels = self._model.config.id2label
        
        # Build probability distribution
        prob_dict = {
            labels[i]: float(probs[i])
            for i in range(len(labels))
        }
        
        predicted_label = labels[predicted_idx]
        confidence = float(probs[predicted_idx])
        
        # Map to risk level
        risk_info = self.EMOTION_SEVERITY_MAP.get(
            predicted_label.lower(),
            ("unknown", 0.5)
        )
        
        return ModelPrediction(
            label=predicted_label,
            confidence=confidence,
            probabilities=prob_dict,
            metadata={
                "risk_level": risk_info[0],
                "severity_weight": risk_info[1],
                "model": self._model_name,
            },
        )
    
    async def get_embeddings(self, text: str) -> list[float]:
        """
        Generate embeddings using model's hidden states.
        
        This is a simplified implementation. For production,
        use sentence-transformers for better embeddings.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        if not self.is_loaded():
            await self.load()
        
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        ).to(self._device)
        
        with torch.no_grad():
            outputs = self._model(**inputs, output_hidden_states=True)
            # Use last hidden state, mean pooling
            hidden_states = outputs.hidden_states[-1]
            embeddings = hidden_states.mean(dim=1).squeeze()
        
        return embeddings.cpu().numpy().tolist()


class SentenceEmbeddingModel(MLModelInterface):
    """
    Sentence-Transformers model for generating high-quality embeddings.
    
    Used for vector database storage and similarity search.
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ) -> None:
        """
        Initialize sentence embedding model.
        
        Args:
            model_name: Sentence-Transformers model name
        """
        self._model_name = model_name
        self._model = None
        self._loaded = False
    
    async def load(self) -> None:
        """Load sentence-transformers model."""
        if self._loaded:
            return
        
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(self._model_name)
        self._loaded = True
    
    async def unload(self) -> None:
        """Unload model."""
        self._model = None
        self._loaded = False
    
    def is_loaded(self) -> bool:
        """Check if loaded."""
        return self._loaded and self._model is not None
    
    async def predict(self, text: str) -> ModelPrediction:
        """
        Not applicable for embedding models.
        Returns placeholder prediction.
        """
        embeddings = await self.get_embeddings(text)
        return ModelPrediction(
            label="embedding",
            confidence=1.0,
            probabilities={},
            embeddings=embeddings,
        )
    
    async def get_embeddings(self, text: str) -> list[float]:
        """
        Generate sentence embeddings.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector (384 dimensions for all-MiniLM-L6-v2)
        """
        if not self.is_loaded():
            await self.load()
        
        embeddings = self._model.encode(text, convert_to_numpy=True)
        return embeddings.tolist()
