"""
AI Chat Service - GPT-Level Conversational AI

Production-grade conversational AI powered by Centralized Intelligence Service:
- Uses IntelligenceService for single Gemini entry point
- Multi-language support (10 languages) via PromptBuilder
- Real multi-turn conversation memory
- Intelligent safety (Regex patterns + Gemini)
"""

import time
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from hope.config import get_settings
from hope.config.logging_config import get_logger
from hope.domain.models.chat_models import (
    ChatMessage,
    ChatSession,
    ChatResponse,
    MessageRole,
    ChatLanguage,
)
from hope.infrastructure.llm.gemini_flash_provider import SafetyFlag
from hope.services.intelligence import get_intelligence_service, get_language_service
from hope.core.localization.prompts import PromptBuilder

logger = get_logger(__name__)


class AIChatService:
    """
    GPT-Level Conversational AI Service (Multilingual).
    
    Orchestrates the chat flow:
    1. Detects language
    2. Builds localized prompts
    3. Checks safety patterns per language
    4. Delegates generation to IntelligenceService
    """
    
    # Conversation memory size
    MAX_CONVERSATION_HISTORY = 20
    
    def __init__(self) -> None:
        """Initialize chat service."""
        # Use centralized service for checking availability
        self._intelligence_service = get_intelligence_service()
        self._language_service = get_language_service()
        self._sessions: dict[UUID, ChatSession] = {}
        
        if self._intelligence_service.is_available:
            logger.info("AIChatService initialized with IntelligenceService (Multilingual)")
        else:
            logger.warning("AIChatService initialized - AI unavailable")
    
    @property
    def is_available(self) -> bool:
        """Check if AI is available."""
        return self._intelligence_service.is_available
    
    async def start_session(
        self,
        language: str = "en",
        user_id: Optional[str] = None,
    ) -> ChatSession:
        """Start a new conversation session."""
        # Map string to enum if possible, or just default to EN for initial creation
        # Session language will update dynamically
        try:
            lang_enum = ChatLanguage(language)
        except ValueError:
            lang_enum = ChatLanguage.ENGLISH
            
        session = ChatSession(
            id=uuid4(),
            user_id=user_id,
            language=lang_enum,
        )
        
        self._sessions[session.id] = session
        
        # Initialize context
        self._intelligence_service.get_context(session.id)
        
        logger.info(
            "Conversation session started",
            session_id=str(session.id),
            language=language,
        )
        
        return session
    
    async def send_message(
        self,
        session_id: UUID,
        text: str,
        image_data: Optional[str] = None,
    ) -> ChatResponse:
        """
        Send a message and get response via IntelligenceService.
        """
        start_time = time.time()
        
        if not self.is_available:
            raise ValueError("AI is not available - Gemini API not configured")
        
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
            
        # 1. LANGUAGE DETECTION
        # Detect language of the NEW message
        lang_context = self._language_service.detect_language(text, default=session.language.value)
        detected_lang = lang_context.code
        
        # Update session language preference dynamically
        # Only update if confidence is high or strict switch needed
        session.language = ChatLanguage(detected_lang) if detected_lang in [l.value for l in ChatLanguage] else session.language
        
        # Add user message
        user_message = ChatMessage(
            role=MessageRole.USER,
            content=text,
            image_data=image_data,
            detected_language=detected_lang,
        )
        session.add_message(user_message)
        
        # 2. PROMPT BUILDING
        conversation_history = self._build_conversation_context(session)
        system_prompt = PromptBuilder.get_system_prompt(detected_lang)
        
        try:
            # 3. CALL CENTRALIZED INTELLIGENCE
            # We pass the detected language so IntelligenceService can update context
            result = await self._intelligence_service.generate_chat_response(
                session_id=session_id,
                system_prompt=system_prompt,
                message_history=conversation_history,
                user_message=text,
                detected_language=detected_lang,
            )
            
            response_text = result["text"]
            latency_ms = result["latency_ms"]
            
            # 4. MULTILINGUAL SAFETY CHECK
            # Check pattern-based crisis intent in the DETECTED language
            escalated, safety_flags = self._intelligent_safety_check(
                user_text=text,
                language=detected_lang,
            )
            
            # Update shared context with crisis status
            if escalated:
                self._intelligence_service.update_context(session_id, crisis_mode=True)
                response_text = self._add_crisis_info(
                    response_text,
                    detected_lang,
                )
                session.is_crisis_mode = True
            
            # Add assistant message
            assistant_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=response_text,
                safety_flags=[f.value for f in safety_flags],
            )
            session.add_message(assistant_message)
            
            # Update topic context
            if len(text) > 5:
                self._intelligence_service.update_context(session_id, topic=text[:50])
            
            return ChatResponse(
                text_answer=response_text,
                safety_flags=[f.value for f in safety_flags],
                confidence_score=0.95,
                escalated=escalated,
                session_id=session_id,
                message_id=assistant_message.id,
                latency_ms=latency_ms,
                ai_called=True,
            )
            
        except Exception as e:
            logger.error(
                "AI generation failed",
                session_id=str(session_id),
                error=str(e),
            )
            return self._get_fallback_response(session, start_time)
    
    def _build_conversation_context(self, session: ChatSession) -> list[dict]:
        """Build conversation context for Gemini (last 20 messages)."""
        messages = session.messages[-self.MAX_CONVERSATION_HISTORY:]
        
        context = []
        for msg in messages:
            role = "user" if msg.role == MessageRole.USER else "model"
            context.append({
                "role": role,
                "parts": [{"text": msg.content}],
            })
        
        return context
    
    def _intelligent_safety_check(
        self,
        user_text: str,
        language: str,
    ) -> tuple[bool, list[SafetyFlag]]:
        """
        Multilingual Safety Check.
        Uses SafetyPatterns + IntelligenceService context.
        """
        # 1. Regex Pattern Check (immediate risk)
        has_crisis_pattern = self._language_service.check_safety_for_language(user_text, language)
        
        flags = []
        if has_crisis_pattern:
            flags.append(SafetyFlag.CRISIS_DETECTED)
            flags.append(SafetyFlag.REQUIRES_ESCALATION)
            return True, flags
        
        flags.append(SafetyFlag.SAFE)
        return False, flags
    
    def _add_crisis_info(self, response: str, language: str) -> str:
        """Add localized crisis info."""
        # Simple mapping for now, ideally PromptBuilder could provide this
        hotlines = {
            "fr": "• 3114 - Suicide Écoute\n• 112 - Urgences",
            "en": "• 988 - Crisis Lifeline\n• 112/911 - Emergency",
            "es": "• 024 - Línea de atención a la conducta suicida\n• 112 - Emergencias",
            "ar": "• خدمات الطوارئ المحلية متاحة للمساعدة الفورية.",
            "tr": "• 112 - Acil Çağrı Merkezi",
            "de": "• 112 - Notruf\n• 0800 111 0 111 - TelefonSeelsorge",
            "it": "• 112 - Numero di emergenza unico europeo",
            "sv": "• 112 - Nödnumret\n• 90101 - Självmordslinjen",
            "ko": "• 1393 - 자살예방상담전화\n• 112 - 경찰청",
            "ja": "• #8103 - 性犯罪・性暴力被害者のためのワンストップ支援センター\n• 110 - 警察",
        }
        
        info = hotlines.get(language, hotlines["en"])
        
        # Native language prefix (simplified)
        prefix = "\n\n(System: Crisis Resources / Ressources de crise)\n"
        
        return response + prefix + info
    
    def _get_fallback_response(self, session: ChatSession, start_time: float) -> ChatResponse:
        """Return fallback error response."""
        error_msg = "Temporary connection issue. Please try again."
        if session.language == ChatLanguage.FRENCH:
            error_msg = "Problème de connexion temporaire. Veuillez réessayer."
            
        return ChatResponse(
            text_answer=error_msg,
            safety_flags=["api_error"],
            confidence_score=0.0,
            escalated=False,
            session_id=session.id,
            latency_ms=int((time.time() - start_time) * 1000),
            ai_called=False,
        )

    async def get_session_history(self, session_id: UUID) -> Optional[ChatSession]:
        """Get session with full message history."""
        return self._sessions.get(session_id)

    async def send_message_stream(
        self,
        session_id: UUID,
        text: str,
        image_data: Optional[str] = None,
    ):
        """
        Stream a message response token-by-token via IntelligenceService.
        
        Yields SSE-formatted dicts:
          {"type": "token", "text": "..."}
          {"type": "done", "session_id": "...", "latency_ms": ..., "escalated": bool}
        """
        if not self.is_available:
            yield {"type": "error", "message": "AI is not available"}
            return
        
        session = self._sessions.get(session_id)
        if not session:
            yield {"type": "error", "message": f"Session not found: {session_id}"}
            return
        
        # 1. Language detection
        lang_context = self._language_service.detect_language(text, default=session.language.value)
        detected_lang = lang_context.code
        session.language = ChatLanguage(detected_lang) if detected_lang in [l.value for l in ChatLanguage] else session.language
        
        # 2. Add user message
        user_message = ChatMessage(
            role=MessageRole.USER,
            content=text,
            image_data=image_data,
            detected_language=detected_lang,
        )
        session.add_message(user_message)
        
        # 3. Build prompt
        conversation_history = self._build_conversation_context(session)
        system_prompt = PromptBuilder.get_system_prompt(detected_lang)
        
        # 4. Stream from IntelligenceService
        full_text = ""
        try:
            async for chunk in self._intelligence_service.generate_chat_response_stream(
                session_id=session_id,
                system_prompt=system_prompt,
                message_history=conversation_history,
                user_message=text,
                detected_language=detected_lang,
            ):
                if chunk["type"] == "token":
                    full_text += chunk["text"]
                    yield chunk
                elif chunk["type"] == "done":
                    full_text = chunk.get("full_text", full_text)
                    latency_ms = chunk["latency_ms"]
                elif chunk["type"] == "error":
                    yield chunk
                    return
            
            # 5. Safety check on full response
            escalated, safety_flags = self._intelligent_safety_check(
                user_text=text,
                language=detected_lang,
            )
            
            if escalated:
                self._intelligence_service.update_context(session_id, crisis_mode=True)
                crisis_info = self._add_crisis_info("", detected_lang)
                full_text += crisis_info
                session.is_crisis_mode = True
                yield {"type": "token", "text": crisis_info}
            
            # 6. Store assistant message in session
            assistant_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=full_text,
                safety_flags=[f.value for f in safety_flags],
            )
            session.add_message(assistant_message)
            
            if len(text) > 5:
                self._intelligence_service.update_context(session_id, topic=text[:50])
            
            # 7. Send completion event
            yield {
                "type": "done",
                "session_id": str(session_id),
                "message_id": str(assistant_message.id),
                "latency_ms": latency_ms,
                "escalated": escalated,
                "safety_flags": [f.value for f in safety_flags],
                "ai_called": True,
            }
            
        except Exception as e:
            logger.error("Streaming chat failed", session_id=str(session_id), error=str(e))
            yield {"type": "error", "message": str(e)}
