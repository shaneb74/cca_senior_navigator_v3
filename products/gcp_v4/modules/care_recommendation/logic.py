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
from typing import Any

from .flags import build_flags

# Import flag manager for persisting flags
try:
    from core import flag_manager

    FLAG_MANAGER_AVAILABLE = True
except ImportError:
    FLAG_MANAGER_AVAILABLE = False


# Tier thresholds based on total score
# CRITICAL: These are the ONLY 5 allowed tier values
TIER_THRESHOLDS = {
    "no_care_needed": (0, 8),  # 0-8 points: no formal care needed
    "in_home": (9, 16),  # 9-16 points: needs regular in-home support
    "assisted_living": (17, 24),  # 17-24 points: needs assisted living environment
    "memory_care": (25, 39),  # 25-39 points: needs memory care
    "memory_care_high_acuity": (40, 100),  # 40+ points: needs intensive memory care
}

# Valid tier values - used for validation
VALID_TIERS = set(TIER_THRESHOLDS.keys())


def _derive_move_preference(answers: dict[str, Any]) -> int | None:
    """Extract and derive move_preference value from answers.
    
    Args:
        answers: User responses
        
    Returns:
        Integer 1-4 representing move willingness, or None if not answered
    """
    move_pref = answers.get("move_preference")
    if move_pref is not None:
        try:
            return int(move_pref)
        except (ValueError, TypeError):
            pass
    return None


def _persist_recommendation_category(tier: str) -> None:
    """Persist recommendation category to session state for conditional rendering.
    
    Stores tier in both module state and top-level keys to enable show_if conditions
    like: {"equals": ["$state.recommendation.category", "assisted_living"]}
    
    Args:
        tier: Recommendation tier/category
    """
    try:
        import streamlit as st
        # Store in both module state and a dedicated recommendation key
        state_key = "gcp_v4_state"
        if state_key in st.session_state:
            module_state = st.session_state[state_key]
            if not isinstance(module_state, dict):
                module_state = {}
            # Store recommendation in nested structure for show_if access
            if "recommendation" not in module_state:
                module_state["recommendation"] = {}
            module_state["recommendation"]["category"] = tier
            st.session_state[state_key] = module_state
        
        # Also store in top-level for easier access
        st.session_state["gcp_recommendation_category"] = tier
    except Exception:
        pass  # Don't fail if streamlit not available (e.g., in tests)


def compute_recommendation_category(answers: dict[str, Any], persist_to_state: bool = True) -> str:
    """Compute and return just the recommendation category (tier) from current answers.
    
    This is used for mid-flow computation (e.g., after Daily Living section completes)
    to enable conditional rendering of subsequent sections based on recommendation.
    
    Args:
        answers: Current user responses (may be partial)
        persist_to_state: If True, stores recommendation in session state for conditional rendering
        
    Returns:
        Tier string (no_care_needed | in_home | assisted_living | memory_care | memory_care_high_acuity)
    """
    module_data = _load_module_json()
    total_score, _ = _calculate_score(answers, module_data)
    tier = _determine_tier(total_score)
    
    # Persist to session state for conditional show_if logic
    if persist_to_state:
        _persist_recommendation_category(tier)
    
    return tier


