# Cost Planner Regional Pricing & GCP Integration - Testing Guide

## What's New

### 1. Regional Pricing System
- **ZIP-based cost adjustments** using comprehensive lookup tables
- **Priority resolution**: WA-specific → National → State → Default
- **190+ ZIP codes** with custom multipliers
- **14 WA ZIP3 regions** covering all 980-994 prefixes
- **All 50 states** with custom multipliers

### 2. GCP Recommendation Integration
- **Contextual messaging** throughout Cost Planner flow
- **Dynamic subtitle** on Quick Estimate screen references GCP recommendation
- **Pre-selection** of recommended care type
- **Comparison guidance** for exploring alternatives

### 3. Updated Flow
```
Intro → Quick Estimate (national avg) → Auth Gate → Profile Flags (+ ZIP) → Dashboard (regional pricing)
```

---

## Files Created/Modified

### New Files
1. **`config/regional_cost_config.json`** (8,500+ lines)
   - Comprehensive regional pricing database
   - WA-specific overrides for Seattle, Bellevue, Tacoma, Spokane, etc.
   - National ZIP/ZIP3/state multipliers
   - Resolution rules and calculation examples

2. **`products/cost_planner/cost_estimate_v2.py`** (380 lines)
   - Regional multiplier resolution engine
   - GCP recommendation integration helpers
   - Updated cost calculation with regional + flag modifiers
   - Enhanced rendering with regional breakdown

### Modified Files
1. **`products/cost_planner/base_module_config.json`**
   - Updated `quick_estimate` step title/subtitle for GCP context
   - Moved `zip_code` field to `profile_flags` step
   - Fixed care type values to match config (`in_home_care` vs `in_home`)

2. **`products/cost_planner/product.py`**
   - Import from `cost_estimate_v2` instead of `cost_estimate`
   - Enhanced `_render_quick_estimate()` with GCP messaging
   - Enhanced `_render_module_dashboard()` with regional pricing display
   - Added ZIP code context throughout

---

## Testing Instructions

### Phase 1: Enable Cost Planner

1. **Open app:** http://localhost:8501
2. **Unlock Cost Planner:**
   - Sidebar → "🛠️ Development Controls"
   - Click "🔓 Unlock Cost Planner"
   - Verify status: "✅ Cost Planner: Enabled"

### Phase 2: Test Without GCP (Baseline)

#### 2.1 Navigate to Cost Planner
1. Go to Concierge hub: http://localhost:8501/?page=hub_concierge
2. Click Cost Planner tile "Start planning"
3. Click "Continue" on intro screen

#### 2.2 Quick Estimate (No GCP Data)
1. **Verify messaging:**
   - Should see: "💡 **Start by selecting a care type below** to see estimated monthly costs..."
   - Should NOT see GCP recommendation banner
   - Should see note about ZIP code for later

2. **Test care type selection:**
   - Default selection: "No Care Needed"
   - Cost breakdown shows national average only
   - No regional adjustment line item

3. **Test each care type:**
   - No Care Needed → $0
   - In-Home Care → $5,200 base
   - Assisted Living → $5,500 base
   - Memory Care → $7,200 base
   - Memory Care (High Acuity) → $9,000 base

4. **Click "Continue to Full Assessment"**

#### 2.3 Auth Gate
1. Verify auth requirement message
2. Click "Sign In (Dev)"
3. Verify success message

#### 2.4 Profile Flags (With ZIP)
1. **Enter test ZIP codes:**
   - **98101** (Seattle downtown - should be +15%)
   - **10001** (Manhattan - should be +40%)
   - **12345** (unknown - should be default 0%)

2. **Answer other questions:**
   - Veteran: Yes
   - Home owner: Yes
   - Medicaid: No

3. **Click "Continue"**

#### 2.5 Module Dashboard
1. **Verify regional pricing display:**
   - Should show: "📍 **Regional Pricing for ZIP 98101:** +15% adjustment (WA ZIP exact)"
   - Message should explain all estimates include regional adjustment

2. **Verify conditional modules:**
   - ✅ VA Benefits (veteran = yes)
   - ✅ Home Decisions (homeowner = yes)
   - No Medicaid Navigator (medicaid = no)

### Phase 3: Test With GCP Recommendation

#### 3.1 Complete GCP First
1. Navigate to GCP: http://localhost:8501/?page=gcp
2. Complete assessment to get a recommendation
3. **Recommended scenario:**
   - Memory changes: Moderate
   - Falls: Multiple times per month
   - Help overall: Moderate
   - Result: Should recommend "Memory Care" or "Assisted Living"

#### 3.2 Open Cost Planner from GCP
1. On GCP results page, look for Cost Planner tile
2. Click "Start planning"
3. Proceed through intro

