"""
Care Hours Calculator - Internal Testing Tool

Allows advisors to input care needs directly and test the hours calculation
without running full GCP workflow. Useful for rapid validation and tuning.

TODO: Remove this product by 2025-12-15 after validation phase complete.
"""

import json
import streamlit as st
from datetime import datetime
from pathlib import Path
from typing import Any

from ai.hours_engine import calculate_baseline_hours_weighted, generate_hours_advice
from ai.hours_schemas import HoursContext
from ai.hours_weights import (
    get_badl_hours,
    get_iadl_hours,
    get_cognitive_multiplier,
    get_fall_risk_multiplier,
    get_mobility_hours,
)
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple
from core.ui import render_navi_panel_v2


# Path to validation cases JSON
VALIDATION_CASES_PATH = Path(__file__).parent / "validation_cases.json"


def _load_validation_cases() -> list[dict[str, Any]]:
    """Load saved validation test cases.
    
    Returns:
        List of validation cases
    """
    if not VALIDATION_CASES_PATH.exists():
        return []
    
    try:
        with open(VALIDATION_CASES_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Failed to load validation cases: {e}")
        return []


def _save_validation_case(case: dict[str, Any]) -> None:
    """Save a validation test case to JSON.
    
    Args:
        case: Test case data with inputs, results, and optional notes
    """
    cases = _load_validation_cases()
    cases.append(case)
    
    try:
        with open(VALIDATION_CASES_PATH, "w") as f:
            json.dump(cases, f, indent=2)
        st.success("✅ Test case saved successfully!")
    except Exception as e:
        st.error(f"Failed to save test case: {e}")


def _render_input_form() -> None:
    """Render input form for care needs."""
    st.markdown("### 📋 Care Needs Input")
    
    # BADLs
    st.markdown("**Basic Activities of Daily Living (BADLs)**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.calc_bathing = st.checkbox("🚿 Bathing", value=st.session_state.get("calc_bathing", False))
        st.session_state.calc_toileting = st.checkbox("🚽 Toileting", value=st.session_state.get("calc_toileting", False))
    with col2:
        st.session_state.calc_dressing = st.checkbox("👔 Dressing", value=st.session_state.get("calc_dressing", False))
        st.session_state.calc_transferring = st.checkbox("🪑 Transferring", value=st.session_state.get("calc_transferring", False))
    with col3:
        st.session_state.calc_feeding = st.checkbox("🍽️ Feeding", value=st.session_state.get("calc_feeding", False))
        st.session_state.calc_hygiene = st.checkbox("🧼 Hygiene", value=st.session_state.get("calc_hygiene", False))
    
    st.markdown("---")
    
    # IADLs
    st.markdown("**Instrumental Activities of Daily Living (IADLs)**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.session_state.calc_medications = st.checkbox("💊 Medications", value=st.session_state.get("calc_medications", False))
        st.session_state.calc_meal_prep = st.checkbox("🍳 Meal Prep", value=st.session_state.get("calc_meal_prep", False))
    with col2:
        st.session_state.calc_housekeeping = st.checkbox("🧹 Housekeeping", value=st.session_state.get("calc_housekeeping", False))
        st.session_state.calc_laundry = st.checkbox("👕 Laundry", value=st.session_state.get("calc_laundry", False))
    with col3:
        st.session_state.calc_transportation = st.checkbox("🚗 Transportation", value=st.session_state.get("calc_transportation", False))
        st.session_state.calc_finances = st.checkbox("💰 Finances", value=st.session_state.get("calc_finances", False))
    with col4:
        st.session_state.calc_shopping = st.checkbox("🛒 Shopping", value=st.session_state.get("calc_shopping", False))
        st.session_state.calc_phone = st.checkbox("📞 Phone", value=st.session_state.get("calc_phone", False))
    
    st.markdown("---")
    
    # Cognitive & Behaviors
    st.markdown("**Cognitive Status & Behaviors**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.calc_cognitive_level = st.radio(
            "Cognitive Level",
            options=["none", "mild", "moderate", "severe", "advanced"],
            index=["none", "mild", "moderate", "severe", "advanced"].index(
                st.session_state.get("calc_cognitive_level", "none")
            ),
            horizontal=False
        )
    
    with col2:
        st.markdown("**Challenging Behaviors**")
        st.session_state.calc_wandering = st.checkbox("🚶 Wandering/Elopement", value=st.session_state.get("calc_wandering", False))
        st.session_state.calc_aggression = st.checkbox("😤 Aggression/Agitation", value=st.session_state.get("calc_aggression", False))
        st.session_state.calc_sundowning = st.checkbox("🌙 Sundowning", value=st.session_state.get("calc_sundowning", False))
        st.session_state.calc_repetitive_questions = st.checkbox("🔁 Repetitive Questions", value=st.session_state.get("calc_repetitive_questions", False))
    
    st.markdown("---")
    
    # Safety & Mobility
    st.markdown("**Safety & Mobility**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.session_state.calc_falls = st.radio(
            "Fall History",
            options=["none", "once", "multiple", "frequent"],
            index=["none", "once", "multiple", "frequent"].index(
                st.session_state.get("calc_falls", "none")
            ),
            horizontal=False
        )
    
    with col2:
        st.session_state.calc_mobility = st.selectbox(
            "Mobility Aid",
            options=["independent", "cane", "walker", "wheelchair", "bedbound"],
            index=["independent", "cane", "walker", "wheelchair", "bedbound"].index(
                st.session_state.get("calc_mobility", "independent")
            )
        )
    
    with col3:
        st.session_state.calc_overnight_needed = st.checkbox(
            "🌙 Overnight Care Needed",
            value=st.session_state.get("calc_overnight_needed", False)
        )
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧮 Calculate Hours", type="primary", use_container_width=True):
            _calculate_and_store()
    with col2:
        if st.button("🗑️ Clear Form", use_container_width=True):
            _clear_form()


def _clear_form() -> None:
    """Clear all form inputs."""
    # BADLs
    st.session_state.calc_bathing = False
    st.session_state.calc_toileting = False
    st.session_state.calc_dressing = False
    st.session_state.calc_transferring = False
    st.session_state.calc_feeding = False
    st.session_state.calc_hygiene = False
    
    # IADLs
    st.session_state.calc_medications = False
    st.session_state.calc_meal_prep = False
    st.session_state.calc_housekeeping = False
    st.session_state.calc_laundry = False
    st.session_state.calc_transportation = False
    st.session_state.calc_finances = False
    st.session_state.calc_shopping = False
    st.session_state.calc_phone = False
    
    # Cognitive & Behaviors
    st.session_state.calc_cognitive_level = "none"
    st.session_state.calc_wandering = False
    st.session_state.calc_aggression = False
    st.session_state.calc_sundowning = False
    st.session_state.calc_repetitive_questions = False
    
    # Safety & Mobility
    st.session_state.calc_falls = "none"
    st.session_state.calc_mobility = "independent"
    st.session_state.calc_overnight_needed = False
    
    # Clear results
    if "calc_results" in st.session_state:
        del st.session_state.calc_results
    
    st.rerun()


def _calculate_and_store() -> None:
    """Calculate hours using weighted baseline and LLM, store results."""
    # Build BADLs list
    badls = []
    if st.session_state.get("calc_bathing", False):
        badls.append("bathing")
    if st.session_state.get("calc_toileting", False):
        badls.append("toileting")
    if st.session_state.get("calc_dressing", False):
        badls.append("dressing")
    if st.session_state.get("calc_transferring", False):
        badls.append("transferring")
    if st.session_state.get("calc_feeding", False):
        badls.append("feeding")
    if st.session_state.get("calc_hygiene", False):
        badls.append("hygiene")
    
    # Build IADLs list
    iadls = []
    if st.session_state.get("calc_medications", False):
        iadls.append("medication_management")
    if st.session_state.get("calc_meal_prep", False):
        iadls.append("meal_preparation")
    if st.session_state.get("calc_housekeeping", False):
        iadls.append("housekeeping")
    if st.session_state.get("calc_laundry", False):
        iadls.append("laundry")
    if st.session_state.get("calc_transportation", False):
        iadls.append("transportation")
    if st.session_state.get("calc_finances", False):
        iadls.append("financial_management")
    if st.session_state.get("calc_shopping", False):
        iadls.append("shopping")
    if st.session_state.get("calc_phone", False):
        iadls.append("phone_use")
    
    # Get values
    cognitive_level = st.session_state.get("calc_cognitive_level", "none")
    wandering = st.session_state.get("calc_wandering", False)
    aggression = st.session_state.get("calc_aggression", False)
    sundowning = st.session_state.get("calc_sundowning", False)
    repetitive_questions = st.session_state.get("calc_repetitive_questions", False)
    falls = st.session_state.get("calc_falls", "none")
    mobility = st.session_state.get("calc_mobility", "independent")
    overnight = st.session_state.get("calc_overnight_needed", False)
    
    # Build context (using schema field names)
    context = HoursContext(
        badls_count=len(badls),
        iadls_count=len(iadls),
        badls_list=badls,
        iadls_list=iadls,
        cognitive_level=cognitive_level,
        wandering=wandering,
        aggression=aggression,
        sundowning=sundowning,
        repetitive_questions=repetitive_questions,
        falls=falls,
        mobility=mobility,
        overnight_needed=overnight,
    )
    
    # Calculate baseline hours (loop through lists)
    badl_hours = sum(get_badl_hours(badl) for badl in badls)
    iadl_hours = sum(get_iadl_hours(iadl) for iadl in iadls)
    cognitive_multiplier = get_cognitive_multiplier(
        cognitive_level,
        wandering,
        aggression,
        sundowning,
        repetitive_questions,
    )
    fall_multiplier = get_fall_risk_multiplier(falls)
    mobility_hours = get_mobility_hours(mobility)
    
    baseline_hours = (badl_hours + iadl_hours) * cognitive_multiplier * fall_multiplier + mobility_hours
    
    # Determine baseline band
    if baseline_hours < 1:
        baseline_band = "<1h"
    elif baseline_hours < 4:
        baseline_band = "1-3h"
    elif baseline_hours < 24:
        baseline_band = "4-8h"
    else:
        baseline_band = "24h"
    
    # Try LLM recommendation (if enabled)
    llm_band = None
    llm_confidence = None
    llm_reasons = []
    llm_error = None
    
    try:
        # Always try to get LLM advice (mode="assist" - will check for API key internally)
        ok, llm_result = generate_hours_advice(context, mode="assist")
        if ok and llm_result:
            llm_band = llm_result.band
            llm_confidence = llm_result.confidence
            llm_reasons = llm_result.reasons
        else:
            llm_error = "LLM not available (check API key or FEATURE_LLM_NAVI flag)"
    except Exception as e:
        llm_error = str(e)
    
    # Store results
    st.session_state.calc_results = {
        "baseline_band": baseline_band,
        "baseline_hours": round(baseline_hours, 2),
        "badl_hours": round(badl_hours, 2),
        "iadl_hours": round(iadl_hours, 2),
        "cognitive_multiplier": cognitive_multiplier,
        "fall_multiplier": fall_multiplier,
        "mobility_hours": mobility_hours,
        "llm_band": llm_band,
        "llm_confidence": llm_confidence,
        "llm_reasons": llm_reasons,
        "llm_error": llm_error,
        "agreement": baseline_band == llm_band if llm_band else None,
        "context": context,
    }
    
    st.rerun()


def _render_results() -> None:
    """Render calculation results."""
    if "calc_results" not in st.session_state:
        st.info("👈 Enter care needs and click **Calculate Hours** to see results")
        return
    
    results = st.session_state.calc_results
    
    st.markdown("### 📊 Calculation Results")
    
    # Baseline calculation
    st.markdown("#### 🧮 Weighted Baseline Calculation")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Recommended Band", results["baseline_band"])
        st.metric("Calculated Hours", f"{results['baseline_hours']}h")
    
    with col2:
        st.markdown("**Breakdown:**")
        st.markdown(f"- BADL hours: `{results['badl_hours']}h`")
        st.markdown(f"- IADL hours: `{results['iadl_hours']}h`")
        st.markdown(f"- × Cognitive multiplier: `{results['cognitive_multiplier']}x`")
        st.markdown(f"- × Fall risk multiplier: `{results['fall_multiplier']}x`")
        st.markdown(f"- + Mobility aid hours: `{results['mobility_hours']}h`")
        st.markdown(f"- **= Total: `{results['baseline_hours']}h` → `{results['baseline_band']}`**")
    
    st.markdown("---")
    
    # LLM recommendation
    st.markdown("#### 🤖 LLM Recommendation")
    
    if results["llm_error"]:
        st.warning(f"⚠️ LLM recommendation failed: {results['llm_error']}")
        st.info("💡 LLM may be disabled (check `FEATURE_LLM_NAVI` flag) or API key not configured.")
    elif results["llm_band"]:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("LLM Band", results["llm_band"])
            st.metric("Confidence", f"{results['llm_confidence']:.0%}")
            
            # Agreement indicator
            if results["agreement"]:
                st.success("✅ Agreement with baseline")
            else:
                st.warning("⚠️ Disagreement with baseline")
        
        with col2:
            st.markdown("**LLM Reasoning:**")
            for i, reason in enumerate(results["llm_reasons"], 1):
                st.markdown(f"{i}. {reason}")
    else:
        st.info("LLM recommendation not available")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Copy Results", use_container_width=True):
            _copy_results_to_clipboard()
    with col2:
        if st.button("💾 Save Test Case", use_container_width=True):
            _show_save_dialog()


def _copy_results_to_clipboard() -> None:
    """Format results as text and show in dialog for copying."""
    results = st.session_state.calc_results
    context = results["context"]
    
    # Format as text
    text = f"""Care Hours Calculator Results
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

INPUTS:
-------
BADLs: {', '.join(context.badls_list) if context.badls_list else 'None'}
IADLs: {', '.join(context.iadls_list) if context.iadls_list else 'None'}
Cognitive Level: {context.cognitive_level}
Wandering: {context.wandering}
Aggression: {context.aggression}
Sundowning: {context.sundowning}
Repetitive Questions: {context.repetitive_questions}
Fall Risk: {context.falls}
Mobility Aid: {context.mobility}
Overnight Care: {context.overnight_needed}

BASELINE CALCULATION:
--------------------
Recommended Band: {results['baseline_band']}
Calculated Hours: {results['baseline_hours']}h
  - BADL hours: {results['badl_hours']}h
  - IADL hours: {results['iadl_hours']}h
  - Cognitive multiplier: {results['cognitive_multiplier']}x
  - Fall risk multiplier: {results['fall_multiplier']}x
  - Mobility aid hours: {results['mobility_hours']}h

LLM RECOMMENDATION:
------------------
Band: {results['llm_band'] or 'N/A'}
Confidence: {f"{results['llm_confidence']:.0%}" if results['llm_confidence'] else 'N/A'}
Agreement: {'Yes' if results['agreement'] else 'No' if results['agreement'] is not None else 'N/A'}
Reasoning:
{chr(10).join(f'  {i}. {r}' for i, r in enumerate(results['llm_reasons'], 1)) if results['llm_reasons'] else '  N/A'}
"""
    
    # Show in text area for copying
    st.text_area("Copy this text:", text, height=400)


def _show_save_dialog() -> None:
    """Show dialog to save test case with optional notes."""
    st.session_state.show_save_dialog = True


def render(ctx=None) -> None:
    """Render Care Hours Calculator.
    
    Args:
        ctx: Optional context (unused, for product interface compatibility)
    """
    # Render header
    render_header_simple(active_route="care_hours_calculator")
    
    # Render Navi panel
    render_navi_panel_v2(
        title="Care Hours Calculator",
        reason="Test the care hours calculation algorithm with direct inputs. Compare weighted baseline vs LLM recommendations.",
        encouragement={
            "icon": "🧮",
            "text": "Internal testing tool for validation",
            "status": "info"
        },
        context_chips=[
            {"label": "Testing Tool"},
            {"label": "Phase 1 Validation", "variant": "muted"},
        ],
        primary_action={"label": "", "route": ""},
        variant="product"
    )
    
    # Warning banner
    st.markdown(
        """
        <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 12px; margin: 16px 0;">
            <strong>⚠️ Internal Testing Tool</strong> — 
            This calculator is for validation purposes only. 
            Results should be compared against real advisor assessments.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Two-column layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        _render_input_form()
    
    with col2:
        _render_results()
    
    # Save dialog (if open)
    if st.session_state.get("show_save_dialog", False):
        with st.container():
            st.markdown("### 💾 Save Test Case")
            notes = st.text_area("Optional Notes:", placeholder="e.g., 'Real case from advisor Sarah, adjusted wandering behavior'")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save", type="primary", use_container_width=True):
                    _save_test_case_with_notes(notes)
                    st.session_state.show_save_dialog = False
                    st.rerun()
            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.show_save_dialog = False
                    st.rerun()
    
    # Render footer
    render_footer_simple()


def _save_test_case_with_notes(notes: str) -> None:
    """Save test case with optional notes.
    
    Args:
        notes: Optional notes about the test case
    """
    results = st.session_state.calc_results
    context = results["context"]
    
    case = {
        "timestamp": datetime.now().isoformat(),
        "inputs": {
            "badls": context.badls_list,
            "iadls": context.iadls_list,
            "cognitive_level": context.cognitive_level,
            "wandering": context.wandering,
            "aggression": context.aggression,
            "sundowning": context.sundowning,
            "repetitive_questions": context.repetitive_questions,
            "falls": context.falls,
            "mobility": context.mobility,
            "overnight_needed": context.overnight_needed,
        },
        "results": {
            "baseline_band": results["baseline_band"],
            "baseline_hours": results["baseline_hours"],
            "llm_band": results["llm_band"],
            "llm_confidence": results["llm_confidence"],
            "llm_reasons": results["llm_reasons"],
            "agreement": results["agreement"],
        },
        "notes": notes.strip() if notes else "",
    }
    
    _save_validation_case(case)
