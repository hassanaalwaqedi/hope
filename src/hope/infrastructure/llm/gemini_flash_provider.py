"""
Google Gemini Flash LLM Provider

Optimized for speed and real-time panic mode interactions.
Uses Gemini Flash model for low-latency responses.

ARCHITECTURE: Implements the same LLMProvider interface.
Swap between providers via configuration only.
"""

import time
from typing import Optional

import google.generativeai as genai
from google.generativeai.types import GenerationConfig, HarmCategory, HarmBlockThreshold
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


class GeminiFlashProvider(LLMProvider):
    """
    Google Gemini Flash provider optimized for real-time panic support.
    
    Key optimizations:
    - Uses Gemini 1.5 Flash for lowest latency
    - Configured for mental health safety context
    - Supports Arabic and English multilingual input
    - Lower temperature for consistent, calm responses
    
    Usage:
        provider = GeminiFlashProvider()
        response = await provider.generate(prompt)
    """
    
    # Default model - Gemini Flash for speed
    DEFAULT_MODEL = "gemini-1.5-flash"
    
    # Lower temperature for panic mode - more consistent, calming responses
    DEFAULT_TEMPERATURE = 0.4
    
    # Shorter max tokens for quick responses
    DEFAULT_MAX_TOKENS = 512
    
    # Safety settings optimized for mental health context
    # Lower thresholds for dangerous content to allow safety-related discussions
    SAFETY_SETTINGS = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        """
        Initialize Gemini Flash provider.
        
        Args:
            api_key: Gemini API key (defaults to env HOPE_GEMINI_API_KEY)
            model: Model identifier (defaults to gemini-1.5-flash)
        """
        settings = get_settings()
        
        self._api_key = api_key or settings.gemini.api_key.get_secret_value()
        self._default_model = model or self.DEFAULT_MODEL
        self._configured = False
        self._model_instance: Optional[genai.GenerativeModel] = None
        
        if self._api_key and self._api_key != "CHANGE_ME":
            genai.configure(api_key=self._api_key)
            self._configured = True
            self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Pre-initialize model to reduce first-request latency."""
        try:
            self._model_instance = genai.GenerativeModel(
                model_name=self._default_model,
                safety_settings=self.SAFETY_SETTINGS,
                system_instruction=self._get_system_instruction(),
            )
            logger.info(
                "Gemini Flash model initialized",
                model=self._default_model,
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Flash: {e}")
    
    def _get_system_instruction(self) -> str:
        """
        Get base system instruction for panic support.
        
        This is embedded in the model to reduce per-request overhead.
        Additional context is added per-request.
        """
        return """You are HOPE, a compassionate AI companion providing support during moments of anxiety and panic.

Core principles:
- You are NOT a medical professional and never claim to be
- Keep responses short, calm, and grounding
- One clear instruction at a time
- Validate feelings without diagnosing
- Guide toward breathing and grounding when appropriate
- Always defer to professional help for serious concerns
- Support both Arabic and English speakers naturally

