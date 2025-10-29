"""
Tests for NAVI Core data models (Pydantic validation).
"""

import pytest
from apps.navi_core.models import ChunkMetadata, ValidationResult, NaviAnswer


def test_chunk_metadata_valid():
    """Test ChunkMetadata creation with valid data."""
    chunk = ChunkMetadata(
        id="chunk_001",
        source="gcp_knowledge.jsonl",
        text="Assisted living provides help with daily activities.",
        similarity=0.92
    )
    assert chunk.id == "chunk_001"
    assert chunk.similarity == 0.92


def test_chunk_metadata_similarity_bounds():
    """Test ChunkMetadata similarity score validation."""
    # Valid: within bounds
    chunk = ChunkMetadata(id="1", source="test", text="content", similarity=0.5)
    assert chunk.similarity == 0.5
    
    # Invalid: below minimum
    with pytest.raises(ValueError):
        ChunkMetadata(id="1", source="test", text="content", similarity=-0.1)
    
    # Invalid: above maximum
    with pytest.raises(ValueError):
        ChunkMetadata(id="1", source="test", text="content", similarity=1.5)


def test_validation_result_passed():
    """Test ValidationResult for passed validation."""
    result = ValidationResult(passed=True, confidence=0.95, reason=None)
    assert result.passed is True
    assert result.confidence == 0.95
    assert result.reason is None


def test_validation_result_failed():
    """Test ValidationResult for failed validation."""
    result = ValidationResult(
        passed=False,
        confidence=0.3,
        reason="Answer contains potentially harmful content"
    )
    assert result.passed is False
    assert result.reason is not None


def test_navi_answer_minimal():
    """Test NaviAnswer with minimal required fields."""
    answer = NaviAnswer(
        question="What is assisted living?",
        answer="Assisted living is...",
        confidence=0.85,
        validated=ValidationResult(passed=True, confidence=0.85)
    )
    assert answer.tier is None
    assert answer.sources == []


def test_navi_answer_complete():
    """Test NaviAnswer with all fields populated."""
    chunks = [
        ChunkMetadata(id="1", source="faq", text="AL info", similarity=0.9),
        ChunkMetadata(id="2", source="kb", text="More info", similarity=0.8)
    ]
    
    answer = NaviAnswer(
        question="What is assisted living?",
        answer="Assisted living provides residential care...",
        tier=1,
        confidence=1.0,
        validated=ValidationResult(passed=True, confidence=1.0),
        sources=chunks
    )
    
    assert answer.tier == 1
    assert len(answer.sources) == 2
    assert answer.sources[0].similarity == 0.9


def test_navi_answer_confidence_bounds():
    """Test NaviAnswer confidence validation."""
    # Valid
    answer = NaviAnswer(
        question="Test?",
        answer="Answer",
        confidence=0.5,
        validated=ValidationResult(passed=True, confidence=0.5)
    )
    assert answer.confidence == 0.5
    
    # Invalid: out of bounds
    with pytest.raises(ValueError):
        NaviAnswer(
            question="Test?",
            answer="Answer",
            confidence=2.0,
            validated=ValidationResult(passed=True, confidence=1.0)
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
