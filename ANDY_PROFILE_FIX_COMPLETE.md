# Andy Profile Complete Fix - GCP Only (No Cost Planner) ✅

## Error Encountered

```
TypeError in CareRecommendation dataclass initialization
File: core/mcip.py, line 197: return CareRecommendation(**filtered_data)
```

**When**: Loading Andy's profile after login  
**Why**: Profile data structure didn't match `CareRecommendation` dataclass requirements

## Root Causes

### 1. Filename Mismatch (First Issue - Resolved)
- UID: `demo_andy_assisted_gcp_complete`
- Wrong filename: `andy_assisted_gcp_complete.json`
- Fixed: Renamed to `demo_andy_assisted_gcp_complete.json`

### 2. Type Mismatches (Second Issue - This Fix)
Profile had wrong data types for CareRecommendation fields:

| Field | Expected Type | Andy Had | Status |
|-------|--------------|----------|--------|
| `flags` | `list[dict]` | `dict` | ❌ Fixed |
| `tier_rankings` | `list[tuple]` | `dict` | ❌ Fixed |
| `rationale` | `list[str]` | `str` | ❌ Fixed |
| `next_step` | `dict[str,str]` | `str` | ❌ Fixed |
| `generated_at` | `str` | Missing | ❌ Fixed |
| `version` | `str` | Missing | ❌ Fixed |
| `input_snapshot_id` | `str` | Missing | ❌ Fixed |
| `rule_set` | `str` | Missing | ❌ Fixed |
| `last_updated` | `str` | Missing | ❌ Fixed |
| `needs_refresh` | `bool` | Missing | ❌ Fixed |

## Solution Applied

### Updated create_demo_andy.py

1. **Added datetime import**:
   ```python
   from datetime import datetime
   ```

2. **Fixed flags structure** (dict → list[dict]):
   ```python
   # WRONG
   "flags": {
       "veteran_aanda_risk": True,
       "no_support": True
   }
   
   # CORRECT
   "flags": [
       {
           "id": "veteran_aanda_risk",
           "label": "VA A&A Eligible",
           "description": "May qualify for VA Aid & Attendance benefits",
           "tone": "success",
           "priority": 1,
           "cta": {
               "label": "Check VA Benefits",
               "route": "learning",
               "filter": "va_benefits"
           }
       }
   ]
   ```

3. **Fixed tier_rankings** (dict → list[list]):
   ```python
   # WRONG
   "tier_rankings": {
       "assisted_living": 18,
       "memory_care": 12
   }
   
   # CORRECT
   "tier_rankings": [
       ["memory_care_high_acuity", 70.0],
       ["memory_care", 32.0],
       ["assisted_living", 18.0],
       ["in_home", 12.5],
       ["no_care_needed", 4.0]
   ]
   ```

4. **Added all missing required fields**:
   ```python
   "generated_at": datetime.now().isoformat(),
   "version": "4.0",
   "input_snapshot_id": f"andy_gcp_{int(TIMESTAMP)}",
   "rule_set": "gcp_v4_standard",
   "last_updated": datetime.now().isoformat(),
   "needs_refresh": False
   ```

### Regenerated Profile

- **File**: `data/users/demo/demo_andy_assisted_gcp_complete.json`
- **Size**: 5.7 KB (was 4.7 KB)
- **Lines**: 218 (was 178)
- **All fields**: ✅ Present with correct types

## Verification

```bash
# Check all required fields are present
jq '.mcip_contracts.care_recommendation | keys' demo_andy_assisted_gcp_complete.json

# Result:
[
  "confidence",        ✅
  "flags",             ✅ (now list, 3 items)
  "generated_at",      ✅ (added)
  "input_snapshot_id", ✅ (added)
  "last_updated",      ✅ (added)
  "needs_refresh",     ✅ (added)
  "next_step",         ✅ (now dict)
  "rationale",         ✅ (now list)
  "rule_set",          ✅ (added)
  "status",            ✅
  "tier",              ✅
  "tier_rankings",     ✅ (now list)
  "tier_score",        ✅
  "version"            ✅ (added)
]
```

## Files Modified

1. **create_demo_andy.py**
   - Added `datetime` import
   - Fixed `mcip_contracts.care_recommendation` structure
   - Fixed output display to handle list of flags

2. **data/users/demo/demo_andy_assisted_gcp_complete.json**
   - Regenerated with correct structure
   - All 14 required CareRecommendation fields
   - All correct data types

## Testing Steps

1. **Clear working copy**:
   ```bash
   rm -f data/users/demo_andy_assisted_gcp_complete.json
   ```

2. **Login as Andy**:
   - Should load without TypeError ✅
   - Should redirect to Concierge Hub ✅

3. **Verify GCP tile**:
   - Shows "✅ Assisted Living (73% confidence)" ✅
   - Marked as complete ✅

4. **Verify flags**:
   - VA A&A Eligible flag visible ✅
   - Limited Support System flag visible ✅
   - Safety Concerns flag visible ✅

## Success Criteria

✅ Filename matches UID pattern  
✅ All 14 CareRecommendation fields present  
✅ All fields have correct types  
✅ No FinancialProfile (Andy hasn't done Cost Planner)  
✅ No TypeError on profile load  
✅ GCP shows as complete  
✅ Cost Planner shows as unlocked (not complete)  
✅ Flags display correctly  

---

**Andy's Journey**: GCP Complete → Cost Planner Unlocked (not started)  
**Status**: ✅ Complete - Ready to test  
**Date**: October 19, 2025
