"""
GCP v4 Care Recommendation Logic - Self-contained scoring engine.

This module respects module.json as the authoritative source of truth:
- Reads scores directly from option.score values in module.json
- Uses flags already set by module engine from option.flags
- Calculates tier based on total score thresholds
- Returns MCIP-compatible CareRecommendation dict
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from .flags import build_flags


# Tier thresholds based on total score
TIER_THRESHOLDS = {
    "independent": (0, 8),      # 0-8 points: can live independently or with minimal help
    "in_home": (9, 16),          # 9-16 points: needs regular in-home support
    "assisted_living": (17, 24), # 17-24 points: needs assisted living environment
    "memory_care": (25, 100),    # 25+ points: needs memory care or skilled nursing
}


def derive_outcome(answers: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Compute care recommendation from answers and module.json scoring.
    
    This function:
    1. Loads module.json to get scoring rules
    2. Calculates total score from user answers
    3. Determines tier based on score thresholds
    4. Builds rationale from high-scoring areas
    5. Reads flags already set by module engine
    
    Args:
        answers: User responses from module engine (already includes flags)
        config: Optional configuration (not currently used)
    
    Returns:
        Dict matching CareRecommendation dataclass schema:
        - tier: str (independent | in_home | assisted_living | memory_care)
        - tier_score: float
        - tier_rankings: List[Tuple[str, float]]
        - confidence: float
        - flags: List[Dict]
        - rationale: List[str]
        - suggested_next_product: str
    """
    
    # Load module.json to get scoring rules
    module_data = _load_module_json()
    
    # Calculate total score from answers
    total_score, scoring_details = _calculate_score(answers, module_data)
    
    # Determine tier from score
    tier = _determine_tier(total_score)
    
    # Build tier rankings (all tiers with calculated scores)
    tier_rankings = _build_tier_rankings(total_score, tier)
    
    # Calculate confidence based on completeness and score clarity
    confidence = _calculate_confidence(answers, scoring_details, total_score)
    
    # Build rationale from high-scoring areas
    rationale = _build_rationale(scoring_details, tier, total_score)
    
    # Extract flag IDs from answers (module engine already set these)
    # The flags are stored in the answers dict under a "flags" key if present
    flag_ids = answers.get("_flags", []) if "_flags" in answers else _extract_flags_from_answers(answers, module_data)
    flags = build_flags(flag_ids)
    
    # Determine suggested next product
    suggested_next = _determine_next_product(tier, confidence)
    
    return {
        "tier": tier,
        "tier_score": round(total_score, 1),
        "tier_rankings": tier_rankings,
        "confidence": round(confidence, 2),
        "flags": flags,
        "rationale": rationale,
        "suggested_next_product": suggested_next
    }


def _load_module_json() -> Dict[str, Any]:
    """Load module.json from disk.
    
    Returns:
        Module configuration dict
    """
    path = Path(__file__).with_name("module.json")
    with path.open() as fh:
        return json.load(fh)


