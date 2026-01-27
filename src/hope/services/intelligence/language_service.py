"""
Language Service - Global Intelligence Orchestrator

Manages language detection, directionality (RTL), and locale-specific safety.
Connects raw detection logic with application context.
"""

from typing import Optional, Tuple
from dataclasses import dataclass

from langdetect import detect, detect_langs, LangDetectException

from hope.config.logging_config import get_logger
from hope.core.safety.safety_patterns import SafetyPatterns

logger = get_logger(__name__)


@dataclass
class LanguageContext:
    """Context for language-specific behavior."""
    code: str  # 'en', 'fr', 'ar', etc.
    name: str
    is_rtl: bool
    confidence: float
    region_hint: Optional[str] = None


class LanguageService:
    """
    Central service for multi-language intelligence.
    
    Supported: EN, FR, ES, AR, TR, DE, IT, SV, KO, JA
    """
    
    SUPPORTED_LANGUAGES = {
        "en": {"name": "English", "rtl": False},
        "fr": {"name": "French", "rtl": False},
        "es": {"name": "Spanish", "rtl": False},
        "ar": {"name": "Arabic", "rtl": True},
        "tr": {"name": "Turkish", "rtl": False},
        "de": {"name": "German", "rtl": False},
        "it": {"name": "Italian", "rtl": False},
        "sv": {"name": "Swedish", "rtl": False},
        "ko": {"name": "Korean", "rtl": False},
        "ja": {"name": "Japanese", "rtl": False},
    }
    
    DEFAULT_LANGUAGE = "en"
    
    def detect_language(self, text: str, default: Optional[str] = None) -> LanguageContext:
        """
        Detect language from text with fallback.
        Includes heuristics for short text.
        """
        if not text or len(text.strip()) < 3:
            return self._get_context(default or self.DEFAULT_LANGUAGE, confidence=1.0)
            
        try:
            # Langdetect is fast but needs enough text
            detected = detect(text)
            
            # If supported, return it
            if detected in self.SUPPORTED_LANGUAGES:
                return self._get_context(detected, confidence=0.9)
                
            # Fallback for dialects or similar langs
            # e.g., 'no' (Norwegian) -> 'sv' (Swedish) map? No, strict for now.
            logger.warning(f"Detected unsupported language: {detected}")
            return self._get_context(default or self.DEFAULT_LANGUAGE, confidence=0.5)
            
        except LangDetectException:
            return self._get_context(default or self.DEFAULT_LANGUAGE, confidence=0.0)
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return self._get_context(default or self.DEFAULT_LANGUAGE, confidence=0.0)

    def check_safety_for_language(self, text: str, language_code: str) -> bool:
        """
        Check specific safety patterns for the language.
        Returns True if CRISIS detected.
        """
        return SafetyPatterns.check_crisis(text, language_code)

    def _get_context(self, code: str, confidence: float) -> LanguageContext:
        """Build context object from code."""
        info = self.SUPPORTED_LANGUAGES.get(code, self.SUPPORTED_LANGUAGES[self.DEFAULT_LANGUAGE])
        return LanguageContext(
            code=code,
            name=info["name"],
            is_rtl=info["rtl"],
            confidence=confidence,
        )

# Singleton
_language_service = LanguageService()

def get_language_service() -> LanguageService:
    return _language_service
