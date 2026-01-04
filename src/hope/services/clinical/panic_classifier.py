"""
Panic Severity Classifier

ML-based panic severity classification using transformer embeddings.
Produces probabilistic outputs, not binary classifications.

ARCHITECTURE: This is a pure ML component with no business logic.
All thresholds and interpretations happen in the clinical pipeline.

CLINICAL_VALIDATION_REQUIRED: Model training data and severity
boundaries require clinical dataset and psychologist validation.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Optional

import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel

from hope.domain.enums.panic_severity import PanicSeverity
from hope.domain.models.clinical_output import SeverityClassification
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ClassifierConfig:
    """
    Configuration for the panic severity classifier.
    
    CLINICAL_VALIDATION_REQUIRED: Model selection and
    hyperparameters should be validated on clinical data.
    """
    
    # Base model for embeddings
    # Using XLM-RoBERTa for multilingual support (Arabic + English)
    model_name: str = "xlm-roberta-base"
    
    # Number of severity classes (matches PanicSeverity enum)
    num_classes: int = 5
    
    # Classification head configuration
    hidden_size: int = 768  # XLM-RoBERTa base hidden size
    dropout_rate: float = 0.3
    
    # Inference settings
    max_length: int = 256
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Model version for tracking
    version: str = "1.0.0"


class SeverityClassificationHead(nn.Module):
    """
    Classification head for severity prediction.
    
    Takes transformer embeddings and produces class probabilities.
    
    Architecture:
    - Dropout for regularization
    - Linear projection to class logits
    - Softmax for probabilities
    """
    
    def __init__(self, config: ClassifierConfig) -> None:
        super().__init__()
        
        self.dropout = nn.Dropout(config.dropout_rate)
        self.classifier = nn.Linear(config.hidden_size, config.num_classes)
    
    def forward(self, pooled_output: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            pooled_output: Pooled transformer output [batch, hidden_size]
            
        Returns:
            logits: Class logits [batch, num_classes]
        """
        x = self.dropout(pooled_output)
        logits = self.classifier(x)
        return logits


