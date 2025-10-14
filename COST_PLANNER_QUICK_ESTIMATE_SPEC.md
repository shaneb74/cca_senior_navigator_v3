# Cost Planner - Quick Estimate Page Implementation

**Date:** October 14, 2025  
**Status:** ✅ **IMPLEMENTED**  
**Scope:** Unauthenticated "Get a Quick Cost Estimate" screen only

---

## Executive Summary

Implemented the Cost Planner Quick Estimate page according to comprehensive specification:
- **ZIP only** (removed State field)
- **5 care types only** (removed Independent Living, Skilled Nursing, all legacy types)
- **GCP recommendation seeding** (defaults to recommendation if available)
- **Line-item breakdown** (base cost, regional %, condition add-ons, total)
- **Reassurance copy** + CTA to Full Assessment
- **Scenario switching** (preview different care types without overwriting GCP rec)

---

## Specification Requirements

### ✅ 1. Form Inputs (Unauthenticated)

**ZIP Code:**
- Required field (5 digits)
- Drives regional cost adjustment via precedence: ZIP → ZIP3 → state → default
- Inline validation with clear error messaging

**Care Type Selector:**
- **ONLY 5 allowed values:**
  1. No Care Recommended
  2. In-Home Care
  3. Assisted Living
  4. Memory Care
  5. Memory Care (High Acuity)

**Removed:**
- ❌ State field (eliminated entirely)
- ❌ Independent Living
- ❌ Skilled Nursing
- ❌ Any other legacy tier names

**GCP Recommendation Seeding:**
- When GCP recommendation available → pre-select that care type
- Show caption: "💡 Based on your Guided Care Plan, we've pre-selected: [Type]"
- If no GCP rec → default to "In-Home Care"
- User can switch to preview other scenarios

---

### ✅ 2. Cost Calculation & Display

**Line-Item Breakdown Format:**

```
Base Cost (Care Type):                $X,XXX / month
+ Regional Adjustment (ZIP 9XXXX):     +N%  ($XXX)
+ Cognitive-related Adjustment:        +20% ($XXX)   [if applicable]
+ Mobility-related Adjustment:         +15% ($XXX)   [if applicable]
+ High-Acuity Adjustment:              +25% ($XXX)   [if applicable]
= Adjusted Total:                      $Y,YYY / month
```

**Condition-Based Add-Ons (No Internal Flag Names Exposed):**

| Indicator | Add-On | Detection Logic |
|-----------|--------|-----------------|
| **Cognitive-related** | +20% | `memory_support` flag present in GCP results |
| **Mobility-related** | +15% | `mobility_limited` flag present in GCP results |
| **High-Acuity** | +25% | Care type is "Memory Care (High Acuity)" (always applied) |

**Display Rules:**
- If no add-ons apply → show: "ℹ️ No additional care adjustments applied for your area."
- Only show add-on lines that are actually applied
- Regional adjustment shows percentage and dollar amount

**Scenario Switching:**
- User can change care type dropdown
- Click "Calculate Quick Estimate" again
- Recomputes and re-renders full breakdown
- **Does NOT overwrite** the original GCP recommendation

---

### ✅ 3. Copy & CTA

**Reassurance Copy (Before CTA):**
```
"We know these numbers can feel overwhelming. Don't worry — we'll help you plan how to cover these costs."

Our detailed Financial Assessment will show you:
- ✅ All available funding sources (Medicare, VA benefits, insurance, etc.)
- ✅ Gap analysis: what's covered vs. what you'll pay out-of-pocket
- ✅ Strategies to reduce costs and maximize benefits
- ✅ Facility comparison with real pricing data
```

**Primary CTA:**
```
➡️ Continue to Full Assessment
```
- Triggers authentication flow (if not logged in)
- Transitions to authenticated Financial Assessment modules
- Preserves current care selection and ZIP for context

---

## Implementation Details

### File: `products/cost_planner_v2/intro.py`

**Key Changes:**

1. **Removed State Field:**
   ```python
   # OLD: col1, col2 = st.columns(2) with ZIP and State
   # NEW: Single ZIP input only
   zip_code = st.text_input(
       "ZIP Code",
       max_chars=5,
       placeholder="90210",
       help="Enter your 5-digit ZIP code for regional cost adjustment",
       key="cost_v2_quick_zip"
   )
   ```

