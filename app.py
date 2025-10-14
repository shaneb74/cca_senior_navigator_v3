import streamlit as st

from core.events import log_event
from core.nav import current_route, load_nav
from core.state import ensure_session, get_user_ctx
from core.ui import page_container_close, page_container_open
from layout import reset_global_frame

# Session persistence
from core.session_store import (
    get_or_create_user_id,
    load_session,
    save_session,
    load_user,
    save_user,
    extract_session_state,
    extract_user_state,
    merge_into_state,
    cleanup_old_sessions,
)

# Development utilities
from products.cost_planner.dev_unlock import show_dev_controls

st.set_page_config(page_title="Senior Navigator", page_icon="🧭", layout="wide")


def _sanitize_query_params_for_welcome(current_route: str) -> None:
    if current_route not in ("welcome", "welcome_contextual"):
        return

    qp = dict(st.query_params)
    dirty = False
    for key in list(qp.keys()):
        if key == "page" and qp.get(key) in ("login", "signup", "render_signup"):
            qp.pop(key, None)
            dirty = True

    if not dirty:
        return

    st.query_params.clear()
    for key, value in qp.items():
        st.query_params[key] = value


def inject_css():
    """Load global CSS and module-specific CSS."""
    try:
        # Load global CSS
        with open("assets/css/global.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
        # Load module CSS (must come after global to override)
        with open("assets/css/modules.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    except FileNotFoundError:
        # no-op on Cloud if path differs; don't crash
        pass


def _cleanup_legacy_gcp_state() -> None:
    legacy_keys = [k for k in st.session_state.keys() if k.startswith("gcp_legacy")]
    legacy_keys.extend([k for k in ("gcp.step", "gcp_view") if k in st.session_state])
    for key in legacy_keys:
        st.session_state.pop(key, None)


inject_css()
ensure_session()
_cleanup_legacy_gcp_state()

# ====================================================================
# SESSION PERSISTENCE - Load state from disk
# ====================================================================

# Get or generate session ID (browser-specific)
if 'session_id' not in st.session_state:
    # Try to get from query params (if user bookmarked a session)
    session_id_from_url = st.query_params.get('sid')
    if session_id_from_url:
        st.session_state['session_id'] = session_id_from_url
    else:
        from core.session_store import generate_session_id
        st.session_state['session_id'] = generate_session_id()

session_id = st.session_state['session_id']

# Get or create user ID (persistent across sessions if authenticated)
uid = get_or_create_user_id(st.session_state)

# Load persisted data on first run
if 'persistence_loaded' not in st.session_state:
    # Load session data (browser-specific, temporary)
    session_data = load_session(session_id)
    merge_into_state(st.session_state, session_data)
    
    # Load user data (persistent, cross-device)
    user_data = load_user(uid)
    merge_into_state(st.session_state, user_data)
    
    st.session_state['persistence_loaded'] = True
    log_event("session.loaded", {"session_id": session_id, "uid": uid})

# Cleanup old session files periodically (1% chance per page load)
import random
if random.random() < 0.01:
    deleted = cleanup_old_sessions(max_age_days=7)
    if deleted > 0:
        log_event("session.cleanup", {"deleted": deleted})

# Initialize MCIP v2 (The Conductor)
from core.mcip import MCIP
from core.mcip_events import register_default_listeners
MCIP.initialize()
register_default_listeners()

ctx = get_user_ctx()
PAGES = load_nav(ctx)
route = current_route("welcome", PAGES)
_sanitize_query_params_for_welcome(route)

LAYOUT_CHROME_ROUTES = {
    "welcome",
    "self",
    "someone_else",
    "professionals",
    "hub_concierge",
    "hub_waiting",
    "hub_learning",
    "hub_trusted",
    "hub_professional",
    "gcp",
}
uses_layout_frame = route in LAYOUT_CHROME_ROUTES

reset_global_frame()

# Show development controls in sidebar
show_dev_controls()

if not uses_layout_frame:
    page_container_open()

log_event("nav.page_change", {"to": route})
PAGES[route]["render"]()

if not uses_layout_frame:
    page_container_close()

# ====================================================================
# SESSION PERSISTENCE - Save state to disk after page render
# ====================================================================

# Save session data (browser-specific, temporary)
session_state_to_save = extract_session_state(st.session_state)
if session_state_to_save:
    save_session(session_id, session_state_to_save)

# Save user data (persistent, cross-device)
user_state_to_save = extract_user_state(st.session_state)
if user_state_to_save:
    save_user(uid, user_state_to_save)
