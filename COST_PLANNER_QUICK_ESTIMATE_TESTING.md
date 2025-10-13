# Cost Planner Quick Estimate Testing Guide

## Overview
This guide covers testing the new Cost Planner Quick Estimate flow with authentication gate and flag collection.

**Phase Implemented:** Introduction → Quick Estimate → Auth Gate → Profile Flags → Module Dashboard

---

## Implementation Summary

### New Files Created
1. **`products/cost_planner/cost_estimate.py`** (230 lines)
   - Cost calculation engine with national averages
   - Care type mapping from GCP recommendations
   - Flag-based cost modifiers (fall risk, cognitive risk, medication complexity, etc.)
   - Cost breakdown rendering utilities

2. **`products/cost_planner/dev_unlock.py`** (60 lines)
   - Development utility to enable Cost Planner tile visibility
   - Sidebar controls for lock/unlock during testing
   - Mimics MCIP flag approval system

### Modified Files
1. **`products/cost_planner/base_module_config.json`**
   - Added `quick_estimate` step with care type radio selector
   - Added `auth_gate` step with authentication requirement
   - Added `profile_flags` step for veteran/homeowner/medicaid status
   - Removed deprecated `path_selection` step

2. **`products/cost_planner/product.py`**
   - Added custom rendering for `quick_estimate` step
   - Integrated cost estimation engine
   - Added authentication gate rendering
   - Added module dashboard rendering with conditional module display

3. **`app.py`**
   - Imported dev unlock utility
   - Added `show_dev_controls()` call to display sidebar lock/unlock button

---

## Testing Instructions

### Step 1: Enable Cost Planner for Testing

1. **Open the app:** http://localhost:8501
2. **Look for sidebar controls** (bottom of sidebar):
   ```
   🛠️ Development Controls
   🔒 Cost Planner: Locked
   [🔓 Unlock Cost Planner]
   ```
3. **Click "🔓 Unlock Cost Planner"**
4. **Verify status changes to:**
   ```
   ✅ Cost Planner: Enabled
   [🔒 Lock Cost Planner]
   ```

### Step 2: Navigate to Concierge Hub

1. **Go to:** http://localhost:8501/?page=hub_concierge
2. **Verify Cost Planner tile appears** in Additional Services section
3. **Tile should show:**
   - Title: "Cost Planner"
   - Subtitle: "Estimate monthly costs based on your [recommendation] recommendation."
   - CTA: "Start planning"

### Step 3: Test Quick Estimate Flow

#### 3.1 Introduction Screen
1. **Click "Start planning" on Cost Planner tile**
2. **Verify intro screen loads:**
   - Title: "Cost Planner"
   - Description of what the tool does
   - "Continue" button at bottom

#### 3.2 Quick Estimate Screen
1. **Click "Continue" from intro**
2. **Verify Quick Estimate screen loads with:**
   - Title: "Your Care Recommendation & Quick Estimate"
   - Radio buttons for 5 care types:
     - No Care Needed
     - In-Home Care
     - Assisted Living
     - Memory Care
     - Memory Care (High Acuity)
   - Cost breakdown section below radio buttons

3. **Test care type selection:**
   - **Select "No Care Needed"**
     - Base cost: $0
     - No modifiers (unless isolation_risk or emotional_support_risk flags set)
     - Total: $0
   
   - **Select "In-Home Care"**
     - Base cost: $4,500
     - Modifiers appear if flags active (fall_risk, cognitive_risk, etc.)
     - Total: $4,500 + modifiers
   
   - **Select "Memory Care"**
     - Base cost: $7,500
     - Multiple modifiers likely (cognitive_risk, meds_management, etc.)
     - Total: $7,500 + modifiers
   
   - **Select "Memory Care (High Acuity)"**
     - Base cost: $10,500
     - Highest modifier total
     - Total: $10,500 + modifiers

4. **Verify cost breakdown displays:**
   - Base monthly cost
   - List of applicable modifiers with reasons
   - Modifier amounts and percentages
   - Total estimated monthly cost
   - Disclaimer about regional variation

### Step 4: Test GCP Integration

#### 4.1 Complete Guided Care Plan First
1. **Navigate to GCP:** http://localhost:8501/?page=gcp
2. **Complete assessment** to get a care recommendation
3. **Verify handoff data includes:**
   - `recommendation` (e.g., "Memory Care")
   - `flags` (e.g., `cognitive_risk`, `fall_risk`, `meds_management_needed`)

