"""
Clinical Intelligence Layer - Regulation Engine

This module implements the RegulationEngine class which serves as the
core state machine for determining clinical responses based on client
input, intensity levels, and safety concerns.
"""

import re
from typing import Pattern, Set

from hope.ml.contracts import (
    ClientState,
    ClinicalInput,
    ClinicalResponse,
    InterventionTool,
)
from hope.ml.safety_guard import SafetyGuard


class RegulationEngine:
    """
    Core state machine for clinical response generation.
    
    Processes client input through a three-stage pipeline:
        1. Safety Check: Detect critical safety concerns
        2. Panic Detection: Identify high-intensity distress or panic keywords
        3. Regulation Logic: Determine appropriate intervention based on intensity
    
    The engine maintains no internal state between calls, making it
    thread-safe and suitable for concurrent request handling.
    
    Usage:
        engine = RegulationEngine()
        response = engine.process(ClinicalInput(
            text="I can't breathe",
            current_intensity=8,
            language="en"
        ))
        print(response.next_state)  # ClientState.PANIC_MODE
    """

    # Panic keywords for English and Arabic
    PANIC_KEYWORDS_EN: Set[str] = {
        "panic",
        "can't breathe",
        "cannot breathe",
        "cant breathe",
        "dying",
        "help",
        "heart racing",
        "can't stop shaking",
        "terrified",
        "losing control",
    }
    
    PANIC_KEYWORDS_AR: Set[str] = {
        "هلع",
        "اموت",
        "بموت",
        "مش قادر اتنفس",
        "مش قادرة اتنفس",
        "خايف",
        "خايفة",
        "مرعوب",
        "مرعوبة",
        "قلبي بيدق",
        "حاسس اني بموت",
    }

    # Scripted responses
    RESPONSES = {
        "en": {
            "danger": (
                "I am detecting a safety concern. I am switching to safety mode. "
                "Please use the buttons below to contact help immediately."
            ),
            "panic": (
                "I am here. You are safe. Let's focus on your breathing right now. "
                "Follow the circle."
            ),
            "regulation": (
                "Let's ground ourselves. Can you tap 3 things you see around you?"
            ),
            "check_in": (
                "You seem calmer now. How are you feeling about what happened?"
            ),
        },
        "ar": {
            "danger": (
                "أشعر بوجود قلق على سلامتك. أنا أنتقل إلى وضع السلامة. "
                "من فضلك استخدم الأزرار أدناه للتواصل مع المساعدة فوراً."
            ),
            "panic": (
                "أنا هنا معك. أنت بأمان. دعنا نركز على تنفسك الآن. "
                "تابع الدائرة."
            ),
            "regulation": (
                "دعنا نعيد التوازن لأنفسنا. هل يمكنك النقر على ٣ أشياء تراها حولك؟"
            ),
            "check_in": (
                "يبدو أنك أهدأ الآن. كيف تشعر بخصوص ما حدث؟"
            ),
        },
    }

    def __init__(self) -> None:
        """
        Initialize the RegulationEngine with SafetyGuard and compiled patterns.
        """
        self._safety_guard = SafetyGuard()
        
        # Compile panic keyword patterns for efficient matching
        # Create pattern that matches any panic keyword (case-insensitive)
        en_pattern = "|".join(re.escape(kw) for kw in self.PANIC_KEYWORDS_EN)
        ar_pattern = "|".join(re.escape(kw) for kw in self.PANIC_KEYWORDS_AR)
        
        self._panic_pattern_en: Pattern[str] = re.compile(
            en_pattern,
            re.IGNORECASE | re.UNICODE
        )
        self._panic_pattern_ar: Pattern[str] = re.compile(
            ar_pattern,
            re.UNICODE
        )

    def process(self, input_data: ClinicalInput) -> ClinicalResponse:
        """
        Process client input and generate appropriate clinical response.
        
        This method implements the core state machine logic:
        
        Step 1 - Safety Check:
            If safety concerns detected (suicide/danger), immediately
            return DANGER_MODE with SAFETY_SCREEN.
            
        Step 2 - Panic Detection:
            If intensity >= 6 OR panic keywords detected, return
            PANIC_MODE with BREATHING_CIRCLE.
            
        Step 3 - Regulation Logic:
            - Intensity 4-5: REGULATION_MODE with GROUNDING_54321
            - Intensity 1-3: CHECK_IN_MODE with NONE (text only)
        
        Args:
            input_data: ClinicalInput containing text, intensity, and language
            
        Returns:
            ClinicalResponse with next_state, tool, scripted_text, and flags
        """
        text = input_data.text
        intensity = input_data.current_intensity
        language = input_data.language if input_data.language in ("en", "ar") else "en"
        
        # ============================================================
        # STEP 1: SAFETY CHECK
        # ============================================================
        safety_result = self._safety_guard.scan(text)
        
        if not safety_result["is_safe"]:
            return ClinicalResponse(
                next_state=ClientState.DANGER_MODE,
                tool_to_render=InterventionTool.SAFETY_SCREEN,
                scripted_text=self.RESPONSES[language]["danger"],
                safety_flags=safety_result["flags"]
            )
        
        # ============================================================
        # STEP 2: PANIC DETECTION
        # ============================================================
        has_panic_keywords = self._detect_panic_keywords(text, language)
        
        if intensity >= 6 or has_panic_keywords:
            return ClinicalResponse(
                next_state=ClientState.PANIC_MODE,
                tool_to_render=InterventionTool.BREATHING_CIRCLE,
                scripted_text=self.RESPONSES[language]["panic"],
                safety_flags=[]
            )
        
        # ============================================================
        # STEP 3: REGULATION / CALM LOGIC
        # ============================================================
        if 4 <= intensity <= 5:
            return ClinicalResponse(
                next_state=ClientState.REGULATION_MODE,
                tool_to_render=InterventionTool.GROUNDING_54321,
                scripted_text=self.RESPONSES[language]["regulation"],
                safety_flags=[]
            )
        
        # Intensity <= 3: Client is calm
        return ClinicalResponse(
            next_state=ClientState.CHECK_IN_MODE,
            tool_to_render=InterventionTool.NONE,
            scripted_text=self.RESPONSES[language]["check_in"],
            safety_flags=[]
        )

    def _detect_panic_keywords(self, text: str, language: str) -> bool:
        """
        Detect panic-related keywords in the input text.
        
        Args:
            text: Client message text
            language: Language code ("en" or "ar")
            
        Returns:
            True if any panic keyword is detected
        """
        # Always check both patterns for bilingual users
        en_match = self._panic_pattern_en.search(text)
        ar_match = self._panic_pattern_ar.search(text)
        
        return bool(en_match or ar_match)

    def get_supported_languages(self) -> Set[str]:
        """
        Get the set of supported language codes.
        
        Returns:
            Set of ISO language codes
        """
        return set(self.RESPONSES.keys())

    def get_panic_keywords(self, language: str) -> Set[str]:
        """
        Get panic keywords for a specific language.
        
        Args:
            language: ISO language code ("en" or "ar")
            
        Returns:
            Set of panic keywords for the specified language
        """
        if language == "ar":
            return self.PANIC_KEYWORDS_AR.copy()
        return self.PANIC_KEYWORDS_EN.copy()
