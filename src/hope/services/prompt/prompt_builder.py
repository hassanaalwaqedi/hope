"""
Prompt Builder

Constructs prompts for LLM with clinical constraints and context control.

ARCHITECTURE: Prompts are built dynamically based on decision engine output.
System prompts embed safety constraints directly.

CLINICAL_REVIEW_REQUIRED: System prompts and intervention templates
should be validated by mental health professionals.
"""

from dataclasses import dataclass, field
from typing import Optional

from hope.domain.models.panic_event import PanicIntervention
from hope.services.decision.decision_engine import Decision, ResponseStrategy, ResponseTone
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class BuiltPrompt:
    """
    Complete prompt ready for LLM.
    
    Attributes:
        system_prompt: System/instruction prompt
        user_context: Context about the user/situation
        conversation_history: Recent conversation messages
        user_message: Current user message
        full_prompt: Complete formatted prompt
        max_tokens: Suggested max tokens for response
        temperature: Suggested temperature setting
    """
    
    system_prompt: str
    user_context: str = ""
    conversation_history: list[dict] = field(default_factory=list)
    user_message: str = ""
    full_prompt: str = ""
    max_tokens: int = 512
    temperature: float = 0.7
    
    def to_messages(self) -> list[dict]:
        """
        Convert to OpenAI-style message format.
        
        Returns:
            List of message dictionaries
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if self.user_context:
            messages.append({
                "role": "system",
                "content": f"Context: {self.user_context}"
            })
        
        messages.extend(self.conversation_history)
        
        if self.user_message:
            messages.append({"role": "user", "content": self.user_message})
        
        return messages


class PromptBuilder:
    """
    Builds LLM prompts with safety constraints and clinical guidance.
    
    Prompts are constructed based on:
    1. Decision engine output (strategy, tone, interventions)
    2. Conversation context
    3. User preferences
    4. Hard safety constraints
    
    CLINICAL_REVIEW_REQUIRED: All prompt templates should be
    reviewed and approved by clinical team.
    """
    
    # Base system prompt with safety constraints
    # CLINICAL_REVIEW_REQUIRED
    BASE_SYSTEM_PROMPT: str = """You are HOPE, a supportive AI assistant specialized in helping people during panic attacks and moments of high anxiety.

CRITICAL SAFETY RULES (NON-NEGOTIABLE):
- NEVER provide medical diagnoses or claim the user has any specific condition
- NEVER recommend or mention specific medications or dosages
- NEVER claim to replace professional mental health care
- NEVER be dismissive of the user's experience
- NEVER promise to "cure" or "fix" their anxiety
- ALWAYS validate the user's feelings and experiences
- ALWAYS use trauma-informed, compassionate language
- ALWAYS recommend professional help for severe or recurring issues
- If the user mentions self-harm or suicide, IMMEDIATELY provide crisis resources

YOUR ROLE:
- Provide emotional support and validation
- Guide users through evidence-based coping techniques
- Help ground users in the present moment during panic
- Encourage (never replace) professional mental health care
- Be a calm, steady presence during difficult moments

COMMUNICATION STYLE:
- Keep responses focused and concise during active panic
- Use clear, simple language
- Be warm but not overly casual
- Match the user's emotional pace
- Avoid overwhelming with information during crisis moments"""
    
    # Strategy-specific additions
    STRATEGY_PROMPTS: dict[ResponseStrategy, str] = {
        ResponseStrategy.CHECK_IN: """
Current approach: Supportive check-in
- Ask open-ended questions about how they're doing
- Listen actively and reflect what you hear
- Offer general wellness support""",
        
        ResponseStrategy.ACKNOWLEDGE: """
