"""
GCP v4 Care Recommendation Logic - Self-contained scoring engine.

This module respects module.json as the authoritative source of truth:
- Reads scores directly from option.score values in module.json
- Uses flags already set by module engine from option.flags
- Calculates tier based on total score thresholds
- Returns MCIP-compatible CareRecommendation dict
"""

import json
import os
from pathlib import Path
from typing import Any

from .flags import build_flags

# Import flag manager for persisting flags
try:
    from core import flag_manager

    FLAG_MANAGER_AVAILABLE = True
except ImportError:
    FLAG_MANAGER_AVAILABLE = False


def mc_behavior_gate_enabled() -> bool:
    """Check if moderate×high behavior gate is enabled.
    
    Behavior gate prevents MC/MC-HA recommendations for moderate cognition + high support
    cases UNLESS risky cognitive behaviors are present.
    
    Priority: Streamlit Secrets → environment variable → default (off)
    
    Returns:
        True if gate is enabled
    """
    try:
        import streamlit as st
        v = st.secrets.get("FEATURE_GCP_MC_BEHAVIOR_GATE")
        if v is not None:
            return str(v).lower() == "on"
    except Exception:
        pass
    
    return os.getenv("FEATURE_GCP_MC_BEHAVIOR_GATE", "off").lower() == "on"


def gcp_hours_mode() -> str:
    """Check hours/day suggestion feature mode.
    
    Controls hours/day baseline + LLM refinement:
    - "off": No suggestion (default)
    - "shadow": Compute suggestion but don't show in UI (logging only)
    - "assist": Show suggestion to user (non-binding)
    
    Priority: Streamlit Secrets → environment variable → default (off)
    
    Returns:
        Mode string: "off" | "shadow" | "assist"
    """
    try:
        import streamlit as st
        v = st.secrets.get("FEATURE_GCP_HOURS")
        if v is not None:
            mode = str(v).lower()
            if mode in {"off", "shadow", "assist"}:
                return mode
    except Exception:
        pass
    
    mode = os.getenv("FEATURE_GCP_HOURS", "off").lower()
    return mode if mode in {"off", "shadow", "assist"} else "off"


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

# Cognitive high-risk flags/behaviors that gate memory care access
COGNITIVE_HIGH_RISK = {
    "wandering",
    "elopement",
    "aggression",
    "severe_sundowning",
    "severe_cognitive_risk",
    "memory_support",
}

# Tier map cache (loaded from tier_map.json)
_TIER_MAP_CACHE = None


def _load_tier_map() -> dict:
    """Load tier map from JSON file (cached).
    
    Returns:
        Dict mapping (cognition_band, support_band) -> tier
    """
    global _TIER_MAP_CACHE
    
    if _TIER_MAP_CACHE is not None:
        return _TIER_MAP_CACHE
    
    tier_map_path = Path(__file__).parent / "tier_map.json"
    
    try:
        with open(tier_map_path, "r") as f:
            _TIER_MAP_CACHE = json.load(f)
        return _TIER_MAP_CACHE
    except Exception as e:
        print(f"[GCP_WARN] Could not load tier_map.json: {e}")
        # Return empty dict as fallback
        return {}


def cognitive_gate(answers: dict[str, Any], flags: list[str]) -> bool:
    """Determine if cognitive criteria are met for memory care access.
    
    Memory care requires moderate/severe memory changes OR risky behaviors.
    This is a HARD gate - without it, MC/MC-HA are blocked.
    
    Args:
        answers: User responses from GCP module
        flags: Flags set by assessment
    
    Returns:
        True if memory care access should be allowed
    """
    # Check memory_changes level
    mem = (answers.get("memory_changes") or "").lower()
    if mem in ("moderate", "severe"):
        return True
    
    # Check for risky behaviors
    behaviors = answers.get("behaviors") or []
    risky_behav = set(b.lower() for b in behaviors)
    if len(risky_behav & COGNITIVE_HIGH_RISK) > 0:
        return True
    
    # Check for cognitive risk flags
    flags_lower = set(f.lower() for f in (flags or []))
    if len(flags_lower & COGNITIVE_HIGH_RISK) > 0:
        return True
    
    return False


