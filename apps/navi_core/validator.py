"""
NAVI Core Answer Validator

Validates LLM-generated answers for safety, accuracy, empathy, and completeness.
"""

from typing import Optional
from apps.navi_core.models import ValidationResult


class AnswerValidator:
    """Validates NAVI answers for quality, safety, and appropriateness."""
    
    def __init__(self, strict_mode: bool = True):
        """Initialize validator."""
        self.strict_mode = strict_mode
        
    def validate(self, question: str, answer: str, sources: Optional[list] = None, confidence: float = 1.0) -> ValidationResult:
        """Validate an answer."""
        if not answer or len(answer.strip()) < 10:
            return ValidationResult(passed=False, confidence=0.0, reason="Answer too short or empty")
        
        # Safety check
        harmful_keywords = ["die", "kill", "suicide", "hurt"]
        if any(keyword in answer.lower() for keyword in harmful_keywords):
            return ValidationResult(passed=False, confidence=0.0, reason="Safety concern: potentially harmful content")
        
        return ValidationResult(passed=True, confidence=confidence, reason=None)
    
    def check_empathy(self, answer: str) -> float:
        """Score answer empathy (0-1)."""
        empathy_indicators = ["understand", "help", "support", "care", "here for you"]
        score = sum(1 for indicator in empathy_indicators if indicator in answer.lower())
        return min(score / len(empathy_indicators), 1.0)
    
    def check_completeness(self, question: str, answer: str) -> float:
        """Score answer completeness (0-1)."""
        if len(answer) > 100:
            return 0.9
        elif len(answer) > 50:
            return 0.7
        else:
            return 0.5
