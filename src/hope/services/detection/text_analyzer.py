"""
Text Analyzer

Analyzes text input for panic indicators using rule-based
and ML-based approaches.

CLINICAL_REVIEW_REQUIRED: Panic indicator patterns and 
thresholds require clinical validation before production use.
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TextAnalysisResult:
    """
    Results from text analysis.
    
    Attributes:
        raw_text: Original input text
        normalized_text: Cleaned/normalized text
        word_count: Number of words
        panic_keywords_found: Panic-related keywords detected
        crisis_indicators: Critical safety indicators
        intensity_markers: Words/patterns indicating intensity
        physiological_mentions: Physical symptom mentions
        cognitive_patterns: Thought patterns (catastrophizing, etc.)
        temporal_urgency: Time-related urgency markers
        risk_score: Calculated risk score (0.0-1.0)
        requires_immediate_attention: Critical flag
    """
    
    raw_text: str
    normalized_text: str = ""
    word_count: int = 0
    panic_keywords_found: list[str] = field(default_factory=list)
    crisis_indicators: list[str] = field(default_factory=list)
    intensity_markers: list[str] = field(default_factory=list)
    physiological_mentions: list[str] = field(default_factory=list)
    cognitive_patterns: list[str] = field(default_factory=list)
    temporal_urgency: list[str] = field(default_factory=list)
    risk_score: float = 0.0
    requires_immediate_attention: bool = False
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "word_count": self.word_count,
            "panic_keywords_count": len(self.panic_keywords_found),
            "crisis_indicators_count": len(self.crisis_indicators),
            "risk_score": self.risk_score,
            "requires_immediate_attention": self.requires_immediate_attention,
        }


class TextAnalyzer:
    """
    Analyzes text for panic attack indicators.
    
    Uses pattern matching and keyword detection as a first-pass
    filter before ML model inference.
    
    CLINICAL_REVIEW_REQUIRED: All keyword lists and patterns
    should be reviewed by mental health professionals.
    """
    
    # Panic-related keywords
    # CLINICAL_REVIEW_REQUIRED: Validate and expand these lists
    PANIC_KEYWORDS: frozenset[str] = frozenset({
        "panic", "panicking", "panicked",
        "attack", "anxiety", "anxious",
        "cant breathe", "can't breathe", "cannot breathe",
        "dying", "heart attack", "going crazy",
        "losing control", "losing my mind",
        "terrified", "terror", "scared",
        "overwhelming", "overwhelmed",
        "shaking", "trembling",
    })
    
    # Crisis indicators requiring immediate attention
    # SAFETY_CRITICAL: These trigger immediate escalation
    CRISIS_INDICATORS: frozenset[str] = frozenset({
        "suicide", "suicidal", "kill myself",
        "want to die", "end my life", "end it all",
        "self harm", "self-harm", "hurt myself",
        "no reason to live", "better off dead",
    })
    
    # Intensity markers
    INTENSITY_MARKERS: frozenset[str] = frozenset({
        "very", "extremely", "so much",
        "worst", "terrible", "horrible",
        "unbearable", "intense", "severe",
        "can't take it", "too much",
    })
    
    # Physiological symptom mentions
    PHYSIOLOGICAL_PATTERNS: list[re.Pattern] = [
        re.compile(r"heart\s*(is\s*)?(racing|pounding|beating fast)", re.I),
        re.compile(r"(can't|cannot|cant)\s*breathe", re.I),
        re.compile(r"(chest|heart)\s*(pain|tight|hurts)", re.I),
        re.compile(r"(dizzy|lightheaded|faint)", re.I),
        re.compile(r"(shaking|trembling|shivering)", re.I),
        re.compile(r"(sweating|sweaty|cold sweat)", re.I),
        re.compile(r"(numb|tingling|pins and needles)", re.I),
        re.compile(r"(nausea|nauseous|sick to my stomach)", re.I),
    ]
    
    # Cognitive patterns (catastrophizing, etc.)
    COGNITIVE_PATTERNS: list[re.Pattern] = [
        re.compile(r"(going to|gonna)\s*(die|have a heart attack)", re.I),
        re.compile(r"something (terrible|awful|bad)\s*(is|will)\s*happen", re.I),
        re.compile(r"losing\s*(control|my mind|it)", re.I),
        re.compile(r"(never|won't)\s*(end|stop|get better)", re.I),
        re.compile(r"(everyone|they)\s*(will|can)\s*see", re.I),
        re.compile(r"what if", re.I),
    ]
    
    # Temporal urgency markers
    TEMPORAL_URGENCY: frozenset[str] = frozenset({
        "right now", "happening now", "at this moment",
        "can't wait", "need help now", "emergency",
        "immediately", "urgent", "asap",
    })
    
    # Weights for risk score calculation
    WEIGHTS: dict[str, float] = {
        "panic_keyword": 0.15,
        "crisis_indicator": 0.5,  # Heavily weighted
        "intensity_marker": 0.08,
        "physiological": 0.12,
        "cognitive_pattern": 0.10,
        "temporal_urgency": 0.10,
    }
    
    def __init__(self) -> None:
        """Initialize text analyzer."""
        pass
    
    def analyze(self, text: str) -> TextAnalysisResult:
        """
        Analyze text for panic indicators.
        
        Args:
            text: User input text
            
        Returns:
            TextAnalysisResult with detected patterns and risk score
        """
        if not text or not text.strip():
            return TextAnalysisResult(raw_text=text)
        
        # Normalize text
        normalized = self._normalize_text(text)
        text_lower = normalized.lower()
        
        # Detect patterns
        panic_keywords = self._find_keywords(text_lower, self.PANIC_KEYWORDS)
        crisis_indicators = self._find_keywords(text_lower, self.CRISIS_INDICATORS)
        intensity_markers = self._find_keywords(text_lower, self.INTENSITY_MARKERS)
        physiological = self._find_patterns(text_lower, self.PHYSIOLOGICAL_PATTERNS)
        cognitive = self._find_patterns(text_lower, self.COGNITIVE_PATTERNS)
        temporal = self._find_keywords(text_lower, self.TEMPORAL_URGENCY)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(
            panic_count=len(panic_keywords),
            crisis_count=len(crisis_indicators),
            intensity_count=len(intensity_markers),
            physiological_count=len(physiological),
            cognitive_count=len(cognitive),
            temporal_count=len(temporal),
        )
        
        # Immediate attention flag
        requires_immediate = len(crisis_indicators) > 0 or risk_score >= 0.7
        
        return TextAnalysisResult(
            raw_text=text,
            normalized_text=normalized,
            word_count=len(normalized.split()),
            panic_keywords_found=panic_keywords,
            crisis_indicators=crisis_indicators,
            intensity_markers=intensity_markers,
            physiological_mentions=physiological,
            cognitive_patterns=cognitive,
            temporal_urgency=temporal,
            risk_score=min(1.0, risk_score),
            requires_immediate_attention=requires_immediate,
        )
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for analysis.
        
        Args:
            text: Raw input text
            
        Returns:
            Normalized text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Normalize common contractions
        text = re.sub(r"(\w)'(\w)", r"\1'\2", text)
        return text
    
    def _find_keywords(
        self,
        text: str,
        keywords: frozenset[str],
    ) -> list[str]:
        """
        Find keywords in text.
        
        Args:
            text: Lowercased text to search
            keywords: Set of keywords to find
            
        Returns:
            List of found keywords
        """
        found = []
        for keyword in keywords:
            if keyword in text:
                found.append(keyword)
        return found
    
    def _find_patterns(
        self,
        text: str,
        patterns: list[re.Pattern],
    ) -> list[str]:
        """
        Find regex patterns in text.
        
        Args:
            text: Text to search
            patterns: Compiled regex patterns
            
        Returns:
            List of matched strings
        """
        found = []
        for pattern in patterns:
            matches = pattern.findall(text)
            if matches:
                found.extend(matches if isinstance(matches[0], str) else [m[0] for m in matches])
        return found
    
    def _calculate_risk_score(
        self,
        panic_count: int,
        crisis_count: int,
        intensity_count: int,
        physiological_count: int,
        cognitive_count: int,
        temporal_count: int,
    ) -> float:
        """
        Calculate composite risk score.
        
        CLINICAL_REVIEW_REQUIRED: Scoring weights and formula
        should be validated against clinical outcomes.
        
        Args:
            Various pattern counts
            
        Returns:
            Risk score (0.0-1.0)
        """
        score = 0.0
        
        # Crisis indicators are critical
        if crisis_count > 0:
            score += self.WEIGHTS["crisis_indicator"] * min(crisis_count, 2)
        
        # Panic keywords
        score += self.WEIGHTS["panic_keyword"] * min(panic_count, 3)
        
        # Intensity
        score += self.WEIGHTS["intensity_marker"] * min(intensity_count, 3)
        
        # Physiological symptoms
        score += self.WEIGHTS["physiological"] * min(physiological_count, 4)
        
        # Cognitive patterns
        score += self.WEIGHTS["cognitive_pattern"] * min(cognitive_count, 3)
        
        # Temporal urgency
        if temporal_count > 0:
            score += self.WEIGHTS["temporal_urgency"]
        
        return min(1.0, score)