def _calculate_score(answers: Dict[str, Any], module_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Calculate total score from user answers using module.json scoring.
    
    Args:
        answers: User responses
        module_data: Loaded module.json
    
    Returns:
        Tuple of (total_score, scoring_details)
        scoring_details contains breakdown by question/section
    """
    total_score = 0.0
    scoring_details = {
        "by_section": {},
        "by_question": {},
        "answer_count": 0,
        "total_questions": 0
    }
    
    # Iterate through sections in module.json
    for section in module_data.get("sections", []):
        if section.get("type") != "questions":
            continue
            
        section_id = section["id"]
        section_score = 0.0
        section_details = []
        
        # Iterate through questions in section
        for question in section.get("questions", []):
            question_id = question["id"]
            scoring_details["total_questions"] += 1
            
            # Get user's answer
            user_answer = answers.get(question_id)
            if user_answer is None:
                continue
                
            scoring_details["answer_count"] += 1
            
            # Handle multi-select questions (list of values)
            if isinstance(user_answer, list):
                question_score = 0.0
                for option in question.get("options", []):
                    if option.get("value") in user_answer:
                        option_score = option.get("score", 0)
                        question_score += option_score
                        section_details.append({
                            "question": question.get("label", question_id),
                            "answer": option.get("label"),
                            "score": option_score
                        })
            else:
                # Single-select question
                question_score = 0.0
                for option in question.get("options", []):
                    if option.get("value") == user_answer:
                        question_score = option.get("score", 0)
                        section_details.append({
                            "question": question.get("label", question_id),
                            "answer": option.get("label"),
                            "score": question_score
                        })
                        break
            
            scoring_details["by_question"][question_id] = question_score
            section_score += question_score
        
        scoring_details["by_section"][section_id] = {
            "score": section_score,
            "details": section_details
        }
        total_score += section_score
    
    return total_score, scoring_details


def _determine_tier(total_score: float) -> str:
    """Determine care tier from total score.
    
    Args:
        total_score: Total points from all questions
    
    Returns:
        Tier name (independent | in_home | assisted_living | memory_care)
    """
    for tier, (min_score, max_score) in TIER_THRESHOLDS.items():
        if min_score <= total_score <= max_score:
            return tier
    
    # Default to memory_care if score exceeds all thresholds
    return "memory_care"


def _build_tier_rankings(total_score: float, winning_tier: str) -> List[Tuple[str, float]]:
    """Build tier rankings showing all tiers with their distance from user's score.
    
    Args:
        total_score: User's total score
        winning_tier: The recommended tier
    
    Returns:
        List of (tier_name, score) tuples sorted by score descending
    """
    rankings = []
    
    for tier, (min_score, max_score) in TIER_THRESHOLDS.items():
        if tier == winning_tier:
            # Winning tier gets the actual score
            rankings.append((tier, total_score))
        else:
            # Other tiers get the midpoint of their range as a reference
            midpoint = (min_score + max_score) / 2
            rankings.append((tier, round(midpoint, 1)))
    
    # Sort by score descending
    rankings.sort(key=lambda x: x[1], reverse=True)
    
    return rankings


def _calculate_confidence(answers: Dict[str, Any], scoring_details: Dict[str, Any], total_score: float) -> float:
    """Calculate confidence in the recommendation.
    
    Based on:
    - Completeness (answered questions / total questions)
    - Score clarity (how far from tier boundaries)
    
    Args:
        answers: User responses
        scoring_details: Scoring breakdown
        total_score: Total calculated score
    
    Returns:
        Confidence score between 0 and 1
    """
    # Base confidence from completeness
    answered = scoring_details["answer_count"]
    total = scoring_details["total_questions"]
    completeness = answered / total if total > 0 else 0.0
    
    # Adjust for score clarity (distance from boundaries)
    tier = _determine_tier(total_score)
    min_score, max_score = TIER_THRESHOLDS[tier]
    
    # Distance from nearest boundary
    distance_from_min = total_score - min_score
    distance_from_max = max_score - total_score
    distance_from_boundary = min(distance_from_min, distance_from_max)
    
    # Normalize distance (3+ points from boundary = full confidence)
    boundary_confidence = min(distance_from_boundary / 3.0, 1.0)
    
    # Combined confidence (weighted average)
    confidence = (completeness * 0.6) + (boundary_confidence * 0.4)
    
    return max(0.5, confidence)  # Minimum 50% confidence


def _build_rationale(scoring_details: Dict[str, Any], tier: str, total_score: float) -> List[str]:
    """Build human-readable rationale for the recommendation.
    
    Args:
        scoring_details: Scoring breakdown by section/question
        tier: Recommended tier
        total_score: Total score
    
    Returns:
        List of rationale strings
    """
    rationale = []
    
    # Start with overall recommendation
    tier_labels = {
        "independent": "Independent Living or In-Home Support",
        "in_home": "In-Home Care",
        "assisted_living": "Assisted Living",
        "memory_care": "Memory Care or Skilled Nursing"
    }
    rationale.append(f"Based on {int(total_score)} points, we recommend: {tier_labels.get(tier, tier)}")
    
    # Add top scoring sections
    sorted_sections = sorted(
        scoring_details["by_section"].items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )
    
    for section_id, section_data in sorted_sections[:3]:  # Top 3 sections
        score = section_data["score"]
        if score > 0:
            section_label = section_id.replace("_", " ").title()
            rationale.append(f"{section_label}: {int(score)} points")
            
            # Add top detail from this section
            if section_data["details"]:
                top_detail = max(section_data["details"], key=lambda x: x["score"])
                if top_detail["score"] > 0:
                    rationale.append(f"  • {top_detail['answer']}")
    
    return rationale[:6]  # Keep top 6 items


def _extract_flags_from_answers(answers: Dict[str, Any], module_data: Dict[str, Any]) -> List[str]:
    """Extract flag IDs from answers by matching against module.json options.
    
    Note: The module engine should have already set these flags, but this
    provides a fallback in case flags weren't captured properly.
    
    Args:
        answers: User responses
        module_data: Loaded module.json
    
    Returns:
        List of flag IDs
    """
    flag_ids = set()
    
    # Iterate through sections and questions
    for section in module_data.get("sections", []):
        if section.get("type") != "questions":
            continue
            
        for question in section.get("questions", []):
            question_id = question["id"]
            user_answer = answers.get(question_id)
            
            if user_answer is None:
                continue
            
            # Handle multi-select (list)
            if isinstance(user_answer, list):
                for option in question.get("options", []):
                    if option.get("value") in user_answer:
                        flags = option.get("flags", [])
                        flag_ids.update(flags)
            else:
                # Single-select
                for option in question.get("options", []):
                    if option.get("value") == user_answer:
                        flags = option.get("flags", [])
                        flag_ids.update(flags)
                        break
    
    return list(flag_ids)



def _determine_next_product(tier: str, confidence: float) -> str:
    """Determine suggested next product based on tier and confidence.
    
    Args:
        tier: Recommended care tier
        confidence: Recommendation confidence
    
    Returns:
        Product key for suggested next step
    """
    if confidence < 0.7:
        return "gcp"  # Need more information
    else:
        return "cost_planner"  # Ready for cost estimation


# Backward compatibility alias
compute = derive_outcome
