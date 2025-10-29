"""
Tests for NAVI Core RAG (Retrieval-Augmented Generation).
"""

import pytest
from pathlib import Path
from apps.navi_core.rag import MiniFAQRetriever, SemanticRetriever


def test_mini_faq_retriever_init():
    """Test MiniFAQRetriever initialization."""
    retriever = MiniFAQRetriever()
    assert retriever.faq is not None
    assert isinstance(retriever.faq, dict)


def test_mini_faq_exact_match():
    """Test exact question matching."""
    retriever = MiniFAQRetriever()
    answer = retriever.match("What is assisted living?")
    assert answer is not None
    assert "assisted living" in answer.lower()


def test_mini_faq_fuzzy_match():
    """Test fuzzy/substring matching."""
    retriever = MiniFAQRetriever()
    
    # Should match "What is assisted living?"
    answer = retriever.match("assisted living")
    assert answer is not None
    
    # Should match "What is memory care?"
    answer = retriever.match("tell me about memory care")
    assert answer is not None


def test_mini_faq_case_insensitive():
    """Test case-insensitive matching."""
    retriever = MiniFAQRetriever()
    
    answer1 = retriever.match("What is ASSISTED LIVING?")
    answer2 = retriever.match("what is assisted living?")
    
    assert answer1 == answer2


def test_mini_faq_no_match():
    """Test no match returns None."""
    retriever = MiniFAQRetriever()
    answer = retriever.match("What is the meaning of life?")
    assert answer is None


def test_mini_faq_empty_question():
    """Test empty question handling."""
    retriever = MiniFAQRetriever()
    assert retriever.match("") is None
    assert retriever.match("   ") is None


def test_mini_faq_reload():
    """Test FAQ reload functionality."""
    retriever = MiniFAQRetriever()
    initial_count = len(retriever.faq)
    retriever.reload()
    assert len(retriever.faq) == initial_count


def test_semantic_retriever_init():
    """Test SemanticRetriever initialization."""
    retriever = SemanticRetriever()
    assert retriever.embedding_model == "text-embedding-3-small"


def test_semantic_retriever_placeholder():
    """Test SemanticRetriever placeholder behavior."""
    retriever = SemanticRetriever()
    chunks = retriever.retrieve("What is assisted living?")
    assert chunks == []  # Placeholder returns empty list


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