class PanicSeverityClassifier:
    """
    Transformer-based panic severity classifier.
    
    Uses XLM-RoBERTa for multilingual support and a custom
    classification head for severity prediction.
    
    Outputs:
    - Predicted severity class
    - Probability distribution over all classes
    - Confidence score
    - Uncertainty flags
    
    Usage:
        classifier = PanicSeverityClassifier()
        await classifier.load()
        result = await classifier.predict("I'm having a panic attack")
    
    ARCHITECTURE: This is a stateless ML component. It receives
    text and returns structured predictions. No session state.
    """
    
    # Severity class mapping
    SEVERITY_CLASSES: list[PanicSeverity] = [
        PanicSeverity.NONE,
        PanicSeverity.MILD,
        PanicSeverity.MODERATE,
        PanicSeverity.SEVERE,
        PanicSeverity.CRITICAL,
    ]
    
    def __init__(
        self,
        config: Optional[ClassifierConfig] = None,
    ) -> None:
        """
        Initialize classifier.
        
        Args:
            config: Classifier configuration
        """
        self.config = config or ClassifierConfig()
        self._tokenizer: Optional[AutoTokenizer] = None
        self._base_model: Optional[AutoModel] = None
        self._classifier_head: Optional[SeverityClassificationHead] = None
        self._loaded = False
    
    async def load(self) -> None:
        """
        Load model components.
        
        Should be called during application startup.
        """
        if self._loaded:
            return
        
        logger.info(
            "Loading panic severity classifier",
            model=self.config.model_name,
            device=self.config.device,
        )
        
        # Load tokenizer and base model in thread pool
        loop = asyncio.get_event_loop()
        
        def _load_models():
            tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
            base_model = AutoModel.from_pretrained(self.config.model_name)
            base_model.to(self.config.device)
            base_model.eval()
            return tokenizer, base_model
        
        self._tokenizer, self._base_model = await loop.run_in_executor(
            None, _load_models
        )
        
        # Initialize classification head
        self._classifier_head = SeverityClassificationHead(self.config)
        self._classifier_head.to(self.config.device)
        self._classifier_head.eval()
        
        # NOTE: In production, load pre-trained weights here
        # self._classifier_head.load_state_dict(torch.load("path/to/weights.pt"))
        # CLINICAL_VALIDATION_REQUIRED: Weights must be trained on clinical data
        
        self._loaded = True
        logger.info("Panic severity classifier loaded")
    
    async def unload(self) -> None:
        """Unload model to free memory."""
        self._tokenizer = None
        self._base_model = None
        self._classifier_head = None
        self._loaded = False
        
        # Clear CUDA cache if using GPU
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    async def predict(self, text: str) -> SeverityClassification:
        """
        Predict panic severity from text.
        
        Args:
            text: Input text (Arabic or English)
            
        Returns:
            SeverityClassification with probabilities
        """
        if not self._loaded:
            await self.load()
        
        if not text or not text.strip():
            return SeverityClassification(
                predicted_severity=PanicSeverity.NONE,
                probabilities={s: 0.0 for s in self.SEVERITY_CLASSES},
                confidence=1.0,
                model_version=self.config.version,
            )
        
        # Get embeddings and classify
        loop = asyncio.get_event_loop()
        
        def _inference():
            # Tokenize
            inputs = self._tokenizer(
                text,
                max_length=self.config.max_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )
            inputs = {k: v.to(self.config.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                # Get base model outputs
                outputs = self._base_model(**inputs)
                
                # Use [CLS] token (first token) as pooled representation
                pooled = outputs.last_hidden_state[:, 0, :]
                
                # Get classification logits
                logits = self._classifier_head(pooled)
                
                # Apply softmax for probabilities
                probs = torch.softmax(logits, dim=-1)
                
            return probs.cpu().numpy()[0]
        
        probs = await loop.run_in_executor(None, _inference)
        
        # Build probability dictionary
        probabilities = {
            severity: float(probs[i])
            for i, severity in enumerate(self.SEVERITY_CLASSES)
        }
        
        # Get predicted class
        predicted_idx = probs.argmax()
        predicted_severity = self.SEVERITY_CLASSES[predicted_idx]
        confidence = float(probs[predicted_idx])
        
        result = SeverityClassification(
            predicted_severity=predicted_severity,
            probabilities=probabilities,
            confidence=confidence,
            model_version=self.config.version,
        )
        
        logger.debug(
            "Severity prediction",
            predicted=predicted_severity.name,
            confidence=round(confidence, 3),
            uncertainty=result.uncertainty_flag,
        )
        
        return result
    
    async def predict_batch(
        self,
        texts: list[str],
    ) -> list[SeverityClassification]:
        """
        Predict severity for multiple texts.
        
        More efficient than individual predictions.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of classifications
        """
        if not self._loaded:
            await self.load()
        
        if not texts:
            return []
        
        loop = asyncio.get_event_loop()
        
        def _batch_inference():
            # Tokenize all texts
            inputs = self._tokenizer(
                texts,
                max_length=self.config.max_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )
            inputs = {k: v.to(self.config.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self._base_model(**inputs)
                pooled = outputs.last_hidden_state[:, 0, :]
                logits = self._classifier_head(pooled)
                probs = torch.softmax(logits, dim=-1)
                
            return probs.cpu().numpy()
        
        all_probs = await loop.run_in_executor(None, _batch_inference)
        
        results = []
        for probs in all_probs:
            probabilities = {
                severity: float(probs[i])
                for i, severity in enumerate(self.SEVERITY_CLASSES)
            }
            predicted_idx = probs.argmax()
            predicted_severity = self.SEVERITY_CLASSES[predicted_idx]
            confidence = float(probs[predicted_idx])
            
            results.append(SeverityClassification(
                predicted_severity=predicted_severity,
                probabilities=probabilities,
                confidence=confidence,
                model_version=self.config.version,
            ))
        
        return results
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._loaded
    
    def get_model_info(self) -> dict:
        """Get model information for debugging."""
        return {
            "model_name": self.config.model_name,
            "version": self.config.version,
            "device": self.config.device,
            "loaded": self._loaded,
            "num_classes": self.config.num_classes,
        }
