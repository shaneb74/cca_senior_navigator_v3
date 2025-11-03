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
    """Render input form for care needs (matches GCP v4 structure)."""
    st.markdown("### 📋 Care Needs Input")
    st.caption("Fields match GCP v4 module structure for accurate testing")
    
    # BADLs (matches gcp_v4 badls question)
    st.markdown("**Basic Activities of Daily Living (BADLs)**")
    st.caption("GCP field: `badls` (multi-select)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.calc_bathing = st.checkbox("🚿 Bathing/Showering", value=st.session_state.get("calc_bathing", False), key="calc_badl_bathing")
        st.session_state.calc_dressing = st.checkbox("� Dressing", value=st.session_state.get("calc_dressing", False), key="calc_badl_dressing")
        st.session_state.calc_eating = st.checkbox("🍽️ Eating", value=st.session_state.get("calc_eating", False), key="calc_badl_eating")
    with col2:
        st.session_state.calc_toileting = st.checkbox("� Toileting", value=st.session_state.get("calc_toileting", False), key="calc_badl_toileting")
        st.session_state.calc_transferring = st.checkbox("🪑 Transferring", value=st.session_state.get("calc_transferring", False), key="calc_badl_transferring")
        st.session_state.calc_hygiene = st.checkbox("🧼 Personal Hygiene", value=st.session_state.get("calc_hygiene", False), key="calc_badl_hygiene")
    with col3:
        st.session_state.calc_mobility = st.checkbox("🚶 Mobility", value=st.session_state.get("calc_mobility", False), key="calc_badl_mobility")
    
    st.markdown("---")
    
    # IADLs (matches gcp_v4 iadls question)
    st.markdown("**Instrumental Activities of Daily Living (IADLs)**")
    st.caption("GCP field: `iadls` (multi-select)")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.session_state.calc_meal_prep = st.checkbox("🍳 Meal preparation", value=st.session_state.get("calc_meal_prep", False), key="calc_iadl_meal")
        st.session_state.calc_housekeeping = st.checkbox("🧹 Housekeeping", value=st.session_state.get("calc_housekeeping", False), key="calc_iadl_house")
    with col2:
        st.session_state.calc_finances = st.checkbox("💰 Managing finances", value=st.session_state.get("calc_finances", False), key="calc_iadl_finances")
        st.session_state.calc_med_management = st.checkbox("� Medication management", value=st.session_state.get("calc_med_management", False), key="calc_iadl_meds")
    with col3:
        st.session_state.calc_transportation = st.checkbox("🚗 Transportation", value=st.session_state.get("calc_transportation", False), key="calc_iadl_transport")
        st.session_state.calc_shopping = st.checkbox("🛒 Shopping", value=st.session_state.get("calc_shopping", False), key="calc_iadl_shopping")
    with col4:
        st.session_state.calc_communication = st.checkbox("📞 Communication", value=st.session_state.get("calc_communication", False), key="calc_iadl_comm")
    
    st.markdown("---")
    
    # Cognitive & Behaviors (matches gcp_v4 memory_changes + behaviors)
    st.markdown("**Cognitive Status & Behaviors**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption("GCP field: `memory_changes` (single-select)")
        st.session_state.calc_memory_changes = st.radio(
            "Cognitive health or memory changes",
            options=["no_concerns", "occasional", "moderate", "severe"],
            format_func=lambda x: {
                "no_concerns": "No concerns",
                "occasional": "Occasional forgetfulness",
                "moderate": "Moderate memory/thinking issues",
                "severe": "Severe (dementia/Alzheimer's)"
            }[x],
            index=["no_concerns", "occasional", "moderate", "severe"].index(
                st.session_state.get("calc_memory_changes", "no_concerns")
            ),
            horizontal=False,
            key="calc_memory"
        )
    
    with col2:
        st.caption("GCP field: `behaviors` (multi-select)")
        st.markdown("**Challenging Behaviors**")
        col2a, col2b = st.columns(2)
        with col2a:
            st.session_state.calc_wandering = st.checkbox("🚶 Wandering", value=st.session_state.get("calc_wandering", False), key="calc_behav_wander")
            st.session_state.calc_aggression = st.checkbox("😤 Aggression", value=st.session_state.get("calc_aggression", False), key="calc_behav_aggr")
            st.session_state.calc_elopement = st.checkbox("🚪 Elopement", value=st.session_state.get("calc_elopement", False), key="calc_behav_elope")
            st.session_state.calc_confusion = st.checkbox("❓ Confusion", value=st.session_state.get("calc_confusion", False), key="calc_behav_conf")
            st.session_state.calc_sundowning = st.checkbox("🌙 Sundowning", value=st.session_state.get("calc_sundowning", False), key="calc_behav_sun")
        with col2b:
            st.session_state.calc_repetitive = st.checkbox("🔁 Repetitive questioning", value=st.session_state.get("calc_repetitive", False), key="calc_behav_rep")
            st.session_state.calc_judgment = st.checkbox("⚖️ Poor judgment", value=st.session_state.get("calc_judgment", False), key="calc_behav_judg")
            st.session_state.calc_hoarding = st.checkbox("📦 Hoarding", value=st.session_state.get("calc_hoarding", False), key="calc_behav_hoard")
            st.session_state.calc_sleep = st.checkbox("😴 Sleep disturbances", value=st.session_state.get("calc_sleep", False), key="calc_behav_sleep")
    
    st.markdown("---")
    
    # Safety & Mobility (matches gcp_v4 falls + mobility)
    st.markdown("**Safety & Mobility**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption("GCP field: `falls` (single-select)")
        st.session_state.calc_falls = st.radio(
            "Fall history",
            options=["none", "one", "multiple"],
            format_func=lambda x: {
                "none": "No falls in past 6 months",
                "one": "One fall",
                "multiple": "Multiple falls"
            }[x],
            index=["none", "one", "multiple"].index(
                st.session_state.get("calc_falls", "none")
            ),
            horizontal=False,
            key="calc_fall_hist"
        )
    
    with col2:
        st.caption("GCP field: `mobility` (single-select)")
        st.session_state.calc_mobility_aid = st.radio(
            "Mobility level",
            options=["independent", "walker", "wheelchair", "bedbound"],
            format_func=lambda x: {
                "independent": "Walks independently",
                "walker": "Uses cane or walker",
                "wheelchair": "Uses wheelchair/scooter",
                "bedbound": "Bed-bound/limited"
            }[x],
            index=["independent", "walker", "wheelchair", "bedbound"].index(
                st.session_state.get("calc_mobility_aid", "independent")
            ),
            horizontal=False,
            key="calc_mob_aid"
        )
    
    st.markdown("---")
    
    # Advisor Estimate (for model training comparison)
    st.markdown("**💡 Advisor Estimate** *(Optional - for model training)*")
    st.caption("Your professional judgment helps us improve the model")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.session_state.calc_advisor_hours = st.number_input(
            "Hours per day you recommend",
            min_value=0.0,
            max_value=24.0,
            value=st.session_state.get("calc_advisor_hours", 0.0),
            step=0.5,
            help="Enter your professional estimate (leave 0 if not providing)",
            key="calc_adv_hours"
        )
    
    with col2:
        st.session_state.calc_advisor_rationale = st.text_area(
            "Why this estimate? (reasoning)",
            value=st.session_state.get("calc_advisor_rationale", ""),
            placeholder="e.g., 'Based on similar cases, family support available, wandering requires constant supervision...'",
            height=100,
            help="Explain your reasoning - this helps train the model",
            key="calc_adv_reason"
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
    # BADLs (GCP structure)
    st.session_state.calc_bathing = False
    st.session_state.calc_dressing = False
    st.session_state.calc_eating = False
    st.session_state.calc_toileting = False
    st.session_state.calc_transferring = False
    st.session_state.calc_hygiene = False
    st.session_state.calc_mobility = False
    
    # IADLs (GCP structure)
    st.session_state.calc_meal_prep = False
    st.session_state.calc_housekeeping = False
    st.session_state.calc_finances = False
    st.session_state.calc_med_management = False
    st.session_state.calc_transportation = False
    st.session_state.calc_shopping = False
    st.session_state.calc_communication = False
    
    # Cognitive & Behaviors (GCP structure)
    st.session_state.calc_memory_changes = "no_concerns"
    st.session_state.calc_wandering = False
    st.session_state.calc_aggression = False
    st.session_state.calc_elopement = False
    st.session_state.calc_confusion = False
    st.session_state.calc_sundowning = False
    st.session_state.calc_repetitive = False
    st.session_state.calc_judgment = False
    st.session_state.calc_hoarding = False
    st.session_state.calc_sleep = False
    
    # Safety & Mobility (GCP structure)
    st.session_state.calc_falls = "none"
    st.session_state.calc_mobility_aid = "independent"
    
    # Advisor Estimate
    st.session_state.calc_advisor_hours = 0.0
    st.session_state.calc_advisor_rationale = ""
    
    # Clear results
    if "calc_results" in st.session_state:
        del st.session_state.calc_results
    
    st.rerun()


def _calculate_and_store() -> None:
    """Calculate hours using weighted baseline and LLM, store results."""
    # Build BADLs list (GCP values → hours engine values)
    badls = []
    if st.session_state.get("calc_bathing", False):
        badls.append("bathing")
    if st.session_state.get("calc_dressing", False):
        badls.append("dressing")
    if st.session_state.get("calc_eating", False):
        badls.append("eating")
    if st.session_state.get("calc_toileting", False):
        badls.append("toileting")
    if st.session_state.get("calc_transferring", False):
        badls.append("transferring")
    if st.session_state.get("calc_hygiene", False):
        badls.append("hygiene")
    if st.session_state.get("calc_mobility", False):
        badls.append("mobility")
    
    # Build IADLs list (GCP values → hours engine values)
    iadls = []
    if st.session_state.get("calc_meal_prep", False):
        iadls.append("meal_preparation")
    if st.session_state.get("calc_housekeeping", False):
        iadls.append("housekeeping")
    if st.session_state.get("calc_finances", False):
        iadls.append("financial_management")
    if st.session_state.get("calc_med_management", False):
        iadls.append("medication_management")
    if st.session_state.get("calc_transportation", False):
        iadls.append("transportation")
    if st.session_state.get("calc_shopping", False):
        iadls.append("shopping")
    if st.session_state.get("calc_communication", False):
        iadls.append("phone_use")  # Map communication → phone_use for weights
    
    # Map GCP memory_changes to cognitive_level for hours engine
    memory_changes = st.session_state.get("calc_memory_changes", "no_concerns")
    cognitive_level_map = {
        "no_concerns": "none",
        "occasional": "mild",
        "moderate": "moderate",
        "severe": "severe"
    }
    cognitive_level = cognitive_level_map.get(memory_changes, "none")
    
    # Get behavior flags (GCP structure)
    wandering = st.session_state.get("calc_wandering", False)
    aggression = st.session_state.get("calc_aggression", False)
    sundowning = st.session_state.get("calc_sundowning", False)
    repetitive_questions = st.session_state.get("calc_repetitive", False)
    
    # Get falls (GCP uses "one" not "once")
    falls_gcp = st.session_state.get("calc_falls", "none")
    falls_map = {
        "none": "none",
        "one": "once",  # Map GCP "one" → hours engine "once"
        "multiple": "multiple"
    }
    falls = falls_map.get(falls_gcp, "none")
    
    # Get mobility (GCP structure matches hours engine)
    mobility = st.session_state.get("calc_mobility_aid", "independent")
    
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
        overnight_needed=False,  # Not in GCP, set to false
    )
    
    # Calculate baseline hours (loop through lists + ALL 9 behaviors)
    badl_hours = sum(get_badl_hours(badl) for badl in badls)
    iadl_hours = sum(get_iadl_hours(iadl) for iadl in iadls)
    cognitive_multiplier = get_cognitive_multiplier(
        cognitive_level,
        has_wandering=wandering,
        has_aggression=aggression,
        has_sundowning=sundowning,
        has_repetitive_questions=repetitive_questions,
        has_elopement=st.session_state.get("calc_elopement", False),
        has_confusion=st.session_state.get("calc_confusion", False),
        has_judgment=st.session_state.get("calc_judgment", False),
        has_hoarding=st.session_state.get("calc_hoarding", False),
        has_sleep=st.session_state.get("calc_sleep", False),
    )
    fall_multiplier = get_fall_risk_multiplier(falls)
    mobility_hours = get_mobility_hours(mobility)
    
    baseline_hours = (badl_hours + iadl_hours) * cognitive_multiplier * fall_multiplier + mobility_hours
    
    # Determine baseline band (CRITICAL: Must match production thresholds)
    if baseline_hours < 1:
        baseline_band = "<1h"
    elif baseline_hours < 4:
        baseline_band = "1-3h"
    elif baseline_hours < 8:
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
        "advisor_hours": st.session_state.get("calc_advisor_hours", 0.0),
        "advisor_rationale": st.session_state.get("calc_advisor_rationale", ""),
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
    
    # Advisor Estimate (if provided)
    if results.get("advisor_hours", 0.0) > 0:
        st.markdown("#### 💡 Advisor Estimate")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Advisor Hours", f"{results['advisor_hours']}h")
            
            # Comparison with baseline
            diff = results['advisor_hours'] - results['baseline_hours']
            if abs(diff) < 1:
                st.success("✅ Close to baseline")
            elif diff > 0:
                st.warning(f"⬆️ +{diff:.1f}h above baseline")
            else:
                st.warning(f"⬇️ {diff:.1f}h below baseline")
        
        with col2:
            st.markdown("**Advisor Rationale:**")
            st.info(results['advisor_rationale'] if results['advisor_rationale'] else "_No rationale provided_")
    
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

ADVISOR ESTIMATE:
----------------
Hours: {results.get('advisor_hours', 0.0)}h
Rationale: {results.get('advisor_rationale', 'Not provided')}
Difference from Baseline: {results.get('advisor_hours', 0) - results['baseline_hours']:.1f}h
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
            "memory_changes": st.session_state.get("calc_memory_changes", "no_concerns"),  # Store GCP value
            "cognitive_level": context.cognitive_level,  # Mapped value for engine
            "behaviors": {
                "wandering": context.wandering,
                "aggression": context.aggression,
                "elopement": st.session_state.get("calc_elopement", False),
                "confusion": st.session_state.get("calc_confusion", False),
                "sundowning": context.sundowning,
                "repetitive": context.repetitive_questions,
                "judgment": st.session_state.get("calc_judgment", False),
                "hoarding": st.session_state.get("calc_hoarding", False),
                "sleep": st.session_state.get("calc_sleep", False),
            },
            "falls": st.session_state.get("calc_falls", "none"),  # Store GCP value (one/multiple)
            "mobility": context.mobility,
            "overnight_needed": context.overnight_needed,
        },
        "results": {
            "baseline_band": results["baseline_band"],
            "baseline_hours": results["baseline_hours"],
            "baseline_breakdown": {
                "badl_hours": results["badl_hours"],
                "iadl_hours": results["iadl_hours"],
                "cognitive_multiplier": results["cognitive_multiplier"],
                "fall_multiplier": results["fall_multiplier"],
                "mobility_hours": results["mobility_hours"],
            },
            "llm_band": results["llm_band"],
            "llm_confidence": results["llm_confidence"],
            "llm_reasons": results["llm_reasons"],
            "agreement": results["agreement"],
            "advisor_hours": results.get("advisor_hours", 0.0),
            "advisor_rationale": results.get("advisor_rationale", ""),
            "advisor_vs_baseline_diff": results.get("advisor_hours", 0.0) - results["baseline_hours"],
        },
        "notes": notes.strip() if notes else "",
    }
    
    _save_validation_case(case)
