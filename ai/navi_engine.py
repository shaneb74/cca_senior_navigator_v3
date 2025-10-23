"""
Navi Engine: LLM-powered advice generation for Cost Planner.

Composes prompts, calls LLM client, validates responses with Pydantic schemas.
Enforces strict JSON validation and timeout handling for shadow mode safety.
"""

import json
from typing import Literal, Optional

from ai.llm_client import get_client
from ai.schemas import CPAdvice, CPContext


# ====================================================================
# TIER CANONICALIZATION
# ====================================================================

# Canonical tier values (must match CPContext.tier Literal)
CANONICAL_TIERS = {"none", "in_home", "assisted_living", "memory_care", "memory_care_high_acuity"}

# Aliases for common tier name variations
ALIASES = {
    "in_home_care": "in_home",
    "home_care": "in_home",
    "no_care": "none",
    "no_care_needed": "none",
}

# Forbidden terms that should never appear in tier or advice
FORBIDDEN_TERMS = {"skilled nursing", "independent living"}


def normalize_tier(value: str) -> Optional[str]:
    """Normalize tier value to canonical form.
    
    Handles common aliases and variations, ensuring only canonical
    tier values are used in CPContext and LLM prompts.
    
    Args:
        value: Raw tier string from Cost Planner
    
    Returns:
        Canonical tier value or None if invalid
    """
    if not value:
        return None
    
    v = value.strip().lower()
    v = ALIASES.get(v, v)
    
    # Check against canonical tiers
    if v in CANONICAL_TIERS:
        return v
    
    # Check for forbidden terms
    for forbidden in FORBIDDEN_TERMS:
        if forbidden in v:
            return None
    
    return None


def detect_dual_mode_from_careplans(careplans: list) -> bool:
    """Detect if dual mode is needed based on multiple care plans.
    
    Args:
        careplans: List of care plan objects with tier fields
        
    Returns:
        True if dual mode should be enabled (multiple different tiers)
    """
    if len(careplans) < 2:
        return False
    
    # Extract tiers and normalize them
    tiers = set()
    for cp in careplans:
        if hasattr(cp, 'tier') and cp.tier:
            normalized = normalize_tier(cp.tier)
            if normalized:
                tiers.add(normalized)
        elif hasattr(cp, 'final_tier') and cp.final_tier:
            normalized = normalize_tier(cp.final_tier)
            if normalized:
                tiers.add(normalized)
    
    # Dual mode if we have multiple different tiers
    return len(tiers) > 1


def get_primary_tier_from_careplans(careplans: list) -> Optional[str]:
    """Get the primary (most recent) care tier from care plans.
    
    Args:
        careplans: List of care plan objects
        
    Returns:
        Primary tier string (normalized) or None
    """
    if not careplans:
        return None
    
    # Use the most recent care plan (assume they're ordered)
    latest_cp = careplans[-1]
    
    # Try tier first, then final_tier
    tier = getattr(latest_cp, 'tier', None) or getattr(latest_cp, 'final_tier', None)
    if tier:
        return normalize_tier(tier)
    
    return None


def generate_handoff_blurb(
    primary_tier: str, 
    dual_mode: bool = False, 
    flags: list = None,
    partner_tier: str = None,
    threshold_crossed: bool = False,
    care_intensity: str = "medium",
    compare_inhome_suggested: bool = False
) -> str:
    """Generate a 'what to expect' blurb for GCP→Cost Planner handoff using LLM templates.
    
    Args:
        primary_tier: Primary care tier (assisted_living | memory_care | in_home | stay_home)
        dual_mode: Whether dual mode comparison is available
        flags: List of care flags for context
        partner_tier: Optional partner's care tier
        threshold_crossed: Whether cost threshold was crossed
        care_intensity: Care intensity level (low|medium|high)
        compare_inhome_suggested: Whether in-home comparison is suggested
        
    Returns:
        Formatted blurb text for intro display using contextual templates
    """
    flags = flags or []
    
    # Template selection based on context
    templates = _get_handoff_templates(
        primary_tier=primary_tier,
        partner_tier=partner_tier,
        dual_mode=dual_mode,
        threshold_crossed=threshold_crossed,
        care_intensity=care_intensity,
        compare_inhome_suggested=compare_inhome_suggested,
        flags=flags
    )
    
    # For now, select the first matching template
    # In future, this could use LLM to choose the best template
    return templates[0] if templates else _get_fallback_template(primary_tier, dual_mode)


