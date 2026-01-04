"""
Unit Tests for Text Analyzer

Tests rule-based panic detection patterns and risk scoring.
"""

import pytest

from hope.services.detection.text_analyzer import TextAnalyzer, TextAnalysisResult


class TestTextAnalyzer:
    """Test suite for TextAnalyzer."""
    
    @pytest.fixture
    def analyzer(self) -> TextAnalyzer:
        """Create text analyzer instance."""
        return TextAnalyzer()
    
    def test_empty_input(self, analyzer: TextAnalyzer) -> None:
        """Test handling of empty input."""
        result = analyzer.analyze("")
        assert result.risk_score == 0.0
        assert not result.requires_immediate_attention
    
    def test_normal_text(self, analyzer: TextAnalyzer) -> None:
        """Test normal non-panic text."""
        result = analyzer.analyze("I had a great day today. The weather was nice.")
        assert result.risk_score < 0.2
        assert not result.requires_immediate_attention
    
    def test_panic_keywords_detected(self, analyzer: TextAnalyzer) -> None:
        """Test detection of panic-related keywords."""
        result = analyzer.analyze("I'm having a panic attack and I'm so anxious")
        assert len(result.panic_keywords_found) > 0
        assert "panic" in result.panic_keywords_found
        assert result.risk_score > 0.3
    
    def test_crisis_indicators_trigger_immediate_attention(self, analyzer: TextAnalyzer) -> None:
        """Test that crisis indicators trigger immediate attention flag."""
        result = analyzer.analyze("I want to kill myself")
        assert len(result.crisis_indicators) > 0
        assert result.requires_immediate_attention
        assert result.risk_score >= 0.5
    
    def test_physiological_symptoms_detected(self, analyzer: TextAnalyzer) -> None:
        """Test detection of physiological symptom patterns."""
        result = analyzer.analyze("My heart is racing and I can't breathe")
        assert len(result.physiological_mentions) > 0
        assert result.risk_score > 0.2
    
    def test_cognitive_patterns_detected(self, analyzer: TextAnalyzer) -> None:
        """Test detection of cognitive distortion patterns."""
        result = analyzer.analyze("I feel like I'm going to die from this")
        assert len(result.cognitive_patterns) > 0
    
    def test_intensity_markers_increase_score(self, analyzer: TextAnalyzer) -> None:
        """Test that intensity markers increase risk score."""
        mild_result = analyzer.analyze("I feel anxious")
        intense_result = analyzer.analyze("I feel extremely anxious and it's unbearable")
        
        assert intense_result.risk_score > mild_result.risk_score
    
    def test_multiple_indicators_compound(self, analyzer: TextAnalyzer) -> None:
        """Test that multiple indicators compound the risk score."""
        single = analyzer.analyze("I'm panicking")
        multiple = analyzer.analyze(
            "I'm panicking, my heart is racing, I can't breathe, "
            "I feel like I'm going to die"
        )
        
        assert multiple.risk_score > single.risk_score
    
    def test_normalization(self, analyzer: TextAnalyzer) -> None:
        """Test text normalization."""
        result = analyzer.analyze("   I   have   anxiety   ")
        assert result.normalized_text == "I have anxiety"
        assert result.word_count == 3


class TestTextAnalysisResult:
    """Test TextAnalysisResult dataclass."""
    
    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        result = TextAnalysisResult(
            raw_text="test",
            risk_score=0.5,
            requires_immediate_attention=False,
            panic_keywords_found=["panic"],
        )
        
        data = result.to_dict()
        
        assert "risk_score" in data
        assert data["risk_score"] == 0.5
        assert data["panic_keywords_count"] == 1