Response style:
- Use simple, clear language
- Avoid long paragraphs
- Be warm but direct
- No questions unless necessary"""
    
    @property
    def provider_name(self) -> str:
        return "gemini_flash"
    
    @property
    def default_model(self) -> str:
        return self._default_model
    
    def is_configured(self) -> bool:
        return self._configured
    
    @retry(
        stop=stop_after_attempt(2),  # Fewer retries for speed
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
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
        Generate completion using Gemini Flash.
        
        Optimized for low-latency panic support responses.
        
        Args:
            prompt: Built prompt with system and user messages
            model: Model override (defaults to gemini-1.5-flash)
            max_tokens: Max tokens (defaults to 512 for quick responses)
            temperature: Temperature (defaults to 0.4 for consistency)
            
        Returns:
            LLMResponse with generated content
        """
        if not self.is_configured():
            raise LLMProviderError(
                "Gemini API key not configured",
                provider=self.provider_name,
            )
        
        model_name = model or self._default_model
        
        # Use pre-initialized model or create new one
        if self._model_instance and model_name == self._default_model:
            gemini_model = self._model_instance
        else:
            gemini_model = genai.GenerativeModel(
                model_name=model_name,
                safety_settings=self.SAFETY_SETTINGS,
            )
        
        # Build the prompt content
        # Gemini Flash supports system instructions natively
        user_content = self._build_user_content(prompt)
        
        start_time = time.time()
        
        try:
            # Generation config optimized for panic mode
            generation_config = GenerationConfig(
                max_output_tokens=max_tokens or prompt.max_tokens or self.DEFAULT_MAX_TOKENS,
                temperature=temperature or prompt.temperature or self.DEFAULT_TEMPERATURE,
            )
            
            # Use generate_content_async for proper async support
            response = await gemini_model.generate_content_async(
                user_content,
                generation_config=generation_config,
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Check for blocked content
            if response.prompt_feedback:
                block_reason = getattr(response.prompt_feedback, 'block_reason', None)
                if block_reason:
                    logger.warning(
                        "Gemini content blocked",
                        reason=str(block_reason),
                    )
                    raise ContentFilterError(
                        provider=self.provider_name,
                        filter_reason=str(block_reason),
                    )
            
            # Extract content
            content = ""
            if response.candidates:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    content = candidate.content.parts[0].text or ""
                
                # Check finish reason
                finish_reason = str(getattr(candidate, 'finish_reason', 'STOP'))
                if 'SAFETY' in finish_reason:
                    raise ContentFilterError(
                        provider=self.provider_name,
                        filter_reason="Response blocked by safety filters",
                    )
            
            # Estimate token usage
            usage = self._estimate_usage(user_content, content)
            
            logger.debug(
                "Gemini Flash response generated",
                model=model_name,
                latency_ms=latency_ms,
                content_length=len(content),
            )
            
            return LLMResponse(
                content=content,
                finish_reason="stop",
                usage=usage,
                model=model_name,
                provider=self.provider_name,
                latency_ms=latency_ms,
                raw_response=response,
            )
            
        except ContentFilterError:
            raise
        except Exception as e:
            self._handle_error(e)
    
    def _build_user_content(self, prompt: BuiltPrompt) -> str:
        """Build user content from prompt."""
        parts = []
        
        # Add context if present
        if prompt.user_context:
            parts.append(f"Context: {prompt.user_context}")
        
        # Add any modifiers
        if prompt.modifiers:
            modifier_text = " ".join([f"[{m}]" for m in prompt.modifiers])
            parts.append(f"Response modifiers: {modifier_text}")
        
        # Add the main user message
        parts.append(prompt.user_message)
        
        return "\n\n".join(parts)
    
    def _estimate_usage(self, input_text: str, output_text: str) -> dict:
        """Estimate token usage (Gemini doesn't provide exact counts)."""
        # Rough estimate: ~1.3 tokens per word
        input_tokens = int(len(input_text.split()) * 1.3)
        output_tokens = int(len(output_text.split()) * 1.3)
        
        return {
            "prompt_tokens": input_tokens,
            "completion_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        }
    
    def _handle_error(self, error: Exception) -> None:
        """Handle and re-raise appropriate error type."""
        error_msg = str(error).lower()
        
        if "quota" in error_msg or "rate" in error_msg or "429" in error_msg:
            logger.warning("Gemini Flash rate limit", error=str(error))
            raise RateLimitError(
                provider=self.provider_name,
                retry_after_seconds=30,  # Shorter wait for Flash tier
            )
        
        if "safety" in error_msg or "blocked" in error_msg:
            raise ContentFilterError(
                provider=self.provider_name,
                filter_reason=str(error),
            )
        
        logger.error("Gemini Flash API error", error=str(error))
        raise LLMProviderError(
            f"Gemini Flash error: {str(error)}",
            provider=self.provider_name,
            is_retryable=True,
            original_error=error,
        )
    
    async def health_check(self) -> bool:
        """Check Gemini Flash availability."""
        if not self.is_configured():
            return False
        
        try:
            # Quick check by listing models
            models = list(genai.list_models())
            flash_available = any("flash" in m.name.lower() for m in models)
            return flash_available
        except Exception as e:
            logger.warning("Gemini Flash health check failed", error=str(e))
            return False
