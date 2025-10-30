"""
Module-level Navi component for GCP, Cost Planner, CCR, and other products.

Displays compact coaching panel with primary message, optional "Why this question?" 
explanation, and current plan summary (recommendation + care costs).
"""

import streamlit as st


def render_module_navi_coach(title_text: str, body_text: str, tip_text: str | None = None):
    """Compact module coach with title, body, and optional tip.
    
    Renders a minimal coaching panel with:
    - Title text (h4 weight)
    - One-sentence body text (≤120 chars)
    - Optional small tip
    
    Uses standard navi-panel-compact styling:
    - 4px blue left border (#3B82F6)
    - White background
    - 8px rounded corners
    - Subtle shadow
    - Max-width 1120px centered
    
    This function renders and returns immediately, allowing the page to continue.
    """
    # Build tip HTML if provided
    tip_html = f"<p style='font-size:0.9rem;color:#555;margin-top:.75rem;'>{tip_text}</p>" if tip_text else ""
    
    # Render compact Navi card with inline styling
    st.markdown(
        """
        <div class="navi-panel-compact"
             style="
                background:#fff;
                border-left:4px solid rgb(59,130,246);
                border-radius:8px;
                padding:1.25rem;
                margin:0 auto 1.5rem;
                max-width:1120px;
                box-shadow:0 0 4px 1px rgba(0,0,0,0.05);
             ">
          <p style="color:rgb(59,130,246);font-weight:600;margin:0 0 .5rem;">✨ NAVI</p>
          <p style="font-weight:600;font-size:1rem;margin:0;">{title_text}</p>
          <p style="margin:0.25rem 0 0;">{body_text}</p>
          {tip_html}
        </div>
        """.format(
            title_text=title_text,
            body_text=body_text,
            tip_html=tip_html,
        ),
        unsafe_allow_html=True,
    )
    
    # Function completes and returns control to caller
    print("[NAVI_MODULE] rendered; continuing page content")
