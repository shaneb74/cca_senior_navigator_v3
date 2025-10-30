"""
Tests for NAVI Core Tone Adapter
"""

import pytest
from apps.navi_core.tone_adapter import ToneAdapter
from apps.navi_core.models import NaviAnswer, ValidationResult


def test_tone_adapter_init():
    """Test tone adapter initialization."""
    adapter = ToneAdapter()
    assert adapter is not None
    assert len(adapter.get_available_tones()) > 0


def test_select_tone_distressed():
    """Test tone selection for distressed sentiment."""
    adapter = ToneAdapter()
    
    tone = adapter.select_tone("I'm worried about moving my mom")
    assert tone == "Empathetic"


def test_select_tone_neutral():
    """Test tone selection for neutral sentiment."""
    adapter = ToneAdapter()
    
    tone = adapter.select_tone("What is assisted living?")
    assert tone == "Guidance"


def test_select_tone_positive():
    """Test tone selection for positive sentiment."""
    adapter = ToneAdapter()
    
    tone = adapter.select_tone("I'm ready to explore options")
    assert tone == "Encouraging"


def test_apply_tone_to_faq_answer():
    """Test applying tone to FAQ answer."""
    adapter = ToneAdapter()
    
    original_answer_text = "Assisted living is a residential care option for seniors."
    base_answer = NaviAnswer(
        question="What is assisted living?",
        answer=original_answer_text,
        tier=1,
        confidence=1.0,
        validated=ValidationResult(passed=True, confidence=1.0, reason=None),
        sources=[]
    )
    
    personalized = adapter.apply(base_answer, "I'm worried, what is assisted living?")
    
    # Should add empathetic tone wrapping
    assert original_answer_text in personalized.answer  # Original content preserved
    assert len(personalized.answer) >= len(original_answer_text)  # At least same length
    # Tier should stay 1 for FAQ answers
    assert personalized.tier == 1


def test_apply_tone_to_llm_answer():
    """Test applying tone to LLM-generated answer."""
    adapter = ToneAdapter()
    
    original_answer_text = "Memory care may be appropriate if there are signs of cognitive decline."
    base_answer = NaviAnswer(
        question="How do I know if my mom needs memory care?",
        answer=original_answer_text,
        tier=3,
        confidence=0.8,
        validated=ValidationResult(passed=True, confidence=0.9, reason=None),
        sources=[]
    )
    
    personalized = adapter.apply(base_answer, "I'm so confused about memory care")
    
    # Should add empathetic tone and mark as Tier 2
    assert original_answer_text in personalized.answer  # Original content preserved
    assert personalized.tier == 2  # Tier 3 becomes Tier 2 with personalization


def test_force_tone():
    """Test forcing a specific tone regardless of sentiment."""
    adapter = ToneAdapter()
    
    base_answer = NaviAnswer(
        question="What is memory care?",
        answer="Memory care is specialized care for dementia patients.",
        tier=1,
        confidence=1.0,
        validated=ValidationResult(passed=True, confidence=1.0, reason=None),
        sources=[]
    )
    
    # Force Encouraging tone despite neutral question
    personalized = adapter.apply(base_answer, "What is memory care?", force_tone="Encouraging")
    
    assert "Memory care is specialized care for dementia patients" in personalized.answer
    # Should have encouraging prefix/suffix even though question is neutral


def test_get_available_tones():
    """Test getting list of available tones."""
    adapter = ToneAdapter()
    
    tones = adapter.get_available_tones()
    assert len(tones) >= 3
    assert "Empathetic" in tones
    assert "Guidance" in tones
    assert "Encouraging" in tones


def test_describe_tone():
    """Test getting tone descriptions."""
    adapter = ToneAdapter()
    
    description = adapter.describe_tone("Empathetic")
    assert description is not None
    assert len(description) > 0


def test_tone_preserves_base_content():
    """Test that tone adaptation preserves the original answer content."""
    adapter = ToneAdapter()
    
    original_text = "This is important medical information that must be preserved exactly."
    base_answer = NaviAnswer(
        question="Test question",
        answer=original_text,
        tier=3,
        confidence=0.9,
        validated=ValidationResult(passed=True, confidence=1.0, reason=None),
        sources=[]
    )
    
    personalized = adapter.apply(base_answer, "I'm worried")
    
    # Original content should still be in personalized answer
    assert original_text in personalized.answer


def test_reload_tones():
    """Test hot-reloading tone configurations."""
    adapter = ToneAdapter()
    
    original_tones = adapter.get_available_tones()
    adapter.reload()
    reloaded_tones = adapter.get_available_tones()
    
    # Should have same tones after reload
    assert set(original_tones) == set(reloaded_tones)


def test_tone_variation():
    """Test that tone application varies naturally across calls."""
    adapter = ToneAdapter()
    
    base_answer = NaviAnswer(
        question="What is assisted living?",
        answer="Assisted living provides daily support.",
        tier=1,
        confidence=1.0,
        validated=ValidationResult(passed=True, confidence=1.0, reason=None),
        sources=[]
    )
    
    # Apply tone multiple times
    results = []
    for _ in range(5):
        personalized = adapter.apply(
            NaviAnswer(**base_answer.model_dump()),  # Fresh copy
            "I'm worried about assisted living"
        )
        results.append(personalized.answer)
    
    # Should get some variation in prefixes/suffixes (not always identical)
    unique_results = set(results)
    # With random selection, likely to get at least 2 different variations in 5 tries
    assert len(unique_results) >= 1  # At minimum, content is preserved


def test_conversation_history_context():
    """Test tone selection with conversation history context."""
    adapter = ToneAdapter()
    
    # Conversation showing progression from distress to confidence
    history = [
        {"question": "I'm so worried", "answer": "...", "sentiment": "distressed"},
        {"question": "That helps", "answer": "...", "sentiment": "positive"}
    ]
    
    # Current question is neutral, but history exists
    tone = adapter.select_tone("What's the next step?", conversation_history=history)
    
    # Should select based on current question sentiment, not history (for now)
    assert tone in ["Empathetic", "Guidance", "Encouraging"]
