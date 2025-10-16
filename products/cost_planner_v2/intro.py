"""
Cost Planner v2 - Intro Page (Quick Estimate)

Unauthenticated quick estimate calculator.
Allows anonymous users to get a ballpark cost estimate before creating an account.

Spec:
- ZIP only (no State field)
- 5 care types only: No Care Recommended, In-Home Care, Assisted Living, Memory Care, Memory Care (High Acuity)
- Seed with GCP recommendation when available
- Line-item breakdown: base cost, regional %, condition add-ons, total
- Reassurance copy + CTA to Full Assessment

Workflow:
1. Welcome message
2. Quick estimate form (care type + ZIP)
3. Show line-item breakdown
4. Reassurance copy
5. CTA → Full Assessment (authentication)
"""

import streamlit as st
from typing import Optional, Dict, Any
from products.cost_planner_v2.utils import CostCalculator
from core.mcip import MCIP


def render():
    """Render intro page with quick estimate."""
    
    st.title("💰 Cost Planner")
    st.markdown("### Get a Quick Cost Estimate")
    
    # Simplified intro - Navi handles the guidance
    st.markdown("See what senior care costs in your area based on your needs and location.")
    
    st.markdown("---")
    
    # Initialize session state for quick estimate
    if "cost_v2_quick_estimate" not in st.session_state:
        st.session_state.cost_v2_quick_estimate = None
    
    # Quick estimate form
    _render_quick_estimate_form()
    
    # Show results if calculated
    if st.session_state.cost_v2_quick_estimate:
        st.markdown("---")
        _render_quick_estimate_results()


def _render_quick_estimate_form():
    """Render quick estimate input form.
    
    Spec:
    - ZIP only (no State field)
    - 5 care types only
    - Seed with GCP recommendation if available
    """
    
    st.markdown("#### 📝 Tell us about your needs:")
    
    # CRITICAL: These are the ONLY 5 allowed care types
    ALLOWED_CARE_TYPES = [
        "No Care Recommended",
        "In-Home Care",
        "Assisted Living",
        "Memory Care",
        "Memory Care (High Acuity)"
    ]
    
    # Map display name to internal key
    care_type_map = {
        "No Care Recommended": "no_care_needed",
        "In-Home Care": "in_home_care",
        "Assisted Living": "assisted_living",
        "Memory Care": "memory_care",
        "Memory Care (High Acuity)": "memory_care_high_acuity"
    }
    
    # Reverse map for seeding from GCP
    tier_to_display = {v: k for k, v in care_type_map.items()}
    
    # Check if we have a GCP recommendation to seed the selector
    default_index = 1  # Default to "In-Home Care"
    gcp_rec = MCIP.get_care_recommendation()
    if gcp_rec and gcp_rec.tier:
        # Map GCP tier to display name
        gcp_display = tier_to_display.get(gcp_rec.tier)
        if gcp_display and gcp_display in ALLOWED_CARE_TYPES:
            default_index = ALLOWED_CARE_TYPES.index(gcp_display)
            st.caption(f"💡 Based on your Guided Care Plan, we've pre-selected: **{gcp_display}**")
    
    # Care type selection
    care_type = st.selectbox(
        "What type of care are you exploring?",
        options=ALLOWED_CARE_TYPES,
        index=default_index,
        help="Choose the care option that best matches your current needs. Switch to preview costs for different scenarios.",
        key="cost_v2_quick_care_type"
    )
    
    care_tier = care_type_map[care_type]
    
    # ZIP code input (ZIP only - no State field per spec)
    zip_code = st.text_input(
        "ZIP Code",
        max_chars=5,
        placeholder="90210",
        help="Enter your 5-digit ZIP code for regional cost adjustment",
        key="cost_v2_quick_zip"
    )
    
    # Calculate button
    if st.button("🔍 Calculate Quick Estimate", type="primary", use_container_width=True):
        _calculate_quick_estimate(care_tier, zip_code or None)


