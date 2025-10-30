"""
Unified audience selection page.
Single contextual page between Welcome and Concierge Hub.
"""
import streamlit as st
import html

from core.nav import route_to
from core.ui import img_src
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
    """Inject designer-style CSS for audience page with pure white background."""
    if st.session_state.get("_audience_css_injected"):
        return
    
    st.markdown("""
    <style>
    /* Force pure white background globally - no gray backgrounds */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"], .stApp {
      background-color: #ffffff !important;
    }
    
    /* Remove any default Streamlit padding/background */
    .main .block-container {
      background-color: #ffffff !important;
      padding-top: 3rem !important;
    }
    
    /* Layout container */
    .audience-layout {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 4rem;
      max-width: 1200px;
      margin: 3rem auto;
      padding: 0 2rem;
      align-items: center;
      background-color: #ffffff !important;
    }
    
    /* Left content panel - white background */
    .audience-content {
      max-width: 500px;
      background-color: #ffffff !important;
    }
    
    /* Right image panel */
    .audience-image-panel {
      position: relative;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    
    .audience-image-panel img {
      max-width: 100%;
      height: auto;
      border-radius: 20px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
    }
    
    /* Pill container - designer style */
    .pill-container {
      display: flex;
      gap: 1rem;
      margin-bottom: 2rem;
    }
    
    /* Pill wrapper for Streamlit buttons */
    .pill-wrapper {
      flex: 1;
    }
    
    /* Override Streamlit button styling for pills */
    .pill-wrapper .stButton button {
      width: 100% !important;
      border-radius: 999px !important;
      font-weight: 600 !important;
      padding: 0.7rem 1.2rem !important;
      background: #f7f8fa !important;
      color: #0b132b !important;
      border: 1px solid #e0e5ec !important;
      transition: all 0.25s ease !important;
      cursor: pointer !important;
      font-size: 0.95rem !important;
    }
    
    /* Active pill */
    .pill-wrapper.active .stButton button {
      background: #0b132b !important;
      color: #ffffff !important;
      border: none !important;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Hover effect */
    .pill-wrapper .stButton button:hover {
      background: #e8eaef !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1) !important;
    }
    
    .pill-wrapper.active .stButton button:hover {
      background: #1a1f3a !important;
      transform: translateY(-1px);
    }
    
    /* Close button */
    .close-button {
      position: absolute;
      top: 0;
      right: 0;
      color: #64748b;
      text-decoration: none;
      font-size: 1.5rem;
      font-weight: 700;
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      background: #f7f8fa;
      transition: all 0.2s ease;
    }
    
    .close-button:hover {
      background: #e8eaef;
      color: #0b132b;
    }
    
    /* Title */
    .audience-title {
      font-size: 1.8rem;
      font-weight: 700;
      color: #0b132b;
      margin-bottom: 1.5rem;
      line-height: 1.3;
    }
    
    /* Form labels */
    .form-label {
      font-weight: 600;
      color: #0b132b;
      margin-bottom: 0.5rem;
      display: block;
      font-size: 0.9rem;
    }
    
    /* Form note - only the note box has light background, not the page */
    .form-note {
      color: #64748b;
      font-size: 0.9rem;
      margin-top: 1.5rem;
      padding: 0.75rem 1rem;
      background: #f7f8fa;
      border-radius: 8px;
      line-height: 1.5;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
      .audience-layout {
        grid-template-columns: 1fr;
        gap: 2rem;
      }
      
      .audience-image-panel {
        order: -1;
      }
      
      .pill-container {
        flex-direction: column;
      }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.session_state["_audience_css_injected"] = True


def _page_content():
    """Main audience selection content with designer layout."""
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
        image_path = "static/images/tell_us_about_you.png"
    else:  # someone
        title = "We're here to help you find the support your loved ones need."
        placeholder = "What's their name?"
        image_path = "static/images/tell_us_about_them.png"
    
    # Load image
    photo_data = img_src(image_path)
    
    # Create two-column layout
    st.markdown('<div class="audience-layout">', unsafe_allow_html=True)
    
    # Left column - form content
    left_col, right_col = st.columns([1, 1], gap="large")
    
    with left_col:
        st.markdown('<div class="audience-content" style="position: relative;">', unsafe_allow_html=True)
        
        # Close button
        back_href = add_uid_to_href("?page=welcome")
        st.markdown(
            f'<a href="{back_href}" class="close-button" aria-label="Back to welcome">×</a>',
            unsafe_allow_html=True,
        )
        
        # Designer-style pills
        st.markdown('<div class="pill-container">', unsafe_allow_html=True)
        
        pill_col1, pill_col2 = st.columns([1, 1])
        
        with pill_col1:
            pill_class = "active" if mode == "someone" else ""
            st.markdown(f'<div class="pill-wrapper {pill_class}">', unsafe_allow_html=True)
            if st.button("👥 For someone", key="pill-someone", use_container_width=True):
                st.session_state["audience_mode"] = "someone"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with pill_col2:
            pill_class = "active" if mode == "self" else ""
            st.markdown(f'<div class="pill-wrapper {pill_class}">', unsafe_allow_html=True)
            if st.button("🙋 For me", key="pill-self", use_container_width=True):
                st.session_state["audience_mode"] = "self"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
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
    
    # Right column - image panel
    with right_col:
        if photo_data:
            st.markdown(
                f'<div class="audience-image-panel"><img src="{photo_data}" alt="Family care moments" /></div>',
                unsafe_allow_html=True,
            )
    
    st.markdown('</div>', unsafe_allow_html=True)


def render(ctx=None):
    """Main render function."""
    render_header_simple(active_route="audience")
    _page_content()
    render_footer_simple()
