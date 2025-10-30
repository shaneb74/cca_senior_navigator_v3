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

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import streamlit as st

from core.flags import get_all_flags
from core.mcip import MCIP
from core.state import get_user_name, is_authenticated


def _get_tier_display_name(tier: str) -> str:
    """Convert internal tier name to user-friendly display name.

    Args:
        tier: Internal tier name (e.g., 'assisted_living', 'no_care_needed')

    Returns:
        User-friendly display name (e.g., 'Assisted Living', 'No Care Recommended')
    """
    tier_map = {
        "no_care_needed": "No Care Recommended",
        "independent": "Independent Living",
        "in_home": "In-Home Care",
        "in_home_care": "In-Home Care",
        "assisted_living": "Assisted Living",
        "memory_care": "Memory Care",
        "memory_care_high_acuity": "Memory Care (High Acuity)",
    }
    return tier_map.get(tier, tier.replace("_", " ").title())


@dataclass
class NaviContext:
    """Complete context for Navi's intelligence.

    This is what Navi knows about the user's journey.
    """

    # Journey state
    progress: dict[str, Any]  # From MCIP.get_journey_progress()
    next_action: dict[str, str]  # From MCIP.get_recommended_next_action()

    # Product outcomes
    care_recommendation: Any | None = None
    financial_profile: Any | None = None
    advisor_appointment: Any | None = None

    # Flags and context
    flags: dict[str, bool] = None
    user_name: str = ""
    is_authenticated: bool = False

    # Location context
    location: str = "hub"  # "hub" or "product"
    hub_key: str | None = None
    product_key: str | None = None
    module_step: int | None = None
    module_total: int | None = None


class NaviOrchestrator:
    """Central coordinator for Navi's intelligence."""

    @staticmethod
    def get_context(
        location: str = "hub",
        hub_key: str | None = None,
        product_key: str | None = None,
        module_config: Any | None = None,
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
            module_total=module_total,
        )

    @staticmethod
    def get_next_action(ctx: NaviContext) -> dict[str, str]:
        """Get next-best action for user.

        Args:
            ctx: Navi context

        Returns:
            Dict with action, reason, route, icon
        """
        # Use MCIP's existing recommendation
        return ctx.next_action

    @staticmethod
    def get_suggested_questions(flags: dict[str, bool], completed_products: list[str]) -> list[str]:
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

        if flags.get("moderate_safety_concern") and (
            flags.get("moderate_cognitive_decline") or flags.get("severe_cognitive_risk")
        ):
            questions.append("What specialized care is available for dementia or Alzheimer's?")

        # VETERAN FLAGS (Priority 2 - important benefits)
        if flags.get("veteran_aanda_risk"):
            questions.append("Am I eligible for VA Aid & Attendance benefits?")

        # DEPENDENCE & CARE FLAGS (Priority 2)
        if flags.get("moderate_dependence") or flags.get("high_dependence"):
            if not any(
                q in questions
                for q in ["What's the difference between Memory Care and Assisted Living?"]
            ):
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
    def get_additional_services(flags: dict[str, bool]) -> list[str]:
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
        if (
            flags.get("falls_multiple")
            or flags.get("high_safety_concern")
            or flags.get("moderate_mobility")
            or flags.get("high_mobility_dependence")
        ):
            services.append("omcare")

        # Memory care & cognitive support
        if (
            flags.get("moderate_cognitive_decline")
            or flags.get("severe_cognitive_risk")
            or flags.get("moderate_safety_concern")
        ):
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
                tier = _get_tier_display_name(ctx.care_recommendation.tier)
                return f"Great progress! You've chosen {tier}. Now let's figure out the costs."
            else:
                return "Great progress! 1/3 complete. Keep going!"

        elif completed == 2:
            return "Almost done! 2/3 complete. Just schedule your advisor appointment."

        else:  # completed == 3
            return "🎉 Journey complete! You've planned your care, calculated costs, and booked your appointment."

    @staticmethod
    def get_context_boost(ctx: NaviContext) -> list[str]:
        """Get context boost bullets (what we know so far).

        Args:
            ctx: Navi context

        Returns:
            List of context statements
        """
        boost = []

        if ctx.care_recommendation:
            tier = _get_tier_display_name(ctx.care_recommendation.tier)
            confidence = int(ctx.care_recommendation.confidence * 100)
            boost.append(f"✅ Care Plan: {tier} ({confidence}% confidence)")

        if ctx.financial_profile:
            # Get the detailed summary message from session state if available
            financial_data = st.session_state.get("financial_assessment_complete", {})
            timeline = financial_data.get("timeline", {})
            summary_message = timeline.get("summary_message")

            if summary_message:
                # Use the user-friendly message
                boost.append(f"✅ {summary_message}")
            else:
                # Fallback to technical format
                monthly = ctx.financial_profile.estimated_monthly_cost
                runway = ctx.financial_profile.runway_months
                boost.append(f"✅ Cost Estimate: ${monthly:,.0f}/month ({runway} month runway)")

        if ctx.advisor_appointment:
            advisor_type = getattr(ctx.advisor_appointment, "advisor_type", "Financial Advisor")
            boost.append(f"✅ Appointment Scheduled: {advisor_type}")

        return boost


