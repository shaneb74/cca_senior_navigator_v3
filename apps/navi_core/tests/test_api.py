"""
Tests for NAVI Core public API.
"""

import pytest
from apps.navi_core import get_answer
from apps.navi_core.models import NaviAnswer
from apps.navi_core import api


def test_get_answer_basic():
    """Test basic get_answer call."""
    result = get_answer("What is assisted living?")
    
    assert isinstance(result, NaviAnswer)
    assert result.question == "What is assisted living?"
    assert result.answer is not None
    assert result.confidence > 0


def test_get_answer_with_name():
    """Test get_answer with personalization."""
    result = get_answer(
        question="What is memory care?",
        name="Sarah"
    )
    
    assert isinstance(result, NaviAnswer)
    assert result.answer is not None


def test_get_answer_with_tags():
    """Test get_answer with context tags."""
    result = get_answer(
        question="What is assisted living?",
        tags=["gcp", "care_recommendation"]
    )
    
    assert isinstance(result, NaviAnswer)


def test_get_answer_with_source():
    """Test get_answer with source tracking."""
    result = get_answer(
        question="What is assisted living?",
        source="hub"
    )
    
    assert isinstance(result, NaviAnswer)


def test_get_answer_with_conversation():
    """Test get_answer with conversation tracking."""
    conv_id = "test_api_conv_001"
    
    result1 = get_answer(
        question="What is assisted living?",
        conversation_id=conv_id
    )
    
    result2 = get_answer(
        question="How much does it cost?",
        conversation_id=conv_id
    )
    
    assert isinstance(result1, NaviAnswer)
    assert isinstance(result2, NaviAnswer)


def test_get_answer_modes():
    """Test get_answer with different modes."""
    modes = ["assist", "adjust", "shadow"]
    
    for mode in modes:
        result = get_answer(
            question="What is assisted living?",
            mode=mode
        )
        assert isinstance(result, NaviAnswer)


def test_reload_config():
    """Test config reload functionality."""
    # Should not raise exception
    api.reload_config()


def test_clear_conversation():
    """Test conversation clearing through API."""
    conv_id = "test_api_conv_002"
    
    # Create conversation
    get_answer(
        question="What is assisted living?",
        conversation_id=conv_id
    )
    
    # Clear it
    api.clear_conversation(conv_id)


def test_api_consistency():
    """Test that multiple calls return consistent base content (with or without tone)."""
    question = "What is assisted living?"
    
    result1 = get_answer(question, enable_tone=False)
    result2 = get_answer(question, enable_tone=False)
    
    # Without tone personalization, Tier-1 answers should be identical
    if result1.tier == 1 and result2.tier == 1:
        assert result1.answer == result2.answer


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
