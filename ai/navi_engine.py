"""
Navi Engine: LLM-powered advice generation for Cost Planner.

Composes prompts, calls LLM client, validates responses with Pydantic schemas.
Enforces strict JSON validation and timeout handling for shadow mode safety.
"""

import json
from typing import Literal, Optional

from ai.llm_client import get_client
from ai.schemas import CPAdvice, CPContext


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
            return advice
        except Exception as e:
            print(f"[LLM_WARN] Pydantic validation failed: {e}")
            return None
    
    except Exception as e:
        # Catch-all for unexpected errors
        print(f"[LLM_ERROR] Unexpected error in generate(): {e}")
        return None


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
