"""
Navi Communication Layer - Consumes MCIP Intelligence

This module is purely a presentation/communication layer that translates
MCIP's technical intelligence into user-friendly coaching messages.

CRITICAL ARCHITECTURAL BOUNDARY:
- MCIP (Multi-Contextual Intelligence Panel) = The Brain
  - Calculates all flags, tiers, confidence scores
  - Evaluates financial projections
  - Publishes standardized contracts
  
- NaviCommunicator = The Translator
  - READS flags/outcomes from MCIP (never calculates)
  - Selects appropriate coaching messages
  - Generates user-facing dialogue
  - NEVER modifies or creates intelligence

This separation ensures MCIP remains the single source of truth while
Navi provides contextual, user-friendly communication.
"""

from typing import Optional
from dataclasses import dataclass

from core.navi import NaviContext


class NaviCommunicator:
    """
    Communication layer that consumes MCIP intelligence and presents it to users.
    
    All methods READ from NaviContext (which contains MCIP data) and return
    user-facing message dictionaries. No intelligence calculation happens here.
    """
    
    @staticmethod
    def get_hub_encouragement(ctx: NaviContext) -> dict:
        """Generate flag-aware encouragement by reading MCIP's published data.
        
        Reads from:
        - ctx.care_recommendation.flags (published by MCIP)
        - ctx.care_recommendation.tier (calculated by MCIP)
        - ctx.care_recommendation.confidence (calculated by MCIP)
        - ctx.financial_profile (published by Cost Planner via MCIP)
        
        Returns: User-facing encouragement message dict with:
            - icon: str (emoji)
            - text: str (encouragement message)
            - status: str (urgent|important|planning|confident|in_progress)
        
        Priority order:
        1. Urgent flags (falls + memory + multiple risks)
        2. Financial urgency (low runway from MCIP)
        3. High confidence + low risk (positive reinforcement)
        4. Generic progress encouragement
        """
        # Read flags from MCIP (never calculate them)
        flags = ctx.care_recommendation.flags if ctx.care_recommendation else []
        tier = ctx.care_recommendation.tier if ctx.care_recommendation else None
        confidence = ctx.care_recommendation.confidence if ctx.care_recommendation else None
        
        # Check financial urgency from MCIP
        runway_months = None
        if ctx.financial_profile:
            runway_months = getattr(ctx.financial_profile, 'runway_months', None)
        
        # Message selection logic (presentation layer only)
        has_falls_risk = any(f.get('type') == 'falls_risk' and f.get('active') for f in flags)
        has_memory_support = any(f.get('type') == 'memory_support' and f.get('active') for f in flags)
        has_veteran_flag = any(f.get('type') == 'veteran_aanda_risk' and f.get('active') for f in flags)
        
        # Count active risk flags
        active_risk_count = sum(1 for f in flags if f.get('active') and 
                               f.get('type') in ['falls_risk', 'memory_support', 'wandering_risk', 
                                               'mobility_needs', 'safety_concern'])
        
        # Priority 1: Multiple urgent risks
        if has_falls_risk and has_memory_support:
            return {
                "icon": "🛡️",
                "text": "Fall risk plus memory support needs—safety is the priority.",
                "status": "urgent"
            }
        
        # Priority 2: Single urgent risk - Falls
        if has_falls_risk:
            return {
                "icon": "🛡️",
                "text": "Given the fall risk, finding the right support level is critical.",
                "status": "urgent"
            }
        
        # Priority 3: Single urgent risk - Memory
        if has_memory_support:
            return {
                "icon": "🧠",
                "text": "Memory support options will give you peace of mind and safety.",
                "status": "important"
            }
        
        # Priority 4: Financial urgency (low runway from MCIP)
        if runway_months and runway_months < 12:
            return {
                "icon": "⏰",
                "text": f"Only {runway_months} months of funding—immediate planning is critical.",
                "status": "urgent"
            }
        elif runway_months and runway_months < 24:
            return {
                "icon": "💡",
                "text": f"You have {runway_months} months of runway. Let's create a funding strategy.",
                "status": "planning"
            }
        
        # Priority 5: Veteran benefits opportunity
        if has_veteran_flag:
            return {
                "icon": "🎖️",
                "text": "As a veteran, you may qualify for Aid & Attendance benefits—up to $2,431/month.",
                "status": "important"
            }
        
        # Priority 6: High confidence + low risk (positive reinforcement)
        if confidence and confidence > 0.9 and active_risk_count == 0:
            return {
                "icon": "✅",
                "text": "Your plan is crystal clear—let's move forward with confidence.",
                "status": "confident"
            }
        
        # Priority 7: Multiple risk flags (general)
        if active_risk_count >= 3:
            return {
                "icon": "🎯",
                "text": f"We've identified {active_risk_count} important needs. Let's find the right support.",
                "status": "important"
            }
        
        # Default: Generic progress encouragement
        completed_count = ctx.progress.get("completed_count", 0)
        if completed_count == 0:
            return {
                "icon": "🚀",
                "text": "Let's find the care option that fits best.",
                "status": "in_progress"
            }
        elif completed_count == 1:
            return {
                "icon": "💪",
                "text": "Great start! One step done, let's keep the momentum going.",
                "status": "in_progress"
            }
        elif completed_count == 2:
            return {
                "icon": "🎯",
                "text": "Almost there! Just one more step to complete your plan.",
                "status": "in_progress"
            }
        else:
            return {
                "icon": "💪",
                "text": "You're making great progress!",
                "status": "in_progress"
            }
    
    @staticmethod
    def get_dynamic_reason_text(ctx: NaviContext) -> str:
        """Generate personalized reason text based on MCIP outcomes.
        
        Reads from:
        - ctx.care_recommendation.tier (MCIP's published tier)
        - ctx.care_recommendation.flags (MCIP's published flags)
        - ctx.financial_profile.gap_amount (MCIP's calculation)
        - ctx.progress.completed_count (MCIP's journey tracking)
        
        Returns: Personalized reason text for next action
        """
        tier = ctx.care_recommendation.tier if ctx.care_recommendation else None
        flags = ctx.care_recommendation.flags if ctx.care_recommendation else []
        completed_count = ctx.progress.get("completed_count", 0)
        
        # After GCP, before Cost Planner
        if completed_count == 1 and tier:
            has_falls_risk = any(f.get('type') == 'falls_risk' and f.get('active') for f in flags)
            
            if tier == "memory_care" or tier == "memory_care_high_acuity":
                return "Memory Care costs more but provides specialized support. Let's explore your options and funding strategies."
            elif tier == "assisted_living":
                if has_falls_risk:
                    return "Now let's see what fall prevention services cost and how to fund them."
                else:
                    return "Assisted Living balances independence with support. Let's calculate costs and plan funding."
            elif tier == "in_home" or tier == "in_home_care":
                return "In-home care gives you flexibility. Let's calculate hourly costs and create a sustainable plan."
            else:
                return "Now let's calculate costs for your recommended care level."
        
        # After Cost Planner, before PFMA
        elif completed_count == 2:
            gap_amount = None
            if ctx.financial_profile:
                gap_amount = getattr(ctx.financial_profile, 'gap_amount', None)
            
            if gap_amount and gap_amount > 1000:
                return f"Your advisor will help you close the ${gap_amount:,.0f}/month gap through VA benefits, insurance, and asset strategies."
            else:
                return "Your advisor will refine your plan and connect you with quality care providers."
        
        # After all complete
        elif completed_count >= 3:
            return "You've built a complete plan. Your advisor will help you take the next steps."
        
        # Default
        return "This will help us find the right support for your situation."
    
    @staticmethod
    def get_gcp_step_coaching(step_id: str, ctx: NaviContext) -> dict:
        """Generate step-aware coaching by reading GCP progress from MCIP.
        
        Args:
            step_id: Current GCP step identifier
            ctx: NaviContext with MCIP data
        
        Reads from:
        - MCIP's published partial assessment state (future)
        - Cumulative score patterns (future - if MCIP exposes them)
        
        Returns: Step-specific coaching message dict with:
            - title: str (coaching headline)
            - body: str (coaching message)
            - tip: Optional[str] (additional guidance)
        
        Note: Phase 1 implementation - will be enhanced in Phase 3
        """
        # Phase 1: Return generic coaching
        # Phase 3 will add cumulative score analysis from MCIP
        
        return {
            "title": "Let's work through this together",
            "body": "Answer these questions to help us understand the care needs.",
            "tip": None
        }
    
    @staticmethod
    def get_cost_planner_intro(ctx: NaviContext) -> dict:
        """Generate tier-specific intro by reading MCIP's care recommendation.
        
        Reads from:
        - ctx.care_recommendation.tier (MCIP's published tier)
        - ctx.care_recommendation.flags (MCIP's published flags)
        
        Returns: Tier-specific financial context message dict with:
            - title: str (cost range headline)
            - body: str (explanation)
            - tip: Optional[str] (helpful tip)
        """
        tier = ctx.care_recommendation.tier if ctx.care_recommendation else None
        flags = ctx.care_recommendation.flags if ctx.care_recommendation else []
        
        # Check for veteran flag
        has_veteran_flag = any(f.get('type') == 'veteran_aanda_risk' and f.get('active') for f in flags)
        
        # Map MCIP's tier to user-facing cost expectations
        if tier == "memory_care" or tier == "memory_care_high_acuity":
            return {
                "title": "Memory Care typically costs $6,000-9,000/month",
                "body": "I've pre-selected Memory Care from your Guided Care Plan. Specialized staffing and secured environments cost more, but financial planning can help.",
                "tip": "Veterans may qualify for up to $2,431/month in Aid & Attendance benefits to offset costs." if has_veteran_flag else "Some facilities offer shared rooms at lower rates while maintaining quality memory care."
            }
        
        elif tier == "assisted_living":
            return {
                "title": "Assisted Living typically costs $4,500-6,500/month",
                "body": "I've pre-selected Assisted Living from your Guided Care Plan. We'll calculate your specific costs based on location, room type, and care level.",
                "tip": "Memory support or medication management can add $500-1,000/month."
            }
        
        elif tier == "in_home" or tier == "in_home_care":
            return {
                "title": "In-Home Care costs vary widely by hours needed",
                "body": "From your Guided Care Plan, you need daily support. We'll calculate costs based on hours per day and regional rates.",
                "tip": "Veterans may qualify for Aid & Attendance benefits covering up to $2,431/month." if has_veteran_flag else "Family members can sometimes provide some hours to reduce costs."
            }
        
        elif tier == "independent":
            return {
                "title": "Independent Living typically costs $2,500-4,000/month",
                "body": "Much more affordable than assisted care. You're paying for community, meals, and activities—not daily care assistance.",
                "tip": "Focus on location and amenities since care needs are minimal."
            }
        
        else:
            # No tier from GCP (user skipped or incomplete)
            return {
                "title": "Let's explore care costs",
                "body": "We'll look at costs for different care levels since you haven't completed the Guided Care Plan yet.",
                "tip": "Completing the Guided Care Plan first gives you personalized estimates."
            }
    
    @staticmethod
    def get_financial_strategy_advice(ctx: NaviContext) -> dict:
        """Generate funding strategy by reading MCIP's financial profile.
        
        Reads from:
        - ctx.financial_profile.runway_months (MCIP's calculation)
        - ctx.financial_profile.gap_amount (MCIP's calculation)
        - ctx.care_recommendation.flags (veteran status, etc.)
        
        Returns: Funding strategy coaching message dict with:
            - title: str (strategy headline)
            - body: str (situation summary)
            - strategies: list[str] (actionable strategies)
            - urgency: str (critical|high|moderate|low)
            - next_step: str (advisor guidance)
        
        Urgency mapping:
        - Critical: runway < 12 months
        - Urgent: runway 12-24 months
        - Moderate: runway 24-48 months
        - Comfortable: runway 48+ months
        """
        if not ctx.financial_profile:
            # No financial data yet
            return {
                "title": "Complete Cost Planner for funding strategies",
                "body": "We'll analyze your financial situation and create a detailed funding plan.",
                "strategies": [],
                "urgency": "low",
                "next_step": "Complete the Cost Planner to get personalized strategies."
            }
        
        runway_months = getattr(ctx.financial_profile, 'runway_months', None)
        gap_amount = getattr(ctx.financial_profile, 'gap_amount', None)
        monthly_cost = getattr(ctx.financial_profile, 'estimated_monthly_cost', None)
        coverage_pct = getattr(ctx.financial_profile, 'coverage_percentage', None)
        
        # Check for veteran flag from care recommendation
        flags = ctx.care_recommendation.flags if ctx.care_recommendation else []
        has_veteran_flag = any(f.get('type') == 'veteran_aanda_risk' and f.get('active') for f in flags)
        
        # Determine urgency and strategies based on runway
        if runway_months and runway_months < 12:
            # Critical: Less than 1 year
            strategies = [
                "Emergency Medicaid application (if qualified)",
                "Immediate asset liquidation planning",
                "Family emergency care fund discussion",
                "Lower-cost care options (shared rooms, hybrid in-home)"
            ]
            if has_veteran_flag:
                strategies.insert(0, "URGENT: Apply for VA Aid & Attendance immediately ($2,431/mo)")
            
            return {
                "title": f"⚠️ Only {runway_months} months of funding available",
                "body": "Current assets will only cover less than a year of care. Immediate financial planning is critical.",
                "strategies": strategies,
                "urgency": "critical",
                "next_step": "Schedule your advisor call ASAP to create an emergency funding plan."
            }
        
        elif runway_months and runway_months < 24:
            # Urgent: 1-2 years
            strategies = [
                "Medicaid planning: Start spend-down strategy now",
                "Long-term care insurance: Review policy benefits",
                "Asset liquidation timeline planning",
                "Family contribution discussions"
            ]
            if has_veteran_flag:
                strategies.insert(0, "Apply for VA Aid & Attendance immediately ($2,431/mo)")
            
            return {
                "title": f"⚠️ {runway_months} months of funding - Urgent planning needed",
                "body": f"Current assets will cover {runway_months} months. We need to act now to extend your runway.",
                "strategies": strategies,
                "urgency": "high",
                "next_step": "Schedule your advisor call soon to implement funding strategy."
            }
        
        elif runway_months and runway_months < 48:
            # Moderate: 2-4 years
            gap_text = f"${gap_amount:,.0f}/month gap" if gap_amount else "funding shortfall"
            coverage_text = f"{int(coverage_pct * 100)}% of costs" if coverage_pct else "some costs"
            
            strategies = [
                "Medicaid planning: Start spend-down strategy before assets deplete",
                "Long-term care insurance: Review and maximize policy benefits",
                "Asset preservation strategies to extend runway",
                "Family contributions: Shared care costs discussion"
            ]
            if has_veteran_flag:
                strategies.insert(0, f"VA Aid & Attendance: Could cover up to $2,431/month (check eligibility)")
            
            return {
                "title": f"You have {runway_months} months of funding, with a {gap_text}",
                "body": f"Your income covers {coverage_text}. Strategic planning now prevents crisis later.",
                "strategies": strategies,
                "urgency": "moderate",
                "next_step": "Your advisor will create a detailed funding strategy and connect you with resources."
            }
        
        elif runway_months and runway_months >= 48:
            # Comfortable: 4+ years
            strategies = [
                "Quality-focused facility selection (you can afford premium options)",
                "Asset preservation strategies to extend runway further",
                "Estate planning considerations",
                "Tax-advantaged strategies for care funding"
            ]
            if has_veteran_flag:
                strategies.insert(0, "Check VA Aid & Attendance eligibility to increase runway even more")
            
            years = runway_months // 12
            return {
                "title": f"✅ Excellent financial position - {years}+ years fully funded",
                "body": "Your income and assets comfortably cover all projected costs with room to spare.",
                "strategies": strategies,
                "urgency": "low",
                "next_step": "Your advisor will help you choose high-quality care options within your comfortable budget."
            }
        
        else:
            # No runway data - fully covered or incomplete data
            return {
                "title": "Let's review your financial options",
                "body": "We'll work with you to create a sustainable funding strategy.",
                "strategies": [],
                "urgency": "low",
                "next_step": "Your advisor will analyze your situation and recommend strategies."
            }
    
    @staticmethod
    def get_next_product_preview(ctx: NaviContext) -> dict:
        """Generate next product preview by reading MCIP's journey state.
        
        Reads from:
        - ctx.progress (MCIP's journey coordination)
        - ctx.next_action (MCIP's recommendation)
        - ctx.care_recommendation (for context)
        
        Returns: Preview message with personalized context dict with:
            - icon: str (emoji)
            - title: str (preview headline)
            - body: str (preview text)
            - preview: str (what to expect)
            - cta: str (call-to-action button text)
        """
        completed_count = ctx.progress.get("completed_count", 0)
        tier = ctx.care_recommendation.tier if ctx.care_recommendation else None
        flags = ctx.care_recommendation.flags if ctx.care_recommendation else []
        
        # Check for specific flags
        has_veteran_flag = any(f.get('type') == 'veteran_aanda_risk' and f.get('active') for f in flags)
        has_falls_risk = any(f.get('type') == 'falls_risk' and f.get('active') for f in flags)
        
        # After GCP, preview Cost Planner
        if completed_count == 1 and tier:
            if tier == "memory_care" or tier == "memory_care_high_acuity":
                body_text = "Memory Care typically costs $6,000-9,000/month"
                if has_veteran_flag:
                    body_text += ", but as a veteran you may qualify for up to $2,431/month in benefits."
                else:
                    body_text += ", but financial planning can help make it affordable."
                
                return {
                    "icon": "📊",
                    "title": "Next: Calculate Memory Care Costs",
                    "body": body_text,
                    "preview": "We'll check eligibility for benefits, review your assets, and create a funding strategy.",
                    "cta": "Start Cost Planning"
                }
            
            elif tier == "assisted_living":
                body_text = "Assisted Living averages $4,500-6,500/month in your area."
                if has_falls_risk:
                    body_text += " Fall prevention support is included in this level."
                
                return {
                    "icon": "📊",
                    "title": "Next: Explore Assisted Living Costs",
                    "body": body_text,
                    "preview": "We'll identify funding sources and show you what's affordable.",
                    "cta": "Start Cost Planning"
                }
            
            else:
                return {
                    "icon": "📊",
                    "title": "Next: Calculate Care Costs",
                    "body": f"Let's see what {tier.replace('_', ' ').title()} costs and how to fund it.",
                    "preview": "We'll review your finances and create a funding strategy.",
                    "cta": "Start Cost Planning"
                }
        
        # After Cost Planner, preview PFMA
        elif completed_count == 2:
            gap_amount = None
            if ctx.financial_profile:
                gap_amount = getattr(ctx.financial_profile, 'gap_amount', None)
            
            if gap_amount and gap_amount > 1000:
                return {
                    "icon": "🤝",
                    "title": "Next: Schedule Your Advisor Call",
                    "body": f"Your advisor will create a plan to close the ${gap_amount:,.0f}/month gap through benefits, insurance, and strategies.",
                    "preview": "Come prepared with questions about Medicaid planning, insurance claims, and facility selection.",
                    "cta": "Book Appointment"
                }
            else:
                return {
                    "icon": "🤝",
                    "title": "Next: Schedule Your Advisor Call",
                    "body": "You're in good financial shape. Your advisor will help you choose quality facilities and optimize your plan.",
                    "preview": "Focus on quality, amenities, and location—you have options.",
                    "cta": "Book Appointment"
                }
        
        # Default
        return {
            "icon": "➡️",
            "title": "Next Step",
            "body": ctx.next_action.get("reason", "Continue your care planning journey."),
            "preview": "",
            "cta": ctx.next_action.get("action", "Continue")
        }


# Export
__all__ = ["NaviCommunicator"]
