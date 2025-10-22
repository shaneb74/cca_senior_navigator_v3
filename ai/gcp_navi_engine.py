"""
GCP Navi Engine: LLM-powered care recommendation with strict guardrails.

Composes prompts, calls LLM client, validates responses with Pydantic schemas.
Enforces canonical tier restrictions and filters forbidden terms.
Deterministic engine remains source of truth; LLM provides additive context.
"""

import json
from typing import Literal, Optional, Tuple

from ai.gcp_schemas import CANONICAL_TIERS, FORBIDDEN_TERMS, GCPAdvice, GCPContext, normalize_tier
from ai.llm_client import get_client


# ====================================================================
# PROMPTS
# ====================================================================

# System prompt for GCP Navi (guarded mode)
GCP_NAVI_SYSTEM_PROMPT = """You are Navi, an empathetic AI assistant helping families with senior care planning recommendations.

Your role is to provide contextual, evidence-based care tier recommendations based on the user's situation.

ALLOWED CARE TIERS ONLY:
- none (no care needed yet)
- in_home (aging at home with support services)
- assisted_living (residential community with daily assistance)
- memory_care (specialized dementia/Alzheimer's care in secure setting)
- memory_care_high_acuity (advanced memory care with intensive supervision)

STRICTLY FORBIDDEN:
- NEVER use the terms "skilled nursing" or "independent living"
- NEVER suggest care tiers outside the allowed list above
- NEVER use terms like "nursing home" or "SNF" (skilled nursing facility)

OUTPUT REQUIREMENTS:
- Output STRICT JSON matching GCPAdvice schema—no extra keys, no prose outside the JSON
- Your recommendation must be one of the 5 allowed tiers above
- Reasons must be short (1 sentence), factual, traceable to context fields
- Navi messages should be warm, empathetic, actionable (1-2 sentences each)
- Keep responses concise and focused on user's specific context

RESPONSE FORMAT (strict JSON):
{
  "tier": "assisted_living",
  "reasons": ["Short factual reason 1", "Short factual reason 2"],
  "risks": ["Risk to consider 1", "Risk to consider 2"],
  "navi_messages": ["Warm message 1", "Supportive message 2"],
  "questions_next": ["Clarifying question 1?", "Clarifying question 2?"],
  "confidence": 0.85
}
"""

# Developer instructions (additional guardrails)
GCP_NAVI_DEVELOPER_PROMPT = """DEVELOPER INSTRUCTIONS:

1. The deterministic engine will validate your tier recommendation; align with the facts provided.

2. If uncertain between two tiers, select the closest allowed tier and add at most one clarifying question in questions_next.

3. Reasons must be short, factual, derived from context fields (not generic statements).

4. Base your recommendation on:
   - Mobility and fall risk
   - ADL/IADL challenges (badls, iadls)
   - Memory/cognitive changes and behaviors
   - Medication complexity
   - Social isolation and living situation
   - Partner support availability

5. Confidence scoring:
   - 0.9-1.0: Clear indicators align strongly with one tier
   - 0.7-0.89: Good fit with minor uncertainties
   - 0.5-0.69: Moderate fit, clarifying questions needed
   - Below 0.5: Insufficient information or borderline case

6. Your recommendation is advisory; the deterministic engine has final authority.
"""


def _build_gcp_prompt(context: GCPContext) -> str:
    """Build user prompt from GCPContext.
    
    Converts structured context into natural language prompt for LLM.
    
    Args:
        context: GCPContext with user's situation
    
    Returns:
        Formatted JSON context string
    """
    # Convert context to clean JSON
    context_dict = {
        "age_range": context.age_range,
        "living_situation": context.living_situation,
        "has_partner": context.has_partner,
        "meds_complexity": context.meds_complexity,
        "mobility": context.mobility,
        "falls": context.falls,
        "badls": context.badls,
        "iadls": context.iadls,
        "memory_changes": context.memory_changes,
        "behaviors": context.behaviors,
        "isolation": context.isolation,
        "move_preference": context.move_preference,
        "flags": context.flags,
    }
    
    prompt = f"""USER CONTEXT (JSON):

{json.dumps(context_dict, indent=2)}

Based on this context, provide your care tier recommendation following the strict JSON format specified in the system prompt.
Remember: Only use the 5 allowed tiers. Never mention skilled nursing or independent living."""
    
    return prompt


