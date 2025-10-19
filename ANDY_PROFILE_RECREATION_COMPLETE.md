# Andy Demo Profile Recreation - Complete ✅

## Problem Identified

**Root Cause**: Filename mismatch between UID and demo source file
- **UID in login.py**: `demo_andy_assisted_gcp_complete`
- **Expected filename**: `demo_andy_assisted_gcp_complete.json`
- **Actual filename**: `andy_assisted_gcp_complete.json` ❌

The `load_user()` function in `core/session_store.py` (lines 381-425) looks for demo files using the pattern `{uid}.json`, so it couldn't find Andy's profile.

## Solution

Recreated Andy's profile from scratch following all demo user checklist rules:

### 1. Created Proper Generation Script
**File**: `create_demo_andy.py`
- Mirrors `create_demo_john_v2.py` structure
- Includes all required USER_PERSIST_KEYS
- Proper numeric timestamps
- UID prefixed with `demo_`

### 2. Profile Structure (Following All Rules)

✅ **Identity & Auth**
- `uid`: `demo_andy_assisted_gcp_complete`
- `auth.user_id`: matches UID
- `auth.is_authenticated`: true

✅ **Profile & Qualifiers**
- Age: 75-84
- Location: San Francisco, CA
- `profile.qualifiers` and `cost_v2_qualifiers` duplicated
- Veteran status included

✅ **Feature Flags**
- `is_veteran`: true
- `veteran_aanda_risk`: true
- `enable_cost_planner_v2`: true

✅ **Care Snapshot**
- Complete `gcp_care_recommendation` block
- `gcp_v4_published`: true
- `mcip_contracts.care_recommendation` fully populated
- Status: "complete"
- Tier: "assisted_living" (18 points, 73% confidence)

✅ **Financial Profile**
- `mcip_contracts.financial_profile` with estimate/coverage/gap/runway
- `cost_v2_quick_estimate` with San Francisco multiplier (1.4x)
- Monthly estimate: $7,574

✅ **Journey & Tiles**
- `mcip_contracts.journey.completed_products`: ["gcp"]
- `mcip_contracts.journey.unlocked_products`: ["cost_planner", "facility_finder"]
- `tiles.gcp_v4.status`: "done"
- `tiles.gcp_v4.progress`: 100.0

✅ **Ops Requirements**
- Stored in: `data/users/demo/demo_andy_assisted_gcp_complete.json`
- Filename matches UID pattern
- Already registered in `pages/login.py` DEMO_USERS
- Old incorrectly named files cleaned up

## Files Modified

### Created
1. **create_demo_andy.py** - Profile generation script
   - 380 lines
   - Follows demo user checklist exactly
   - Includes verification output

### Updated
2. **data/users/demo/demo_andy_assisted_gcp_complete.json** - Demo source
   - 4.7 KB (178 lines)
   - Proper UID: `demo_andy_assisted_gcp_complete`
   - All completion markers in place

### Already Configured (No Changes Needed)
3. **pages/login.py** - Login configuration
   - Andy already in DEMO_USERS dict (from previous session)
   - UID matches new filename

### Cleaned Up
4. Removed old files:
   - `andy_assisted_gcp_complete.json` (wrong name)
   - `andy_assisted_gcp_complete_EXACT_JOHN.json` (backup)
   - `andy_assisted_gcp_complete_OLD.json` (backup)

## How Demo Loading Works

```python
# From core/session_store.py (lines 381-425)

def load_user(uid: str) -> dict[str, Any]:
    """Load user profile and progress from disk."""
    
    path = get_user_path(uid)  # data/users/{uid}.json (working copy)
    
    # Check if this is a demo user
    if is_demo_user(uid):  # Checks if uid.startswith('demo_')
        demo_path = get_demo_path(uid)  # data/users/demo/{uid}.json
        
        # Always refresh working copy from demo source if it exists
        if demo_path.exists():
            print(f"[DEMO] Loading fresh demo profile from: {demo_path}")
            print(f"[DEMO] Creating/refreshing working copy at: {path}")
            shutil.copy2(demo_path, path)  # Force overwrite
            print(f"[DEMO] ✅ Demo profile copied successfully!")
    
    # Load from working copy
    data = _safe_read(path)
    return data
```

