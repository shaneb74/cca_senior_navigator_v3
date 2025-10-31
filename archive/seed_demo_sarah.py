#!/usr/bin/env python3
"""Seed demo_sarah user with GCP + CP complete (unlocks CCR tile).

Creates protected demo profile in data/users/demo/ directory.
This file is never modified by the app - it's copied to data/users/ on first load.
"""
import json
from pathlib import Path

# Demo user session data
session_data = {
    "gcp": {
        "summary_ready": True,  # GCP complete (canonical gate)
        "published_tier": "assisted_living",
        "flags": [
            {"id": "moderate_cognitive_risk", "label": "Moderate cognitive decline"},
            {"id": "fall_risk", "label": "Fall risk"},
            {"id": "medication_management", "label": "Medication management"},
        ]
    },
    "cost": {
        "completed": True,  # CP complete (canonical gate)
        "monthly_total": 5175.0,
        "last_totals": {
            "al": 5175.0,
            "home": 5000.0,
        }
    },
    "_qe_totals": {
        "al": 5175.0,
        "home": 5000.0,
    },
    "ccr": {
        "checklist_generated": False,
        "appt_scheduled": False,
    },
    "profile": {
        "first_name": "Sarah",
        "age_band": "75–84",
    },
}

# Write to protected demo directory (read-only source for app)
demo_dir = Path.cwd() / "data" / "users" / "demo"
demo_dir.mkdir(parents=True, exist_ok=True)
demo_path = demo_dir / "demo_sarah.json"
demo_path.write_text(json.dumps(session_data, indent=2))
print(f"[DEMO] wrote protected demo profile at {demo_path}")
print(f"[DEMO] app will copy to data/users/demo_sarah.json on first load")
