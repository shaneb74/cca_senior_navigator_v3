# Demo User Creation Guide

## Overview

Demo users are **protected profiles** with complete, pre-filled data used for testing, demos, and development. They auto-refresh from this `demo/` directory on every login, ensuring consistent starting state.

**Key Principle**: Demo source files in `data/users/demo/` are **READ-ONLY**. The app copies them to `data/users/` as working copies that can be modified during the session but reset on next login.

---

## Quick Start

### 1. Create Generation Script

Create a new file: `create_demo_<name>.py` (e.g., `create_demo_andy.py`)

```python
#!/usr/bin/env python3
"""
Create <Name> Demo Profile

Description of what this profile demonstrates.

Output: data/users/demo/demo_<name>_<description>.json
"""

import json
from pathlib import Path
import time
from datetime import datetime

# Current timestamp for created_at/last_updated
TIMESTAMP = time.time()

# UID MUST be prefixed with "demo_" for protected demo loading
UID = "demo_<name>_<description>"

data = {
    # ... profile data (see structure below)
}

def main():
    """Create the demo profile file."""
    demo_dir = Path("data/users/demo")
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = demo_dir / f"{UID}.json"
    
    if output_file.exists():
        print(f"⚠️  Profile file already exists: {output_file}")
        response = input("Overwrite? (yes/no): ").strip().lower()
        if response not in ["yes", "y"]:
            print("❌ Aborted.")
            return
    
    try:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Profile created successfully!")
        print(f"   File: {output_file}")
        # ... add verification output
        
    except Exception as e:
        print(f"❌ Error writing profile: {e}")
        return

if __name__ == "__main__":
    main()
```

### 2. Run Script

```bash
python3 create_demo_<name>.py
```

### 3. Add to Login Page

Edit `pages/login.py`, add to `DEMO_USERS` dict:

```python
DEMO_USERS = {
    # ... existing users
    "demo_<key>": {
        "name": "<Display Name>",
        "email": "<email>@demo.test",
        "uid": "demo_<name>_<description>",  # MUST match filename
        "description": "<Brief description for login button>",
    },
}
```

### 4. Test

```bash
# Delete any existing working copy
rm -f data/users/demo_<name>_<description>.json

# Login as demo user
# Navigate to http://localhost:8501/?page=login
# Click the new demo user button
```

---

## Critical Rules

### 1. UID & Filename Matching

✅ **CORRECT**:
- UID: `demo_andy_assisted_gcp_complete`
- Filename: `demo_andy_assisted_gcp_complete.json`
- Pattern: `{uid}.json`

❌ **WRONG**:
- UID: `demo_andy_assisted_gcp_complete`
- Filename: `andy_assisted_gcp_complete.json` (missing `demo_` prefix)

**Why**: `load_user()` looks for `data/users/demo/{uid}.json`. Mismatch = file not found = empty profile.

### 2. UID Must Start with "demo_"

```python
# ✅ CORRECT
UID = "demo_john_cost_planner"
UID = "demo_sarah_memory_care"

# ❌ WRONG
UID = "john_demo"
UID = "test_user"
```

**Why**: `is_demo_user(uid)` checks `uid.startswith("demo_")` to trigger protected loading.

### 3. Numeric Timestamps

```python
# ✅ CORRECT
import time
TIMESTAMP = time.time()

data = {
    "created_at": TIMESTAMP,
    "last_updated": TIMESTAMP,
    # ...
}

# ❌ WRONG
data = {
    "created_at": "2025-10-19",  # String, not number
    "last_updated": datetime.now().isoformat(),  # String, not number
}
```

**Why**: Persistence system expects numeric unix timestamps for `created_at`/`last_updated`.

### 4. Include ALL USER_PERSIST_KEYS

Required top-level keys (from `core/session_store.py`):

```python
data = {
    "uid": UID,                    # String
    "created_at": TIMESTAMP,       # Numeric timestamp
    "last_updated": TIMESTAMP,     # Numeric timestamp
    "auth": {...},                 # Auth block
    "profile": {...},              # User profile
    "mcip_contracts": {...},       # MCIP state
    "tiles": {...},                # Tile states
    "progress": {},                # Product progress (can be empty)
    "preferences": {},             # UI preferences (can be empty)
    "flags": {...},                # Feature flags
    # Product-specific keys as needed
}
```

### 5. Auth Block Required

```python
"auth": {
    "user_id": UID,              # MUST match top-level uid
    "is_authenticated": True,
    "name": "Display Name",
    "email": "email@demo.test"
}
```

**Why**: Session state expects authenticated users to have auth data.

---

## MCIP Dataclass Contracts

### CareRecommendation (Required if GCP Complete)

