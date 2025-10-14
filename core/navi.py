"""
Navi - The Single Intelligence Layer

Navi is THE canonical intelligence layer that owns:
- Journey coordination across all products
- Next-best action recommendations  
- Dynamic Q&A and suggested questions
- Additional Services orchestration
- Flag aggregation and context-aware guidance

Navi replaces and deprecates:
- Hub Guide (orchestration layer)
- Standalone MCIP journey status (consolidated here)
- Module progress bars (Navi IS the progress indicator)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import streamlit as st

from core.mcip import MCIP
from core.flags import get_all_flags
from core.state import is_authenticated, get_user_name


@dataclass
class NaviContext:
    """Complete context for Navi's intelligence.
    
    This is what Navi knows about the user's journey.
    """
    # Journey state
    progress: Dict[str, Any]  # From MCIP.get_journey_progress()
    next_action: Dict[str, str]  # From MCIP.get_recommended_next_action()
    
    # Product outcomes
    care_recommendation: Optional[Any] = None
    financial_profile: Optional[Any] = None
    advisor_appointment: Optional[Any] = None
    
    # Flags and context
    flags: Dict[str, bool] = None
    user_name: str = ""
    is_authenticated: bool = False
    
    # Location context
    location: str = "hub"  # "hub" or "product"
    hub_key: Optional[str] = None
    product_key: Optional[str] = None
    module_step: Optional[int] = None
    module_total: Optional[int] = None


class NaviOrchestrator:
    """Central coordinator for Navi's intelligence."""
    
    @staticmethod
    def get_context(
        location: str = "hub",
        hub_key: Optional[str] = None,
        product_key: Optional[str] = None,
        module_config: Optional[Any] = None
    ) -> NaviContext:
        """Get complete Navi context for current location.
        
        Args:
            location: "hub" or "product"
            hub_key: Hub identifier (for hub pages)
            product_key: Product identifier (for product pages)
            module_config: Module config (for product pages)
        
        Returns:
            NaviContext with all intelligence data
        """
        # Get journey state from MCIP
        progress = MCIP.get_journey_progress()
        next_action = MCIP.get_recommended_next_action()
        
        # Get product outcomes
        care_rec = None
        financial = None
        appointment = None
        
        try:
            care_rec = MCIP.get_care_recommendation()
        except:
            pass
        
        try:
            financial = MCIP.get_financial_profile()
        except:
            pass
        
        try:
            appointment = MCIP.get_advisor_appointment()
        except:
            pass
        
        # Get flags
        flags = get_all_flags()
        
        # Get user context
        user_name = get_user_name() or ""
        is_auth = is_authenticated()
        
        # Get module context if in product
        module_step = None
        module_total = None
        if location == "product" and module_config:
            state_key = module_config.state_key
            module_step = st.session_state.get(f"{state_key}._step", 0)
            module_total = len(module_config.steps)
        
        return NaviContext(
            progress=progress,
            next_action=next_action,
            care_recommendation=care_rec,
            financial_profile=financial,
            advisor_appointment=appointment,
            flags=flags,
            user_name=user_name,
            is_authenticated=is_auth,
            location=location,
            hub_key=hub_key,
            product_key=product_key,
            module_step=module_step,
            module_total=module_total
        )
    
    @staticmethod
    def get_next_action(ctx: NaviContext) -> Dict[str, str]:
        """Get next-best action for user.
        
        Args:
            ctx: Navi context
        
        Returns:
            Dict with action, reason, route, icon
        """
        # Use MCIP's existing recommendation
        return ctx.next_action
    
    @staticmethod
    def get_suggested_questions(flags: Dict[str, bool], completed_products: List[str]) -> List[str]:
        """Get 3 dynamic question chips based on flags and progress.
        
        Args:
            flags: Current flag set
            completed_products: List of completed product keys
        
        Returns:
            List of 3 suggested questions
        """
        questions = []
        
        # Flag-based questions
        if flags.get("veteran"):
            questions.append("Can I use VA benefits for senior care?")
        
        if flags.get("fall_risk"):
            questions.append("What services help prevent falls at home?")
        
        if flags.get("memory_concerns"):
            questions.append("What's the difference between Assisted Living and Memory Care?")
        
        if flags.get("financial_strain"):
            questions.append("What if I can't afford the recommended care level?")
        
        # Progress-based questions
        if "gcp" in completed_products:
            if "cost_planner" not in completed_products:
                questions.append("How much will my recommended care level cost?")
            else:
                questions.append("When should I start looking for facilities?")
        
        # Default starter questions (if we don't have 3 yet)
        default_questions = [
            "What level of care is right for me?",
            "How do I pay for senior care?",
            "What's the difference between Independent and Assisted Living?",
            "How do I choose the right facility?",
            "What questions should I ask during facility tours?"
        ]
        
        # Add defaults until we have 3
        for q in default_questions:
            if q not in questions:
                questions.append(q)
            if len(questions) >= 3:
                break
        
        return questions[:3]
    
    @staticmethod
    def get_additional_services(flags: Dict[str, bool]) -> List[str]:
        """Get recommended Additional Services based on flags.
        
        Maps flags → service tags → partner keys.
        
        Args:
            flags: Current flag set
        
        Returns:
            List of recommended service keys in priority order
        """
        services = []
        
        # Map flags to service keys
        # These should match keys in config/partners.json
        
        if flags.get("veteran"):
            services.append("veterans_benefits")
        
        if flags.get("fall_risk") or flags.get("mobility_concerns"):
            services.append("omcare")
        
        if flags.get("memory_concerns") or flags.get("cognitive_decline"):
            services.append("memory_care_specialists")
        
        if flags.get("financial_strain") or flags.get("low_runway"):
            services.append("financial_planning")
        
        # Always show SeniorLife AI as an option
        if "senior_life_ai" not in services:
            services.append("senior_life_ai")
        
        # Default services (if none matched)
        if not services:
            services = ["senior_life_ai", "omcare", "facility_tours"]
        
        return services[:5]  # Limit to top 5
    
    @staticmethod
    def get_context_summary(ctx: NaviContext) -> str:
        """Get context-aware summary text for Navi panel.
        
        Args:
            ctx: Navi context
        
        Returns:
            Summary text
        """
        completed = ctx.progress["completed_count"]
        total = 3
        
        if completed == 0:
            if ctx.is_authenticated:
                return f"Hey {ctx.user_name}! Let's get started on your senior care plan."
            else:
                return "Hey there! Let's get started on your senior care plan."
        
        elif completed == 1:
            if ctx.care_recommendation:
                tier = ctx.care_recommendation.recommended_tier
                return f"Great progress! You've chosen {tier}. Now let's figure out the costs."
            else:
                return "Great progress! 1/3 complete. Keep going!"
        
        elif completed == 2:
            return f"Almost done! 2/3 complete. Just schedule your advisor appointment."
        
        else:  # completed == 3
            return "🎉 Journey complete! You've planned your care, calculated costs, and booked your appointment."
    
    @staticmethod
    def get_context_boost(ctx: NaviContext) -> List[str]:
        """Get context boost bullets (what we know so far).
        
        Args:
            ctx: Navi context
        
        Returns:
            List of context statements
        """
        boost = []
        
        if ctx.care_recommendation:
            tier = ctx.care_recommendation.recommended_tier
            confidence = int(ctx.care_recommendation.confidence_score * 100)
            boost.append(f"✅ Care Plan: {tier} ({confidence}% confidence)")
        
        if ctx.financial_profile:
            monthly = ctx.financial_profile.monthly_cost
            runway = ctx.financial_profile.runway_months
            boost.append(f"✅ Cost Estimate: ${monthly:,.0f}/month ({runway} month runway)")
        
        if ctx.advisor_appointment:
            advisor_type = getattr(ctx.advisor_appointment, 'advisor_type', 'Financial Advisor')
            boost.append(f"✅ Appointment Scheduled: {advisor_type}")
        
        return boost


