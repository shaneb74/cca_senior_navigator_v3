from copy import deepcopy

import streamlit as st

DEFAULT_CTX = {
    "auth": {"is_authenticated": False, "user_id": None, "role": "guest"},
    "flags": {},
}


def ensure_session():
    if "ctx" not in st.session_state:
        st.session_state.ctx = deepcopy(DEFAULT_CTX)


def get_user_ctx():
    return st.session_state.ctx


def set_module_status(module_key: str, status: str):
    """Set the status of a module (e.g., 'done', 'in_progress')."""
    if "module_status" not in st.session_state:
        st.session_state.module_status = {}
    st.session_state.module_status[module_key] = status


def get_product_state(user_id: str, product_key: str) -> dict:
    """Get the state of a product."""
    # For now, return mock data; in production, this would query a database
    if product_key == "gcp":
        return {
            "status": "done",
            "progress": 100,
            "modules": ["intake", "daily_living", "cognition", "safety_support", "results"]
        }
    elif product_key == "cost_planner":
        return {
            "status": "doing",
            "progress": 62,
            "modules": ["quick_estimate", "income_assets", "housing_options", "va_benefits", "home_mods", "runway_projection"]
        }
    elif product_key == "pfma":
        return {
            "status": "new",
            "progress": 0,
            "modules": ["schedule", "verify_summary", "prep_questions"]
        }
    else:
        return {
            "status": "new",
            "progress": 0,
            "modules": []
        }


def get_module_state(user_id: str, product_key: str, module_key: str) -> dict:
    """Get the state of a module."""
    # Mock data; in production, query database
    if product_key == "gcp" and module_key == "results":
        return {
            "status": "done",
            "progress": 100,
            "outputs": [
                {"label": "Recommendation", "value": "In-Home Care"},
                {"label": "Notes", "value": "Mobility support recommended"}
            ],
            "completed_at": "2025-10-09T14:22:51Z"
        }
    elif product_key == "cost_planner" and module_key == "va_benefits":
        return {
            "status": "done",
            "progress": 100,
            "outputs": [
                {"label": "Aid & Attendance", "value": "Eligible"}
            ],
            "completed_at": "2025-10-09T15:00:00Z"
        }
    elif product_key == "cost_planner" and module_key == "quick_estimate":
        return {
            "status": "done",
            "progress": 100,
            "outputs": [
                {"label": "Est. monthly cost", "value": "$4,200"}
            ],
            "completed_at": "2025-10-09T15:00:00Z"
        }
    elif product_key == "cost_planner" and module_key == "income_assets":
        return {
            "status": "done",
            "progress": 100,
            "outputs": [
                {"label": "Monthly income", "value": "$3,500"},
                {"label": "Assets", "value": "$250,000"}
            ],
            "completed_at": "2025-10-09T15:00:00Z"
        }
    elif product_key == "cost_planner" and module_key == "runway_projection":
        return {
            "status": "done",
            "progress": 100,
            "outputs": [
                {"label": "Runway", "value": "3.8 years"}
            ],
            "completed_at": "2025-10-09T15:00:00Z"
        }
    else:
        return {
            "status": "new",
            "progress": 0,
            "outputs": [],
            "completed_at": None
        }
