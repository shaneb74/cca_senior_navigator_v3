"""
GCP Test Tool - Internal Testing Tool

Allows advisors to test the complete Guided Care Plan logic with direct inputs.
Replicates all GCP v4 sections and scoring to validate tier recommendations,
cognitive gates, behavior gates, and LLM adjudication logic.

TODO: Remove this product by 2025-12-15 after validation phase complete.
"""

import json
import streamlit as st
from datetime import datetime
from pathlib import Path
from typing import Any

from products.gcp_v4.modules.care_recommendation.logic import (
    derive_outcome,
    cognitive_gate,
    cognition_band,
    support_band,
    mc_behavior_gate_enabled,
    cognitive_gate_behaviors_only,
    TIER_THRESHOLDS,
)
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple
from core.ui import render_navi_panel_v2


# Path to validation cases JSON
VALIDATION_CASES_PATH = Path(__file__).parent / "gcp_validation_cases.json"


def _load_validation_cases() -> list[dict[str, Any]]:
    """Load saved GCP validation test cases.
    
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
    """Save a GCP validation test case to JSON.
    
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


def _render_about_you_section() -> None:
    """Render About You section inputs."""
    with st.expander("📋 **About You**", expanded=True):
        st.caption("GCP Section: `about_you`")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.gcp_age_range = st.selectbox(
                "Age Range",
                options=["under_65", "65_74", "75_84", "85_plus"],
                format_func=lambda x: {
                    "under_65": "Under 65",
                    "65_74": "65–74",
                    "75_84": "75–84",
                    "85_plus": "85+"
                }[x],
                index=["under_65", "65_74", "75_84", "85_plus"].index(
                    st.session_state.get("gcp_age_range", "75_84")
                ),
                key="gcp_test_age"
            )
            
            st.session_state.gcp_living_situation = st.selectbox(
                "Living Situation",
                options=["alone", "with_spouse_or_partner", "with_family", "assisted_living"],
                format_func=lambda x: {
                    "alone": "Alone",
                    "with_spouse_or_partner": "With spouse/partner",
                    "with_family": "With family",
                    "assisted_living": "Assisted living"
                }[x],
                index=["alone", "with_spouse_or_partner", "with_family", "assisted_living"].index(
                    st.session_state.get("gcp_living_situation", "alone")
                ),
                key="gcp_test_living"
            )
        
        with col2:
            st.session_state.gcp_isolation = st.selectbox(
                "Geographic Isolation",
                options=["accessible", "somewhat", "very"],
                format_func=lambda x: {
                    "accessible": "Accessible",
                    "somewhat": "Somewhat isolated",
                    "very": "Very isolated"
                }[x],
                index=["accessible", "somewhat", "very"].index(
                    st.session_state.get("gcp_isolation", "accessible")
                ),
                key="gcp_test_isolation"
            )


def _render_medication_mobility_section() -> None:
    """Render Medication & Mobility section inputs."""
    with st.expander("💊 **Medication & Mobility**", expanded=True):
        st.caption("GCP Section: `medication_mobility`")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.gcp_meds_complexity = st.selectbox(
                "Medication Complexity",
                options=["none", "simple", "moderate", "complex"],
                format_func=lambda x: {
                    "none": "None",
                    "simple": "Simple",
                    "moderate": "Moderate",
                    "complex": "Complex"
                }[x],
                index=["none", "simple", "moderate", "complex"].index(
                    st.session_state.get("gcp_meds_complexity", "simple")
                ),
                key="gcp_test_meds"
            )
            
            st.session_state.gcp_mobility = st.selectbox(
                "Mobility Level",
                options=["independent", "walker", "wheelchair", "bedbound"],
                format_func=lambda x: {
                    "independent": "Walks independently",
                    "walker": "Uses cane/walker",
                    "wheelchair": "Uses wheelchair",
                    "bedbound": "Bed-bound"
                }[x],
                index=["independent", "walker", "wheelchair", "bedbound"].index(
                    st.session_state.get("gcp_mobility", "independent")
                ),
                key="gcp_test_mobility"
            )
        
        with col2:
            st.session_state.gcp_falls = st.selectbox(
                "Fall History",
                options=["none", "one", "multiple"],
                format_func=lambda x: {
                    "none": "No falls",
                    "one": "One fall",
                    "multiple": "Multiple falls"
                }[x],
                index=["none", "one", "multiple"].index(
                    st.session_state.get("gcp_falls", "none")
                ),
                key="gcp_test_falls"
            )
            
            st.markdown("**Chronic Conditions** (multi-select)")
            chronic_options = ["diabetes", "chf", "copd", "hypertension", "arthritis", "stroke", "parkinsons", "cancer", "other"]
            st.session_state.gcp_chronic = st.multiselect(
                "Select all that apply",
                options=chronic_options,
                default=st.session_state.get("gcp_chronic", []),
                key="gcp_test_chronic"
            )


