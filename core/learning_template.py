"""
Learning Template - Reusable component for educational tiles

Phase 5B: Standardized learning experience architecture.
Used by Discovery Learning, Learn About My Recommendation, and future learning tiles.

Features:
- Consistent visual structure
- Scoped NAVI chat for topic-specific guidance
- Resource integration (videos, links, documents)
- Completion tracking integrated with journey phases
"""

import streamlit as st
from typing import Optional

from core.journeys import mark_tile_complete, get_current_journey
from core.nav import route_to
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple


def render_learning(
    title: str,
    intro: str,
    topic: str,
    resources: list[dict],
    phase: str,
    tile_key: str,
    sections: Optional[list[dict]] = None,
    next_route: Optional[str] = None,
    show_navi_chat: bool = True,
) -> None:
    """Render a standardized learning experience tile.
    
    Phase 5B: Core template for all NAVI-guided learning experiences.
    
    Args:
        title: Page title (e.g., "Start Your Discovery Journey")
        intro: Introductory markdown text
        topic: Topic scope for NAVI chat (e.g., "senior_navigator_overview")
        resources: List of resource dicts with 'type' and 'url' keys
        phase: Journey phase (discovery/planning/post_planning)
        tile_key: Product key for completion tracking (e.g., "discovery_learning")
        sections: Optional list of content section dicts with 'title' and 'content'
        next_route: Optional route to navigate to after completion (default: hub_lobby)
        show_navi_chat: Whether to show scoped NAVI chat (default: True)
    
    Example:
        >>> render_learning(
        ...     title="Start Your Discovery Journey",
        ...     intro="👋 Hi, I'm NAVI...",
        ...     topic="senior_navigator_overview",
        ...     resources=[{"type": "video", "url": "https://youtube.com/..."}],
        ...     phase="discovery",
        ...     tile_key="discovery_learning"
        ... )
    """
    # Render header
    render_header_simple(active_route=tile_key)
    
    # Load learning card CSS
    st.markdown(
        """
        <style>
        .learning-card {
            background: #fff;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 2px 6px rgba(0,0,0,.05);
            margin-bottom: 1.5rem;
        }
        .learning-card h1 {
            margin-bottom: 0.75rem;
            color: #0A1E4A;
        }
        .learning-card h2 {
            color: #1E5BD7;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }
        .learning-resource {
            background: #F8F9FA;
            border-left: 4px solid #1E5BD7;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 8px;
        }
        .learning-resource a {
            color: #1E5BD7;
            text-decoration: none;
            font-weight: 500;
        }
        .learning-resource a:hover {
            text-decoration: underline;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Main content card
    st.markdown('<div class="learning-card">', unsafe_allow_html=True)
    
    # Title and intro
    st.title(title)
    st.markdown(intro)
    
    # Content sections (if provided)
    if sections:
        st.markdown("---")
        for section in sections:
            st.markdown(f"### {section['title']}")
            st.markdown(section['content'])
    
    # Resources section
    if resources:
        st.markdown("---")
        st.markdown("### 📚 Resources")
        
        for resource in resources:
            resource_type = resource.get("type", "link")
            resource_url = resource.get("url", "")
            resource_title = resource.get("title", "Resource")
            resource_desc = resource.get("description", "")
            
            if resource_type == "video" and "youtube" in resource_url.lower():
                st.video(resource_url)
                if resource_desc:
                    st.caption(resource_desc)
            elif resource_type == "link":
                st.markdown(
                    f'<div class="learning-resource">'
                    f'<a href="{resource_url}" target="_blank">🔗 {resource_title}</a>'
                    f'<br/><small>{resource_desc}</small>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                # Generic resource display
                st.markdown(
                    f'<div class="learning-resource">'
                    f'<a href="{resource_url}" target="_blank">📄 {resource_title}</a>'
                    f'<br/><small>{resource_desc}</small>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Scoped NAVI Chat (if enabled)
    if show_navi_chat:
        st.markdown("---")
        st.subheader("💬 Ask NAVI a Question")
        st.caption(f"NAVI can answer questions specifically about: **{topic.replace('_', ' ').title()}**")
        
        # Import here to avoid circular dependency
        from apps.navi_core.scoped_chat import ScopedNaviChat
        chat = ScopedNaviChat(topic_scope=topic)
        chat.render()
    
    # Action buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Return to Lobby", use_container_width=True):
            route_to("hub_lobby")
    
    with col2:
        # Determine button label based on completion status
        is_complete = st.session_state.get(f"{tile_key}_complete", False)
        button_label = "Review Complete ✓" if is_complete else "Mark Lesson Complete →"
        button_type = "secondary" if is_complete else "primary"
        
        if st.button(button_label, type=button_type, use_container_width=True):
            # Mark as complete
            mark_tile_complete(tile_key, phase)
            st.session_state[f"{tile_key}_complete"] = True
            
            # Navigate to next route
            target_route = next_route or "hub_lobby"
            st.success(f"✓ Lesson marked complete! Journey phase: {phase}")
            st.toast(f"✓ {title} completed!")
            route_to(target_route)
    
    # Render footer
    render_footer_simple()


def render_learning_simple(
    title: str,
    intro: str,
    content: str,
    tile_key: str,
    phase: str = "discovery",
) -> None:
    """Simplified learning template without resources or NAVI chat.
    
    Phase 5B: Lightweight version for simple informational tiles.
    
    Args:
        title: Page title
        intro: Introduction text
        content: Main content markdown
        tile_key: Product key for completion tracking
        phase: Journey phase (default: discovery)
    """
    render_learning(
        title=title,
        intro=intro,
        topic=tile_key,
        resources=[],
        phase=phase,
        tile_key=tile_key,
        sections=[{"title": "", "content": content}],
        show_navi_chat=False,
    )