def _calculate_quick_estimate(care_tier: str, zip_code: Optional[str]):
    """Calculate and store quick estimate.
    
    Args:
        care_tier: Internal tier key (e.g., "memory_care")
        zip_code: 5-digit ZIP code (optional)
    """
    
    # Validate ZIP code
    if zip_code and len(zip_code) != 5:
        st.error("Please enter a valid 5-digit ZIP code, or leave it blank.")
        return
    
    # Calculate estimate with line-item breakdown
    try:
        estimate = CostCalculator.calculate_quick_estimate_with_breakdown(
            care_tier=care_tier,
            zip_code=zip_code
        )
        
        st.session_state.cost_v2_quick_estimate = {
            "estimate": estimate,
            "care_tier": care_tier,
            "zip_code": zip_code
        }
        
        st.rerun()
        
    except Exception as e:
        st.error(f"Error calculating estimate: {str(e)}")


def _render_quick_estimate_results():
    """Render quick estimate results with line-item breakdown.
    
    Spec:
    - Show line-item breakdown: base cost, regional %, condition add-ons, total
    - Reassurance copy
    - CTA to Full Assessment
    """
    
    data = st.session_state.cost_v2_quick_estimate
    estimate = data["estimate"]
    
    st.markdown("### 📊 Your Quick Cost Estimate")
    
    # Show care type and location
    care_type_display_map = {
        "no_care_needed": "No Care Recommended",
        "in_home_care": "In-Home Care",
        "assisted_living": "Assisted Living",
        "memory_care": "Memory Care",
        "memory_care_high_acuity": "Memory Care (High Acuity)"
    }
    care_type_display = care_type_display_map.get(estimate.care_tier, estimate.care_tier.replace("_", " ").title())
    
    st.markdown(f"""
    **Care Type:** {care_type_display}  
    **Location:** {estimate.region_name}
    """)
    
    st.markdown("---")
    
    # LINE-ITEM BREAKDOWN (per spec)
    st.markdown("#### 📊 Cost Breakdown")
    
    # Use breakdown dict from estimate
    breakdown = estimate.breakdown
    
    # Base cost
    base_cost = breakdown.get("base_cost", 0)
    st.markdown(f"**Base Cost ({care_type_display}):** ${base_cost:,.0f} / month")
    
    # Regional adjustment
    if estimate.multiplier != 1.0:
        regional_pct = int((estimate.multiplier - 1.0) * 100)
        regional_amount = breakdown.get("regional_adjustment", 0)
        if regional_pct > 0:
            st.markdown(f"**+ Regional Adjustment (ZIP {data['zip_code'] or 'N/A'}):** +{regional_pct}% (${regional_amount:,.0f})")
        else:
            st.markdown(f"**+ Regional Adjustment (ZIP {data['zip_code'] or 'N/A'}):** {regional_pct}% (${regional_amount:,.0f})")
    else:
        st.markdown(f"**+ Regional Adjustment (ZIP {data['zip_code'] or 'N/A'}):** National Average (no adjustment)")
    
    # CARE MULTIPLIERS (show only if present)
    
    # Severe cognitive impairment (+20%)
    if "severe_cognitive_addon" in breakdown and breakdown["severe_cognitive_addon"] > 0:
        st.markdown(f"**+ Severe Cognitive Impairment:** +20% (${breakdown['severe_cognitive_addon']:,.0f})")
        st.caption("   ↳ Specialized memory care for Alzheimer's/dementia")
    
    # Serious mobility/transferring (+15%)
    if "mobility_transferring_addon" in breakdown and breakdown["mobility_transferring_addon"] > 0:
        st.markdown(f"**+ Mobility/Transferring Support:** +15% (${breakdown['mobility_transferring_addon']:,.0f})")
        st.caption("   ↳ Wheelchair/bedbound care with lifting assistance")
    
    # High-level ADL support (+10%)
    if "high_adl_support_addon" in breakdown and breakdown["high_adl_support_addon"] > 0:
        st.markdown(f"**+ Extensive ADL Assistance:** +10% (${breakdown['high_adl_support_addon']:,.0f})")
        st.caption("   ↳ Help with bathing, dressing, eating, toileting")
    
    # Complex medication management (+8%)
    if "medication_management_addon" in breakdown and breakdown["medication_management_addon"] > 0:
        st.markdown(f"**+ Medication Management:** +8% (${breakdown['medication_management_addon']:,.0f})")
        st.caption("   ↳ Complex prescriptions requiring professional oversight")
    
    # Behavioral/psychiatric care (+12%)
    if "behavioral_care_addon" in breakdown and breakdown["behavioral_care_addon"] > 0:
        st.markdown(f"**+ Behavioral/Psychiatric Care:** +12% (${breakdown['behavioral_care_addon']:,.0f})")
        st.caption("   ↳ Wandering, aggression, specialized behavioral support")
    
    # Fall risk/safety monitoring (+8%)
    if "fall_risk_monitoring_addon" in breakdown and breakdown["fall_risk_monitoring_addon"] > 0:
        st.markdown(f"**+ Fall Risk Monitoring:** +8% (${breakdown['fall_risk_monitoring_addon']:,.0f})")
        st.caption("   ↳ Enhanced supervision and safety measures")
    
    # Multiple chronic conditions (+10%)
    if "chronic_conditions_addon" in breakdown and breakdown["chronic_conditions_addon"] > 0:
        st.markdown(f"**+ Chronic Conditions Management:** +10% (${breakdown['chronic_conditions_addon']:,.0f})")
        st.caption("   ↳ Coordinated care for multiple health conditions")
    
    # High-acuity intensive care (+25%)
    if "high_acuity_intensive_addon" in breakdown and breakdown["high_acuity_intensive_addon"] > 0:
        st.markdown(f"**+ High-Acuity Intensive Care:** +25% (${breakdown['high_acuity_intensive_addon']:,.0f})")
        st.caption("   ↳ 24/7 skilled nursing and advanced medical support")
    
    # Show note if no care multipliers applied
    has_care_addons = any(key in breakdown for key in [
        "severe_cognitive_addon", "mobility_transferring_addon", "high_adl_support_addon",
        "medication_management_addon", "behavioral_care_addon", "fall_risk_monitoring_addon",
        "chronic_conditions_addon", "high_acuity_intensive_addon"
    ])
    if not has_care_addons:
        st.caption("ℹ️ No additional care adjustments applied based on your assessment.")
    
    st.markdown("---")
    
    # ADJUSTED TOTAL
    st.markdown(f"### **= Adjusted Total: ${estimate.monthly_adjusted:,.0f} / month**")
    
    st.markdown("---")
    
    # Annual and 3-year projections
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="Annual Cost",
            value=f"${estimate.annual:,.0f}",
            help="Estimated annual cost (monthly × 12)"
        )
    
    with col2:
        st.metric(
            label="3-Year Projection",
            value=f"${estimate.three_year:,.0f}",
            help="Estimated 3-year cost (annual × 3)"
        )
    
    st.markdown("---")
    
    # Simplified CTA - let Navi handle the messaging
    st.markdown("### Ready for Your Full Financial Plan?")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("➡️ Continue to Full Assessment", type="primary", use_container_width=True, key="continue_full_assessment"):
            # Start authentication flow (if not logged in) then go to Full Assessment
            st.session_state.cost_v2_step = "auth"
            st.rerun()
    
    with col2:
        if st.button("🏠 Return to Hub", use_container_width=True, key="quick_estimate_hub"):
            from core.nav import route_to
            route_to("hub_concierge")


def _render_auth_gate():
    """Render authentication gate.
    
    Users must authenticate to access detailed financial planning.
    This is the mandatory workflow step after quick estimate.
    """
    
    st.title("🔐 Sign In Required")
    
    st.info("""
    ### Create Your Free Account
    
    To access the detailed Cost Planner, you'll need to sign in or create a free account.
    
    **Why sign in?**
    - 💾 Save your progress automatically
    - 📊 Access personalized recommendations
    - 🔒 Keep your financial data secure
    - 📧 Get expert guidance and updates
    """)
    
    # Placeholder for auth buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📧 Sign In with Email", type="primary", use_container_width=True):
            st.info("🚧 Email authentication coming soon")
    
    with col2:
        if st.button("🔗 Sign In with Google", use_container_width=True):
            st.info("🚧 Google OAuth coming soon")
    
    st.markdown("---")
    
    if st.button("← Back to Quick Estimate", key="auth_back"):
        st.session_state.cost_v2_step = "intro"
        st.rerun()
