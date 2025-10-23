"""LLM-powered summary generation for GCP recommendation page."""

import json
from openai import OpenAI
from .llm_client import get_api_key, get_openai_model
from .summary_schemas import SummaryAdvice


SYSTEM_PROMPT = (
    "You are Navi, a calm, supportive care navigator. "
    "Output ONLY valid JSON matching this schema: "
    '{"headline": "string (1 sentence)", "what_it_means": "string (1-2 sentences)", '
    '"why": ["reason1", "reason2", ...], "next_line": "string (1 sentence)", "confidence": 0.8}. '
    "Do NOT wrap in code fences. Return raw JSON only. "
    "Use plain, concise language. No prices, no guarantees. "
    "For 'headline': 1 concise sentence about the care tier recommendation. "
    "For 'what_it_means': 1-2 sentences explaining what this tier means for daily life. "
    "For 'why': Array of 2-4 brief reasons drawing from ADLs, IADLs, mobility, falls, behaviors, isolation, partner status. "
    "For 'next_line': 1 sentence inviting cost exploration. "
    "For 'confidence': 0.7 to 0.95 based on signal clarity."
)


def _get_flag(name: str, default: str = "off") -> str:
    import os
    try:
        import streamlit as st
        s = getattr(st, "secrets", None)
        if s:
            v = s.get(name)
            if v is not None:
                return str(v).strip().strip('"').lower()
    except Exception:
        pass
    return str(os.getenv(name, default)).strip().strip('"').lower()

DEBUG_LLM = (_get_flag("DEBUG_LLM", "off") == "on")


def generate_summary(
    context: dict,
    deterministic_tier: str,
    hours_suggested: str | None,
    user_hours: str | None,
    mode: str
) -> tuple[bool, SummaryAdvice | None]:
    """Generate conversational summary advice for GCP recommendation.
    
    Args:
        context: Dict with badls, iadls, mobility, falls, behaviors, etc.
        deterministic_tier: Final tier from logic engine
        hours_suggested: Suggested hours/day band
        user_hours: User's selected hours/day band
        mode: Feature flag mode ("shadow" or "assist")
    
    Returns:
        Tuple of (success: bool, advice: SummaryAdvice | None)
    """
    if mode not in ("shadow", "assist"):
        return False, None
    
    key = get_api_key()
    if not key:
        return False, None
    
    client = OpenAI(api_key=key)
    model = get_openai_model()

    # Call instrumentation (always on for diagnostics)
    try:
        print(f"[GCP_SUMMARY_CALL] mode={mode} model={model} keys={list(context.keys())}")
    except Exception:
        pass
    
    # Build payload for LLM
    payload = {
        "tier": deterministic_tier,
        "hours_suggested": hours_suggested,
        "user_hours": user_hours,
        "signals": {
            "badls": context.get("badls", []),
            "iadls": context.get("iadls", []),
            "mobility": context.get("mobility"),
            "falls": context.get("falls"),
            "behaviors": context.get("behaviors", []),
            "meds_complexity": context.get("meds_complexity"),
            "isolation": context.get("isolation"),
            "partner_at_home": context.get("has_partner", False)
        }
    }
    
    try:
        resp = client.chat.completions.create(
            model=model,
            temperature=0.2,
            max_tokens=320,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Context JSON:\n" + json.dumps(payload)}
            ]
        )
        
        text = (resp.choices[0].message.content or "").strip()
        
        # Always log raw response length
        try:
            print(f"[GCP_SUMMARY_RAW] len={len(text)}")
        except Exception:
            pass
        
        # Strip code fences if present
        if text.startswith("```"):
            text = text.strip().strip("`")
            if text.lower().startswith("json"):
                text = text[4:].lstrip()
        
        # Try parsing as JSON
        try:
            adv = SummaryAdvice.model_validate_json(text)
            return True, adv
        except Exception as e1:
            # Fallback: try parsing as dict
            try:
                adv = SummaryAdvice(**json.loads(text))
                return True, adv
            except Exception as e2:
                print(f"[GCP_SUMMARY_PARSE_ERROR] validate_json: {e1}")
                print(f"[GCP_SUMMARY_PARSE_ERROR] json_loads: {e2}")
                print(f"[GCP_SUMMARY_PARSE_ERROR] text_preview: {text[:200]}")
                return False, None
    
    except Exception as e:
        # Propagate a concise failure log but do not raise
        print(f"[GCP_SUMMARY_CALL_ERROR] {e}")
        return False, None
