#!/usr/bin/env python3
"""Create demo_mary_memorycare user with GCP+CP complete flags for CCR tile unlock."""
from __future__ import annotations
import json
import pathlib
import time

# Use current directory as root
ROOT = pathlib.Path.cwd()
user_dir = ROOT / "data" / "users" / "demo_mary_memorycare"
user_dir.mkdir(parents=True, exist_ok=True)

now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

session = {
    "gcp": {
        "summary_ready": True,
        "published_tier": "memory_care",
        "flags": [
            {"id": "severe_cognitive_risk", "label": "Severe cognitive impairment"},
            {"id": "fall_risk", "label": "Fall risk"},
            {"id": "adl_support_high", "label": "Multiple ADLs require assistance"},
            {"id": "medication_management", "label": "Complex medication regimen"},
        ],
    },
    "cost": {
        "completed": True,
        "monthly_total": 6825.0,
        "last_totals": {"mc": 6825.0, "al": 5175.0},
    },
    "_qe_totals": {"mc": 6825.0, "al": 5175.0},
    "ccr": {"checklist_generated": False, "appt_scheduled": False},
    "profile": {"first_name": "Mary", "age_band": "80–89"},
}

with (user_dir / "session.json").open("w", encoding="utf-8") as f:
    json.dump(session, f, ensure_ascii=False, indent=2)

print(f"[DEMO] wrote demo user at {user_dir}/session.json")