def cognition_band(answers: dict[str, Any], flags: list[str]) -> str:
    """Derive cognition band from memory changes and behaviors.
    
    Returns:
        One of: "none", "mild", "moderate", "high"
    """
    mem = (answers.get("memory_changes") or "").lower()
    behaviors = answers.get("behaviors") or []
    risky_behav = set(b.lower() for b in behaviors)
    
    # Count risky behaviors
    risky_count = len(risky_behav & COGNITIVE_HIGH_RISK)
    
    # High: severe memory OR multiple risky behaviors
    if mem == "severe" or risky_count >= 2:
        return "high"
    
    # Moderate: moderate memory OR single risky behavior
    if mem == "moderate" or risky_count >= 1:
        return "moderate"
    
    # Mild: mild memory changes
    if mem == "mild":
        return "mild"
    
    # None: no significant cognitive issues
    return "none"


def support_band(answers: dict[str, Any], flags: list[str]) -> str:
    """Derive support band from ADLs, mobility, falls, meds.
    
    Returns:
        One of: "low", "moderate", "high", "24h"
    """
    # Count BADL challenges
    badls = answers.get("badls") or []
    badl_count = len(badls) if isinstance(badls, list) else 0
    
    # Count IADL challenges
    iadls = answers.get("iadls") or []
    iadl_count = len(iadls) if isinstance(iadls, list) else 0
    
    # Check mobility
    mobility = (answers.get("mobility") or "").lower()
    
    # Check falls
    falls = (answers.get("falls") or "").lower()
    
    # Check meds complexity
    meds = (answers.get("meds_complexity") or "").lower()
    
    # 24h: wheelchair/bedbound OR multiple BADLs + high falls
    if mobility in ("wheelchair", "bedbound") or (badl_count >= 3 and falls == "multiple"):
        return "24h"
    
    # High: multiple BADLs OR significant mobility + falls
    if badl_count >= 2 or (mobility in ("walker", "cane") and falls in ("once", "multiple")):
        return "high"
    
    # Moderate: some IADLs OR single BADL OR meds complexity
    if iadl_count >= 2 or badl_count >= 1 or meds in ("moderate", "complex"):
        return "moderate"
    
    # Low: minimal support needs
    return "low"


def cognitive_gate_behaviors_only(answers: dict[str, Any], flags: list[str]) -> bool:
    """Check if risky behaviors are present (for disagreement logging).
    
    Used to identify cases where MC recommendation might be driven by
    behaviors rather than pure cognition band.
    
    Args:
        answers: User responses from GCP module
        flags: Flags set by assessment
    
    Returns:
        True if risky cognitive behaviors present
    """
    risky_flags = {"wandering", "elopement", "aggression", "severe_sundowning", 
                   "severe_cognitive_risk", "memory_support"}
    
    behaviors = set((answers.get("behaviors") or []))
    flags_set = set(flags or [])
    
    return bool(behaviors & risky_flags) or bool(flags_set & risky_flags)


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


def compute_section_feedback(
    answers: dict[str, Any],
    section_name: str,
    context: dict[str, Any] = None,
) -> None:
    """Generate LLM feedback after a section completes (shadow/assist mode only).
    
    Builds a partial GCPContext from answers so far and calls the LLM to
    generate contextual Navi advice and a running tier estimate.
    
    Stores result in session state for potential UI use (assist mode).
    In shadow mode, only logs results without affecting UI.
    
    Args:
        answers: Current user responses (partial)
        section_name: Section identifier (about_you, health_safety, daily_living, etc.)
        context: Context dict from module engine
    """
    try:
        from ai.llm_client import get_feature_gcp_mode
        llm_mode = get_feature_gcp_mode()
        
        if llm_mode not in ("shadow", "assist"):
            return  # Off mode, skip LLM
        
        # Build partial GCP context from answers so far
        from ai.gcp_navi_engine import generate_section_advice
        from ai.gcp_schemas import GCPContext
        
        gcp_context = _build_gcp_context(answers, context or {})
        
        # Generate section advice
        ok, advice = generate_section_advice(gcp_context, section_name, mode=llm_mode)
        
        if ok and advice:
            # Store in session state for potential UI use
            import streamlit as st
            session_key = f"_gcp_llm_section_{section_name}"
            st.session_state[session_key] = {
                "tier": advice.tier,
                "reasons": advice.reasons,
                "risks": advice.risks,
                "navi_messages": advice.navi_messages,
                "questions_next": advice.questions_next,
                "confidence": advice.confidence,
            }
    
    except Exception as e:
        # Silent failure - LLM must not affect flow
        print(f"[GCP_LLM_SECTION] Exception (silent) - section={section_name}: {e}")


