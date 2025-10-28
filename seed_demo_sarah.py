#!/usr/bin/env python3
"""Create demo_sarah user with GCP+CP complete flags for CCR tile unlock."""
from __future__ import annotations
import json
import pathlib
import time

# Use current directory as root
ROOT = pathlib.Path.cwd()
user_dir = ROOT / "data" / "users" / "demo_sarah"
user_dir.mkdir(parents=True, exist_ok=True)

now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

session = {
    # canonical GCP publish keys
    "gcp": {
        "summary_ready": True,
        "published_tier": "assisted_living",
        "flags": [
            {"id": "moderate_cognitive_decline", "label": "Moderate cognitive decline"},
            {"id": "fall_risk", "label": "Fall risk"},
            {"id": "medication_management", "label": "Complex medication regimen"},
        ],
    },
    # cost planner completion + postcard
    "cost": {
        "completed": True,
        "monthly_total": 5175.0,
        "last_totals": {"al": 5175.0, "home": 5000.0},
    },
    # quick estimate cache (so CP is instant)
    "_qe_totals": {"al": 5175.0, "home": 5000.0},
    # mark CCR in a clean initial state
    "ccr": {"checklist_generated": False, "appt_scheduled": False},
    # optional: simple identity
    "profile": {"first_name": "Sarah", "age_band": "75–84"},
}

with (user_dir / "session.json").open("w", encoding="utf-8") as f:
    json.dump(session, f, ensure_ascii=False, indent=2)

print(f"[DEMO] wrote demo user at {user_dir}/session.json")
