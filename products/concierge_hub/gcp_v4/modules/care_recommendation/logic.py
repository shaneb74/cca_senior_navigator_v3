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
    """Resolve FEATURE_GCP_HOURS flag from secrets or environment."""
    import os

    import streamlit as st
    try:
        v = st.secrets.get("FEATURE_GCP_HOURS")
        if v:
            return str(v).strip().strip('"').lower()
    except Exception:
        pass
    v = os.getenv("FEATURE_GCP_HOURS")
    return str(v).strip().strip('"').lower() if v else "off"


def get_llm_tier_mode() -> str:
    """Resolve FEATURE_GCP_LLM_TIER flag from secrets or environment.
    
    Returns:
        "off" | "shadow" | "replace" (default: "shadow")
    """
    try:
        import os

        import streamlit as st
        v = st.secrets.get("FEATURE_GCP_LLM_TIER", None)
        if v is None:
            v = os.getenv("FEATURE_GCP_LLM_TIER", "shadow")
        return str(v).strip().strip('"').lower()
    except Exception:
        import os
        return str(os.getenv("FEATURE_GCP_LLM_TIER", "shadow")).strip().strip('"').lower()


def _choose_final_tier(
    det_tier: str,
    allowed_tiers: set[str],
    llm_tier: str | None,
    llm_conf: float | None,
    bands: dict,
    risky: bool
) -> tuple[str, dict]:
    """Return (final_tier, decision_info) using LLM-first policy with deterministic fallback.
    
    LLM-First Policy:
    1) If LLM_TIER exists AND LLM_TIER ∈ ALLOWED_TIERS → CHOSEN = LLM_TIER (source=llm).
    2) Else if LLM_TIER missing/timeout/invalid OR not in ALLOWED_TIERS → CHOSEN = DET_TIER (source=fallback).
    3) Confidence is NOT used to override; it is logged for analytics only.
    
    This function is PURE - no Streamlit state modifications.
    
    Args:
        det_tier: Deterministic tier recommendation (backup)
        allowed_tiers: Set of tiers allowed by cognitive/behavioral gates
        llm_tier: LLM-recommended tier (if available)
        llm_conf: LLM confidence score (if available)
        bands: Dict with cognitive and support bands {"cog": str, "sup": str}
        risky: True if risky cognitive behaviors present
        
    Returns:
        Tuple of (final_tier, decision_info_dict) where decision_info contains:
        - source: "llm" or "fallback"
        - reason: Why this tier was chosen
        - adjudication_reason: Code for logging/analytics
    """
    info = {
        "det": det_tier,
        "llm": llm_tier,
        "conf": llm_conf,
        "allowed": sorted(list(allowed_tiers)),
        "bands": bands,
        "risky": risky,
        "reason": "deterministic",
        "source": "fallback",
        "adjudication_reason": "unknown"
    }

    # Edge case: both tiers missing (shouldn't happen)
    if not det_tier and not llm_tier:
        default_tier = "assisted_living"  # Safe default
        info["reason"] = "double_missing_default"
        info["adjudication_reason"] = "double_missing_default"
        info["source"] = "fallback"
        return default_tier, info

    # Rule 1: LLM exists and is in allowed set → use LLM (primary path)
    if llm_tier and llm_tier in allowed_tiers:
        info["reason"] = "llm_valid"
        info["source"] = "llm"
        info["adjudication_reason"] = "llm_valid"
        return llm_tier, info

    # Rule 2: LLM invalid or missing → fallback to deterministic (backup path)
    if llm_tier is None:
        info["reason"] = "llm_timeout_or_error"
        info["adjudication_reason"] = "llm_timeout"
    elif llm_tier not in allowed_tiers:
        info["reason"] = "llm_disallowed_by_guard"
        info["adjudication_reason"] = "llm_guard_disallow"
    else:
        # This shouldn't happen, but handle edge case
        info["reason"] = "llm_invalid_unknown"
        info["adjudication_reason"] = "llm_invalid_unknown"

    info["source"] = "fallback"

    # Emit fallback warning for monitoring (< 2% expected)
    import uuid
    fallback_id = str(uuid.uuid4())[:12]
    print(f"[LLM_FALLBACK] reason={info['adjudication_reason']} det={det_tier} llm={llm_tier or 'none'} id={fallback_id}")

    return det_tier, info


