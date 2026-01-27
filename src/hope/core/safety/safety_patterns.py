"""
Multilingual Safety Patterns

Regex patterns for detecting crisis intent across 10 global languages.
Focus is on CLEAR INTENT (suicide, self-harm) rather than general distress.

Supported: EN, FR, ES, AR, TR, DE, IT, SV, KO, JA
"""

import re
from typing import Dict, List, Pattern

class SafetyPatterns:
    """Crisis detection patterns for multi-language support."""
    
    # Crisis patterns by language code
    # These match "I want to kill myself", "I want to die", "I'm going to end it" variations
    PATTERNS: Dict[str, List[str]] = {
        "en": [
            r"i want to (kill|end) (myself|it|my life)",
            r"i('m| am) going to (kill|end) (myself|it|my life)",
            r"i want to die",
            r"better off dead",
            r"suicide",
            r"kill myself",
        ],
        "fr": [
            r"je veux (me tuer|mourir|en finir)",
            r"je vais (me tuer|en finir|me suicider)",
            r"je pense au suicide",
            r"envie de mourir",
            r"me faire du mal",
        ],
        "es": [
            r"(quiero|voy a) (matarme|suicidarme|morir)",
            r"(quiero|voy a) quitarme la vida",
            r"acabar con todo",
            r"pensando en el suicidio",
            r"deseo morir",
        ],
        "ar": [
            r"(أريد|bghit|bghet) (أن)? (أنتحر|amout|amot|amoot|أموت)",
            r"(أفكر|kanfaker) (في)? (الانتحار|suicide|lmont)",
            r"(بقتل|baqtal) (حالي|nefsi|nfsy)",
            r"خلاص تعبت من الحياة", # "I'm done/tired of life" (context dependent, but high risk in crisis context)
            r"إنهاء حياتي",
        ],
        "tr": [
            r"(kendimi|hayatımı) (öldürmek|bitirmek|sonlandırmak) (istiyorum|düşünüyorum)",
            r"ölmek istiyorum",
            r"intihar (etmek|düşüncesi)",
            r"yaşamak istemiyorum",
            r"bıktım artık bu hayattan", # "Fed up with this life"
        ],
        "de": [
            r"ich (will|möchte) (mich töten|sterben|mein leben beenden)",
            r"ich (werde|bringe) mich (umbringen|um)",
            r"selbstmord",
            r"freitod",
            r"nicht mehr leben",
        ],
        "it": [
            r"(voglio|desidero) (uccidermi|morire|farla finita)",
            r"(mi|me) (ammazzo|uccido)",
            r"suicidio",
            r"togliermi la vita",
            r"non voglio più vivere",
        ],
        "sv": [
            r"jag (vill|ska) (dö|ta livet av mig|begå självmord)",
            r"vill inte leva (längre)?",
            r"orkar inte mer", # "Can't take it anymore"
            r"självmord",
        ],
        "ko": [
            r"(죽고|juko) (싶어|sip-eo|sipeo)", # "Want to die"
            r"(자살|jasal)", # "Suicide"
            r"(그만|geuman) (살고|salgo) (싶어|sipeo)", # "Stop living"
            r"(뛰어내리|ttwieonaeli)", # "Jump off"
            r"(죽을|jugeul) (거야|geoya)", # "Going to die"
        ],
        "ja": [
            r"(死にたい|shinitai)", # "Want to die"
            r"(殺して|koroshite)", # "Kill me"
            r"(消えたい|kietai)", # "Want to disappear" (often precursor)
            r"(自殺|jisatsu)", # "Suicide"
            r"(もう|mou) (嫌|iya|iyada)", # "I can't take it" (context)
            r"(終わり|owari) (に)? (したい|shitai)", # "Want to end it"
        ]
    }

    # Pre-compiled regex cache
    _COMPILED: Dict[str, List[Pattern]] = {}

    @classmethod
    def get_patterns(cls, language: str) -> List[Pattern]:
        """Get compiled patterns for a language."""
        lang = language.lower()[:2]
        if lang not in cls._COMPILED:
            patterns = cls.PATTERNS.get(lang, cls.PATTERNS["en"])
            cls._COMPILED[lang] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]
        return cls._COMPILED.get(lang, [])

    @classmethod
    def check_crisis(cls, text: str, language: str) -> bool:
        """Check text against crisis patterns for specific language."""
        patterns = cls.get_patterns(language)
        return any(p.search(text) for p in patterns)