**Key Points**:
1. Demo source in `data/users/demo/` is **read-only** and **never modified**
2. Working copy in `data/users/` is **always refreshed** from demo source on login
3. Filename MUST match UID pattern: `{uid}.json`
4. UID MUST start with `demo_` to trigger demo loading logic

## Testing Steps

### 1. Verify Clean State
```bash
# Demo source should exist
ls -lh data/users/demo/demo_andy_assisted_gcp_complete.json
# Should show: 4.7K file

# Working copy should NOT exist (we deleted it)
ls data/users/demo_andy_assisted_gcp_complete.json
# Should show: No such file or directory
```

### 2. Test Login
1. Navigate to: `http://localhost:8501/?page=login`
2. Click **"👤 Andy Assisted GCP Complete"** button
3. Watch terminal for demo copy logs:
   ```
   [DEMO] Loading fresh demo profile from: data/users/demo/demo_andy_assisted_gcp_complete.json
   [DEMO] Creating/refreshing working copy at: data/users/demo_andy_assisted_gcp_complete.json
   [DEMO] ✅ Demo profile copied successfully!
   ```
4. Should redirect to Concierge Hub

### 3. Verify GCP Tile
- **Expected**: GCP tile shows "✅ Assisted Living (73% confidence)"
- **Expected**: GCP is marked as complete (green checkmark)
- **Expected**: Cost Planner is unlocked

### 4. Verify Persistence
1. Refresh browser → GCP should remain complete
2. Navigate away and back → GCP should remain complete
3. Restart app → GCP should remain complete

### 5. Verify No Regression
- Test John's profile → Should still work
- Test other demo users → Should still work

## What Was Wrong Before

1. **Filename didn't match UID**:
   - UID: `demo_andy_assisted_gcp_complete`
   - File: `andy_assisted_gcp_complete.json` (missing `demo_` prefix)
   - Result: `get_demo_path()` couldn't find the file

2. **load_user() fell back to empty default**:
   - Couldn't find demo source
   - Created empty working copy
   - Empty data merged into session state
   - GCP showed as "not started"

3. **GCP restart fix was irrelevant**:
   - The restart fix (requiring `?restart=true`) was correct
   - But it didn't help because the profile wasn't loading at all
   - The real issue was the filename mismatch

## Success Criteria

✅ Filename matches UID pattern  
✅ Demo source exists in correct location  
✅ All completion markers present in JSON  
✅ Login page configured  
✅ Working copy deleted for fresh test  
✅ Old incorrectly named files cleaned up  
✅ Generation script available for future updates  

## Next Steps

1. **Test the login** as described above
2. **Verify GCP shows complete** on first load
3. **If it works**, commit the changes:
   ```bash
   git add create_demo_andy.py
   git add data/users/demo/demo_andy_assisted_gcp_complete.json
   git commit -m "feat: Add Andy demo profile with complete GCP

   - Created proper demo profile with correct UID/filename match
   - Includes complete GCP (Assisted Living, 73% confidence)
   - VA A&A eligibility flags included
   - Follows all demo user checklist rules
   - Generated via create_demo_andy.py script"
   ```

## Troubleshooting

### Issue: "GCP still shows incomplete"
**Check**: Did you clear the working copy?
```bash
rm -f data/users/demo_andy_assisted_gcp_complete.json
```

### Issue: "Profile not loading"
**Check**: Does demo source exist with correct name?
```bash
ls -lh data/users/demo/demo_andy_assisted_gcp_complete.json
```

### Issue: "Different data than expected"
**Regenerate**: Run the creation script
```bash
python3 create_demo_andy.py
# Say "yes" to overwrite
```

## Files Reference

| File | Purpose | Size |
|------|---------|------|
| `create_demo_andy.py` | Generation script | 12 KB |
| `data/users/demo/demo_andy_assisted_gcp_complete.json` | Demo source (read-only) | 4.7 KB |
| `data/users/demo_andy_assisted_gcp_complete.json` | Working copy (created on login) | 4.7 KB |
| `pages/login.py` | Login configuration (already has Andy) | N/A |

---

**Status**: ✅ Ready to test  
**Last Updated**: October 19, 2025  
**Session**: Andy Profile Recreation
