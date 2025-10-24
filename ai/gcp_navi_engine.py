"""
GCP Navi Engine: LLM-powered care recommendation with strict guardrails.

Composes prompts, calls LLM client, validates responses with Pydantic schemas.
Enforces canonical tier restrictions and filters forbidden terms.
Deterministic engine remains source of truth; LLM provides additive context.
"""

import json
from typing import Literal

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
    allowed_tiers: list[str] | None = None,
) -> tuple[bool, GCPAdvice | None]:
    """Generate GCP advice from context with strict guardrails.
    
    Args:
        context: GCPContext with user's situation
        mode: Generation mode (off, shadow, or assist)
        allowed_tiers: Optional list of allowed tier values (cognitive gate enforcement)
    
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
        # Build prompts (inject allowed_tiers if provided)
        system_prompt = GCP_NAVI_SYSTEM_PROMPT + "\n\n" + GCP_NAVI_DEVELOPER_PROMPT

        # Add allowed tiers constraint if provided
        if allowed_tiers:
            allowed_list = ", ".join(sorted(allowed_tiers))
            tier_constraint = f"\n\nIMPORTANT: Due to cognitive assessment results, you must choose ONE tier from this restricted list ONLY: {allowed_list}"
            system_prompt += tier_constraint

        user_prompt = _build_gcp_prompt(context)

        # Generate JSON response (uses client's configured timeout, currently 10s)
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

            # Post-guard: Verify tier is allowed (cognitive gate enforcement)
            if allowed_tiers and advice.tier not in allowed_tiers:
                print(f"[GCP_LLM_SKIP] tier '{advice.tier}' not in allowed_tiers {sorted(allowed_tiers)}")
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
    llm_advice: GCPAdvice | None,
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
        # Check what the actual chosen tier was from adjudication
        final_tier = None
        adjudication = {}
        try:
            import streamlit as st
            final_tier = st.session_state.get("gcp.final_tier")
            adjudication = st.session_state.get("gcp.adjudication_decision", {})
        except Exception:
            # Streamlit not available or session state not accessible
            pass

        source = adjudication.get("source", "unknown")
        reason = adjudication.get("adjudication_reason", "unknown")

        print(
            f"[GCP_LLM_NOTE] mismatch: llm={llm_tier} vs det={det_normalized}; "
            f"chosen={final_tier or det_normalized} source={source} reason={reason} (conf={llm_advice.confidence:.2f})"
        )

        # Log disagreement for training (no PHI)
        try:
            import json
            import time

            from products.gcp_v4.modules.care_recommendation.logic import (
                cognition_band,
                cognitive_gate_behaviors_only,
                support_band,
            )
            from tools.log_disagreement import append_case

            # Hardened context serialization helper
            def _jsonify_ctx(ctx):
                try:
                    if hasattr(ctx, "model_dump"):
                        return ctx.model_dump()
                    return json.loads(json.dumps(ctx, default=str))
                except Exception as e:
                    return {"_note": "context_unserializable", "type": str(type(ctx)), "err": str(e)}

            # Extract context (gcp_context should be available from calling scope)
            # If not available, we'll skip logging rather than fail
            import streamlit as st

            # Get GCP context from session state (stored during generation)
            gcp_ctx = st.session_state.get("_gcp_context_for_logging")
            if gcp_ctx:
                answers = gcp_ctx.get("answers", {})
                flags = gcp_ctx.get("flags", [])
                allowed = gcp_ctx.get("allowed_tiers", [])

                # Compute bands for context
                cog_band = cognition_band(answers, flags)
                sup_band = support_band(answers, flags)
                risky = cognitive_gate_behaviors_only(answers, flags)

                row = {
                    "gcp_context": _jsonify_ctx(gcp_ctx),
                    "allowed_tiers": sorted(list(allowed)) if allowed else [],
                    "det_tier": det_normalized,
                    "llm_tier": getattr(llm_advice, "narrowed_band", None) or getattr(llm_advice, "band", None) or getattr(llm_advice, "tier", None),
                    "llm_conf": getattr(llm_advice, "confidence", None),
                    "reasons": getattr(llm_advice, "reasons", []),
                    "bands": {"cog": cog_band, "sup": sup_band},
                    "has_risky_behaviors": risky,
                    "ts": int(time.time())
                }

                case_id = append_case(row)
                print(f"[GCP_LOG] disagreement captured id={case_id}")
        except Exception as e:
            # Silent failure - logging must not disrupt operation
            print(f"[GCP_LOG_WARN] Could not log disagreement: {e}")

    # Deterministic always wins
    return det_tier


def generate_section_advice(
    context: GCPContext,
    section: str,
    mode: Literal["off", "shadow", "assist"] = "off",
    allowed_tiers: list[str] | None = None,
) -> tuple[bool, GCPAdvice | None]:
    """Generate contextual Navi advice after a GCP section completes.
    
    This function provides incremental feedback as the user progresses through
    the assessment, computing a running tier estimate based on answers so far.
    
    Args:
        context: GCPContext with answers completed so far (may be partial)
        section: Section name (about_you, health_safety, daily_living, etc.)
        mode: Generation mode (off, shadow, or assist)
        allowed_tiers: Optional list of allowed tier values (cognitive gate enforcement)
    
    Returns:
        Tuple of (success: bool, advice: Optional[GCPAdvice])
    """
    # Mode validation
    if mode == "off":
        return (False, None)

    if mode not in ("off", "shadow", "assist"):
        print(f"[GCP_LLM_SECTION] Invalid mode: {mode}. Using 'off'.")
        return (False, None)

    # Get LLM client
    client = get_client()
    if client is None:
        print(f"[GCP_LLM_SECTION] Could not create LLM client - skipping section={section}")
        return (False, None)

    try:
        # Build section-specific prompt (inject allowed_tiers if provided)
        system_prompt = _build_section_system_prompt(section)

        # Add allowed tiers constraint if provided
        if allowed_tiers:
            allowed_list = ", ".join(sorted(allowed_tiers))
            tier_constraint = f"\n\nIMPORTANT: Due to cognitive assessment results, you must choose ONE tier from this restricted list ONLY: {allowed_list}"
            system_prompt += tier_constraint

        user_prompt = _build_section_user_prompt(context, section)

        # Generate JSON response (uses client's configured timeout, currently 10s)
        response_text = client.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        if response_text is None:
            print(f"[GCP_LLM_SECTION] LLM returned None - section={section}")
            return (False, None)

        # Parse JSON
        try:
            response_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"[GCP_LLM_SECTION] Failed to parse JSON - section={section}: {e}")
            return (False, None)

        # Validate with Pydantic
        try:
            advice = GCPAdvice(**response_data)

            # Post-guard: Verify tier is canonical
            if advice.tier not in CANONICAL_TIERS:
                print(f"[GCP_LLM_SECTION] Non-canonical tier '{advice.tier}' rejected - section={section}")
                return (False, None)

            # Post-guard: Verify tier is allowed (cognitive gate enforcement)
            if allowed_tiers and advice.tier not in allowed_tiers:
                print(f"[GCP_LLM_SKIP] section={section} tier '{advice.tier}' not in allowed_tiers {sorted(allowed_tiers)}")
                return (False, None)

            # Post-guard: Filter forbidden terms
            advice = _filter_forbidden_terms(advice)

            # Log section completion
            print(
                f"[GCP_LLM_SECTION] section={section} tier={advice.tier} "
                f"conf={advice.confidence:.2f} msgs={len(advice.navi_messages)} "
                f"reasons={len(advice.reasons)}"
            )

            return (True, advice)

        except Exception as e:
            print(f"[GCP_LLM_SECTION] Pydantic validation failed - section={section}: {e}")
            return (False, None)

    except Exception as e:
        print(f"[GCP_LLM_SECTION] Unexpected error - section={section}: {e}")
        return (False, None)


def _build_section_system_prompt(section: str) -> str:
    """Build section-specific system prompt.
    
    Tailors the base system prompt to focus on the specific section context.
    
    Args:
        section: Section name
    
    Returns:
        System prompt string
    """
    base_prompt = GCP_NAVI_SYSTEM_PROMPT

    section_context = {
        "about_you": "Focus on demographic factors, living situation, and partner support. This is early in the assessment.",
        "health_safety": "Focus on medication complexity, mobility, fall risk, and safety concerns. Consider these health indicators carefully.",
        "daily_living": "Focus on ADL/IADL challenges, which are strong indicators of care needs. This is a critical section.",
        "cognition_behavior": "Focus on memory changes and behaviors, which may indicate need for specialized memory care.",
        "move_preferences": "Focus on user's timeline and readiness to move, which affects care planning urgency.",
    }

    context_note = section_context.get(section, "Provide contextual feedback based on information gathered so far.")

    return f"""{base_prompt}