def _render_cognition_section() -> None:
    """Render Cognition & Mental Health section inputs."""
    with st.expander("🧠 **Cognition & Mental Health**", expanded=True):
        st.caption("GCP Section: `cognition_mental_health`")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.gcp_memory_changes = st.selectbox(
                "Memory Changes",
                options=["no_concerns", "occasional", "moderate", "severe"],
                format_func=lambda x: {
                    "no_concerns": "No concerns",
                    "occasional": "Occasional forgetfulness",
                    "moderate": "Moderate issues",
                    "severe": "Severe (dementia/Alzheimer's)"
                }[x],
                index=["no_concerns", "occasional", "moderate", "severe"].index(
                    st.session_state.get("gcp_memory_changes", "no_concerns")
                ),
                key="gcp_test_memory"
            )
            
            st.session_state.gcp_mood = st.selectbox(
                "Mood",
                options=["great", "mostly_good", "okay", "low"],
                format_func=lambda x: {
                    "great": "Great",
                    "mostly_good": "Mostly good",
                    "okay": "Okay",
                    "low": "Low"
                }[x],
                index=["great", "mostly_good", "okay", "low"].index(
                    st.session_state.get("gcp_mood", "mostly_good")
                ),
                key="gcp_test_mood"
            )
        
        with col2:
            st.markdown("**Behaviors** (multi-select)")
            behavior_options = [
                "wandering", "aggression", "elopement", "confusion", 
                "sundowning", "repetitive", "judgment", "hoarding", "sleep"
            ]
            st.session_state.gcp_behaviors = st.multiselect(
                "Select all that apply",
                options=behavior_options,
                format_func=lambda x: x.replace("_", " ").title(),
                default=st.session_state.get("gcp_behaviors", []),
                key="gcp_test_behaviors"
            )
        
        # Cognitive diagnosis confirmation (only if severe)
        if st.session_state.get("gcp_memory_changes") == "severe":
            st.markdown("---")
            st.session_state.gcp_cognitive_dx = st.selectbox(
                "Formal Diagnosis? (dementia/Alzheimer's)",
                options=["dx_yes", "dx_no", "dx_unsure"],
                format_func=lambda x: {
                    "dx_yes": "Yes, diagnosed",
                    "dx_no": "No",
                    "dx_unsure": "Not sure"
                }[x],
                index=["dx_yes", "dx_no", "dx_unsure"].index(
                    st.session_state.get("gcp_cognitive_dx", "dx_yes")
                ),
                key="gcp_test_dx"
            )


def _render_daily_living_section() -> None:
    """Render Daily Living section inputs."""
    with st.expander("🏠 **Daily Living**", expanded=True):
        st.caption("GCP Section: `daily_living`")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.gcp_help_overall = st.selectbox(
                "Overall Help Needed",
                options=["independent", "some_help", "daily_help", "full_support"],
                format_func=lambda x: {
                    "independent": "Independent",
                    "some_help": "Some help",
                    "daily_help": "Daily help",
                    "full_support": "Full support"
                }[x],
                index=["independent", "some_help", "daily_help", "full_support"].index(
                    st.session_state.get("gcp_help_overall", "some_help")
                ),
                key="gcp_test_help"
            )
            
            st.markdown("**BADLs** (multi-select)")
            badl_options = [
                "bathing", "dressing", "eating", "toileting", 
                "transferring", "hygiene", "mobility"
            ]
            st.session_state.gcp_badls = st.multiselect(
                "Basic ADLs needing help",
                options=badl_options,
                format_func=lambda x: x.replace("_", " ").title(),
                default=st.session_state.get("gcp_badls", []),
                key="gcp_test_badls"
            )
        
        with col2:
            st.session_state.gcp_primary_support = st.selectbox(
                "Primary Support Provider",
                options=["family", "paid", "community", "none"],
                format_func=lambda x: {
                    "family": "Family/friends",
                    "paid": "Paid caregiver",
                    "community": "Community/agency",
                    "none": "No regular support"
                }[x],
                index=["family", "paid", "community", "none"].index(
                    st.session_state.get("gcp_primary_support", "family")
                ),
                key="gcp_test_support"
            )
            
            st.markdown("**IADLs** (multi-select)")
            iadl_options = [
                "meal_prep", "housekeeping", "finances", "med_management",
                "transportation", "shopping", "communication"
            ]
            st.session_state.gcp_iadls = st.multiselect(
                "Instrumental ADLs needing help",
                options=iadl_options,
                format_func=lambda x: x.replace("_", " ").title(),
                default=st.session_state.get("gcp_iadls", []),
                key="gcp_test_iadls"
            )
        
        # Hours per day
        st.markdown("---")
        st.session_state.gcp_hours_per_day = st.selectbox(
            "Hours per Day of Assistance",
            options=["<1h", "1-3h", "4-8h", "12-16h", "24h"],
            index=["<1h", "1-3h", "4-8h", "12-16h", "24h"].index(
                st.session_state.get("gcp_hours_per_day", "1-3h")
            ),
            key="gcp_test_hours"
        )


