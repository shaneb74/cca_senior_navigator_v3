import streamlit as st
from core.nav import route_to
from core.state import get_user_ctx
from core.gcp_data import evaluate
from core.base_hub import BaseHub
from core.product_tile import ProductTile
from core.ui import tiles_open, tiles_close


class ConciergeHub(BaseHub):
    def __init__(self):
        super().__init__(
            title="Concierge Care Hub",
            icon="🏠",
            description="Your personalized dashboard for senior care planning and guidance."
        )

    def render_content(self):
        # Get dynamic data
        person_name = st.session_state.get("person_name", "John")
        gcp_answers = st.session_state.get("gcp_answers", {})
        gcp_completed = bool(gcp_answers)
        gcp_recommendation = ""
        if gcp_completed:
            try:
                result = evaluate(gcp_answers)
                gcp_recommendation = f"Summary: Recommended {result['tier']}"
            except:
                gcp_recommendation = "Summary: Assessment in progress"

        # Create product tiles
        products = []

        # Guided Care Plan
        products.append(ProductTile(
            title="Guided Care Plan",
            icon_path="downward-arrow.png",
            pre_start_text="Begin here to find your best senior care living options.",
            in_progress_text="Continue your assessment...",
            post_complete_text=gcp_recommendation if gcp_completed else "Summary: Assessment completed",
            buttons=[{"text": "Start", "callback": lambda t="Guided Care Plan": st.session_state.update({"current_tile": t})}] if not gcp_completed else [{"text": "See responses", "callback": lambda: route_to("gcp")}, {"text": "Start over", "callback": lambda: st.session_state.update({"gcp_answers": {}})}, {"text": "✓ Completed", "callback": lambda: route_to("gcp")}],
            order=1,
            progress=100 if gcp_completed else 0,
            workflow_type='assessment',
            workflow_config=[
                {"id": 1, "label": "What is your relationship to the person needing care?", "type": "radio", "options": ["self", "someone_else"], "required": True},
                {"id": 2, "label": "What is your age range?", "type": "radio", "options": ["under_65", "65_74", "75_84", "85_plus"], "required": True},
                {"id": 3, "label": "What is the age range of the person needing care?", "type": "radio", "options": ["under_65", "65_74", "75_84", "85_plus"], "required": True},
                {"id": 4, "label": "What type of care setting are you considering?", "type": "radio", "options": ["in_home", "assisted_living", "memory_care"], "required": True},
                {"id": 5, "label": "What is your monthly budget for care?", "type": "slider", "min": 1000, "max": 10000, "required": True},
                {"id": 6, "label": "Do you have any chronic conditions?", "type": "pill_list", "required": False}
            ]
        ))

        # Cost Planner (top-level)
        cost_completed = st.session_state.get("cost_planner_completed", False)
        products.append(ProductTile(
            title="Cost Planner",
            icon_path="calculator.png",
            pre_start_text="Estimate reliable monthly costs—project how long your savings will last.",
            in_progress_text="Working on your financial timeline...",
            post_complete_text="Summary: Cost of care timeline available",
            buttons=[{"text": "Continue", "callback": lambda: route_to("cost_planner")}, {"text": "⭐ Next step", "callback": lambda: route_to("cost_planner")}] if cost_completed else [{"text": "Start", "callback": lambda: route_to("cost_planner")}, {"text": "⭐ Next step", "callback": lambda: route_to("cost_planner")}],
            order=2,
            prereq="Guided Care Plan",
            progress=100 if cost_completed else 0
        ))

        # Plan With My Advisor
        appointment_time = st.session_state.get("appointment_time", "")
        products.append(ProductTile(
            title="Plan With My Advisor",
            icon_path="phone.png",
            pre_start_text="Schedule a one-on-one with your advisor.",
            in_progress_text="Scheduling appointment...",
            post_complete_text="Appointment scheduled",
            buttons=[
                {"text": "Get connected", "callback": lambda: route_to("pfma")},
                {"text": "↻ Start from scratch", "callback": lambda: st.session_state.update({"appointment_time": ""})}
            ],
            order=3
        ))

        # FAQs & Answers
        products.append(ProductTile(
            title="FAQs & Answers",
            icon_path="robot.png",
            pre_start_text="Receive instant, tailored assistance from our advanced AI chat.",
            in_progress_text="Chatting with AI assistant...",
            post_complete_text="Questions answered",
            buttons=[{"text": "Open", "callback": lambda: route_to("faqs")}],
            order=4
        ))

        # Filter to only top-level products
        top_level_products = [p for p in products if not p.parent_product]

        # Render products
        tiles_open()

        # Render top-level products
        for product in top_level_products:
            product.render("concierge_state", top_level_products)

        tiles_close()

        # Additional Services Section (keep as is for now)
        st.markdown(
            """
            <div class="additional-services">
                <h3 class="services-title">Trusted partners</h3>
                <div class="service-cards">
                    <div class="service-card">
                        <div class="service-icon">💙✓</div>
                        <div class="service-content">
                            <h4>Senior Life AI</h4>
                            <p>Get insights about """ + f"{person_name}'s overall body health</p>" + """
                        </div>
                        <button class="btn btn-blue" style="width: 80px; height: 30px;">Open</button>
                    </div>
                    <div class="service-card">
                        <div class="service-icon">📚</div>
                        <div class="service-content">
                            <h4>Learning Center</h4>
                            <p>Media Center</p>
                        </div>
                        <button class="btn btn-blue" style="width: 80px; height: 30px;">Open</button>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render():
    hub = ConciergeHub()
    hub.render()
