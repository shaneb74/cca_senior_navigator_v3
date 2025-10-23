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
    # Format flags as readable list
    flags_text = ", ".join(context.flags) if context.flags else "none"
    
    # Format reasons as readable list
    reasons_text = ", ".join(context.top_reasons) if context.top_reasons else "general care needs"
    
    # Build prompt
    prompt = f"""USER CONTEXT:
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
