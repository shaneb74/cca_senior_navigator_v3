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


def _apply_clinical_rules(context: HoursContext, band: HoursBand, total_hours: float) -> HoursBand:
    """
    Apply clinical escalation rules that match LLM reasoning.
    
    These deterministic rules capture clinical judgment patterns:
    1. Toileting assistance requires 24/7 availability (not just task time)
    2. Moderate+ cognitive + multiple risks → escalate for safety
    3. Overnight needs + other risk factors → strong 24h indicator
    4. Multiple falls + mobility challenges → escalate for supervision
    5. Complex medication + cognitive impairment → escalate for safety
    
    Args:
        context: HoursContext with all care signals
        band: Initial band from weighted calculation
        total_hours: Calculated hours for reference
    
    Returns:
        Escalated band if clinical rules apply, otherwise original band
    """
    _BAND_ORDER = ["<1h", "1-3h", "4-8h", "12-16h", "24h"]
    
    def escalate(current: HoursBand, target: HoursBand, reason: str) -> HoursBand:
        """Helper to escalate band with logging."""
        if _BAND_ORDER.index(target) > _BAND_ORDER.index(current):
            print(f"[HOURS_CLINICAL] Escalate {current} → {target}: {reason}")
            return target
        return current
    
    original_band = band
    
    # Rule 1: Toileting requires 24/7 availability (minimum 4-8h)
    if "toileting" in context.badls_list and band in ["<1h", "1-3h"]:
        band = escalate(band, "4-8h", "Toileting assistance requires availability")
    
    # Rule 2: Moderate+ cognitive + safety risks → escalate significantly
    if context.cognitive_level in ["moderate", "severe", "advanced"]:
        risk_count = sum([
            context.wandering,
            context.aggression,
            context.sundowning,
            getattr(context, 'elopement', False),
            getattr(context, 'confusion', False),
            context.falls in ["multiple", "frequent"],
            context.mobility in ["wheelchair", "bedbound"],
        ])
        
        if risk_count >= 2 and band in ["<1h", "1-3h"]:
            band = escalate(band, "4-8h", f"Moderate+ cognitive with {risk_count} safety risks")
        elif risk_count >= 3 and band == "4-8h":
            band = escalate(band, "12-16h", f"Moderate+ cognitive with {risk_count} major safety risks")
        elif risk_count >= 4 and band == "12-16h":
            band = escalate(band, "24h", f"Moderate+ cognitive with {risk_count} critical safety risks")
    
    # Rule 3: Overnight needs + other indicators → escalate to 12-16h
    # Only escalate to 24h if VERY high risk (3+ risks AND severe cognitive)
    if context.overnight_needed:
        overnight_risks = sum([
            context.falls in ["multiple", "frequent"],
            context.wandering or getattr(context, 'elopement', False),
            context.meds_complexity in ["moderate", "complex"],
            "toileting" in context.badls_list,
        ])
        
        if overnight_risks >= 1 and band in ["<1h", "1-3h", "4-8h"]:
            band = escalate(band, "12-16h", f"Overnight needs with {overnight_risks} risk factors")
        
        # Only escalate to 24h if severe cognitive + 3+ risks
        if overnight_risks >= 3 and band == "12-16h":
            if context.cognitive_level in ["severe", "advanced"]:
                band = escalate(band, "24h", f"Overnight + severe cognitive + {overnight_risks} critical risks")
    
    # Rule 4: Multiple falls + mobility challenges + ADLs → safety escalation
    if context.falls in ["multiple", "frequent"] and context.mobility in ["walker", "wheelchair", "bedbound"]:
        if context.badls_count >= 2 and band in ["<1h", "1-3h"]:
            band = escalate(band, "4-8h", "Multiple falls + mobility aid + ADL needs")
    
    # Rule 5: Complex medications + cognitive impairment → supervision needs
    if context.meds_complexity in ["moderate", "complex"]:
        if context.cognitive_level in ["moderate", "severe", "advanced"] and band == "1-3h":
            band = escalate(band, "4-8h", "Complex meds + cognitive impairment requires supervision")
    
    # Rule 6: Primary support context - no support + moderate needs → escalate
    if context.primary_support in ["none", None]:
        if context.badls_count >= 2 or context.iadls_count >= 3:
            if band == "1-3h":
                band = escalate(band, "4-8h", "No regular support with moderate needs")
    
    if band != original_band:
        print(f"[HOURS_CLINICAL] Final: {original_band} → {band} (clinical rules applied)")
    
    return band


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
    
    # Apply cognitive multiplier (supervision overhead including ALL behaviors)
    cognitive_mult = get_cognitive_multiplier(
        context.cognitive_level,
        has_wandering=context.wandering,
        has_aggression=context.aggression,
        has_sundowning=context.sundowning,
        has_repetitive_questions=context.repetitive_questions,
        has_elopement=getattr(context, 'elopement', False),
        has_confusion=getattr(context, 'confusion', False),
        has_judgment=getattr(context, 'judgment', False),
        has_hoarding=getattr(context, 'hoarding', False),
        has_sleep=getattr(context, 'sleep', False),
    )
    if cognitive_mult > 1.0:
        print(f"[HOURS_WEIGHTED] Cognitive multiplier: {cognitive_mult}x for {context.cognitive_level} + behaviors")
        total_hours *= cognitive_mult
    
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
    
    # Convert to band (CRITICAL: Must match production thresholds)
    # Thresholds designed to avoid edge cases pushing into higher bands
    if total_hours < 1.0:
        band = "<1h"
    elif total_hours < 4.0:
        band = "1-3h"
    elif total_hours < 10.0:  # 4-8h band extends to 10h to avoid edge case escalation
        band = "4-8h"
    elif total_hours < 20.0:  # 12-16h band for true around-the-clock cases (10-20h)
        band = "12-16h"
    else:
        band = "24h"
    
    # Apply clinical escalation rules (matches LLM logic)
    band = _apply_clinical_rules(context, band, total_hours)
    
    return band


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

    prompt = f"""You are a geriatric care planning specialist helping estimate daily care hours needed.

CLINICAL CONTEXT:

Physical Needs:
- BADLs requiring help: {context.badls_count}/6 ({badls_str})
- IADLs requiring help: {context.iadls_count}/8 ({iadls_str})
- Falls history: {context.falls or "unknown"} (risk factor for 24/7 supervision)
- Mobility: {context.mobility or "unknown"} (affects transfer time and safety)

Cognitive Status:
- Level: {context.cognitive_level or "unknown"}
- Specific behaviors: {behaviors_str}
- Supervision needs: {'Yes - constant monitoring' if context.risky_behaviors else 'Standard'}

Medical Complexity:
- Medication complexity: {context.meds_complexity or "unknown"}
- Overnight care needed: {context.overnight_needed}

Support System:
- Primary support: {context.primary_support or "unknown"}
- Current arrangement: {context.current_hours or "none established"}

WEIGHTED BASELINE SUGGESTION (rule-based): {baseline}
This baseline uses task-specific time weights, cognitive multipliers, and fall risk adjustments.

CLINICAL DECISION FRAMEWORK:

Task Time Considerations:
1. Toileting assistance → Requires availability 24/7, not just task time (2.0h base weight)
2. Bathing/dressing → Discrete time blocks (0.5-0.6h each)
3. Meal preparation → Includes shopping, cooking, cleanup (1.0h daily average)
4. Medication management → Setup, prompting, monitoring (0.5h+ for complex regimens)

Cognitive Supervision Overhead:
- None: 1.0x (no supervision needed)
- Mild: 1.2x (occasional prompting, forgetfulness)
- Moderate: 1.6x (frequent supervision, decision-making help)
- Severe: 2.2x (constant supervision, safety critical)
- Behavioral symptoms add: wandering (+0.3h), aggression (+0.2h), sundowning (+0.3h)

Fall Risk Impact:
- Once: 1.1x (some caution)
- Multiple: 1.3x (extra caution, slower pace)
- Frequent: 1.5x (very high risk, constant vigilance)

Mobility Aid Requirements:
- Cane: +0.2h (minimal assistance)
- Walker: +0.5h (more assistance, slower pace)
- Wheelchair: +1.0h (transfers, positioning)
- Bedbound: +2.0h (all transfers, repositioning)

REAL-WORLD EXAMPLES:
- "2 BADLs (bathing, dressing) + no cognition issues" → 1-3h (morning routine help)
- "3 BADLs + moderate dementia + wandering" → 4-8h (supervision overhead dominates)
- "Toileting help + falls + insulin management" → 24h (availability + medical + safety)
- "Walker + mild cognitive + 2 IADLs" → 1-3h (support for specific tasks)
- "Multiple ADLs + severe cognitive + overnight needs" → 24h (round-the-clock required)

YOUR TASK:
Choose ONE band from this EXACT list ONLY:
- "<1h"    (minimal support, mostly independent, light assistance)
- "1-3h"   (moderate support, morning/evening routines, some ADL help)
- "4-8h"   (substantial support, multiple ADLs or significant supervision needs)
- "12-16h" (around-the-clock with breaks, waking hours + overnight checks)
- "24h"    (true round-the-clock care, constant supervision required)

DECISION RULES:
1. Start with the weighted baseline - it already accounts for task times, cognitive multipliers, fall risk
2. Adjust by ONE step maximum unless clear evidence for larger change
3. Toileting needs almost always require 4-8h minimum (availability requirement)
4. Moderate+ cognitive impairment with wandering/aggression → consider 4-8h, 12-16h or 24h
5. Overnight needs + other risk factors → strong indicator for 12-16h or 24h
6. Multiple falls + mobility aid + ADLs → likely 4-8h minimum for safety
7. Use 12-16h for cases needing around-the-clock availability but not constant supervision

RESPONSE FORMAT:
Provide 2-3 SPECIFIC reasons (be clinical: "toileting requires availability" not "high needs")
Include confidence 0.0-1.0 based on data completeness and clarity

OUTPUT (JSON only, no other text):
{{
  "band": "<1h|1-3h|4-8h|12-16h|24h>",
  "reasons": ["specific reason 1 with clinical detail", "specific reason 2"],
  "confidence": 0.85
}}

CRITICAL: Output ONLY valid JSON. Do not invent band values. Be specific in reasons.
"""

    try:
        client = OpenAI(api_key=api_key, timeout=10.0)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300,
        )

        raw = (response.choices[0].message.content or "").strip()

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
_BAND_ORDER = ["<1h", "1-3h", "4-8h", "12-16h", "24h"]


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

Allowed bands ONLY: "<1h", "1-3h", "4-8h", "12-16h", "24h" (exactly 5 options).

The user has selected a LOWER band than recommended. Write ONE sentence (max ~24 words). No more than one clause. Zero numbers except the target band label. No lists. No second sentence.

Reference ONE or TWO key care signals (e.g., "multiple falls", "walker", "3 ADLs") and state the recommended band.

Example: "Given multiple falls and walker use, we recommend 4-8 hours per day for safety."

RULES:
- ONE sentence only
- Max 24 words
- No prices or financial calculations
- No new band values (only use the 5 allowed bands)
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
