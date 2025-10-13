# Cost Planner Quick Estimate - Activation Summary

## What Was Implemented

### Complete Introduction → Quick Estimate → Auth Gate → Profile Flags Flow

This implementation delivers the **Quick Estimate** phase of Cost Planner, allowing users to:
1. See their GCP care recommendation
2. Compare costs for different care types
3. View cost modifiers based on health/safety flags
4. Transition to Full Assessment (with authentication)
5. Provide profile information (veteran, homeowner, medicaid status)

---

## Files Created (3 new files)

### 1. `products/cost_planner/cost_estimate.py` (230 lines)
**Purpose:** Cost calculation engine

**Features:**
- National average base costs for 5 care types
- GCP recommendation → care type mapping
- 6 flag-based cost modifiers (fall risk, cognitive risk, medication, etc.)
- Cost breakdown rendering utilities
- Currency formatting helpers

**Key Functions:**
- `calculate_cost_estimate(care_type, flags)` → Returns cost breakdown
- `get_gcp_recommendation()` → Pulls GCP data from handoff
- `get_gcp_flags()` → Pulls flags from handoff
- `render_cost_breakdown(estimate)` → Displays formatted cost in UI

---

### 2. `products/cost_planner/dev_unlock.py` (60 lines)
**Purpose:** Development utility for testing

**Features:**
- Enable/disable Cost Planner tile visibility
- Sidebar controls for lock/unlock
- Mimics MCIP flag approval system

**Key Functions:**
- `enable_cost_planner_for_testing()` → Sets `cost_planner_enabled` flag
- `disable_cost_planner()` → Removes flag
- `show_dev_controls()` → Renders sidebar toggle button

**Usage:**
Called in `app.py` to show sidebar controls during development. Allows testing Cost Planner tile appearance without completing GCP or modifying production logic.

---

### 3. `COST_PLANNER_QUICK_ESTIMATE_TESTING.md` (450 lines)
**Purpose:** Comprehensive testing guide

**Sections:**
- Step-by-step testing instructions
- Expected cost calculations by care type
- Flag-to-modifier mapping table
- Authentication flow diagram
- Test scenarios (5 scenarios)
- Debugging tips
- Success criteria checklist

---

## Files Modified (3 files)

### 1. `products/cost_planner/base_module_config.json`
**Changes:**
- Removed: `path_selection` step (deprecated)
- Added: `quick_estimate` step with care type radio selector
- Added: `auth_gate` step with authentication requirement
- Added: `profile_flags` step with veteran/homeowner/medicaid questions
- Updated: `intro` subtitle with clearer value proposition

**New Flow:**
```
intro → quick_estimate → auth_gate → profile_flags → module_dashboard
```

---

### 2. `products/cost_planner/product.py`
**Changes:**
- Added import for cost estimation utilities
- Added `_render_quick_estimate()` function → Shows cost breakdown
- Added `_render_auth_gate()` function → Blocks unauthenticated users
- Added `_render_module_dashboard()` function → Shows conditional modules
- Updated `_render_base_module()` to dispatch to custom renderers

**New Logic:**
- Quick Estimate auto-selects care type from GCP recommendation
- Auth gate displays login buttons and success message
- Module dashboard shows/hides modules based on profile flags

---

### 3. `app.py`
**Changes:**
- Added import: `from products.cost_planner.dev_unlock import show_dev_controls`
- Added call: `show_dev_controls()` in main flow

**Effect:**
Sidebar now shows Cost Planner lock/unlock toggle for development testing.

---

## How to Activate for Testing

---

## How to Activate for Testing

### Option 1: Use Sidebar Controls (Recommended)
1. Open app: http://localhost:8501
2. Look for "🛠️ Development Controls" in sidebar
3. Click "🔓 Unlock Cost Planner"
4. Navigate to Concierge hub
5. Cost Planner tile will appear in Additional Services

### Option 2: Programmatic (Python/Terminal)
```python
import streamlit as st
from products.cost_planner.dev_unlock import enable_cost_planner_for_testing

# Run this after starting Streamlit
enable_cost_planner_for_testing()
st.rerun()
```