#### 4.2 Return to Cost Planner
1. **Navigate to Cost Planner:** http://localhost:8501/?page=cost
2. **Progress to Quick Estimate step**
3. **Verify GCP recommendation appears:**
   - Info box: "💡 **Your Guided Care Plan Recommendation:** [recommendation]"
   - Radio selector pre-selected to matching care type
   - Cost estimate automatically calculated with GCP flags applied

#### 4.3 Test Flag-Based Modifiers
1. **With GCP completed, check which flags are active:**
   - Cognitive risk → +20% adjustment
   - Fall risk → +15% adjustment
   - Medication complexity → +10% adjustment
   - Mobility impaired → +12% adjustment
   - Isolation risk → +5% adjustment
   - Emotional support → +8% adjustment

2. **Verify modifiers appear in cost breakdown**
3. **Change care type** and verify modifiers recalculate correctly

### Step 5: Test Authentication Gate

1. **From Quick Estimate, click "Continue to Full Assessment"**
2. **Verify auth gate screen loads:**
   - Title: "Sign In for Full Assessment"
   - Description of what's included in Full Assessment
   - Authentication requirement message
   - Two buttons: "Sign In (Dev)" and "Create Account (Dev)"

3. **Verify authentication state:**
   - If NOT authenticated: Warning displayed, buttons enabled
   - If authenticated: Success message, can proceed

4. **Test mock authentication:**
   - Click "Sign In (Dev)" button
   - Page should reload
   - Auth gate should now show: "✅ You're signed in! Click Continue to proceed."

### Step 6: Test Profile Flags Collection

1. **Click "Continue" from authenticated auth gate**
2. **Verify profile flags screen loads:**
   - Title: "A Few Quick Questions"
   - Three radio fields:
     - "Is the care recipient a military veteran?" (Yes/No)
     - "Does the care recipient own their home?" (Yes/No)
     - "Is the care recipient currently receiving Medicaid benefits?" (Yes/No/Not sure)

3. **Test different flag combinations:**
   - **Veteran = Yes** → Should enable VA Benefits module in dashboard
   - **Home Owner = Yes** → Should enable Home Decisions module
   - **Medicaid = Yes** → Should enable Medicaid Navigator

### Step 7: Test Module Dashboard

1. **Complete profile flags and click "Continue"**
2. **Verify module dashboard loads:**
   - Title: "Financial Assessment Modules"
   - Description about completing modules
   - Conditional messages based on profile flags:
     - "✅ VA Benefits module enabled" (if veteran)
     - "✅ Home Decisions module enabled" (if homeowner)
     - "✅ Medicaid Navigator enabled" (if medicaid)
   - Warning: "🚧 Module tiles coming in Phase 2"

---

## Expected Behavior

### Cost Calculation Accuracy

| Care Type | Base Cost | Common Modifiers | Example Total |
|-----------|-----------|------------------|---------------|
| No Care Needed | $0 | None | $0 |
| In-Home Care | $4,500 | Fall risk (+15%), Meds (+10%) | $5,625 |
| Assisted Living | $5,500 | Fall risk (+15%), Cognitive (+20%) | $7,425 |
| Memory Care | $7,500 | Cognitive (+20%), Meds (+10%), Fall (+15%) | $10,875 |
| Memory Care (High) | $10,500 | All flags (~50-60% total) | $15,750+ |

### Flag-to-Modifier Mapping

| Flag | Adjustment | Reason | Applies To |
|------|------------|--------|------------|
| `fall_risk` | +15% | Fall prevention monitoring | In-home, AL, MC, MC-High |
| `cognitive_risk` | +20% | Specialized cognitive care | In-home, AL, MC, MC-High |
| `meds_management_needed` | +10% | Medication management | In-home, AL, MC, MC-High |
| `isolation_risk` | +5% | Companionship services | In-home, No care |
| `mobility_impaired` | +12% | Mobility assistance | In-home, AL, MC, MC-High |
| `emotional_support_risk` | +8% | Wellness counseling | In-home, No care |

### Authentication Flow

```
Quick Estimate (PUBLIC)
    ↓
Auth Gate (BLOCKS if not authenticated)
    ↓
Profile Flags (REQUIRES authentication)
    ↓
Module Dashboard (REQUIRES authentication)
```

---

## Known Limitations (Expected for This Phase)

1. **Module tiles not implemented yet**
   - Dashboard shows placeholder message
   - Actual module tiles coming in Phase 2