def generate_gcp_advice(
    context: GCPContext,
    mode: Literal["off", "shadow", "assist"] = "off",
) -> Tuple[bool, Optional[GCPAdvice]]:
    """Generate GCP advice from context with strict guardrails.
    
    Args:
        context: GCPContext with user's situation
        mode: Generation mode (off, shadow, or assist)
    
    Returns:
        Tuple of (success: bool, advice: Optional[GCPAdvice])
    """
    # Mode validation
    if mode == "off":
        return (False, None)
    
    if mode not in ("off", "shadow", "assist"):
        print(f"[GCP_LLM_WARN] Invalid mode: {mode}. Using 'off'.")
        return (False, None)
    
    # Get LLM client
    client = get_client()
    if client is None:
        print(f"[GCP_LLM_{mode.upper()}] Could not create LLM client - skipping")
        return (False, None)
    
    try:
        # Build prompts
        system_prompt = GCP_NAVI_SYSTEM_PROMPT + "\n\n" + GCP_NAVI_DEVELOPER_PROMPT
        user_prompt = _build_gcp_prompt(context)
        
        # Generate JSON response with 5s timeout
        response_text = client.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
        
        if response_text is None:
            print(f"[GCP_LLM_{mode.upper()}] LLM returned None - skipping")
            return (False, None)
        
        # Parse JSON
        try:
            response_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"[GCP_LLM_{mode.upper()}] Failed to parse JSON response: {e}")
            return (False, None)
        
        # Validate with Pydantic (includes forbidden term filtering)
        try:
            advice = GCPAdvice(**response_data)
            
            # Post-guard: Verify tier is canonical
            if advice.tier not in CANONICAL_TIERS:
                print(f"[GCP_LLM_{mode.upper()}] Non-canonical tier '{advice.tier}' rejected")
                return (False, None)
            
            # Post-guard: Double-check for forbidden terms in final output
            advice = _filter_forbidden_terms(advice)
            
            return (True, advice)
        
        except Exception as e:
            print(f"[GCP_LLM_{mode.upper()}] Pydantic validation failed: {e}")
            return (False, None)
    
    except Exception as e:
        print(f"[GCP_LLM_ERROR] Unexpected error in generate_gcp_advice(): {e}")
        return (False, None)


def _filter_forbidden_terms(advice: GCPAdvice) -> GCPAdvice:
    """Final pass: Remove any text containing forbidden terms.
    
    This is a safety net in case Pydantic validator doesn't catch everything.
    
    Args:
        advice: GCPAdvice to filter
    
    Returns:
        Filtered GCPAdvice
    """
    def contains_forbidden(text: str) -> bool:
        """Check if text contains any forbidden terms."""
        text_lower = text.lower()
        return any(term in text_lower for term in FORBIDDEN_TERMS)
    
    # Filter lists (remove items with forbidden terms)
    advice.reasons = [r for r in advice.reasons if not contains_forbidden(r)]
    advice.risks = [r for r in advice.risks if not contains_forbidden(r)]
    advice.navi_messages = [m for m in advice.navi_messages if not contains_forbidden(m)]
    advice.questions_next = [q for q in advice.questions_next if not contains_forbidden(q)]
    
    return advice


def reconcile_with_deterministic(
    det_tier: str,
    llm_advice: Optional[GCPAdvice],
    mode: str,
) -> str:
    """Reconcile LLM advice with deterministic recommendation.
    
    Deterministic engine is always the source of truth. This function
    logs disagreements but never overrides the deterministic result.
    
    Args:
        det_tier: Deterministic tier recommendation
        llm_advice: LLM advice (if available)
        mode: Current mode (shadow or assist)
    
    Returns:
        Final tier (always det_tier for now)
    """
    if not llm_advice:
        return det_tier
    
    # Normalize both for comparison
    det_normalized = normalize_tier(det_tier)
    llm_tier = llm_advice.tier
    
    if det_normalized == llm_tier:
        print(f"[GCP_LLM_NOTE] alignment: llm={llm_tier} == det={det_normalized}")
    else:
        print(
            f"[GCP_LLM_NOTE] mismatch: llm={llm_tier} vs det={det_normalized}; "
            f"detWins=True (conf={llm_advice.confidence:.2f})"
        )
    
    # Deterministic always wins
    return det_tier