def derive_outcome(
    answers: dict[str, Any], context: dict[str, Any] = None, config: dict[str, Any] = None
) -> dict[str, Any]:
    """Compute care recommendation from answers and module.json scoring.

    This function:
    1. Loads module.json to get scoring rules
    2. Calculates total score from user answers
    3. Determines tier based on score thresholds
    4. Builds rationale from high-scoring areas
    5. Reads flags already set by module engine

    Args:
        answers: User responses from module engine (already includes flags)
        context: Context dict from module engine (product, version, person_name, etc.)
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
    
    # Persist recommendation category to session state for conditional rendering
    # This enables show_if conditions to access $state.recommendation.category
    _persist_recommendation_category(tier)

    # Build tier rankings (all tiers with calculated scores)
    tier_rankings = _build_tier_rankings(total_score, tier)

    # Calculate confidence based on completeness and score clarity
    confidence = _calculate_confidence(answers, scoring_details, total_score)

    # Build rationale from high-scoring areas
    rationale = _build_rationale(scoring_details, tier, total_score)

    # Derive move preference values if present
    move_preference_value = _derive_move_preference(answers)
    
    # Extract flag IDs from answers (module engine already set these)
    # The flags are stored in the answers dict under a "flags" key if present
    flag_ids = _extract_flags_from_state(answers)
    if not flag_ids:
        flag_ids = _extract_flags_from_answers(answers, module_data)
    
    # Add derived flag for move flexibility
    if move_preference_value is not None and move_preference_value >= 3:
        flag_ids.append("is_move_flexible")
    
    flags = build_flags(flag_ids)

    # Persist flags via Flag Manager (CHECKPOINT 2 integration)
    if FLAG_MANAGER_AVAILABLE:
        _persist_flags_via_manager(flag_ids, answers)

    # Determine suggested next product
    suggested_next = _determine_next_product(tier, confidence)
    
    # Build derived data (for summary display)
    derived = {}
    if move_preference_value is not None:
        derived["move_preference"] = move_preference_value
        derived["is_move_flexible"] = move_preference_value >= 3

    return {
        "tier": tier,
        "tier_score": round(total_score, 1),
        "tier_rankings": tier_rankings,
        "confidence": round(confidence, 2),
        "flags": flags,
        "rationale": rationale,
        "suggested_next_product": suggested_next,
        "derived": derived,
    }


def _load_module_json() -> dict[str, Any]:
    """Load module.json from disk.

    Returns:
        Module configuration dict
    """
    path = Path(__file__).with_name("module.json")
    with path.open() as fh:
        return json.load(fh)


def _calculate_score(
    answers: dict[str, Any], module_data: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
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
        "required_answered": 0,
        "required_total": 0,
        "optional_answered": 0,
    }

    # Iterate through sections in module.json
    for section in module_data.get("sections", []):
        section_type = section.get("type", "questions")
        if section_type not in ["questions", None]:
            continue

        section_id = section["id"]
        section_score = 0.0
        section_details = []

        # Iterate through questions in section
        for question in section.get("questions", []):
            question_id = question["id"]
            required = bool(question.get("required", False))

            user_answer = answers.get(question_id)
            answered = _has_answer(user_answer)

            if required:
                scoring_details["required_total"] += 1
                if answered:
                    scoring_details["required_answered"] += 1
            elif answered:
                scoring_details["optional_answered"] += 1

            if not answered:
                scoring_details["by_question"][question_id] = 0.0
                continue

            # Handle multi-select questions (list of values)
            if isinstance(user_answer, list):
                question_score = 0.0
                for option in question.get("options", []):
                    if option.get("value") in user_answer:
                        option_score = option.get("score", 0)
                        question_score += option_score
                        section_details.append(
                            {
                                "question": question.get("label", question_id),
                                "answer": option.get("label"),
                                "score": option_score,
                            }
                        )
            else:
                # Single-select question
                question_score = 0.0
                for option in question.get("options", []):
                    if option.get("value") == user_answer:
                        question_score = option.get("score", 0)
                        section_details.append(
                            {
                                "question": question.get("label", question_id),
                                "answer": option.get("label"),
                                "score": question_score,
                            }
                        )
                        break

            scoring_details["by_question"][question_id] = question_score
            section_score += question_score

        scoring_details["by_section"][section_id] = {
            "score": section_score,
            "details": section_details,
        }
        total_score += section_score

    scoring_details["answer_count"] = scoring_details["required_answered"]
    scoring_details["total_questions"] = scoring_details["required_total"]

    return total_score, scoring_details


def _has_answer(value: Any) -> bool:
    """Determine if a field has a meaningful answer."""
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, (list, tuple, set)):
        return any(str(v).strip() != "" for v in value)
    return True


def _determine_tier(total_score: float) -> str:
    """Determine care tier from total score.

    Args:
        total_score: Total points from all questions

    Returns:
        Tier name (no_care_needed | in_home | assisted_living | memory_care | memory_care_high_acuity)

    Raises:
        ValueError: If determined tier is not in VALID_TIERS
    """
    tier = None

    for tier_name, (min_score, max_score) in TIER_THRESHOLDS.items():
        if min_score <= total_score <= max_score:
            tier = tier_name
            break

    # Default to highest tier if score exceeds all thresholds
    if tier is None:
        tier = "memory_care_high_acuity"

    # CRITICAL VALIDATION: Ensure only allowed tiers can be returned
    if tier not in VALID_TIERS:
        raise ValueError(f"Invalid tier '{tier}' - must be one of {VALID_TIERS}")

    return tier


def _build_tier_rankings(total_score: float, winning_tier: str) -> list[tuple[str, float]]:
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


def _calculate_confidence(
    answers: dict[str, Any], scoring_details: dict[str, Any], total_score: float
) -> float:
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
    required_answered = scoring_details.get("required_answered", 0)
    required_total = scoring_details.get("required_total", 0)
    completeness = required_answered / required_total if required_total > 0 else 1.0

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


def _build_rationale(scoring_details: dict[str, Any], tier: str, total_score: float) -> list[str]:
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
    # CRITICAL: These are the ONLY 5 allowed tier display names
    tier_labels = {
        "no_care_needed": "No Care Needed",
        "in_home": "In-Home Care",
        "assisted_living": "Assisted Living",
        "memory_care": "Memory Care",
        "memory_care_high_acuity": "Memory Care (High Acuity)",
    }
    rationale.append(
        f"Based on {int(total_score)} points, we recommend: {tier_labels.get(tier, tier)}"
    )

    # Add top scoring sections
    sorted_sections = sorted(
        scoring_details["by_section"].items(), key=lambda x: x[1]["score"], reverse=True
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

    # Add special message for "No Care Needed" tier
    if tier == "no_care_needed":
        rationale.append(
            "✓ No formal care is needed at this time. If circumstances change, return to update your assessment."
        )

    return rationale[:6]  # Keep top 6 items


def _persist_flags_via_manager(flag_ids: list[str], answers: dict[str, Any]) -> None:
    """
    Persist flags using Flag Manager service (CHECKPOINT 2-5 integration).

    Special handling:
    - Chronic conditions: Use update_chronic_conditions() for auto-flag activation
    - All other flags: Use activate() for direct persistence

    Args:
        flag_ids: List of flag IDs to persist
        answers: User answers (used to extract chronic condition codes)
    """
    if not FLAG_MANAGER_AVAILABLE:
        return

    # Handle chronic conditions separately (CHECKPOINT 5)
    chronic_codes = answers.get("chronic_conditions", [])
    if chronic_codes and isinstance(chronic_codes, list):
        try:
            # This will auto-activate chronic_present/chronic_conditions flags
            flag_manager.update_chronic_conditions(
                chronic_codes, source="gcp", context="gcp.chronic_conditions"
            )
        except Exception as e:
            # Don't fail GCP if flag manager has issues
            print(f"⚠️  Warning: Could not persist chronic conditions: {e}")

    # Activate all other flags
    for flag_id in flag_ids:
        # Skip chronic flags (handled above by update_chronic_conditions)
        if flag_id in ["chronic_present", "chronic_conditions"]:
            continue

        try:
            flag_manager.activate(flag_id, source="gcp", context="gcp.care_recommendation")
        except flag_manager.InvalidFlagError as e:
            # Log but don't fail - allows GCP to work even with invalid flags
            print(f"⚠️  Warning: Invalid flag '{flag_id}': {e}")
        except Exception as e:
            print(f"⚠️  Warning: Could not activate flag '{flag_id}': {e}")


def _extract_flags_from_state(answers: dict[str, Any]) -> list[str]:
    """Extract flag IDs from the module state flags dictionary."""
    flag_ids: list[str] = []
    flags_map = answers.get("flags")
    if isinstance(flags_map, dict):
        for flag_key, value in flags_map.items():
            if flag_key.endswith("_message"):
                continue
            if bool(value):
                flag_ids.append(str(flag_key))

    raw_flags = answers.get("_flags")
    if isinstance(raw_flags, (list, tuple, set)):
        flag_ids.extend(str(flag) for flag in raw_flags if flag)

    # Deduplicate while preserving order
    seen: set[str] = set()
    ordered_flags: list[str] = []
    for flag in flag_ids:
        if flag not in seen:
            seen.add(flag)
            ordered_flags.append(flag)
    return ordered_flags


def _extract_flags_from_answers(answers: dict[str, Any], module_data: dict[str, Any]) -> list[str]:
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
        section_type = section.get("type", "questions")
        if section_type not in ["questions", None]:
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
