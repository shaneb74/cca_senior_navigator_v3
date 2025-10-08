import streamlit as st

from core.events import log_event
from core.nav import current_route, load_nav, route_to
from core.state import ensure_session, get_user_ctx
from core.ui import footer, header, page_container_close, page_container_open

st.set_page_config(page_title="Senior Navigator", page_icon="🧭", layout="wide")


def inject_css():
    with open("assets/css/theme.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


inject_css()
ensure_session()
ctx = get_user_ctx()
PAGES = load_nav(ctx)
route = current_route("welcome", PAGES)

header("Senior Navigator", route, PAGES)

# Dev-only auth toggles (remove before prod)
with st.sidebar.expander("Dev: auth & role"):
    ctx["auth"]["is_authenticated"] = st.checkbox(
        "Authenticated", value=ctx["auth"]["is_authenticated"]
    )
    roles = ["guest", "user", "pro", "admin"]
    ctx["auth"]["role"] = st.selectbox(
        "Role", roles, index=roles.index(ctx["auth"]["role"])
    )

page_container_open()
log_event("nav.page_change", {"to": route})
PAGES[route]["render"]()
page_container_close()

footer()
