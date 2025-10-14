"""
Cost Planner v2 Product Router

Demonstrates universal product interface:
- Check prerequisites via MCIP (not direct state reads)
- Show friendly gate if prerequisites missing
- Orchestrate modules when prerequisites met
- Publish output to MCIP when complete

Uses Navi as the single intelligence layer for guidance and progress.
"""

import streamlit as st
from core.mcip import MCIP
from core.navi import render_navi_panel


def render():
    """Render Cost Planner v2 with MCIP gate.
    
    Universal Product Interface Implementation:
    1. Check prerequisites via MCIP
    2. Show gate if prerequisites missing (with Navi guidance)
    3. Run product logic (module hub) when gate passes
    4. Publish to MCIP when complete
    5. Show completion screen
    """
    
    # STEP 1: Check prerequisites via MCIP
    # This demonstrates clean boundaries - we read from MCIP, not from gcp state
    recommendation = MCIP.get_care_recommendation()
    
    if not recommendation:
        # Gate: Prerequisites not met
        # Render Navi for gate screen (shows journey status and next action)
        render_navi_panel(
            location="product",
            product_key="cost_v2",
            module_config=None  # No module config for gate screen
        )
        _render_gcp_gate()
        return
    
    # STEP 2: Gate passed - run product logic
    # Pass recommendation to hub (no direct state access)
    from products.cost_planner_v2.hub import render_module_hub
    render_module_hub(recommendation)


def _render_gcp_gate():
    """Show friendly gate requiring GCP completion.
    
    This is the universal pattern for prerequisites:
    - Clear explanation of why gate exists
    - Friendly messaging (not just "locked")
    - Direct path forward (button to start prerequisite)
    - Return to hub option
    """
    
    st.title("💰 Financial Planning")
    
    st.info("### 💡 Complete Your Guided Care Plan First")
    
    st.markdown("""
    Before we can calculate costs, we need to know what level of care is recommended.
    
    The **Guided Care Plan** takes just 2 minutes and will:
    - ✅ Assess daily living needs
    - ✅ Evaluate safety and cognitive factors  
    - ✅ Recommend the right care level
    - ✅ Unlock personalized cost estimates
    
    ---
    
    **Why this matters:** Different care levels (in-home care, assisted living, memory care) 
    have vastly different costs. Your personalized recommendation ensures accurate estimates.
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🎯 Start Guided Care Plan", type="primary", use_container_width=True, key="gate_start_gcp"):
            from core.nav import route_to
            route_to("gcp_v4")
    
    with col2:
        if st.button("🏠 Return to Hub", use_container_width=True, key="gate_return_hub"):
            from core.nav import route_to
            route_to("hub_concierge")
    
    # Optional: Show what user will get after completing GCP
    with st.expander("📊 What you'll see after completing the Guided Care Plan"):
        st.markdown("""
        Once you complete the Guided Care Plan, you'll unlock:
        
        1. **Base Care Costs** - Monthly costs for your recommended care level
        2. **Care Hours Calculator** - Cost of hourly care (if applicable)
        3. **Additional Services** - Therapy, transportation, activities
        4. **Veteran Benefits** - Calculate VA Aid & Attendance eligibility
        5. **Insurance & Medicare** - Apply coverage to reduce out-of-pocket
        6. **Facility Selection** - Compare specific facilities in your area
        
        We'll give you:
        - 💰 **Monthly cost breakdown**
        - 📊 **3-year and 5-year projections**
        - 💳 **Funding sources and gap analysis**
        - 📍 **Regional cost comparisons**
        """)
