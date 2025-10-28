#!/usr/bin/env python3
"""Seed demo_mary_memorycare user with GCP + CP complete (unlocks CCR tile).

Creates protected demo profile in data/users/demo/ directory.
This file is never modified by the app - it's copied to data/users/ on first load.
"""
import json
from pathlib import Path

# Demo user session data (Memory Care tier)
session_data = {
    "gcp": {
        "summary_ready": True,  # GCP complete (canonical gate)
        "published_tier": "memory_care",
        "flags": [
            {"id": "severe_cognitive_risk", "label": "Severe cognitive impairment"},
            {"id": "fall_risk", "label": "Fall risk"},
            {"id": "adl_support_high", "label": "Multiple ADLs require assistance"},
            {"id": "medication_management", "label": "Complex medication regimen"},
        ]
    },
    "cost": {
        "completed": True,  # CP complete (canonical gate)
        "monthly_total": 6825.0,
        "last_totals": {
            "mc": 6825.0,
            "al": 5175.0,
        }
    },
    "_qe_totals": {
        "mc": 6825.0,
        "al": 5175.0,
    },
    "ccr": {
        "checklist_generated": False,
        "appt_scheduled": False,
    },
    "profile": {
        "first_name": "Mary",
        "age_band": "80–89",
    },
}

# Write to protected demo directory (read-only source for app)
demo_dir = Path.cwd() / "data" / "users" / "demo"
demo_dir.mkdir(parents=True, exist_ok=True)
demo_path = demo_dir / "demo_mary_memorycare.json"
demo_path.write_text(json.dumps(session_data, indent=2))
print(f"[DEMO] wrote protected demo profile at {demo_path}")
print(f"[DEMO] app will copy to data/users/demo_mary_memorycare.json on first load")
