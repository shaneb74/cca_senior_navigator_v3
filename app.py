# Silence Streamlit file watcher spam
import logging

import streamlit as st

logging.getLogger("streamlit.watcher.local_sources_watcher").setLevel(logging.ERROR)
logging.getLogger("streamlit.watcher").setLevel(logging.ERROR)

from core.events import log_event
from core.nav import current_route, load_nav

# Session persistence
from core.session_store import (
    cleanup_old_sessions,
    extract_session_state,
    extract_user_state,
    get_or_create_user_id,
    load_session,
    load_user,
    merge_into_state,
    save_session,
    save_user,
)
from core.state import ensure_session, get_user_ctx
from core.ui import page_container_close, page_container_open
from layout import reset_global_frame

st.set_page_config(
    page_title="Senior Navigator",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",  # Hide the sidebar navigation
)


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


def inject_css() -> None:
    """Load global CSS and module-specific CSS."""
    try:
        # Load global CSS
        with open("assets/css/global.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

        # Load module CSS (must come after global to override)
        # Adding cache-busting comment to force browser reload
        with open("assets/css/modules.css", encoding="utf-8") as f:
            css_content = f.read()
            # Add timestamp comment to bust cache
            import time

            cache_buster = f"/* Cache bust: {int(time.time())} */\n"
            st.markdown(f"<style>{cache_buster}{css_content}</style>", unsafe_allow_html=True)

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
# URL-DRIVEN ROUTING - Hydrate from query params (do this ONCE at startup)
# ====================================================================
from core.url_helpers import current_route as get_current_route

if not st.session_state.get("_hydrated_from_qp"):
    # Hydrate route from URL query params
    st.session_state["current_route"] = get_current_route()
    st.session_state["_hydrated_from_qp"] = True

# ====================================================================
# DEV MODE & FLAG VALIDATION
# ====================================================================

# Enable dev mode based on URL query param (?dev=true)
if "dev" in st.query_params and st.query_params["dev"].lower() in ("true", "1", "yes"):
    st.session_state["dev_mode"] = True

    # Run flag validation on first load in dev mode
    if "flag_validation_run" not in st.session_state:
        from core.validators import check_flags_at_startup

        check_flags_at_startup(verbose=True)  # Print validation summary to console
        st.session_state["flag_validation_run"] = True
else:
    st.session_state["dev_mode"] = False

# ====================================================================
# FEATURE FLAGS
# ====================================================================

# LLM Navi feature flag: off|shadow|assist|adjust (default: off)
# Shadow mode = read-only logging, no UI changes
if "FEATURE_LLM_NAVI" not in st.session_state:
    import os
    def _get_flag(name, default="off"):
        try:
            v = st.secrets.get(name)
            if v:
                return str(v).strip().strip('"').lower()
        except Exception:
            pass
        v = os.getenv(name, default)
        return str(v).strip().strip('"').lower()

    # respect secrets.toml / env instead of hard-coding shadow
    st.session_state["FEATURE_LLM_NAVI"] = _get_flag("FEATURE_LLM_GCP", "off")

# ====================================================================
# SESSION PERSISTENCE - Load state from disk
# ====================================================================

# Get or generate session ID (browser-specific, stable across navigation)
if "session_id" not in st.session_state:
    # Use Streamlit's internal session ID for stability
    # This persists across page navigation (query param changes)
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        ctx = get_script_run_ctx()
        if ctx and ctx.session_id:
            # Use Streamlit's session ID (stable for browser session)
            st.session_state["session_id"] = ctx.session_id
        else:
            # Fallback: generate UUID
            from core.session_store import generate_session_id

            st.session_state["session_id"] = generate_session_id()
    except ImportError:
        # Fallback for older Streamlit versions
        from core.session_store import generate_session_id

        st.session_state["session_id"] = generate_session_id()

session_id = st.session_state["session_id"]

# Get or create user ID (persistent across sessions if authenticated)
# CRITICAL FIX: Check query params for uid first (preserves across href navigation)
uid_from_url = st.query_params.get("uid")
if uid_from_url:
    # Restore UID from query params (href navigation)
    if uid_from_url.startswith("anon_"):
        st.session_state["anonymous_uid"] = uid_from_url
    else:
        if "auth" not in st.session_state:
            st.session_state["auth"] = {}
        st.session_state["auth"]["user_id"] = uid_from_url
        st.session_state["auth"]["is_authenticated"] = True
    uid = uid_from_url
else:
    uid = get_or_create_user_id(st.session_state)
    # Add UID to query params for href persistence
    st.query_params["uid"] = uid

# Load persisted data on first run OR when UID changes
last_loaded_uid = st.session_state.get("_last_loaded_uid")
needs_reload = "persistence_loaded" not in st.session_state or last_loaded_uid != uid

if needs_reload:
    # Load session data (browser-specific, temporary)
    session_data = load_session(session_id)
    merge_into_state(st.session_state, session_data)

    # Load user data (persistent, cross-device)
    user_data = load_user(uid)
    merge_into_state(st.session_state, user_data)
    
    # Rehydrate name from loaded user data
    from core.state_bootstrap import rehydrate_name_from_snapshot
    rehydrate_name_from_snapshot(user_data)

    st.session_state["persistence_loaded"] = True
    st.session_state["_last_loaded_uid"] = uid
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

# Cost Planner v2: Allow direct access to cost_v2 product router
# (removed redirect that was forcing to cost_intro)

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

if not uses_layout_frame:
    page_container_open()

log_event("nav.page_change", {"to": route})

# Log route resolution for key flows
log_routes = ("cost_intro", "cost_quick_estimate", "auth_start", "login", "fa_intro", "pfma_v3")
if route in log_routes:
    module_path = PAGES[route]["render"].__module__ + ":" + PAGES[route]["render"].__name__
    print(f"[ROUTER] page={route} -> {module_path}")

PAGES[route]["render"]()

if not uses_layout_frame:
    page_container_close()

# ====================================================================
# SESSION PERSISTENCE - Save state to disk after page render
# ====================================================================

# Always save state after render to ensure latest changes are persisted
# This is critical for href-based navigation which restarts the app

# Save session data (browser-specific, temporary)
session_state_to_save = extract_session_state(st.session_state)
if session_state_to_save:
    save_session(session_id, session_state_to_save)

# Save user data (persistent, cross-device)
user_state_to_save = extract_user_state(st.session_state)
if user_state_to_save:
    save_user(uid, user_state_to_save)