Current approach: Acknowledge and validate
- Acknowledge what they're feeling without minimizing
- Normalize the experience of anxiety
- Offer gentle support options
- Ask if they'd like guidance on a specific technique""",
        
        ResponseStrategy.GROUND: """
Current approach: Active grounding support
- Focus on grounding in the present moment
- Guide through breathing or sensory exercises
- Keep instructions simple and step-by-step
- Encourage them through the process
- Check in after each step""",
        
        ResponseStrategy.INTERVENE: """
Current approach: Direct intervention support
- Provide immediate calming guidance
- Use short, clear sentences
- Focus on one technique at a time
- Validate that what they're feeling is temporary
- Remind them they've gotten through this before""",
        
        ResponseStrategy.CRISIS: """
Current approach: Crisis support
- Express care and concern clearly
- Provide crisis resources immediately (988, Crisis Text Line)
- Encourage reaching out to emergency services if needed
- Stay present and supportive
- Keep communication simple and direct
- MUST include: "If you're in crisis, please call or text 988"
""",
    }
    
    # Tone modifiers
    TONE_MODIFIERS: dict[ResponseTone, str] = {
        ResponseTone.WARM: "Use a warm, conversational tone. Use phrases like 'I hear you' and 'I'm here with you'.",
        ResponseTone.CALM: "Use a calm, steady tone. Speak as if you're a calm anchor in the storm.",
        ResponseTone.DIRECT: "Be direct and clear. Use short sentences. Get to the important points quickly.",
        ResponseTone.URGENT: "Acknowledge the urgency while remaining calm. Be reassuring but clear about available help.",
    }
    
    # Intervention templates
    # CLINICAL_REVIEW_REQUIRED
    INTERVENTION_TEMPLATES: dict[PanicIntervention, str] = {
        PanicIntervention.BREATHING_EXERCISE: """
Guide them through Box Breathing:
1. Acknowledge what they're feeling
2. Invite them to try a breathing exercise with you
3. Breathe in for 4 counts
4. Hold for 4 counts
5. Breathe out for 4 counts
6. Hold for 4 counts
7. Repeat and check in""",
        
        PanicIntervention.GROUNDING_TECHNIQUE: """
Guide them through 5-4-3-2-1 Grounding:
1. Acknowledge their experience
2. Explain this helps bring focus to the present
3. Name 5 things they can see
4. Name 4 things they can touch
5. Name 3 things they can hear
6. Name 2 things they can smell
7. Name 1 thing they can taste
8. Go at their pace, check in between steps""",
        
        PanicIntervention.VALIDATION: """
Focus on emotional validation:
- Acknowledge their feelings are real and valid
- Normalize the experience without minimizing
- Express understanding and empathy
- Ask what would feel supportive right now""",
        
        PanicIntervention.PROGRESSIVE_RELAXATION: """
Guide gentle progressive relaxation:
1. Start with acknowledging their experience
2. Invite them to try releasing tension
3. Focus on one muscle group at a time
4. Tense gently for 5 seconds, then release
5. Notice the difference between tension and relaxation
6. Move through body slowly""",
        
        PanicIntervention.COGNITIVE_REFRAME: """
Gentle cognitive reframing approach:
1. Listen to their thoughts without judgment
2. Acknowledge the fear feels very real
3. Gently explore the evidence
4. Help identify any thinking patterns
5. Offer alternative perspectives carefully
6. NEVER dismiss their experience""",
        
        PanicIntervention.DISTRACTION: """
Supportive distraction techniques:
1. Acknowledge what they're going through
2. Suggest gentle ways to shift focus
3. Engage in a mental activity together
4. Check in on how it's helping""",
        
        PanicIntervention.CRISIS_RESOURCES: """
CRITICAL: Crisis response required
Include these resources clearly:
- 988 Suicide & Crisis Lifeline (call or text 988)
- Crisis Text Line (text HOME to 741741)
- Emergency services (911) if immediate danger
Encourage them to reach out now, and stay present with them.""",
        
        PanicIntervention.PROFESSIONAL_REFERRAL: """
Gently encourage professional support:
- Acknowledge their strength in reaching out
- Suggest speaking with a mental health professional
- Mention that therapy can provide lasting tools
- Offer to help them think about next steps
- NEVER pressure or make them feel inadequate""",
    }
    
    # Temperature settings by strategy
    STRATEGY_TEMPERATURE: dict[ResponseStrategy, float] = {
        ResponseStrategy.CHECK_IN: 0.8,
        ResponseStrategy.ACKNOWLEDGE: 0.7,
        ResponseStrategy.GROUND: 0.5,  # Lower for consistency
        ResponseStrategy.INTERVENE: 0.4,  # Lower for reliability
        ResponseStrategy.CRISIS: 0.3,  # Lowest for critical reliability
    }
    
    def __init__(self) -> None:
        """Initialize prompt builder."""
        pass
    
    def build(
        self,
        decision: Decision,
        user_message: str,
        conversation_history: Optional[list[dict]] = None,
        user_context: Optional[str] = None,
    ) -> BuiltPrompt:
        """
        Build complete prompt from decision.
        
        Args:
            decision: Decision engine output
            user_message: Current user message
            conversation_history: Previous messages in session
            user_context: Additional context about user
            
        Returns:
            BuiltPrompt ready for LLM
        """
        if conversation_history is None:
            conversation_history = []
        
        # Build system prompt
        system_prompt = self._build_system_prompt(decision)
        
        # Build context string
        context = self._build_context(decision, user_context)
        
        # Determine parameters
        temperature = self.STRATEGY_TEMPERATURE.get(decision.strategy, 0.7)
        max_tokens = self._determine_max_tokens(decision)
        
        prompt = BuiltPrompt(
            system_prompt=system_prompt,
            user_context=context,
            conversation_history=conversation_history[-10:],  # Last 10 messages
            user_message=user_message,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        logger.debug(
            "Prompt built",
            strategy=decision.strategy.value,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return prompt
    
    def _build_system_prompt(self, decision: Decision) -> str:
        """Build complete system prompt with all components."""
        parts = [self.BASE_SYSTEM_PROMPT]
        
        # Add strategy-specific guidance
        strategy_prompt = self.STRATEGY_PROMPTS.get(decision.strategy, "")
        if strategy_prompt:
            parts.append(strategy_prompt)
        
        # Add tone modifier
        tone_modifier = self.TONE_MODIFIERS.get(decision.tone, "")
        if tone_modifier:
            parts.append(f"\nTone: {tone_modifier}")
        
        # Add primary intervention template
        if decision.primary_intervention:
            intervention_template = self.INTERVENTION_TEMPLATES.get(
                decision.primary_intervention, ""
            )
            if intervention_template:
                parts.append(f"\nIntervention approach:{intervention_template}")
        
        # Add response constraints
        if decision.response_constraints:
            constraints = "\n".join(f"- {c}" for c in decision.response_constraints[:5])
            parts.append(f"\nAdditional constraints:\n{constraints}")
        
        return "\n\n".join(parts)
    
    def _build_context(
        self,
        decision: Decision,
        user_context: Optional[str],
    ) -> str:
        """Build context string for prompt."""
        context_parts = []
        
        if user_context:
            context_parts.append(user_context)
        
        # Add modifiers as context
        modifiers = decision.prompt_modifiers
        if modifiers:
            if modifiers.get("is_recurring"):
                context_parts.append("User has experienced panic episodes before.")
            if modifiers.get("mentions_physical_symptoms"):
                context_parts.append("User mentions physical symptoms.")
            if modifiers.get("triggers"):
                triggers = ", ".join(modifiers["triggers"])
                context_parts.append(f"Possible triggers: {triggers}")
        
        return " ".join(context_parts)
    
    def _determine_max_tokens(self, decision: Decision) -> int:
        """Determine appropriate max tokens based on strategy."""
        token_limits = {
            ResponseStrategy.CHECK_IN: 256,
            ResponseStrategy.ACKNOWLEDGE: 300,
            ResponseStrategy.GROUND: 400,  # More for step-by-step guidance
            ResponseStrategy.INTERVENE: 350,
            ResponseStrategy.CRISIS: 500,  # Room for resources
        }
        return token_limits.get(decision.strategy, 300)
