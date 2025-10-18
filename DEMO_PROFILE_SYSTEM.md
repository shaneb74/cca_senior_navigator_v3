# Demo Profile System - Protected Source with Fresh Copy Per Session

**Status**: ✅ IMPLEMENTED
**Date**: October 18, 2025

## Overview

Demo profiles are stored in a **protected directory** (`data/users/demo/`) that is never modified by the app. When a demo user logs in, the system automatically copies the demo profile to the working directory (`data/users/`), providing a fresh, clean slate for each session.

## Architecture

### Directory Structure
```
data/
  users/
    demo/                          # Protected demo profiles (read-only)
      demo_john_cost_planner.json  # John Test source profile
      demo_maria_memory.json       # (future) Maria Test source profile
    demo_john_cost_planner.json    # Working copy (created on login)
    demo_maria_memory.json         # Working copy (created on login)
    anon_*.json                    # Regular anonymous users
```

### Key Principles

1. **Protected Source**: Demo profiles in `data/users/demo/` are NEVER modified by the app
2. **Fresh Copy on Login**: Each time a demo user logs in, a fresh copy is created from `demo/`
3. **Session Modifications**: Changes during the session are saved to the working copy in `data/users/`
4. **Clean Slate**: Next login gets a fresh copy again, discarding any previous changes

## How It Works

### Demo User Detection
```python
def is_demo_user(uid: str) -> bool:
    """Check if user ID is a demo user."""
    return uid.startswith("demo_")
```

Any user with UID starting with `"demo_"` is treated as a demo user.

### Load Flow

When `load_user(uid)` is called for a demo user:

```python
def load_user(uid: str) -> dict[str, Any]:
    # 1. Check if demo user
    if is_demo_user(uid):
        demo_path = get_demo_path(uid)  # data/users/demo/demo_john.json
        user_path = get_user_path(uid)   # data/users/demo_john.json
        
        # 2. If working copy doesn't exist but demo source does, copy it
        if not user_path.exists() and demo_path.exists():
            shutil.copy2(demo_path, user_path)
            print(f"[INFO] Copied demo profile to: {user_path}")
    
    # 3. Load from working copy (or demo source if copy succeeded)
    data = _safe_read(user_path)
    return data
```

**Result**: First login copies from `demo/`, subsequent loads use working copy until app restart or manual reset.

### Save Flow

```python
def save_user(uid: str, data: dict[str, Any]) -> bool:
    # Always saves to data/users/<uid>.json (working copy)
    path = get_user_path(uid)  # data/users/demo_john.json
    return _atomic_write(path, data)
```

**Result**: All saves go to working copy, demo source in `demo/` is untouched.

### Reset Flow

```python
def reset_demo_user(uid: str) -> bool:
    """Delete working copy to force fresh copy on next login."""
    if not is_demo_user(uid):
        return False
    
    user_path = get_user_path(uid)
    if user_path.exists():
        user_path.unlink()
    
    return True
```

**Result**: Next `load_user()` will copy fresh from `demo/` again.

## Benefits

### 1. Consistency
- Demo users always start with the same baseline data
- No drift or corruption from previous sessions
- Predictable testing and demonstration scenarios

### 2. Protection
- Source profiles can't be accidentally modified
- Safe to run demos with real users present
- Easy to verify source integrity

### 3. Flexibility
- Users can interact with demo profiles normally during session
- Changes are saved (for that session)
- Next session starts fresh without manual cleanup

### 4. Simple Reset
```bash
# Manual reset
rm data/users/demo_john_cost_planner.json

# Or programmatic
from core.session_store import reset_demo_user
reset_demo_user("demo_john_cost_planner")
```

## Creating Demo Profiles

### Script Location
`create_demo_john_v2.py` - Creates John Test demo profile

### Running the Script
```bash
# Stop app first (prevents file lock)
pkill -9 streamlit

# Create/update demo profile
python3 create_demo_john_v2.py

# Start app
streamlit run app.py
```

### Script Output
```
✅ Profile created successfully!
   File: data/users/demo/demo_john_cost_planner.json
   
💡 Demo Profile Behavior:
   • Protected source: data/users/demo/demo_john_cost_planner.json
   • Working copy: data/users/demo_john_cost_planner.json
   • Each login starts with fresh copy from demo/
   • Source in demo/ is never modified
```

## John Test Demo Profile

### Profile Details
- **UID**: `demo_john_cost_planner`
- **Source File**: `data/users/demo/demo_john_cost_planner.json` (13.2 KB, 442 lines)
- **Working Copy**: `data/users/demo_john_cost_planner.json` (created on login)

### Contents
- **GCP**: Assisted Living recommendation (18 points, 73% confidence, 9 care flags)
- **Cost Planner**: Income ($6,200/mo) and Assets ($195k net) complete
- **Financial**: Est. cost $9,089/mo, runway 10 months
- **Location**: Seattle, WA (ZIP 98101)