def build_partial_gcp_context(section_id: str, answers: dict[str, Any], flags: list[str]) -> Any:
    """Build partial GCPContext for per-section LLM feedback.
    
    Constructs a GCPContext with only fields relevant to the completed section.
    Uses safe defaults for fields not yet answered.
    
    Args:
        section_id: Section identifier (e.g., "about_you", "medication_mobility")
        answers: User responses collected so far
        flags: Flags set by completed sections
    
    Returns:
        GCPContext instance with partial data
    """
    from ai.gcp_schemas import GCPContext
    
    # Build partial context based on section
    # Use safe defaults for unanswered fields
    
    ctx_data = {
        "age_range": answers.get("age_range", "75-84"),
        "living_situation": answers.get("living_situation", "unknown"),
        "has_partner": answers.get("living_situation") == "with_spouse_or_partner",
        "meds_complexity": answers.get("medications", "none"),
        "mobility": answers.get("mobility", "independent"),
        "falls": answers.get("falls", "none"),
        "badls": answers.get("badls", []),
        "iadls": answers.get("iadls", []),
        "memory_changes": answers.get("memory_changes", "none"),
        "behaviors": answers.get("behaviors", []),
        "isolation": answers.get("isolation", "moderate"),
        "move_preference": None,  # Only set after move_preferences section
        "flags": flags,
    }
    
    # Override defaults with actual answers for this section
    if section_id == "about_you":
        # Only age_range, living_situation, isolation are valid
        pass  # Already populated above
    
    elif section_id == "medication_mobility":
        # meds_complexity, mobility, falls, chronic_conditions are valid
        pass  # Already populated above
    
    elif section_id == "cognition_mental_health":
        # memory_changes, mood, behaviors are valid
        ctx_data["memory_changes"] = answers.get("memory_changes", "none")
        ctx_data["behaviors"] = answers.get("behaviors", [])
    
    elif section_id == "daily_living":
        # badls, iadls are valid
        pass  # Already populated above
    
    elif section_id == "move_preferences":
        # move_preference is valid
        move_pref = answers.get("move_preference")
        if move_pref is not None:
            try:
                ctx_data["move_preference"] = int(move_pref)
            except (ValueError, TypeError):
                ctx_data["move_preference"] = None
    
    return GCPContext(**ctx_data)


def _build_gcp_context(answers: dict[str, Any], context: dict[str, Any]) -> Any:
    """Build GCPContext from GCP answers for LLM analysis.
    
    Extracts relevant fields from answers and constructs a GCPContext
    object suitable for LLM-based care recommendation.
    
    Args:
        answers: User responses from GCP module
        context: Context dict from module engine
    
    Returns:
        GCPContext instance
    """
    from ai.gcp_schemas import GCPContext
    
    # Extract age range from context or answers
    age_range = context.get("age_range", "unknown")
    if not age_range or age_range == "unknown":
        # Try to derive from answers if present
        age_range = answers.get("age_range", "75-84")  # Default to common range
    
    # Extract living situation
    living_situation = answers.get("living_situation", "unknown")
    
    # Extract partner status
    has_partner = answers.get("has_partner", False)
    if isinstance(has_partner, str):
        has_partner = has_partner.lower() in ("yes", "true", "1")
    
    # Extract medication complexity
    meds_complexity = answers.get("meds_complexity", "simple")
    
    # Extract mobility
    mobility = answers.get("mobility", "independent")
    
    # Extract falls
    falls = answers.get("falls", "no_falls")
    
    # Extract BADLs (Basic ADLs)
    badls = answers.get("badls", [])
    if not isinstance(badls, list):
        badls = []
    
    # Extract IADLs (Instrumental ADLs)
    iadls = answers.get("iadls", [])
    if not isinstance(iadls, list):
        iadls = []
    
    # Extract memory changes
    memory_changes = answers.get("memory_changes", "no_changes")
    
    # Extract behaviors
    behaviors = answers.get("behaviors", [])
    if not isinstance(behaviors, list):
        behaviors = []
    
    # Extract isolation
    isolation = answers.get("isolation", "minimal")
    
    # Extract move preference
    move_preference = _derive_move_preference(answers)
    
    # Extract flags
    flag_ids = _extract_flags_from_state(answers)
    if not flag_ids:
        flag_ids = _extract_flags_from_answers(answers, _load_module_json())
    
    return GCPContext(
        age_range=age_range,
        living_situation=living_situation,
        has_partner=has_partner,
        meds_complexity=meds_complexity,
        mobility=mobility,
        falls=falls,
        badls=badls,
        iadls=iadls,
        memory_changes=memory_changes,
        behaviors=behaviors,
        isolation=isolation,
        move_preference=move_preference,
        flags=flag_ids,
    )


