import streamlit as st

from core.mcip import MCIP
from core.nav import route_to
from core.state import is_authenticated
from pages.welcome import render_welcome_card
from ui.footer_simple import render_footer_simple
from ui.header_simple import render_header_simple

# Import NAVI Core components for persona selection
try:
    from apps.navi_core import PERSONA_CHOICES, UserProfile
    from apps.navi_core.context_manager import update_context
    from apps.navi_core.guidance_manager import get_guidance
    _NAVI_AVAILABLE = True
except ImportError:
    _NAVI_AVAILABLE = False
    PERSONA_CHOICES = {}


def _page_content(ctx=None):
    # Phase 5: Track page context for contextual guidance
    if _NAVI_AVAILABLE:
        update_context("For Someone Else")
    
    # Check if authenticated user already has planning context
    if is_authenticated():
        has_context = st.session_state.get("planning_for_name") or st.session_state.get(
            "person_name"
        )
        if has_context:
            # Skip contextual welcome - go directly to Navi's recommended route
            next_action = MCIP.get_recommended_next_action()
            route_to(next_action.get("route", "hub_concierge"))
            return

    # Enhanced welcome card with persona selection
    _render_enhanced_welcome_card()


def _render_enhanced_welcome_card():
    """Enhanced welcome card with explicit persona selection."""
    from core.url_helpers import add_uid_to_href
    from core.ui import img_src
    import html
    
    st.markdown('<span class="welcome-context-sentinel"></span>', unsafe_allow_html=True)
    left_col, right_col = st.columns([1.05, 0.95], gap="large")
    
    with left_col:
        st.markdown('<span class="context-card-sentinel"></span>', unsafe_allow_html=True)
        
        back_href = add_uid_to_href("?page=welcome")
        st.markdown(
            f'<div class="context-top"><a class="context-close" href="{back_href}" aria-label="Back to welcome">×</a></div>',
            unsafe_allow_html=True,
        )
        
        st.markdown(
            '<h1 class="context-title">We\'re here to help you find the support your loved ones need.</h1>',
            unsafe_allow_html=True,
        )
        
        # Phase 5.1: Display contextual guidance with smart triggers
        if _NAVI_AVAILABLE:
            guidance_msg = get_guidance()
            if guidance_msg:  # Only display if not suppressed by triggers
                st.info(f"💡 {guidance_msg}")
        
        # Persona selection form
        form = st.form("welcome-form-someone", clear_on_submit=False)
        with form:
            # Step 1: Relationship selector (if NAVI available)
            if _NAVI_AVAILABLE and PERSONA_CHOICES:
                st.markdown('<div class="context-form-section">', unsafe_allow_html=True)
                st.markdown('<label class="context-label">Your relationship</label>', unsafe_allow_html=True)
                relationship = st.selectbox(
                    "Your relationship to the person you're helping",
                    options=list(PERSONA_CHOICES.keys()),
                    index=0,
                    key="someone_else_relationship",
                    label_visibility="collapsed"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                relationship = None
            
            # Step 2: Name input
            st.markdown('<div class="context-form-row">', unsafe_allow_html=True)
            input_col, button_col = st.columns([3, 2], gap="small")
            with input_col:
                st.markdown('<div class="context-input">', unsafe_allow_html=True)
                name_value = st.text_input(
                    "What's their name?",
                    key="welcome-name-someone",
                    label_visibility="collapsed",
                    placeholder="What's their name?",
                )
                st.markdown("</div>", unsafe_allow_html=True)
            with button_col:
                st.markdown('<div class="context-submit">', unsafe_allow_html=True)
                submitted = st.form_submit_button("Continue")
                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Handle form submission
        if submitted:
            # Store relationship context
            st.session_state["relationship_type"] = "Parent"  # Legacy default
            st.session_state["planning_for_relationship"] = "someone_else"
            
            # Store person's name
            from core.state_name import set_person_name
            if name_value and name_value.strip():
                set_person_name(name_value.strip())
            else:
                set_person_name("")
            
            # Create NAVI UserProfile if available
            if _NAVI_AVAILABLE and relationship:
                role = PERSONA_CHOICES.get(relationship, "AdultChild")
                profile = UserProfile(
                    id=f"user_{st.session_state.get('session_id', 'anon')}",
                    name=name_value.strip() if name_value else None,
                    role=role,
                    relationship=relationship,
                    stage="Awareness"
                )
                st.session_state["user_profile"] = profile.model_dump()
                st.session_state["navi_persona"] = role
            
            # Navigate to hub
            route_to("hub_concierge")
        
        st.markdown(
            '<div class="context-note">If you want to assess several people, don\'t worry – you can easily move on to the next step!</div>',
            unsafe_allow_html=True,
        )
    
    with right_col:
        photo_data = img_src("static/images/welcome_someone_else.png")
        if photo_data:
            st.markdown(
                f'<div class="context-image"><div class="context-collage">'
                f'<figure class="context-collage__base"><img src="{photo_data}" alt="Care team supporting family members" /></figure>'
                "</div></div>",
                unsafe_allow_html=True,
            )


def render(ctx=None):
    # Render with simple header/footer
    render_header_simple(active_route="someone_else")
    _page_content(ctx)
    render_footer_simple()