#### 3.3 Quick Estimate (With GCP)
1. **Verify GCP context messaging:**
   - Should see: "💡 **Based on your Guided Care Plan assessment, we recommend: [RECOMMENDATION]**"
   - Message should explain: "The estimate below reflects this recommendation..."
   - Radio selector should be pre-selected to matching care type

2. **Test with Memory Care recommendation:**
   - Pre-selected: "Memory Care"
   - Base cost: $7,200
   - Modifiers from GCP flags (cognitive_risk, fall_risk, etc.)
   - Total should be $7,200 + flag adjustments

3. **Test changing care type:**
   - Select "Assisted Living" instead
   - Cost updates to $5,500 + different flag adjustments
   - Can compare options easily

#### 3.4 Complete Flow with ZIP
1. Auth gate → Sign in
2. Profile flags:
   - **ZIP: 98101** (Seattle)
   - Veteran: No
   - Home owner: Yes
   - Medicaid: No

3. **Dashboard should show:**
   - Regional adjustment: +15% for Seattle
   - Home Decisions enabled
   - NO VA Benefits (not veteran)
   - NO Medicaid Navigator

### Phase 4: Regional Pricing Validation

Test these ZIP codes to verify regional multipliers:

#### Washington State ZIPs
| ZIP | Expected Multiplier | Expected Match | Notes |
|-----|---------------------|----------------|-------|
| 98101 | +15% | WA ZIP exact | Seattle downtown |
| 98103 | +14% | WA ZIP exact | Seattle Green Lake |
| 98004 | +14% | WA ZIP exact | Bellevue |
| 98052 | +12% | WA ZIP exact | Redmond |
| 99201 | -1% | WA ZIP exact | Spokane |
| 98765 | +12% | WA ZIP3 (987) | Fallback to ZIP3 |
| 98999 | +5% | WA ZIP3 (989) | Yakima region |

#### National ZIPs
| ZIP | Expected Multiplier | Expected Match | Notes |
|-----|---------------------|----------------|-------|
| 10001 | +40% | ZIP exact | Manhattan |
| 94103 | +35% | ZIP exact | San Francisco |
| 60601 | +20% | ZIP exact | Chicago Loop |
| 73301 | +12% | ZIP exact | Austin |
| 35203 | -10% | ZIP exact | Birmingham, AL |
| 12345 | +20% | State (NY) | NY state fallback |
| 99999 | 0% | Default | Unknown ZIP |

#### Test Procedure for Each ZIP
1. Navigate to profile_flags step
2. Enter ZIP code
3. Click Continue to dashboard
4. **Verify regional pricing banner:**
   - Correct percentage adjustment
   - Correct match type explanation
5. **Return to Quick Estimate (refresh app):**
   - Verify cost breakdown shows regional adjustment
   - Verify regional subtotal = base * multiplier

### Phase 5: End-to-End Scenario Testing

#### Scenario 1: Seattle Senior with Memory Care Needs
**Setup:**
- Complete GCP → Get "Memory Care" recommendation
- GCP flags: cognitive_risk, fall_risk, meds_management

**Cost Planner Flow:**
1. Quick Estimate:
   - Pre-selected: Memory Care
   - Base: $7,200 (national)
   - No regional yet
   - Flags: +20% (cognitive) +15% (fall) +10% (meds) = +45%
   - Total: $10,440

2. Profile Flags:
   - ZIP: 98101 (Seattle +15%)
   - Veteran: Yes
   - Home: Yes
   - Medicaid: No

3. Dashboard:
   - Regional banner: "+15% for Seattle"
   - Updated calculation:
     - Base: $7,200
     - Regional: $8,280 ($7,200 * 1.15)
     - Flags: $3,726 ($8,280 * 0.45)
     - **Total: $12,006/month**

#### Scenario 2: Rural WA Senior with In-Home Care
**Setup:**
- Complete GCP → Get "In-Home Care" recommendation
- GCP flags: mobility_impaired

**Cost Planner Flow:**
1. Quick Estimate:
   - Pre-selected: In-Home Care
   - Base: $5,200
   - Flags: +12% (mobility)
   - Total: $5,824

2. Profile Flags:
   - ZIP: 99352 (Richland -3%)
   - Veteran: Yes
   - Home: No
   - Medicaid: Yes

3. Dashboard:
   - Regional: "-3% for Tri-Cities"
   - Updated:
     - Base: $5,200
     - Regional: $5,044 ($5,200 * 0.97)
     - Flags: $605 ($5,044 * 0.12)
     - **Total: $5,649/month**
   - Modules: VA + Medicaid (no Home)

#### Scenario 3: Manhattan Senior with High-Acuity Needs
**Setup:**
- Complete GCP → Get "High-Acuity Memory Care"
- GCP flags: cognitive_risk, fall_risk, meds_management, mobility_impaired