2. **5 Care Types Only:**
   ```python
   ALLOWED_CARE_TYPES = [
       "No Care Recommended",
       "In-Home Care",
       "Assisted Living",
       "Memory Care",
       "Memory Care (High Acuity)"
   ]
   ```

3. **GCP Recommendation Seeding:**
   ```python
   default_index = 1  # Default to "In-Home Care"
   gcp_rec = MCIP.get_care_recommendation()
   if gcp_rec and gcp_rec.tier:
       gcp_display = tier_to_display.get(gcp_rec.tier)
       if gcp_display and gcp_display in ALLOWED_CARE_TYPES:
           default_index = ALLOWED_CARE_TYPES.index(gcp_display)
           st.caption(f"💡 Based on your Guided Care Plan...")
   ```

4. **Line-Item Breakdown Rendering:**
   ```python
   # Base cost
   st.markdown(f"**Base Cost ({care_type_display}):** ${base_cost:,.0f} / month")
   
   # Regional adjustment
   if estimate.multiplier != 1.0:
       regional_pct = int((estimate.multiplier - 1.0) * 100)
       regional_amount = breakdown.get("regional_adjustment", 0)
       st.markdown(f"**+ Regional Adjustment (ZIP {zip}):** +{regional_pct}%...")
   
   # Cognitive addon (if present)
   if "cognitive_addon" in breakdown and breakdown["cognitive_addon"] > 0:
       st.markdown(f"**+ Cognitive-related Adjustment:** +20%...")
   
   # ... etc for all add-ons
   
   # Final total
   st.markdown(f"### **= Adjusted Total: ${estimate.monthly_adjusted:,.0f} / month**")
   ```

5. **Reassurance Copy + CTA:**
   ```python
   st.info("""
   **We know these numbers can feel overwhelming. Don't worry — we'll help you plan how to cover these costs.**
   ...
   """)
   
   st.button("➡️ Continue to Full Assessment", ...)
   ```

---

### File: `products/cost_planner_v2/utils/cost_calculator.py`

**New Method:** `calculate_quick_estimate_with_breakdown()`

**Logic Flow:**

1. **Load base cost** for care tier from config
2. **Apply regional multiplier** (ZIP→ZIP3→state→default precedence)
3. **Check for GCP flags** via MCIP:
   ```python
   gcp_rec = MCIP.get_care_recommendation()
   flags = []
   if gcp_rec and hasattr(gcp_rec, 'flags'):
       flags = [f.get('id') if isinstance(f, dict) else f for f in gcp_rec.flags]
   ```

4. **Apply condition-based add-ons:**
   ```python
   # Cognitive (+20%)
   if "memory_support" in flags:
       cognitive_addon = running_total * 0.20
       breakdown["cognitive_addon"] = cognitive_addon
       running_total += cognitive_addon
   
   # Mobility (+15%)
   if "mobility_limited" in flags:
       mobility_addon = running_total * 0.15
       breakdown["mobility_addon"] = mobility_addon
       running_total += mobility_addon
   
   # High-acuity (+25%)
   if care_tier == "memory_care_high_acuity":
       high_acuity_addon = running_total * 0.25
       breakdown["high_acuity_addon"] = high_acuity_addon
       running_total += high_acuity_addon
   ```

5. **Return CostEstimate** with detailed breakdown dict

**Key Features:**
- Add-ons are **cumulative** (each applies to running total)
- Breakdown dict tracks every component separately
- Only includes add-on keys if they're actually applied
- Respects regional multiplier in base calculation before add-ons

---

### File: `products/cost_planner_v2/utils/regional_data.py`

**No changes needed** - already supports ZIP→ZIP3→state→default precedence.

**Precedence System:**
1. Try exact ZIP match (5 digits)
2. Try ZIP3 match (first 3 digits)
3. Try state match
4. Fall back to national default (1.0)

**Returns:** `RegionalMultiplier` with multiplier value and metadata (region name, precision level)

---

## Data Flow & Integration

### Inbound (from GCP):
```
GCP Complete
  ↓
MCIP stores care_recommendation:
  - tier: "memory_care"
  - flags: [{id: "memory_support"}, {id: "mobility_limited"}, ...]
  ↓
Quick Estimate reads MCIP:
  - Seeds care type selector with tier
  - Checks flags for add-ons
```

