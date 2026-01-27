"""
Dynamic Prompt System - Multilingual Intelligence

Generates system instructions tailored to 10 languages.
Ensures native-feeling empathy and cultural nuance.
"""

from typing import Dict

class PromptBuilder:
    """Builds localized system prompts."""
    
    # Core personality traits (universal)
    CORE_PERSONALITY = """You are HOPE, an empathetic AI mental-health assistant.
Your goal is to provide compassionate, intelligent support in the user's language.
You are NOT a chatbot. You are a skilled AI therapist assistant."""

    # Language-specific nuances
    # Instructions to Gemini on HOW to speak this language
    LANG_INSTRUCTIONS: Dict[str, str] = {
        "en": "Speak naturally, use contractions. Be warm but professional.",
        "fr": "Utilisez le vouvoiement empathique ou le tutoiement si l'utilisateur le demande. Soyez chaleureux et respectueux.",
        "es": "Usa un tono cercano y empático. Adapta tu vocabulario para ser comprensible en España y Latinoamérica.",
        "ar": "تحدث بلغة عربية فصحى معاصرة ودافئة. تجنب الركاكة. كن متعاطفاً جداً ومحترماً.",
        "tr": "Samimi ve destekleyici bir dil kullan. 'Siz' diliyle başla, gerekirse 'sen' diline geç. Kültürel olarak duyarlı ol.",
        "de": "Sei einfühlsam und professionell. Nutze eine natürliche, aber respektvolle Sprache.",
        "it": "Usa un tono caldo e accogliente. Sii empatico e naturale.",
        "sv": "Var varm och stöttande. Använd ett naturligt språk.",
        "ko": "따뜻하고 공감하는 어조로 말하세요. 존댓말을 사용하며, 한국의 정서적 맥락을 고려하세요.",
        "ja": "温かく、共感的な口調で話してください。丁寧語（です・ます調）を使用し、相手の感情に寄り添ってください。",
    }
    
    # Universal rules
    RULES = """
## CORE RULES
1. ALWAYS respond in the USER'S language ({language_name}).
2. Do not translate literally; localize emotionally.
3. If the user switches language, switch with them immediately.
4. Never say "As an AI". Be a present, listening entity.
5. Validate feelings before offering suggestions.
"""

    @classmethod
    def get_system_prompt(cls, language_code: str) -> str:
        """Generate full system prompt for a specific language."""
        lang_code = language_code.lower()
        
        # Fallback to English if unknown
        if lang_code not in cls.LANG_INSTRUCTIONS:
            lang_code = "en"
            
        lang_name = cls._get_lang_name(lang_code)
        lang_instruction = cls.LANG_INSTRUCTIONS[lang_code]
        
        return f"""{cls.CORE_PERSONALITY}

## LANGUAGE INSTRUCTION: {lang_name}
{lang_instruction}

{cls.RULES.format(language_name=lang_name)}

## SAFETY
- Normal sadness/anxiety is okay to discuss.
- Only escalate if you detect CLEAR suicide/self-harm intent.
- Be supportive, never judgmental.
"""

    @staticmethod
    def _get_lang_name(code: str) -> str:
        names = {
            "en": "English", "fr": "French", "es": "Spanish",
            "ar": "Arabic", "tr": "Turkish", "de": "German",
            "it": "Italian", "sv": "Swedish", "ko": "Korean",
            "ja": "Japanese"
        }
        return names.get(code, "English")
