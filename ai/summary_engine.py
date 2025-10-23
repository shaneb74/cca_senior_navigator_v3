"""LLM-powered summary generation for GCP recommendation page."""

import json
from openai import OpenAI
from .llm_client import get_api_key, get_openai_model
from .summary_schemas import SummaryAdvice


SYSTEM_PROMPT = (
    "You are Navi, a calm, supportive care navigator. "
    "Output STRICT JSON matching SummaryAdvice (headline, why[], what_it_means?, next_steps[], next_line, confidence). "
    "Use plain, concise language. "
    "No prices, no guarantees. Allowed tiers only: none, in_home, assisted_living, memory_care, memory_care_high_acuity. "
    "For 'headline': 1 concise sentence about the recommendation. "
    "For 'what_it_means': 1 short paragraph (1-2 sentences) explaining what this tier means for daily life. "
    "For 'why': Expand 'When it's a good fit' into a short paragraph (2-4 concise sentences) drawing from ADLs, IADLs, mobility, falls, behaviors, isolation, and partner status. No costs. "
    "For 'next_line': 1 short sentence that tees up the cost view. If tier≠in_home, invite comparing the recommended tier vs in-home. "
    "If tier==in_home, invite exploring monthly cost with hours & supports. If tier==none, invite optional support cost overview."
)


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
        
        # Try parsing as JSON
        try:
            adv = SummaryAdvice.model_validate_json(text)
            return True, adv
        except Exception:
            # Fallback: try parsing as dict
            try:
                adv = SummaryAdvice(**json.loads(text))
                return True, adv
            except Exception:
                return False, None
    
    except Exception:
        return False, None