### Outbound (to Full Assessment):
```
User clicks "Continue to Full Assessment"
  ↓
Persist:
  - Current care selection (might differ from GCP if user switched)
  - ZIP code
  ↓
Trigger authentication flow
  ↓
Full Assessment loads with context
```

**Important:** Quick Estimate **does NOT overwrite** GCP recommendation. It's a preview tool.

---

## Validation & Error Handling

### ZIP Code Validation:
```python
if zip_code and len(zip_code) != 5:
    st.error("Please enter a valid 5-digit ZIP code, or leave it blank.")
    return
```

### Unknown ZIP:
- Falls back to ZIP3 → state → default
- Shows caption: "ℹ️ Using regional average (ZIP not found)"

### Missing GCP Recommendation:
- Defaults selector to "In-Home Care"
- No error shown (graceful fallback)

### Invalid Care Tier:
- Should never happen (dropdown enforces valid options)
- Fallback base cost: $4,000/month

---

## Acceptance Test Results

| Test Case | Status | Notes |
|-----------|--------|-------|
| **ZIP only (State removed)** | ✅ PASS | State field completely removed from UI |
| **5 care types only** | ✅ PASS | Dropdown shows exactly 5 options |
| **No legacy types** | ✅ PASS | No "Independent Living" or "Skilled Nursing" anywhere |
| **GCP recommendation seeding** | ✅ PASS | Pre-selects GCP tier when available |
| **Default to In-Home Care** | ✅ PASS | Defaults to In-Home Care if no GCP rec |
| **Line-item breakdown** | ✅ PASS | Shows base, regional, add-ons, total |
| **Base cost correct** | ✅ PASS | Matches config for each tier |
| **Regional adjustment** | ✅ PASS | ZIP→ZIP3→state→default precedence works |
| **Cognitive add-on (+20%)** | ✅ PASS | Shows only when memory_support flag present |
| **Mobility add-on (+15%)** | ✅ PASS | Shows only when mobility_limited flag present |
| **High-acuity add-on (+25%)** | ✅ PASS | Always shows for Memory Care (High Acuity) |
| **No add-ons message** | ✅ PASS | Shows when no add-ons apply |
| **Adjusted total calculation** | ✅ PASS | Math is correct (cumulative add-ons) |
| **Scenario switching** | ✅ PASS | User can switch care type and recalculate |
| **GCP rec not overwritten** | ✅ PASS | Original rec preserved in MCIP |
| **Reassurance copy** | ✅ PASS | Exact copy from spec displayed |
| **CTA to Full Assessment** | ✅ PASS | Button triggers auth flow |
| **No errors in terminal** | ✅ PASS | No Python errors, no JS errors |

---

## Edge Cases Handled

### 1. User has NO GCP recommendation
**Behavior:** Defaults to "In-Home Care", no caption shown

### 2. User has GCP rec but switches care type
**Behavior:** Shows selected type, original GCP rec preserved in MCIP

### 3. ZIP code not found
**Behavior:** Falls back to ZIP3 → state → default, shows "using regional average"

### 4. User has cognitive AND mobility flags
**Behavior:** Both add-ons applied cumulatively (+20%, then +15% of new total)

### 5. Memory Care (High Acuity) with cognitive flag
**Behavior:** Shows both cognitive (+20%) AND high-acuity (+25%) add-ons

### 6. No Care Recommended with no flags
**Behavior:** Shows only base cost ($500) + regional adjustment, no add-ons

---

## Cost Examples (Illustrative)

### Example 1: In-Home Care, ZIP 90210, No Flags
```
Base Cost (In-Home Care):           $3,500 / month
+ Regional Adjustment (ZIP 90210):  +15% ($525)
= Adjusted Total:                   $4,025 / month
```

### Example 2: Memory Care, ZIP 10001, Cognitive + Mobility Flags
```
Base Cost (Memory Care):                $6,500 / month
+ Regional Adjustment (ZIP 10001):      +25% ($1,625)
+ Cognitive-related Adjustment:         +20% ($1,625)
+ Mobility-related Adjustment:          +15% ($1,462.50)
= Adjusted Total:                       $11,212.50 / month
```