def _get_handoff_templates(
    primary_tier: str,
    partner_tier: str = None,
    dual_mode: bool = False,
    threshold_crossed: bool = False,
    care_intensity: str = "medium",
    compare_inhome_suggested: bool = False,
    flags: list = None
) -> list[str]:
    """Get contextual handoff templates based on structured context.
    
    Returns list of applicable templates in priority order.
    """
    flags = flags or []
    templates = []
    
    # 1. Assisted Living (or Memory Care) Templates
    if primary_tier in ("assisted_living", "memory_care", "memory_care_high_acuity"):
        tier_name = "Assisted Living" if primary_tier == "assisted_living" else "Memory Care"
        
        if dual_mode and partner_tier:
            templates.append(f"We'll compare {tier_name} costs with your partner's care options to find what works best for both of you.")
        elif compare_inhome_suggested or dual_mode:
            templates.append(f"We'll show {tier_name} costs in your area and compare them with staying home with care.")
        elif threshold_crossed:
            templates.append(f"We'll explore {tier_name} options that fit your budget, including financial assistance programs.")
        elif care_intensity == "high":
            templates.append(f"We'll focus on {tier_name} communities with the specialized care level you need.")
        else:
            templates.append(f"We'll help you understand {tier_name} costs and what's included in monthly fees.")
    
    # 2. In-Home Care Templates  
    elif primary_tier == "in_home":
        if dual_mode and partner_tier in ("assisted_living", "memory_care"):
            templates.append("We'll compare in-home care costs with facility options so you can see all your choices.")
        elif care_intensity == "high":
            templates.append("We'll calculate costs for the intensive in-home support you need, including overnight care.")
        elif threshold_crossed:
            templates.append("We'll find in-home care options that work within your budget, including veteran benefits and assistance programs.")
        elif compare_inhome_suggested:
            templates.append("We'll help you customize in-home care hours and services to match your specific needs and budget.")
        else:
            templates.append("We'll break down in-home care costs by hours and services so you can plan what works best.")
    
    # 3. Stay Home / Independent Templates
    elif primary_tier in ("none", "stay_home", "independent"):
        if dual_mode:
            templates.append("We'll explore optional support services and compare costs if care needs change over time.")
        elif threshold_crossed:
            templates.append("We'll focus on affordable support services that help you stay independent longer.")
        else:
            templates.append("We'll look at optional support services and costs that might be helpful as a safety net.")
    
    # Add context-specific enhancements
    context_additions = []
    if "veteran_aanda_risk" in flags:
        context_additions.append("We'll include veteran benefits that can help cover costs.")
    if "limited_support" in flags or "no_support" in flags:
        context_additions.append("We'll highlight options that provide family support and respite.")
    if "fall_risk" in flags or "mobility_issues" in flags:
        context_additions.append("We'll emphasize safety features and emergency response options.")
    
    # Combine templates with context additions
    enhanced_templates = []
    for template in templates:
        if context_additions:
            enhanced_template = f"{template} {context_additions[0]}"  # Add first relevant context
            enhanced_templates.append(enhanced_template)
        enhanced_templates.append(template)  # Also keep original
    
    return enhanced_templates if enhanced_templates else templates


def _get_fallback_template(primary_tier: str, dual_mode: bool) -> str:
    """Fallback template when no specific context matches."""
    if dual_mode:
        return "We'll compare different care options and costs so you can make the best choice for your situation."
    else:
        return "We'll break down the costs and help you understand what's included in your care options."
    
    return v if v in CANONICAL_TIERS else None


# ====================================================================
# PROMPTS
# ====================================================================

