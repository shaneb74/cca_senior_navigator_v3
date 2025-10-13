import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.modules.schema import OutcomeContract


def sections_to_inputs(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract all input questions from manifest sections."""
    inputs: List[Dict[str, Any]] = []
    for section in manifest.get("sections", []):
        inputs.extend(section.get("questions", []))
    return inputs


def _score_from_options(questions: List[Dict[str, Any]], key: str, answers: Dict[str, Any]) -> int:
    """Get score for a single-select answer from question options."""
    val = answers.get(key)
    if not val:
        return 0
    
    for question in questions:
        q_id = question.get("id") or question.get("key")
        if q_id != key:
            continue
        for option in question.get("options", []):
            opt_value = option.get("value", option.get("label"))
            if opt_value == val:
                try:
                    return int(option.get("score", 0))
                except (ValueError, TypeError):
                    return 0
    return 0


def _score_multi(
    questions: List[Dict[str, Any]],
    key: str,
    answers: Dict[str, Any],
    cap: Optional[int] = None,
) -> int:
    """Get cumulative score for multi-select answers, with optional cap."""
    values = answers.get(key) or []
    if not isinstance(values, list):
        values = [values]
    
    total = 0
    for question in questions:
        q_id = question.get("id") or question.get("key")
        if q_id != key:
            continue
        per_question_scores = {
            option.get("value", option.get("label")): int(option.get("score", 0))
            for option in question.get("options", [])
        }
        for value in values:
            total += per_question_scores.get(value, 0)
        if cap is not None:
            try:
                total = min(total, int(cap))
            except (ValueError, TypeError):
                pass
        return total
    return 0

def _eval(rule: dict, ctx: dict) -> bool:
    if not rule:
        return True
    if "all" in rule: return all(_eval(r, ctx) for r in rule["all"])
    if "any" in rule: return any(_eval(r, ctx) for r in rule["any"])
    if "eq" in rule:
        k, v = rule["eq"]; return ctx.get(k) == v
    if "neq" in rule:
        k, v = rule["neq"]; return ctx.get(k) != v
    if "in" in rule:
        k, arr = rule["in"]; return ctx.get(k) in arr
    if "not_in" in rule:
        k, arr = rule["not_in"]; return ctx.get(k) not in arr
    if "includes" in rule:
        # Check if array contains value (for multi-select fields like badls, iadls)
        arr_key, value = rule["includes"]
        arr = ctx.get(arr_key) or []
        return value in arr if isinstance(arr, (list, tuple, set)) else False
    if "lt" in rule:
        k, t = rule["lt"]; return float(ctx.get(k, 0)) < float(t)
    if "lte" in rule:
        k, t = rule["lte"]; return float(ctx.get(k, 0)) <= float(t)
    if "gt" in rule:
        k, t = rule["gt"]; return float(ctx.get(k, 0)) > float(t)
    if "gte" in rule:
        k, t = rule["gte"]; return float(ctx.get(k, 0)) >= float(t)
    if "len_gt" in rule:
        k, t = rule["len_gt"]; return len(ctx.get(k) or []) > int(t)
    if "len_gte" in rule:
        k, t = rule["len_gte"]; return len(ctx.get(k) or []) >= int(t)
    if "len_lt" in rule:
        k, t = rule["len_lt"]; return len(ctx.get(k) or []) < int(t)
    if "len_lte" in rule:
        k, t = rule["len_lte"]; return len(ctx.get(k) or []) <= int(t)
    return False

def _confidence_label(confidence: float) -> str:
    """Convert confidence score to human-readable label."""
    if confidence >= 0.9:
        return "High confidence"
    elif confidence >= 0.7:
        return "Moderate confidence"
    elif confidence >= 0.5:
        return "Low confidence"
    else:
        return "Insufficient data"


def _generate_summary_points(
    answers: dict, 
    score: float, 
    recommendation: str, 
    tier: int,
    flags: dict
) -> List[str]:
    """Generate contextual, actionable summary bullet points."""
    points = []
    
    # Lead with the recommendation
    points.append(f"**Recommended care level:** {recommendation}")
    
    # Identify key driving factors
    factors = []
    
    # Daily living assistance needs
    help_level = answers.get("help_overall", "")
    if help_level in ["daily_help", "full_support"]:
        factors.append("significant daily assistance needs")
    
    # Cognitive/memory concerns
    memory = answers.get("memory_changes", "")
    if memory in ["moderate", "severe"]:
        factors.append("cognitive/memory concerns")
        if memory == "severe":
            points.append("⚠️ **Memory care environment strongly recommended** for safety and specialized support")
    
    # Mobility and fall risk
    mobility = answers.get("mobility", "")
    falls = answers.get("falls", "")
    if mobility in ["wheelchair", "bedbound"] or falls == "multiple":
        factors.append("mobility limitations and/or fall risk")
        if falls == "multiple":
            points.append("⚠️ **Fall prevention critical** - environment should minimize hazards and provide monitoring")
    
    # Medication complexity
    meds = answers.get("meds_complexity", "")
    if meds in ["moderate", "complex"]:
        factors.append("medication management complexity")
    
    # Support network concerns
    support = answers.get("primary_support", "")
    hours = answers.get("hours_per_day", "")
    if support == "none" or hours == "24h":
        factors.append("limited informal support network")
    
    # ADL dependencies
    badls = answers.get("badls", [])
    if isinstance(badls, list) and len(badls) >= 2:
        factors.append(f"assistance needed with {len(badls)} basic activities")
        adl_list = ", ".join(badls[:3])
        if len(badls) > 3:
            adl_list += f", and {len(badls) - 3} more"
        points.append(f"**Care needs:** Requires help with {adl_list}")
    
    # Summarize driving factors
    if factors:
        points.insert(1, f"**Key considerations:** {'; '.join(factors)}")
    
    # Add tier-specific next steps
    if tier >= 3:  # Memory Care or Skilled Nursing
        points.append("**Next steps:** Schedule tours of specialized memory care facilities; consult with geriatric care specialist; review financial planning options")
    elif tier >= 2:  # Assisted Living
        points.append("**Next steps:** Visit assisted living communities in your area; meet with admissions directors; discuss transition plan with family")
    elif tier >= 1:  # In-home with support
        points.append("**Next steps:** Research in-home care agencies; assess home for safety modifications; consider adult day programs")
    else:  # Independent
        points.append("**Next steps:** Implement preventive measures; schedule regular wellness check-ins; plan for future care needs")
    
    # Add chronic condition context if relevant
    chronic = answers.get("chronic_conditions", [])
    if isinstance(chronic, list) and len(chronic) > 0:
        condition_list = ", ".join(chronic[:3])
        if len(chronic) > 3:
            condition_list += f" (+ {len(chronic) - 3} more)"
        points.append(f"**Health considerations:** Managing {condition_list}")
    
    # Add high-priority flag messages
    high_priority_flags = [
        flags[f].get("message") 
        for f, data in flags.items() 
        if data.get("priority") == "high" and data.get("message")
    ]
    if high_priority_flags:
        for msg in high_priority_flags[:2]:  # Limit to 2 most important
            if msg and msg not in " ".join(points):
                points.append(f"⚠️ {msg}")
    
    return points


def derive(manifest: Dict[str, Any], answers: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Derive care recommendation from user assessment responses.
    
    Args:
        manifest: Module configuration with scoring rules and decision tree
        answers: User responses to assessment questions
        context: Additional context (product, debug flags, etc.)
    
    Returns:
        {
            "tier": str,              # Care level recommendation
            "score": float,           # Weighted numeric score
            "points": List[str],      # Summary bullet points
            "confidence": float,      # 0-1 confidence score
            "confidence_label": str,  # Human-readable confidence
            "flags": dict,            # Active warning flags
            "metadata": dict          # Additional scoring details
        }
    """
    # Validate inputs
    if not answers:
        return {
            "tier": "Unable to determine",
            "score": 0,
            "points": ["No answers provided. Please complete the assessment."],
            "confidence": 0.0,
            "confidence_label": "Insufficient data",
            "flags": {},
            "metadata": {}
        }
    
    # Normalize answer values to match OLD manifest expectations
    # The new module_config.json uses full label text as values, but OLD manifest expects short codes
    normalized_answers = dict(answers)
    
    # Normalize memory_changes
    memory_val = str(normalized_answers.get("memory_changes", "")).lower()
    if "severe" in memory_val or "dementia" in memory_val or "alzheimer" in memory_val:
        normalized_answers["memory_changes"] = "severe"
    elif "moderate" in memory_val:
        normalized_answers["memory_changes"] = "moderate"
    elif "occasional" in memory_val:
        normalized_answers["memory_changes"] = "occasional"
    elif "no concern" in memory_val:
        normalized_answers["memory_changes"] = "none"
    
    # Normalize meds_complexity
    meds_val = str(normalized_answers.get("meds_complexity", "")).lower()
    if "complex" in meds_val:
        normalized_answers["meds_complexity"] = "complex"
    elif "moderate" in meds_val:
        normalized_answers["meds_complexity"] = "moderate"
    elif "simple" in meds_val:
        normalized_answers["meds_complexity"] = "simple"
    elif "none" in meds_val:
        normalized_answers["meds_complexity"] = "none"
    
    # Normalize mobility
    mobility_val = str(normalized_answers.get("mobility", "")).lower()
    if "wheelchair" in mobility_val or "scooter" in mobility_val:
        normalized_answers["mobility"] = "wheelchair"
    elif "bed" in mobility_val or "bedbound" in mobility_val:
        normalized_answers["mobility"] = "bedbound"
    elif "walker" in mobility_val or "cane" in mobility_val:
        normalized_answers["mobility"] = "walker"
    elif "independent" in mobility_val or "walks" in mobility_val:
        normalized_answers["mobility"] = "independent"
    
    # Normalize falls
    falls_val = str(normalized_answers.get("falls", "")).lower()
    if "multiple" in falls_val:
        normalized_answers["falls"] = "multiple"
    elif "one" in falls_val or "once" in falls_val:
        normalized_answers["falls"] = "one"
    elif "no" in falls_val or "none" in falls_val:
        normalized_answers["falls"] = "none"
    
    # Normalize mood
    mood_val = str(normalized_answers.get("mood", "")).lower()
    if "low" in mood_val or "down" in mood_val:
        normalized_answers["mood"] = "low"
    elif "okay" in mood_val or "ups and downs" in mood_val:
        normalized_answers["mood"] = "okay"
    elif "great" in mood_val or "positive" in mood_val:
        normalized_answers["mood"] = "great"
    
    # Normalize isolation
    isolation_val = str(normalized_answers.get("isolation", "")).lower()
    if "very" in isolation_val:
        normalized_answers["isolation"] = "very"
    elif "somewhat" in isolation_val:
        normalized_answers["isolation"] = "somewhat"
    elif "easy" in isolation_val or "accessible" in isolation_val:
        normalized_answers["isolation"] = "easy"
    
    # Check for critical required fields
    required_keys = ["memory_changes", "mobility", "help_overall"]
    missing = [k for k in required_keys if k not in normalized_answers or not normalized_answers.get(k)]
    if missing:
        return {
            "tier": "Incomplete assessment",
            "score": 0,
            "points": [
                "⚠️ Assessment incomplete",
                f"Missing critical information: {', '.join(missing)}",
                "Please complete all required questions for an accurate recommendation."
            ],
            "confidence": 0.0,
            "confidence_label": "Insufficient data",
            "flags": {},
            "metadata": {"missing_fields": missing}
        }
    
    questions = sections_to_inputs(manifest)
    logic = manifest.get("logic", {})
    scored_inputs = logic.get("scored_inputs", [])
    
    # Calculate weighted score using NORMALIZED answers
    total = 0.0
    score_breakdown = {}
    
    for scored in scored_inputs:
        key = scored.get("id")
        if not key:
            continue
        
        weight = float(scored.get("weight", 1))
        score_cap = scored.get("score_cap")
        domain = scored.get("domain", "General")
        
        if isinstance(normalized_answers.get(key), list):
            raw = _score_multi(questions, key, normalized_answers, score_cap)
        else:
            raw = _score_from_options(questions, key, normalized_answers)
            if score_cap is not None:
                raw = min(raw, int(score_cap))
        
        weighted = raw * weight
        total += weighted
        
        # Track scoring breakdown by domain
        if domain not in score_breakdown:
            score_breakdown[domain] = {"raw": 0, "weighted": 0, "count": 0}
        score_breakdown[domain]["raw"] += raw
        score_breakdown[domain]["weighted"] += weighted
        score_breakdown[domain]["count"] += 1
    
    # Build context for decision tree using NORMALIZED answers
    ctx = dict(normalized_answers)
    ctx["score"] = total
    
    # Evaluate decision tree
    tier = 0
    recommendation = None
    matched_rule = None
    
    for idx, node in enumerate(logic.get("decision_tree", [])):
        if _eval(node.get("if", {}), ctx):
            recommendation = node.get("recommendation")
            tier = node.get("tier", tier)
            matched_rule = idx
            break
    
    # Apply modifiers
    modifiers_applied = []
    for modifier in logic.get("modifiers", []):
        if _eval(modifier.get("if", {}), ctx):
            action = modifier.get("action")
            value = int(modifier.get("value", 1))
            if action == "increase_tier":
                tier = int(tier or 0) + value
                modifiers_applied.append(f"Tier increased by {value}")
            elif action == "decrease_tier":
                tier = int(tier or 0) - value
                modifiers_applied.append(f"Tier decreased by {value}")
    
    # Clamp tier and set default recommendation
    tier = max(0, min(int(tier or 0), 4))
    if recommendation is None:
        recommendation = "Independent / In-Home"
    
    # Evaluate flags
    flags = {}
    flag_config = logic.get("flags", {})
    for flag_name, flag_rule in flag_config.items():
        if _eval(flag_rule.get("if", {}), ctx):
            flags[flag_name] = {
                "priority": flag_rule.get("priority", "medium"),
                "message": flag_rule.get("message", "")
            }
    
    # Calculate confidence
    total_questions = len(questions)
    answered_questions = len([k for k in answers.keys() if answers.get(k)])
    completeness = answered_questions / total_questions if total_questions > 0 else 0
    
    # Boost confidence if critical questions answered
    critical_answered = all(
        answers.get(k) for k in ["memory_changes", "mobility", "help_overall", "primary_support", "meds_complexity"]
    )
    confidence = completeness * (1.1 if critical_answered else 0.9)
    confidence = min(1.0, max(0.0, confidence))
    
    # Generate detailed summary points
    points = _generate_summary_points(answers, total, recommendation, tier, flags)
    
    # Build metadata
    metadata = {
        "total_score": round(total, 2),
        "tier_level": tier,
        "matched_rule_index": matched_rule,
        "modifiers_applied": modifiers_applied,
        "score_breakdown": score_breakdown,
        "answered_count": answered_questions,
        "total_questions": total_questions
    }
    
    # Debug output if requested
    if context.get("debug"):
        print("\n=== CARE RECOMMENDATION DEBUG ===")
        print(f"Total score: {total} (tier {tier})")
        print(f"Recommendation: {recommendation}")
        print(f"Confidence: {confidence:.2%}")
        print(f"Flags: {list(flags.keys())}")
        print(f"Modifiers: {modifiers_applied}")
        print("=================================\n")
    
    return {
        "tier": recommendation,
        "score": round(total, 2),
        "points": points,
        "confidence": round(confidence, 2),
        "confidence_label": _confidence_label(confidence),
        "flags": flags,
        "metadata": metadata
    }


def derive_outcome(answers: Dict[str, Any], context: Dict[str, Any]) -> OutcomeContract:
    """
    Wrapper for the module engine - loads manifest and calls derive().
    
    Expected by core.modules.engine when specified in outcomes_compute.
    
    Merges flags from two sources:
    1. Field-level effects (set during step navigation in answers["flags"])
    2. Outcome-level logic (computed from manifest rules)
    """
    # Load the OLD scoring manifest (kept for backward compatibility with derive() logic)
    # The UI flow uses module_config.json, but scoring uses this legacy format
    manifest_path = Path(__file__).parent / "module.json.OLD"
    with manifest_path.open() as f:
        manifest = json.load(f)
    
    # Call the main derive function
    result = derive(manifest, answers, context)
    
    # Extract detailed flags from result (computed from manifest logic)
    detailed_flags = result.get("flags", {})
    
    # Build simplified boolean flags for handoff from manifest-computed flags
    simple_flags = {k: True for k in detailed_flags.keys()}
    
    # MERGE in field-level effect flags (set during step navigation)
    # These are stored in answers["flags"] by core.modules.engine._apply_step_effects
    field_flags = answers.get("flags", {})
    if isinstance(field_flags, dict):
        for flag_key, flag_value in field_flags.items():
            if flag_value is True:  # Only set True flags
                simple_flags[flag_key] = True
    
    # Add simplified flag names for easier service matching
    # These are set based on DIRECT answer values, not just manifest flag logic
    
    # Cognitive risk: set if ANY cognition_risk_* flag OR moderate/severe memory selection
    if any(k.startswith("cognition_risk") for k in simple_flags):
        simple_flags["cognitive_risk"] = True
    
    # Medication management: set if moderate/complex meds OR any medication-related flag
    # Check the actual answer value directly to ensure Omcare shows for any moderate+ complexity
    meds_val = str(answers.get("meds_complexity", "")).lower()
    if "medication_risk" in simple_flags or "medication_adherence_risk" in simple_flags:
        simple_flags["meds_management_needed"] = True
    elif "moderate" in meds_val or "complex" in meds_val:
        # Set flag directly if moderate or complex medication complexity
        simple_flags["meds_management_needed"] = True
    
    # Fall risk: keep as-is from manifest
    if "fall_risk" in simple_flags:
        simple_flags["fall_risk"] = True
    
    # Convert to OutcomeContract
    return OutcomeContract(
        recommendation=result.get("tier"),
        confidence=result.get("confidence"),
        flags=simple_flags,
        tags=[],
        domain_scores=result.get("metadata", {}).get("score_breakdown", {}),
        summary={
            "points": result.get("points", []),
            "score": result.get("score", 0),
            "confidence_label": result.get("confidence_label", ""),
        },
        routing={},
        audit=result.get("metadata", {}),
    )


if __name__ == "__main__":
    import json
    manifest = json.load(open("module.json"))
    answers = {"memory_changes": "moderate", "falls": "multiple", "primary_support": "none"}
    print(derive(manifest, answers, {}))