### Option 3: Direct Session State (Console/Debugger)
```python
st.session_state.setdefault("handoff", {})
st.session_state["handoff"].setdefault("gcp", {})
st.session_state["handoff"]["gcp"].setdefault("flags", {})
st.session_state["handoff"]["gcp"]["flags"]["cost_planner_enabled"] = True
```

---

## Testing Quick Reference

### 1. Unlock Cost Planner
- Sidebar → "🔓 Unlock Cost Planner"
- Status changes to "✅ Cost Planner: Enabled"

### 2. Navigate to Concierge Hub
- URL: `http://localhost:8501/?page=hub_concierge`
- Verify Cost Planner tile appears

### 3. Click "Start planning"
- Intro screen loads
- Click "Continue"

### 4. Test Care Type Selection
- Select each care type (5 options)
- Verify cost updates in real-time
- Verify modifiers appear/disappear based on care type

### 5. Test with GCP Data
- Complete GCP assessment first
- Return to Cost Planner
- Verify GCP recommendation pre-selects care type
- Verify flags from GCP apply cost modifiers

### 6. Test Authentication Gate
- Click "Continue to Full Assessment"
- Verify auth gate blocks progress
- Click "Sign In (Dev)"
- Verify success message appears

### 7. Test Profile Flags
- Answer three questions (veteran, homeowner, medicaid)
- Click "Continue"
- Verify conditional module messages in dashboard

---

## Cost Calculation Examples

### Example 1: No Care Needed (Healthy Senior)
```
Base Cost: $0
Modifiers: None (unless isolation_risk flag set)
Total: $0
```

### Example 2: In-Home Care (Moderate Needs)
```
Base Cost: $4,500
Modifiers:
  + Fall risk (+15%): $675
  + Medication complexity (+10%): $450
Total: $5,625/month
```

### Example 3: Memory Care (High Needs)
```
Base Cost: $7,500
Modifiers:
  + Cognitive risk (+20%): $1,500
  + Fall risk (+15%): $1,125
  + Medication complexity (+10%): $750
  + Mobility impaired (+12%): $900
Total: $11,775/month
```

### Example 4: Memory Care High Acuity (Complex Case)
```
Base Cost: $10,500
Modifiers:
  + Cognitive risk (+20%): $2,100
  + Fall risk (+15%): $1,575
  + Medication complexity (+10%): $1,050
  + Mobility impaired (+12%): $1,260
Total: $16,485/month
```

---

## Flag-Based Modifiers Reference

| Flag Name | Adjustment | Reason | Applies To |
|-----------|------------|--------|------------|
| `fall_risk` | +15% | Fall prevention monitoring | In-home, AL, MC, MC-High |
| `cognitive_risk` | +20% | Specialized cognitive care | In-home, AL, MC, MC-High |
| `meds_management_needed` | +10% | Medication management | In-home, AL, MC, MC-High |
| `isolation_risk` | +5% | Companionship services | In-home, No care |
| `mobility_impaired` | +12% | Mobility assistance | In-home, AL, MC, MC-High |
| `emotional_support_risk` | +8% | Wellness counseling | In-home, No care |

**Note:** Multiple modifiers stack additively. A senior with cognitive risk, fall risk, and medication complexity would see a +45% total adjustment.

---

## Integration with GCP

### How GCP Data Flows to Cost Planner

1. **User completes GCP assessment**
   - GCP calculates care recommendation (e.g., "Memory Care")
   - GCP identifies health/safety flags (e.g., `cognitive_risk`, `fall_risk`)
   - GCP writes to `st.session_state["handoff"]["gcp"]`

2. **User opens Cost Planner**
   - Cost Planner reads `handoff.gcp.recommendation`
   - Maps recommendation to care type (e.g., "Memory Care" → `memory_care`)
   - Pre-selects matching care type in Quick Estimate radio selector

3. **Cost calculation applies flags**
   - Cost Planner reads `handoff.gcp.flags`
   - Identifies applicable modifiers for selected care type
   - Calculates adjusted cost and displays breakdown

**Example Handoff Structure:**
```python
st.session_state["handoff"]["gcp"] = {
    "recommendation": "Memory Care",
    "tier": 3,
    "flags": {
        "cognitive_risk": True,
        "fall_risk": True,
        "meds_management_needed": True,
        "cost_planner_enabled": True  # ← Enables tile visibility
    }
}
```

---

## Success Checklist

Run through this checklist to verify the implementation:

