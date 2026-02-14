"""
Intelligence Service - Centralized AI Entry Point

This is the PRIMARY INTELLIGENCE LAYER for the entire HOPE application.
All AI-powered features MUST use this service - no duplicate Gemini logic allowed.

Features:
- Streaming chat responses (SSE)
- Single Gemini entry point
- Cross-feature context memory
- AI metrics logging (latency, tokens, fallback)
- Shared user state across all features
- Safety pipeline integration

Usage:
    service = get_intelligence_service()
    response = await service.generate_chat_response(user_message, context)
    technique = await service.get_adapted_breathing_technique(user_state)
    resources = await service.get_personalized_resources(user_context)
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Any
from uuid import UUID, uuid4
import google.generativeai as genai

from hope.config import get_settings
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


# =============================================================================
# DATA MODELS
# =============================================================================

class FeatureType(Enum):
    """All AI-enabled features in the application."""
    CHAT = "chat"
    BREATHING = "breathing"
    GROUNDING = "grounding"
    RESOURCES = "resources"
    HISTORY = "history"
    SETTINGS = "settings"
    CRISIS = "crisis"


@dataclass
class AIMetrics:
    """Metrics for each AI call - used for observability."""
    feature: FeatureType
    latency_ms: int
    tokens_used: int
    ai_called: bool
    fallback_used: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            "feature": self.feature.value,
            "latency_ms": self.latency_ms,
            "tokens_used": self.tokens_used,
            "ai_called": self.ai_called,
            "fallback_used": self.fallback_used,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class FeatureContext:
    """Cross-feature context for unified AI experience."""
    user_id: Optional[str] = None
    session_id: Optional[UUID] = None
    language: str = "fr"
    
    # Emotional state from recent interactions
    emotional_state: str = "neutral"
    anxiety_level: float = 0.5  # 0.0-1.0
    last_exercise_completed: Optional[str] = None
    exercises_today: int = 0
    
    # Chat history summary (for cross-feature awareness)
    recent_topics: list[str] = field(default_factory=list)
    crisis_mode: bool = False
    
    def to_prompt_context(self) -> str:
        """Generate context string for Gemini prompts."""
        context_parts = [
            f"Language: {self.language}",
            f"Emotional state: {self.emotional_state}",
            f"Anxiety level: {self.anxiety_level:.1f}/1.0",
        ]
        
        if self.last_exercise_completed:
            context_parts.append(f"Last exercise: {self.last_exercise_completed}")
        
        if self.exercises_today > 0:
            context_parts.append(f"Exercises completed today: {self.exercises_today}")
        
        if self.recent_topics:
            context_parts.append(f"Recent topics discussed: {', '.join(self.recent_topics[-3:])}")
        
        if self.crisis_mode:
            context_parts.append("⚠️ User in crisis mode - be extra supportive")
        
        return "\n".join(context_parts)


# =============================================================================
# SYSTEM PROMPTS FOR EACH FEATURE
# =============================================================================

BREATHING_PROMPT = """You are HOPE, an AI assistant helping with breathing exercises.

Based on the user's current state, recommend ONE breathing technique and guide them through it.

TECHNIQUE OPTIONS:
- 4-7-8 breathing (calming, for high anxiety)
- Box breathing (grounding, for moderate anxiety)
- Diaphragmatic breathing (general relaxation)
- Resonant breathing (balanced state)