### Example 3: Memory Care (High Acuity), ZIP 60601, No Other Flags
```
Base Cost (Memory Care High Acuity):    $9,000 / month
+ Regional Adjustment (ZIP 60601):      +10% ($900)
+ High-Acuity Adjustment:               +25% ($2,475)
= Adjusted Total:                       $12,375 / month
```

### Example 4: No Care Recommended, ZIP 73301, No Flags
```
Base Cost (No Care Recommended):    $500 / month
+ Regional Adjustment (ZIP 73301):  -5% ($-25)
ℹ️ No additional care adjustments applied for your area.
= Adjusted Total:                   $475 / month
```

---

## Configuration Dependencies

### Base Costs: `config/cost_config.v3.json`
```json
{
  "care_tiers": {
    "no_care_needed": {"monthly_base": 500},
    "in_home_care": {"monthly_base": 3500},
    "assisted_living": {"monthly_base": 4500},
    "memory_care": {"monthly_base": 6500},
    "memory_care_high_acuity": {"monthly_base": 9000}
  }
}
```

### Regional Multipliers: `config/regional_cost_config.json`
```json
{
  "zip_multipliers": {
    "90210": {"multiplier": 1.15, "name": "Beverly Hills, CA"}
  },
  "zip3_multipliers": {
    "902": {"multiplier": 1.12, "name": "Los Angeles Area"}
  },
  "state_multipliers": {
    "CA": {"multiplier": 1.10, "name": "California"}
  },
  "default_multiplier": 1.0
}
```

### GCP Flags: `products/gcp_v4/modules/care_recommendation/flags.py`
```python
FLAGS_SCHEMA = {
    "memory_support": {...},   # Triggers cognitive add-on
    "mobility_limited": {...}  # Triggers mobility add-on
}
```

---

## Future Enhancements

### Phase 2: Enhanced Quick Estimate
- [ ] Show comparison of all 5 care types side-by-side
- [ ] Add "Why these costs?" explainer tooltips
- [ ] Show national average comparison for each tier
- [ ] Add "See what's included" dropdown for each tier

### Phase 3: Advanced Scenarios
- [ ] Allow user to toggle add-ons on/off to see impact
- [ ] Show cost range (min/max) instead of single estimate
- [ ] Add "Find facilities in your area" link with real pricing

### Phase 4: Personalization
- [ ] Remember last ZIP code in session
- [ ] Show "Similar users paid X" benchmarking
- [ ] Add "Email this estimate" feature

---

## Related Documentation

- **5-Tier System:** `GCP_5_TIER_SYSTEM_IMPLEMENTATION.md`
- **Cost Planner V2 Architecture:** `COST_PLANNER_ARCHITECTURE.md`
- **Regional Cost Data:** `config/regional_cost_config.json`
- **GCP Flags:** `products/gcp_v4/modules/care_recommendation/flags.py`

---

## Commit Information

**Files Modified:**
1. `products/cost_planner_v2/intro.py` - UI form and results rendering
2. `products/cost_planner_v2/utils/cost_calculator.py` - New calculation method with breakdown

**Lines Changed:**
- intro.py: ~200 lines (complete rewrite of form and results sections)
- cost_calculator.py: +100 lines (new method)

**Testing:** Manual testing completed, all acceptance criteria met

---

## Support & Troubleshooting

### Issue: Add-ons not showing
**Check:** Does user have GCP completed? Are flags present in MCIP?
```python
from core.mcip import MCIP
rec = MCIP.get_care_recommendation()
print(f"Flags: {rec.flags if rec else 'No GCP rec'}")
```

### Issue: Regional adjustment wrong
**Check:** Is ZIP code in config? Check precedence fallback.
```python
from products.cost_planner_v2.utils.regional_data import RegionalDataProvider
result = RegionalDataProvider.get_multiplier(zip_code="90210")
print(f"Multiplier: {result.multiplier}, Precision: {result.precision}")
```

### Issue: Wrong care type shown
**Check:** Mapping between GCP tier and display name.
```python
tier_to_display = {
    "no_care_needed": "No Care Recommended",
    "in_home": "In-Home Care",  # Note: GCP uses "in_home", Cost uses "in_home_care"
    ...
}
```

---

**Status:** ✅ **COMPLETE & TESTED**  
**Ready for:** Production deployment  
**Next Step:** Full Assessment modules (authenticated flow)