def _render_move_preferences_section() -> None:
    """Render Move Preferences section inputs."""
    with st.expander("🏡 **Move Preferences** (Optional)", expanded=False):
        st.caption("GCP Section: `move_preferences` (only shown for facility recommendations)")
        
        st.session_state.gcp_move_preference = st.selectbox(
            "Willingness to Move",
            options=["1", "2", "3", "4"],
            format_func=lambda x: {
                "1": "1 – Strong preference to stay home",
                "2": "2 – Uncertain",
                "3": "3 – Open if it improves care",
                "4": "4 – Comfortable moving"
            }[x],
            index=["1", "2", "3", "4"].index(
                st.session_state.get("gcp_move_preference", "2")
            ),
            key="gcp_test_move"
        )


def _render_input_form() -> None:
    """Render complete GCP input form."""
    st.markdown("### 📋 GCP Input Form")
    st.caption("All sections match GCP v4 module structure")
    
    # Render all sections
    _render_about_you_section()
    _render_medication_mobility_section()
    _render_cognition_section()
    _render_daily_living_section()
    _render_move_preferences_section()
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧮 Calculate Recommendation", type="primary", use_container_width=True):
            _calculate_and_store()
    with col2:
        if st.button("🗑️ Clear Form", use_container_width=True):
            _clear_form()


def _clear_form() -> None:
    """Clear all form inputs."""
    # About You
    st.session_state.gcp_age_range = "75_84"
    st.session_state.gcp_living_situation = "alone"
    st.session_state.gcp_isolation = "accessible"
    
    # Medication & Mobility
    st.session_state.gcp_meds_complexity = "simple"
    st.session_state.gcp_mobility = "independent"
    st.session_state.gcp_falls = "none"
    st.session_state.gcp_chronic = []
    
    # Cognition & Mental Health
    st.session_state.gcp_memory_changes = "no_concerns"
    st.session_state.gcp_mood = "mostly_good"
    st.session_state.gcp_behaviors = []
    st.session_state.gcp_cognitive_dx = "dx_yes"
    
    # Daily Living
    st.session_state.gcp_help_overall = "some_help"
    st.session_state.gcp_badls = []
    st.session_state.gcp_iadls = []
    st.session_state.gcp_primary_support = "family"
    st.session_state.gcp_hours_per_day = "1-3h"
    
    # Move Preferences
    st.session_state.gcp_move_preference = "2"
    
    # Clear results
    if "gcp_test_results" in st.session_state:
        del st.session_state.gcp_test_results
    
    st.rerun()


