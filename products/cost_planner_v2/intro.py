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
    
    st.info("""
    **See what senior care costs in your area** — in less than 30 seconds.
    
    This quick calculator gives you ballpark costs based on:
    - ✅ Type of care needed
    - ✅ Your location (ZIP code)
    - ✅ Your specific care needs (if you've completed the Guided Care Plan)
    
    💡 **Sign in later** to get a detailed financial plan with personalized recommendations.
    """)
    
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
    
    st.success("### ✅ Your Quick Cost Estimate")
    
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
    
    # Cognitive-related adjustment (if applicable)
    if "cognitive_addon" in breakdown and breakdown["cognitive_addon"] > 0:
        st.markdown(f"**+ Cognitive-related Adjustment:** +20% (${breakdown['cognitive_addon']:,.0f})")
    
    # Mobility-related adjustment (if applicable)
    if "mobility_addon" in breakdown and breakdown["mobility_addon"] > 0:
        st.markdown(f"**+ Mobility-related Adjustment:** +15% (${breakdown['mobility_addon']:,.0f})")
    
    # High-acuity adjustment (if applicable - always for Memory Care High Acuity)
    if "high_acuity_addon" in breakdown and breakdown["high_acuity_addon"] > 0:
        st.markdown(f"**+ High-Acuity Adjustment:** +25% (${breakdown['high_acuity_addon']:,.0f})")
    
    # Show note if no add-ons
    has_addons = any(key in breakdown for key in ["cognitive_addon", "mobility_addon", "high_acuity_addon"])
    if not has_addons:
        st.caption("ℹ️ No additional care adjustments applied for your area.")
    
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
    
    # REASSURANCE COPY (per spec)
    st.info("""
    **We know these numbers can feel overwhelming. Don't worry — we'll help you plan how to cover these costs.**
    
    Our detailed Financial Assessment will show you:
    - ✅ All available funding sources (Medicare, VA benefits, insurance, etc.)
    - ✅ Gap analysis: what's covered vs. what you'll pay out-of-pocket
    - ✅ Strategies to reduce costs and maximize benefits
    - ✅ Facility comparison with real pricing data
    """)
    
    st.markdown("---")
    
    # CTA TO FULL ASSESSMENT (per spec)
    st.markdown("### 🎯 Continue to Full Assessment")
    
    st.markdown("""
    **Ready to get your personalized financial plan?**
    
    The Full Assessment will help you:
    - Understand exactly what care costs in your specific situation
    - Identify all funding sources you qualify for
    - Create a step-by-step plan to cover the costs
    - Get expert guidance on next steps
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("➡️ Continue to Full Assessment", type="primary", use_container_width=True, key="continue_full_assessment"):
            # Start authentication flow (if not logged in) then go to Full Assessment
            # For now, go to auth gate
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