def _has_diabetes_condition() -> bool:
    """Check if user has diabetes as a chronic condition.

    Checks:
    1. Primary: medical.conditions.chronic[] contains diabetes
    2. Alternate: chronic_present flag + diabetes in conditions

    Returns:
        True if diabetes condition is present
    """
    try:
        from core.flag_manager import get_active, get_chronic_conditions

        # Check chronic conditions list for diabetes
        conditions = get_chronic_conditions()
        for condition in conditions:
            if condition.get("code") == "diabetes":
                return True

        # Alternate: check if chronic_present flag active AND diabetes in list
        active_flags = get_active()
        if "chronic_present" in active_flags:
            for condition in conditions:
                code = condition.get("code", "").lower()
                if "diabetes" in code or "diabetic" in code:
                    return True

        return False
    except Exception:
        # Graceful degradation if flag_manager unavailable
        return False


def render_navi_panel(
    location: str = "hub",
    hub_key: str | None = None,
    product_key: str | None = None,
    module_config: Any | None = None,
) -> NaviContext:
    """Render Navi panel at canonical location.

    This is THE single intelligence layer. It replaces:
    - Hub Guide (orchestration)
    - MCIP journey status (consolidated here)
    - Module progress bars (Navi IS the progress)
    
    Enhanced with LLM-powered contextual advice generation.

    Args:
        location: "hub" or "product"
        hub_key: Hub identifier (for hub pages)
        product_key: Product identifier (for product pages)
        module_config: Module config (for product pages)

    Returns:
        NaviContext for downstream use
    """
    from core.navi_dialogue import NaviDialogue, render_navi_enhanced_panel
    from core.ui import render_navi_panel_v2
    from core.flags import get_flag_value

    # Get complete context
    ctx = NaviOrchestrator.get_context(location, hub_key, product_key, module_config)

    # LLM enhancement will integrate with existing UI, not replace it
    # We'll enhance the content that gets passed to the existing beautiful UI functions
    # Get guidance text based on location
    if location == "hub":
        # ============================================================
        # PROFESSIONAL HUB - DEMO-ONLY SCOPE
        # ============================================================
        # Professional-specific Navi that references Professional Hub cards only
        # This does not affect Member Hub, Cost Planner, FAQs, or any other Navi instances
        if hub_key == "professional":
            # Professional-specific content
            title = "Your professional dashboard"
            reason = "Manage your caseload, track referrals, and coordinate care for your clients."

            encouragement = {
                "icon": "💼",
                "text": "Everything you need to support your patients and families.",
                "status": "professional",
            }

            # Professional context chips - showing caseload snapshot
            context_chips = [
                {"icon": "📊", "label": "Pending", "value": "7", "sublabel": "actions"},
                {"icon": "🆕", "label": "Referrals", "value": "3", "sublabel": "today"},
                {"icon": "📝", "label": "Updates", "value": "5", "sublabel": "needed"},
            ]

            # Primary action - Open Dashboard (demo, non-functional)
            primary_action = {"label": "Open Dashboard", "route": "hub_professional"}

            # Secondary action - CRM Query Engine (demo, non-functional)
            secondary_action = {"label": "Open CRM →", "route": "hub_professional"}

            # No progress bar for Professional Hub (not journey-based)
            # No alert HTML for Professional Hub

            # Render Professional-specific V2 panel
            render_navi_panel_v2(
                title=title,
                reason=reason,
                encouragement=encouragement,
                context_chips=context_chips,
                primary_action=primary_action,
                secondary_action=secondary_action,
                progress=None,  # No progress bar for Professional Hub
                alert_html="",  # No alerts for Professional Hub
            )

            return ctx

        # ============================================================
        # WAITING ROOM HUB - POST-CONCIERGE PROGRESSION
        # ============================================================
        if hub_key == "waiting_room":
            # Get Waiting Room tracking state from MCIP
            wr_state = MCIP.get_waiting_room_state()
            advisor_prep_status = wr_state.get("advisor_prep_status", "not_started")
            trivia_status = wr_state.get("trivia_status", "not_started")
            current_focus = wr_state.get("current_focus", "advisor_prep")

            # Determine guidance state (6 possible states based on spec)
            if advisor_prep_status == "not_started":
                wr_phase = "advisor_prep_not_started"
            elif advisor_prep_status == "in_progress":
                wr_phase = "advisor_prep_in_progress"
            elif advisor_prep_status == "complete" and trivia_status == "not_started":
                wr_phase = "advisor_prep_complete_trivia_not_started"
            elif trivia_status == "in_progress":
                wr_phase = "trivia_in_progress"
            elif trivia_status == "complete":
                wr_phase = "trivia_complete"
            else:
                wr_phase = "advisor_prep_not_started"  # Default fallback

            # Map phase to title, reason, CTA
            wr_messages = {
                "advisor_prep_not_started": {
                    "title": "🪑 Welcome to your Waiting Room!",
                    "reason": "Let's start by preparing for your advisor call. It only takes a few minutes and helps your advisor personalize your session.",
                    "cta_label": "Start Prep",
                    "cta_route": "advisor_prep",
                    "encouragement": "This is where you can prepare, play, and explore while you wait.",
                },
                "advisor_prep_in_progress": {
                    "title": "Nice progress on your prep!",
                    "reason": "You've completed some prep sections. Want to finish them up before your call?",
                    "cta_label": "Continue Prep",
                    "cta_route": "advisor_prep",
                    "encouragement": "You're doing great—let's finish this up!",
                },
                "advisor_prep_complete_trivia_not_started": {
                    "title": "Great work! You're ready for your call.",
                    "reason": "While you wait, want to play a few Trivia games to learn more about your care topics?",
                    "cta_label": "Play Trivia",
                    "cta_route": "senior_trivia",
                    "encouragement": "Test your knowledge and have some fun!",
                },
                "trivia_in_progress": {
                    "title": "Keep it up!",
                    "reason": "Each trivia round helps us learn more about what's relevant to you.",
                    "cta_label": "Resume Trivia",
                    "cta_route": "senior_trivia",
                    "encouragement": "You're on a roll—let's keep going!",
                },
                "trivia_complete": {
                    "title": "🎉 You've finished your prep and trivia!",
                    "reason": "Explore other resources while you wait for your appointment.",
                    "cta_label": "Explore Learning Center",
                    "cta_route": "educational_feed",
                    "encouragement": "You're all set! Feel free to browse around.",
                },
            }

            wr_msg = wr_messages.get(wr_phase, wr_messages["advisor_prep_not_started"])

            # Build context chips for Waiting Room
            context_chips = []

            # Appointment chip
            if ctx.advisor_appointment:
                appt_date = ctx.advisor_appointment.date
                context_chips.append(
                    {
                        "icon": "📅",
                        "label": "Appt",
                        "value": appt_date,
                        "sublabel": ctx.advisor_appointment.time,
                    }
                )

            # Prep status chip
            prep_summary = MCIP.get_advisor_prep_summary()
            if prep_summary.get("available"):
                progress = prep_summary.get("progress", 0)
                sections_complete = len(prep_summary.get("sections_complete", []))

                # Get duck progress (local import to avoid circular dependency)
                try:
                    from products.waiting_room.advisor_prep.utils import get_duck_progress, is_all_ducks_earned

                    duck_progress = get_duck_progress()
                    duck_count = duck_progress["earned_count"]

                    # Build chip display
                    if is_all_ducks_earned():
                        chip_value = "🦆🦆🦆🦆"
                        chip_sublabel = "All Ducks!"
                    elif duck_count > 0:
                        chip_value = "🦆" * duck_count
                        chip_sublabel = f"{sections_complete}/4 sections"
                    else:
                        chip_value = f"{sections_complete}/4"
                        chip_sublabel = f"{progress}%"
                except ImportError:
                    # Fallback if utils not available
                    chip_value = "Complete" if progress == 100 else f"{sections_complete}/4"
                    chip_sublabel = f"{progress}%"

                context_chips.append(
                    {"icon": "📝", "label": "Prep", "value": chip_value, "sublabel": chip_sublabel}
                )

            # Trivia status chip (if any games played)
            tiles = st.session_state.get("product_tiles_v2", {})
            trivia_progress = tiles.get("senior_trivia_hub", {})
            badges_earned = trivia_progress.get("badges_earned", {})
            if badges_earned:
                context_chips.append(
                    {
                        "icon": "🎮",
                        "label": "Trivia",
                        "value": f"{len(badges_earned)}/5",
                        "sublabel": "quizzes",
                    }
                )

            # Build encouragement banner
            encouragement_text = wr_msg["encouragement"]

            # Check for condition-triggered trivia unlocks
            diabetes_badge = badges_earned.get("diabetes_knowledge")
            if _has_diabetes_condition() and not diabetes_badge:
                encouragement_text = "Since we know you're managing diabetes, I've unlocked a quick trivia game about healthy habits and glucose management. Want to give it a try?"

            encouragement = {"icon": "💪", "text": encouragement_text, "status": "in_progress"}

            # Primary action
            primary_action = {"label": wr_msg["cta_label"], "route": wr_msg["cta_route"]}

            # Secondary action (optional)
            secondary_action = None

            # No progress bar for Waiting Room (not linear journey)
            # No alert HTML for Waiting Room

            # Render Waiting Room V2 panel
            render_navi_panel_v2(
                title=wr_msg["title"],
                reason=wr_msg["reason"],
                encouragement=encouragement,
                context_chips=context_chips,
                primary_action=primary_action,
                secondary_action=secondary_action,
                progress=None,  # No progress bar for Waiting Room
                alert_html="",  # No alerts
            )

            return ctx

        # ============================================================
        # MEMBER HUB (CONCIERGE) - EXISTING LOGIC UNCHANGED
        # ============================================================
        # Hub-level guidance - use NEW V2 panel design
        completed_count = ctx.progress.get("completed_count", 0)

        # Check if PFMA is complete (Concierge journey finished)
        pfma_complete = ctx.advisor_appointment and ctx.advisor_appointment.scheduled

        # Determine journey phase
        if pfma_complete:
            phase = "concierge_complete"
        elif completed_count == 0:
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
                "name": ctx.user_name,
                "tier": ctx.care_recommendation.tier if ctx.care_recommendation else None,
                "completed_count": completed_count,
            },
        )

        # Build title (personalized)
        if ctx.user_name:
            title = (
                f"Hey {ctx.user_name}—let's keep going."
                if completed_count > 0
                else f"Hey {ctx.user_name}—let's get started."
            )
        else:
            title = "Let's keep going." if completed_count > 0 else "Let's get started."

        # Build reason text from next action
        next_action = ctx.next_action
        reason = next_action.get(
            "reason", "This will help us find the right support for your situation."
        )

        # Build incomplete GCP alert if applicable
        alert_html = ""
        tiles = st.session_state.get("tiles", {})
        gcp_tile = tiles.get("gcp_v4") or tiles.get("gcp", {})
        gcp_progress = float(gcp_tile.get("progress", 0))

        # Show alert if GCP is started but not complete (progress > 0 but < 100)
        if 0 < gcp_progress < 100:
            alert_html = f"""
            <div style="background: #fef3c7; border: 1px solid #fde68a; border-radius: 12px; padding: 16px; margin-bottom: 20px; display: flex; align-items: start; gap: 12px;">
                <span style="font-size: 20px;">⚠️</span>
                <div style="flex: 1;">
                    <div style="font-weight: 700; color: #78350f; margin-bottom: 4px;">Your Care Plan is {int(gcp_progress)}% complete.</div>
                    <div style="font-size: 14px; color: #92400e;">Finish it to unlock Cost Planner and personalized recommendations.</div>
                    <a href="?route=gcp_v4" style="display: inline-flex; align-items: center; justify-content: center; height: 36px; padding: 0 16px; margin-top: 8px; border-radius: 8px; background: #fbbf24; color: #78350f; font-weight: 700; font-size: 14px; text-decoration: none; border: 1px solid #f59e0b;">Resume Care Plan</a>
                </div>
            </div>
            """

        # Build encouragement banner
        encouragement_icons = {
            "getting_started": "🚀",
            "in_progress": "💪",
            "nearly_there": "🎯",
            "complete": "🎉",
            "concierge_complete": "🎉",
        }
        encouragement = {
            "icon": encouragement_icons.get(phase, "💪"),
            "text": journey_msg.get("text", ""),
            "status": phase,
        }

        # Build context chips (achievement cards)
        context_chips = []

        if ctx.care_recommendation:
            tier = _get_tier_display_name(ctx.care_recommendation.tier)
            confidence = int(ctx.care_recommendation.confidence * 100)
            context_chips.append(
                {"icon": "🧭", "label": "Care", "value": tier, "sublabel": f"{confidence}%"}
            )

        if ctx.financial_profile:
            monthly = ctx.financial_profile.estimated_monthly_cost
            runway = ctx.financial_profile.runway_months
            context_chips.append(
                {
                    "icon": "💰",
                    "label": "Cost",
                    "value": f"${monthly:,.0f}",
                    "sublabel": f"{runway} mo",
                }
            )

        if ctx.advisor_appointment:
            appt_date = ctx.advisor_appointment.date
            context_chips.append(
                {
                    "icon": "📅",
                    "label": "Appt",
                    "value": appt_date,
                    "sublabel": ctx.advisor_appointment.time,
                }
            )
        else:
            context_chips.append({"icon": "📅", "label": "Appt", "value": "Not scheduled"})

        # Build primary action - special handling for concierge_complete
        if phase == "concierge_complete":
            # Concierge complete - route to Waiting Room
            title = journey_msg.get("text", "Congratulations!")
            reason = journey_msg.get("subtext", "You've completed the Concierge journey.")
            primary_action = {"label": "Go to Waiting Room", "route": "hub_waiting"}
        else:
            # Standard title and action logic
            if ctx.user_name:
                title = (
                    f"Hey {ctx.user_name}—let's keep going."
                    if completed_count > 0
                    else f"Hey {ctx.user_name}—let's get started."
                )
            else:
                title = "Let's keep going." if completed_count > 0 else "Let's get started."

            reason = next_action.get(
                "reason", "This will help us find the right support for your situation."
            )
            primary_label = next_action.get("action", "Continue")
            primary_route = next_action.get("route", "hub_lobby")
            primary_action = {"label": primary_label, "route": primary_route}

        # Build secondary action (Ask Navi → FAQ)

        # Build secondary action (Ask Navi → FAQ)
        num_suggested = len(
            NaviOrchestrator.get_suggested_questions(ctx.flags, ctx.progress["completed_products"])
        )
        secondary_action = None
        if num_suggested > 0:
            secondary_action = {
                "label": "Ask Navi →",
                "route": "faq",  # Points to AI Advisor chat
            }

        # Render V2 panel
        render_navi_panel_v2(
            title=title,
            reason=reason,
            encouragement=encouragement,
            context_chips=context_chips,
            primary_action=primary_action,
            secondary_action=secondary_action,
            progress={"current": completed_count, "total": 3},
            alert_html=alert_html,  # Pass alert to panel renderer
        )

    elif location == "product":
        # Product/module-level guidance using V2 panel with module variant
        # Check if module has embedded guidance
        if module_config and ctx.module_step is not None and ctx.module_total:
            # Bounds check to prevent IndexError
            if ctx.module_step < 0 or ctx.module_step >= ctx.module_total:
                # Module step out of bounds - show generic message
                render_navi_panel_v2(
                    title="Let's work through this together",
                    reason="I'm here to guide you step by step.",
                    encouragement={
                        "icon": "💪",
                        "text": "Take your time—we'll get through this.",
                        "status": "in_progress",
                    },
                    context_chips=[],
                    primary_action={"label": "", "route": ""},
                    variant="module",
                )
            else:
                current_step_def = module_config.steps[ctx.module_step]

                # Use embedded navi_guidance if available
                if hasattr(current_step_def, "navi_guidance") and current_step_def.navi_guidance:
                    guidance = current_step_def.navi_guidance

                    # Build title from guidance
                    # Priority order: section_purpose → title
                    if guidance.get("section_purpose"):
                        title = guidance["section_purpose"]
                    else:
                        title = current_step_def.title

                    # Build reason text from guidance
                    # Priority order: why_this_matters → what_happens_next → context_note
                    reason = ""
                    if guidance.get("why_this_matters"):
                        reason = guidance["why_this_matters"]
                    elif guidance.get("what_happens_next"):
                        reason = guidance["what_happens_next"]
                    elif guidance.get("context_note"):
                        reason = guidance["context_note"]
                    elif guidance.get("time_estimate"):
                        reason = f"This should take about {guidance['time_estimate']}."
                    else:
                        reason = "Let's gather some important information."

                    # Build encouragement
                    encouragement_text = guidance.get(
                        "encouragement", "You're making great progress!"
                    )
                    encouragement = {
                        "icon": guidance.get("icon", "💪"),
                        "text": encouragement_text,
                        "status": "in_progress",
                    }

                    # Check if this is the results step
                    is_results = (
                        module_config.results_step_id
                        and current_step_def.id == module_config.results_step_id
                    )

                    # Build progress dict (hide on results page)
                    progress = (
                        None
                        if is_results
                        else {"current": ctx.module_step + 1, "total": ctx.module_total}
                    )

                    # Render V2 panel with module variant
                    render_navi_panel_v2(
                        title=title,
                        reason=reason,
                        encouragement=encouragement,
                        context_chips=[],  # Modules don't show chips (page content is the focus)
                        primary_action={"label": "", "route": ""},  # Modules have own CTAs
                        progress=progress,
                        variant="module",
                    )

                    # Show support message for sensitive topics
                    if guidance.get("support_message"):
                        st.info(f"💙 {guidance['support_message']}")

                    # Show red flags warning if present (for clinicians/caregivers)
                    if guidance.get("red_flags"):
                        with st.expander("⚠️ Important Considerations"):
                            st.warning("**Watch for these combinations:**")
                            for flag in guidance["red_flags"]:
                                st.markdown(f"- {flag}")

                else:
                    # Fallback to generic progress
                    # Check if this is the results step
                    is_results = (
                        module_config.results_step_id
                        and current_step_def.id == module_config.results_step_id
                    )

                    progress = (
                        None
                        if is_results
                        else {"current": ctx.module_step + 1, "total": ctx.module_total}
                    )

                    render_navi_panel_v2(
                        title=current_step_def.title,
                        reason="I'm here to help you through each step.",
                        encouragement={
                            "icon": "💪",
                            "text": "You're doing great—keep going!",
                            "status": "in_progress",
                        },
                        context_chips=[],
                        primary_action={"label": "", "route": ""},
                        progress=progress,
                        variant="module",
                    )
        else:
            # No module config - check for product-specific guidance
            if product_key in ("cost_planner", "cost_v2"):
                # Cost Planner guidance - use published_tier (post-adjudication)
                g = st.session_state.get("gcp", {})
                final_tier = g.get("published_tier") or g.get("recommended_tier")
                interim = bool(st.session_state.get("_show_mc_interim_advice", False))
                
                # Generate tier display name and copy
                if interim:
                    title = "Let's look at costs"
                    reason = "I've pre-selected Assisted Living with enhanced cognitive support from your Guided Care Plan. You can explore other scenarios too."
                elif final_tier == "memory_care" or final_tier == "memory_care_high_acuity":
                    title = "Let's look at costs"
                    reason = "I've pre-selected Memory Care from your Guided Care Plan. You can explore other scenarios too."
                elif final_tier == "assisted_living":
                    title = "Let's look at costs"
                    reason = "I've pre-selected Assisted Living from your Guided Care Plan. You can explore other scenarios too."
                elif final_tier in ("in_home", "in_home_care"):
                    title = "Let's look at costs"
                    reason = "I've pre-selected In-Home Care from your Guided Care Plan. You can explore other scenarios too."
                else:
                    title = "Let's look at costs"
                    reason = "We'll help you explore different care options and their costs."

                render_navi_panel_v2(
                    title=title,
                    reason=reason,
                    encouragement={
                        "icon": "✨",
                        "text": "You can adjust details anytime to see how costs change.",
                        "status": "in_progress",
                    },
                    context_chips=[],
                    primary_action={"label": "", "route": ""},
                    variant="module",
                )
            else:
                # Generic fallback for other products
                render_navi_panel_v2(
                    title="I'm here to help",
                    reason="Let's work through this together.",
                    encouragement={
                        "icon": "💪",
                        "text": "Take your time—we'll get through this.",
                        "status": "in_progress",
                    },
                    context_chips=[],
                    primary_action={"label": "", "route": ""},
                    variant="module",
                )

    return ctx


