"""
Tests for NAVI Core orchestrator (multi-tier routing).
"""

import pytest
from apps.navi_core.orchestrator import NaviOrchestrator
from apps.navi_core.models import NaviAnswer


def test_orchestrator_init():
    """Test NaviOrchestrator initialization."""
    orch = NaviOrchestrator()
    assert orch.faq is not None
    assert orch.semantic is not None
    assert orch.validator is not None
    assert orch.prompt_manager is not None


def test_tier1_faq_answer():
    """Test Tier-1 FAQ routing for common questions."""
    orch = NaviOrchestrator()
    result = orch.answer("What is assisted living?")
    
    assert isinstance(result, NaviAnswer)
    assert result.tier == 1
    assert result.confidence == 1.0
    assert result.validated.passed is True
    assert "assisted living" in result.answer.lower()


def test_tier1_multiple_questions():
    """Test multiple Tier-1 FAQ questions."""
    orch = NaviOrchestrator()
    
    questions = [
        "What is memory care?",
        "How much does assisted living cost?",
        "What is in-home care?"
    ]
    
    for question in questions:
        result = orch.answer(question)
        assert result.tier == 1
        assert result.confidence == 1.0


def test_tier3_llm_fallback():
    """Test Tier-3 LLM fallback for complex questions (becomes Tier-2 with tone)."""
    orch = NaviOrchestrator()
    result = orch.answer("What are the emotional challenges of transitioning to senior care?")
    
    assert isinstance(result, NaviAnswer)
    # With tone personalization enabled, Tier 3 becomes Tier 2
    assert result.tier in [2, 3]  # Allow both for flexibility
    assert result.answer is not None
    assert len(result.answer) > 0


def test_answer_with_name():
    """Test personalized answer with user name."""
    orch = NaviOrchestrator()
    result = orch.answer(
        question="What is assisted living?",
        name="Mary"
    )
    
    assert isinstance(result, NaviAnswer)
    assert result.answer is not None


def test_answer_with_conversation_id():
    """Test answer with conversation tracking."""
    orch = NaviOrchestrator()
    
    # First question
    result1 = orch.answer(
        question="What is assisted living?",
        conversation_id="test_conv_001"
    )
    
    # Follow-up question
    result2 = orch.answer(
        question="How much does it cost?",
        conversation_id="test_conv_001"
    )
    
    assert result1.answer is not None
    assert result2.answer is not None
    assert "test_conv_001" in orch.conversations


def test_answer_with_tags():
    """Test answer with context tags."""
    orch = NaviOrchestrator()
    result = orch.answer(
        question="What is assisted living?",
        tags=["gcp", "care_recommendation"]
    )
    
    assert isinstance(result, NaviAnswer)


def test_answer_validation():
    """Test that all answers pass through validation."""
    orch = NaviOrchestrator()
    result = orch.answer("What is assisted living?")
    
    assert result.validated is not None
    assert hasattr(result.validated, 'passed')
    assert hasattr(result.validated, 'confidence')


def test_clear_conversation():
    """Test conversation clearing."""
    orch = NaviOrchestrator()
    
    # Create conversation
    orch.answer(
        question="What is assisted living?",
        conversation_id="test_conv_002"
    )
    
    assert "test_conv_002" in orch.conversations
    
    # Clear it
    orch.clear_conversation("test_conv_002")
    
    # Should still exist but be empty
    assert "test_conv_002" in orch.conversations
    assert len(orch.conversations["test_conv_002"].turns) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