SECTION CONTEXT:
You are providing feedback after the "{section}" section.
{context_note}

Remember: This is a running assessment. The user hasn't completed all sections yet, so your tier estimate is preliminary based on available information."""


def _build_section_user_prompt(context: GCPContext, section: str) -> str:
    """Build section-specific user prompt.
    
    Only includes fields that have been answered so far (non-default values).
    
    Args:
        context: GCPContext (may be partial)
        section: Section name
    
    Returns:
        User prompt string
    """
    # Build minimal context dict with only answered fields
    context_dict = {}

    # Always include these if available
    if context.age_range and context.age_range != "unknown":
        context_dict["age_range"] = context.age_range
    if context.living_situation and context.living_situation != "unknown":
        context_dict["living_situation"] = context.living_situation

    context_dict["has_partner"] = context.has_partner

    # Add fields based on section progress
    if context.meds_complexity and context.meds_complexity != "simple":
        context_dict["meds_complexity"] = context.meds_complexity
    if context.mobility and context.mobility != "independent":
        context_dict["mobility"] = context.mobility
    if context.falls and context.falls != "no_falls":
        context_dict["falls"] = context.falls

    if context.badls:
        context_dict["badls"] = context.badls
    if context.iadls:
        context_dict["iadls"] = context.iadls

    if context.memory_changes and context.memory_changes != "no_changes":
        context_dict["memory_changes"] = context.memory_changes
    if context.behaviors:
        context_dict["behaviors"] = context.behaviors

    if context.isolation and context.isolation != "minimal":
        context_dict["isolation"] = context.isolation

    if context.move_preference is not None:
        context_dict["move_preference"] = context.move_preference

    if context.flags:
        context_dict["flags"] = context.flags

    prompt = f"""SECTION: {section}

CONTEXT SO FAR (partial assessment):
{json.dumps(context_dict, indent=2)}

Based on the information gathered in this section and prior sections, provide your preliminary care tier estimate and contextual feedback.

Remember:
1. This is a running assessment - more sections may follow
2. Provide a preliminary tier based on available information
3. Include 1-2 supportive Navi messages appropriate to this stage
4. Suggest 1-2 clarifying questions if needed"""

    return prompt

