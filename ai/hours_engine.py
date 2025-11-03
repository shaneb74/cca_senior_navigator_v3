"""
Hours/day suggestion engine (baseline + LLM refinement).

Provides:
- baseline_hours(): Transparent rule-based suggestion (legacy simple thresholds)
- calculate_baseline_hours_weighted(): Realistic weighted scoring based on actual care tasks
- generate_hours_advice(): Schema-validated LLM refinement
"""
import json
import os

import streamlit as st

from ai.hours_schemas import HoursAdvice, HoursBand, HoursContext
from ai.hours_weights import (
    get_badl_hours,
    get_iadl_hours,
    get_cognitive_multiplier,
    get_fall_risk_multiplier,
    get_mobility_hours,
)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def calculate_baseline_hours_weighted(context: HoursContext) -> HoursBand:
    """
    Calculate realistic hours/day using weighted scoring system.
    
    Uses actual care task times rather than simple thresholds:
    - BADLs weighted by task/availability time (toileting→2.0h, bathing→0.5h)
    - IADLs weighted by frequency (medication→0.5h, housekeeping→1.5h)
    - Cognitive multiplier applied (mild→1.2x, moderate→1.6x, severe→2.2x)
    - Behavior adjustments added (wandering+0.3h, aggression+0.2h, etc.)
    - Fall risk multiplier (once→1.1x, multiple→1.3x, frequent→1.5x)
    - Mobility aid hours added (cane→0.2h, walker→0.5h, wheelchair→1.0h)
    
    Returns:
        HoursBand: "<1h", "1-3h", "4-8h", or "24h"
    """
    # Start with base hours from weighted ADL/IADL tasks
    total_hours = 0.0
    
    # Sum BADL hours
    badl_hours = sum(get_badl_hours(badl) for badl in context.badls_list)
    print(f"[HOURS_WEIGHTED] BADL hours: {badl_hours:.1f}h from {context.badls_list}")
    
    # Sum IADL hours
    iadl_hours = sum(get_iadl_hours(iadl) for iadl in context.iadls_list)
    print(f"[HOURS_WEIGHTED] IADL hours: {iadl_hours:.1f}h from {context.iadls_list}")
    
    total_hours = badl_hours + iadl_hours
    
    # Apply cognitive multiplier (supervision overhead)
    cognitive_mult = get_cognitive_multiplier(context.cognitive_level)
    if cognitive_mult > 1.0:
        print(f"[HOURS_WEIGHTED] Cognitive multiplier: {cognitive_mult}x for {context.cognitive_level}")
        total_hours *= cognitive_mult
    
    # Add behavior-specific hours (cumulative)
    behavior_hours = 0.0
    if context.wandering:
        behavior_hours += 0.3
        print("[HOURS_WEIGHTED] +0.3h for wandering risk")
    if context.aggression:
        behavior_hours += 0.2
        print("[HOURS_WEIGHTED] +0.2h for aggression management")
    if context.sundowning:
        behavior_hours += 0.3
        print("[HOURS_WEIGHTED] +0.3h for sundowning support")
    if context.repetitive_questions:
        behavior_hours += 0.1
        print("[HOURS_WEIGHTED] +0.1h for cognitive symptom management")
    
    total_hours += behavior_hours
    
    # Apply fall risk multiplier
    fall_mult = get_fall_risk_multiplier(context.falls)
    if fall_mult > 1.0:
        print(f"[HOURS_WEIGHTED] Fall risk multiplier: {fall_mult}x for {context.falls}")
        total_hours *= fall_mult
    
    # Add mobility aid hours
    mobility_hours = get_mobility_hours(context.mobility)
    if mobility_hours > 0:
        print(f"[HOURS_WEIGHTED] +{mobility_hours}h for {context.mobility} mobility aid")
        total_hours += mobility_hours
    
    # Apply overnight floor if needed
    if context.overnight_needed and total_hours < 16.0:
        print(f"[HOURS_WEIGHTED] Overnight floor: {total_hours:.1f}h → 16.0h")
        total_hours = 16.0
    
    print(f"[HOURS_WEIGHTED] Total weighted hours: {total_hours:.1f}h")
    
    # Convert to band
    if total_hours < 2.0:
        return "<1h"
    elif total_hours < 4.0:
        return "1-3h"
    elif total_hours < 12.0:
        return "4-8h"
    else:
        return "24h"