def ensure_summary_ready(answers: dict, flags: list[str], tier: str) -> None:
    """
    Computes summary context + LLM advice once, stores to session so UI
    can render immediately (no widget interaction required).
    Also applies tier decision policy if FEATURE_GCP_LLM_TIER="replace".
    Safe to call repeatedly (idempotent).
    """
    try:
        import streamlit as st
    except Exception:
        return  # Only meaningful in Streamlit runtime

    # Check if summary is already ready using session state flags
    if st.session_state.get("summary_ready", False):
        # Summary already computed and ready
        print("[GCP_RENDER] Using cached summary result")
        return

    # Check if LLM result is already cached for this session (legacy check)
    llm_result_ready = st.session_state.get("gcp.llm_result_ready", False)
    if llm_result_ready:
        # Use cached result, skip LLM call
        import uuid
        cache_id = str(uuid.uuid4())[:12]
        try:
            has_advice = bool(st.session_state.get("_summary_advice"))
            keys = "summary_ready,llm_result_ready,_summary_advice" if has_advice else "summary_ready,llm_result_ready"
            print(f"[LLM_CACHE] ready=True keys={keys} id={cache_id}")
        except Exception:
            pass
        print("[GCP_RENDER] Using cached LLM result")
        st.session_state["summary_ready"] = True
        return

    # Set loading state at start of summary computation
    st.session_state["llm_loading"] = True
    st.session_state["summary_ready"] = False

    summary_ctx = {
        "badls": answers.get("badls", []),
        "iadls": answers.get("iadls", []),
        "mobility": answers.get("mobility"),
        "falls": answers.get("falls"),
        "behaviors": answers.get("behaviors", []),
        "meds_complexity": answers.get("meds_complexity"),
        "isolation": answers.get("isolation"),
        "has_partner": ("has_partner" in (flags or [])) or st.session_state.get("has_partner", False),
    }

    hours = st.session_state.get("_hours_suggestion", {}) or {}
    user_hours = st.session_state.get("gcp_hours_user_choice")
    suggested = hours.get("band")

    try:
        from ai.llm_client import get_feature_gcp_mode
        from ai.summary_engine import generate_summary
        mode = get_feature_gcp_mode()  # "shadow"|"assist"|others
    except Exception:
        # If imports fail, don't attempt LLM
        mode = "off"
        generate_summary = None

    # Log effective mode on RESULTS
    try:
        print(f"[LLM_MODE] {mode}")
    except Exception:
        pass

    # Generate correlation ID for tracing
    import uuid
    correlation_id = str(uuid.uuid4())[:12]

    ok = False
    adv_obj = None
    if generate_summary is not None:
        try:
            ok, adv_obj = generate_summary(summary_ctx, tier, suggested, user_hours, mode, correlation_id)
        except Exception:
            ok, adv_obj = False, None
    else:
        ok, adv_obj = False, None

    # Log the call outcome with advice presence
    try:
        print(f"[LLM_CALL] ok={bool(ok)} advice={'yes' if adv_obj else 'no'}")
    except Exception:
        pass

    if ok and adv_obj:
        try:
            d = adv_obj.model_dump() if hasattr(adv_obj, 'model_dump') else dict(getattr(adv_obj, '__dict__', {}))
            d.setdefault("tier", tier)
            st.session_state["_summary_advice"] = d

            # Mark summary as ready and clear loading state
            st.session_state["summary_ready"] = True
            st.session_state["llm_loading"] = False

            # Concise LLM vs deterministic log + disagreement capture
            try:
                from core.logging import get_flag
                TRAIN_LOG_ALL = (get_flag("FEATURE_TRAIN_LOG_ALL", "off") in {"on", "true", "1", "yes"})

                det = tier
                # Prefer advice tier; else fall back to deterministic tier
                llm_tier = d.get("tier") or d.get("recommended_tier") or tier
                conf = float(d.get("confidence", 0.0) or 0.0)
                aligned = (det == llm_tier)

                print(f"[GCP_LLM_SUMMARY] det={det} llm={llm_tier} aligned={aligned} conf={conf:.2f}")

                if llm_tier and not aligned:
                    from tools.log_disagreement import append_case
                    row = {
                        "gcp_context": {"answers": answers, "flags": list(flags or [])},
                        "det_tier": det,
                        "llm_tier": llm_tier,
                        "llm_conf": conf
                    }
                    append_case(row)
                    print("[GCP_LOG] disagreement captured")
                elif TRAIN_LOG_ALL:
                    from tools.log_disagreement import append_case
                    row = {
                        "gcp_context": {"answers": answers, "flags": list(flags or [])},
                        "det_tier": det,
                        "llm_tier": llm_tier,
                        "llm_conf": conf,
                        "aligned": True
                    }
                    append_case(row)
            except Exception:
                pass  # Never fail on logging

        except Exception:
            # If we cannot serialize, treat as failure
            st.session_state.pop("_summary_advice", None)
            # Clear loading state even on failure
            st.session_state["llm_loading"] = False
            st.session_state["summary_ready"] = False
    else:
        # Create graceful fallback text based on tier instead of leaving blank
        try:
            print(f"[LLM_FALLBACK] reason=parse_error tier={tier} id={correlation_id}")
        except Exception:
            pass

        # Generate safe fallback headline based on tier
        tier_display_map = {
            "assisted_living": "Assisted Living",
            "memory_care": "Memory Care",
            "memory_care_high_acuity": "Memory Care",
            "in_home": "In-Home Care",
            "in_home_care": "In-Home Care"
        }
        tier_display = tier_display_map.get(tier, tier.replace("_", " ").title())

        fallback_headline = f"We've matched {tier_display} based on your answers."
        if tier in ["in_home", "in_home_care"]:
            fallback_headline += " You can adjust hours anytime."
        else:
            fallback_headline += " You can adjust details anytime."

        fallback_advice = {
            "tier": tier,
            "headline": fallback_headline,
            "what_it_means": f"{tier_display} provides the level of support that matches your current needs.",
            "why": ["Based on your assessment responses"],
            "next_line": "Let's explore the costs and see how to make it work for you.",
            "confidence": 0.8
        }

        st.session_state["_summary_advice"] = fallback_advice
        # Clear loading state when using fallback
        st.session_state["llm_loading"] = False
        st.session_state["summary_ready"] = False

    # ====================================================================
    # TIER DECISION POLICY (LLM-FIRST WITH DETERMINISTIC FALLBACK)
    # ====================================================================
    # ALWAYS use LLM-first logic regardless of mode.
    # Mode only affects logging verbosity, not the decision path.
    tier_mode = get_llm_tier_mode()  # "off"|"shadow"|"assist"|"adjust"

    # Get LLM tier and confidence from advice
    d = st.session_state.get("_summary_advice") or {}
    llm_tier = d.get("tier") or d.get("recommended_tier")
    llm_conf = float(d.get("confidence", 0.0) or 0.0)

    # Compute allowed tiers (same logic as in derive_outcome)
    try:
        from ai.gcp_schemas import CANONICAL_TIERS
        allowed_tiers = set(CANONICAL_TIERS)

        # Apply cognitive gate
        passes_cognitive = cognitive_gate(answers, flags)
        if not passes_cognitive:
            allowed_tiers -= {"memory_care", "memory_care_high_acuity"}

        # Apply behavior gate if enabled
        gate_on = mc_behavior_gate_enabled()
        cog_band = cognition_band(answers, flags)
        supervision_bucket_legacy = support_band(answers, flags)  # Diagnostic only

        # For routing/gates, map 24h → high
        sup_band_for_routing = "high" if supervision_bucket_legacy == "24h" else supervision_bucket_legacy
        risky = cognitive_gate_behaviors_only(answers, flags)

        if gate_on and cog_band == "moderate" and sup_band_for_routing == "high" and not risky:
            allowed_tiers.discard("memory_care")
            allowed_tiers.discard("memory_care_high_acuity")

        bands = {"cog": cog_band, "sup": sup_band_for_routing}

    except Exception:
        # Fallback: all tiers allowed, no bands
        from ai.gcp_schemas import CANONICAL_TIERS
        allowed_tiers = set(CANONICAL_TIERS)
        bands = {"cog": "unknown", "sup": "unknown"}
        risky = False

    # ALWAYS apply LLM-first decision logic (deterministic is fallback only)
    final_tier, decision = _choose_final_tier(
        det_tier=tier,
        allowed_tiers=allowed_tiers,
        llm_tier=llm_tier,
        llm_conf=llm_conf,
        bands=bands,
        risky=risky
    )

    # Publish chosen tier (single source of truth)
    st.session_state["gcp.final_tier"] = final_tier
    st.session_state["gcp.adjudication_decision"] = decision  # Store for CarePlan creation

    # Update advice object with final tier for UI consistency
    if final_tier != tier and d:
        d["tier"] = final_tier
        st.session_state["_summary_advice"] = d

    # Generate correlation ID for tracing
    import uuid
    corr_id = str(uuid.uuid4())[:12]

    # Single-line adjudication log (ALWAYS emitted, shows source)
    source = decision.get("source", "unknown")
    reason = decision.get("adjudication_reason", "unknown")

    # Fire emoji if LLM disagreed with deterministic AND was used
    if final_tier != tier and source == "llm":
        print(f"\n{'🔥'*40}")
        print("[DISAGREEMENT] LLM overrode deterministic engine!")
        print(f"[DISAGREEMENT] Deterministic: {tier} → LLM: {final_tier}")
        print(f"[DISAGREEMENT] Reason: {reason}")
        print(f"{'🔥'*40}\n")

    print(f"[GCP_ADJ] chosen={final_tier} llm={llm_tier or 'none'} det={tier} source={source} allowed={decision['allowed']} conf={llm_conf or 0.0:.2f} reason={reason} id={corr_id}")

    # Legacy mode logging (for analytics/debugging only - does NOT affect publish)
    if tier_mode in ("shadow", "off"):
        mode_msg = "LLM disabled" if tier_mode == "off" else "diagnostic logging only"
        print(f"[GCP_MODE] mode={tier_mode} ({mode_msg}) published={final_tier} source={source}")

    # NOW reconcile with deterministic for mismatch logging (after adjudication_decision is set)
    try:
        from ai.gcp_navi_engine import reconcile_with_deterministic
        # Build advice-like object for reconcile
        class AdjudicatedAdvice:
            def __init__(self, tier, conf):
                self.tier = tier
                self.confidence = conf

        if llm_tier:
            advice_for_reconcile = AdjudicatedAdvice(llm_tier, llm_conf)
            reconcile_with_deterministic(tier, advice_for_reconcile, tier_mode)
    except Exception as e:
        print(f"[GCP_RECONCILE_ERROR] {e}")

    # Training/audit row
    try:
        from tools.log_disagreement import append_case
        row = {
            "det_tier": tier,
            "llm_tier": llm_tier,
            "llm_conf": llm_conf,
            "final_tier": final_tier,
            "allowed_tiers": sorted(list(allowed_tiers)),
            "bands": decision["bands"],
            "risky": decision["risky"],
            "reason": decision["reason"],
            "answers": answers,
            "flags": list(flags),
        }
        append_case(row)
    except Exception:
        pass  # Never fail on logging

    # Clear hours suggestion for facility-based tiers when not comparing with in-home
    # Use final tier from canonical helper (post-adjudication)
    # Hours only apply to in-home scenarios OR when comparing facility with in-home
    from core.modules.engine import get_final_recommendation_tier
    
    published_tier = get_final_recommendation_tier(st.session_state)
    facility_tiers = ["assisted_living", "memory_care", "memory_care_high_acuity"]
    compare_inhome = st.session_state.get("cost.compare_inhome", False)

    if published_tier in facility_tiers and not compare_inhome:
        # Get person_id for person-scoped clearing (dual flow support)
        person_id = st.session_state.get("person_id", "self")
        hours_key = f"_hours_suggestion_{person_id}"

        # Clear person-scoped hours suggestion
        if hours_key in st.session_state:
            st.session_state.pop(hours_key, None)
            print(f"[HOURS_CLEAR] Cleared {hours_key} for facility tier={published_tier} (not comparing)")

        # Also clear legacy global key for backward compatibility
        if "_hours_suggestion" in st.session_state:
            st.session_state.pop("_hours_suggestion", None)
            print(f"[HOURS_CLEAR] Cleared legacy _hours_suggestion for facility tier={published_tier}")

    # ====================================================================

    st.session_state["_summary_ready"] = True
    # Set cache flag to prevent duplicate LLM calls on subsequent renders
    st.session_state["gcp.llm_result_ready"] = True

    # Explicit readiness marker
    try:
        present = bool(st.session_state.get("_summary_advice"))
        print(f"[SUMMARY_READY] present={present} cached=True")
    except Exception:
        pass


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
        with open(tier_map_path) as f:
            _TIER_MAP_CACHE = json.load(f)
        return _TIER_MAP_CACHE
    except Exception as e:
        print(f"[GCP_WARN] Could not load tier_map.json: {e}")
        # Return empty dict as fallback
        return {}


