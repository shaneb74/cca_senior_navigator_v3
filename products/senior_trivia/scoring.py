"""
Scoring logic for Senior Trivia modules.

Computes scores, badges, and outcomes based on correct answers.
"""

from typing import Dict, Any


def compute_trivia_outcome(module_state: Dict[str, Any], config: Any) -> Dict[str, Any]:
    """Compute trivia outcome based on answers.
    
    Args:
        module_state: Module state with answers
        config: Module configuration
    
    Returns:
        Outcome dict with scores, badge, and summary
    """
    # Extract answers
    answers = module_state.get("answers", {})
    
    # Get all questions from config steps
    all_questions = []
    for step in config.steps:
        if step.fields:
            all_questions.extend(step.fields)
    
    # Count correct answers
    correct_count = 0
    total_questions = len(all_questions)
    
    for field in all_questions:
        question_id = field.key
        user_answer = answers.get(question_id)
        
        if user_answer:
            # Check if answer is correct
            for option in field.options:
                if option.get("value") == user_answer and option.get("is_correct"):
                    correct_count += 1
                    break
    
    # Calculate score percentage
    score_percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
    
    # Calculate points (10 points per correct answer)
    points_earned = correct_count * 10
    
    # Determine badge based on score
    if score_percentage >= 90:
        badge_name = "Platinum ⭐⭐⭐⭐"
        badge_level = "platinum"
    elif score_percentage >= 70:
        badge_name = "Gold ⭐⭐⭐"
        badge_level = "gold"
    elif score_percentage >= 50:
        badge_name = "Silver ⭐⭐"
        badge_level = "silver"
    else:
        badge_name = "Bronze ⭐"
        badge_level = "bronze"
    
    # Build outcome
    return {
        "recommendation": f"You scored {score_percentage:.0f}%! {_get_encouragement(score_percentage)}",
        "confidence": score_percentage / 100,  # Normalize to 0-1 for module engine
        "summary": {
            "correct_count": correct_count,
            "total_questions": total_questions,
            "score_percentage": f"{score_percentage:.0f}",
            "points_earned": points_earned,
            "badge_name": badge_name,
            "badge_level": badge_level,
        },
        "domain_scores": {
            "accuracy": score_percentage,
        },
        "flags": {},
        "tags": [badge_level],
        "routing": {},
        "audit": {},
    }


def _get_encouragement(score: float) -> str:
    """Get encouraging message based on score.
    
    Args:
        score: Score percentage (0-100)
    
    Returns:
        Encouraging message
    """
    if score >= 90:
        return "Outstanding! You're a trivia master! 🎯"
    elif score >= 70:
        return "Great job! You really know your stuff! 🌟"
    elif score >= 50:
        return "Nice work! You're learning a lot! 💪"
    else:
        return "Thanks for playing! Every question teaches something new! 📚"


__all__ = ["compute_trivia_outcome"]
