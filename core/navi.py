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
        """Get 3 suggested questions based on current flags and progress.
        
        Maps GCP module flags to relevant FAQ questions.
        
        Args:
            flags: Current flag set (from get_all_flags()) - uses GCP module flag names
            completed_products: List of completed product keys
        
        Returns:
            List of 3 question strings
        """
        questions = []
        
        # SAFETY & MOBILITY FLAGS (Priority 1 - most urgent)
        if flags.get("falls_multiple") or flags.get("high_safety_concern"):
            questions.append("How can I reduce fall risk at home?")
        
        if flags.get("moderate_mobility") or flags.get("high_mobility_dependence"):
            questions.append("What mobility aids and modifications can help at home?")
        
        # COGNITIVE FLAGS (Priority 1 - urgent)
        if flags.get("severe_cognitive_risk") or flags.get("moderate_cognitive_decline"):
            questions.append("What's the difference between Memory Care and Assisted Living?")
        
        if flags.get("moderate_safety_concern") and (flags.get("moderate_cognitive_decline") or flags.get("severe_cognitive_risk")):
            questions.append("What specialized care is available for dementia or Alzheimer's?")
        
        # VETERAN FLAGS (Priority 2 - important benefits)
        if flags.get("veteran_aanda_risk"):
            questions.append("Am I eligible for VA Aid & Attendance benefits?")
        
        # DEPENDENCE & CARE FLAGS (Priority 2)
        if flags.get("moderate_dependence") or flags.get("high_dependence"):
            if not any(q in questions for q in ["What's the difference between Memory Care and Assisted Living?"]):
                questions.append("What level of in-home care or facility care do I need?")
        
        # MEDICATION & CHRONIC CONDITIONS
        if flags.get("chronic_present"):
            questions.append("Who can help manage medications safely?")
        
        # MENTAL HEALTH FLAGS
        if flags.get("mental_health_concern") or flags.get("high_risk"):
            questions.append("How do I find emotional support and mental health services?")
        
        # ISOLATION & ACCESS FLAGS
        if flags.get("geo_isolated") or flags.get("very_low_access"):
            questions.append("What services are available in remote or rural areas?")
        
        # SUPPORT FLAGS
        if flags.get("no_support") or flags.get("limited_support"):
            questions.append("How do I find and hire reliable caregivers?")
        
        # Progress-based questions
        if "gcp" in completed_products or "gcp_v4" in completed_products:
            if "cost_planner" not in completed_products and "cost_v2" not in completed_products:
                questions.append("How much will my recommended care level cost?")
            else:
                questions.append("When should I start looking for facilities?")
        
        # Default starter questions (if we don't have 3 yet)
        # DISABLED until PFMA module is complete - keep users focused on primary flow
        # default_questions = [
        #     "What level of care is right for me?",
        #     "How do I pay for senior care?",
        #     "What's the difference between Independent and Assisted Living?",
        #     "How do I choose the right facility?",
        #     "What questions should I ask during facility tours?"
        # ]
        # 
        # # Add defaults until we have 3
        # for q in default_questions:
        #     if q not in questions:
        #         questions.append(q)
        #     if len(questions) >= 3:
        #         break
        
        return questions[:3]
    
    @staticmethod
    def get_additional_services(flags: Dict[str, bool]) -> List[str]:
        """Get recommended Additional Services based on flags.
        
        Maps GCP module flags → service tags → partner keys.
        
        Args:
            flags: Current flag set (uses GCP module flag names)
        
        Returns:
            List of recommended service keys in priority order
        """
        services = []
        
        # Map GCP module flags to service keys
        # These should match keys in config/partners.json
        
        # Veteran benefits
        if flags.get("veteran_aanda_risk"):
            services.append("veterans_benefits")
        
        # Mobility & fall prevention
        if flags.get("falls_multiple") or flags.get("high_safety_concern") or flags.get("moderate_mobility") or flags.get("high_mobility_dependence"):
            services.append("omcare")
        
        # Memory care & cognitive support
        if flags.get("moderate_cognitive_decline") or flags.get("severe_cognitive_risk") or flags.get("moderate_safety_concern"):
            services.append("memory_care_specialists")
        
        # Financial planning (if financial flags exist from cost planner)
        if flags.get("financial_strain") or flags.get("low_runway") or flags.get("financial_gap"):
            services.append("financial_planning")
        
        # Mental health support
        if flags.get("mental_health_concern") or flags.get("high_risk"):
            services.append("mental_health_services")
        
        # Home modifications for dependence
        if flags.get("moderate_dependence") or flags.get("high_dependence"):
            services.append("home_modifications")
        
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
                tier = ctx.care_recommendation.tier
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
            tier = ctx.care_recommendation.tier
            confidence = int(ctx.care_recommendation.confidence * 100)
            boost.append(f"✅ Care Plan: {tier} ({confidence}% confidence)")
        
        if ctx.financial_profile:
            monthly = ctx.financial_profile.estimated_monthly_cost
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
    from core.ui import render_navi_guide_bar, render_navi_panel_v2
    from core.nav import route_to
    from core.navi_dialogue import NaviDialogue
    
    # Get complete context
    ctx = NaviOrchestrator.get_context(location, hub_key, product_key, module_config)
    
    # Get guidance text based on location
    if location == "hub":
        # Hub-level guidance - use NEW V2 panel design
        completed_count = ctx.progress.get('completed_count', 0)
        
        # Determine journey phase
        if completed_count == 0:
            phase = "getting_started"
        elif completed_count == 3:
            phase = "complete"
        elif completed_count == 2:
            phase = "nearly_there"
        else:
            phase = "in_progress"
        
        # Get contextual message from dialogue system
        journey_msg = NaviDialogue.get_journey_message(
            phase=phase,
            is_authenticated=ctx.is_authenticated,
            context={
                'name': ctx.user_name,
                'tier': ctx.care_recommendation.tier if ctx.care_recommendation else None,
                'completed_count': completed_count
            }
        )
        
        # Build title (personalized)
        if ctx.user_name:
            title = f"Hey {ctx.user_name}—let's keep going." if completed_count > 0 else f"Hey {ctx.user_name}—let's get started."
        else:
            title = "Let's keep going." if completed_count > 0 else "Let's get started."
        
        # Build reason text from next action
        next_action = ctx.next_action
        reason = next_action.get('reason', 'This will help us find the right support for your situation.')
        
        # Build encouragement banner
        encouragement_icons = {
            'getting_started': '🚀',
            'in_progress': '💪',
            'nearly_there': '🎯',
            'complete': '🎉'
        }
        encouragement = {
            'icon': encouragement_icons.get(phase, '💪'),
            'text': journey_msg['text'],
            'status': phase
        }
        
        # Build context chips (achievement cards)
        context_chips = []
        
        if ctx.care_recommendation:
            tier = ctx.care_recommendation.tier
            confidence = int(ctx.care_recommendation.confidence * 100)
            context_chips.append({
                'icon': '🧭',
                'label': 'Care',
                'value': tier,
                'sublabel': f'{confidence}%'
            })
        
        if ctx.financial_profile:
            monthly = ctx.financial_profile.estimated_monthly_cost
            runway = ctx.financial_profile.runway_months
            context_chips.append({
                'icon': '💰',
                'label': 'Cost',
                'value': f'${monthly:,.0f}',
                'sublabel': f'{runway} mo'
            })
        
        if ctx.advisor_appointment:
            advisor_type = getattr(ctx.advisor_appointment, 'advisor_type', 'Financial Advisor')
            context_chips.append({
                'icon': '📅',
                'label': 'Appt',
                'value': 'Scheduled',
                'sublabel': advisor_type
            })
        else:
            context_chips.append({
                'icon': '📅',
                'label': 'Appt',
                'value': 'Not scheduled'
            })
        
        # Build primary action
        primary_label = next_action.get('label', 'Continue')
        primary_route = next_action.get('action_key', 'hub_concierge')
        primary_action = {
            'label': primary_label,
            'route': primary_route
        }
        
        # Build secondary action (Ask Navi → FAQ)
        num_suggested = len(NaviOrchestrator.get_suggested_questions(ctx.flags, ctx.progress['completed_products']))
        secondary_action = None
        if num_suggested > 0:
            secondary_action = {
                'label': 'Ask Navi →',
                'route': 'faq'
            }
        
        # Render V2 panel
        render_navi_panel_v2(
            title=title,
            reason=reason,
            encouragement=encouragement,
            context_chips=context_chips,
            primary_action=primary_action,
            secondary_action=secondary_action,
            progress={'current': completed_count, 'total': 3}
        )
    
    elif location == "product":
        # Product/module-level guidance
        # Check if module has embedded guidance
        if module_config and ctx.module_step is not None and ctx.module_total:
            # Bounds check to prevent IndexError
            if ctx.module_step < 0 or ctx.module_step >= ctx.module_total:
                # Module step out of bounds - show generic message
                render_navi_guide_bar(
                    text="🤖 Navi: Let's work through this together",
                    subtext="I'm here to guide you step by step.",
                    icon="🧭",
                    show_progress=False,
                    color="#0066cc"
                )
            else:
                current_step_def = module_config.steps[ctx.module_step]
                
                # Use embedded navi_guidance if available
                if hasattr(current_step_def, 'navi_guidance') and current_step_def.navi_guidance:
                    guidance = current_step_def.navi_guidance
                    
                    # Build message from guidance
                    main_text = None
                    subtext = None
                    
                    # Priority order for main message:
                    # 1. section_purpose (what this section does)
                    # 2. encouragement (friendly motivational text)
                    # 3. Fallback to title
                    if guidance.get('section_purpose'):
                        main_text = f"🤖 Navi: {guidance['section_purpose']}"
                    elif guidance.get('encouragement'):
                        main_text = f"🤖 Navi: {guidance['encouragement']}"
                    else:
                        main_text = f"🤖 Navi: {current_step_def.title}"
                    
                    # Priority order for subtext:
                    # 1. why_this_matters (educational/contextual)
                    # 2. what_happens_next (preview)
                    # 3. time_estimate (for intro/info pages)
                    # 4. context_note (additional details)
                    if guidance.get('why_this_matters'):
                        subtext = f"💡 {guidance['why_this_matters']}"
                    elif guidance.get('what_happens_next'):
                        subtext = guidance['what_happens_next']
                    elif guidance.get('time_estimate'):
                        subtext = f"⏱️ {guidance['time_estimate']}"
                    elif guidance.get('context_note'):
                        subtext = guidance['context_note']
                    
                    # Render with extracted guidance
                    render_navi_guide_bar(
                        text=main_text,
                        subtext=subtext,
                        icon=guidance.get('icon', '�'),
                        show_progress=True,
                        current_step=ctx.module_step + 1,
                        total_steps=ctx.module_total,
                        color=guidance.get('color', '#0066cc')
                    )
                    
                    # Show encouragement or support message as additional info
                    if guidance.get('encouragement') and guidance.get('section_purpose'):
                        # If we used section_purpose as main, show encouragement below
                        st.info(f"💬 {guidance['encouragement']}")
                    elif guidance.get('support_message'):
                        # Show support message for sensitive topics
                        st.info(f"💙 {guidance['support_message']}")
                    
                    # Show red flags warning if present (for clinicians/caregivers)
                    if guidance.get('red_flags'):
                        with st.expander("⚠️ Important Considerations"):
                            st.warning("**Watch for these combinations:**")
                            for flag in guidance['red_flags']:
                                st.markdown(f"- {flag}")
                    
                else:
                    # Fallback to generic progress
                    render_navi_guide_bar(
                        text=f"🤖 Navi: {current_step_def.title}",
                        subtext="I'm here to help you through each step.",
                        icon="🧭",
                        show_progress=True,
                        current_step=ctx.module_step + 1,
                        total_steps=ctx.module_total,
                        color="#0066cc"
                    )
        else:
            # No module config or step info - show simple guidance
            render_navi_guide_bar(
                text="🤖 Navi: I'm here to help",
                subtext="Let's work through this together.",
                icon="🧭",
                show_progress=False,
                color="#0066cc"
            )
    
    return ctx


__all__ = [
    "NaviContext",
    "NaviOrchestrator",
    "render_navi_panel"
]