def _calculate_and_store() -> None:
    """Calculate GCP recommendation using actual GCP logic, store results."""
    # Build answers dict (matches GCP v4 structure)
    answers = {
        # About You
        "age_range": st.session_state.get("gcp_age_range", "75_84"),
        "living_situation": st.session_state.get("gcp_living_situation", "alone"),
        "isolation": st.session_state.get("gcp_isolation", "accessible"),
        
        # Medication & Mobility
        "meds_complexity": st.session_state.get("gcp_meds_complexity", "simple"),
        "mobility": st.session_state.get("gcp_mobility", "independent"),
        "falls": st.session_state.get("gcp_falls", "none"),
        "chronic_conditions": st.session_state.get("gcp_chronic", []),
        
        # Cognition & Mental Health
        "memory_changes": st.session_state.get("gcp_memory_changes", "no_concerns"),
        "mood": st.session_state.get("gcp_mood", "mostly_good"),
        "behaviors": st.session_state.get("gcp_behaviors", []),
        "cognitive_dx_confirm": st.session_state.get("gcp_cognitive_dx", "dx_yes"),
        
        # Daily Living
        "help_overall": st.session_state.get("gcp_help_overall", "some_help"),
        "badls": st.session_state.get("gcp_badls", []),
        "iadls": st.session_state.get("gcp_iadls", []),
        "primary_support": st.session_state.get("gcp_primary_support", "family"),
        "hours_per_day": st.session_state.get("gcp_hours_per_day", "1-3h"),
        
        # Move Preferences
        "move_preference": st.session_state.get("gcp_move_preference", "2"),
    }
    
    # Build minimal context
    context = {
        "age_range": answers["age_range"],
    }
    
    # Call actual GCP derive_outcome function
    try:
        outcome = derive_outcome(answers, context=context)
        
        # Extract gate results for diagnostics
        flags = []
        passes_cognitive = cognitive_gate(answers, flags)
        cog_band = cognition_band(answers, flags)
        sup_band = support_band(answers, flags)
        gate_enabled = mc_behavior_gate_enabled()
        has_risky_behaviors = cognitive_gate_behaviors_only(answers, flags)
        
        # Store results
        st.session_state.gcp_test_results = {
            "tier": outcome["tier"],
            "tier_score": outcome["tier_score"],
            "confidence": outcome["confidence"],
            "flags": outcome["flags"],
            "rationale": outcome["rationale"],
            "tier_rankings": outcome["tier_rankings"],
            "allowed_tiers": outcome.get("allowed_tiers", []),
            "cognitive_gate_pass": passes_cognitive,
            "cognition_band": cog_band,
            "support_band": sup_band,
            "behavior_gate_enabled": gate_enabled,
            "has_risky_behaviors": has_risky_behaviors,
            "answers": answers,
            "success": True,
            "error": None,
        }
        
    except Exception as e:
        st.session_state.gcp_test_results = {
            "success": False,
            "error": str(e),
            "answers": answers,
        }
    
    st.rerun()


def _render_results() -> None:
    """Render calculation results."""
    if "gcp_test_results" not in st.session_state:
        st.info("👈 Enter GCP inputs and click **Calculate Recommendation** to see results")
        return
    
    results = st.session_state.gcp_test_results
    
    if not results.get("success", False):
        st.error(f"❌ Calculation failed: {results.get('error', 'Unknown error')}")
        return
    
    st.markdown("### 📊 GCP Recommendation Results")
    
    # Primary Recommendation
    st.markdown("#### 🎯 Primary Recommendation")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        tier_display = {
            "no_care_needed": "No Care Needed",
            "in_home": "In-Home Care",
            "assisted_living": "Assisted Living",
            "memory_care": "Memory Care",
            "memory_care_high_acuity": "Memory Care (High Acuity)"
        }
        st.metric("Recommended Tier", tier_display.get(results["tier"], results["tier"]))
    
    with col2:
        st.metric("Tier Score", f"{results['tier_score']} pts")
    
    with col3:
        st.metric("Confidence", f"{results['confidence']:.0%}")
    
    st.markdown("---")
    
    # Tier Rankings
    st.markdown("#### 📈 All Tier Rankings")
    for tier, score in results["tier_rankings"]:
        is_selected = (tier == results["tier"])
        display = tier_display.get(tier, tier)
        
        if is_selected:
            st.markdown(f"**✅ {display}**: `{score} pts` ← **Selected**")
        else:
            st.markdown(f"   {display}: `{score} pts`")
    
    st.markdown("---")
    
    # Gate Analysis
    st.markdown("#### 🚪 Gate Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Cognitive Gate**")
        if results["cognitive_gate_pass"]:
            st.success("✅ PASSED - Memory care allowed")
        else:
            st.warning("❌ FAILED - Memory care blocked")
        
        st.caption(f"Cognition Band: `{results['cognition_band']}`")
        st.caption(f"Support Band: `{results['support_band']}`")
    
    with col2:
        st.markdown("**Behavior Gate**")
        if results["behavior_gate_enabled"]:
            st.info(f"🔒 Enabled (risky behaviors: {results['has_risky_behaviors']})")
        else:
            st.info("🔓 Disabled")
        
        st.caption(f"Allowed Tiers: {', '.join(results['allowed_tiers'])}")
    
    st.markdown("---")
    
    # Rationale
    st.markdown("#### 💡 Rationale")
    for item in results["rationale"]:
        st.markdown(f"- {item}")
    
    st.markdown("---")
    
    # Flags
    if results["flags"]:
        st.markdown("#### 🚩 Flags")
        for flag in results["flags"]:
            st.markdown(f"- `{flag['id']}`: {flag.get('message', 'No message')}")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Copy Results", use_container_width=True):
            _show_copy_dialog()
    with col2:
        if st.button("💾 Save Test Case", use_container_width=True):
            st.session_state.show_save_dialog = True
            st.rerun()