- [ ] Sidebar shows "🔓 Unlock Cost Planner" button
- [ ] Clicking unlock sets status to "Enabled"
- [ ] Cost Planner tile appears in Concierge hub
- [ ] Intro screen loads cleanly
- [ ] Quick Estimate shows 5 care type options
- [ ] Selecting care type updates cost in real-time
- [ ] Cost breakdown shows base + modifiers + total
- [ ] GCP recommendation pre-selects correct care type
- [ ] GCP flags apply correct modifiers
- [ ] Auth gate blocks unauthenticated users
- [ ] Mock login button works
- [ ] Profile flags collect three Boolean values
- [ ] Module dashboard shows conditional modules
- [ ] No console errors in browser
- [ ] Session state persists across reloads

---

## Questions?

Refer to:
- **Testing Guide:** `COST_PLANNER_QUICK_ESTIMATE_TESTING.md`
- **Architecture:** `COST_PLANNER_ARCHITECTURE.md`
- **Module Guide:** `NEW_PRODUCT_QUICKSTART.md`
- **Extensibility:** `EXTENSIBILITY_AUDIT.md`

### Option 2: Enable for Specific Users (Beta Testing)

Add the flag to specific user sessions in `core/state.py` or during hub rendering:

```python
# In ensure_session() or user onboarding logic
if user_is_in_beta_group():
    st.session_state.setdefault("handoff", {}).setdefault("flags", {})
    st.session_state["handoff"]["flags"]["cost_planner_enabled"] = True
```

### Option 3: Enable via Feature Flag System (Future)

When you implement a feature flag system:

```python
from core.feature_flags import is_enabled

if is_enabled("cost_planner"):
    # Show tile
    pass
```

---

## Testing the Change

### After Enabling:

1. **Clear Session State:**
   ```python
   # In Streamlit app
   st.cache_data.clear()
   st.cache_resource.clear()
   # Or restart the app
   ```

2. **Complete GCP:**
   - Navigate to Concierge Hub
   - Complete Guided Care Plan (100%)
   - Return to Concierge Hub

3. **Verify Tile Appears:**
   - Look for "Cost Planner" tile in Additional Services section
   - Should show after GCP tile
   - Subtitle should reference your care recommendation

4. **Click Through:**
   - Click "Start planning"
   - Verify it navigates to `/product/cost`
   - Check for any errors in console

---

## Why It's Hidden

The Cost Planner product logic is implemented but requires:
- ✅ **VA Benefits module** - Currently returns placeholder data
- ✅ **Quick Estimate module** - Currently returns placeholder data
- ⏳ **MCIP approval** - Waiting for medical partner sign-off
- ⏳ **Cost calculation validation** - Verify accuracy with real data
- ⏳ **Regional customization** - Adjust for geographic cost variations

---

## Monitoring After Activation

### Week 1 Metrics:
- [ ] Track Cost Planner start rate
- [ ] Monitor completion rate
- [ ] Check for error rates
- [ ] Gather user feedback

### Analytics to Watch:
```python
# Track in core/events.py
log_event("cost_planner.started", {"from": "additional_services"})
log_event("cost_planner.completed", {"total_cost": cost})
log_event("cost_planner.abandoned", {"step": current_step})
```

---

## Rollback Plan

If issues arise after activation:

### Quick Disable:
```python
# In core/additional_services.py
"visible_when": [
    {"includes": {"path": "flags", "value": "cost_planner_disabled_emergency"}},
],
```

This will hide it immediately (default false = hidden).

### Full Revert:
```bash
git revert <commit-hash>
git push origin main
```

---

## Contact

**Questions about activation?**
- Product Owner: _____________
- Technical Lead: Shane
- MCIP Contact: _____________

**Ready to activate?**
1. Get MCIP sign-off
2. Update this document with approval details
3. Follow "How to Enable" steps above
4. Monitor metrics for 48 hours

---

## Sign-Off

**MCIP Approval:** _____________  
**Date:** _____________  
**Activation By:** _____________  
**Date Activated:** _____________  

**Status After Activation:**
- [ ] Tile visible in Concierge Hub
- [ ] Analytics tracking confirmed
- [ ] Error monitoring in place
- [ ] Rollback plan tested

---

*Last Updated: October 12, 2025*
