"""
Cost Planner v2 - Monthly Costs Module

Calculates detailed monthly care costs based on:
- Base care cost (from GCP tier)
- Regional adjustments
- Additional services
- Care hours (if applicable)

Returns standard contract for aggregation.
"""

import streamlit as st
from typing import Dict, Any
from core.mcip import MCIP
from products.cost_planner_v2.utils import CostCalculator


def render():
    """Render monthly costs assessment module."""
    
    st.title("💰 Monthly Costs Breakdown")
    st.markdown("### Detailed care cost calculation")
    
    # Get context from MCIP
    recommendation = MCIP.get_care_recommendation()
    triage = st.session_state.get("cost_v2_triage", {})
    
    if not recommendation:
        st.error("❌ No care recommendation found. Please complete Guided Care Plan first.")
        return
    
    tier = recommendation.tier
    tier_display = tier.replace("_", " ").title()
    
    st.info(f"📋 **Calculating costs for:** {tier_display}")
    
    st.markdown("---")
    
    # Initialize module state
    if "cost_v2_monthly_costs" not in st.session_state:
        st.session_state.cost_v2_monthly_costs = {
            "zip_code": triage.get("location", "").split(",")[-1].strip() if triage.get("location") else "",
            "care_hours_per_week": 0,
            "additional_services": {}
        }
    
    # Base Care Cost
    st.markdown("## 🏥 Base Care Cost")
    
    # Get base cost from config
    base_costs = {
        "independent": 0,
        "in_home": 3500,
        "assisted_living": 4500,
        "memory_care": 6500
    }
    
    base_cost = base_costs.get(tier, 3500)
    
    st.metric("Base Monthly Cost", f"${base_cost:,.0f}", help=f"National average for {tier_display}")
    
    st.markdown("---")
    
    # Regional Adjustment
    st.markdown("## 📍 Regional Cost Adjustment")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        zip_code = st.text_input(
            "ZIP Code",
            value=st.session_state.cost_v2_monthly_costs.get("zip_code", ""),
            max_chars=5,
            placeholder="90210",
            help="Enter ZIP code for regional cost adjustment",
            key="monthly_zip"
        )
    
    # Calculate regional multiplier
    from products.cost_planner_v2.utils import RegionalDataProvider
    regional = RegionalDataProvider.get_multiplier(zip_code=zip_code if zip_code else None)
    
    with col2:
        multiplier_pct = int((regional.multiplier - 1.0) * 100)
        if multiplier_pct > 0:
            st.metric("Regional Adjustment", f"+{multiplier_pct}%", delta=f"Above average")
        elif multiplier_pct < 0:
            st.metric("Regional Adjustment", f"{multiplier_pct}%", delta=f"Below average")
        else:
            st.metric("Regional Adjustment", "0%", delta="National average")
    
    adjusted_base = base_cost * regional.multiplier
    
    st.caption(f"ℹ️ **Location:** {regional.region_name}")
    st.metric("Adjusted Base Cost", f"${adjusted_base:,.0f}")
    
    st.markdown("---")
    
    # Care Hours (for in-home care)
    if tier == "in_home":
        st.markdown("## ⏰ Care Hours")
        
        care_hours = st.slider(
            "Weekly Care Hours",
            min_value=0,
            max_value=168,
            value=st.session_state.cost_v2_monthly_costs.get("care_hours_per_week", 20),
            step=1,
            help="Number of hours of professional care per week",
            key="care_hours"
        )
        
        hourly_rate = 25 * regional.multiplier
        monthly_hours = care_hours * 4.33  # weeks per month
        monthly_care_cost = hourly_rate * monthly_hours
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Hourly Rate", f"${hourly_rate:.0f}")
        with col2:
            st.metric("Monthly Hours", f"{monthly_hours:.0f}")
        with col3:
            st.metric("Monthly Care Cost", f"${monthly_care_cost:,.0f}")
        
        st.markdown("---")
    else:
        care_hours = 0
        monthly_care_cost = 0
    
    # Additional Services
    st.markdown("## 🎯 Additional Services")
    
    st.caption("Select services that apply (costs vary by tier and region)")
    
    services_config = {
        "transportation": {"label": "Medical Transportation", "cost": 200},
        "therapy": {"label": "Physical/Occupational Therapy", "cost": 300},
        "activities": {"label": "Social Activities & Programs", "cost": 150},
        "meals": {"label": "Meal Delivery Service", "cost": 250},
        "housekeeping": {"label": "Housekeeping & Laundry", "cost": 200},
        "medication": {"label": "Medication Management", "cost": 100},
        "personal_care": {"label": "Additional Personal Care", "cost": 350}
    }
    
    additional_services = {}
    additional_total = 0
    
    for service_key, service_info in services_config.items():
        enabled = st.checkbox(
            f"{service_info['label']} (+${service_info['cost'] * regional.multiplier:,.0f}/mo)",
            value=st.session_state.cost_v2_monthly_costs.get("additional_services", {}).get(service_key, False),
            key=f"service_{service_key}"
        )
        additional_services[service_key] = enabled
        
        if enabled:
            additional_total += service_info['cost'] * regional.multiplier
    
    st.metric("Additional Services Total", f"${additional_total:,.0f}")
    
    st.markdown("---")
    
    # Total Monthly Cost Summary
    st.markdown("## 📊 Total Monthly Cost")
    
    if tier == "in_home":
        total_monthly = adjusted_base + monthly_care_cost + additional_total
    else:
        total_monthly = adjusted_base + additional_total
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Base Care", f"${adjusted_base:,.0f}")
    
    with col2:
        if tier == "in_home":
            st.metric("Care Hours", f"${monthly_care_cost:,.0f}")
        else:
            st.metric("Care Hours", "N/A")
    
    with col3:
        st.metric("Services", f"${additional_total:,.0f}")
    
    with col4:
        st.metric("**Total**", f"**${total_monthly:,.0f}**")
    
    # Annual projection
    annual_cost = total_monthly * 12
    st.caption(f"📅 **Annual Cost:** ${annual_cost:,.0f}")
    
    st.markdown("---")
    
    # Navigation
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("← Back to Hub", key="monthly_back"):
            st.session_state.cost_v2_step = "modules"
            st.rerun()
    
    with col2:
        if st.button("Save & Continue →", type="primary", use_container_width=True, key="monthly_save"):
            # Save data
            data = {
                "care_tier": tier,
                "zip_code": zip_code,
                "regional_multiplier": regional.multiplier,
                "region_name": regional.region_name,
                "base_care_cost": adjusted_base,
                "care_hours_per_week": care_hours,
                "monthly_care_cost": monthly_care_cost if tier == "in_home" else 0,
                "additional_services": additional_services,
                "additional_services_cost": additional_total,
                "total_monthly_cost": total_monthly,
                "annual_cost": annual_cost
            }
            
            # Update session state
            st.session_state.cost_v2_monthly_costs = data
            
            # Mark module complete
            st.session_state.cost_v2_modules["monthly_costs"] = {
                "status": "completed",
                "progress": 100,
                "data": data
            }
            
            # Return to hub
            st.session_state.cost_v2_step = "modules"
            st.success("✅ Monthly costs saved!")
            st.rerun()
    
    st.caption("💾 Your progress is automatically saved")
