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
from products.advisor_prep.prefill import get_financial_prefill


def render():
    """Render Financial data inventory for advisor review."""
    _render_data_inventory()


def _render_data_inventory():
    """Display captured financial information in inventory format."""
    
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
    st.markdown(f"### {section_header('Financial Data Inventory')}")
    st.markdown(personalize("*Review what we know about {NAME_POS} financial situation and care funding.*"))

    # Get financial data from various sources
    financial_session_data = st.session_state.get("financial_assessment", {})
    advisor_prep_data = st.session_state.get("advisor_prep", {}).get("data", {}).get("financial", {})
    cost_planner_data = st.session_state.get("cost_planner_v2", {})
    
    # Get prefill data from Cost Planner / Financial Profile
    prefill_data = get_financial_prefill()
    
    # Combine data sources
    all_financial_data = {**financial_session_data, **advisor_prep_data}
    
    # Income and assets
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
        ("Monthly Income", f"${monthly_income:,.0f}" if monthly_income else "Not captured"),
        ("Total Assets", f"${total_assets:,.0f}" if total_assets else "Not captured"),
    ])
    
    # Insurance coverage
    insurance_coverage = (
        all_financial_data.get("insurance_coverage") or 
        prefill_data.get("insurance_coverage", [])
    )
    
    if insurance_coverage:
        insurance_display = ", ".join(insurance_coverage)
    else:
        insurance_display = "Not captured"
    
    _display_data_section("🛡️ Insurance Coverage", [
        ("Insurance Types", insurance_display),
        ("Coverage Count", f"{len(insurance_coverage)} types" if insurance_coverage else "No coverage data"),
    ])
    
    # Primary financial concerns
    primary_concern = (
        all_financial_data.get("primary_concern") or 
        prefill_data.get("primary_concern")
    )
    
    _display_data_section("⚠️ Financial Concerns", [
        ("Primary Concern", primary_concern if primary_concern else "Not captured"),
    ])
    
    # Cost Planner results (if available)
    if cost_planner_data:
        total_monthly_cost = cost_planner_data.get("total_monthly_cost")
        affordability_status = cost_planner_data.get("affordability_status")
        
        _display_data_section("📊 Cost Planning Results", [
            ("Estimated Monthly Cost", f"${total_monthly_cost:,.0f}" if total_monthly_cost else "Not calculated"),
            ("Affordability Status", affordability_status if affordability_status else "Not assessed"),
        ])
    
    # Show completion status
    if any([monthly_income, total_assets, insurance_coverage, primary_concern, cost_planner_data]):
        st.success("✓ Financial information captured")
        _mark_section_complete()
    else:
        st.info("No financial data captured yet.")

    # Show data sources info
    st.markdown("---")
    st.markdown("#### 📋 Data Sources")
    
    sources = []
    if prefill_data.get("monthly_income") or prefill_data.get("total_assets"):
        sources.append("Cost Planner assessments")
    if cost_planner_data:
        sources.append("Cost Planner calculations")
    if all_financial_data:
        sources.append("Direct advisor prep input")
    
    if sources:
        st.info(f"Data gathered from: {', '.join(sources)}")
    else:
        st.info("No financial data sources identified yet")

    # Render Navi panel for contextual guidance
    render_navi_panel()


def _display_data_section(title: str, data_items: list):
    """Display a section of data inventory.
    
    Args:
        title: Section title
        data_items: List of (field_name, value) tuples
    """
    st.markdown(f"#### {title}")
    
    for field_name, value in data_items:
        if value and value != "Not captured" and value != [] and value != "No coverage data" and value != "No financial data sources identified yet":
            status = "✅ Captured"
            value_display = f"**{value}**"
        else:
            status = "❌ Not Captured"
            value_display = "*No data*"
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.write(field_name)
        with col2:
            st.write(status)
        with col3:
            st.write(value_display)
    
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
        log_event("advisor_prep", "financial_section_complete", {"method": "data_inventory"})
