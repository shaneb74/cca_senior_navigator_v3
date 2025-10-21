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

from typing import Optional
import streamlit as st

from core.mcip import MCIP
from products.cost_planner_v2.utils import CostCalculator
from products.cost_planner_v2.utils.cost_calculator import CostEstimate


def render():
    """Render intro page with quick estimate."""

    st.title("💰 Cost Planner")
    st.markdown("### Get a Quick Cost Estimate")

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
    - Allow exploration of multiple scenarios
    """

    # CRITICAL: These are the ONLY 5 allowed care types
    ALLOWED_CARE_TYPES = [
        "No Care Recommended",
        "In-Home Care",
        "Assisted Living",
        "Memory Care",
        "Memory Care (High Acuity)",
    ]

    # Map display name to internal key
    care_type_map = {
        "No Care Recommended": "no_care_needed",
        "In-Home Care": "in_home_care",
        "Assisted Living": "assisted_living",
        "Memory Care": "memory_care",
        "Memory Care (High Acuity)": "memory_care_high_acuity",
    }

    # Reverse map for seeding from GCP
    tier_to_display = {v: k for k, v in care_type_map.items()}

    # Check if we have a GCP recommendation (seed selector, but don't show banner)
    default_index = 1  # Default to "In-Home Care"
    gcp_rec = MCIP.get_care_recommendation()
    has_gcp = gcp_rec and gcp_rec.tier

    if has_gcp:
        # Map GCP tier to display name and pre-select it
        gcp_display = tier_to_display.get(gcp_rec.tier)
        if gcp_display and gcp_display in ALLOWED_CARE_TYPES:
            default_index = ALLOWED_CARE_TYPES.index(gcp_display)

    st.markdown("#### 📍 Location")

    # ZIP code input (ZIP only - no State field per spec)
    zip_code = st.text_input(
        "ZIP Code",
        max_chars=5,
        placeholder="90210",
        help="Enter your 5-digit ZIP code for regional cost adjustment",
        key="cost_v2_quick_zip",
    )

    st.markdown("#### 🏥 Care Type")

    # Care type selection
    care_type = st.selectbox(
        "What type of care would you like to explore?",
        options=ALLOWED_CARE_TYPES,
        index=default_index,
        help="Start with our recommendation or explore different care scenarios",
        key="cost_v2_quick_care_type",
    )

    care_tier = care_type_map[care_type]

    # Calculate button and Back to Hub
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div data-role="primary">', unsafe_allow_html=True)
        if st.button(
            "🔍 Calculate Estimate",
            type="primary",
            use_container_width=True,
            key="calc_estimate_btn",
        ):
            _calculate_quick_estimate(care_tier, zip_code or None)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div data-role="secondary">', unsafe_allow_html=True)
        if st.button("← Back to Hub", use_container_width=True, key="intro_back_hub"):
            st.switch_page("pages/_stubs.py")
        st.markdown("</div>", unsafe_allow_html=True)


def _calculate_quick_estimate(care_tier: str, zip_code: Optional[str]):
    """Calculate and store quick estimate.

    Args:
        care_tier: Internal tier key (e.g., "memory_care")
        zip_code: 5-digit ZIP code (optional)
    """
    
    print(f"[QUICK_ESTIMATE] Button clicked - care_tier: {care_tier}, zip_code: {zip_code}")

    # Validate ZIP code
    if zip_code and len(zip_code) != 5:
        st.error("Please enter a valid 5-digit ZIP code, or leave it blank.")
        print(f"[QUICK_ESTIMATE] Invalid ZIP code: {zip_code}")
        return

    # Calculate estimate with line-item breakdown
    try:
        print(f"[QUICK_ESTIMATE] Calculating estimate...")
        estimate = CostCalculator.calculate_quick_estimate_with_breakdown(
            care_tier=care_tier, zip_code=zip_code
        )

        print(f"[QUICK_ESTIMATE] Estimate calculated: ${estimate.monthly_adjusted:,.2f}/month")
        
        st.session_state.cost_v2_quick_estimate = {
            "estimate": estimate.to_dict(),  # Convert to dict for JSON serialization
            "care_tier": care_tier,
            "zip_code": zip_code,
        }

        print(f"[QUICK_ESTIMATE] Estimate saved to session_state, triggering rerun...")
        st.rerun()

    except Exception as e:
        print(f"[QUICK_ESTIMATE] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        st.error(f"Error calculating estimate: {str(e)}")


def _render_quick_estimate_results():
    """Render quick estimate results with line-item breakdown.

    Simplified display - Navi provides context and explanations.
    """

    data = st.session_state.cost_v2_quick_estimate
    
    # Reconstruct CostEstimate from dict (for backward compatibility and persistence)
    estimate_data = data["estimate"]
    if isinstance(estimate_data, dict):
        estimate = CostEstimate.from_dict(estimate_data)
    else:
        # Legacy: already a CostEstimate object
        estimate = estimate_data

    st.markdown("### 📊 Your Cost Estimate")

    # Show care type and location (compact)
    care_type_display_map = {
        "no_care_needed": "No Care Recommended",
        "in_home_care": "In-Home Care",
        "assisted_living": "Assisted Living",
        "memory_care": "Memory Care",
        "memory_care_high_acuity": "Memory Care (High Acuity)",
    }
    care_type_display = care_type_display_map.get(
        estimate.care_tier, estimate.care_tier.replace("_", " ").title()
    )

    # Check if viewing different scenario than GCP recommendation
    gcp_rec = MCIP.get_care_recommendation()
    is_different_scenario = False
    if gcp_rec and gcp_rec.tier and gcp_rec.tier != estimate.care_tier:
        is_different_scenario = True
        gcp_recommended = care_type_display_map.get(gcp_rec.tier, gcp_rec.tier)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Care Type:** {care_type_display}")
        if is_different_scenario:
            st.caption(f"💡 Your GCP recommendation: {gcp_recommended}")
    with col2:
        st.markdown(f"**Location:** {estimate.region_name}")

    st.markdown("---")

    # LINE-ITEM BREAKDOWN
    st.markdown("#### Cost Breakdown")

    breakdown = estimate.breakdown

    # Base cost
    base_cost = breakdown.get("base_cost", 0)
    st.markdown(f"**Base Cost:** ${base_cost:,.0f}/mo")

    # Regional adjustment
    if estimate.multiplier != 1.0:
        regional_pct = int((estimate.multiplier - 1.0) * 100)
        regional_amount = breakdown.get("regional_adjustment", 0)
        if regional_pct > 0:
            st.markdown(f"**+ Regional Adjustment:** +{regional_pct}% (${regional_amount:,.0f})")
        else:
            st.markdown(f"**+ Regional Adjustment:** {regional_pct}% (${regional_amount:,.0f})")

    # CARE MULTIPLIERS (show only if present, no captions - Navi explains)

    if "severe_cognitive_addon" in breakdown and breakdown["severe_cognitive_addon"] > 0:
        st.markdown(
            f"**+ Severe Cognitive Impairment:** +20% (${breakdown['severe_cognitive_addon']:,.0f})"
        )

    if "mobility_transferring_addon" in breakdown and breakdown["mobility_transferring_addon"] > 0:
        st.markdown(
            f"**+ Mobility/Transferring Support:** +15% (${breakdown['mobility_transferring_addon']:,.0f})"
        )

    if "high_adl_support_addon" in breakdown and breakdown["high_adl_support_addon"] > 0:
        st.markdown(
            f"**+ Extensive ADL Assistance:** +10% (${breakdown['high_adl_support_addon']:,.0f})"
        )

    if "medication_management_addon" in breakdown and breakdown["medication_management_addon"] > 0:
        st.markdown(
            f"**+ Medication Management:** +8% (${breakdown['medication_management_addon']:,.0f})"
        )

    if "behavioral_care_addon" in breakdown and breakdown["behavioral_care_addon"] > 0:
        st.markdown(
            f"**+ Behavioral/Psychiatric Care:** +12% (${breakdown['behavioral_care_addon']:,.0f})"
        )

    if "fall_risk_monitoring_addon" in breakdown and breakdown["fall_risk_monitoring_addon"] > 0:
        st.markdown(
            f"**+ Fall Risk Monitoring:** +8% (${breakdown['fall_risk_monitoring_addon']:,.0f})"
        )

    if "chronic_conditions_addon" in breakdown and breakdown["chronic_conditions_addon"] > 0:
        st.markdown(
            f"**+ Chronic Conditions Management:** +10% (${breakdown['chronic_conditions_addon']:,.0f})"
        )

    if "high_acuity_intensive_addon" in breakdown and breakdown["high_acuity_intensive_addon"] > 0:
        st.markdown(
            f"**+ High-Acuity Intensive Care:** +25% (${breakdown['high_acuity_intensive_addon']:,.0f})"
        )

    st.markdown("---")

    # ADJUSTED TOTAL (prominent)
    st.markdown(f"### **Monthly Total: ${estimate.monthly_adjusted:,.0f}**")

    # Annual and 3-year projections (compact)
    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="Annual", value=f"${estimate.annual:,.0f}")

    with col2:
        st.metric(label="3-Year", value=f"${estimate.three_year:,.0f}")

    st.markdown("---")

    # Simplified CTA - Navi provides reassurance
    st.markdown("### Ready for Your Full Financial Plan?")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div data-role="primary">', unsafe_allow_html=True)
        if st.button(
            "➡️ Continue to Full Assessment",
            type="primary",
            use_container_width=True,
            key="continue_full_assessment",
        ):
            # Clear the step query parameter to prevent it from overriding our navigation
            if "step" in st.query_params:
                del st.query_params["step"]
            
            # Start authentication flow (if not logged in) then go to Full Assessment
            st.session_state.cost_v2_step = "auth"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div data-role="secondary">', unsafe_allow_html=True)
        if st.button("🔄 Calculate Another", use_container_width=True, key="recalculate"):
            # Clear results to allow recalculation
            st.session_state.cost_v2_quick_estimate = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


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