def _build_hours_context(answers: dict[str, Any], flags: list[str]) -> Any:
    """Build HoursContext for hours/day suggestion.
    
    Extracts minimal signals from answers for baseline + LLM refinement.
    
    Args:
        answers: User responses
        flags: Flag IDs (e.g., ["wandering", "aggression"])
    
    Returns:
        HoursContext instance (from ai.hours_schemas)
    """
    from ai.hours_schemas import HoursContext
    
    # Count BADLs
    badls = answers.get("badls", [])
    if not isinstance(badls, list):
        badls = []
    badls_count = len(badls)
    
    # Count IADLs
    iadls = answers.get("iadls", [])
    if not isinstance(iadls, list):
        iadls = []
    iadls_count = len(iadls)
    
    # Falls
    falls = answers.get("falls", "none")
    
    # Mobility
    mobility = answers.get("mobility", "independent")
    
    # Risky behaviors (check flags)
    risky_behaviors = bool(set(flags) & COGNITIVE_HIGH_RISK)
    
    # Meds complexity
    meds_complexity = answers.get("meds_complexity", "none")
    
    # Primary support
    primary_support = answers.get("primary_support", "none")
    
    # Overnight needed (heuristic: help_overall == "full_support" or 24h current)
    help_overall = answers.get("help_overall", "independent")
    raw_hours = answers.get("hours_per_day")
    overnight_needed = (help_overall == "full_support" or raw_hours == "24h")
    
    # Get user's current hours selection (validate it's a valid band)
    import streamlit as st
    current = raw_hours or st.session_state.get("gcp_hours_user_choice")
    valid_bands = {"<1h", "1-3h", "4-8h", "24h"}
    current_hours = current if current in valid_bands else None
    
    return HoursContext(
        badls_count=badls_count,
        iadls_count=iadls_count,
        falls=falls,
        mobility=mobility,
        risky_behaviors=risky_behaviors,
        meds_complexity=meds_complexity,
        primary_support=primary_support,
        overnight_needed=overnight_needed,
        current_hours=current_hours,
    )


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

    # Determine tier from score (traditional point-sum approach)
    tier_from_score = _determine_tier(total_score)

    # ====================================================================
    # COGNITIVE GATES + 2-AXIS MAPPING
    # ====================================================================
    # Compute allowed tiers based on cognitive assessment
    # Memory care requires moderate/severe memory changes OR risky behaviors
    flags = _extract_flags_from_state(answers) or _extract_flags_from_answers(answers, module_data)
    
    # Determine if cognitive gate passes
    passes_cognitive_gate = cognitive_gate(answers, flags)
    
    # Derive cognition and support bands
    cog_band = cognition_band(answers, flags)
    sup_band = support_band(answers, flags)
    
    # Load tier map and compute base recommendation
    tier_map = _load_tier_map()
    tier_from_mapping = None
    
    if tier_map and cog_band in tier_map and sup_band in tier_map.get(cog_band, {}):
        tier_from_mapping = tier_map[cog_band][sup_band]
    
    # Build allowed tiers set
    from ai.gcp_schemas import CANONICAL_TIERS
    allowed_tiers = set(CANONICAL_TIERS)
    
    if not passes_cognitive_gate:
        # Block memory care tiers
        allowed_tiers -= {"memory_care", "memory_care_high_acuity"}
        print(f"[GCP_GUARD] Cognitive gate FAILED (cog={cog_band} sup={sup_band}) - MC/MC-HA blocked")
    else:
        print(f"[GCP_GUARD] Cognitive gate PASSED (cog={cog_band} sup={sup_band}) - all tiers allowed")
    
    # --- Behavior gate for moderate × high without risky behaviors ---
    gate_on = mc_behavior_gate_enabled()
    risky = cognitive_gate_behaviors_only(answers, flags)  # True iff any of COGNITIVE_HIGH_RISK present
    print(f"[GCP_FLAG] MC_BEHAVIOR_GATE={gate_on} cog={cog_band} sup={sup_band} risky={risky} allowed_pre={sorted(list(allowed_tiers))}")
    
    if gate_on and cog_band == "moderate" and sup_band == "high" and not risky:
        # remove MC and MC-HA from allowed before selecting det tier
        if "memory_care" in allowed_tiers or "memory_care_high_acuity" in allowed_tiers:
            allowed_tiers.discard("memory_care")
            allowed_tiers.discard("memory_care_high_acuity")
            print(f"[GCP_GUARD] moderate×high without risky behaviors → remove {{'memory_care','memory_care_high_acuity'}} from allowed: {sorted(list(allowed_tiers))}")
    # --- end behavior gate ---
    
    # ====================================================================
    # HOURS/DAY SUGGESTION (GUARDED): Baseline + LLM refinement + Nudge
    # ====================================================================
    # Compute hours/day suggestion if enabled (shadow/assist mode)
    hours_mode = gcp_hours_mode()
    if hours_mode in {"shadow", "assist"}:
        try:
            from ai.hours_engine import (
                baseline_hours,
                generate_hours_advice,
                under_selected,
                generate_hours_nudge_text
            )
            
            # Build context
            hours_ctx = _build_hours_context(answers, flags)
            
            # Get baseline
            baseline = baseline_hours(hours_ctx)
            
            # Get LLM refinement
            ok, advice = generate_hours_advice(hours_ctx, hours_mode)
            
            # Determine suggested band (prefer LLM if available, else baseline)
            suggested = advice.band if (ok and advice) else baseline
            user_band = hours_ctx.current_hours
            
            # Generate nudge if user under-selected
            nudge_text = None
            severity = None
            if under_selected(user_band, suggested):
                nudge_text = generate_hours_nudge_text(hours_ctx, suggested, user_band, hours_mode)
                if nudge_text:
                    severity = "strong"
                    # Store nudge in advice object if available
                    if ok and advice:
                        advice.nudge_text = nudge_text
                        advice.severity = severity
            
            # Store suggestion in session state
            try:
                import streamlit as st
                st.session_state["_hours_suggestion"] = {
                    "band": suggested,
                    "base": baseline,
                    "llm": advice.band if (ok and advice) else None,
                    "conf": advice.confidence if (ok and advice) else None,
                    "reasons": advice.reasons if (ok and advice) else [],
                    "mode": hours_mode,
                    "user": user_band,
                    "nudge_text": nudge_text,
                    "severity": severity,
                }
            except Exception:
                pass
            
            # Log (dev-only) - include user selection
            user_choice = user_band or "-"
            if ok and advice:
                print(f"[GCP_HOURS_{hours_mode.upper()}] base={baseline} user={user_choice} llm={advice.band} conf={advice.confidence:.2f}")
            else:
                print(f"[GCP_HOURS_{hours_mode.upper()}] base={baseline} user={user_choice} llm=None (fallback to baseline)")
            
            # Log nudge if generated (shadow mode visibility)
            if nudge_text:
                print(f"[GCP_HOURS_NUDGE_{hours_mode.upper()}] user={user_choice} → suggest={suggested} | {nudge_text}")
            
            # Log case for offline analysis (training data)
            try:
                from tools.log_hours import log_hours_case
                log_hours_case(
                    context=hours_ctx,
                    base_band=baseline,
                    llm_band=advice.band if (ok and advice) else None,
                    llm_conf=advice.confidence if (ok and advice) else None,
                    mode=hours_mode
                )
            except Exception as log_err:
                print(f"[HOURS_LOG_ERROR] Failed to log case: {log_err}")
        
        except Exception as e:
            print(f"[GCP_HOURS_WARN] Hours suggestion failed: {e}")
    
    # Choose final deterministic tier
    # Priority: mapping (if available and in allowed) > score-based (if in allowed) > fallback to best permitted
    chosen = None
    
    if tier_from_mapping and tier_from_mapping in allowed_tiers:
        chosen = tier_from_mapping
        print(f"[GCP_GUARD] Using tier_map result: {chosen} (mapping: {cog_band}×{sup_band})")
    elif tier_from_score and tier_from_score in allowed_tiers:
        chosen = tier_from_score
        print(f"[GCP_GUARD] Using score-based tier: {chosen} (score={total_score})")
    else:
        # Fallback to best permitted tier given the map order: prefer assisted_living, else in_home, else none
        for cand in ("assisted_living", "in_home", "none", "memory_care", "memory_care_high_acuity"):
            if cand in allowed_tiers:
                chosen = cand
                print(f"[GCP_GUARD] fallback chosen tier={cand} due to constraints; mapping={tier_from_mapping} score={tier_from_score} allowed={sorted(list(allowed_tiers))}")
                break
    
    det_tier = chosen or (tier_from_mapping or tier_from_score or "none")
    
    # Ensure MC/MC-HA is downgraded if not allowed (safety check)
    if det_tier in {"memory_care", "memory_care_high_acuity"} and "memory_care" not in allowed_tiers:
        print("[GCP_GUARD] forced downgrade: MC/MC-HA not allowed → det=assisted_living")
        det_tier = "assisted_living"
    
    tier = det_tier
    
    # Persist recommendation category to session state for conditional rendering
    # This enables show_if conditions to access $state.recommendation.category
    _persist_recommendation_category(tier)

    # ====================================================================
    # LLM-ASSISTED GCP (GUARDED): Generate additive Navi advice
    # ====================================================================
    # Read FEATURE_LLM_GCP flag; if shadow/assist, call LLM for contextual advice
    # Deterministic engine ALWAYS remains source of truth for final tier
    llm_advice = None
    try:
        from ai.llm_client import get_feature_gcp_mode
        llm_mode = get_feature_gcp_mode()
        
        if llm_mode in ("shadow", "assist"):
            # Build GCP context from answers
            from ai.gcp_navi_engine import generate_gcp_advice, reconcile_with_deterministic
            from ai.gcp_schemas import GCPContext
            
            gcp_context = _build_gcp_context(answers, context or {})
            
            # JSON-safe helper for serializing context
            def _jsonify_ctx(ctx):
                import json
                try:
                    if hasattr(ctx, "model_dump"):
                        return ctx.model_dump()
                    return json.loads(json.dumps(ctx, default=str))
                except Exception as e:
                    return {"_note": "context_unserializable",
                            "type": str(type(ctx)),
                            "err": str(e)}
            
            # Store context for disagreement logging (no PHI)
            try:
                import streamlit as st
                st.session_state["_gcp_context_for_logging"] = {
                    "answers": answers,
                    "flags": list(flags or []),
                    "allowed_tiers": sorted(list(allowed_tiers)),
                    "context": _jsonify_ctx(context or {})
                }
            except Exception:
                pass  # Silent failure if streamlit not available
            
            # Generate LLM advice (with guardrails) - pass allowed_tiers to scope LLM
            print(f"[GCP_FLAG] allowed_tiers_sent={sorted(list(allowed_tiers))}")
            ok, advice = generate_gcp_advice(gcp_context, mode=llm_mode, allowed_tiers=sorted(list(allowed_tiers)))
            
            if ok and advice:
                # Reconcile with deterministic (logs disagreements)
                reconcile_with_deterministic(tier, advice, llm_mode)
                
                # Store advice for UI rendering (assist mode only)
                llm_advice = advice
                
                # Final recommendation logging (det vs llm)
                print(
                    f"[GCP_LLM_FINAL] det={tier} llm={advice.tier} "
                    f"conf={advice.confidence:.2f} "
                    f"msgs={len(advice.navi_messages)} reasons={len(advice.reasons)}"
                )
            else:
                print(f"[GCP_LLM_{llm_mode.upper()}] ok=False (generation failed)")
                
    except Exception as e:
        # Silent failure - LLM must not affect deterministic flow
        print(f"[GCP_LLM_ERROR] Exception (silent): {e}")
    # ====================================================================

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

    # Store LLM advice in session state (for UI rendering in assist mode)
    if llm_advice:
        try:
            import streamlit as st
            st.session_state["_gcp_llm_advice"] = {
                "tier": llm_advice.tier,
                "reasons": llm_advice.reasons,
                "risks": llm_advice.risks,
                "navi_messages": llm_advice.navi_messages,
                "questions_next": llm_advice.questions_next,
                "confidence": llm_advice.confidence,
            }
        except Exception:
            pass  # Silent failure if streamlit not available

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