2. **No sub-module navigation**
   - Cannot navigate to income, assets, etc.
   - Coming in Phase 2

3. **Mock authentication only**
   - Real auth integration planned for later phase
   - Dev controls visible in sidebar

4. **Cost estimates are national averages**
   - No regional pricing yet
   - No provider-specific pricing
   - Future enhancement

5. **No progress tracking to MCIP**
   - Product-level progress calculation not yet implemented
   - Coming when sub-modules are built

---

## Test Scenarios

### Scenario 1: New User (No GCP Data)
- **Expected:** Default to "No Care Needed" selection
- **Expected:** No GCP recommendation banner
- **Expected:** Minimal/no cost modifiers

### Scenario 2: User with GCP Assessment (Low Need)
- **GCP Result:** "Independent / In-Home"
- **Expected:** Quick Estimate defaults to "No Care Needed"
- **Expected:** Few/no flags, low modifier total
- **Expected:** Smooth progression through auth gate

### Scenario 3: User with GCP Assessment (High Need)
- **GCP Result:** "Memory Care" or "High-Acuity Memory Care"
- **Expected:** Quick Estimate defaults to matching care type
- **Expected:** Multiple flags active (cognitive, fall, meds, etc.)
- **Expected:** Cost estimate shows significant modifiers
- **Expected:** Auth gate → Profile flags → Dashboard with conditional modules

### Scenario 4: Testing Care Type Comparison
- **Action:** Select each care type in sequence
- **Expected:** Cost updates in real-time
- **Expected:** Modifier list changes based on care type
- **Expected:** Base cost increases with care intensity

### Scenario 5: Testing Profile Flags Impact
- **Action:** Answer "Yes" to all three profile questions
- **Expected:** All three conditional modules enabled in dashboard
- **Action:** Answer "No" to all three
- **Expected:** Only core modules available (income, assets, insurance)

---

## Debugging Tips

### Cost Calculation Issues
1. **Check session state flags:**
   ```python
   import streamlit as st
   st.write(st.session_state.get("handoff", {}).get("gcp", {}).get("flags", {}))
   ```

2. **Verify care type mapping:**
   - Check `TIER_TO_CARE_TYPE` in `cost_estimate.py`
   - Ensure GCP recommendation matches expected tier

3. **Inspect cost breakdown:**
   - Modifiers should only apply to relevant care types
   - Total adjustment % should match sum of individual modifiers

### Authentication Issues
1. **Check auth state:**
   ```python
   st.write(st.session_state.get("auth", {}))
   ```

2. **Verify auth gate logic:**
   - Should block if `is_authenticated = False`
   - Should allow if `is_authenticated = True`

### Flag Collection Issues
1. **Check profile flag answers:**
   ```python
   st.write(st.session_state.get("cost.base", {}).get("answers", {}))
   ```

2. **Verify conditional module display:**
   - Veteran flag → VA Benefits message
   - Homeowner flag → Home Decisions message
   - Medicaid flag → Medicaid Navigator message

---

## Success Criteria

✅ **Cost Planner tile appears when unlocked**  
✅ **Introduction screen loads cleanly**  
✅ **Quick Estimate displays all 5 care types**  
✅ **Cost calculations are mathematically correct**  
✅ **Modifiers apply only to appropriate care types**  
✅ **GCP recommendation pre-selects correct care type**  
✅ **GCP flags correctly modify cost estimates**  
✅ **Auth gate blocks unauthenticated users**  
✅ **Mock authentication works correctly**  
✅ **Profile flags collect three Boolean values**  
✅ **Module dashboard shows conditional modules**  
✅ **No console errors during flow**  
✅ **Session state persists across page reloads**

---

## Next Steps (Phase 2)

After validating this phase:
1. **Build first sub-module:** Income Sources
2. **Implement module tiles** in dashboard
3. **Add sub-module navigation** routing
4. **Build aggregation logic** for product-level progress
5. **Integrate with MCIP** for progress tracking
6. **Add remaining sub-modules:** Assets, VA Benefits, Home Decisions, Insurance

---

## Contact / Questions

If you encounter unexpected behavior or have questions about the implementation, refer to:
- `COST_PLANNER_ARCHITECTURE.md` - Overall design
- `NEW_PRODUCT_QUICKSTART.md` - Module creation guide
- `EXTENSIBILITY_AUDIT.md` - Architecture patterns
