"""
MLOps Model Registry

Model versioning, performance tracking, and input/output logging.
Foundation for ML lifecycle management.

PRIVACY: All input/output sampling is configurable and privacy-safe.
No raw user messages are logged without explicit consent.
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from hope.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ModelVersion:
    """Model version metadata."""
    
    model_id: str
    version: str
    name: str
    provider: str  # gemini_flash, openai, local
    created_at: datetime
    config: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "version": self.version,
            "name": self.name,
            "provider": self.provider,
            "created_at": self.created_at.isoformat(),
            "config": self.config,
            "metrics": self.metrics,
        }


@dataclass
class PredictionLog:
    """Privacy-safe prediction log entry."""
    
    log_id: str
    model_id: str
    timestamp: datetime
    latency_ms: int
    input_hash: str  # Hash of input, not raw input
    input_length: int
    output_length: int
    tokens_used: int
    success: bool
    error_type: Optional[str] = None
    
    # Optional sampled data (only with consent)
    sampled_input: Optional[str] = None
    sampled_output: Optional[str] = None


class ModelRegistry:
    """
    Model version registry and performance tracker.
    
    Features:
    - Model versioning
    - Performance metrics
    - Privacy-safe logging
    - Sampling for quality monitoring
    """
    
    def __init__(
        self,
        sample_rate: float = 0.01,  # 1% sampling
        enable_sampling: bool = False,  # Disabled by default for privacy
    ) -> None:
        self._models: dict[str, ModelVersion] = {}
        self._predictions: list[PredictionLog] = []
        self._sample_rate = sample_rate
        self._enable_sampling = enable_sampling
        self._metrics_buffer: list[dict] = []
        
        # Performance aggregates
        self._request_counts: dict[str, int] = {}
        self._latency_sums: dict[str, float] = {}
        self._error_counts: dict[str, int] = {}
    
    def register_model(
        self,
        name: str,
        version: str,
        provider: str,
        config: Optional[dict] = None,
    ) -> str:
        """
        Register a model version.
        
        Returns: Model ID
        """
        model_id = f"{name}:{version}"
        
        model = ModelVersion(
            model_id=model_id,
            version=version,
            name=name,
            provider=provider,
            created_at=datetime.utcnow(),
            config=config or {},
        )
        
        self._models[model_id] = model
        self._request_counts[model_id] = 0
        self._latency_sums[model_id] = 0.0
        self._error_counts[model_id] = 0
        
        logger.info(
            "Model registered",
            model_id=model_id,
            provider=provider,
        )
        
        return model_id
    
    def get_model(self, model_id: str) -> Optional[ModelVersion]:
        """Get model by ID."""
        return self._models.get(model_id)
    
    def list_models(self) -> list[ModelVersion]:
        """List all registered models."""
        return list(self._models.values())
    
    def log_prediction(
        self,
        model_id: str,
        input_text: str,
        output_text: str,
        latency_ms: int,
        tokens_used: int,
        success: bool = True,
        error_type: Optional[str] = None,
    ) -> str:
        """
        Log a prediction for monitoring.
        
        Privacy: Input is hashed, not stored raw.
        Sampling is configurable and off by default.
        
        Returns: Log ID
        """
        log_id = str(uuid4())
        
        # Hash input for privacy
        input_hash = hashlib.sha256(input_text.encode()).hexdigest()[:16]
        
        # Decide if we should sample
        should_sample = (
            self._enable_sampling and
            hash(log_id) % 100 < self._sample_rate * 100
        )
        
        log = PredictionLog(
            log_id=log_id,
            model_id=model_id,
            timestamp=datetime.utcnow(),
            latency_ms=latency_ms,
            input_hash=input_hash,
            input_length=len(input_text),
            output_length=len(output_text),
            tokens_used=tokens_used,
            success=success,
            error_type=error_type,
            sampled_input=input_text[:200] if should_sample else None,
            sampled_output=output_text[:500] if should_sample else None,
        )
        
        self._predictions.append(log)
        
        # Update aggregates
        if model_id in self._request_counts:
            self._request_counts[model_id] += 1
            self._latency_sums[model_id] += latency_ms
            if not success:
                self._error_counts[model_id] += 1
        
        # Trim buffer if too large
        if len(self._predictions) > 10000:
            self._predictions = self._predictions[-5000:]
        
        return log_id
    
    def get_model_metrics(self, model_id: str) -> dict:
        """
        Get performance metrics for a model.
        
        Returns aggregate statistics.
        """
        if model_id not in self._models:
            return {}
        
        request_count = self._request_counts.get(model_id, 0)
        if request_count == 0:
            return {
                "model_id": model_id,
                "request_count": 0,
            }
        
        latency_sum = self._latency_sums.get(model_id, 0)
        error_count = self._error_counts.get(model_id, 0)
        
        return {
            "model_id": model_id,
            "request_count": request_count,
            "avg_latency_ms": latency_sum / request_count,
            "error_count": error_count,
            "error_rate": error_count / request_count,
        }
    
    def get_recent_predictions(
        self,
        model_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        """
        Get recent prediction logs.
        
        Filtered by model if specified.
        """
        predictions = self._predictions
        
        if model_id:
            predictions = [p for p in predictions if p.model_id == model_id]
        
        # Return most recent
        recent = predictions[-limit:]
        
        return [
            {
                "log_id": p.log_id,
                "model_id": p.model_id,
                "timestamp": p.timestamp.isoformat(),
                "latency_ms": p.latency_ms,
                "input_length": p.input_length,
                "output_length": p.output_length,
                "tokens_used": p.tokens_used,
                "success": p.success,
                "error_type": p.error_type,
            }
            for p in recent
        ]
    
    def export_metrics(self) -> dict:
        """Export all metrics for external consumption."""
        return {
            "models": [m.to_dict() for m in self._models.values()],
            "metrics": {
                model_id: self.get_model_metrics(model_id)
                for model_id in self._models
            },
            "exported_at": datetime.utcnow().isoformat(),
        }


# Global registry instance
_registry: Optional[ModelRegistry] = None


def get_model_registry() -> ModelRegistry:
    """Get or create model registry."""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry


def init_model_registry(
    sample_rate: float = 0.01,
    enable_sampling: bool = False,
) -> ModelRegistry:
    """Initialize model registry with configuration."""
    global _registry
    _registry = ModelRegistry(
        sample_rate=sample_rate,
        enable_sampling=enable_sampling,
    )
    return _registry