def _show_copy_dialog() -> None:
    """Show results in copyable text format."""
    results = st.session_state.gcp_test_results
    
    # Format as text
    text = f"""GCP Test Tool Results
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

RECOMMENDATION:
--------------
Tier: {results['tier']}
Score: {results['tier_score']} pts
Confidence: {results['confidence']:.0%}

TIER RANKINGS:
-------------
{chr(10).join(f"  {tier}: {score} pts" for tier, score in results['tier_rankings'])}

GATE ANALYSIS:
-------------
Cognitive Gate: {'PASSED' if results['cognitive_gate_pass'] else 'FAILED'}
  - Cognition Band: {results['cognition_band']}
  - Support Band: {results['support_band']}

Behavior Gate: {'Enabled' if results['behavior_gate_enabled'] else 'Disabled'}
  - Risky Behaviors: {results['has_risky_behaviors']}
  - Allowed Tiers: {', '.join(results['allowed_tiers'])}

RATIONALE:
---------
{chr(10).join(f"  - {item}" for item in results['rationale'])}

FLAGS:
-----
{chr(10).join(f"  - {flag['id']}" for flag in results['flags']) if results['flags'] else '  None'}
"""
    
    st.text_area("Copy this text:", text, height=400)


def render(ctx=None) -> None:
    """Render GCP Test Tool.
    
    Args:
        ctx: Optional context (unused, for product interface compatibility)
    """
    # Render header
    render_header_simple(active_route="gcp_test_tool")
    
    # Render Navi panel
    render_navi_panel_v2(
        title="GCP Test Tool",
        reason="Test the complete Guided Care Plan logic with direct inputs. Validate tier recommendations, cognitive gates, behavior gates, and LLM adjudication.",
        encouragement={
            "icon": "🧪",
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
            This tool uses the EXACT logic from GCP v4 module for accurate validation.
            Compare results against real assessments to verify tier recommendations.
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
            notes = st.text_area(
                "Optional Notes:", 
                placeholder="e.g., 'Real case from advisor Sarah, moderate cognition + high support without risky behaviors'",
                key="gcp_save_notes"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save", type="primary", use_container_width=True, key="gcp_save_confirm"):
                    _save_test_case_with_notes(notes)
                    st.session_state.show_save_dialog = False
                    st.rerun()
            with col2:
                if st.button("Cancel", use_container_width=True, key="gcp_save_cancel"):
                    st.session_state.show_save_dialog = False
                    st.rerun()
    
    # Render footer
    render_footer_simple()


def _save_test_case_with_notes(notes: str) -> None:
    """Save test case with optional notes.
    
    Args:
        notes: Optional notes about the test case
    """
    results = st.session_state.gcp_test_results
    
    case = {
        "timestamp": datetime.now().isoformat(),
        "inputs": results["answers"],
        "results": {
            "tier": results["tier"],
            "tier_score": results["tier_score"],
            "confidence": results["confidence"],
            "tier_rankings": results["tier_rankings"],
            "allowed_tiers": results["allowed_tiers"],
            "cognitive_gate_pass": results["cognitive_gate_pass"],
            "cognition_band": results["cognition_band"],
            "support_band": results["support_band"],
            "behavior_gate_enabled": results["behavior_gate_enabled"],
            "has_risky_behaviors": results["has_risky_behaviors"],
            "flags": [flag["id"] for flag in results["flags"]],
        },
        "notes": notes.strip() if notes else "",
    }
    
    _save_validation_case(case)
