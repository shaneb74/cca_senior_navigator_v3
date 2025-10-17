"""
Scoring logic for Senior Trivia modules.

Computes scores, badges, and outcomes based on correct answers.
"""

from typing import Dict, Any


def compute_trivia_outcome(answers: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Compute trivia outcome based on answers.
    
    Args:
        answers: User answers dict {question_id: value}
        context: Context dict with config and other metadata
    
    Returns:
        Outcome dict with scores, badge, and question breakdown
    """
    # Get config from context
    config = context.get("config")
    
    # Get all questions from config steps
    all_questions = []
    for step in config.steps:
        if step.fields:
            all_questions.extend(step.fields)
    
    # Build question breakdown with details
    question_breakdown = []
    correct_count = 0
    total_questions = len(all_questions)
    
    for field in all_questions:
        question_id = field.key
        user_answer = answers.get(question_id)
        
        # Find correct option and user's option
        correct_option = None
        user_option = None
        is_correct = False
        
        for option in field.options:
            if option.get("is_correct"):
                correct_option = option
            if option.get("value") == user_answer:
                user_option = option
                if option.get("is_correct"):
                    is_correct = True
                    correct_count += 1
        
        # Get feedback (prioritize user's choice, fall back to correct)
        feedback = ""
        if user_option and user_option.get("feedback"):
            feedback = user_option.get("feedback")
        elif correct_option and correct_option.get("feedback"):
            feedback = correct_option.get("feedback")
        
        question_breakdown.append({
            "question_id": question_id,
            "question_text": field.label,
            "user_answer": user_option.get("label") if user_option else "Not answered",
            "user_answer_value": user_answer,
            "correct_answer": correct_option.get("label") if correct_option else "Unknown",
            "correct_answer_value": correct_option.get("value") if correct_option else None,
            "is_correct": is_correct,
            "feedback": feedback
        })
    
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
    
    # Sort question breakdown: wrong answers first, then correct
    question_breakdown.sort(key=lambda q: (q["is_correct"], q["question_id"]))
    
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
        "question_breakdown": question_breakdown,  # NEW: detailed question analysis
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
