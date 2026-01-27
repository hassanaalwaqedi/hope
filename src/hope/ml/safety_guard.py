"""
Clinical Intelligence Layer - Safety Guard

This module implements the SafetyGuard class which serves as a firewall
for detecting safety-critical content in client messages using compiled
regex patterns for both English and Arabic.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Pattern


@dataclass(frozen=True)
class SafetyScanResult:
    """
    Immutable result from a safety scan operation.
    
    Attributes:
        is_safe: True if no critical safety concerns detected
        flags: List of triggered safety categories
        severity: Overall severity level ("none", "low", "medium", "high", "critical")
    """
    is_safe: bool
    flags: List[str] = field(default_factory=list)
    severity: str = "none"

    def to_dict(self) -> Dict[str, object]:
        """Convert to dictionary representation."""
        return {
            "is_safe": self.is_safe,
            "flags": self.flags,
            "severity": self.severity
        }


class SafetyGuard:
    """
    Safety firewall for detecting critical safety concerns in client messages.
    
    Compiles regex patterns at initialization for optimal performance.
    Supports both English and Arabic language patterns.
    
    Pattern Categories:
        - SUICIDE: Suicidal ideation or intent
        - DANGER: Physical danger or threat to safety
        - MEDICAL: Medical emergency indicators
    
    Usage:
        guard = SafetyGuard()
        result = guard.scan("I want to end it all")
        if not result["is_safe"]:
            handle_safety_concern(result["flags"])
    """

    # Pattern constants - compiled once at class instantiation
    SUICIDE_PATTERN_RAW: str = (
        r"(suicid|kill myself|want to die|end it all|better off dead|"
        r"انتحار|بموت|عايز اموت|بنهي حياتي|اقتل نفسي)"
    )
    
    DANGER_PATTERN_RAW: str = (
        r"(following me|not safe|hurt me|stalk|weapon|danger|"
        r"يلاحقني|خايف|سلاح|خطر|مش امان|حد بيطاردني)"
    )
    
    MEDICAL_PATTERN_RAW: str = (
        r"(heart attack|chest pain|faint|stroke|pain in left arm|"
        r"نوبة قلبية|وجع صدر|الم في صدري|يغمى علي|جلطة)"
    )

    def __init__(self) -> None:
        """
        Initialize SafetyGuard with pre-compiled regex patterns.
        
        Patterns are compiled with IGNORECASE and UNICODE flags for
        comprehensive matching across languages and case variations.
        """
        self._suicide_pattern: Pattern[str] = re.compile(
            self.SUICIDE_PATTERN_RAW,
            re.IGNORECASE | re.UNICODE
        )
        self._danger_pattern: Pattern[str] = re.compile(
            self.DANGER_PATTERN_RAW,
            re.IGNORECASE | re.UNICODE
        )
        self._medical_pattern: Pattern[str] = re.compile(
            self.MEDICAL_PATTERN_RAW,
            re.IGNORECASE | re.UNICODE
        )

    def scan(self, text: str) -> Dict[str, object]:
        """
        Scan input text for safety-critical content.
        
        Args:
            text: The client message text to analyze
            
        Returns:
            Dictionary containing:
                - is_safe (bool): True if no critical concerns detected
                - flags (List[str]): List of triggered safety categories
                - severity (str): Overall severity level
                
        Severity Levels:
            - "none": No safety concerns
            - "low": Medical concerns only
            - "medium": Danger/threat detected
            - "high": Suicide ideation detected
            - "critical": Multiple critical flags detected
            
        Example:
            >>> guard = SafetyGuard()
            >>> result = guard.scan("I feel safe and calm")
            >>> result["is_safe"]
            True
            >>> result = guard.scan("I want to end it all")
            >>> result["is_safe"]
            False
            >>> "SUICIDE_RISK" in result["flags"]
            True
        """
        flags: List[str] = []
        
        # Check for suicide-related content
        suicide_match = self._suicide_pattern.search(text)
        if suicide_match:
            flags.append("SUICIDE_RISK")
        
        # Check for danger/threat content
        danger_match = self._danger_pattern.search(text)
        if danger_match:
            flags.append("DANGER_THREAT")
        
        # Check for medical emergency indicators
        medical_match = self._medical_pattern.search(text)
        if medical_match:
            flags.append("MEDICAL_EMERGENCY")
        
        # Determine overall safety and severity
        is_safe = self._determine_safety(flags)
        severity = self._calculate_severity(flags)
        
        result = SafetyScanResult(
            is_safe=is_safe,
            flags=flags,
            severity=severity
        )
        
        return result.to_dict()

    def _determine_safety(self, flags: List[str]) -> bool:
        """
        Determine if the input is safe based on detected flags.
        
        Args:
            flags: List of detected safety concern categories
            
        Returns:
            False if SUICIDE_RISK or DANGER_THREAT detected, True otherwise
        """
        critical_flags = {"SUICIDE_RISK", "DANGER_THREAT"}
        return not any(flag in critical_flags for flag in flags)

    def _calculate_severity(self, flags: List[str]) -> str:
        """
        Calculate overall severity level based on detected flags.
        
        Args:
            flags: List of detected safety concern categories
            
        Returns:
            Severity string: "none", "low", "medium", "high", or "critical"
        """
        if not flags:
            return "none"
        
        # Count critical flags
        has_suicide = "SUICIDE_RISK" in flags
        has_danger = "DANGER_THREAT" in flags
        has_medical = "MEDICAL_EMERGENCY" in flags
        
        # Multiple critical concerns
        critical_count = sum([has_suicide, has_danger])
        if critical_count >= 2 or (critical_count >= 1 and has_medical):
            return "critical"
        
        # Single critical concern
        if has_suicide:
            return "high"
        
        if has_danger:
            return "medium"
        
        if has_medical:
            return "low"
        
        return "none"

    def scan_batch(self, texts: List[str]) -> List[Dict[str, object]]:
        """
        Scan multiple texts for safety concerns.
        
        Args:
            texts: List of client messages to analyze
            
        Returns:
            List of scan results, one per input text
        """
        return [self.scan(text) for text in texts]
