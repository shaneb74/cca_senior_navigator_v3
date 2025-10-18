"""
Navi Dialogue System

Loads and renders contextual messages from Navi throughout the user journey.
Foundation for future LLM integration.
"""

import json
import random
from collections.abc import Callable
from pathlib import Path
from typing import Optional,  Any

try:
    import streamlit as st

    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


class NaviDialogue:
    """Navi's dialogue system - loads contextual messages based on journey state."""

    _dialogue_data: Optional[dict[str, Any]] = None

    @classmethod
    def load_dialogue(cls) -> dict[str, Any]:
        """Load Navi dialogue configuration from JSON."""
        if cls._dialogue_data is None:
            config_path = Path(__file__).parent.parent / "config" / "navi_dialogue.json"
            with open(config_path) as f:
                cls._dialogue_data = json.load(f)
        return cls._dialogue_data

    @classmethod
    def get_journey_message(
        cls, phase: str, is_authenticated: bool = False, context: Optional[dict[str, Any]] = None
    ) -> dict[str, str]:
        """Get Navi's main journey message for current phase.

        Args:
            phase: Journey phase (getting_started, in_progress, nearly_there, complete)
            is_authenticated: Whether user is logged in
            context: Additional context (name, tier, costs, etc.)

        Returns:
            Dict with text, subtext, cta, icon
        """
        dialogue = cls.load_dialogue()
        phase_data = dialogue["journey_phases"].get(phase, {})
        messages = phase_data.get("messages", {})

        # Choose authenticated or guest message (try multiple patterns)
        message = None
        if is_authenticated:
            # Try authenticated variants
            for key in [
                "main_authenticated",
                "greeting_authenticated",
                "celebration_authenticated",
            ]:
                if key in messages:
                    message = messages[key]
                    break

        # Fall back to guest message
        if message is None:
            for key in ["main_guest", "greeting_guest", "celebration_guest"]:
                if key in messages:
                    message = messages[key]
                    break

        # Last resort: return empty dict
        if message is None:
            message = {}

        # Format with context
        if context:
            message = cls._format_message(message, context)

        return message

    @classmethod
    def get_context_boost(cls, phase: str, context: Optional[dict[str, Any]] = None) -> list[str]:
        """Get contextual boost messages for current phase.

        Args:
            phase: Journey phase
            context: Context for formatting

        Returns:
            List of context-specific messages
        """
        dialogue = cls.load_dialogue()
        phase_data = dialogue["journey_phases"].get(phase, {})
        boost = phase_data.get("messages", {}).get("context_boost", [])

        if context:
            boost = [cls._format_string(msg, context) for msg in boost]

        return boost

    @classmethod
    def get_product_intro(
        cls, product_key: str, context: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Get Navi's introduction message when starting a product.

        Args:
            product_key: Product key (gcp_start, cost_start, pfma_start)
            context: Context for formatting

        Returns:
            Dict with welcome, what_to_expect, navi_says
        """
        dialogue = cls.load_dialogue()
        intro = dialogue["product_intros"].get(product_key, {})

        if context:
            intro = cls._format_message(intro, context)

        return intro

    @classmethod
    def get_gate_message(cls, product_key: str) -> dict[str, str]:
        """Get Navi's message when product is locked/gated.

        Args:
            product_key: Product key (gcp_locked, cost_locked, pfma_locked)

        Returns:
            Dict with message, action, encouragement
        """
        dialogue = cls.load_dialogue()
        return dialogue["product_gates"].get(product_key, {})

    @classmethod
    def get_micro_moment(cls, moment_type: str, context: Optional[dict[str, Any]] = None) -> str:
        """Get a micro-moment message (progress save, unlock, achievement, etc.).

        Args:
            moment_type: Type of moment (progress_save, product_unlock, achievement_earned, etc.)
            context: Context for formatting

        Returns:
            Message string (randomly selected if multiple available)
        """
        dialogue = cls.load_dialogue()
        moments = dialogue["micro_moments"].get(moment_type, {})

        # Handle nested structure (e.g., product_unlock.cost_unlocked)
        if isinstance(moments, dict) and "messages" in moments:
            messages = moments["messages"]
            if isinstance(messages, list):
                message = random.choice(messages)
            elif isinstance(messages, dict) and context and context.get("product_key"):
                message = messages.get(context["product_key"], "")
            else:
                message = str(messages)
        elif isinstance(moments, list):
            message = random.choice(moments)
        else:
            message = str(moments)

        if context:
            message = cls._format_string(message, context)

        return message

    @classmethod
    def get_tip(cls, tip_category: str) -> str:
        """Get a random tip/hint for a product.

        Args:
            tip_category: Category key (gcp_tips, cost_tips, pfma_tips)

        Returns:
            Random tip string
        """
        dialogue = cls.load_dialogue()
        tips = dialogue["tips_and_hints"].get(tip_category, [])
        return random.choice(tips) if tips else ""

    @classmethod
    def get_module_message(
        cls, product_key: str, module_key: str, context: Optional[dict[str, Any]] = None
    ) -> dict[str, str]:
        """Get Navi's guidance message for a specific module.

        Args:
            product_key: Product key (gcp, cost_planner, pfma)
            module_key: Module key (intro, mobility, income, select_advisor, etc.)
            context: Context for formatting

        Returns:
            Dict with text, subtext, icon
        """
        dialogue = cls.load_dialogue()
        module_guidance = dialogue.get("module_guidance", {})
        product_modules = module_guidance.get(product_key, {})
        message = product_modules.get(module_key, {})

        if context:
            message = cls._format_message(message, context)

        return message

    @classmethod
    def _format_message(cls, message: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Format all strings in message dict with context."""
        formatted = {}
        for key, value in message.items():
            if isinstance(value, str):
                formatted[key] = cls._format_string(value, context)
            elif isinstance(value, list):
                formatted[key] = [
                    cls._format_string(v, context) if isinstance(v, str) else v for v in value
                ]
            elif isinstance(value, dict):
                formatted[key] = cls._format_message(value, context)
            else:
                formatted[key] = value
        return formatted

    @classmethod
    def _format_string(cls, template: str, context: dict[str, Any]) -> str:
        """Format a string template with context variables.

        Supports {name}, {tier}, {confidence}, {monthly_cost}, {runway_months}, etc.
        """
        try:
            return template.format(**context)
        except (KeyError, ValueError):
            # If formatting fails, return original string
            return template


# ============================================================================
# UI HELPERS - Render Navi messages in Streamlit
# ============================================================================


def render_navi_message(
    message: dict[str, str], show_cta: bool = True, cta_callback: Optional[Callable] = None
) -> None:
    """Render a Navi message in Streamlit.

    Args:
        message: Message dict with text, subtext, cta, icon
        show_cta: Whether to show CTA button
        cta_callback: Function to call when CTA clicked
    """
    if not HAS_STREAMLIT:
        return

    icon = message.get("icon", "🤖")
    text = message.get("text", "")
    subtext = message.get("subtext", "")
    cta = message.get("cta")

    # Message display
    st.markdown(
        f"""
        <div style="
            padding: 16px 20px;
            background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
            border-radius: 12px;
            color: white;
            margin: 16px 0;
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 28px;">{icon}</span>
                <div>
                    <div style="font-size: 16px; font-weight: 600;">{text}</div>
                    {f'<div style="font-size: 14px; opacity: 0.9; margin-top: 4px;">{subtext}</div>' if subtext else ""}
                </div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # CTA button
    if show_cta and cta:
        if st.button(
            f"→ {cta}", key=f"navi_cta_{hash(cta)}", use_container_width=True, type="primary"
        ):
            if cta_callback:
                cta_callback()


def render_navi_tip(tip: str) -> None:
    """Render a Navi tip/hint box."""
    if not HAS_STREAMLIT:
        return
    st.info(f"💡 **Navi's Tip:** {tip}")


def render_navi_boost(boost_messages: list[str]) -> None:
    """Render Navi's context boost messages."""
    if not HAS_STREAMLIT:
        return
    if boost_messages:
        st.markdown("**🤖 Here's what I know so far:**")
        for msg in boost_messages:
            st.markdown(f"- {msg}")


def render_navi_intro(intro: dict[str, Any]) -> None:
    """Render Navi's product introduction."""
    if not HAS_STREAMLIT:
        return
    welcome = intro.get("welcome", "")
    what_to_expect = intro.get("what_to_expect", [])
    navi_says = intro.get("navi_says", "")

    st.markdown(f"### 🤖 {welcome}")

    if what_to_expect:
        st.markdown("**What to expect:**")
        for item in what_to_expect:
            st.markdown(f"- {item}")

    if navi_says:
        st.info(f"**Navi says:** {navi_says}")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def show_navi_journey_phase(phase: str, context: Optional[dict[str, Any]] = None) -> None:
    """Show Navi's message for current journey phase.

    Args:
        phase: Journey phase (getting_started, in_progress, nearly_there, complete)
        context: User context (name, tier, costs, etc.)
    """
    if not HAS_STREAMLIT:
        return
    from core.state import get_user_name, is_authenticated

    # Build context
    if context is None:
        context = {}

    if is_authenticated():
        context["name"] = get_user_name() or "there"

    # Get and render message
    message = NaviDialogue.get_journey_message(phase, is_authenticated(), context)
    render_navi_message(message)

    # Show context boost if available
    boost = NaviDialogue.get_context_boost(phase, context)
    if boost:
        render_navi_boost(boost)


def show_navi_product_intro(product_key: str, context: Optional[dict[str, Any]] = None) -> None:
    """Show Navi's introduction when starting a product.

    Args:
        product_key: Product key (gcp_start, cost_start, pfma_start)
        context: Context for formatting
    """
    if not HAS_STREAMLIT:
        return
    intro = NaviDialogue.get_product_intro(product_key, context)
    render_navi_intro(intro)


def show_navi_gate(product_key: str) -> None:
    """Show Navi's gate message when product is locked.

    Args:
        product_key: Product key (gcp_locked, cost_locked, pfma_locked)
    """
    if not HAS_STREAMLIT:
        return
    gate = NaviDialogue.get_gate_message(product_key)
    message = {
        "text": gate.get("message", ""),
        "subtext": gate.get("encouragement", ""),
        "cta": gate.get("action", ""),
        "icon": "🔒",
    }
    render_navi_message(message)


def show_navi_micro_moment(moment_type: str, context: Optional[dict[str, Any]] = None) -> None:
    """Show a quick Navi micro-moment message.

    Args:
        moment_type: Moment type (progress_save, product_unlock, achievement_earned, etc.)
        context: Context for formatting
    """
    if not HAS_STREAMLIT:
        return
    message = NaviDialogue.get_micro_moment(moment_type, context)
    if message:
        st.success(f"🤖 {message}")


def show_navi_module_guide(
    product_key: str,
    module_key: str,
    context: Optional[dict[str, Any]] = None,
    show_progress: bool = False,
    current_step: Optional[int] = None,
    total_steps: Optional[int] = None,
) -> None:
    """Show Navi's persistent guide bar for current module.

    This is the key integration point - call this at the top of EVERY module
    to give users contextual guidance about what they're doing and why.

    Args:
        product_key: Product key (gcp, cost_planner, pfma)
        module_key: Module key (intro, mobility, income, select_advisor, etc.)
        context: Context for formatting (name, tier, costs, etc.)
        show_progress: Whether to show progress indicator
        current_step: Current step number
        total_steps: Total steps

    Example:
        # At top of GCP mobility module
        show_navi_module_guide("gcp", "mobility", show_progress=True, current_step=1, total_steps=5)

        # At top of Cost Planner income step
        show_navi_module_guide("cost_planner", "income", context={"tier": "Assisted Living"})
    """
    if not HAS_STREAMLIT:
        return

    from core.ui import render_navi_guide_bar

    # Get module message
    message = NaviDialogue.get_module_message(product_key, module_key, context)

    if not message:
        return

    # Render guide bar
    render_navi_guide_bar(
        text=message.get("text", ""),
        subtext=message.get("subtext"),
        icon=message.get("icon", "🤖"),
        show_progress=show_progress,
        current_step=current_step,
        total_steps=total_steps,
    )