def cognitive_gate(answers: dict[str, Any], flags: list[str]) -> bool:
    """Determine if cognitive criteria are met for memory care access.
    
    Memory care requires BOTH:
    1. Moderate/severe memory changes OR risky behaviors
    2. Formal diagnosis (cognitive_dx_confirm == "dx_yes")
    
    This is a HARD gate - without it, MC/MC-HA are blocked.
    
    Args:
        answers: User responses from GCP module
        flags: Flags set by assessment
    
    Returns:
        True if memory care access should be allowed
    """
    # CRITICAL: Check for formal diagnosis FIRST
    dx_confirm = (answers.get("cognitive_dx_confirm") or "").lower()
    
    # Diagnostic logging
    mem = (answers.get("memory_changes") or "").lower()
    behaviors = answers.get("behaviors") or []
    print(f"[COGNITIVE_GATE] dx_confirm='{dx_confirm}' memory={mem} behaviors={len(behaviors)}")
    
    if dx_confirm != "dx_yes":
        # No formal diagnosis = MC not allowed
        print(f"[COGNITIVE_GATE] FAILED - no formal diagnosis (dx_confirm={dx_confirm})")
        return False
    
    # Check memory_changes level
    if mem in ("moderate", "severe"):
        print(f"[COGNITIVE_GATE] PASSED - {mem} memory changes + diagnosis")
        return True

    # Check for risky behaviors
    risky_behav = set(b.lower() for b in behaviors)
    if len(risky_behav & COGNITIVE_HIGH_RISK) > 0:
        print(f"[COGNITIVE_GATE] PASSED - risky behaviors + diagnosis")
        return True

    # Check for cognitive risk flags
    flags_lower = set(f.lower() for f in (flags or []))
    if len(flags_lower & COGNITIVE_HIGH_RISK) > 0:
        print(f"[COGNITIVE_GATE] PASSED - cognitive risk flags + diagnosis")
        return True

    print(f"[COGNITIVE_GATE] FAILED - no cognitive symptoms despite diagnosis")
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

    behaviors = set(answers.get("behaviors") or [])
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

    # Canonical BADL mapping to deduplicate UI variations
    CANON_BADLS = {
        "Bathing/Showering": "bathing",
        "Bathing": "bathing",
        "Showering": "bathing",
        "Dressing": "dressing",
        "Toileting": "toileting",
        "Transferring": "transferring",
        "Eating": "feeding",
        "Feeding": "feeding",
        "Mobility": "mobility",
        "Personal Hygiene": "hygiene",
        "Hygiene": "hygiene",
    }

    # Count BADLs (deduplicated)
    badls = answers.get("badls", [])
    if not isinstance(badls, list):
        badls = []

    # Deduplicate using canonical mapping
    badls_unique = {CANON_BADLS.get(x, x.lower()) for x in badls}
    badls_count = len(badls_unique)

    print(f"[GUARD_INPUT] badls_raw={badls} badls_unique={badls_unique} badls_count={badls_count}")

    # Count IADLs
    iadls = answers.get("iadls", [])
    if not isinstance(iadls, list):
        iadls = []
    iadls_count = len(iadls)

    print(f"[GUARD_INPUT] iadls_count={iadls_count}")

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

    # Clear legacy support keys to prevent stale values from previous runs
    import streamlit as st
    legacy_keys = ["support", "support_bucket", "supervision_bucket"]
    for key in legacy_keys:
        st.session_state.pop(key, None)

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

    # Derive cognition band for tier mapping
    cog_band = cognition_band(answers, flags)

    # Derive supervision bucket (LEGACY DIAGNOSTIC - not used for routing)
    # This 24h bucket is diagnostic only and should NOT influence tier selection
    supervision_bucket_legacy = support_band(answers, flags)
    print(f"[LEGACY_SUP] bucket={supervision_bucket_legacy} cog={cog_band} (diagnostic only, not used for routing)")

    # For tier_map lookup, we use a routing-safe support band (without 24h)
    # Map 24h → high for routing purposes only
    sup_band_for_routing = "high" if supervision_bucket_legacy == "24h" else supervision_bucket_legacy

    # Load tier map and compute base recommendation using routing-safe band
    tier_map = _load_tier_map()
    tier_from_mapping = None

    if tier_map and cog_band in tier_map and sup_band_for_routing in tier_map.get(cog_band, {}):
        tier_from_mapping = tier_map[cog_band][sup_band_for_routing]

    # Build allowed tiers set
    from ai.gcp_schemas import CANONICAL_TIERS
    allowed_tiers = set(CANONICAL_TIERS)

    if not passes_cognitive_gate:
        # Block memory care tiers
        allowed_tiers -= {"memory_care", "memory_care_high_acuity"}
        print(f"[GCP_GUARD] Cognitive gate FAILED (cog={cog_band} sup={sup_band_for_routing}) - MC/MC-HA blocked")
        
        # CRITICAL: Set interim advice flag if tier mapping would have selected MC
        # This ensures the interim banner shows even though MC is blocked
        if tier_from_mapping in ("memory_care", "memory_care_high_acuity"):
            import streamlit as st
            st.session_state["_show_mc_interim_advice"] = True
            print(f"[GCP_INTERIM] Would-be tier={tier_from_mapping} blocked by no DX → setting interim AL flag")
    else:
        print(f"[GCP_GUARD] Cognitive gate PASSED (cog={cog_band} sup={sup_band_for_routing}) - all tiers allowed")

    # --- Behavior gate for moderate × high without risky behaviors ---
    gate_on = mc_behavior_gate_enabled()
    risky = cognitive_gate_behaviors_only(answers, flags)  # True iff any of COGNITIVE_HIGH_RISK present
    print(f"[GCP_FLAG] MC_BEHAVIOR_GATE={gate_on} cog={cog_band} sup={sup_band_for_routing} risky={risky} allowed_pre={sorted(list(allowed_tiers))}")

    if gate_on and cog_band == "moderate" and sup_band_for_routing == "high" and not risky:
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
                generate_hours_nudge_text,
                under_selected,
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

            # Persist hours bands to GCP state for Cost Planner
            try:
                import streamlit as st
                gcp_state = st.session_state.setdefault("gcp", {})
                gcp_state["hours_user_band"] = user_band or "1-3h"
                gcp_state["hours_llm"] = suggested or baseline
                gcp_state["hours_band"] = suggested or baseline  # legacy key
                print(f"[GCP_HOURS_PERSIST] user={gcp_state['hours_user_band']} llm={gcp_state['hours_llm']}")
            except Exception as persist_err:
                print(f"[GCP_HOURS_PERSIST_ERROR] {persist_err}")

            # Store suggestion in session state
            try:
                import streamlit as st
                sugg = {
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
                # Compute under-selected and nudge key strictly by band order
                ORDER = ["<1h", "1-3h", "4-8h", "24h"]
                def _band_index(b):
                    try:
                        return ORDER.index(b)
                    except Exception:
                        return -1

                user_band_cur = user_band
                suggested_band_cur = suggested
                under_selected_flag = (
                    (user_band_cur in ORDER)
                    and (suggested_band_cur in ORDER)
                    and (_band_index(user_band_cur) < _band_index(suggested_band_cur))
                )

                # store on the suggestion dict too for UI use
                sugg["user"] = user_band_cur
                sugg["under_selected"] = bool(under_selected_flag)

                # Persist suggestion first
                st.session_state["_hours_suggestion"] = sugg

                # nudge-key changes only when the (user,suggested) pair changes
                key = f"{user_band_cur or '-'}->{suggested_band_cur or '-'}"
                prev = st.session_state.get("_hours_nudge_key")
                st.session_state["_hours_nudge_new"] = bool(under_selected_flag and key != prev)
                st.session_state["_hours_nudge_key"] = key
                print(
                    f"[HOURS_NUDGE] key={key} under={under_selected_flag} new={st.session_state['_hours_nudge_new']}"
                )
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
            print(f"[GCP_HOURS_FALLBACK] {e}")
            # Graceful degradation: persist user band and provide safe default
            try:
                import streamlit as st

                # Try to get user's current selection
                raw_hours = answers.get("hours_per_day")
                valid_bands = {"<1h", "1-3h", "4-8h", "24h"}
                user_band = raw_hours if raw_hours in valid_bands else "1-3h"

                # Determine if high cognition + high support (conservative default)
                cog_level = answers.get("cognition", {}).get("level", "none")
                is_high_cog = cog_level in {"moderate", "advanced"}

                badls_raw = answers.get("badls", [])
                iadls_raw = answers.get("iadls", [])
                is_high_support = len(badls_raw) >= 3 or len(iadls_raw) >= 4

                # Provide conservative LLM band when in doubt
                if is_high_cog and is_high_support:
                    llm_band = "4-8h"
                else:
                    llm_band = user_band  # match user if unsure

                gcp_state = st.session_state.setdefault("gcp", {})
                gcp_state["hours_user_band"] = user_band
                gcp_state["hours_llm"] = llm_band
                gcp_state["hours_band"] = llm_band  # legacy key

                print(f"[GCP_HOURS_PERSIST] user={user_band} llm={llm_band} (fallback)")
            except Exception as fallback_err:
                print(f"[GCP_HOURS_PERSIST_ERROR] fallback failed: {fallback_err}")

    # Choose final deterministic tier
    # Priority: mapping (if available and in allowed) > score-based (if in allowed) > fallback to best permitted
    chosen = None

    if tier_from_mapping and tier_from_mapping in allowed_tiers:
        chosen = tier_from_mapping
        print(f"[GCP_GUARD] Using tier_map result: {chosen} (mapping: {cog_band}×{sup_band_for_routing})")
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

    # NOTE: Hours clearing moved to ensure_summary_ready AFTER adjudication
    # This ensures we use the published tier (not deterministic) and check compare mode

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
            # POLICY-MEDIATED LLM RECOMMENDATION
            # Replace raw LLM call with policy-aware mediator that applies guardrails
            import uuid

            from ai.llm_mediator import get_mediated_recommendation

            # Generate correlation ID for tracing policy decisions
            correlation_id = str(uuid.uuid4())[:12]

            # Convert flags list to dict format for mediator
            flags_dict = {}
            flag_list = flags or []
            for flag in flag_list:
                flags_dict[flag] = True

            # Add derived flags from answers for mediator context
            if answers.get("age_range"):
                flags_dict["age_range"] = answers["age_range"]
            if answers.get("preference"):
                flags_dict["preference"] = answers["preference"]

            # JSON-safe helper for serializing context (preserved for logging)
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

            # Get policy-mediated recommendation
            print(f"[GCP_MEDIATOR] Calling policy-aware LLM mediator for tier={tier}")
            try:
                policy_decision = get_mediated_recommendation(
                    base_tier=tier,
                    flags=flags_dict,
                    answers=answers,
                    correlation_id=correlation_id
                )

                # Convert PolicyDecision to advice-like object for existing UI compatibility
                if policy_decision:
                    # Create advice object that matches existing interface
                    class PolicyAdvice:
                        def __init__(self, decision):
                            self.tier = decision.chosen_tier
                            self.confidence = decision.confidence
                            self.empathy_score = decision.empathy_score
                            self.navi_messages = [decision.rationale] if decision.rationale else []
                            self.reasons = decision.advisory_notes or []

                    advice = PolicyAdvice(policy_decision)
                    ok = True

                    # NOTE: reconcile_with_deterministic moved to ensure_summary_ready AFTER adjudication
                    # This ensures adjudication_decision is set before logging reads it

                    # Store advice for UI rendering (assist mode only)
                    llm_advice = advice

                    # Enhanced logging with policy context
                    print(
                        f"[GCP_POLICY_FINAL] det={tier} policy={advice.tier} "
                        f"conf={advice.confidence:.2f} empathy={policy_decision.empathy_score} "
                        f"source={policy_decision.source} clamp={policy_decision.clamp_applied} "
                        f"allowed={','.join(policy_decision.allowed_tiers)} id={correlation_id}"
                    )
                else:
                    print(f"[GCP_POLICY_{llm_mode.upper()}] ok=False (policy decision failed)")
                    ok = False

            except Exception as e:
                print(f"[GCP_POLICY_ERROR] type={e.__class__.__name__} msg={str(e)}")
                ok = False
                llm_advice = None  # Clear advice on error to ensure clean fallback

    except Exception as e:
        # Silent failure - LLM must not affect deterministic flow
        print(f"[GCP_LLM_ERROR] type={e.__class__.__name__} msg={str(e)}")
        llm_advice = None  # Ensure llm_advice is None on outer exception
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

    # ====================================================================
    # LLM SUMMARY GENERATION (deprecated here): moved to ensure_summary_ready()
    # ====================================================================

    outcome = {
        "tier": tier,
        "tier_score": round(total_score, 1),
        "tier_rankings": tier_rankings,
        "confidence": round(confidence, 2),
        "flags": flags,
        "rationale": rationale,
        "suggested_next_product": suggested_next,
        "derived": derived,
        "allowed_tiers": sorted(list(allowed_tiers)),  # Persist for Cost Planner
    }

    print(f"[DERIVE_OUTCOME] tier={tier} allowed={sorted(list(allowed_tiers))} confidence={round(confidence, 2)}")

    return outcome


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
