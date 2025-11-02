"""
Navi Redesign — Standardized Helper Functions

Two variants:
1. Hub-level: What's Next snapshot (inside hero)
2. Module-level: Compact coach panel (top of module pages)

Phase 1: Structure only with placeholders.
Phase 2: Data wiring (comes later).
"""

import streamlit as st
from typing import Optional


def friendly_tier(tier: Optional[str]) -> Optional[str]:
    """Convert tier code to friendly display string.
    
    Args:
        tier: Tier code (e.g., "assisted_living", "memory_care")
        
    Returns:
        Friendly tier string or None if tier is None
    """
    if not tier:
        return None
    
    tier_map = {
        "assisted_living": "Assisted Living (memory support)",
        "memory_care": "Memory Care",
        "memory_care_high_acuity": "Memory Care",
        "in_home": "In-Home Care",
    }
    
    return tier_map.get(tier, tier.replace("_", " ").title())


def render_hub_navi_next() -> None:
    """Render Hub-level Navi 'What's Next' snapshot inside hero.
    
    Phase 1: Structure only with placeholders.
    Shows exactly 4 lines: Recommendation, Clinical Review, Advisor, Tip.
    No CTA button yet.
    """
    # Phase 1: Hardcoded placeholders (data wiring comes in Phase 2)
    st.write("**Recommendation:** Assisted Living (memory support)")
    st.write("**Clinical Review:** Not yet scheduled")
    st.write("**Advisor:** Tue, Nov 4 · 2:30 PM · Virtual")
    st.caption("Tip: You can confirm your plan with a brief clinical review.")


def render_module_navi_coach(primary_msg: str = "Answer these questions to match the right level of support.") -> None:
    """Render Module-level compact Navi panel at top of module pages.
    
    Phase 1: Structure only - just the coach line in a compact panel.
    No Why? block, no plan summary yet.
    
    Styling driven by .navi-panel-compact and .navi-card CSS classes.
    
    Args:
        primary_msg: Primary coaching message (default provided)
    """
    # Phase 1: Simple compact panel with coach line only - styling from CSS
    st.markdown(f"""
    <div class="navi-panel-compact navi-card ai-card animate-border">
        <div style="color: #7c5cff; font-weight: 600; margin-bottom: 0.5rem;">
            ✨ NAVI
        </div>
        <div style='color: #111827;'>{primary_msg}</div>
    </div>
    <div style='margin-bottom: 0.5rem;'></div>
    """, unsafe_allow_html=True)