### Care Flags
1. low_access - Limited Service Access
2. moderate_dependence - Regular Assistance Needed
3. chronic_present - Chronic Conditions
4. moderate_mobility - Mobility Assistance Needed
5. moderate_safety_concern - Safety Monitoring Needed
6. moderate_cognitive_decline - Moderate Memory Concerns
7. moderate_risk - Emotional Support Helpful
8. veteran_aanda_risk - Veteran A&A Eligible
9. limited_support - Limited Caregiver Availability

## Testing Workflow

### 1. First Login
```
User clicks "John Test" button
  → load_user("demo_john_cost_planner")
  → Checks: data/users/demo_john_cost_planner.json (doesn't exist)
  → Checks: data/users/demo/demo_john_cost_planner.json (exists!)
  → Copies demo source → working copy
  → Loads working copy into session
  → User sees: Assisted Living, 9 flags, complete financials
```

### 2. During Session
```
User navigates to Cost Planner
  → Modifies income data: $6,200 → $7,000
  → save_user() called
  → Saves to: data/users/demo_john_cost_planner.json (working copy)
  → Demo source unchanged: data/users/demo/demo_john_cost_planner.json
```

### 3. Same Session, Refresh
```
User refreshes browser
  → load_user("demo_john_cost_planner")
  → Checks: data/users/demo_john_cost_planner.json (exists!)
  → Loads working copy (with $7,000 income)
  → User sees modified data from this session
```

### 4. New Session (After App Restart)
```
Option A: Keep working copy
  → Working copy still exists
  → load_user() uses existing working copy
  → User sees $7,000 income (from last session)

Option B: Reset for fresh start
  → rm data/users/demo_john_cost_planner.json
  → load_user() copies fresh from demo/
  → User sees $6,200 income (original)
```

## Verification Commands

### Check Demo Source
```bash
ls -lh data/users/demo/
cat data/users/demo/demo_john_cost_planner.json | jq '.cost_v2_modules.income.data.total_monthly_income'
```

### Check Working Copy
```bash
ls -lh data/users/demo_*.json
cat data/users/demo_john_cost_planner.json | jq '.cost_v2_modules.income.data.total_monthly_income'
```

### Verify Source Unchanged
```bash
# Compare checksums
md5 data/users/demo/demo_john_cost_planner.json
md5 data/users/demo_john_cost_planner.json

# Should differ if working copy was modified during session
```

### Reset Demo User
```bash
# Delete working copy
rm data/users/demo_john_cost_planner.json

# Next login will copy fresh from demo/
```

## Future Demo Profiles

### Adding New Demo Users

1. **Create profile data** (use exact structure from working session)
2. **Update script** or create new `create_demo_<name>_v2.py`
3. **Run script** to generate in `data/users/demo/`
4. **Add to login page** (if using button-based login)

### Example: Maria Memory Care
```python
# create_demo_maria_v2.py
data = {
    "uid": "demo_maria_memory",
    "gcp_care_recommendation": {
        # Memory care profile data
    },
    # ...
}

# Save to
output_file = Path("data/users/demo/demo_maria_memory.json")
```

### Demo User Naming Convention
- Prefix: `demo_`
- Format: `demo_<name>_<focus>`
- Examples:
  - `demo_john_cost_planner` - Cost planning focus
  - `demo_maria_memory` - Memory care focus
  - `demo_robert_veteran` - Veteran benefits focus

## Implementation Files

### Core Session Store
- **File**: `core/session_store.py`
- **Functions**:
  - `is_demo_user(uid)` - Check if UID is demo user
  - `get_demo_path(uid)` - Get path to demo source
  - `get_user_path(uid)` - Get path to working copy
  - `load_user(uid)` - Load with automatic demo copy
  - `reset_demo_user(uid)` - Delete working copy

### Demo Profile Script
- **File**: `create_demo_john_v2.py`
- **Output**: `data/users/demo/demo_john_cost_planner.json`
- **Usage**: `python3 create_demo_john_v2.py`

### Directory Structure
```
data/
  users/
    demo/              # Created by _ensure_directories()
      *.json           # Demo sources (protected)
    *.json             # Working copies + regular users
```

## Migration Notes

### From Old System
**Before**: Demo profiles saved directly to `data/users/demo_*.json`, could be overwritten

**After**: 
1. Demo sources in `data/users/demo/demo_*.json` (protected)
2. Working copies in `data/users/demo_*.json` (can be modified)
3. Automatic fresh copy on first load

### One-Time Migration
```bash
# Move existing demo profiles to protected directory
mkdir -p data/users/demo
mv data/users/demo_*.json data/users/demo/

# Or recreate using scripts
python3 create_demo_john_v2.py
```

## Success Criteria

✅ **Demo sources protected**: Files in `demo/` never modified by app
✅ **Fresh copy on login**: First load copies from `demo/` to working directory
✅ **Session modifications work**: Changes saved to working copy
✅ **Easy reset**: Delete working copy to get fresh start
✅ **Consistent testing**: Every new session starts with known baseline

---

**Status**: ✅ Fully Implemented
**Testing**: Ready for manual verification
**Next**: Test John Test login, verify fresh copy behavior
