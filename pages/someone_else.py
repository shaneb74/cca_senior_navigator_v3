import streamlit as st
import html

from core.mcip import MCIP
from core.nav import route_to
from core.state import is_authenticated
from core.ui import img_src
from core.url_helpers import add_uid_to_href
from ui.footer_simple import render_footer_simple
from ui.header_simple import render_header_simple

# Ensure NAVI is NOT imported (per golden rules)
assert "navi_core" not in locals() and "navi_core" not in globals(), "NAVI must not be imported on audience selection page"

# Define relationship choices locally (matching NAVI PERSONA_CHOICES keys)
# These map to internal persona IDs in NAVI when used later in the journey
RELATIONSHIP_CHOICES = [
    "Adult Child (Son or Daughter)",
    "Spouse / Partner",
    "Friend or Neighbor",
    "Advisor / Professional",
    "Other / Unsure",
]


def _page_content(ctx=None):
    # Check if authenticated user already has planning context
    if is_authenticated():
        has_context = st.session_state.get("planning_for_name") or st.session_state.get(
            "person_name"
        )
        if has_context:
            # Skip contextual welcome - go directly to recommended route
            next_action = MCIP.get_recommended_next_action()
            route_to(next_action.get("route", "hub_lobby"))
            return

    # Render unified audience selection with relationship dropdown
    _render_unified_audience_selection()


def _inject_welcome_css() -> None:
    """Inject welcome CSS if not already loaded."""
    if st.session_state.get("_welcome_css_main"):
        return
    
    # Import CSS from welcome.py by calling its injection function
    from pages.welcome import _inject_welcome_css as inject_main_css
    inject_main_css()


def _render_unified_audience_selection() -> None:
    """Designer-accurate audience selection with centered card and black/gray pills.
    
    Matches designer's exact layout:
    - Centered white card with soft shadow
    - Black active pill vs light gray inactive pill  
    - Single hero image on right
    - Soft blue gradient background
    - Clean, airy spacing
    
    Preserves smooth behavior without st.rerun() calls.
    """
    _inject_welcome_css()
    
    # Initialize session state for audience mode (no rerun needed)
    if "audience_mode" not in st.session_state:
        st.session_state["audience_mode"] = "someone"
    
    # Get current mode from state
    mode = st.session_state.get("audience_mode", "someone")
    
    # Configure content based on mode
    if mode == "self":
        title = "We're here to help you find the support you're looking for."
        placeholder = "What's your name?"
        image_path = "static/images/welcome_self.png"
        alt_text = "Senior smiling outdoors"
    else:  # someone
        title = "We're here to help you find the support your loved ones need."
        placeholder = "What's their name?"
        image_path = "static/images/welcome_someone_else.png"
        alt_text = "Care team supporting family members"
    
    photo_data = img_src(image_path)
    
    # Render sentinel for CSS targeting
    st.markdown('<span class="welcome-context-sentinel"></span>', unsafe_allow_html=True)
    left_col, right_col = st.columns([1.05, 0.95], gap="large")
    
    with left_col:
        # Start centered card container
        st.markdown('<div class="audience-card">', unsafe_allow_html=True)
        
        # Designer pills - use Streamlit buttons styled with CSS
        st.markdown('<div class="pill-container">', unsafe_allow_html=True)
        
        pill_col1, pill_col2 = st.columns([1, 1])
        
        with pill_col1:
            # Use custom CSS class based on active state
            pill_class = "active" if mode == "someone" else ""
            st.markdown(f'<div class="pill-wrapper {pill_class}">', unsafe_allow_html=True)
            if st.button("👥 For someone", key="pill-someone", use_container_width=True):
                st.session_state["audience_mode"] = "someone"
            st.markdown('</div>', unsafe_allow_html=True)
        
        with pill_col2:
            pill_class = "active" if mode == "self" else ""
            st.markdown(f'<div class="pill-wrapper {pill_class}">', unsafe_allow_html=True)
            if st.button("🙋 For me", key="pill-self", use_container_width=True):
                st.session_state["audience_mode"] = "self"
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Back button
        back_href = add_uid_to_href("?page=welcome")
        st.markdown(
            f'<div style="text-align: right; margin-top: -10px;"><a class="context-close" href="{back_href}" aria-label="Back to welcome">×</a></div>',
            unsafe_allow_html=True,
        )
        
        # Title
        st.markdown(
            f'<h1 class="context-title">{html.escape(title)}</h1>',
            unsafe_allow_html=True,
        )
        
        # Conditional relationship dropdown (no form wrapper for reactive button state)
        if mode == "someone":
            st.markdown('<div class="context-form-section">', unsafe_allow_html=True)
            st.markdown('<label class="context-label">Your relationship</label>', unsafe_allow_html=True)
            relationship = st.selectbox(
                "Your relationship to the person you're helping",
                options=RELATIONSHIP_CHOICES,
                index=0,
                key=f"relationship_select_{mode}",
                label_visibility="collapsed"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            relationship = None
        
        # Name input + Continue button (reactive state)
        st.markdown('<div class="context-form-row">', unsafe_allow_html=True)
        input_col, button_col = st.columns([3, 2], gap="small")
        with input_col:
            st.markdown('<div class="context-input">', unsafe_allow_html=True)
            # Get current value from session state or empty string
            current_name = st.session_state.get("audience_name_input", "")
            name_value = st.text_input(
                placeholder,
                value=current_name,
                key=f"welcome-name-{mode}",
                label_visibility="collapsed",
                placeholder=placeholder,
            )
            # Save to session state immediately for reactive updates
            st.session_state["audience_name_input"] = name_value
            st.markdown("</div>", unsafe_allow_html=True)
        with button_col:
            st.markdown('<div class="context-submit">', unsafe_allow_html=True)
            # Enable button only if name has content
            button_disabled = not (name_value and name_value.strip())
            submitted = st.button("Continue", disabled=button_disabled, key=f"continue-{mode}")
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Handle button click
        if submitted and name_value and name_value.strip():
            # Store using specified session state keys
            st.session_state["audience_mode"] = mode
            st.session_state["audience_name"] = name_value.strip()
            
            if mode == "someone":
                st.session_state["relationship"] = relationship
                # Legacy keys for backward compatibility
                st.session_state["relationship_type"] = relationship
                st.session_state["planning_for_relationship"] = "someone_else"
            else:  # self
                st.session_state["relationship"] = "Myself"
                # Legacy keys for backward compatibility
                st.session_state["relationship_type"] = "Myself"
                st.session_state["planning_for_relationship"] = "self"
            
            # Store person's name in legacy system
            from core.state_name import set_person_name
            set_person_name(name_value.strip())
            
            # Navigate to hub using route_to (compatible with nav system)
            route_to("hub_lobby")
        
        # Optional note for "someone" mode
        if mode == "someone":
            st.markdown(
                '<div class="context-note">If you want to assess several people, don\'t worry – you can easily move on to the next step!</div>',
                unsafe_allow_html=True,
            )
        
        # Close audience card
        st.markdown('</div>', unsafe_allow_html=True)
    
    with right_col:
        if photo_data:
            st.markdown(
                f'<div class="context-image"><div class="context-collage">'
                f'<figure class="context-collage__base"><img src="{photo_data}" alt="{html.escape(alt_text)}" /></figure>'
                "</div></div>",
                unsafe_allow_html=True,
            )


def render(ctx=None):
    # Render with simple header/footer
    render_header_simple(active_route="someone_else")
    _page_content(ctx)
    render_footer_simple()

