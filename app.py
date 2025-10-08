import streamlit as st

from core.events import log_event
from core.nav import current_route, load_nav, route_to
from core.state import ensure_session, get_user_ctx

st.set_page_config(page_title="Senior Navigator", page_icon="🧭", layout="wide")


def inject_css():
    try:
        with open("assets/css/theme.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


inject_css()
ensure_session()
ctx = get_user_ctx()
PAGES = load_nav(ctx)
route = current_route("welcome", PAGES)

last_group = None
for key, meta in PAGES.items():
    group_label = meta.get("group")
    if group_label and group_label != last_group:
        st.sidebar.header(group_label)
        last_group = group_label
    if st.sidebar.button(meta["label"], key=f"nav-{key}"):
        route_to(key)

log_event("nav.page_change", {"to": route})
PAGES[route]["render"]()