**Cost Planner Flow:**
1. Quick Estimate:
   - Pre-selected: Memory Care (High Acuity)
   - Base: $9,000
   - Flags: +20% +15% +10% +12% = +57%
   - Total: $14,130

2. Profile Flags:
   - ZIP: 10001 (Manhattan +40%)
   - Veteran: No
   - Home: Yes (co-op)
   - Medicaid: No

3. Dashboard:
   - Regional: "+40% for Manhattan"
   - Updated:
     - Base: $9,000
     - Regional: $12,600 ($9,000 * 1.40)
     - Flags: $7,182 ($12,600 * 0.57)
     - **Total: $19,782/month**

---

## Expected Behavior

### GCP Recommendation Context

#### With GCP Completed
- ✅ Info banner: "Based on your Guided Care Plan assessment, we recommend: [RECOMMENDATION]"
- ✅ Care type pre-selected to match GCP
- ✅ Flags from GCP automatically apply modifiers
- ✅ Guidance to compare alternatives

#### Without GCP
- ✅ Info banner: "Start by selecting a care type below..."
- ✅ Suggestion to complete GCP for accurate recommendation
- ✅ Default selection: "No Care Needed"
- ✅ No flags applied

### Regional Pricing Flow

#### Quick Estimate (Pre-Auth)
- Uses **national averages** only
- Note displayed: "We'll ask for ZIP code after authentication..."
- No regional adjustment shown

#### After Profile Flags (Post-Auth)
- Uses **regional pricing** based on ZIP
- Regional adjustment displayed in cost breakdown
- Dashboard shows regional context banner
- All future estimates use regional pricing

### Cost Calculation Accuracy

**Formula:**
```
effective_cost = (base_monthly_usd * regional_multiplier) * (1 + sum(flag_adjustments))
```

**Example (Seattle Memory Care with flags):**
```
base = $7,200
regional_multiplier = 1.15 (Seattle)
regional_cost = $7,200 * 1.15 = $8,280

flag_adjustments = 0.20 + 0.15 + 0.10 = 0.45
flag_modifier_total = $8,280 * 0.45 = $3,726

total_cost = $8,280 + $3,726 = $12,006/month
```

---

## Success Criteria

### GCP Integration
- [ ] Without GCP: Shows generic messaging
- [ ] With GCP: Shows specific recommendation in banner
- [ ] Care type pre-selected matches GCP tier
- [ ] GCP flags apply cost modifiers correctly
- [ ] Can change care type to compare options

### Regional Pricing
- [ ] Quick Estimate uses national averages
- [ ] Profile flags step collects ZIP code
- [ ] Dashboard displays regional adjustment
- [ ] WA ZIPs resolve correctly (exact → ZIP3 → state)
- [ ] National ZIPs resolve correctly
- [ ] Unknown ZIPs default to 1.0 multiplier
- [ ] Cost breakdown shows regional line item

### User Experience
- [ ] Contextual messaging guides user flow
- [ ] GCP recommendation clearly displayed
- [ ] Regional pricing explanation clear
- [ ] Can test multiple ZIP codes
- [ ] Conditional modules display correctly
- [ ] No console errors

---

## Debugging Tips

### Check Regional Multiplier Resolution
```python
from products.cost_planner.cost_estimate_v2 import resolve_regional_multiplier

zip_code = "98101"
multiplier, match_type = resolve_regional_multiplier(zip_code)
print(f"ZIP {zip_code}: {multiplier} ({match_type})")
```

### Check GCP Recommendation
```python
import streamlit as st
handoff = st.session_state.get("handoff", {}).get("gcp", {})
print(f"Recommendation: {handoff.get('recommendation')}")
print(f"Flags: {handoff.get('flags')}")
```

### Verify Cost Calculation
```python
from products.cost_planner.cost_estimate_v2 import calculate_cost_estimate

estimate = calculate_cost_estimate(
    care_type="memory_care",
    zip_code="98101",
    flags={"cognitive_risk": True, "fall_risk": True}
)
print(estimate)
```

---

## Known Limitations

✅ **Expected for this phase:**
- Module tiles not yet implemented (Phase 2)
- ZIP code only collected after auth (by design)
- Regional pricing only applies post-auth
- No state inference from ZIP (uses ZIP3/state tables)

✅ **Future enhancements:**
- Real-time ZIP validation
- Auto-detect state from ZIP
- Provider-specific pricing
- Room type variations

---

## Next Steps

After validating regional pricing + GCP integration:
1. Test all ZIP code scenarios
2. Verify GCP recommendation pre-selection
3. Validate cost calculations across regions
4. Test conditional module display logic
5. Proceed to Phase 2: Build first sub-module (Income Sources)