def baseline_hours(context: HoursContext) -> HoursBand:
    """
    Transparent baseline rules for hours/day suggestion.
    
    DEPRECATED: Use calculate_baseline_hours_weighted() for more realistic estimates.
    This function remains as fallback only.
    
    Rules (in priority order):
    1. If overnight_needed OR risky_behaviors: floor at "4-8h" (LLM may escalate to "24h")
    2. Elif badls_count >= 3 OR falls == "multiple": "4-8h"
    3. Elif badls_count == 2 OR iadls_count >= 3 OR mobility in {"walker", "wheelchair"}: "1-3h"
    4. Else: "<1h"
    """
    # Priority 1: Safety/behavioral needs
    if context.overnight_needed or context.risky_behaviors:
        return "4-8h"  # Floor; LLM can escalate to "24h" with justification

    # Priority 2: High ADL needs or fall risk
    if context.badls_count >= 3 or context.falls == "multiple":
        return "4-8h"

    # Priority 3: Moderate ADL needs or mobility aids
    if (
        context.badls_count == 2
        or context.iadls_count >= 3
        or context.mobility in {"walker", "wheelchair"}
    ):
        return "1-3h"

    # Default: Light support
    return "<1h"


def generate_hours_advice(
    context: HoursContext, mode: str
) -> tuple[bool, HoursAdvice | None]:
    """
    Generate LLM-refined hours/day suggestion.
    
    Args:
        context: Input signals
        mode: "off" | "shadow" | "assist"
    
    Returns:
        (ok: bool, advice: Optional[HoursAdvice])
        - ok=False if mode="off" or validation fails
        - advice=None if LLM unavailable or invalid output
    """
    if mode == "off":
        return (False, None)

    if OpenAI is None:
        print("[GCP_HOURS_WARN] OpenAI not available; falling back to baseline only")
        return (False, None)

    # Get API key
    api_key = None
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        pass
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[GCP_HOURS_WARN] No OpenAI API key; falling back to baseline only")
        return (False, None)

    # Build prompt with clinical context
    baseline = calculate_baseline_hours_weighted(context)
    
    # Format ADL/IADL lists for prompt
    badls_str = ", ".join(context.badls_list) if context.badls_list else "none"
    iadls_str = ", ".join(context.iadls_list) if context.iadls_list else "none"
    
    # Format behavior flags
    behaviors = []
    if context.wandering:
        behaviors.append("wandering/elopement risk")
    if context.aggression:
        behaviors.append("aggressive behaviors")
    if context.sundowning:
        behaviors.append("sundowning/evening confusion")
    if context.repetitive_questions:
        behaviors.append("repetitive questions/behaviors")
    behaviors_str = ", ".join(behaviors) if behaviors else "none reported"

    prompt = f"""You are a care planning assistant helping estimate hours/day of care support needed.

CONTEXT:
- Basic ADLs needing help: {badls_str}
  Total count: {context.badls_count}/6
- Instrumental ADLs needing help: {iadls_str}
  Total count: {context.iadls_count}/8
- Cognitive level: {context.cognitive_level or "none"}
- Specific behaviors: {behaviors_str}
- Falls history: {context.falls or "unknown"}
- Mobility: {context.mobility or "unknown"}
- Medication complexity: {context.meds_complexity or "unknown"}
- Primary support: {context.primary_support or "unknown"}
- Overnight needs: {context.overnight_needed}
- Current arrangement: {context.current_hours or "none"}

WEIGHTED BASELINE SUGGESTION: {baseline}

CLINICAL DECISION RULES:
1. Toileting needs = 24/7 availability (2.0h base, not just task time)
2. Cognitive supervision overhead:
   - Mild: 20% more time (prompting, redirection)
   - Moderate: 60% more time (constant supervision)
   - Severe: 120% more time (hands-on guidance)
3. Fall risk = slower pace for all tasks (1.1x-1.5x multiplier)
4. Wandering = monitoring + redirection (+0.3h)
5. Aggression = de-escalation + safety (+0.2h)
6. Overnight needs = minimum 16h (not just task time)

REAL-WORLD EXAMPLES:
- 2 BADLs (bathing, dressing), no cognitive issues → 1-3h
- 3 BADLs (bathing, dressing, toileting), mild cognitive → 4-8h  
- Toileting + moderate dementia + wandering → 4-8h or 24h
- Multiple BADLs + severe cognitive + overnight → 24h

YOUR TASK:
Choose ONE band from this EXACT list ONLY:
- "<1h"   (minimal support, mostly independent)
- "1-3h"  (moderate support, some ADL help)
- "4-8h"  (substantial support, multiple ADLs or safety needs)
- "24h"   (round-the-clock care, significant medical/safety needs)

DEVELOPER RULES (STRICT):
1. Prefer the baseline suggestion unless clear evidence to adjust by ONE step
2. NEVER jump >1 step from baseline UNLESS overnight_needed=True or risky_behaviors=True
3. If overnight_needed=True or risky_behaviors=True, baseline is "4-8h" (floor); you may choose "24h" if justified
4. Provide 1-3 SHORT reasons (one sentence each) for your choice
5. Include confidence (0.0-1.0): how certain are you this matches the person's needs?

OUTPUT FORMAT (strict JSON):
{{
  "band": "<one of 4 allowed bands>",
  "reasons": ["reason 1", "reason 2", "reason 3"],
  "confidence": 0.85
}}

IMPORTANT: Output ONLY valid JSON. Do not invent band values outside the 4 allowed options.
"""

    try:
        client = OpenAI(api_key=api_key, timeout=10.0)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300,
        )

        raw = response.choices[0].message.content.strip()

        # Parse JSON
        if raw.startswith("```json"):
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif raw.startswith("```"):
            raw = raw.split("```")[1].split("```")[0].strip()

        data = json.loads(raw)

        # Validate against schema
        advice = HoursAdvice(**data)
        return (True, advice)

    except Exception as e:
        print(f"[GCP_HOURS_WARN] LLM refinement failed: {e}")
        return (False, None)


