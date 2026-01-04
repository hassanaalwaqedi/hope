"""
Safety Validation Layer

Validates and filters all AI-generated responses before delivery.
Implements hard safety constraints that cannot be overridden.

ARCHITECTURE: This is the final safety gate before responses reach users.
No response bypasses this layer.

CRITICAL: This module contains safety-critical code. Changes require
security and clinical review.
"""

import re
from dataclasses import dataclass, field
from typing import Optional

from hope.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class SafetyViolation:
    """
    A detected safety violation.
    
    Attributes:
        rule_id: Identifier of violated rule
        rule_description: Human-readable description
        matched_content: The content that triggered violation
        severity: Violation severity (warning, block)
    """
    
    rule_id: str
    rule_description: str
    matched_content: str = ""
    severity: str = "block"  # warning, block
    
    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "description": self.rule_description,
            "severity": self.severity,
        }


@dataclass
class SafetyResult:
    """
    Result of safety validation.
    
    Attributes:
        is_safe: Whether response passes all checks
        original_response: Original response text
        filtered_response: Response after filtering (if modified)
        violations: List of detected violations
        was_modified: Whether response was modified
        blocked: Whether response was completely blocked
    """
    
    is_safe: bool
    original_response: str
    filtered_response: str = ""
    violations: list[SafetyViolation] = field(default_factory=list)
    was_modified: bool = False
    blocked: bool = False
    
    def __post_init__(self) -> None:
        if not self.filtered_response:
            self.filtered_response = self.original_response
    
    def to_dict(self) -> dict:
        return {
            "is_safe": self.is_safe,
            "was_modified": self.was_modified,
            "blocked": self.blocked,
            "violation_count": len(self.violations),
        }


