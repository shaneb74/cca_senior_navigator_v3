import streamlit as st

from core.events import log_event
from core.nav import current_route, load_nav
from core.state import ensure_session, get_user_ctx
from core.ui import page_container_close, page_container_open
from layout import reset_global_frame

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

if not uses_layout_frame:
    page_container_open()

log_event("nav.page_change", {"to": route})
PAGES[route]["render"]()

if not uses_layout_frame:
    page_container_close()