**All 14 fields required** - missing any will cause `TypeError`:

```python
"mcip_contracts": {
    "care_recommendation": {
        # Core fields
        "tier": "assisted_living",                    # str
        "tier_score": 18.0,                           # float
        "tier_rankings": [                            # list[list]
            ["memory_care_high_acuity", 70.0],
            ["memory_care", 32.0],
            ["assisted_living", 18.0],
            ["in_home", 12.5],
            ["no_care_needed", 4.0]
        ],
        "confidence": 0.73,                           # float (0.0-1.0)
        
        # Flags - list of flag objects (NOT dict of booleans)
        "flags": [                                    # list[dict]
            {
                "id": "veteran_aanda_risk",
                "label": "VA A&A Eligible",
                "description": "May qualify for VA Aid & Attendance benefits",
                "tone": "success",  # success|warning|info|error
                "priority": 1,      # 1-5
                "cta": {
                    "label": "Check VA Benefits",
                    "route": "learning",
                    "filter": "va_benefits"
                }
            },
            # ... more flags
        ],
        
        # Rationale - list of strings (NOT single string)
        "rationale": [                                # list[str]
            "Assisted living recommended based on moderate ADL/IADL needs",
            "Lack of family support system increases care requirements",
            "Safety concerns warrant 24/7 staff availability"
        ],
        
        # Metadata fields
        "generated_at": "2025-10-19T11:24:52.445680", # str (ISO timestamp)
        "version": "4.0",                             # str
        "input_snapshot_id": "andy_gcp_1760891092",   # str
        "rule_set": "gcp_v4_standard",                # str
        
        # Next step - dict with product/label/reason (NOT string)
        "next_step": {                                # dict[str, str]
            "product": "cost_planner",
            "label": "Explore Costs",
            "reason": "Review budget and payment options"
        },
        
        # Status fields
        "status": "complete",                         # str
        "last_updated": "2025-10-19T11:24:52.445685", # str (ISO timestamp)
        "needs_refresh": False                        # bool
    }
}
```

**Common Mistakes**:

❌ **WRONG** - Dict instead of list:
```python
"flags": {
    "veteran_aanda_risk": True,
    "no_support": True
}
```

❌ **WRONG** - String instead of list:
```python
"rationale": "Assisted living recommended..."
```

❌ **WRONG** - Missing required fields:
```python
{
    "tier": "assisted_living",
    "confidence": 0.73,
    "status": "complete"
    # Missing 11 other required fields!
}
```

### FinancialProfile (Required if Cost Planner Complete)

**All 7 fields required** - only include if user completed Cost Planner:

```python
"mcip_contracts": {
    "financial_profile": {
        "estimated_monthly_cost": 7574.0,             # float
        "coverage_percentage": 15.85,                 # float (0-100)
        "gap_amount": 6374.0,                         # float
        "runway_months": 8,                           # int
        "confidence": 0.85,                           # float (0.0-1.0)
        "generated_at": "2025-10-19T11:29:39.178097", # str (ISO timestamp)
        "status": "complete"                          # str
    }
}
```

