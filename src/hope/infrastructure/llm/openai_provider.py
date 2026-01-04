"""
OpenAI LLM Provider

Implementation of the LLM provider interface for OpenAI API.
Includes rate limiting, retries, and error handling.
"""

import time
from typing import Optional

from openai import AsyncOpenAI, APIError, RateLimitError as OpenAIRateLimitError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from hope.config import get_settings
from hope.config.logging_config import get_logger
from hope.infrastructure.llm.provider import (
    LLMProvider,
    LLMResponse,
    LLMProviderError,
    RateLimitError,
    ContentFilterError,
)
from hope.services.prompt.prompt_builder import BuiltPrompt

logger = get_logger(__name__)


class OpenAIProvider(LLMProvider):
    """
    OpenAI API provider implementation.
    
    Supports GPT-4 and GPT-3.5-turbo models with:
    - Async operation
    - Automatic retries with exponential backoff
    - Rate limit handling
    - Content filter detection
    
    Usage:
        provider = OpenAIProvider()
        response = await provider.generate(prompt)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> None:
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to settings)
            model: Model identifier (defaults to settings)
            max_tokens: Default max tokens
            temperature: Default temperature
        """
        settings = get_settings()
        
        self._api_key = api_key or settings.openai.api_key.get_secret_value()
        self._default_model = model or settings.openai.model
        self._default_max_tokens = max_tokens or settings.openai.max_tokens
        self._default_temperature = temperature or settings.openai.temperature
        
        self._client: Optional[AsyncOpenAI] = None
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    @property
    def default_model(self) -> str:
        return self._default_model
    
    def is_configured(self) -> bool:
        """Check if API key is configured."""
        return bool(self._api_key and self._api_key != "sk-CHANGE_ME")
    
    def _get_client(self) -> AsyncOpenAI:
        """Get or create async client."""
        if self._client is None:
            self._client = AsyncOpenAI(api_key=self._api_key)
        return self._client
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((OpenAIRateLimitError, APIError)),
    )
    async def generate(
        self,
        prompt: BuiltPrompt,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """
        Generate completion using OpenAI API.
        
        Args:
            prompt: Built prompt
            model: Model override
            max_tokens: Max tokens override
            temperature: Temperature override
            
        Returns:
            LLMResponse with generated content
        """
        if not self.is_configured():
            raise LLMProviderError(
                "OpenAI API key not configured",
                provider=self.provider_name,
            )
        
        client = self._get_client()
        messages = prompt.to_messages()
        model_name = model or self._default_model
        
        start_time = time.time()
        
        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens or prompt.max_tokens or self._default_max_tokens,
                temperature=temperature or prompt.temperature or self._default_temperature,
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract response
            choice = response.choices[0]
            content = choice.message.content or ""
            finish_reason = choice.finish_reason or "stop"
            
            # Check for content filter
            if finish_reason == "content_filter":
                raise ContentFilterError(
                    provider=self.provider_name,
                    filter_reason="Content was filtered by OpenAI safety systems",
                )
            
            usage = {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            }
            
            logger.debug(
                "OpenAI completion generated",
                model=model_name,
                tokens=usage.get("total_tokens"),
                latency_ms=latency_ms,
            )
            
            return LLMResponse(
                content=content,
                finish_reason=finish_reason,
                usage=usage,
                model=model_name,
                provider=self.provider_name,
                latency_ms=latency_ms,
                raw_response=response,
            )
            
        except OpenAIRateLimitError as e:
            logger.warning("OpenAI rate limit hit", error=str(e))
            raise RateLimitError(
                provider=self.provider_name,
                retry_after_seconds=60,
            )
            
        except APIError as e:
            logger.error("OpenAI API error", error=str(e))
            raise LLMProviderError(
                f"OpenAI API error: {str(e)}",
                provider=self.provider_name,
                is_retryable=True,
                original_error=e,
            )
            
        except Exception as e:
            logger.error("Unexpected OpenAI error", error=str(e))
            raise LLMProviderError(
                f"Unexpected error: {str(e)}",
                provider=self.provider_name,
                original_error=e,
            )
    
    async def health_check(self) -> bool:
        """Check OpenAI API availability."""
        if not self.is_configured():
            return False
        
        try:
            client = self._get_client()
            # Simple models list call to verify connectivity
            await client.models.list()
            return True
        except Exception as e:
            logger.warning("OpenAI health check failed", error=str(e))
            return False
