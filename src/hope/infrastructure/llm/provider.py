"""
LLM Provider Abstract Interface

Defines the contract for all LLM provider implementations.
Enables swapping between providers without changing service code.

ARCHITECTURE: All LLM interactions go through this interface.
This allows future migration to self-hosted models (LLaMA).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from hope.services.prompt.prompt_builder import BuiltPrompt


@dataclass
class LLMResponse:
    """
    Response from LLM provider.
    
    Attributes:
        content: Generated text response
        finish_reason: Why generation stopped
        usage: Token usage statistics
        model: Model identifier used
        provider: Provider name
        latency_ms: Response time in milliseconds
        raw_response: Original API response (for debugging)
    """
    
    content: str
    finish_reason: str = "stop"
    usage: dict = field(default_factory=dict)
    model: str = ""
    provider: str = ""
    latency_ms: int = 0
    raw_response: Optional[Any] = None
    
    @property
    def total_tokens(self) -> int:
        """Get total tokens used."""
        return self.usage.get("total_tokens", 0)
    
    @property
    def input_tokens(self) -> int:
        """Get prompt tokens used."""
        return self.usage.get("prompt_tokens", 0)
    
    @property
    def output_tokens(self) -> int:
        """Get completion tokens used."""
        return self.usage.get("completion_tokens", 0)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary (excluding raw_response)."""
        return {
            "content": self.content,
            "finish_reason": self.finish_reason,
            "usage": self.usage,
            "model": self.model,
            "provider": self.provider,
            "latency_ms": self.latency_ms,
        }


class LLMProvider(ABC):
    """
    Abstract LLM provider interface.
    
    All LLM providers must implement this interface to be
    usable by the HOPE system.
    
    Required capabilities:
    - Async completion generation
    - Error handling with fallbacks
    - Rate limiting awareness
    - Usage tracking
    
    ARCHITECTURE: This abstraction enables:
    1. Easy provider switching (OpenAI <-> Gemini)
    2. Future self-hosted model support (LLaMA)
    3. A/B testing between providers
    4. Fallback chains for reliability
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get provider name for logging/tracking."""
        pass
    
    @property
    @abstractmethod
    def default_model(self) -> str:
        """Get default model identifier."""
        pass
    
    @abstractmethod
    async def generate(
        self,
        prompt: BuiltPrompt,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """
        Generate completion from prompt.
        
        Args:
            prompt: Built prompt with system and user messages
            model: Optional model override
            max_tokens: Optional max tokens override
            temperature: Optional temperature override
            
        Returns:
            LLMResponse with generated content
            
        Raises:
            LLMProviderError: On provider-specific errors
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check provider availability.
        
        Returns:
            True if provider is available
        """
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """
        Check if provider is properly configured.
        
        Returns:
            True if API key and settings are configured
        """
        pass


class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    
    def __init__(
        self,
        message: str,
        provider: str,
        is_retryable: bool = False,
        original_error: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.is_retryable = is_retryable
        self.original_error = original_error


class RateLimitError(LLMProviderError):
    """Rate limit exceeded error."""
    
    def __init__(
        self,
        provider: str,
        retry_after_seconds: Optional[int] = None,
    ) -> None:
        super().__init__(
            f"Rate limit exceeded for {provider}",
            provider=provider,
            is_retryable=True,
        )
        self.retry_after_seconds = retry_after_seconds


class ContentFilterError(LLMProviderError):
    """Content was filtered by provider's safety systems."""
    
    def __init__(self, provider: str, filter_reason: str = "") -> None:
        super().__init__(
            f"Content filtered by {provider}: {filter_reason}",
            provider=provider,
            is_retryable=False,
        )
        self.filter_reason = filter_reason
