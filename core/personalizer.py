"""
core/personalizer.py
Phase 5E - Dynamic Personalization Engine

Provides schema-driven personalization based on user tier, cognition band,
support level, and journey phase. Integrates with session_store for persistence.
"""

import json
import os
import streamlit as st

SCHEMA_PATH = os.path.join("config", "personalization_schema.json")

# --- Load schema once per session ---
@st.cache_data
def load_schema():
    with open(SCHEMA_PATH, "r") as f:
        return json.load(f)

# --- Merge rules by precedence ---
def get_user_context(uid=None, flags=None):
    schema = load_schema()

    # Get UID from parameter, session state, or anonymous
    if uid is None:
        uid = st.session_state.get("user_id") or st.session_state.get("anonymous_uid", "anonymous")
    
    # Phase 5E: Persist uid in session state for cross-navigation tracking
    if uid != "anonymous":
        st.session_state["_personalization_uid"] = uid

    # In a real app, this would pull from the user profile or DB
    user = st.session_state.get("user_profile", {
        "tier": "independent",
        "cognition_band": "a&o4",
        "support_band": "medium",
        "phase": "discovery",
        "is_repeat_user": False,
        "has_referral": False
    })

    ctx = dict(schema["defaults"])
    tier_rules = schema["tiers"].get(user["tier"], {})
    cognition_rules = schema["cognition_bands"].get(user["cognition_band"], {})
    support_rules = schema["support_bands"].get(user["support_band"], {})
    phase_rules = schema["phases"].get(user["phase"], {})

    # Merge by order of precedence
    for ruleset in (tier_rules, cognition_rules, support_rules, phase_rules):
        ctx.update(ruleset)

    # Merge flags if present
    if user.get("is_repeat_user"):
        ctx.update(schema["flags"]["is_repeat_user"])
    if user.get("has_referral"):
        ctx.update(schema["flags"]["has_referral"])

    ctx["uid"] = uid or st.session_state.get("uid", "anonymous")
    return ctx

# --- Apply personalization to UI components ---
def apply_to_header():
    ctx = get_user_context()
    st.markdown(f"### {ctx.get('navi_header_message', '')}")
    st.caption(ctx.get("header_text", ""))

def get_visible_modules():
    """Return combined list of modules for the current user context.
    
    Phase 5E Correction: Merges both modules_enabled (from tier) and 
    visible_modules (from phase) to ensure all planning tiles appear.
    
    Returns:
        List of module keys that should be visible in the current context
    """
    ctx = get_user_context()
    modules = set()

    # Add tier-based modules
    if "modules_enabled" in ctx:
        modules.update(ctx["modules_enabled"])
    
    # Add phase-based modules (ensures planning journey shows all 4 modules)
    if "visible_modules" in ctx:
        modules.update(ctx["visible_modules"])

    return list(modules)
