#!/usr/bin/env python3
"""Smoke test for LLM summary generation (no Streamlit required)."""

import sys
import json

# Add parent to path for imports
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai.summary_engine import generate_summary
from ai.llm_client import get_openai_model

ctx = {
    "badls": ["bathing", "mobility"],
    "iadls": ["med_management", "finances"],
    "mobility": "walker",
    "falls": "one",
    "behaviors": ["confusion"],
    "meds_complexity": "moderate",
    "isolation": "somewhat",
    "has_partner": False,
}
tier = "assisted_living"
suggested = "4-8h"
user_hours = "1-3h"

ok, adv = generate_summary(ctx, tier, suggested, user_hours, mode="assist")
print(f"[SMOKE] model={get_openai_model()} ok={ok} advice={'yes' if adv else 'no'}")
if ok and adv:
    d = adv.model_dump() if hasattr(adv, "model_dump") else adv
    print("[SMOKE] headline:", d.get("headline", "")[:120])
    print("[SMOKE] keys:", list(d.keys()))
    sys.exit(0)
else:
    sys.exit(2)
