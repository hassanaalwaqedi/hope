"""
Recovery Prompt Templates

Deterministic, safety-bounded prompts for Gemini in post-panic recovery.
All prompts enforce strict constraints to protect vulnerable users.

SAFETY CRITICAL: These prompts are the only way Gemini can be invoked.
No free-form prompt building is allowed.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RecoveryPromptType(Enum):
    """Types of recovery prompts."""
    POST_BREATHING = "post_breathing"
    POST_GROUNDING = "post_grounding"
    RECOVERY_ENCOURAGEMENT = "recovery_encouragement"
    SESSION_CLOSING = "session_closing"


# Hard safety envelope - prepended to ALL prompts
SAFETY_ENVELOPE = """
CONTEXT: You are supporting someone who has just experienced a panic attack.
They are in early recovery and emotionally vulnerable.
You are providing gentle, supportive presence.

STRICT RULES - VIOLATION IS NOT ALLOWED:
1. Maximum 2 sentences
2. Warm, supportive tone only
3. NO clinical claims or diagnoses
4. NO advice or suggestions  
5. NO questions
6. NO absolute statements ("you will be fine", "it's over")
7. NO urgency language
8. NO future predictions
9. Validate their experience
10. Acknowledge their effort

FORBIDDEN CONTENT:
- Medical terminology
- Therapeutic interventions
- Trauma exploration
- Deep emotional analysis
- Philosophical language
- Storytelling
- Long explanations

You speak as a calm, present companion. Not a therapist. Not an AI.
"""


@dataclass
class RecoveryPrompt:
    """A bounded recovery prompt."""
    prompt_type: RecoveryPromptType
    system_prompt: str
    user_context: str
    
    @property
    def full_prompt(self) -> str:
        return f"{self.system_prompt}\n\n{self.user_context}"


# Pre-built prompts - deterministic and reusable
RECOVERY_PROMPTS = {
    RecoveryPromptType.POST_BREATHING: RecoveryPrompt(
        prompt_type=RecoveryPromptType.POST_BREATHING,
        system_prompt=SAFETY_ENVELOPE,
        user_context="""
The user just completed breathing exercises during panic recovery.
They took slow, intentional breaths and showed commitment to calming.

Generate a brief (1-2 sentence) supportive acknowledgment of their effort.
Focus on: their breathing work, being present, their body calming.
""",
    ),
    
    RecoveryPromptType.POST_GROUNDING: RecoveryPrompt(
        prompt_type=RecoveryPromptType.POST_GROUNDING,
        system_prompt=SAFETY_ENVELOPE,
        user_context="""
The user just completed grounding exercises during panic recovery.
They engaged their senses and reconnected with their surroundings.

Generate a brief (1-2 sentence) supportive acknowledgment of their effort.
Focus on: their grounding work, being present, feeling more connected.
""",
    ),
    
    RecoveryPromptType.RECOVERY_ENCOURAGEMENT: RecoveryPrompt(
        prompt_type=RecoveryPromptType.RECOVERY_ENCOURAGEMENT,
        system_prompt=SAFETY_ENVELOPE,
        user_context="""
The user is showing signs of stabilization after a panic episode.
Their intensity has decreased and they are regaining calm.

Generate a brief (1-2 sentence) normalizing statement about recovery.
Focus on: validating the experience, acknowledging progress.
""",
    ),
    
    RecoveryPromptType.SESSION_CLOSING: RecoveryPrompt(
        prompt_type=RecoveryPromptType.SESSION_CLOSING,
        system_prompt=SAFETY_ENVELOPE,
        user_context="""
The user is ending a panic support session.
They came through a difficult moment and are now ready to continue their day.

Generate a brief (1-2 sentence) gentle closing.
Focus on: acknowledging their work, warm presence, no pressure.
""",
    ),
}


# Fallback responses - used when Gemini fails or is blocked
FALLBACK_RESPONSES = {
    RecoveryPromptType.POST_BREATHING: 
        "Your breathing helped bring calm. You did good work.",
    
    RecoveryPromptType.POST_GROUNDING:
        "Connecting with your senses helped ground you. Well done.",
    
    RecoveryPromptType.RECOVERY_ENCOURAGEMENT:
        "You're moving through this. That takes real strength.",
    
    RecoveryPromptType.SESSION_CLOSING:
        "Thank you for letting me be here with you.",
}


def get_recovery_prompt(prompt_type: RecoveryPromptType) -> RecoveryPrompt:
    """
    Get a pre-built recovery prompt.
    
    Args:
        prompt_type: Type of recovery prompt needed
        
    Returns:
        RecoveryPrompt with safety envelope
    """
    return RECOVERY_PROMPTS[prompt_type]


def get_fallback_response(prompt_type: RecoveryPromptType) -> str:
    """
    Get fallback response when Gemini is unavailable.
    
    Args:
        prompt_type: Type of recovery prompt
        
    Returns:
        Static fallback response string
    """
    return FALLBACK_RESPONSES.get(
        prompt_type, 
        "You're doing well. I'm here with you."
    )
