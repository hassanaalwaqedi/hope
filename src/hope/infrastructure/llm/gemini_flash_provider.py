"""
Google Gemini Flash LLM Provider

Optimized for speed and real-time panic mode interactions.
Uses Gemini Flash model for low-latency responses.
Supports multimodal input (text + images) for vision analysis.

ARCHITECTURE: Implements the same LLMProvider interface.
Swap between providers via configuration only.
"""

import base64
import time
from dataclasses import dataclass, field
from typing import Optional, Union
from enum import Enum

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


class SafetyFlag(Enum):
    """Safety flags for AI responses in mental health context."""
    SAFE = "safe"
    CRISIS_DETECTED = "crisis_detected"
    SELF_HARM_RISK = "self_harm_risk"
    REQUIRES_ESCALATION = "requires_escalation"
    UNCLEAR_IMAGE = "unclear_image"
    MEDICAL_CONTENT = "medical_content"


@dataclass
class MultimodalResponse:
    """
    Response from multimodal (text + image) Gemini call.
    
    Attributes:
        text_answer: The AI-generated text response
        safety_flags: List of safety concerns detected
        confidence_score: Confidence in the response (0.0-1.0)
        image_description: Description of analyzed image if present
        escalated: Whether response triggered crisis escalation
        latency_ms: Response time in milliseconds
        model: Model used for generation
    """
    text_answer: str
    safety_flags: list[SafetyFlag] = field(default_factory=list)
    confidence_score: float = 0.85
    image_description: Optional[str] = None
    escalated: bool = False
    latency_ms: int = 0
    model: str = ""
    
    def to_dict(self) -> dict:
        return {
            "text_answer": self.text_answer,
            "safety_flags": [f.value for f in self.safety_flags],
            "confidence_score": self.confidence_score,
            "image_description": self.image_description,
            "escalated": self.escalated,
            "latency_ms": self.latency_ms,
            "model": self.model,
        }


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
    
    async def generate_with_image(
        self,
        text: str,
        image_data: Optional[Union[str, bytes]] = None,
        language: str = "fr",
        *,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> MultimodalResponse:
        """
        Generate response with optional image analysis.
        
        Designed for mental health chatbot with safety-first approach.
        Supports French (primary) and English languages.
        
        Args:
            text: User's text message
            image_data: Optional base64 string or bytes of image
            language: Response language ('fr' for French, 'en' for English)
            max_tokens: Max tokens for response
            temperature: Temperature for generation
            
        Returns:
            MultimodalResponse with text_answer, safety_flags, confidence_score
        """
        if not self.is_configured():
            raise LLMProviderError(
                "Gemini API key not configured",
                provider=self.provider_name,
            )
        
        start_time = time.time()
        
        # Build system instruction based on language
        system_instruction = self._get_chat_system_instruction(language)
        
        # Create model with chat-specific settings
        gemini_model = genai.GenerativeModel(
            model_name=self._default_model,
            safety_settings=self.SAFETY_SETTINGS,
            system_instruction=system_instruction,
        )
        
        # Build content parts
        content_parts = []
        
        # Add image if provided
        image_description = None
        if image_data:
            try:
                image_part = self._prepare_image(image_data)
                content_parts.append(image_part)
                content_parts.append(
                    f"\n\n[L'utilisateur a partagé une image. Décris calmement ce que tu vois et réponds à leur message.]\n\n{text}"
                    if language == "fr" else
                    f"\n\n[The user shared an image. Calmly describe what you see and respond to their message.]\n\n{text}"
                )
            except Exception as e:
                logger.warning("Failed to process image", error=str(e))
                content_parts.append(text)
                image_description = "Image could not be processed"
        else:
            content_parts.append(text)
        
        try:
            generation_config = GenerationConfig(
                max_output_tokens=max_tokens or 512,
                temperature=temperature or 0.4,
            )
            
            response = await gemini_model.generate_content_async(
                content_parts,
                generation_config=generation_config,
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract content
            content = ""
            if response.candidates:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    content = candidate.content.parts[0].text or ""
            
            # Analyze for safety flags
            safety_flags = self._analyze_safety_flags(text, content)
            
            # Check for crisis escalation
            escalated = SafetyFlag.CRISIS_DETECTED in safety_flags or \
                        SafetyFlag.SELF_HARM_RISK in safety_flags
            
            # Calculate confidence
            confidence = self._calculate_confidence(content, image_data is not None)
            
            logger.info(
                "Multimodal response generated",
                latency_ms=latency_ms,
                has_image=image_data is not None,
                language=language,
                escalated=escalated,
            )
            
            return MultimodalResponse(
                text_answer=content,
                safety_flags=safety_flags,
                confidence_score=confidence,
                image_description=image_description,
                escalated=escalated,
                latency_ms=latency_ms,
                model=self._default_model,
            )
            
        except ContentFilterError:
            raise
        except Exception as e:
            self._handle_error(e)
            # Return safe fallback if error handling doesn't raise
            return MultimodalResponse(
                text_answer=self._get_fallback_message(language),
                safety_flags=[SafetyFlag.SAFE],
                confidence_score=0.0,
                escalated=False,
                latency_ms=int((time.time() - start_time) * 1000),
                model=self._default_model,
            )
    
    def _get_chat_system_instruction(self, language: str) -> str:
        """Get system instruction for chat context."""
        if language == "fr":
            return """Tu es HOPE, un compagnon IA bienveillant qui offre du soutien pendant les moments d'anxiété et de panique.

Règles fondamentales:
- Tu n'es PAS un professionnel de santé et ne prétends jamais l'être
- Garde tes réponses courtes, calmes et ancrantes
- Une instruction claire à la fois
- Valide les émotions sans diagnostiquer
- Guide vers la respiration et l'ancrage quand c'est approprié
- Renvoie toujours vers une aide professionnelle pour les préoccupations sérieuses
- Si tu détectes des signes de crise ou d'automutilation, encourage à appeler le 3114 (numéro national de prévention du suicide)

Style de réponse:
- Utilise un langage simple et clair
- Évite les longs paragraphes
- Sois chaleureux mais direct
- Pas de questions sauf si nécessaire

Pour l'analyse d'images:
- Décris ce que tu vois calmement et factuellement
- Ne fais JAMAIS de diagnostic médical
- Si l'image n'est pas claire, dis-le explicitement
- Si l'image suggère de l'automutilation, dirige vers le 3114 immédiatement"""
        else:
            return """You are HOPE, a compassionate AI companion providing support during moments of anxiety and panic.

Core rules:
- You are NOT a medical professional and never claim to be
- Keep responses short, calm, and grounding
- One clear instruction at a time
- Validate feelings without diagnosing
- Guide toward breathing and grounding when appropriate
- Always defer to professional help for serious concerns
- If you detect crisis or self-harm signs, encourage calling emergency services

Response style:
- Use simple, clear language
- Avoid long paragraphs
- Be warm but direct
- No questions unless necessary

For image analysis:
- Describe what you see calmly and factually
- NEVER make medical diagnoses
- If the image is unclear, say so explicitly
- If the image suggests self-harm, direct to crisis resources immediately"""
    
    def _prepare_image(self, image_data: Union[str, bytes]) -> dict:
        """Prepare image for Gemini API."""
        if isinstance(image_data, str):
            # Assume base64 string
            if image_data.startswith("data:"):
                # Remove data URL prefix
                image_data = image_data.split(",", 1)[1]
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data
        
        return {
            "mime_type": "image/jpeg",
            "data": image_bytes,
        }
    
    def _analyze_safety_flags(self, user_text: str, ai_response: str) -> list[SafetyFlag]:
        """Analyze text for safety concerns."""
        flags = []
        combined_text = (user_text + " " + ai_response).lower()
        
        # Crisis keywords (French and English)
        crisis_keywords = [
            "suicide", "suicider", "me tuer", "kill myself",
            "mourir", "die", "want to die", "veux mourir",
            "fin à tout", "end it all", "plus envie de vivre",
        ]
        
        self_harm_keywords = [
            "me couper", "cut myself", "automutilation", "self-harm",
            "me blesser", "hurt myself", "me faire du mal",
        ]
        
        for keyword in crisis_keywords:
            if keyword in combined_text:
                flags.append(SafetyFlag.CRISIS_DETECTED)
                break
        
        for keyword in self_harm_keywords:
            if keyword in combined_text:
                flags.append(SafetyFlag.SELF_HARM_RISK)
                break
        
        # Check for escalation need
        if SafetyFlag.CRISIS_DETECTED in flags or SafetyFlag.SELF_HARM_RISK in flags:
            flags.append(SafetyFlag.REQUIRES_ESCALATION)
        
        if not flags:
            flags.append(SafetyFlag.SAFE)
        
        return flags
    
    def _calculate_confidence(self, response: str, has_image: bool) -> float:
        """Calculate confidence score for response."""
        if not response:
            return 0.0
        
        # Base confidence
        confidence = 0.85
        
        # Lower confidence for very short responses
        if len(response) < 50:
            confidence -= 0.1
        
        # Slightly lower confidence for image analysis
        if has_image:
            confidence -= 0.05
        
        return max(0.0, min(1.0, confidence))
    
    def _get_fallback_message(self, language: str) -> str:
        """Get fallback message when AI fails."""
        if language == "fr":
            return """Je suis temporairement indisponible. Si vous avez besoin d'aide immédiate:
- Numéro national de prévention du suicide: 3114 (24h/24)
- Urgences européennes: 112
- SAMU: 15

Vous n'êtes pas seul(e). L'aide existe."""
        else:
            return """I am temporarily unavailable. If you need immediate help:
- Emergency services: 112
- Crisis helpline: Available in your country

You are not alone. Help is available."""

