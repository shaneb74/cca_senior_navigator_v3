import streamlit as st

from core.nav import PRODUCTS
from core.state import get_product_state, get_user_ctx
from core.ui import hub_section, render_hub_tile
from core.gcp_data import evaluate


def render():
    ctx = get_user_ctx()
    user_id = ctx["auth"].get("user_id", "guest")
    
    # Import the theme CSS
    st.markdown(
        "<link rel='stylesheet' href='/assets/css/theme.css'>",
        unsafe_allow_html=True
    )
    
    # Apply canvas background like welcome pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    # Main content container
    st.markdown('<section class="container section">', unsafe_allow_html=True)
    
    # Hero section with title
    st.markdown(
        f"""
        <div class="text-center" style="margin-bottom: var(--space-10);">
            <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
                Concierge Care Hub
            </h1>
            <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
                Your personalized dashboard for senior care planning and guidance.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Hub tiles grid
    st.markdown('<div class="tiles-2x2">', unsafe_allow_html=True)

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
                    
                render_hub_tile(
                    title="Guided Care Plan",
                    badge="Guided Care Plan",
                    label=label,
                    value=value,
                    status=status,
                    primary_label=primary_label
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
                
                render_hub_tile(
                    title="Plan with My Advisor",
                    badge="Plan with My Advisor",
                    label=label,
                    value=value,
                    status=status,
                    primary_label=primary_label
                )

    # Add FAQs & Answers tile
    render_hub_tile(
        title="FAQs & Answers",
        badge="FAQ",
        label="Common Questions",
        value="25 topics",
        status="new",
        primary_label="Search FAQs",
        secondary_label="Contact support"
    )

    # Close the tiles grid and section
    st.markdown('</div></section>', unsafe_allow_html=True)