# Band ordering for under-selection detection
_BAND_ORDER = ["<1h", "1-3h", "4-8h", "24h"]


def under_selected(user_band: HoursBand | None, suggested: HoursBand) -> bool:
    """Check if user's selection is lower than the suggested band.
    
    Args:
        user_band: User's current hours selection (or None)
        suggested: Suggested band (baseline or LLM)
    
    Returns:
        True if user_band is lower than suggested in the 4-band hierarchy
    """
    if not user_band:
        return False

    try:
        user_idx = _BAND_ORDER.index(user_band)
        suggested_idx = _BAND_ORDER.index(suggested)
        return user_idx < suggested_idx
    except (ValueError, AttributeError):
        return False


def generate_hours_nudge_text(
    context: HoursContext,
    suggested: HoursBand,
    user_band: HoursBand | None,
    mode: str
) -> str | None:
    """Generate firm but supportive nudge when user under-selects hours.
    
    Uses LLM to create personalized message referencing concrete care signals.
    
    Args:
        context: HoursContext with all care signals
        suggested: Suggested band (baseline or LLM)
        user_band: User's current selection
        mode: "off" | "shadow" | "assist"
    
    Returns:
        Nudge text (1-2 sentences) or None if generation fails or mode is off
    """
    if mode == "off":
        return None

    if OpenAI is None:
        return None

    # Get API key
    api_key = None
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        pass
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[GCP_HOURS_WARN] No API key; skipping nudge")
        return None

    try:
        client = OpenAI(api_key=api_key, timeout=10.0)

        # Build minimal, guardrailed system prompt (CONCISE VERSION)
        system_prompt = """You are 'Navi', a clinical care planning assistant. Your job is to suggest daily in-home care hours.

Allowed bands ONLY: "<1h", "1-3h", "4-8h", "24h" (exactly 4 options).

The user has selected a LOWER band than recommended. Write ONE sentence (max ~24 words). No more than one clause. Zero numbers except the target band label. No lists. No second sentence.

Reference ONE or TWO key care signals (e.g., "multiple falls", "walker", "3 ADLs") and state the recommended band.

Example: "Given multiple falls and walker use, we recommend 4-8 hours per day for safety."

RULES:
- ONE sentence only
- Max 24 words
- No prices or financial calculations
- No new band values (only use the 4 allowed bands)
- No clinical guarantees or medical advice
- Be firm but supportive and respectful"""

        user_message = {
            "user_hours": user_band,
            "suggested_hours": suggested,
            "signals": {
                "badls_count": context.badls_count,
                "iadls_count": context.iadls_count,
                "falls": context.falls,
                "mobility": context.mobility,
                "risky_behaviors": context.risky_behaviors,
                "meds_complexity": context.meds_complexity,
                "primary_support": context.primary_support,
                "overnight_needed": context.overnight_needed
            }
        }

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate nudge for: {json.dumps(user_message)}"}
            ],
            max_tokens=80,  # Reduced from 160 for conciseness
            temperature=0.2,
        )

        text = (response.choices[0].message.content or "").strip()
        if not text:
            return None

        # Post-process: Keep first sentence only, trim to ≤ 160 chars
        sentences = text.split('.')
        first_sentence = sentences[0].strip()
        if first_sentence and not first_sentence.endswith('.'):
            first_sentence += '.'

        # Trim to max 160 characters
        if len(first_sentence) > 160:
            first_sentence = first_sentence[:157] + '...'

        return first_sentence

    except Exception as e:
        print(f"[GCP_HOURS_WARN] Nudge generation error: {e}")
        return None
