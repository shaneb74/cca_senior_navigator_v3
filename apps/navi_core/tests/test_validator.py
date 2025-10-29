"""
Tests for NAVI Core answer validator.
"""

import pytest
from apps.navi_core.validator import AnswerValidator
from apps.navi_core.models import ValidationResult


def test_validator_init():
    """Test AnswerValidator initialization."""
    validator = AnswerValidator(strict_mode=True)
    assert validator.strict_mode is True


def test_validate_good_answer():
    """Test validation of good answer."""
    validator = AnswerValidator()
    result = validator.validate(
        question="What is assisted living?",
        answer="Assisted living provides residential care with help for daily activities.",
        confidence=0.9
    )
    assert result.passed is True
    assert result.confidence > 0


def test_validate_empty_answer():
    """Test validation fails on empty answer."""
    validator = AnswerValidator()
    result = validator.validate(
        question="Test question?",
        answer="",
        confidence=1.0
    )
    assert result.passed is False
    assert "too short or empty" in result.reason.lower()


def test_validate_short_answer():
    """Test validation fails on too-short answer."""
    validator = AnswerValidator()
    result = validator.validate(
        question="Test?",
        answer="Yes",
        confidence=1.0
    )
    assert result.passed is False


def test_validate_harmful_content():
    """Test validation fails on harmful keywords."""
    validator = AnswerValidator()
    result = validator.validate(
        question="Test?",
        answer="You should consider options to end suffering and die peacefully.",
        confidence=1.0
    )
    assert result.passed is False
    assert "safety concern" in result.reason.lower()


def test_check_empathy():
    """Test empathy scoring."""
    validator = AnswerValidator()
    
    # High empathy
    score1 = validator.check_empathy(
        "I understand this is difficult. We're here to help support you through this."
    )
    assert score1 > 0.5
    
    # Low empathy
    score2 = validator.check_empathy(
        "The answer is 42."
    )
    assert score2 < 0.5


def test_check_completeness():
    """Test completeness scoring."""
    validator = AnswerValidator()
    
    # Complete answer
    score1 = validator.check_completeness(
        "What is assisted living?",
        "Assisted living is a residential care option for seniors who need help with daily activities like bathing, dressing, or medication management."
    )
    assert score1 > 0.7
    
    # Incomplete answer
    score2 = validator.check_completeness(
        "What is assisted living?",
        "It's care."
    )
    assert score2 < 0.7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