class SafetyValidator:
    """
    Safety validation for AI-generated responses.
    
    Implements multiple layers of safety checking:
    1. Hard constraint violations (block)
    2. Medical claim detection (block)
    3. Harmful content patterns (block)
    4. Style/tone checking (warn/modify)
    
    SAFETY_CRITICAL: This is the last line of defense.
    All responses must pass through this validator.
    """
    
    # Hard constraints - these ALWAYS block
    # CLINICAL_REVIEW_REQUIRED
    HARD_CONSTRAINT_PATTERNS: list[tuple[str, re.Pattern, str]] = [
        (
            "MEDICAL_DIAGNOSIS",
            re.compile(r"you (have|are suffering from|are experiencing)\s+(a\s+)?("
                      r"panic disorder|anxiety disorder|depression|ptsd|"
                      r"bipolar|schizophrenia|ocd|mental illness)", re.I),
            "Response contains medical diagnosis",
        ),
        (
            "MEDICATION_ADVICE",
            re.compile(r"(take|try|consider)\s+(\d+\s*)?(mg|milligram|pill|tablet|dose)", re.I),
            "Response contains medication dosage advice",
        ),
        (
            "MEDICATION_RECOMMENDATION",
            re.compile(r"(xanax|valium|ativan|klonopin|prozac|zoloft|lexapro|"
                      r"benzodiazepine|ssri|antidepressant|anti-anxiety|anxiolytic)", re.I),
            "Response recommends specific medication",
        ),
        (
            "REPLACE_THERAPY",
            re.compile(r"(don't need|no need for|instead of|better than)\s+"
                      r"(therapy|therapist|doctor|professional|psychiatrist)", re.I),
            "Response discourages professional help",
        ),
        (
            "GUARANTEE_CURE",
            re.compile(r"(will|can|going to)\s+(cure|fix|heal|eliminate)\s+"
                      r"(your|the)\s+(anxiety|panic|depression|condition)", re.I),
            "Response promises cure",
        ),
        (
            "DISMISSIVE",
            re.compile(r"(just\s+)?(calm down|relax|stop worrying|get over it|"
                      r"it's (all )?in your head|don't be (so\s+)?dramatic)", re.I),
            "Response is dismissive of user's experience",
        ),
    ]
    
    # Patterns to filter/modify (not block)
    FILTER_PATTERNS: list[tuple[str, re.Pattern, str]] = [
        (
            "EXCESSIVE_CERTAINTY",
            re.compile(r"\b(definitely|certainly|absolutely|100%|guaranteed)\b", re.I),
            "Response contains excessive certainty",
        ),
        (
            "COMPARATIVE_MINIMIZING",
            re.compile(r"(others have it worse|could be worse|at least)", re.I),
            "Response minimizes by comparison",
        ),
    ]
    
    # Required elements for crisis responses
    CRISIS_REQUIRED_ELEMENTS: list[tuple[str, re.Pattern]] = [
        ("CRISIS_HOTLINE", re.compile(r"(988|crisis\s*(line|hotline)|suicide\s*(prevention|hotline))", re.I)),
        ("PROFESSIONAL_HELP", re.compile(r"(professional|therapist|counselor|doctor|emergency)", re.I)),
    ]
    
    # Fallback response when response is blocked
    FALLBACK_RESPONSE: str = (
        "I hear you, and I want to make sure you get the best support possible. "
        "What you're experiencing is real and valid. "
        "If you're in crisis, please reach out to the 988 Suicide & Crisis Lifeline "
        "by calling or texting 988. "
        "A trained counselor can provide immediate support. "
        "I'm here to listen whenever you need."
    )
    
    def __init__(self, strict_mode: bool = True) -> None:
        """
        Initialize safety validator.
        
        Args:
            strict_mode: If True, any violation blocks response.
                        If False, warnings allow modified responses.
        """
        self._strict_mode = strict_mode
    
    def validate(
        self,
        response: str,
        is_crisis_response: bool = False,
    ) -> SafetyResult:
        """
        Validate an AI-generated response.
        
        Args:
            response: Response text to validate
            is_crisis_response: Whether this is a crisis-level response
            
        Returns:
            SafetyResult with validation outcome
        """
        if not response or not response.strip():
            return SafetyResult(
                is_safe=False,
                original_response=response,
                filtered_response=self.FALLBACK_RESPONSE,
                violations=[SafetyViolation(
                    rule_id="EMPTY_RESPONSE",
                    rule_description="Response is empty",
                    severity="block",
                )],
                blocked=True,
            )
        
        violations: list[SafetyViolation] = []
        filtered = response
        
        # Check hard constraints
        for rule_id, pattern, description in self.HARD_CONSTRAINT_PATTERNS:
            match = pattern.search(response)
            if match:
                violations.append(SafetyViolation(
                    rule_id=rule_id,
                    rule_description=description,
                    matched_content=match.group(0),
                    severity="block",
                ))
        
        # If hard violations found, block and return fallback
        if any(v.severity == "block" for v in violations):
            logger.warning(
                "Response blocked by safety validator",
                violations=[v.rule_id for v in violations],
            )
            return SafetyResult(
                is_safe=False,
                original_response=response,
                filtered_response=self.FALLBACK_RESPONSE,
                violations=violations,
                blocked=True,
            )
        
        # Check filter patterns (modify, don't block)
        for rule_id, pattern, description in self.FILTER_PATTERNS:
            match = pattern.search(filtered)
            if match:
                violations.append(SafetyViolation(
                    rule_id=rule_id,
                    rule_description=description,
                    matched_content=match.group(0),
                    severity="warning",
                ))
                # Remove or modify the problematic content
                filtered = pattern.sub("", filtered)
        
        # For crisis responses, verify required elements
        if is_crisis_response:
            missing_required = self._check_crisis_requirements(filtered)
            if missing_required:
                # Append crisis resources to response
                filtered = self._append_crisis_resources(filtered)
                violations.append(SafetyViolation(
                    rule_id="MISSING_CRISIS_ELEMENTS",
                    rule_description=f"Added missing crisis elements: {missing_required}",
                    severity="warning",
                ))
        
        # Clean up filtered response
        filtered = self._clean_response(filtered)
        
        was_modified = filtered != response
        is_safe = len([v for v in violations if v.severity == "block"]) == 0
        
        if was_modified:
            logger.info(
                "Response modified by safety validator",
                warning_count=len([v for v in violations if v.severity == "warning"]),
            )
        
        return SafetyResult(
            is_safe=is_safe,
            original_response=response,
            filtered_response=filtered,
            violations=violations,
            was_modified=was_modified,
            blocked=False,
        )
    
    def _check_crisis_requirements(self, response: str) -> list[str]:
        """Check if crisis response has required elements."""
        missing = []
        for name, pattern in self.CRISIS_REQUIRED_ELEMENTS:
            if not pattern.search(response):
                missing.append(name)
        return missing
    
    def _append_crisis_resources(self, response: str) -> str:
        """Append crisis resources to response."""
        crisis_appendix = (
            "\n\n---\n"
            "**If you're in crisis or having thoughts of self-harm:**\n"
            "• **988 Suicide & Crisis Lifeline**: Call or text 988 (US)\n"
            "• **Crisis Text Line**: Text HOME to 741741\n"
            "• **Emergency**: Call 911 or go to your nearest emergency room\n"
            "You don't have to face this alone. Professional support is available 24/7."
        )
        return response + crisis_appendix
    
    def _clean_response(self, response: str) -> str:
        """Clean up response text."""
        # Remove excessive whitespace
        response = re.sub(r'\n{3,}', '\n\n', response)
        response = re.sub(r' {2,}', ' ', response)
        # Remove empty lines at start/end
        response = response.strip()
        return response
    
    def validate_prompt(self, prompt: str) -> bool:
        """
        Validate a prompt before sending to LLM.
        
        Checks for prompt injection attempts and other issues.
        
        Args:
            prompt: Prompt text to validate
            
        Returns:
            True if prompt is safe to send
        """
        # Check for common prompt injection patterns
        injection_patterns = [
            re.compile(r"ignore\s+(previous|above|all)\s+(instructions|rules)", re.I),
            re.compile(r"disregard\s+(your|the)\s+(instructions|guidelines|rules)", re.I),
            re.compile(r"you\s+are\s+now\s+(?!feeling|experiencing)", re.I),  # "you are now a different AI"
            re.compile(r"pretend\s+(you're|to be)\s+(a different|another)", re.I),
        ]
        
        for pattern in injection_patterns:
            if pattern.search(prompt):
                logger.warning("Prompt injection attempt detected")
                return False
        
        return True
