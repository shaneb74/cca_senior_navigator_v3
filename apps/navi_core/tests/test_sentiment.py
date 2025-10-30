"""
Tests for NAVI Core Sentiment Analyzer
"""

import pytest
from apps.navi_core.sentiment import SentimentAnalyzer


def test_sentiment_analyzer_init():
    """Test sentiment analyzer initialization."""
    analyzer = SentimentAnalyzer()
    assert analyzer is not None


def test_analyze_distressed_keywords():
    """Test detection of distressed sentiment via keywords."""
    analyzer = SentimentAnalyzer()
    
    # Test various distress keywords
    assert analyzer.analyze("I'm worried about my mom") == "distressed"
    assert analyzer.analyze("This is so overwhelming") == "distressed"
    assert analyzer.analyze("I feel anxious about this decision") == "distressed"
    assert analyzer.analyze("I'm scared to make the wrong choice") == "distressed"
    assert analyzer.analyze("This is really hard for me") == "distressed"


def test_analyze_positive_keywords():
    """Test detection of positive sentiment via keywords."""
    analyzer = SentimentAnalyzer()
    
    # Test various positive keywords
    assert analyzer.analyze("I'm ready to move forward") == "positive"
    assert analyzer.analyze("Feeling confident about this") == "positive"
    assert analyzer.analyze("This is a great option") == "positive"
    assert analyzer.analyze("I'm hopeful this will work") == "positive"


def test_analyze_neutral():
    """Test detection of neutral sentiment."""
    analyzer = SentimentAnalyzer()
    
    # Informational/neutral questions
    assert analyzer.analyze("What is assisted living?") == "neutral"
    assert analyzer.analyze("How much does memory care cost?") == "neutral"
    assert analyzer.analyze("Tell me about in-home care options") == "neutral"


def test_analyze_empty_text():
    """Test handling of empty text."""
    analyzer = SentimentAnalyzer()
    
    assert analyzer.analyze("") == "neutral"
    assert analyzer.analyze("   ") == "neutral"
    assert analyzer.analyze(None) == "neutral"


def test_analyze_mixed_sentiment():
    """Test text with mixed sentiment leans toward stronger signal."""
    analyzer = SentimentAnalyzer()
    
    # Distress keyword should dominate
    text = "I'm worried but also ready to explore options"
    assert analyzer.analyze(text) == "distressed"


def test_get_emotion_score():
    """Test numerical emotion scoring."""
    analyzer = SentimentAnalyzer()
    
    # Should return values between 0 and 1
    score = analyzer.get_emotion_score("This is wonderful news!")
    assert 0.0 <= score <= 1.0
    assert score > 0.5  # Positive should be > 0.5
    
    score = analyzer.get_emotion_score("This is terrible and awful")
    assert 0.0 <= score <= 1.0
    assert score < 0.5  # Negative should be < 0.5
    
    score = analyzer.get_emotion_score("The weather is today")
    assert 0.0 <= score <= 1.0  # Just check it's in valid range


def test_analyze_case_insensitive():
    """Test that analysis is case-insensitive."""
    analyzer = SentimentAnalyzer()
    
    assert analyzer.analyze("I'M WORRIED") == "distressed"
    assert analyzer.analyze("i'm worried") == "distressed"
    assert analyzer.analyze("I'm Worried") == "distressed"


def test_analyze_compound_sentences():
    """Test analysis of longer, compound sentences."""
    analyzer = SentimentAnalyzer()
    
    # Long distressed message
    text = "I don't know if I'm ready to move my mom into assisted living. This feels overwhelming."
    assert analyzer.analyze(text) == "distressed"
    
    # Long informational message
    text = "Can you explain the difference between assisted living and memory care facilities?"
    assert analyzer.analyze(text) == "neutral"


def test_sentiment_consistency():
    """Test that similar messages get similar sentiment."""
    analyzer = SentimentAnalyzer()
    
    # Similar distressed messages
    result1 = analyzer.analyze("I'm so anxious about this")
    result2 = analyzer.analyze("Feeling very anxious right now")
    assert result1 == result2 == "distressed"
