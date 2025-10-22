"""
Hours/day suggestion engine (baseline + LLM refinement).

Provides:
- baseline_hours(): Transparent rule-based suggestion
- generate_hours_advice(): Schema-validated LLM refinement
"""
import json
import os
from typing import Optional, Tuple

import streamlit as st

from ai.hours_schemas import HoursBand, HoursAdvice, HoursContext

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def baseline_hours(context: HoursContext) -> HoursBand:
    """
    Transparent baseline rules for hours/day suggestion.
    
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
) -> Tuple[bool, Optional[HoursAdvice]]:
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
    
    # Build prompt
    baseline = baseline_hours(context)
    
    prompt = f"""You are a care planning assistant helping estimate hours/day of care support needed.

CONTEXT:
- Basic ADLs needing help: {context.badls_count}/6 (bathing, dressing, toileting, etc.)
- Instrumental ADLs needing help: {context.iadls_count}/8 (meds, meals, housekeeping, etc.)
- Falls history: {context.falls or "unknown"}
- Mobility: {context.mobility or "unknown"}
- Risky behaviors (wandering, aggression, etc.): {context.risky_behaviors}
- Medication complexity: {context.meds_complexity or "unknown"}
- Primary support: {context.primary_support or "unknown"}
- Overnight needs: {context.overnight_needed}
- Current arrangement: {context.current_hours or "none"}

BASELINE SUGGESTION (rule-based): {baseline}

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
