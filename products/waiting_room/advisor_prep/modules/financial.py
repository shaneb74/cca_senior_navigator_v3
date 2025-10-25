"""
Advisor Prep - Financial Section

Data inventory view showing captured financial information for advisor review.
"""

import json
from pathlib import Path

import streamlit as st

from core.events import log_event
from core.mcip import MCIP
from core.name_utils import section_header, personalize
from core.navi import render_navi_panel
from products.waiting_room.advisor_prep.prefill import get_financial_prefill


def render():
    """Render Financial data inventory for advisor review."""
    _render_data_inventory()


def _render_data_inventory():
    """Display all capturable financial information fields."""
    
    # Navigation buttons at top
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Housing Preferences", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "housing"
            st.rerun()
    with col2:
        if st.button("About Person →", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "personal"
            st.rerun()
    with col3:
        if st.button("Medical & Care →", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "medical"
            st.rerun()

    # Section header
    st.markdown(f"### {section_header('Financial Information - Capturable Fields')}")
    st.markdown(personalize("*These are all the financial fields the app can capture for {NAME}.*"))

    # Get financial data from various sources
    financial_session_data = st.session_state.get("financial_assessment", {})
    advisor_prep_data = st.session_state.get("advisor_prep", {}).get("data", {}).get("financial", {})
    cost_planner_data = st.session_state.get("cost_planner_v2", {})
    
    # Get prefill data from Cost Planner / Financial Profile
    prefill_data = get_financial_prefill()
    
    # Combine data sources
    all_financial_data = {**financial_session_data, **advisor_prep_data}
    
    # Income and assets fields (from financial.json config)
    monthly_income = (
        all_financial_data.get("monthly_income") or 
        prefill_data.get("monthly_income") or
        cost_planner_data.get("monthly_income")
    )
    
    total_assets = (
        all_financial_data.get("total_assets") or 
        prefill_data.get("total_assets") or
        cost_planner_data.get("total_assets")
    )
    
    _display_data_section("💰 Income & Assets", [
        ("Monthly Income", f"${monthly_income:,.0f}" if monthly_income else "Not captured", 
         ["Number field: Total from all sources (SS, pensions, employment, investments, family)"]),
        ("Total Assets", f"${total_assets:,.0f}" if total_assets else "Not captured",
         ["Number field: Liquid assets, investments, retirement accounts, real estate equity, life insurance"]),
    ])
    
    # Insurance coverage fields (from financial.json config)
    insurance_coverage = (
        all_financial_data.get("insurance_coverage") or 
        prefill_data.get("insurance_coverage", [])
    )
    
    insurance_options = [
        "Medicare Part A (Hospital)", "Medicare Part B (Medical)", "Medicare Part D (Prescription)",
        "Medigap/Supplement", "Medicaid", "VA Benefits", "Long-term Care Insurance", 
        "Private Health Insurance", "None"
    ]
    
    if insurance_coverage:
        insurance_display = ", ".join(insurance_coverage)
    else:
        insurance_display = "Not captured"
    
    _display_data_section("🛡️ Insurance Coverage", [
        ("Insurance Types", insurance_display, insurance_options),
        ("Coverage Count", f"{len(insurance_coverage)} types" if insurance_coverage else "0 types", 
         ["Multi-select: Up to 9 insurance types"]),
    ])
    
    # Primary financial concerns field (from financial.json config)
    primary_concern = (
        all_financial_data.get("primary_concern") or 
        prefill_data.get("primary_concern")
    )
    
    concern_options = ["Affordability", "Limited runway", "Benefits navigation", "None identified"]
    
    _display_data_section("⚠️ Financial Concerns", [
        ("Primary Concern", primary_concern if primary_concern else "Not captured", concern_options),
    ])
    
    # Cost Planner integration fields (computed)
    if cost_planner_data:
        total_monthly_cost = cost_planner_data.get("total_monthly_cost")
        affordability_status = cost_planner_data.get("affordability_status")
        
        _display_data_section("📊 Cost Planning Results", [
            ("Estimated Monthly Cost", f"${total_monthly_cost:,.0f}" if total_monthly_cost else "Not calculated",
             ["Computed by Cost Planner v2"]),
            ("Affordability Status", affordability_status if affordability_status else "Not assessed",
             ["Computed: Affordable/Stretched/Unaffordable"]),
        ])
    else:
        _display_data_section("📊 Cost Planning Results", [
            ("Estimated Monthly Cost", "Not calculated", ["Computed by Cost Planner v2"]),
            ("Affordability Status", "Not assessed", ["Computed: Affordable/Stretched/Unaffordable"]),
        ])
    
    # Show completion status
    if any([monthly_income, total_assets, insurance_coverage, primary_concern, cost_planner_data]):
        st.success("✓ Some financial information captured")
        _mark_section_complete()
    else:
        st.info("No financial data captured yet.")

    # Show data sources and capacity info
    st.markdown("---")
    st.markdown("#### 📋 Financial Data Capacity")
    
    sources = []
    if prefill_data.get("monthly_income") or prefill_data.get("total_assets"):
        sources.append("Cost Planner assessments")
    if cost_planner_data:
        sources.append("Cost Planner calculations")
    if all_financial_data:
        sources.append("Direct advisor prep input")
    
    source_info = f"Data sources: {', '.join(sources)}" if sources else "No financial data sources active"
    
    st.info(f"""
    **Available for capture:**
    - **Income/Assets:** Numeric fields with prefill from Cost Planner
    - **Insurance:** 9 insurance types (multi-select)
    - **Concerns:** 4 predefined financial concern categories
    - **Cost Planning:** Auto-computed from Cost Planner integration
    
    {source_info}
    """)

    # Render Navi panel for contextual guidance
    render_navi_panel()


def _display_data_section(title: str, data_items: list):
    """Display a section of capturable fields.
    
    Args:
        title: Section title
        data_items: List of (field_name, current_value, options) tuples
    """
    st.markdown(f"#### {title}")
    
    for item in data_items:
        if len(item) == 3:
            field_name, value, options = item
            if isinstance(options, list) and len(options) > 1:
                if len(options) > 5:
                    options_display = f"{len(options)} options available"
                else:
                    options_display = f"Options: {', '.join(options)}"
            else:
                options_display = "Type: " + str(options[0]) if options else "Free text"
        else:
            field_name, value = item
            options_display = "Available"
        
        if (value and value != "Not captured" and value != [] and value != "No coverage data" 
            and "0 types" not in str(value) and "Not calculated" not in str(value) 
            and "Not assessed" not in str(value)):
            status = "✅ Captured"
            value_display = f"**{value}**"
        else:
            status = "❌ Not Captured"
            value_display = "*Available for capture*"
        
        col1, col2, col3 = st.columns([2, 1, 3])
        with col1:
            st.write(f"**{field_name}**")
        with col2:
            st.write(status)
        with col3:
            if (value and value != "Not captured" and value != [] and value != "No coverage data" 
                and "0 types" not in str(value) and "Not calculated" not in str(value) 
                and "Not assessed" not in str(value)):
                st.write(value_display)
            else:
                st.caption(options_display)
    
    st.markdown("---")


def _mark_section_complete():
    """Mark financial section as complete."""
    # Initialize advisor_prep structure if needed
    if "advisor_prep" not in st.session_state:
        st.session_state["advisor_prep"] = {
            "sections_complete": [],
            "data": {"personal": {}, "financial": {}, "housing": {}, "medical": {}},
        }
    
    sections_complete = st.session_state["advisor_prep"]["sections_complete"]
    if "financial" not in sections_complete:
        sections_complete.append("financial")
        
        # Update MCIP contract with prep progress
        appt = MCIP.get_advisor_appointment()
        if appt:
            appt.prep_sections_complete = sections_complete
            appt.prep_progress = len(sections_complete) * 25
            MCIP.set_advisor_appointment(appt)

        # Log completion
        log_event("advisor_prep.financial_section_complete", {"method": "data_inventory"})