# ============================================================================
# LLM ENHANCEMENT FUNCTIONS
# ============================================================================

def _try_llm_enhanced_panel(
    ctx: NaviContext, 
    location: str, 
    hub_key: str | None = None, 
    product_key: str | None = None
) -> bool:
    """Try to render LLM-enhanced Navi panel.
    
    Args:
        ctx: Navi context with journey state
        location: "hub" or "product" 
        hub_key: Hub identifier
        product_key: Product identifier
        
    Returns:
        True if LLM panel was rendered, False to fall back to static
    """
    try:
        import streamlit as st
        from ai.navi_llm_engine import NaviLLMEngine, build_navi_context_from_session
        from core.navi_dialogue import render_navi_message
        from core.flags import get_flag_value
        
        # Build LLM context from current session
        navi_context = build_navi_context_from_session()
        
        # Override with specific context
        navi_context.current_location = location
        if product_key:
            navi_context.current_location = product_key
            
        # Add context from NaviOrchestrator
        if ctx.care_recommendation:
            navi_context.care_tier = ctx.care_recommendation.tier
            navi_context.care_confidence = getattr(ctx.care_recommendation, 'confidence', None)
            
        if ctx.financial_profile:
            navi_context.estimated_cost = getattr(ctx.financial_profile, 'monthly_cost', None)
            navi_context.has_financial_profile = True
            
        navi_context.user_name = ctx.user_name
        navi_context.is_authenticated = ctx.is_authenticated
        
        # Add product-specific context
        navi_context.product_context = {
            "location": location,
            "hub_key": hub_key,
            "product_key": product_key,
            "progress": ctx.progress,
            "next_action": ctx.next_action
        }
        
        # Generate LLM-powered advice
        advice = NaviLLMEngine.generate_advice(navi_context)
        tips = NaviLLMEngine.generate_contextual_tips(navi_context)
        
        if advice or tips:
            # Convert advice to message format that existing UI expects
            if advice:
                # Get appropriate icon for advice tone
                tone_icons = {
                    "supportive": "🤗",
                    "encouraging": "💪", 
                    "celebratory": "🎉",
                    "urgent": "⚡",
                }
                icon = tone_icons.get(advice.tone, "🤖")
                
                advice_message = {
                    "text": advice.title,
                    "subtext": advice.message,
                    "cta": advice.guidance,
                    "icon": icon,
                    "encouragement": advice.encouragement,
                    "priority": advice.priority
                }
                
                # Use existing render_navi_message function
                render_navi_message(advice_message, show_cta=False)
            
            # Render contextual tips if available
            if tips and tips.tips:
                with st.expander("💡 Contextual Tips", expanded=True):
                    for tip in tips.tips:
                        st.markdown(f"• {tip}")
                    
                    if tips.why_this_matters:
                        st.markdown(f"\n**💡 Why this matters:** {tips.why_this_matters}")
                        
                    if tips.time_estimate:
                        st.markdown(f"**⏱️ Time needed:** {tips.time_estimate}")
            
            # Log for shadow mode
            llm_mode = get_flag_value("FEATURE_LLM_NAVI", "off")
            if llm_mode == "shadow":
                print(f"[NAVI_LLM_SHADOW] Generated advice: {advice}")
                print(f"[NAVI_LLM_SHADOW] Generated tips: {tips}")
            
            return True
            
    except Exception as e:
        print(f"[NAVI_LLM] Enhancement failed, falling back to static: {e}")
        return False
        
    return False


__all__ = ["NaviContext", "NaviOrchestrator", "render_navi_panel"]