# System prompt for Navi shadow mode
NAVI_SYSTEM_PROMPT = """You are Navi, an empathetic AI assistant helping families navigate senior care planning.

Your role is to provide contextual, actionable advice based on the user's care planning situation.

RULES:
1. Be warm, empathetic, and encouraging
2. Acknowledge financial/emotional challenges without being dismissive
3. Provide 1-2 short conversational messages (1-2 sentences each)
4. Offer 1-2 insights about their situation
5. Suggest 2-3 relevant follow-up questions
6. NEVER change cost estimates or care tier - those are deterministic
7. Focus on emotional support, next steps, and clarifying questions

ALLOWED CARE TIERS ONLY:
- none (no care needed yet)
- in_home (aging at home with support)
- assisted_living (residential community with assistance)
- memory_care (specialized dementia/Alzheimer's care)
- memory_care_high_acuity (advanced memory care needs)

STRICTLY FORBIDDEN:
- Do NOT mention or propose "skilled nursing" or "independent living" as care options
- Do NOT suggest care tiers outside the allowed list above
- Never use terms like "nursing home" or "SNF"

RESPONSE FORMAT (strict JSON):
{
  "messages": ["Short message 1", "Short message 2"],
  "insights": ["Insight about their situation"],
  "questions_next": ["Question 1?", "Question 2?"],
  "confidence": 0.8
}

Keep responses concise, actionable, and focused on the user's specific context.
"""


def _build_context_prompt(context: CPContext) -> str:
    """Build user prompt from CPContext.
    
    Converts structured context into natural language prompt for LLM.
    
    Args:
        context: CPContext with user's situation
    
    Returns:
        Formatted prompt string
    """
    # Check for additional inhome context (for in_home tier cost analysis)
    inhome_context = ""
    try:
        import streamlit as st
        inhome_context = st.session_state.get("_llm_inhome_context", "")
    except Exception:
        # Handle case where streamlit is not available
        pass
    
    # Format flags as readable list
    flags_text = ", ".join(context.flags) if context.flags else "none"
    
    # Format reasons as readable list
    reasons_text = ", ".join(context.top_reasons) if context.top_reasons else "general care needs"
    
    # Prepend inhome context if available
    context_prefix = inhome_context if inhome_context else ""
    
    # Build prompt
    prompt = f"""{context_prefix}USER CONTEXT:
- Care Tier: {context.tier.replace('_', ' ').title()}
- Has Partner: {'Yes' if context.has_partner else 'No'}
- Monthly Cost: ${context.monthly_adjusted:,.2f}
- Region: {context.region}
- Move Preference: {context.move_preference or 'not specified'}
- Keep Home: {'Yes' if context.keep_home else 'No'}
- Flags: {flags_text}
- Top Reasons for Care: {reasons_text}

Based on this context, provide empathetic, actionable advice to help them with their care planning journey.
Focus on emotional support, practical next steps, and clarifying questions.

Remember: You CANNOT change the care tier or cost estimates. Those are deterministic.
Your role is to provide context, encouragement, and help them think through their options."""
    
    return prompt


def generate(
    context: CPContext,
    mode: Literal["shadow", "assist", "adjust"] = "shadow",
) -> Optional[CPAdvice]:
    """Generate Navi advice from Cost Planner context.
    
    Args:
        context: CPContext with user's situation
        mode: Generation mode (shadow, assist, or adjust)
    
    Returns:
        CPAdvice with generated content, or None if generation fails
    """
    # Validate mode (only shadow implemented for now)
    if mode not in ("shadow", "assist", "adjust"):
        print(f"[LLM_WARN] Invalid mode: {mode}. Using 'shadow'.")
        mode = "shadow"
    
    # Get LLM client
    client = get_client()
    if client is None:
        print("[LLM_WARN] Could not create LLM client - skipping generation")
        return None
    
    try:
        # Build prompts
        system_prompt = NAVI_SYSTEM_PROMPT
        user_prompt = _build_context_prompt(context)
        
        # Generate JSON response
        response_text = client.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
        
        if response_text is None:
            print("[LLM_WARN] LLM returned None - skipping")
            return None
        
        # Parse JSON
        try:
            response_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"[LLM_WARN] Failed to parse JSON response: {e}")
            return None
        
        # Validate with Pydantic
        try:
            advice = CPAdvice(**response_data)
            
            # Post-filter: Remove any forbidden terms from advice
            advice = _filter_forbidden_terms(advice)
            
            return advice
        except Exception as e:
            print(f"[LLM_WARN] Pydantic validation failed: {e}")
            return None
    
    except Exception as e:
        # Catch-all for unexpected errors
        print(f"[LLM_ERROR] Unexpected error in generate(): {e}")
        return None