def render_navi_panel(
    location: str = "hub",
    hub_key: Optional[str] = None,
    product_key: Optional[str] = None,
    module_config: Optional[Any] = None
) -> NaviContext:
    """Render Navi panel at canonical location.
    
    This is THE single intelligence layer. It replaces:
    - Hub Guide (orchestration)
    - MCIP journey status (consolidated here)
    - Module progress bars (Navi IS the progress)
    
    Args:
        location: "hub" or "product"
        hub_key: Hub identifier (for hub pages)
        product_key: Product identifier (for product pages)  
        module_config: Module config (for product pages)
    
    Returns:
        NaviContext for downstream use
    """
    from core.ui import render_navi_guide_bar
    from core.nav import route_to
    
    # Get complete context
    ctx = NaviOrchestrator.get_context(location, hub_key, product_key, module_config)
    
    # Get guidance text based on location
    if location == "hub":
        # Hub-level guidance
        summary = NaviOrchestrator.get_context_summary(ctx)
        next_action = ctx.next_action
        
        # Render main panel
        render_navi_guide_bar(
            text=f"🤖 Navi: {next_action['action']}",
            subtext=next_action['reason'],
            icon=next_action.get('icon', '🧭'),
            show_progress=True,
            current_step=ctx.progress['completed_count'],
            total_steps=3
        )
        
        # Context boost (what we know)
        boost = NaviOrchestrator.get_context_boost(ctx)
        if boost:
            st.markdown("**🤖 Here's what I know so far:**")
            for item in boost:
                st.markdown(f"- {item}")
        
        # CTA to FAQs for questions (don't show question chips in Navi - keep focused on mission)
        num_suggested = len(NaviOrchestrator.get_suggested_questions(ctx.flags, ctx.progress['completed_products']))
        if num_suggested > 0:
            st.markdown(f"**💬 Have questions?** I have {num_suggested} personalized answers ready for you.")
            if st.button("Ask Navi →", key="navi_faq_cta", type="secondary", use_container_width=True):
                route_to("faq")
    
    elif location == "product":
        # Product/module-level guidance
        # Check if module has embedded guidance
        if module_config and ctx.module_step is not None:
            current_step_def = module_config.steps[ctx.module_step]
            
            # Use embedded guidance if available
            if hasattr(current_step_def, 'navi_guidance') and current_step_def.navi_guidance:
                guidance = current_step_def.navi_guidance
                render_navi_guide_bar(
                    text=guidance.get('text', ''),
                    subtext=guidance.get('subtext'),
                    icon=guidance.get('icon', '🤖'),
                    show_progress=True,
                    current_step=ctx.module_step + 1,
                    total_steps=ctx.module_total,
                    color=guidance.get('color', '#8b5cf6')
                )
            else:
                # Fallback to generic progress
                render_navi_guide_bar(
                    text=f"🤖 Navi: {current_step_def.title}",
                    subtext="I'm here to help you through each step.",
                    icon="🧭",
                    show_progress=True,
                    current_step=ctx.module_step + 1,
                    total_steps=ctx.module_total
                )
    
    return ctx


__all__ = [
    "NaviContext",
    "NaviOrchestrator",
    "render_navi_panel"
]
