"""
Cost Planner v2 - Quick Estimate (Tabbed Comparison)

Clean tabbed comparison view with:
- Navi blurbs (context-aware per tab)
- Back to Intro navigation
- Interactive tabs (In-Home, AL, MC)
- Exactly one card per tab
- Choose Your Path Forward radios
- Bottom CTAs
"""

import hashlib
import json
import time

import streamlit as st

from core import user_persist
from core.mcip import MCIP
from core.nav import route_to
from core.navi import render_navi_panel
from core.perf import perf
from core.user_persist import get_current_user_id, persist_costplan


# ==============================================================================
# WRITE-BEHIND FOR COSTPLAN (DEBOUNCED, DEDUPED)
# ==============================================================================

def _payload_hash(d: dict) -> str:
    """Generate SHA1 hash of payload for deduplication."""
    return hashlib.sha1(json.dumps(d, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def persist_costplan_debounced(payload: dict, delay_ms: int = 600) -> None:
    """Debounce and deduplicate costplan writes.
    
    Args:
        payload: Costplan data to persist
        delay_ms: Milliseconds to wait before flushing (default: 600)
    """
    ss = st.session_state
    h = _payload_hash(payload)
    if ss.get("_costplan_last_hash") == h:
        return  # unchanged
    ss["_costplan_last_hash"] = h
    ss["_costplan_pending"] = payload
    ss["_costplan_due_ts"] = time.time() + (delay_ms / 1000.0)


def flush_costplan_if_due(force: bool = False) -> None:
    """Flush pending costplan write if due or forced.
    
    Args:
        force: If True, flush immediately regardless of timeout
    """
    ss = st.session_state
    due = time.time() >= ss.get("_costplan_due_ts", 0)
    if ("_costplan_pending" in ss) and (force or due):
        with perf("write.flush"):
            user_persist.persist_costplan(ss.get("anonymous_uid"), ss["_costplan_pending"])
        ss.pop("_costplan_pending", None)
        ss.pop("_costplan_due_ts", None)


def _maybe_cleanup_files(force: bool = False):
    """Throttled cleanup - only run on route changes or every 60s.
    
    Prevents per-rerun cleanup spam while ensuring orphans are removed periodically.
    
    Args:
        force: If True, run cleanup immediately regardless of timeout
    """
    ss = st.session_state
    now = time.time()
    last_cleanup = ss.get("_last_cleanup_ts", 0)
    
    if force or (now - last_cleanup >= 60):
        print("[CLEANUP] running...")
        # Placeholder for future cleanup logic
        # Example: cleanup_orphans() from utils when available
        ss["_last_cleanup_ts"] = now


# ==============================================================================
# PER-SIGNATURE COMPUTE CACHE
# ==============================================================================

def _sig(prefix: str, obj: dict) -> str:
    """Generate cache key from prefix + object signature."""
    h = hashlib.sha1(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return f"cp_cache::{prefix}::{h}"


def compute_cached(prefix: str, signature: dict, fn, *args, **kwargs):
    """Cache expensive computation by input signature.
    
    Args:
        prefix: Cache namespace (e.g., "totals", "compose")
        signature: Dictionary of inputs that determine output
        fn: Function to call if cache miss
        *args, **kwargs: Arguments to pass to fn
        
    Returns:
        Cached or freshly computed result
    """
    ss = st.session_state
    key = _sig(prefix, signature)
    if key in ss:
        return ss[key]
    with perf(f"{prefix}"):
        out = fn(*args, **kwargs)
    ss[key] = out
    return out


def set_selected_assessment_once(new_sel: str):
    """Set selected assessment without triggering redundant tab switches.
    
    Single source of truth for tab selection. Tracks timestamp to identify
    most recent user intent and prevent bounce/flicker.
    
    Args:
        new_sel: New assessment key ("home", "al", "mc")
    """
    ss = st.session_state
    cost = ss.setdefault("cost", {})
    
    # Only update if different from current selection
    if new_sel and new_sel != cost.get("selected_assessment"):
        cost["selected_assessment"] = new_sel
        ss["_cp_tab_ts"] = time.time()  # Mark most recent user intent
        ss["_cp_tab_changed"] = True
        print(f"[CP_TAB] switched to {new_sel} at {ss['_cp_tab_ts']:.3f}")

# ==============================================================================
# HELPER: User Persistence
# ==============================================================================

def _eager_compute_totals(assessment: str, zip_code: str) -> float:
    """Eagerly compute monthly total for an assessment (for pre-warming).
    
    Computes the total and caches it via totals_set() so it's available
    before the card renders.
    
    Args:
        assessment: Assessment key ("home", "al", "mc")
        zip_code: ZIP code for regional pricing
        
    Returns:
        Monthly total (float)
    """
    from products.concierge_hub.cost_planner_v2.comparison_calcs import (
        calculate_facility_scenario,
        calculate_inhome_scenario,
    )
    from products.concierge_hub.cost_planner_v2.ui_helpers import totals_set
    
    ss = st.session_state
    
    if assessment == "home":
        breakdown = calculate_inhome_scenario(
            zip_code=zip_code,
            hours_per_day=ss.get("comparison_hours_per_day", 8),
            home_carry_override=ss.get("comparison_home_carry_cost", 0) or None
        )
    elif assessment == "al":
        breakdown = calculate_facility_scenario(
            care_type="assisted_living",
            zip_code=zip_code,
            keep_home=ss.get("comparison_keep_home", False),
            home_carry_override=ss.get("comparison_home_carry_cost", 0) or None
        )
    elif assessment == "mc":
        breakdown = calculate_facility_scenario(
            care_type="memory_care",
            zip_code=zip_code,
            keep_home=ss.get("comparison_keep_home", False),
            home_carry_override=ss.get("comparison_home_carry_cost", 0) or None
        )
    else:
        return 0.0
    
    monthly_total = breakdown.monthly_total
    totals_set(assessment, monthly_total)
    return monthly_total


def _snapshot_costplan(event: str):
    """Persist CostPlan snapshot to disk (debounced, deduped).
    
    Args:
        event: Event name (qe_mount, tab_change, path_change, etc.)
    """
    try:
        cost = st.session_state.get("cost", {})
        g = st.session_state.get("gcp", {})

        snap = {
            "event": event,
            "corr_id": st.session_state.get("corr_id", "unknown"),
            "zip": cost.get("inputs", {}).get("zip"),
            "region": cost.get("region_label"),
            "selected_assessment": cost.get("selected_assessment"),
            "chosen_path": cost.get("path_choice"),
            "home_hours": cost.get("home_hours_scalar"),
            "home_carry": cost.get("inputs", {}).get("home_carry"),
            "keep_home": cost.get("keep_home"),
            "totals_cache": cost.get("totals_cache"),
            "gcp_summary": {
                "published_tier": g.get("published_tier"),
                "allowed_tiers": g.get("allowed_tiers"),
                "hours_user_band": g.get("hours_user_band"),
                "hours_llm_band": g.get("hours_llm"),
            },
        }

        with perf("persist.debounce"):
            persist_costplan_debounced(snap)

    except Exception as e:
        print(f"[USER_PERSIST_ERR] _snapshot_costplan({event}) failed: {e}")


# ==============================================================================
# HELPER: Get GCP Hours
# ==============================================================================

def _get_gcp_hours_per_day() -> float:
    """Get hours per day from GCP recommendation, with categorical mapping.
    
    GCP provides categorical answers which map to numeric hours:
    - "Less than 1 hour" → 1.0
    - "1–3 hours" → 2.0
    - "4–8 hours" → 8.0 (or 6.0 if user explicitly chose mid-range)
    - "24-hour support" → 24.0
    
    Returns:
        Float hours per day (default: 2.0 if not found - safer than 1.0)
    """
    # First try new GCP state structure (preferred)
    gcp = st.session_state.get("gcp", {})
    user_band = gcp.get("hours_user_band")

    if user_band:
        # Map band to numeric value (use mid-range for ranges)
        band_map = {
            "<1h": 1.0,
            "1-3h": 2.0,
            "4-8h": 6.0,  # mid-range unless user explicitly chose 8
            "24h": 24.0,
        }
        mapped = band_map.get(user_band)
        if mapped:
            print(f"[QE_INIT] Using hours from gcp.hours_user_band: {user_band} → {mapped}")
            return mapped

    # Fall back to legacy gcp_care_recommendation structure
    gcp_data = st.session_state.get("gcp_care_recommendation", {})
    hours_category = gcp_data.get("hours_per_day", "")

    # Mapping dictionary (handles various formats)
    hours_map = {
        # Standard formats
        "less than 1 hour": 1.0,
        "<1h": 1.0,
        "1-3h": 2.0,
        "1–3 hours": 2.0,
        "4-8h": 6.0,  # use mid-range
        "4–8 hours": 6.0,
        "24h": 24.0,
        "24-hour support": 24.0,
        # Additional variations
        "less_than_1": 1.0,
        "1_to_3": 2.0,
        "4_to_8": 6.0,
        "24_hour": 24.0,
    }

    # Normalize and lookup
    hours_normalized = str(hours_category).lower().strip()
    mapped_hours = hours_map.get(hours_normalized, 2.0)  # default to 2.0, not 1.0 or 8.0

    return mapped_hours


# ==============================================================================
# CTA VALIDATION & SNAPSHOT
# ==============================================================================

def _validate_qe_ready(cost: dict) -> tuple[bool, str | None]:
    """Validate if QE has minimum required inputs for PFMA handoff.
    
    Args:
        cost: Cost session state dict
        
    Returns:
        (is_valid, error_message) tuple
    """
    # Require a chosen path and ZIP at minimum
    # Check both path_choice (old) and selected_assessment (new)
    path = cost.get("path_choice") or cost.get("selected_assessment")
    zip_code = cost.get("inputs", {}).get("zip")

    if not path:
        return False, "Choose a care path above to continue."
    if not zip_code:
        return False, "Enter your ZIP code to localize costs."

    return True, None


def _snapshot_for_pfma(event: str = "qe_pay_cta"):
    """Persist comprehensive CostPlan snapshot for PFMA handoff.
    
    Args:
        event: Event name for logging
    """
    cost = st.session_state.get("cost", {})
    g = st.session_state.get("gcp", {})

    snap = {
        "event": event,
        "corr_id": st.session_state.get("corr_id"),
        "zip": cost.get("inputs", {}).get("zip"),
        "region": cost.get("region_label"),
        "selected_assessment": cost.get("selected_assessment"),
        "chosen_path": cost.get("path_choice"),
        "home_hours": cost.get("home_hours_scalar"),
        "home_carry": cost.get("inputs", {}).get("home_carry"),
        "keep_home": cost.get("keep_home"),
        "totals_cache": cost.get("totals_cache"),
        "segments_cache": cost.get("segments_cache"),
        "gcp": {
            "published_tier": g.get("published_tier"),
            "allowed_tiers": g.get("allowed_tiers"),
            "hours_user_band": g.get("hours_user_band"),
            "hours_llm_band": g.get("hours_llm"),
        },
    }

    # Debounce write instead of immediate persist - will flush on route
    with perf("persist.debounce"):
        persist_costplan_debounced(snap, delay_ms=600)
    print(f"[CTA_PAY] debounced costplan snapshot event={event}")


# ==============================================================================
# NAVI BLURBS (Tab-Specific)
# ==============================================================================

NAVI_BLURBS = {
    "home": "Adjust daily hours and home expense to see in-home costs.",
    "al": "Adjust facility costs or home carry costs to explore different scenarios.",
    "mc": "Adjust facility costs or home carry costs to explore different scenarios."
}


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def render():
    """Render Quick Estimate tabbed comparison view."""

    print("[PAGE_MOUNT] cost_quick_estimate")
    
    # Assert navigation consistency (verify interim flag matches published tier)
    from core.modules.engine import assert_nav_consistency
    assert_nav_consistency(st.session_state, where="CP")

    # Get ZIP from session state
    zip_code = st.session_state.get("cost.inputs", {}).get("zip") or st.session_state.get("cost_v2_quick_zip")
    has_zip = bool(zip_code and len(str(zip_code)) == 5)

    # ---- READ FINALS FROM SESSION OR MCIP ----
    # Single source of truth for active tab
    cost = st.session_state.setdefault("cost", {})

    # Get GCP recommendation from session state (persisted by GCP Results)
    g = st.session_state.get("gcp", {})
    rec = g.get("published_tier") or g.get("recommended_tier")
    alwd = g.get("allowed_tiers")

    # Fallback to MCIP persisted contract if session is empty/missing
    if not rec or not alwd:
        mc_rec = MCIP.get_care_recommendation()
        if mc_rec:
            if not rec:
                rec = mc_rec.tier
                # Normalize tier name for consistency
                if rec == "in_home":
                    rec = "in_home_care"
            if not alwd:
                # Read allowed_tiers from MCIP contract (v2 schema)
                alwd = getattr(mc_rec, "allowed_tiers", None) or []

    # Ensure alwd is a list (default empty if still None)
    alwd = alwd or []

    # Debug: Log full state before computing availability
    print(f"[QE_DEBUG] GCP session state: gcp.published_tier={g.get('published_tier')} gcp.recommended_tier={g.get('recommended_tier')} gcp.allowed_tiers={g.get('allowed_tiers')}")

    # Compute availability: MC shows if in allowed OR if recommended
    mc_in_allowed = "memory_care" in alwd or "memory_care_high_acuity" in alwd
    mc_is_recommended = rec in ("memory_care", "memory_care_high_acuity")

    avail = {
        "home": True,
        "al": True,
        "mc": mc_in_allowed or mc_is_recommended
    }
    cost["assessments_available"] = avail

    # Enhanced debug output
    print(f"[QE_DEBUG] MC Tab Logic: mc_in_allowed={mc_in_allowed} (allowed={alwd}), mc_is_recommended={mc_is_recommended} (recommended={rec}), FINAL mc={avail['mc']}")

    # Default selected tab (use final tier from canonical helper for post-adjudication logic)
    from core.modules.engine import get_final_recommendation_tier
    
    final_tier = get_final_recommendation_tier(st.session_state)
    interim = bool(st.session_state.get("_show_mc_interim_advice", False))
    
    sel = cost.get("selected_assessment")
    
    # Only preset selection on first mount OR if current selection is invalid
    # DO NOT overwrite user's explicit tab choice on subsequent renders
    need_preset = (sel not in ("home", "al", "mc")) or not avail.get(sel, False)
    
    if need_preset:
        # No valid selection yet OR current selection not available
        if interim:
            # Interim AL case (MC clamped due to no DX)
            cost["selected_assessment"] = "al"
            print(f"[QE_PRESET] Interim AL selected (MC without DX)")
        elif avail["mc"] and final_tier in ("memory_care", "memory_care_high_acuity"):
            cost["selected_assessment"] = "mc"
            print(f"[QE_PRESET] MC selected (final_tier={final_tier})")
        elif final_tier == "assisted_living":
            cost["selected_assessment"] = "al"
            print(f"[QE_PRESET] AL selected (final_tier={final_tier})")
        else:
            cost["selected_assessment"] = "home"
            print(f"[QE_PRESET] Home selected (final_tier={final_tier})")
    else:
        # Valid selection exists and is available - respect it (single source of truth)
        print(f"[QE_RETAIN] Keeping user selection: {sel}")

    # Log availability with full context
    print(f"[QE_AVAIL] recommended={rec} final_tier={final_tier} interim={interim} allowed={alwd} avail={avail} sel={cost['selected_assessment']}")
    print(f"[QE] selected_assessment={cost['selected_assessment']}")

    # Persist initial state snapshot (after availability/selection computed)
    _snapshot_costplan("qe_mount")

    # Initialize session state for calculations
    if "comparison_selected_plan" not in st.session_state:
        st.session_state.comparison_selected_plan = None
    if "comparison_facility_breakdown" not in st.session_state:
        st.session_state.comparison_facility_breakdown = None
    if "comparison_inhome_breakdown" not in st.session_state:
        st.session_state.comparison_inhome_breakdown = None
    if "comparison_home_carry_cost" not in st.session_state:
        st.session_state.comparison_home_carry_cost = 0.0
    if "comparison_keep_home" not in st.session_state:
        st.session_state.comparison_keep_home = False

    # Initialize hours from GCP (only on first load)
    if "comparison_inhome_hours" not in st.session_state:
        gcp_hours = _get_gcp_hours_per_day()
        st.session_state.comparison_inhome_hours = gcp_hours
        st.session_state.comparison_hours_gcp_source = gcp_hours  # Track original GCP value

        # Log initialization with user band and LLM band
        gcp = st.session_state.get("gcp", {})
        user_band = gcp.get("hours_user_band", "unknown")
        llm_band = gcp.get("hours_llm", "unknown")
        print(f"[QE_INIT] home_hours={gcp_hours} user_band={user_band}")

        # Log LLM band parsing
        from products.concierge_hub.cost_planner_v2.ui_helpers import parse_hours_band_to_high_end
        if llm_band != "unknown":
            llm_high = parse_hours_band_to_high_end(llm_band)
            print(f"[QE_LLM] band={llm_band} → high={llm_high}")
    if "comparison_hours_per_day" not in st.session_state:
        st.session_state.comparison_hours_per_day = st.session_state.comparison_inhome_hours

    # Open centered container
    st.markdown("<div class='sn-container'>", unsafe_allow_html=True)

    # Render Navi panel (always at top)
    render_navi_panel(location="product", product_key="cost_planner")

    st.markdown("")

    # ZIP warning if missing
    if not has_zip:
        st.warning("⚠️ **ZIP code required:** Return to the previous page to enter your ZIP code.")
        st.markdown("")

    # Pre-warm ALL visible tabs BEFORE rendering strip to avoid flicker
    # Force-compute totals for every available tab so first render is complete
    selected = cost.get("selected_assessment")
    visible_tabs = [k for k, ok in avail.items() if ok]
    
    # Eager compute all visible tabs (selected first for priority)
    priority_order = [selected] + [k for k in visible_tabs if k != selected]
    for key in priority_order:
        _ = _eager_compute_totals(key, zip_code or "00000")
    
    # Now totals_cache is fully populated before rendering strip
    print(f"[QE_PREWARM] computed all visible tabs={visible_tabs} cache={cost.get('totals_cache', {})}")

    # C) Compact cost tabs (horizontal with costs under labels)
    _render_compact_cost_tabs()

    # D) Panels - exactly one card per panel
    st.markdown("<div class='cp-panels'>", unsafe_allow_html=True)

    if avail.get("home"):
        _render_panel("home", lambda: _render_home_card(zip_code or "00000"))

    if avail.get("al"):
        _render_panel("al", lambda: _render_facility_card("assisted_living", zip_code or "00000", show_keep_home=True))

    if avail.get("mc"):
        _render_panel("mc", lambda: _render_facility_card("memory_care", zip_code or "00000", show_keep_home=True))

    st.markdown("</div>", unsafe_allow_html=True)

    # E) Choose Your Path Forward (link-cards)
    st.markdown("---")
    cp_render_path_forward()

    # F) Bottom CTAs
    _render_bottom_ctas()

    # Close container
    st.markdown("</div>", unsafe_allow_html=True)

    # Debounced write flush (idle flush)
    flush_costplan_if_due(force=False)
    
    # Reset tab changed flag after render
    st.session_state.pop("_cp_tab_changed", None)


# ==============================================================================
# TAB RENDERING
# ==============================================================================

def _render_compact_cost_tabs():
    """Render compact horizontal cost tabs with costs under labels."""
    from products.concierge_hub.cost_planner_v2.ui_helpers import format_currency, get_cached_monthly_total

    cost = st.session_state.get("cost", {})
    available = cost.get("assessments_available", {"home": True, "al": True, "mc": False})
    sel = cost.get("selected_assessment", "home")

    # Diagnostic print
    print(f"[COMPACT_TABS] render strip sel={sel} totals={cost.get('totals_cache', {})}")

    # Get visible tabs in order
    order = [k for k in ("home", "al", "mc") if available.get(k)]

    if not order:
        return

    label_map = {"home": "In-Home Care", "al": "Assisted Living", "mc": "Memory Care"}

    # Render tab container
    st.markdown('<div class="cp-cost-tabs" role="tablist" aria-label="Cost options">', unsafe_allow_html=True)

    # Build columns for clickable tabs
    tab_cols = st.columns(len(order))

    for idx, assessment in enumerate(order):
        with tab_cols[idx]:
            total = get_cached_monthly_total(assessment)
            total_str = format_currency(total) if total else "—"
            is_active = (assessment == sel)
            label = label_map[assessment]

            # Render tab as button with label + cost
            button_label = f"{label}\n{total_str}"

            if st.button(
                button_label,
                key=f"cp_tab_{assessment}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                help=f"View {label} details"
            ):
                if not is_active:
                    set_selected_assessment_once(assessment)
                    _snapshot_costplan("tab_change")
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# PANEL RENDERING
# ==============================================================================

def _render_panel(assessment: str, render_card_fn):
    """Render a single panel with conditional visibility."""
    # Single source of truth: cost.selected_assessment
    active = (st.session_state["cost"]["selected_assessment"] == assessment)
    clz = "cp-panel is-active" if active else "cp-panel"

    st.markdown(f'<div class="{clz}" id="cp-panel-{assessment}" role="tabpanel">', unsafe_allow_html=True)
    if active:  # Only render content for active panel
        render_card_fn()
    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# CARD RENDERING
# ==============================================================================

def _render_home_card(zip_code: str):
    """Render In-Home Care card (hours + home expense, no Keep Home toggle)."""
    from products.concierge_hub.cost_planner_v2.comparison_calcs import calculate_inhome_scenario
    from products.concierge_hub.cost_planner_v2.ui_helpers import (
        donut_cost_chart,
        money,
        render_care_chunk_compare_blurb,
        render_confirm_hours_if_needed,
        segcache_get,
        segcache_set,
        totals_set,
    )

    # Calculate scenario
    breakdown = calculate_inhome_scenario(
        zip_code=zip_code,
        hours_per_day=st.session_state.get("comparison_hours_per_day", 8),
        home_carry_override=st.session_state.get("comparison_home_carry_cost", 0) or None
    )
    st.session_state.comparison_inhome_breakdown = breakdown

    # Extract segments from breakdown (no recompute, reuse existing values)
    care_amt = 0.0
    home_carry_amt = 0.0
    for line in breakdown.lines:
        label_lower = line.label.lower()
        if "home carry" in label_lower:
            if line.applied:
                home_carry_amt += line.value
        else:
            if line.applied and line.value > 0:
                care_amt += line.value

    # Cache monthly total and segments
    monthly_total = breakdown.monthly_total
    totals_set("home", monthly_total)

    segments = {
        "Care Services": float(care_amt or 0),
        "Home Carry": float(home_carry_amt or 0),
    }
    segcache_set("home", {k: v for k, v in segments.items() if v > 0})

    print(f"[CARD] rendered home monthly={monthly_total:,.0f}")
    print(f"[COMPOSE] home segs={segcache_get('home')} total={monthly_total:,.0f}")

    # Card container
    st.markdown('<div class="cost-card">', unsafe_allow_html=True)

    # Header
    st.markdown('<div class="cost-card__title">In-Home Care</div>', unsafe_allow_html=True)
    st.markdown('<div class="cost-card__caption">Estimated monthly total</div>', unsafe_allow_html=True)

    # Totals display removed - now shown in donut center

    # Donut chart (replaces bar + shows total in center)
    donut_cost_chart(segments, total_label=money(monthly_total), emphasize="Care Services")

    # Care chunk comparison (when both cached)
    render_care_chunk_compare_blurb("home")

    # Hours confirmation advisory (shows if LLM hours != current)
    render_confirm_hours_if_needed(current_hours_key="qe_home_hours")

    # Controls: Hours slider
    st.markdown('<div class="cost-section__label">Daily Support Hours</div>', unsafe_allow_html=True)
    current_hours = st.session_state.comparison_inhome_hours
    hours = st.slider(
        "Hours per day",
        min_value=1.0,
        max_value=24.0,
        value=current_hours,
        step=1.0,
        key="qe_home_hours",
        help="Adjust based on care needs",
        label_visibility="collapsed"
    )

    # Mirror slider value to cost state for confirmation logic
    st.session_state.setdefault("cost", {})["home_hours_scalar"] = float(hours)
    st.markdown(f'<div class="cp-hint">{hours:.1f} h/day</div>', unsafe_allow_html=True)

    if hours != st.session_state.comparison_inhome_hours:
        st.session_state.comparison_inhome_hours = hours
        st.session_state.comparison_hours_per_day = hours
        st.rerun()

    st.markdown("")

    # Home Expense (always included for in-home)
    st.markdown('<div class="cost-section__label">🏠 Home Expense</div>', unsafe_allow_html=True)
    prefill_value = st.session_state.comparison_home_carry_cost

    home_carry = st.number_input(
        "Monthly home expense",
        min_value=0.0,
        value=prefill_value,
        step=100.0,
        help="Mortgage, rent, property tax, insurance, maintenance",
        key="qe_home_carry",
        label_visibility="visible"
    )

    if home_carry != st.session_state.comparison_home_carry_cost:
        st.session_state.comparison_home_carry_cost = home_carry
        st.rerun()

    st.markdown(f'<span class="cp-chip">✓ Included in total (${home_carry:,.0f}/mo)</span>', unsafe_allow_html=True)

    st.markdown("")
    st.caption("Actual costs vary by caregiver rates and location.")

    st.markdown('</div>', unsafe_allow_html=True)


def _render_facility_card(tier: str, zip_code: str, show_keep_home: bool = False):
    """Render facility card (AL or MC) with optional Keep Home toggle."""
    from products.concierge_hub.cost_planner_v2.comparison_calcs import calculate_facility_scenario
    from products.concierge_hub.cost_planner_v2.ui_helpers import (
        donut_cost_chart,
        money,
        render_care_chunk_compare_blurb,
        segcache_get,
        segcache_set,
        totals_set,
    )

    # Calculate scenario
    breakdown = calculate_facility_scenario(
        care_type=tier,
        zip_code=zip_code,
        keep_home=st.session_state.get("comparison_keep_home", False),
        home_carry_override=st.session_state.get("comparison_home_carry_cost", 0) or None
    )
    st.session_state.comparison_facility_breakdown = breakdown

    # Extract segments from breakdown (no recompute, reuse existing values)
    housing_amt = 0.0
    care_amt = 0.0
    home_carry_amt = 0.0

    for line in breakdown.lines:
        label_lower = line.label.lower()
        # Base cost + regional = housing/room
        if "base cost" in label_lower or "regional adjustment" in label_lower:
            if line.applied:
                housing_amt += line.value
        # Home carry is separate
        elif "home carry" in label_lower:
            if line.applied:
                home_carry_amt += line.value
        # Everything else is care services
        else:
            if line.applied and line.value > 0:
                care_amt += line.value

    # Cache monthly total and segments
    assessment_key = "mc" if tier == "memory_care" else "al"
    monthly_total = breakdown.monthly_total
    totals_set(assessment_key, monthly_total)

    segments = {
        "Housing/Room": float(housing_amt or 0),
        "Care Services": float(care_amt or 0),
    }
    if show_keep_home and st.session_state.get("comparison_keep_home", False):
        segments["Home Carry"] = float(home_carry_amt or 0)

    segcache_set(assessment_key, {k: v for k, v in segments.items() if v > 0})

    print(f"[CARD] rendered {assessment_key} monthly={monthly_total:,.0f}")
    print(f"[COMPOSE] {assessment_key} segs={segcache_get(assessment_key)} total={monthly_total:,.0f}")

    # Card container
    st.markdown('<div class="cost-card">', unsafe_allow_html=True)

    # Header
    display_name = "Assisted Living" if tier == "assisted_living" else "Memory Care"
    st.markdown(f'<div class="cost-card__title">{display_name}</div>', unsafe_allow_html=True)
    st.markdown('<div class="cost-card__caption">Estimated monthly total</div>', unsafe_allow_html=True)

    # Totals display removed - now shown in donut center

    # Donut chart (replaces bar + shows total in center)
    donut_cost_chart(segments, total_label=money(monthly_total), emphasize="Care Services")

    # Care chunk comparison (when both cached)
    render_care_chunk_compare_blurb(assessment_key)

    # Keep Home toggle (only if show_keep_home=True)
    if show_keep_home:
        st.markdown('<div class="cost-section__label">🏠 Keep Home?</div>', unsafe_allow_html=True)

        keep_home = st.checkbox(
            "Keep Home (spouse/partner remains)",
            value=st.session_state.comparison_keep_home,
            key=f"qe_{tier}_keep_home",
            help="Check if you need to maintain your current home while in facility care"
        )

        if keep_home != st.session_state.comparison_keep_home:
            st.session_state.comparison_keep_home = keep_home
            st.rerun()

        if keep_home:
            prefill_value = st.session_state.comparison_home_carry_cost

            home_carry = st.number_input(
                "Monthly home expense",
                min_value=0.0,
                value=prefill_value,
                step=100.0,
                help="Mortgage, rent, property tax, insurance, maintenance",
                key=f"qe_{tier}_home_carry",
                label_visibility="visible"
            )

            if home_carry != st.session_state.comparison_home_carry_cost:
                st.session_state.comparison_home_carry_cost = home_carry
                st.rerun()

            st.markdown(f'<span class="cp-chip">✓ Added to total (${home_carry:,.0f}/mo)</span>', unsafe_allow_html=True)

        st.markdown("")

    st.caption("Costs vary by community and level of care.")

    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# PATH SELECTION
# ==============================================================================

def cp_render_path_forward():
    """Render Choose Your Path Forward section - clean header based on active tab."""
    # Get active assessment (selected tab)
    cost = st.session_state.get("cost", {})
    active_key = cost.get("selected_assessment", "home")
    
    # Map keys to display labels
    labels = {
        "home": "In-Home Care",
        "al": "Assisted Living",
        "mc": "Memory Care"
    }
    active_label = labels.get(active_key, active_key.title().replace("_", " "))
    
    # Dynamic heading based on active tab
    st.markdown(f"### Choose Your Path Forward: {active_label}")
    st.caption("The selected care type is based on your current tab. Change tabs above to compare paths.")


# ==============================================================================
# BOTTOM CTAs
# ==============================================================================

def _render_bottom_ctas():
    """Render bottom CTA row."""
    st.markdown("")

    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button(
            "Help Me Figure Out How to Pay for This ▶",
            type="primary",
            use_container_width=True,
            key="qe_continue"
        ):
            # Ensure path_choice is set from selected_assessment
            cost = st.session_state.setdefault("cost", {})
            selected = cost.get("selected_assessment")
            if selected:
                # Map assessment to path_choice for PFMA compatibility
                path_map = {"home": "in_home_care", "al": "assisted_living", "mc": "memory_care"}
                cost["path_choice"] = path_map.get(selected, selected)

            # Validate QE is ready for PFMA handoff
            ok, err = _validate_qe_ready(cost)

            if not ok:
                # Store error in cost state to display inline
                st.session_state["cost"]["cta_error"] = err
                print(f"[CTA_PAY] blocked: {err}")
                st.rerun()
            else:
                # Persist CostPlan snapshot for PFMA
                _snapshot_for_pfma()

                # Navigate to Cost Planner v2 triage step
                print(f"[CTA_PAY] → cost_v2 triage (path={cost['path_choice']})")
                st.session_state["_route_changed"] = True
                flush_costplan_if_due(force=True)
                _maybe_cleanup_files(force=True)
                st.session_state.cost_v2_step = "triage"
                st.query_params["page"] = "cost_v2"
                st.rerun()

    with col2:
        if st.button("← Back to Hub", use_container_width=True, key="qe_back_hub"):
            st.session_state["_route_changed"] = True
            flush_costplan_if_due(force=True)
            _maybe_cleanup_files(force=True)
            route_to("hub_concierge")

    # Display inline error if CTA validation failed
    err = st.session_state.get("cost", {}).pop("cta_error", None)
    if err:
        st.caption(f"⚠️ {err}")