def _filter_forbidden_terms(advice: CPAdvice) -> CPAdvice:
    """Remove any messages/insights containing forbidden terms.
    
    Args:
        advice: CPAdvice to filter
    
    Returns:
        Filtered CPAdvice with forbidden terms removed
    """
    def contains_forbidden(text: str) -> bool:
        """Check if text contains any forbidden terms."""
        text_lower = text.lower()
        return any(term in text_lower for term in FORBIDDEN_TERMS)
    
    # Filter messages
    advice.messages = [msg for msg in advice.messages if not contains_forbidden(msg)]
    
    # Filter insights
    advice.insights = [insight for insight in advice.insights if not contains_forbidden(insight)]
    
    # Filter questions
    advice.questions_next = [q for q in advice.questions_next if not contains_forbidden(q)]
    
    return advice


def generate_safe_with_normalization(
    tier: str,
    has_partner: bool,
    move_preference: Optional[str],
    keep_home: bool,
    monthly_adjusted: float,
    region: str,
    flags: list[str],
    top_reasons: list[str],
    mode: Literal["shadow", "assist", "adjust"] = "shadow",
) -> tuple[bool, Optional[CPAdvice]]:
    """Safe wrapper that normalizes tier before creating CPContext.
    
    This function should be used by calling code instead of directly
    constructing CPContext, as it handles tier normalization and
    validation gracefully.
    
    Args:
        tier: Raw tier value (may be alias)
        has_partner: Whether user has a partner/spouse
        move_preference: User's move timeline preference
        keep_home: Whether user wants to keep their home
        monthly_adjusted: Estimated monthly care cost
        region: Geographic region
        flags: List of user flags
        top_reasons: Top reasons for seeking care
        mode: Generation mode (shadow, assist, or adjust)
    
    Returns:
        Tuple of (success: bool, advice: Optional[CPAdvice])
    """
    # Normalize tier
    normalized_tier = normalize_tier(tier)
    
    if normalized_tier is None:
        print(f"[LLM_SHADOW] skip: non-canonical tier '{tier}'")
        return (False, None)
    
    try:
        # Create context with normalized tier
        context = CPContext(
            tier=normalized_tier,
            has_partner=has_partner,
            move_preference=move_preference,
            keep_home=keep_home,
            monthly_adjusted=monthly_adjusted,
            region=region,
            flags=flags,
            top_reasons=top_reasons,
        )
        
        # Generate advice
        return generate_safe(context, mode)
    
    except Exception as e:
        print(f"[LLM_ERROR] Exception in generate_safe_with_normalization(): {e}")
        return (False, None)


def generate_safe(
    context: CPContext,
    mode: Literal["shadow", "assist", "adjust"] = "shadow",
) -> tuple[bool, Optional[CPAdvice]]:
    """Safe wrapper for generate() with explicit success flag.
    
    Returns a tuple of (success, advice) to make error handling explicit
    in calling code.
    
    Args:
        context: CPContext with user's situation
        mode: Generation mode (shadow, assist, or adjust)
    
    Returns:
        Tuple of (success: bool, advice: Optional[CPAdvice])
    """
    try:
        advice = generate(context, mode)
        if advice is None:
            return (False, None)
        return (True, advice)
    except Exception as e:
        print(f"[LLM_ERROR] Exception in generate_safe(): {e}")
        return (False, None)
