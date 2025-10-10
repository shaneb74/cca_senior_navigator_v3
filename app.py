import streamlit as st

from core.events import log_event
from core.nav import current_route, load_nav
from core.state import ensure_session, get_user_ctx
from core.ui import footer, header, page_container_close, page_container_open

st.set_page_config(page_title="Senior Navigator", page_icon="🧭", layout="wide")


def inject_css():
    """
    Inject custom CSS to override Streamlit's default theming.
    
    CRITICAL: The try-except block is essential for cloud deployments where
    the file path may differ. This prevents the app from crashing if the CSS
    file is not found, while still allowing the custom theme to be applied
    when available.
    
    DO NOT REMOVE - this is required to suppress error styling (red borders,
    red backgrounds) that can appear when background exceptions occur in Streamlit.
    Works in conjunction with .streamlit/config.toml settings.
    """
    try:
        with open("assets/css/theme.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # no-op on Cloud if path differs; don't crash
        pass


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

st.markdown(
    """<nav class="mnav">
  <div class="bar">
    <a class="is-active" href="?page=welcome">Dashboard</a>
    <a href="?page=hub_learning">Learning Center</a>
    <a href="?page=waiting_room">Get Connected</a>
  </div>
</nav>""",
    unsafe_allow_html=True,
)

footer()