**If Cost Planner NOT complete**: Omit `financial_profile` entirely (don't include empty object).

```python
# ✅ CORRECT - User hasn't done Cost Planner
"mcip_contracts": {
    "care_recommendation": {...},
    "journey": {...}
    # NO financial_profile key at all
}

# ❌ WRONG - Empty financial_profile
"mcip_contracts": {
    "care_recommendation": {...},
    "financial_profile": {}  # Will cause TypeError
}
```

### Journey Tracking

```python
"mcip_contracts": {
    "journey": {
        "current_hub": "concierge",
        "completed_products": ["gcp"],              # Only products actually finished
        "unlocked_products": ["cost_planner", "facility_finder"],
        "recommended_next": "cost_planner"
    },
    "waiting_room": {
        "status": "available",
        "appointment_scheduled": False
    }
}
```

---

## Tiles State

Mirrors product completion for UI display:

```python
"tiles": {
    "gcp_v4": {
        "status": "done",            # not_started | in_progress | done
        "progress": 100.0,
        "tier": "assisted_living",
        "confidence": 0.73,
        "tier_score": 18.0,
        "last_updated": TIMESTAMP
    },
    "cost_planner_v2": {
        "status": "not_started",     # Unlocked but not started
        "progress": 0,
        "last_updated": TIMESTAMP
    }
}
```

**Tile Status Values**:
- `"not_started"` - Product available but not begun
- `"in_progress"` - Product started but not finished
- `"done"` - Product completed

---

## Profile & Qualifiers

```python
"profile": {
    "name": "Andy",
    "age_range": "75-84",
    "location": "San Francisco, CA",
    "zip_code": "94102",
    "relationship": "self",
    "qualifiers": {
        "is_veteran": True,
        "service_connected_disability": False,
        "has_spouse": False,
        "spouse_needs_care": False
    }
},

# Duplicate qualifiers for Cost Planner compatibility
"cost_v2_qualifiers": {
    "is_veteran": True,
    "service_connected_disability": False,
    "has_spouse": False,
    "spouse_needs_care": False
}
```

**Why duplicate?**: Legacy compatibility - both GCP and Cost Planner read qualifiers.

---

## Feature Flags

```python
"flags": {
    "is_veteran": True,
    "veteran_aanda_risk": True,
    "enable_cost_planner_v2": True
    # Add any feature toggles needed
}
```

---

## Cost Planner Quick Estimate (Optional)

If you want to show a quick cost estimate without full Cost Planner completion:

```python
"cost_v2_quick_estimate": {
    "location": "San Francisco, CA",
    "tier": "assisted_living",
    "tier_multiplier": 1.4,
    "base_cost": 5410,
    "adjusted_cost": 7574,
    "breakdown": {
        "room_board": 4500,
        "care_services": 1800,
        "medication_management": 450,
        "activities": 300,
        "transportation": 250,
        "personal_care": 274
    },
    "created_at": TIMESTAMP
}
```

This shows on the GCP results page but **doesn't mark Cost Planner as complete**.

---

## Common Scenarios

### Scenario 1: GCP Complete Only

User finished Guided Care Plan, hasn't started Cost Planner:

```python
data = {
    "uid": "demo_user_gcp_only",
    # ... auth, profile, flags
    "mcip_contracts": {
        "care_recommendation": {
            # All 14 required fields
        },
        # NO financial_profile
        "journey": {
            "completed_products": ["gcp"],
            "unlocked_products": ["cost_planner", "facility_finder"]
        }
    },
    "tiles": {
        "gcp_v4": {"status": "done", "progress": 100.0},
        "cost_planner_v2": {"status": "not_started", "progress": 0}
    }
}
```

**Result**:
- GCP tile: ✅ Complete
- Cost Planner tile: 🔓 Unlocked (not complete)

### Scenario 2: GCP + Cost Planner Complete

User finished both products:

```python
data = {
    "uid": "demo_user_full_journey",
    # ... auth, profile, flags
    "mcip_contracts": {
        "care_recommendation": {
            # All 14 required fields
        },
        "financial_profile": {
            # All 7 required fields
        },
        "journey": {
            "completed_products": ["gcp", "cost_planner"],
            "unlocked_products": ["facility_finder"]
        }
    },
    "tiles": {
        "gcp_v4": {"status": "done", "progress": 100.0},
        "cost_planner_v2": {"status": "done", "progress": 100.0}
    },
    # Include cost_v2_modules with completed module data
    "cost_v2_modules": {
        "income": {
            "status": "completed",
            "progress": 100,
            "data": {"status": "done", ...}
        },
        # ... other modules
    },
    "cost_v2_step": "exit"  # Show completed summary
}
```

**Result**:
- GCP tile: ✅ Complete
- Cost Planner tile: ✅ Complete

### Scenario 3: Fresh Start

New user, no products started:

```python
data = {
    "uid": "demo_user_fresh",
    # ... auth, profile, flags
    "mcip_contracts": {
        # NO care_recommendation
        # NO financial_profile
        "journey": {
            "completed_products": [],
            "unlocked_products": []
        }
    },
    "tiles": {
        "gcp_v4": {"status": "not_started", "progress": 0},
        "cost_planner_v2": {"status": "not_started", "progress": 0}
    }
}
```

**Result**:
- GCP tile: 🆕 Not started
- Cost Planner tile: 🔒 Locked

---

## Verification Checklist

Before committing a new demo user:

### File Structure
- [ ] File in `data/users/demo/` directory
- [ ] Filename matches pattern: `{uid}.json`
- [ ] UID starts with `demo_`
- [ ] UID in filename matches UID in JSON

### Required Fields
- [ ] `uid` (string, matches filename)
- [ ] `created_at` (numeric timestamp)
- [ ] `last_updated` (numeric timestamp)
- [ ] `auth` block with `user_id` matching `uid`
- [ ] `profile` with basic info
- [ ] `mcip_contracts` with journey
- [ ] `tiles` with product states
- [ ] `flags` for feature toggles

### MCIP Contracts
- [ ] If GCP complete: `care_recommendation` has all 14 fields
- [ ] If GCP complete: `flags` is list[dict], not dict
- [ ] If GCP complete: `tier_rankings` is list[list], not dict
- [ ] If GCP complete: `rationale` is list[str], not str
- [ ] If GCP complete: `next_step` is dict, not str
- [ ] If Cost Planner complete: `financial_profile` has all 7 fields
- [ ] If Cost Planner NOT complete: NO `financial_profile` key

### Journey Consistency
- [ ] `journey.completed_products` matches tile statuses
- [ ] `journey.unlocked_products` makes sense for journey state
- [ ] Tile progress matches completion status (0 or 100)

### Login Integration
- [ ] Added to `pages/login.py` DEMO_USERS dict
- [ ] UID in login.py matches filename
- [ ] Description is clear and helpful

### Testing
- [ ] Delete working copy: `rm -f data/users/{uid}.json`
- [ ] Login as demo user
- [ ] Verify no TypeErrors
- [ ] Verify tiles show correct status
- [ ] Verify products work as expected

---

## Troubleshooting

### "TypeError: CareRecommendation() missing required field"

**Cause**: Missing or wrong fields in `care_recommendation`

**Fix**: Compare against working profile (e.g., John):
```bash
jq '.mcip_contracts.care_recommendation | keys' data/users/demo/demo_john_cost_planner.json
```

Ensure all 14 fields present with correct types.

### "TypeError: FinancialProfile() missing required field"

**Cause**: Wrong field names or missing fields in `financial_profile`

**Fix**: 
- Use correct field names: `estimated_monthly_cost`, `coverage_percentage`, `gap_amount`
- Include all 7 required fields
- Or remove `financial_profile` entirely if not needed

### "Profile not loading / shows empty"

**Cause**: Filename doesn't match UID

**Fix**:
```bash
# Check UID in JSON
jq '.uid' data/users/demo/your_file.json

# Check filename
ls data/users/demo/

# They must match exactly!
```

### "Demo user changes persist between logins"

**Expected behavior**: Demo users auto-refresh from `demo/` directory on login.

**If changes persist**: 
- Working copy in `data/users/` may not be getting deleted
- Check `core/session_store.py:load_user()` is copying from demo source

---

## Best Practices

### 1. Use Existing Profiles as Templates

Copy from working profiles:
```bash
# Start with John's structure
cp data/users/demo/demo_john_cost_planner.json data/users/demo/demo_new_user.json

# Edit to customize
```

### 2. Version Control

- Commit demo source files in `data/users/demo/`
- Do NOT commit working copies in `data/users/`
- Add to `.gitignore`: `data/users/*.json` (but NOT `data/users/demo/*.json`)

### 3. Documentation

Add header comment in generation script explaining:
- What scenario this profile demonstrates
- What products are complete
- Any special flags or conditions
- Expected UI behavior

### 4. Naming Convention

Use descriptive UIDs:
- `demo_john_cost_planner` - Has complete Cost Planner
- `demo_andy_assisted_gcp_complete` - GCP complete, no Cost Planner
- `demo_sarah_memory_care` - Memory care tier
- `demo_bob_veteran` - Veteran with VA benefits

---

## File Locations

```
data/users/
├── demo/                              # Protected demo sources (tracked in git)
│   ├── README_DEMO_USER_CREATION.md  # This file (KEEP)
│   ├── demo_john_cost_planner.json   # John - Full journey
│   ├── demo_andy_assisted_gcp_complete.json  # Andy - GCP only
│   ├── demo_mary_full_data.json      # Mary - Complete data
│   └── demo_sarah_cost_planner.json  # Sarah - Memory care
│
├── {uid}.json                         # Working copies (gitignored)
└── anon_*.json                        # Anonymous users (gitignored)

create_demo_john_v2.py    # Generation script (tracked in git)
create_demo_andy.py       # Generation script (tracked in git)
```

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Create new demo | `python3 create_demo_<name>.py` |
| Verify structure | `jq '.mcip_contracts.care_recommendation \| keys' demo_file.json` |
| Delete working copy | `rm -f data/users/demo_<uid>.json` |
| Test login | Navigate to login page, click demo button |
| Check UID match | `jq '.uid' demo_file.json` vs filename |
| Compare to John | `jq '.mcip_contracts' demo_john_cost_planner.json` |

---

## Support

**Questions?** Check:
1. `HOW_PERSISTENCE_WORKS.md` - Explains load/save mechanics
2. `core/mcip.py` - Dataclass definitions (lines 14-45)
3. `core/session_store.py` - Demo loading logic (lines 381-425)
4. Existing profiles in `data/users/demo/` - Working examples

**Still stuck?** Compare your profile structure exactly against `demo_john_cost_planner.json` - it has complete, working examples of all contracts.

---

**Last Updated**: October 19, 2025  
**Version**: 1.0  
**Status**: ✅ Keep - Reference documentation
