import streamlit as st

from core.nav import PRODUCTS
from core.state import get_product_state, get_user_ctx
from core.ui import hub_section, render_hub_tile
from core.gcp_data import evaluate


def render():
    ctx = get_user_ctx()
    user_id = ctx["auth"].get("user_id", "guest")
    
    # Import the hub grid CSS
    st.markdown(
        "<link rel='stylesheet' href='/assets/css/theme.css'>"
        "<link rel='stylesheet' href='/assets/css/hub_grid.css'>",
        unsafe_allow_html=True
    )
    
    # Wrap the entire hub content
    st.markdown('<section class="hub-page">', unsafe_allow_html=True)
    st.markdown('<h1 class="text-center" style="margin: 16px 0 32px; font-size: 2rem; font-weight: 700; color: #0f172a;">Concierge Care Hub</h1>', unsafe_allow_html=True)
    
    # Start the hub grid
    st.markdown('<div class="hub-grid">', unsafe_allow_html=True)

    # Render hub tiles for each product
    for product_key in ["gcp", "cost_planner", "pfma"]:
        if PRODUCTS[product_key]["hub"] == "concierge":
            state = get_product_state(user_id, product_key)
            
            if product_key == "gcp":
                # Get GCP recommendation if completed
                answers = st.session_state.get("gcp_answers", {})
                if answers:
                    try:
                        result = evaluate(answers)
                        label = "Recommendation"
                        value = result["tier"]
                        status = "done"
                        primary_label = "See responses"
                        secondary_label = "Start over"
                    except:
                        label = "Status"
                        value = "In progress"
                        status = "doing"
                        primary_label = "Continue"
                        secondary_label = "Start over"
                else:
                    label = "Status"
                    value = "Not started"
                    status = "new"
                    primary_label = "Get started"
                    secondary_label = "Learn more"
                    
                render_hub_tile(
                    title="Guided Care Plan",
                    badge="Guided Care Plan",
                    label=label,
                    value=value,
                    status=status,
                    primary_label=primary_label,
                    secondary_label=secondary_label
                )
                
            elif product_key == "cost_planner":
                # Mock cost planner data - in real implementation, get from state
                label = "Monthly Gap"
                value = "$382"
                status = "doing"
                primary_label = "Continue"
                secondary_label = "Review"
                
                render_hub_tile(
                    title="Cost Planner",
                    badge="Cost Planner",
                    label=label,
                    value=value,
                    status=status,
                    primary_label=primary_label,
                    secondary_label=secondary_label
                )
                
            elif product_key == "pfma":
                # Mock PFMA data - in real implementation, get from state
                label = "Next Step"
                value = "Awaiting Appointment"
                status = "new"
                primary_label = "Get connected"
                secondary_label = "Learn more"
                
                render_hub_tile(
                    title="Plan with My Advisor",
                    badge="Plan with My Advisor",
                    label=label,
                    value=value,
                    status=status,
                    primary_label=primary_label,
                    secondary_label=secondary_label
                )

    # Close the hub grid and page wrapper
    st.markdown('</div></section>', unsafe_allow_html=True)
