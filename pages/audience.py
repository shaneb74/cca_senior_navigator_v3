"""
Unified audience selection page.
Single contextual page between Welcome and Concierge Hub.
"""
import streamlit as st
import html

from core.nav import route_to
from core.url_helpers import add_uid_to_href
from ui.footer_simple import render_footer_simple
from ui.header_simple import render_header_simple

# Relationship choices for "someone" mode
RELATIONSHIP_CHOICES = [
    "Adult Child (Son or Daughter)",
    "Spouse / Partner",
    "Friend or Neighbor",
    "Advisor / Professional",
    "Other / Unsure",
]


def _inject_audience_css() -> None:
    """Inject minimal CSS for audience page with white background."""
    if st.session_state.get("_audience_css_injected"):
        return
    
    st.markdown("""
    <style>
    /* White background globally */
    .stApp {
      background-color: #ffffff !important;
    }
    
    /* Pill container */
    .pill-container {
      display: flex;
      gap: 1rem;
      margin-bottom: 2rem;
    }
    
    /* Individual pill styling */
    .audience-pill {
      flex: 1;
      text-align: center;
      padding: 0.6rem 1.2rem;
      border-radius: 999px;
      font-weight: 600;
      background: #f8f9fb;
      color: #0b132b;
      border: 1px solid #e0e5ec;
      cursor: pointer;
      transition: all 0.2s ease-in-out;
      user-select: none;
    }
    
    /* Active pill: black background */
    .audience-pill.active {
      background: #0b132b;
      color: #fff;
      border: none;
    }
    
    /* Hover effect */
    .audience-pill:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(0,0,0,0.08);
    }
    
    /* Form styling */
    .audience-form {
      max-width: 600px;
      margin: 0 auto;
      padding: 2rem;
    }
    
    .audience-title {
      font-size: 1.8rem;
      font-weight: 700;
      color: #0b132b;
      margin-bottom: 1.5rem;
      line-height: 1.3;
    }
    
    .form-label {
      font-weight: 600;
      color: #0b132b;
      margin-bottom: 0.5rem;
      display: block;
    }
    
    .form-note {
      color: #64748b;
      font-size: 0.9rem;
      margin-top: 1rem;
      padding: 0.75rem;
      background: #f8f9fb;
      border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.session_state["_audience_css_injected"] = True


def _render_pills(mode: str) -> str:
    """Render pill toggle and handle mode changes."""
    st.markdown('<div class="pill-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        left_class = "active" if mode == "someone" else ""
        if st.button("👥 For someone", key="pill-someone", use_container_width=True):
            st.session_state["audience_mode"] = "someone"
            st.rerun()
    
    with col2:
        right_class = "active" if mode == "self" else ""
        if st.button("🙋 For me", key="pill-self", use_container_width=True):
            st.session_state["audience_mode"] = "self"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return st.session_state.get("audience_mode", mode)


def _page_content():
    """Main audience selection content."""
    _inject_audience_css()
    
    # Check for URL parameter to set initial mode
    url_mode = st.query_params.get("mode")
    if url_mode in ["someone", "self"] and "audience_mode" not in st.session_state:
        st.session_state["audience_mode"] = url_mode
    
    # Initialize mode
    if "audience_mode" not in st.session_state:
        st.session_state["audience_mode"] = "someone"
    
    mode = st.session_state.get("audience_mode", "someone")
    
    # Configure content based on mode
    if mode == "self":
        title = "We're here to help you find the support you're looking for."
        placeholder = "What's your name?"
    else:  # someone
        title = "We're here to help you find the support your loved ones need."
        placeholder = "What's their name?"
    
    # Render form
    st.markdown('<div class="audience-form">', unsafe_allow_html=True)
    
    # Pills
    mode = _render_pills(mode)
    
    # Back button
    back_href = add_uid_to_href("?page=welcome")
    st.markdown(
        f'<div style="text-align: right; margin-top: -3rem; margin-bottom: 1rem;"><a href="{back_href}" style="color: #64748b; text-decoration: none; font-size: 1.5rem;" aria-label="Back to welcome">×</a></div>',
        unsafe_allow_html=True,
    )
    
    # Title
    st.markdown(
        f'<h1 class="audience-title">{html.escape(title)}</h1>',
        unsafe_allow_html=True,
    )
    
    # Relationship dropdown (only for "someone" mode)
    relationship = None
    if mode == "someone":
        st.markdown('<label class="form-label">Your relationship</label>', unsafe_allow_html=True)
        relationship = st.selectbox(
            "Your relationship to the person you're helping",
            options=RELATIONSHIP_CHOICES,
            index=0,
            key=f"relationship_select_{mode}",
            label_visibility="collapsed"
        )
    
    # Name input
    st.markdown('<label class="form-label">Name</label>', unsafe_allow_html=True)
    name_value = st.text_input(
        "Name",
        value=st.session_state.get("audience_name_input", ""),
        key=f"name_input_{mode}",
        label_visibility="collapsed",
        placeholder=placeholder,
    )
    
    # Save to session state
    st.session_state["audience_name_input"] = name_value
    
    # Continue button
    button_disabled = not (name_value and name_value.strip())
    submitted = st.button(
        "Continue",
        disabled=button_disabled,
        key=f"continue_{mode}",
        type="primary",
        use_container_width=True
    )
    
    # Handle submission
    if submitted and name_value and name_value.strip():
        # Store data
        st.session_state["audience_mode"] = mode
        st.session_state["audience_name"] = name_value.strip()
        
        if mode == "someone":
            st.session_state["relationship"] = relationship
            st.session_state["relationship_type"] = relationship
            st.session_state["planning_for_relationship"] = "someone_else"
        else:  # self
            st.session_state["relationship"] = "Myself"
            st.session_state["relationship_type"] = "Myself"
            st.session_state["planning_for_relationship"] = "self"
        
        # Store name in legacy system
        from core.state_name import set_person_name
        set_person_name(name_value.strip())
        
        # Navigate to Concierge Hub
        route_to("hub_concierge")
    
    # Optional note for "someone" mode
    if mode == "someone":
        st.markdown(
            '<div class="form-note">💡 If you want to assess several people, don\'t worry – you can easily move on to the next step!</div>',
            unsafe_allow_html=True,
        )
    
    st.markdown('</div>', unsafe_allow_html=True)


def render(ctx=None):
    """Main render function."""
    render_header_simple(active_route="audience")
    _page_content()
    render_footer_simple()
