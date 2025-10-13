"""
Hybrid scoring logic for GCP care recommendation module.

Based on gcp_v3_scoring.csv clinical model with:
- Domain-weighted scoring (ADL=3, Cognitive=3, Support=2, Mobility=2, Health=2, Isolation=1)
- Domain caps per CSV rules
- OVERRIDE rules for high-acuity cases
- MODIFIER rules for support/isolation adjustments
- Clear tier boundaries: 0=Independent, 1=In-Home, 2=Assisted, 3=Memory, 4=High-Acuity Memory
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from core.modules.schema import OutcomeContract


# === DOMAIN WEIGHTS (from CSV) ===
DOMAIN_WEIGHTS = {
    "adl_iadl": 3,          # Critical for daily function
    "cognitive": 3,         # Critical for safety
    "support": 2,           # Important but not critical
    "mobility": 2,          # Important for safety
    "medication": 2,        # Important for health
    "health": 2,            # Important for stability
    "mood": 1,              # Secondary factor
    "isolation": 1          # Modifier only
}

# === DOMAIN CAPS (from CSV) ===
DOMAIN_CAPS = {
    "cognitive": 3,         # Cap behaviors at 3 total
    "health": 3,            # Cap chronic conditions at 3 total
    "adl_iadl_badls": None, # No cap on BADLs
    "adl_iadl_iadls": None  # No cap on IADLs
}

# === TIER BOUNDARIES ===
# Adjusted for capped BADLs/IADLs scoring (max 3 pts each + domain weights)
# Max realistic score: ~50-60 points with all high needs + safety boosts
# Distribution: ~70% of seniors will be in 0-20 range, ~20% in 21-38, ~10% above
TIER_THRESHOLDS = {
    0: (0, 10),      # Independent / In-Home: 0-10 points (minimal/no support needed)
    1: (11, 24),     # In-Home Care: 11-24 points (manageable at home with support)
    2: (25, 37),     # Assisted Living: 25-37 points (needs facility-based support)
    3: (38, 999)     # Memory Care: 38+ points (complex care needs)
}

TIER_NAMES = {
    0: "Independent / In-Home",           # Maps to Cost Planner: "no_care"
    1: "In-Home Care",                    # Maps to Cost Planner: "in_home_care"
    2: "Assisted Living",                 # Maps to Cost Planner: "assisted_living"
    3: "Memory Care",                     # Maps to Cost Planner: "memory_care"
    4: "High-Acuity Memory Care"          # Maps to Cost Planner: "memory_care_high_acuity"
}


def _normalize_answer(key: str, value: Any) -> str:
    """Normalize answer values to match CSV expectations."""
    if value is None:
        return ""
    
    val_str = str(value).lower()
    
    # Memory changes normalization
    if key == "memory_changes":
        if "severe" in val_str or "dementia" in val_str or "alzheimer" in val_str:
            return "severe"
        elif "moderate" in val_str:
            return "moderate"
        elif "occasional" in val_str:
            return "occasional"
        elif "no concern" in val_str:
            return "none"
    
    # Mobility normalization
    if key == "mobility":
        if "bed" in val_str or "bedbound" in val_str:
            return "bedbound"
        elif "wheelchair" in val_str or "scooter" in val_str:
            return "wheelchair"
        elif "walker" in val_str or "cane" in val_str:
            return "walker"
        elif "independent" in val_str or "walks" in val_str:
            return "independent"
    
    # Falls normalization
    if key == "falls":
        if "multiple" in val_str:
            return "multiple"
        elif "one" in val_str:
            return "one"
        elif "no" in val_str or "none" in val_str:
            return "none"
    
    # Help overall normalization
    if key == "help_overall":
        if "independent" in val_str or ("none" in val_str and "fully" in val_str):
            return "independent"
        elif "full" in val_str or "extensive" in val_str:
            return "full_support"
        elif "daily" in val_str or "regular" in val_str:
            return "daily_help"
        elif "some" in val_str or "occasional" in val_str:
            return "some_help"
    
    # Medication complexity
    if key == "meds_complexity":
        # Check for moderate BEFORE complex (since "Moderate" contains "complex" substring)
        if "moderate" in val_str:
            return "moderate"
        elif "complex" in val_str:
            return "complex"
        elif "simple" in val_str:
            return "simple"
        elif "none" in val_str:
            return "none"
    
    # Support hours
    if key == "hours_per_day":
        if "24" in val_str:
            return "24h"
        elif "4" in val_str or "8" in val_str:
            return "4-8h"
        elif "1" in val_str and "3" in val_str:
            return "1-3h"
        elif "<1" in val_str or "less than 1" in val_str:
            return "<1h"
    
    # Primary support
    if key == "primary_support":
        if "none" in val_str:
            return "none"
        elif "family" in val_str or "friend" in val_str:
            return "family"
        elif "paid" in val_str or "caregiver" in val_str:
            return "paid"
        elif "agency" in val_str or "community" in val_str:
            return "agency"
    
    # Isolation
    if key == "isolation":
        if "very" in val_str:
            return "very"
        elif "somewhat" in val_str:
            return "somewhat"
        elif "easy" in val_str or "accessible" in val_str or "no" in val_str:
            return "accessible"
    
    # Mood
    if key == "mood":
        if "low" in val_str or "down" in val_str:
            return "low"
        elif "okay" in val_str or "ups" in val_str:
            return "okay"
        elif "mostly" in val_str or "good" in val_str:
            return "mostly_good"
        elif "great" in val_str or "positive" in val_str:
            return "great"
    
    return val_str


def _score_question(key: str, value: Any, domain: str, weight: int) -> tuple[int, Set[str]]:
    """
    Score a single question answer.
    
    Returns:
        (raw_score_before_weight, flags_set)
    
    Note: The domain weight is applied AFTER summing all question scores in that domain.
    """
    normalized = _normalize_answer(key, value)
    flags = set()
    raw_score = 0
    
    # === COGNITIVE FUNCTION ===
    if key == "memory_changes":
        if normalized == "severe":
            raw_score = 3
            flags.add("cog_severe")
        elif normalized == "moderate":
            raw_score = 2
            flags.add("cog_moderate")
        elif normalized == "occasional":
            raw_score = 1
    
    # === BEHAVIORS (each item adds 1, capped at 3 per CSV) ===
    elif key == "behaviors":
        if isinstance(value, list):
            raw_score = min(len(value), 3)  # Cap at 3
            if len(value) > 0:
                flags.add("behavior_risk")
    
    # === MOBILITY ===
    elif key == "mobility":
        if normalized == "bedbound":
            raw_score = 3
        elif normalized == "wheelchair":
            raw_score = 2
        elif normalized == "walker":
            raw_score = 1
    
    # === FALLS ===
    elif key == "falls":
        if normalized == "multiple":
            raw_score = 3
            flags.add("falls_multiple")
        elif normalized == "one":
            raw_score = 1
            flags.add("fall_recent")
    
    # === MEDICATION ===
    elif key == "meds_complexity":
        if normalized == "complex":
            raw_score = 3
        elif normalized == "moderate":
            raw_score = 2
        elif normalized == "simple":
            raw_score = 1
    
    # === HELP OVERALL ===
    elif key == "help_overall":
        if normalized == "full_support":
            raw_score = 3
            flags.add("high_dependence")
        elif normalized == "daily_help":
            raw_score = 2
        elif normalized == "some_help":
            raw_score = 1
    
    # === BADLs (capped, with severity weighting) ===
    elif key == "badls":
        if isinstance(value, list) and len(value) > 0:
            # Critical BADLs (safety/dignity): toileting, bathing, transferring, mobility
            critical_badls = {"toileting", "bathing", "transferring", "mobility"}
            
            critical_count = sum(1 for item in value if item in critical_badls)
            other_count = len(value) - critical_count
            
            # Scoring: Critical items weigh more heavily
            # 1-2 critical OR 1-3 other = 1 point (mild dependency)
            # 3+ critical OR 4+ other = 2 points (moderate dependency)
            # All critical (4) OR 6+ total = 3 points (severe dependency)
            if critical_count >= 4 or len(value) >= 6:
                raw_score = 3  # Severe dependency
                flags.add("high_dependence")
            elif critical_count >= 3 or len(value) >= 4:
                raw_score = 2  # Moderate dependency
                flags.add("high_dependence")
            elif critical_count >= 1 or len(value) >= 2:
                raw_score = 1  # Mild dependency
            else:
                raw_score = 1  # Any help needed
    
    # === IADLs (capped, with severity weighting) ===
    elif key == "iadls":
        if isinstance(value, list) and len(value) > 0:
            # Critical IADLs (safety): finances, med_management
            critical_iadls = {"finances", "med_management"}
            
            critical_count = sum(1 for item in value if item in critical_iadls)
            other_count = len(value) - critical_count
            
            # Scoring: Critical items (finances, meds) indicate cognitive/safety risk
            # 1-2 critical OR 1-3 other = 1 point
            # 2 critical OR 4+ other = 2 points
            # 2 critical + 4+ other = 3 points (comprehensive support needed)
            if critical_count >= 2 and len(value) >= 5:
                raw_score = 3  # Comprehensive support needed
                flags.add("high_dependence")
            elif critical_count >= 2 or len(value) >= 4:
                raw_score = 2  # Moderate support needed
            else:
                raw_score = 1  # Some support needed
    
    # === SUPPORT HOURS ===
    elif key == "hours_per_day":
        if normalized == "24h":
            raw_score = 3
            flags.add("support_strong")
        elif normalized == "4-8h":
            raw_score = 2
        elif normalized == "1-3h":
            raw_score = 1
        elif normalized == "<1h":
            raw_score = 0
            flags.add("no_support")  # Changed from support_none to match CSV
    
    # === PRIMARY SUPPORT ===
    elif key == "primary_support":
        if normalized == "none":
            raw_score = 3
            flags.add("no_support")
        elif normalized == "family":
            raw_score = 1
            flags.add("informal_support")
        elif normalized in ("paid", "agency"):
            raw_score = 2
            flags.add("formal_support")
    
    # === CHRONIC CONDITIONS (each adds 1, capped at 3 per CSV) ===
    elif key == "chronic_conditions":
        if isinstance(value, list):
            raw_score = min(len(value), 3)  # Cap at 3
            if len(value) > 0:
                flags.add("chronic_present")
    
    # === ADDITIONAL CONDITIONS ===
    elif key == "additional_conditions":
        if isinstance(value, list):
            # Check for dementia-related in text
            text = " ".join(str(v).lower() for v in value)
            if "dementia" in text or "alzheimer" in text:
                flags.add("cog_severe")
    
    # === MOOD (low weight per CSV) ===
    elif key == "mood":
        if normalized == "low":
            raw_score = 2
            flags.add("emo_concern")
        elif normalized in ("okay", "mostly_good"):
            raw_score = 1
    
    # === ISOLATION (modifier only, weight 1) ===
    elif key == "isolation":
        if normalized == "very":
            raw_score = 2
            flags.add("geo_isolated")
        elif normalized == "somewhat":
            raw_score = 1
    
    return raw_score, flags


def _apply_overrides(base_tier: int, flags: Set[str], answers: Dict[str, Any]) -> tuple[int, Optional[str]]:
    """
    Apply CSV OVERRIDE rules (strongest clinical decision rules).
    
    Returns:
        (final_tier, override_reason)
    """
    
    # OVERRIDE 1: High-Acuity Memory Care (Strongest rule)
    # cog_severe AND no_support → Tier 4
    if "cog_severe" in flags and "no_support" in flags:
        return 4, "memory_care_override_high_acuity"
    
    # OVERRIDE 2: Memory Care minimum
    # cog_severe → Tier ≥ 3
    if "cog_severe" in flags:
        return max(base_tier, 3), "memory_care_override"
    
    # OVERRIDE 3: Memory Care for high burden/safety
    # high_dependence (ADL/IADL ≥ 2) AND (behavior_risk OR falls_multiple) → Tier ≥ 3
    if "high_dependence" in flags and ("behavior_risk" in flags or "falls_multiple" in flags):
        return max(base_tier, 3), "memory_care_high_burden_safety"
    
    # OVERRIDE 4: Assisted Living due to falls + no support
    # falls_multiple AND no_support → Tier ≥ 2
    if "falls_multiple" in flags and "no_support" in flags:
        return max(base_tier, 2), "assisted_living_falls_no_support"
    
    # OVERRIDE 5: Medical instability
    # unstable AND chronic_present ≥ 3 → Tier ≥ 3
    chronic_count = len(answers.get("chronic_conditions", []))
    if "unstable" in flags and chronic_count >= 3:
        return max(base_tier, 3), "memory_care_medical_instability"
    
    return base_tier, None


def _apply_modifiers(tier: int, flags: Set[str]) -> tuple[int, List[str]]:
    """
    Apply CSV MODIFIER rules (adjustments to base tier).
    
    Returns:
        (adjusted_tier, modifier_reasons)
    """
    modifiers = []
    
    # MODIFIER 1: Strong support reduces tier
    # support_strong AND NOT (cog_severe OR cog_moderate with behaviors) → Tier = max(Tier - 1, 0)
    # Rationale: Strong support can manage mild needs, but not moderate/severe cognitive issues
    if "support_strong" in flags:
        # Don't reduce if severe cognitive issues
        if "cog_severe" not in flags:
            # Don't reduce if moderate cognitive with behaviors (memory care still needed)
            if not ("cog_moderate" in flags and "behavior_risk" in flags):
                tier = max(tier - 1, 0)
                modifiers.append("strong_support_reduces_tier")
    
    # MODIFIER 2: Isolation with limited support adds risk
    # geo_isolated AND (support_none OR no_support) → Tier = min(Tier + 1, 4)
    if "geo_isolated" in flags and "no_support" in flags:
        tier = min(tier + 1, 4)
        modifiers.append("isolation_with_no_support_increases_tier")
    
    # MODIFIER 3: Very well managed conditions
    # stable → Tier = max(Tier - 1, 0)
    if "stable" in flags and tier > 0:
        tier = max(tier - 1, 0)
        modifiers.append("stable_conditions_reduces_tier")
    
    return tier, modifiers


def _calculate_base_tier(total_score: int) -> int:
    """Map total weighted score to base tier using thresholds."""
    for tier, (min_score, max_score) in TIER_THRESHOLDS.items():
        if min_score <= total_score <= max_score:
            return tier
    # Fallback: if score exceeds all thresholds, return highest tier
    return 3


def _generate_summary_points(answers: Dict[str, Any], flags: Set[str], tier: int) -> List[str]:
    """Generate contextual summary points for results display."""
    points = []
    
    # High-priority alerts first
    if "cog_severe" in flags and "no_support" in flags:
        points.append("⚠️ Severe memory issues with no daily support require immediate specialized care")
    elif "cog_severe" in flags:
        points.append("⚠️ Significant memory challenges suggest need for specialized memory care")
    
    if "falls_multiple" in flags and "no_support" in flags:
        points.append("⚠️ Multiple falls with limited support pose serious safety risks")
    
    # Independence snapshot
    help_level = _normalize_answer("help_overall", answers.get("help_overall"))
    badls = answers.get("badls", [])
    iadls = answers.get("iadls", [])
    
    if help_level == "full_support":
        independence = "Needs full-time support with daily activities"
    elif help_level == "daily_help":
        independence = "Needs regular daily assistance"
    elif help_level == "some_help":
        independence = "Needs occasional help with some tasks"
    else:
        independence = "Mostly independent"
    
    if badls and isinstance(badls, list) and len(badls) > 0:
        independence += f" (help with {len(badls)} basic activities)"
    if iadls and isinstance(iadls, list) and len(iadls) > 0:
        independence += f" (help with {len(iadls)} daily tasks)"
    
    points.append(f"Daily function: {independence}")
    
    # Cognitive status
    memory = _normalize_answer("memory_changes", answers.get("memory_changes"))
    if memory == "severe":
        cognitive = "Severe memory issues or dementia diagnosis"
    elif memory == "moderate":
        cognitive = "Moderate memory or thinking challenges"
    elif memory == "occasional":
        cognitive = "Occasional forgetfulness"
    else:
        cognitive = "No cognitive concerns"
    
    behaviors = answers.get("behaviors", [])
    if behaviors and len(behaviors) > 0:
        cognitive += f" with {len(behaviors)} behavioral concerns"
    
    points.append(f"Cognitive health: {cognitive}")
    
    # Support network
    hours = _normalize_answer("hours_per_day", answers.get("hours_per_day"))
    primary = _normalize_answer("primary_support", answers.get("primary_support"))
    
    if hours == "24h":
        support = "24-hour support in place"
    elif hours == "4-8h":
        support = "4-8 hours daily support"
    elif hours == "1-3h":
        support = "1-3 hours daily support"
    else:
        support = "Less than 1 hour daily support"
    
    if primary == "none":
        support += " (no regular caregiver)"
    elif primary == "family":
        support += " (family caregivers)"
    
    points.append(f"Support network: {support}")
    
    # Safety factors
    safety_notes = []
    mobility = _normalize_answer("mobility", answers.get("mobility"))
    falls = _normalize_answer("falls", answers.get("falls"))
    
    if mobility == "bedbound":
        safety_notes.append("bed-bound")
    elif mobility == "wheelchair":
        safety_notes.append("wheelchair user")
    elif mobility == "walker":
        safety_notes.append("uses walker")
    
    if falls == "multiple":
        safety_notes.append("multiple falls")
    elif falls == "one":
        safety_notes.append("recent fall")
    
    if safety_notes:
        points.append(f"Safety considerations: {', '.join(safety_notes)}")
    
    return points


def derive_outcome(answers: Dict[str, Any], context: Dict[str, Any]) -> OutcomeContract:
    """
    Hybrid scoring logic combining CSV clinical model with current module structure.
    
    Scoring Process:
    1. Normalize answers to match CSV expectations
    2. Score each answer with domain weights
    3. Cap domains per CSV rules
    4. Calculate base tier from total score
    5. Apply OVERRIDE rules (high-acuity, memory care, etc.)
    6. Apply MODIFIER rules (support, isolation adjustments)
    7. Generate summary and flags
    
    Args:
        answers: User responses from module
        context: Additional context (debug flags, etc.)
    
    Returns:
        OutcomeContract with recommendation, confidence, flags, and summary
    """
    
    # Validate inputs
    if not answers:
        return OutcomeContract(
            recommendation="incomplete",
            confidence=0.0,
            flags={"incomplete": True},
            tags=[],
            domain_scores={},
            summary={
                "points": ["No answers provided. Please complete the assessment."],
                "total_score": 0,
                "tier": 0
            },
            routing={},
            audit={}
        )
    
    # === STEP 1: Score all answers by domain ===
    domain_scores = {
        "adl_iadl": 0,
        "cognitive": 0,
        "support": 0,
        "mobility": 0,
        "medication": 0,
        "health": 0,
        "mood": 0,
        "isolation": 0
    }
    
    all_flags = set()
    scoring_audit = {}
    
    # Score each question
    question_domain_map = {
        "memory_changes": "cognitive",
        "behaviors": "cognitive",
        "mobility": "mobility",
        "falls": "mobility",
        "meds_complexity": "medication",
        "help_overall": "adl_iadl",
        "badls": "adl_iadl",
        "iadls": "adl_iadl",
        "hours_per_day": "support",
        "primary_support": "support",
        "chronic_conditions": "health",
        "additional_conditions": "health",
        "mood": "mood",
        "isolation": "isolation"
    }
    
    # First, collect RAW scores per domain (before applying domain weights)
    domain_raw_scores = {domain: 0 for domain in domain_scores.keys()}
    
    for key, value in answers.items():
        if key not in question_domain_map:
            continue
        
        domain = question_domain_map[key]
        
        raw_score, flags = _score_question(key, value, domain, 0)  # Weight not used in function
        
        domain_raw_scores[domain] += raw_score
        all_flags.update(flags)
        
        scoring_audit[key] = {
            "raw": raw_score,
            "domain": domain,
            "flags": list(flags)
        }
    
    # Now apply domain weights to domain totals
    for domain, raw_total in domain_raw_scores.items():
        weight = DOMAIN_WEIGHTS.get(domain, 1)
        domain_scores[domain] = raw_total * weight
        
    # Update audit with weighted scores
    for key in scoring_audit:
        domain = scoring_audit[key]["domain"]
        weight = DOMAIN_WEIGHTS.get(domain, 1)
        scoring_audit[key]["weight"] = weight
        scoring_audit[key]["weighted"] = scoring_audit[key]["raw"] * weight
    
    # Apply domain caps
    if domain_scores["cognitive"] > DOMAIN_CAPS["cognitive"] * DOMAIN_WEIGHTS["cognitive"]:
        domain_scores["cognitive"] = DOMAIN_CAPS["cognitive"] * DOMAIN_WEIGHTS["cognitive"]
    
    if domain_scores["health"] > DOMAIN_CAPS["health"] * DOMAIN_WEIGHTS["health"]:
        domain_scores["health"] = DOMAIN_CAPS["health"] * DOMAIN_WEIGHTS["health"]
    
    # === STEP 2: Calculate total score ===
    total_score = sum(domain_scores.values())
    
    # === STEP 2.5: Apply situational boosts for safety concerns ===
    # Cognitive issues + no support = significant safety risk
    if ("cog_moderate" in all_flags or "cog_severe" in all_flags) and "no_support" in all_flags:
        safety_boost = 5  # Significant boost for unsafe cognitive situation
        total_score += safety_boost
        all_flags.add("cognitive_safety_risk")
        scoring_audit["safety_boost_cognitive_no_support"] = {
            "raw": safety_boost,
            "domain": "safety_adjustment",
            "flags": ["cognitive_safety_risk"],
            "weight": 1,
            "weighted": safety_boost
        }
    
    # High mobility issues + no support = fall risk
    if "falls_multiple" in all_flags and "no_support" in all_flags:
        safety_boost = 3  # Moderate boost for fall risk without support
        total_score += safety_boost
        all_flags.add("fall_risk_no_support")
        scoring_audit["safety_boost_falls_no_support"] = {
            "raw": safety_boost,
            "domain": "safety_adjustment",
            "flags": ["fall_risk_no_support"],
            "weight": 1,
            "weighted": safety_boost
        }
    
    # === STEP 3: Calculate base tier ===
    base_tier = _calculate_base_tier(total_score)
    
    # === STEP 4: Apply OVERRIDE rules ===
    tier_after_overrides, override_reason = _apply_overrides(base_tier, all_flags, answers)
    
    # === STEP 5: Apply MODIFIER rules ===
    final_tier, modifiers = _apply_modifiers(tier_after_overrides, all_flags)
    
    # === STEP 6: Map to recommendation ===
    recommendation = TIER_NAMES.get(final_tier, "in_home_support")
    
    # === STEP 7: Calculate confidence ===
    # High confidence for override rules
    if override_reason:
        confidence = 0.9
    # Moderate confidence for clear tier boundaries
    elif final_tier in (0, 3, 4):
        confidence = 0.85
    # Lower confidence for middle tiers
    else:
        confidence = 0.75
    
    # Adjust for completeness
    critical_questions = ["memory_changes", "mobility", "help_overall", "primary_support", "meds_complexity"]
    answered_critical = sum(1 for q in critical_questions if answers.get(q))
    completeness = answered_critical / len(critical_questions)
    confidence = confidence * completeness
    
    # === STEP 8: Generate summary ===
    summary_points = _generate_summary_points(answers, all_flags, final_tier)
    
    # === STEP 9: Build flags dict for handoff (including additional_services compatibility) ===
    flags_dict = {flag: True for flag in all_flags}
    
    # Add convenience flags for additional_services module
    if any(k.startswith("cog_") for k in flags_dict):
        flags_dict["cognitive_risk"] = True  # For SeniorLife AI visibility
    
    meds = _normalize_answer("meds_complexity", answers.get("meds_complexity"))
    if meds in ("moderate", "complex"):
        flags_dict["meds_management_needed"] = True  # For Omcare visibility
    
    if "falls_multiple" in flags_dict or "fall_risk_no_support" in flags_dict:
        flags_dict["fall_risk"] = True  # For SeniorLife AI visibility
    
    # Debug output
    if context.get("debug"):
        print("\n=== GCP V3 SCORING DEBUG ===")
        print(f"Total Score: {total_score}")
        print(f"Domain Scores: {domain_scores}")
        print(f"Base Tier: {base_tier}")
        print(f"After Overrides: {tier_after_overrides} (reason: {override_reason})")
        print(f"Final Tier: {final_tier} (modifiers: {modifiers})")
        print(f"Recommendation: {recommendation}")
        print(f"Confidence: {confidence:.2%}")
        print(f"Flags: {sorted(all_flags)}")
        print("============================\n")
    
    return OutcomeContract(
        recommendation=recommendation,
        confidence=round(confidence, 2),
        flags=flags_dict,
        tags=[],
        domain_scores=domain_scores,
        summary={
            "points": summary_points,
            "total_score": round(total_score, 1),
            "tier": final_tier,
            "base_tier": base_tier,
            "override_reason": override_reason,
            "modifiers": modifiers
        },
        routing={},
        audit={
            "scoring_breakdown": scoring_audit,
            "domain_scores": domain_scores,
            "tier_progression": {
                "base": base_tier,
                "after_overrides": tier_after_overrides,
                "final": final_tier
            },
            "rules_applied": {
                "override": override_reason,
                "modifiers": modifiers
            }
        }
    )


# Alias for backward compatibility
compute = derive_outcome


if __name__ == "__main__":
    # Quick test
    test_answers = {
        "memory_changes": "severe",
        "primary_support": "none",
        "mobility": "walker",
        "falls": "one",
        "help_overall": "daily_help",
        "meds_complexity": "moderate"
    }
    
    result = derive_outcome(test_answers, {"debug": True})
    print(f"\nTest Result: {result.recommendation} (Tier {result.summary['tier']})")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Summary: {result.summary['points']}")
