"""
Google Gemini LLM Provider

Implementation of the LLM provider interface for Google Gemini API.
"""

import time
from typing import Optional

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from tenacity import retry, stop_after_attempt, wait_exponential

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


class GeminiProvider(LLMProvider):
    """
    Google Gemini API provider implementation.
    
    Supports Gemini Pro and Gemini Pro Vision models with:
    - Async operation
    - Safety setting configuration
    - Content filter handling
    
    Usage:
        provider = GeminiProvider()
        response = await provider.generate(prompt)
    """
    
    # Safety settings for mental health context
    SAFETY_SETTINGS = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_ONLY_HIGH",  # Lower threshold for safety-related content
        },
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Gemini API key (defaults to settings)
            model: Model identifier (defaults to settings)
        """
        settings = get_settings()
        
        self._api_key = api_key or settings.gemini.api_key.get_secret_value()
        self._default_model = model or settings.gemini.model
        self._configured = False
        
        if self._api_key and self._api_key != "CHANGE_ME":
            genai.configure(api_key=self._api_key)
            self._configured = True
    
    @property
    def provider_name(self) -> str:
        return "gemini"
    
    @property
    def default_model(self) -> str:
        return self._default_model
    
    def is_configured(self) -> bool:
        return self._configured
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
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
        Generate completion using Gemini API.
        
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
                "Gemini API key not configured",
                provider=self.provider_name,
            )
        
        model_name = model or self._default_model
        
        # Create model instance
        gemini_model = genai.GenerativeModel(
            model_name=model_name,
            safety_settings=self.SAFETY_SETTINGS,
        )
        
        # Build conversation for Gemini
        # Gemini uses a different format than OpenAI
        system_prompt = prompt.system_prompt
        if prompt.user_context:
            system_prompt += f"\n\nContext: {prompt.user_context}"
        
        # Gemini handles system prompt differently
        chat = gemini_model.start_chat(history=[])
        
        # First, send system prompt as context (in user format)
        # This is a workaround since Gemini handles system prompts differently
        full_prompt = f"""System Instructions:
{system_prompt}

---

User message: {prompt.user_message}"""
        
        start_time = time.time()
        
        try:
            # Generate response
            generation_config = GenerationConfig(
                max_output_tokens=max_tokens or prompt.max_tokens,
                temperature=temperature or prompt.temperature,
            )
            
            response = await chat.send_message_async(
                full_prompt,
                generation_config=generation_config,
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Check for blocked content
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                raise ContentFilterError(
                    provider=self.provider_name,
                    filter_reason=str(response.prompt_feedback.block_reason),
                )
            
            content = response.text or ""
            
            # Gemini doesn't provide detailed usage like OpenAI
            # Estimate based on text length
            usage = {
                "prompt_tokens": len(full_prompt.split()) * 1.3,  # Rough estimate
                "completion_tokens": len(content.split()) * 1.3,
                "total_tokens": (len(full_prompt.split()) + len(content.split())) * 1.3,
            }
            
            logger.debug(
                "Gemini completion generated",
                model=model_name,
                latency_ms=latency_ms,
            )
            
            return LLMResponse(
                content=content,
                finish_reason="stop",
                usage={k: int(v) for k, v in usage.items()},
                model=model_name,
                provider=self.provider_name,
                latency_ms=latency_ms,
                raw_response=response,
            )
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if "quota" in error_msg or "rate" in error_msg:
                logger.warning("Gemini rate limit hit", error=str(e))
                raise RateLimitError(
                    provider=self.provider_name,
                    retry_after_seconds=60,
                )
            
            if "safety" in error_msg or "blocked" in error_msg:
                raise ContentFilterError(
                    provider=self.provider_name,
                    filter_reason=str(e),
                )
            
            logger.error("Gemini API error", error=str(e))
            raise LLMProviderError(
                f"Gemini API error: {str(e)}",
                provider=self.provider_name,
                original_error=e,
            )
    
    async def health_check(self) -> bool:
        """Check Gemini API availability."""
        if not self.is_configured():
            return False
        
        try:
            # List models to verify connectivity
            for _ in genai.list_models():
                break
            return True
        except Exception as e:
            logger.warning("Gemini health check failed", error=str(e))
            return False