YOUR RESPONSE MUST INCLUDE:
1. Which technique you recommend and why (1 sentence)
2. Step-by-step personalized guidance (adapt wording to user's state)
3. Encouragement message

Use warm, calm language. Speak directly to the user.
Keep response under 200 words."""

RESOURCES_PROMPT = """You are HOPE, an AI assistant providing mental health resources.

Based on the user's context, provide personalized resource recommendations.

RULES:
- Prioritize resources for France (user is likely in France)
- Rank resources by relevance to user's current state
- Briefly explain why each resource might help
- Include hotline numbers only if relevant to crisis

FORMAT your response as:
1. [Resource Name] - Brief personal explanation of why this helps
2. [Resource Name] - Brief personal explanation

Maximum 5 resources. Be concise but warm."""

SETTINGS_PROMPT = """You are HOPE, an AI assistant explaining app settings.

Explain the requested setting in natural, friendly language.
Recommend what the user should do based on their context.

Be helpful like a friend explaining technology, not like a manual."""


# =============================================================================
# INTELLIGENCE SERVICE - SINGLE ENTRY POINT
# =============================================================================

class IntelligenceService:
    """
    Centralized AI Service.
    
    ALL AI-powered features must use this service.
    No duplicate Gemini logic allowed elsewhere.
    """
    
    # Gemini model configuration
    MODEL_NAME = "gemini-flash-latest"
    MAX_TOKENS = 800
    TEMPERATURE = 0.8
    
    def __init__(self) -> None:
        """Initialize intelligence service."""
        settings = get_settings()
        self._api_key = settings.gemini.api_key.get_secret_value()
        self._configured = bool(self._api_key)
        
        if self._configured:
            genai.configure(api_key=self._api_key)
            logger.info("IntelligenceService initialized - AI enabled")
        else:
            logger.warning("IntelligenceService initialized - AI DISABLED (no API key)")
        
        # Metrics storage
        self._metrics: list[AIMetrics] = []
        self._feature_call_counts: dict[str, int] = {}
        self._feature_total_latency: dict[str, int] = {}
        
        # Shared context storage (per session)
        self._contexts: dict[UUID, FeatureContext] = {}
    
    @property
    def is_available(self) -> bool:
        """Check if AI is available."""
        return self._configured
    
    # =========================================================================
    # CONTEXT MANAGEMENT
    # =========================================================================
    
    def get_context(self, session_id: UUID) -> FeatureContext:
        """Get or create context for a session."""
        if session_id not in self._contexts:
            self._contexts[session_id] = FeatureContext(session_id=session_id)
        return self._contexts[session_id]
    
    def update_context(
        self,
        session_id: UUID,
        emotional_state: Optional[str] = None,
        anxiety_level: Optional[float] = None,
        exercise_completed: Optional[str] = None,
        topic: Optional[str] = None,
        crisis_mode: Optional[bool] = None,
        language: Optional[str] = None,
    ) -> None:
        """Update shared context after any feature interaction."""
        ctx = self.get_context(session_id)
        
        if emotional_state:
            ctx.emotional_state = emotional_state
        if anxiety_level is not None:
            ctx.anxiety_level = anxiety_level
        if exercise_completed:
            ctx.last_exercise_completed = exercise_completed
            ctx.exercises_today += 1
        if topic:
            ctx.recent_topics.append(topic)
            ctx.recent_topics = ctx.recent_topics[-5:]  # Keep last 5
        if crisis_mode is not None:
            ctx.crisis_mode = crisis_mode
        if language:
            ctx.language = language
    
    # =========================================================================
    # METRICS & OBSERVABILITY
    # =========================================================================
    
    def _record_metrics(
        self,
        feature: FeatureType,
        latency_ms: int,
        tokens_used: int,
        ai_called: bool,
        fallback_used: bool = False,
    ) -> None:
        """Record AI call metrics."""
        metric = AIMetrics(
            feature=feature,
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            ai_called=ai_called,
            fallback_used=fallback_used,
        )
        self._metrics.append(metric)
        
        # Update aggregates
        key = feature.value
        self._feature_call_counts[key] = self._feature_call_counts.get(key, 0) + 1
        self._feature_total_latency[key] = self._feature_total_latency.get(key, 0) + latency_ms
        
        # Log for observability
        logger.info(
            "AI call completed",
            feature=feature.value,
            latency_ms=latency_ms,
            ai_called=ai_called,
            fallback_used=fallback_used,
        )
    
    def get_ai_status(self) -> dict:
        """Get real-time AI status for /debug/ai-status endpoint."""
        features = {}
        for feature in FeatureType:
            key = feature.value
            count = self._feature_call_counts.get(key, 0)
            total_latency = self._feature_total_latency.get(key, 0)
            
            features[key] = {
                "ai_calls": count,
                "avg_latency_ms": total_latency // count if count > 0 else 0,
                "ai_enabled": self._configured,
            }
        
        total_calls = sum(self._feature_call_counts.values())
        ai_calls = sum(1 for m in self._metrics if m.ai_called)
        
        return {
            "ai_enabled": self._configured,
            "model": self.MODEL_NAME,
            "features": features,
            "total_ai_calls": total_calls,
            "coverage_percentage": (ai_calls / total_calls * 100) if total_calls > 0 else 0,
        }
    
    # =========================================================================
    # CORE GEMINI CALL
    # =========================================================================
    
    async def _call_gemini(
        self,
        system_prompt: str,
        user_message: str,
        context: Optional[FeatureContext] = None,
        max_tokens: Optional[int] = None,
    ) -> tuple[str, int, int]:
        """
        Core Gemini API call.
        
        Returns: (response_text, latency_ms, tokens_used)
        """
        start_time = time.time()
        
        # Build full prompt with context
        full_prompt = system_prompt
        if context:
            full_prompt += f"\n\n--- USER CONTEXT ---\n{context.to_prompt_context()}"
        
        model = genai.GenerativeModel(
            model_name=self.MODEL_NAME,
            system_instruction=full_prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens or self.MAX_TOKENS,
                temperature=self.TEMPERATURE,
            ),
        )
        
        response = await model.generate_content_async(user_message)
        
        latency_ms = int((time.time() - start_time) * 1000)
        tokens_used = int(len(response.text.split()) * 1.3)
        
        return response.text, latency_ms, tokens_used
    
    # =========================================================================
    # FEATURE-SPECIFIC AI METHODS
    # =========================================================================
    
    async def get_adapted_breathing_technique(
        self,
        session_id: UUID,
        user_request: Optional[str] = None,
    ) -> dict:
        """
        AI-adapted breathing technique selection.
        
        Returns personalized technique and guidance based on user state.
        """
        if not self._configured:
            return self._get_breathing_fallback()
        
        context = self.get_context(session_id)
        
        user_message = user_request or f"""
I need help with a breathing exercise.
My current anxiety level feels like {context.anxiety_level:.1f}/1.0.
{"I just finished " + context.last_exercise_completed if context.last_exercise_completed else "I haven't done any exercises yet."}
"""
        
        try:
            response, latency_ms, tokens = await self._call_gemini(
                system_prompt=BREATHING_PROMPT,
                user_message=user_message,
                context=context,
            )
            
            self._record_metrics(
                feature=FeatureType.BREATHING,
                latency_ms=latency_ms,
                tokens_used=tokens,
                ai_called=True,
            )
            
            return {
                "guidance": response,
                "ai_called": True,
                "latency_ms": latency_ms,
            }
            
        except Exception as e:
            logger.error(f"Breathing AI failed: {e}")
            self._record_metrics(
                feature=FeatureType.BREATHING,
                latency_ms=0,
                tokens_used=0,
                ai_called=False,
                fallback_used=True,
            )
            return self._get_breathing_fallback()
    
    def _get_breathing_fallback(self) -> dict:
        """Fallback when AI unavailable - static technique."""
        return {
            "guidance": """Let's try 4-7-8 breathing together.

1. Breathe in through your nose for 4 seconds
2. Hold your breath for 7 seconds
3. Exhale slowly through your mouth for 8 seconds

Repeat 4 times. Take your time.""",
            "ai_called": False,
            "fallback": True,
        }
    
    async def get_personalized_resources(
        self,
        session_id: UUID,
        query: Optional[str] = None,
    ) -> dict:
        """
        AI-personalized resource recommendations.
        
        Returns ranked resources with explanations.
        """
        if not self._configured:
            return self._get_resources_fallback()
        
        context = self.get_context(session_id)
        
        user_message = query or f"""
Based on my current state, what mental health resources would help me?
{"Recent topics: " + ", ".join(context.recent_topics) if context.recent_topics else ""}
"""
        
        try:
            response, latency_ms, tokens = await self._call_gemini(
                system_prompt=RESOURCES_PROMPT,
                user_message=user_message,
                context=context,
            )
            
            self._record_metrics(
                feature=FeatureType.RESOURCES,
                latency_ms=latency_ms,
                tokens_used=tokens,
                ai_called=True,
            )
            
            return {
                "recommendations": response,
                "ai_called": True,
                "latency_ms": latency_ms,
            }
            
        except Exception as e:
            logger.error(f"Resources AI failed: {e}")
            self._record_metrics(
                feature=FeatureType.RESOURCES,
                latency_ms=0,
                tokens_used=0,
                ai_called=False,
                fallback_used=True,
            )
            return self._get_resources_fallback()
    
    def _get_resources_fallback(self) -> dict:
        """Fallback resources list when AI unavailable."""
        return {
            "recommendations": """Ressources disponibles:

1. 3114 - Numéro national de prévention du suicide (24h/24)
2. Fil Santé Jeunes - 0 800 235 236 (anonyme, gratuit)
3. SOS Amitié - 09 72 39 40 50
4. Psycom.org - Information sur la santé mentale

Ces ressources sont disponibles pour vous aider.""",
            "ai_called": False,
            "fallback": True,
        }
    
    async def explain_setting(
        self,
        session_id: UUID,
        setting_name: str,
        setting_description: str,
    ) -> dict:
        """AI explains a setting in natural language."""
        if not self._configured:
            return {"explanation": setting_description, "ai_called": False}
        
        context = self.get_context(session_id)
        
        try:
            response, latency_ms, tokens = await self._call_gemini(
                system_prompt=SETTINGS_PROMPT,
                user_message=f"Explain this setting: {setting_name}\nDescription: {setting_description}",
                context=context,
                max_tokens=200,
            )
            
            self._record_metrics(
                feature=FeatureType.SETTINGS,
                latency_ms=latency_ms,
                tokens_used=tokens,
                ai_called=True,
            )
            
            return {
                "explanation": response,
                "ai_called": True,
                "latency_ms": latency_ms,
            }
            
        except Exception as e:
            logger.error(f"Settings AI failed: {e}")
            return {"explanation": setting_description, "ai_called": False}

    async def generate_chat_response(
        self,
        session_id: UUID,
        system_prompt: str,
        message_history: list[dict],
        user_message: str,
        detected_language: Optional[str] = None,
    ) -> dict:
        """
        Generate chat response via centralized service.
        Updates shared context and logs metrics.
        """
        context = self.get_context(session_id)
        
        # Update language if detected
        if detected_language:
            context.language = detected_language
        
        # Build prompt: System + Context + History + User Message
        # Note: We pass history differently to Gemini chat, but for _call_gemini we might need to adapt
        # Typically chat needs start_chat(history=...).
        
        # Let's use specific chat generation logic here since it's stateful
        if not self._configured:
             raise ValueError("AI not configured")
             
        start_time = time.time()
        
        try:
            # 1. Initialize model with system prompt and context
            full_system_prompt = system_prompt + f"\n\n--- SHARED CONTEXT ---\n{context.to_prompt_context()}"
            
            model = genai.GenerativeModel(
                model_name=self.MODEL_NAME,
                system_instruction=full_system_prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=self.MAX_TOKENS,
                    temperature=self.TEMPERATURE,
                ),
            )
            
            # 2. Start chat with history
            chat = model.start_chat(history=message_history)
            
            # 3. Send message
            response = await chat.send_message_async(user_message)
            
            latency_ms = int((time.time() - start_time) * 1000)
            tokens_used = int(len(response.text.split()) * 1.3)
            
            # 4. Record metrics
            self._record_metrics(
                feature=FeatureType.CHAT,
                latency_ms=latency_ms,
                tokens_used=tokens_used,
                ai_called=True,
            )
            
            # 5. Update context based on interaction (naive sentiment update for now)
            # In a real system, we'd ask Gemini to classify sentiment separately or use a multi-head output
            
            return {
                "text": response.text,
                "latency_ms": latency_ms,
                "ai_called": True,
            }
            
        except Exception as e:
            logger.error(f"Chat AI failed: {e}")
            self._record_metrics(
                feature=FeatureType.CHAT,
                latency_ms=int((time.time() - start_time) * 1000),
                tokens_used=0,
                ai_called=False,
                fallback_used=True,
            )
            raise e

    async def generate_chat_response_stream(
        self,
        session_id: UUID,
        system_prompt: str,
        message_history: list[dict],
        user_message: str,
        detected_language: Optional[str] = None,
    ):
        """
        Stream chat response tokens via centralized service.
        
        Yields dicts: {"type": "token", "text": "..."} for each chunk,
        then {"type": "done", "latency_ms": ..., "full_text": "..."} at the end.
        """
        context = self.get_context(session_id)
        
        if detected_language:
            context.language = detected_language
        
        if not self._configured:
            raise ValueError("AI not configured")
        
        start_time = time.time()
        
        try:
            full_system_prompt = system_prompt + f"\n\n--- SHARED CONTEXT ---\n{context.to_prompt_context()}"
            
            model = genai.GenerativeModel(
                model_name=self.MODEL_NAME,
                system_instruction=full_system_prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=self.MAX_TOKENS,
                    temperature=self.TEMPERATURE,
                ),
            )
            
            chat = model.start_chat(history=message_history)
            
            # Stream the response
            response = await chat.send_message_async(user_message, stream=True)
            
            full_text = ""
            async for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    yield {"type": "token", "text": chunk.text}
            
            latency_ms = int((time.time() - start_time) * 1000)
            tokens_used = int(len(full_text.split()) * 1.3)
            
            self._record_metrics(
                feature=FeatureType.CHAT,
                latency_ms=latency_ms,
                tokens_used=tokens_used,
                ai_called=True,
            )
            
            yield {
                "type": "done",
                "full_text": full_text,
                "latency_ms": latency_ms,
                "ai_called": True,
            }
            
        except Exception as e:
            logger.error(f"Streaming chat AI failed: {e}")
            self._record_metrics(
                feature=FeatureType.CHAT,
                latency_ms=int((time.time() - start_time) * 1000),
                tokens_used=0,
                ai_called=False,
                fallback_used=True,
            )
            yield {"type": "error", "message": str(e)}


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_intelligence_service: Optional[IntelligenceService] = None


def get_intelligence_service() -> IntelligenceService:
    """Get the singleton intelligence service instance."""
    global _intelligence_service
    if _intelligence_service is None:
        _intelligence_service = IntelligenceService()
    return _intelligence_service
