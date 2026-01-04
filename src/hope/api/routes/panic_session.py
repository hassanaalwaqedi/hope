"""
Panic Session WebSocket Router

Real-time WebSocket endpoint for panic sessions.
Integrates clinical and safety pipelines for response generation.

ARCHITECTURE: All panic messages flow through this endpoint.
Responses are validated by safety pipeline before delivery.

PHASE 6: Gemini is activated ONLY in post-panic recovery.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel

from hope.domain.models.clinical_output import ClinicalAssessment
from hope.domain.enums.panic_severity import PanicSeverity
from hope.services.clinical.clinical_pipeline import ClinicalPipeline
from hope.services.safety.safety_pipeline import SafetyPipeline
from hope.services.decision.decision_engine import DecisionEngine, DecisionContext
from hope.services.safety.stability_gate import (
    StabilityContext,
    StabilityGate,
    PanicStabilityState,
    stability_gate,
)
from hope.services.llm.gemini_activation_gate import (
    gemini_activation_gate,
    ActivationDecision,
)
from hope.services.llm.gemini_supervisor import gemini_supervisor, GeminiResponse
from hope.services.prompt.recovery_prompt_templates import RecoveryPromptType
from hope.config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


class PanicSessionManager:
    """
    Manages active panic WebSocket sessions.
    
    ARCHITECTURE: Maintains session state and coordinates
    with clinical/safety pipelines for each message.
    """
    
    def __init__(self) -> None:
        self._active_sessions: dict[str, "PanicSession"] = {}
        self._clinical_pipeline: Optional[ClinicalPipeline] = None
        self._safety_pipeline: Optional[SafetyPipeline] = None
        self._decision_engine: Optional[DecisionEngine] = None
    
    async def initialize(self) -> None:
        """Initialize pipelines and Gemini supervisor."""
        self._clinical_pipeline = ClinicalPipeline()
        await self._clinical_pipeline.initialize()
        self._safety_pipeline = SafetyPipeline()
        self._decision_engine = DecisionEngine()
        # Initialize Gemini (Phase 6)
        await gemini_supervisor.initialize()
        logger.info("PanicSessionManager initialized with Gemini support")
    
    def create_session(
        self,
        websocket: WebSocket,
        user_id: Optional[UUID] = None,
    ) -> "PanicSession":
        """Create a new panic session."""
        session_id = str(uuid4())
        session = PanicSession(
            session_id=session_id,
            user_id=user_id or uuid4(),
            websocket=websocket,
            manager=self,
        )
        self._active_sessions[session_id] = session
        logger.info(f"Created panic session: {session_id}")
        return session
    
    def remove_session(self, session_id: str) -> None:
        """Remove a session."""
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
            logger.info(f"Removed panic session: {session_id}")
    
    def get_session(self, session_id: str) -> Optional["PanicSession"]:
        """Get an active session."""
        return self._active_sessions.get(session_id)
    
    @property
    def clinical_pipeline(self) -> ClinicalPipeline:
        if not self._clinical_pipeline:
            raise RuntimeError("Manager not initialized")
        return self._clinical_pipeline
    
    @property
    def safety_pipeline(self) -> SafetyPipeline:
        if not self._safety_pipeline:
            raise RuntimeError("Manager not initialized")
        return self._safety_pipeline
    
    @property
    def decision_engine(self) -> DecisionEngine:
        if not self._decision_engine:
            raise RuntimeError("Manager not initialized")
        return self._decision_engine


class PanicSession:
    """
    Individual panic session handler.
    
    Processes messages and generates responses using
    the clinical and safety pipelines.
    """
    
    def __init__(
        self,
        session_id: str,
        user_id: UUID,
        websocket: WebSocket,
        manager: PanicSessionManager,
    ) -> None:
        self.session_id = session_id
        self.user_id = user_id
        self.websocket = websocket
        self.manager = manager
        self.started_at = datetime.utcnow()
        self.message_count = 0
        self.current_phase = "active"
        self.last_intensity: Optional[float] = None
        
        # Phase 6: Stability tracking for Gemini activation
        self.severity_history: List[PanicSeverity] = []
        self.intensity_history: List[float] = []
        self.breathing_cycles_completed = 0
        self.grounding_steps_completed = 0
        self.has_crisis_signals = False
        self.current_stability_state: PanicStabilityState = PanicStabilityState.PANIC_ACTIVE
    
    async def handle_message(self, data: dict) -> None:
        """
        Handle incoming WebSocket message.
        
        Routes to appropriate handler based on action.
        """
        action = data.get("action")
        
        if action == "start_panic_session":
            await self._handle_start()
        elif action == "user_message":
            await self._handle_user_message(data.get("text", ""))
        elif action == "report_intensity":
            await self._handle_intensity(data.get("intensity", 0.5))
        elif action == "breathing_complete":
            await self._handle_breathing_complete(data.get("cycles", 1))
        elif action == "grounding_complete":
            await self._handle_grounding_complete(data.get("steps", 1))
        elif action == "end_session":
            await self._handle_end()
        else:
            logger.warning(f"Unknown action: {action}")
    
    async def _handle_start(self) -> None:
        """Handle session start."""
        # Send initial grounding message
        await self._send_response(
            text="I'm here with you. Let's take this moment together.",
            message_type="validation",
            phase="active",
        )
        
        # Send first breathing prompt
        await self._send_response(
            text="When you're ready, let's focus on your breathing.",
            message_type="instruction",
            phase="breathing",
            step_number=0,
            total_steps=4,
        )
    
    async def _handle_user_message(self, text: str) -> None:
        """
        Handle user text message.
        
        Runs through clinical and safety pipelines.
        """
        self.message_count += 1
        
        try:
            # Step 1: Clinical analysis
            clinical = await self.manager.clinical_pipeline.analyze(
                text=text,
                user_id=self.user_id,
                session_id=UUID(self.session_id),
            )
            
            # Step 2: Safety evaluation
            # Generate a base response first
            base_response = self._generate_base_response(clinical)
            
            evaluation = self.manager.safety_pipeline.evaluate(
                clinical=clinical,
                proposed_response=base_response,
                raw_text=text,
            )
            
            # Step 3: Send safe response
            await self._send_response(
                text=evaluation.final_response,
                message_type="support",
                phase=self._determine_phase(clinical),
                show_resources=evaluation.requires_crisis_response,
            )
            
            # Log if escalated
            if evaluation.requires_crisis_response:
                logger.warning(
                    "Crisis response in panic session",
                    session_id=self.session_id,
                    user_id=str(self.user_id),
                )
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self._send_fallback_response()
    
    async def _handle_intensity(self, intensity: float) -> None:
        """Handle intensity report."""
        self.last_intensity = intensity
        self.intensity_history.append(intensity)
        
        # Adjust response based on intensity
        if intensity > 0.8:
            await self._send_response(
                text="I can feel this is really intense right now. Let's slow down together.",
                message_type="validation",
            )
        elif intensity < 0.3:
            # User is stabilizing - check if Gemini can help
            gemini_response = await self._try_gemini_response(
                RecoveryPromptType.RECOVERY_ENCOURAGEMENT
            )
            if gemini_response:
                await self._send_response(
                    text=gemini_response,
                    message_type="encouragement",
                    phase="calming",
                )
            else:
                await self._send_response(
                    text="You're doing great. Your body is starting to calm.",
                    message_type="encouragement",
                    phase="calming",
                )
    
    async def _handle_breathing_complete(self, cycles: int) -> None:
        """Handle breathing exercise completion."""
        self.breathing_cycles_completed += cycles
        
        logger.info(
            "Breathing exercise completed",
            session_id=self.session_id,
            cycles=cycles,
            total_cycles=self.breathing_cycles_completed,
        )
        
        # Try Gemini for post-breathing encouragement
        gemini_response = await self._try_gemini_response(
            RecoveryPromptType.POST_BREATHING
        )
        if gemini_response:
            await self._send_response(
                text=gemini_response,
                message_type="encouragement",
                phase="calming",
            )
        else:
            await self._send_response(
                text="Your breathing helped bring calm. You did good work.",
                message_type="encouragement",
                phase="calming",
            )
    
    async def _handle_grounding_complete(self, steps: int) -> None:
        """Handle grounding exercise completion."""
        self.grounding_steps_completed += steps
        
        logger.info(
            "Grounding exercise completed",
            session_id=self.session_id,
            steps=steps,
            total_steps=self.grounding_steps_completed,
        )
        
        # Try Gemini for post-grounding encouragement
        gemini_response = await self._try_gemini_response(
            RecoveryPromptType.POST_GROUNDING
        )
        if gemini_response:
            await self._send_response(
                text=gemini_response,
                message_type="encouragement",
                phase="calming",
            )
        else:
            await self._send_response(
                text="Connecting with your senses helped ground you. Well done.",
                message_type="encouragement",
                phase="calming",
            )
    
    async def _handle_end(self) -> None:
        """Handle session end."""
        # Try Gemini for closing message
        gemini_response = await self._try_gemini_response(
            RecoveryPromptType.SESSION_CLOSING
        )
        if gemini_response:
            await self._send_response(
                text=gemini_response,
                message_type="closing",
                phase="resolved",
            )
        else:
            await self._send_response(
                text="You did wonderful work today. Remember, I'm always here when you need me.",
                message_type="closing",
                phase="resolved",
            )
        
        # Clean up Gemini error counts
        gemini_activation_gate.clear_session(self.session_id)
        self.manager.remove_session(self.session_id)
    
    async def _try_gemini_response(
        self,
        prompt_type: RecoveryPromptType,
    ) -> Optional[str]:
        """
        Attempt to get Gemini response if allowed.
        
        SAFETY: Returns None if Gemini is not allowed,
        falling back to rule-based responses.
        
        Args:
            prompt_type: Type of recovery prompt
            
        Returns:
            Gemini response text or None
        """
        # Build stability context
        context = self._build_stability_context()
        
        # Check if Gemini is allowed
        decision = gemini_activation_gate.is_allowed(context)
        
        if not decision.allowed:
            logger.debug(
                "Gemini activation denied",
                session_id=self.session_id,
                reason=decision.reason,
            )
            return None
        
        # Gemini is allowed - generate response
        logger.info(
            "Gemini activation ALLOWED",
            session_id=self.session_id,
            stability_state=context.current_severity.name,
        )
        
        response = await gemini_supervisor.generate_recovery_message(
            prompt_type=prompt_type,
            session_id=self.session_id,
        )
        
        if response.source == "gemini":
            return response.text
        else:
            # Fallback was used - return None to use rule-based
            return None
    
    def _build_stability_context(self) -> StabilityContext:
        """Build stability context from session state."""
        return StabilityContext(
            session_id=UUID(self.session_id),
            user_id=self.user_id,
            started_at=self.started_at,
            current_severity=self.severity_history[-1] if self.severity_history else PanicSeverity.MODERATE,
            current_intensity=self.last_intensity or 0.5,
            severity_history=self.severity_history,
            intensity_history=self.intensity_history,
            breathing_cycles_completed=self.breathing_cycles_completed,
            grounding_steps_completed=self.grounding_steps_completed,
            has_crisis_signals=self.has_crisis_signals,
            has_self_harm_signals=False,
        )
    
    def _generate_base_response(self, clinical: ClinicalAssessment) -> str:
        """Generate base response from clinical assessment."""
        severity = clinical.severity.predicted_severity
        
        if severity >= PanicSeverity.CRITICAL:
            return (
                "I'm here with you. What you're feeling is intense, "
                "and I want to make sure you have the support you need."
            )
        elif severity >= PanicSeverity.SEVERE:
            return (
                "I hear you. This sounds very difficult right now. "
                "Let's focus on one thing at a time."
            )
        elif severity >= PanicSeverity.MODERATE:
            return (
                "I understand. Let's work through this together. "
                "Try to take a slow breath with me."
            )
        else:
            return "I'm here with you. How can I help right now?"
    
    def _determine_phase(self, clinical: ClinicalAssessment) -> str:
        """Determine session phase from clinical assessment."""
        if clinical.requires_crisis_protocol:
            return "escalated"
        
        severity = clinical.severity.predicted_severity
        if severity >= PanicSeverity.SEVERE:
            return "active"
        elif severity >= PanicSeverity.MODERATE:
            return "breathing"
        else:
            return "calming"
    
    async def _send_response(
        self,
        text: str,
        message_type: str = "instruction",
        phase: Optional[str] = None,
        step_number: Optional[int] = None,
        total_steps: Optional[int] = None,
        show_resources: bool = False,
        emergency_resources: Optional[list[str]] = None,
    ) -> None:
        """Send response to client."""
        response = {
            "session_id": self.session_id,
            "type": "panic_message",
            "data": {
                "text": text,
                "message_type": message_type,
                "phase": phase or self.current_phase,
                "step_number": step_number,
                "total_steps": total_steps,
                "show_resources": show_resources,
                "emergency_resources": emergency_resources,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
        
        if phase:
            self.current_phase = phase
        
        await self.websocket.send_json(response)
    
    async def _send_fallback_response(self) -> None:
        """Send fallback response on error."""
        await self._send_response(
            text=(
                "I'm having a moment of difficulty, but I'm still here with you. "
                "Try taking a slow, deep breath in... and let it out slowly."
            ),
            message_type="fallback",
        )


# Global session manager (initialized on startup)
session_manager = PanicSessionManager()


@router.websocket("/panic")
async def panic_websocket(
    websocket: WebSocket,
    user_id: Optional[str] = None,
) -> None:
    """
    WebSocket endpoint for panic sessions.
    
    Accepts user messages and returns clinical responses
    through the complete pipeline.
    """
    await websocket.accept()
    
    # Create session
    uid = UUID(user_id) if user_id else None
    session = session_manager.create_session(websocket, uid)
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_id": session.session_id,
        })
        
        # Message loop
        while True:
            data = await websocket.receive_json()
            await session.handle_message(data)
    
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session.session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        session_manager.remove_session(session.session_id)


async def initialize_panic_sessions() -> None:
    """Initialize session manager on startup."""
    await session_manager.initialize()
