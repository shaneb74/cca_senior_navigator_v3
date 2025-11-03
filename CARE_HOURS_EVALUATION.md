# Care Hours Recommendation Evaluation
## Quick Estimate Page - Hours Logic Analysis

**Date**: November 2, 2025  
**Scope**: Evaluation of care hours recommendation flow from GCP → Quick Estimate  
**Status**: ⚠️ **ISSUES IDENTIFIED** - See recommendations below

---

## Executive Summary

The care hours recommendation system has **THREE MAIN ISSUES**:

1. **❌ Band-to-Numeric Conversion Inconsistency**: Different mappings in GCP vs Quick Estimate
2. **⚠️ Mid-Range Ambiguity**: "4-8h" band maps to 6.0 hours, but LLM advisory uses 8.0 (high end)
3. **⚠️ User Experience Gap**: Hours confirmation advisory doesn't show for facility-based recommendations

---

## System Architecture

### Flow Overview
```
GCP Module (logic.py)
  ↓ User selects band: "<1h", "1-3h", "4-8h", "24h"
  ↓ LLM suggests band based on care needs
  ↓ Stores: gcp.hours_user_band, gcp.hours_llm
  ↓
Quick Estimate (quick_estimate.py)
  ↓ Reads bands from GCP state
  ↓ Converts band → numeric hours
  ↓ Initializes slider with numeric value
  ↓
Hours Advisory (ui_helpers.py)
  ↓ Compares user hours vs LLM suggestion
  ↓ Shows confirmation if user < LLM
  ↓ User can accept LLM suggestion or keep current
```

---

## Issue #1: Band-to-Numeric Conversion Inconsistency

### Problem
Two different conversion functions with **different mappings**:

**Function 1**: `_get_gcp_hours_per_day()` in `quick_estimate.py` (lines 241-298)
```python
# Quick Estimate mapping
band_map = {
    "<1h": 1.0,
    "1-3h": 2.0,    # ← Uses LOW END of range
    "4-8h": 6.0,    # ← Uses MID-POINT (comment says "mid-range unless explicitly chose 8")
    "24h": 24.0,
}
```

**Function 2**: `parse_hours_band_to_high_end()` in `ui_helpers.py` (lines 57-76)
```python
# Advisory mapping (regex-based)
def parse_hours_band_to_high_end(band: str | None) -> float | None:
    m = re.match(r"(\d+)\s*-\s*(\d+)\s*h", band)
    if m:
        return float(m.group(2))  # ← Always returns HIGH END of range
    # "1-3h" → 3.0
    # "4-8h" → 8.0
```

### Impact
- User selects "4-8h" in GCP
- Quick Estimate initializes slider to **6.0 hours**
- LLM suggests "4-8h" band
- Advisory parses as **8.0 hours** (high end)
- Mismatch: 6.0 ≠ 8.0, so advisory shows even though user "selected" the LLM band

### Evidence
From `quick_estimate.py` line 487:
```python
print(f"[QE_LLM] band={llm_band} → high={llm_high}")
```
This will show: `band=4-8h → high=8.0`

But initialization on line 480 shows:
```python
print(f"[QE_INIT] home_hours={gcp_hours}")  # gcp_hours = 6.0 from _get_gcp_hours_per_day()
```

---

## Issue #2: Mid-Range Philosophy Unclear

### Problem
The "4-8h" band has **ambiguous intent**:
- Comment says "use mid-range" (6.0)
- But advisory logic needs high-end (8.0) for proper cost estimation
- User perception: "I selected 4-8 hours" could mean anywhere in that range

### Current Behavior
1. GCP: User selects "4-8h"
2. Quick Estimate: Initializes slider to 6.0
3. User sees 6.0 on slider (thinks this is their selection)
4. Advisory compares 6.0 < 8.0 (LLM high end)
5. Advisory shows: "Update to 8.0 hours" even though user selected "4-8h"

### User Confusion
User: "I already selected 4-8 hours! Why is it asking me to update to 8?"
System: "Because we initialized you to the mid-point (6), but LLM wants high-end (8)"

---

## Issue #3: Hours Advisory Only Shows for In-Home

### Problem
Hours confirmation advisory is **GATED** to only show when:
```python
# From ui_helpers.py line 306
need_hours = (tier in ("in_home", "in_home_plus")) or bool(compare_inhome)
```

### Impact
- User gets assisted living recommendation
- Cost Planner doesn't enable "Compare In-Home" toggle
- Hours advisory **NEVER SHOWS** even if LLM has hours suggestion
- User never sees hours guidance for comparison scenarios

### Gap
If user wants to compare assisted living vs in-home care:
1. They need accurate hours estimate for in-home costs
2. But advisory won't show unless they explicitly enable comparison
3. This creates a UX gap where hours aren't discussed until later

---

## Recommendation #1: Standardize Band-to-Numeric Conversion

### Proposed Solution
Create a **SINGLE canonical mapping function** that all code uses:

```python
# In products/cost_planner_v2/utils/hours_helpers.py

HOURS_BAND_MAPPINGS = {
    "<1h": {"low": 0.5, "mid": 0.5, "high": 1.0, "default": 1.0},
    "1-3h": {"low": 1.0, "mid": 2.0, "high": 3.0, "default": 2.0},
    "4-8h": {"low": 4.0, "mid": 6.0, "high": 8.0, "default": 6.0},
    "24h": {"low": 24.0, "mid": 24.0, "high": 24.0, "default": 24.0},
}

def band_to_hours(band: str, strategy: str = "default") -> float:
    """
    Convert hours band to numeric hours.
    
    Args:
        band: Hours band ("<1h", "1-3h", "4-8h", "24h")
        strategy: "low", "mid", "high", or "default"
        
    Returns:
        Float hours per day
        
    Examples:
        band_to_hours("4-8h", "mid") → 6.0
        band_to_hours("4-8h", "high") → 8.0
        band_to_hours("1-3h") → 2.0 (default)
    """
    if not band or band not in HOURS_BAND_MAPPINGS:
        return 2.0  # Safe fallback
    
    mapping = HOURS_BAND_MAPPINGS[band]
    return mapping.get(strategy, mapping["default"])
```

### Usage
```python
# Quick Estimate initialization
gcp_hours = band_to_hours(user_band, "mid")  # 6.0 for "4-8h"

# Advisory comparison
llm_hours = band_to_hours(llm_band, "high")  # 8.0 for "4-8h"

# Cost calculation (conservative)
cost_hours = band_to_hours(user_band, "high")  # Use high end for cost safety
```

### Benefits
- ✅ Single source of truth for all conversions
- ✅ Explicit about which strategy is used where
- ✅ Easy to adjust mappings globally
- ✅ Self-documenting code

---

## Recommendation #2: Clarify Advisory Trigger Logic

### Current Problem
Advisory shows when `current_hours < llm_high_end`:
```python
# ui_helpers.py line 311
if current < llm_high:
    # Show advisory
```

This triggers even when user selected the **same band** as LLM but we initialized to mid-point.

### Proposed Solution A: Band-Level Comparison

**Compare bands instead of numeric hours:**
```python
def should_show_hours_advisory() -> bool:
    """Determine if hours advisory should show.
    
    Advisory shows when:
    1. User selected a LOWER band than LLM suggests
    2. User adjusted slider below LLM high-end after seeing suggestion
    """
    gcp = st.session_state.get("gcp", {})
    user_band = gcp.get("hours_user_band")  # e.g., "1-3h"
    llm_band = gcp.get("hours_llm")         # e.g., "4-8h"
    
    # Band hierarchy
    BAND_ORDER = ["<1h", "1-3h", "4-8h", "24h"]
    
    # Compare bands (not numeric hours)
    try:
        user_idx = BAND_ORDER.index(user_band)
        llm_idx = BAND_ORDER.index(llm_band)
        return user_idx < llm_idx  # User selected LOWER band
    except (ValueError, TypeError):
        return False
```

**Benefits:**
- ✅ Only shows when user genuinely selected a lower band
- ✅ Avoids confusion when user selected "4-8h" and we initialized to 6.0
- ✅ Clearer user intent comparison

### Proposed Solution B: Show Advisory Once Per Band Pair

**Use the existing nudge key system** (already implemented in GCP logic):
```python
# From logic.py line 1293
key = f"{user_band_cur or '-'}->{suggested_band_cur or '-'}"
prev = st.session_state.get("_hours_nudge_key")
st.session_state["_hours_nudge_new"] = bool(under_selected_flag and key != prev)
st.session_state["_hours_nudge_key"] = key
```

**Only show advisory when `_hours_nudge_new = True`**

This prevents repeated advisory for same band pair.

---

## Recommendation #3: Expand Advisory Context

### Current Gap
Advisory only shows for in-home recommendations, not for comparison scenarios.

### Proposed Solution
Add hours advisory to **facility cards** when user enables comparison:

```python
def _render_facility_card_with_comparison(zip_code: str):
    """Render facility card with optional in-home comparison."""
    
    # ... existing facility cost display ...
    
    # Show in-home comparison toggle
    compare_inhome = st.checkbox(
        "Compare with In-Home Care",
        key="comparison_compare_inhome",
        value=st.session_state.get("cost.compare_inhome", False)
    )
    
    if compare_inhome:
        st.markdown("---")
        st.markdown("#### In-Home Care Alternative")
        
        # Show hours advisory HERE (before showing in-home costs)
        render_confirm_hours_if_needed(current_hours_key="qe_home_hours")
        
        # Then show in-home cost breakdown
        _render_inhome_comparison_breakdown(zip_code)
```

**Benefits:**
- ✅ Hours guidance shows when user explores in-home option
- ✅ Contextual: shows before they see in-home costs
- ✅ Prevents sticker shock from under-estimated hours

---

## Recommendation #4: Add Visual Band Indicator

### Problem
Slider shows numeric hours (6.0) but user selected a band ("4-8h").

### Proposed Solution
Show band context on slider:

```python
st.slider(
    "Hours per day",
    min_value=1.0,
    max_value=24.0,
    value=current_hours,
    step=1.0,
    key="qe_home_hours",
    help="Adjust based on care needs",
    label_visibility="collapsed"
)

# Add band indicator below slider
band = _hours_to_band(current_hours)
st.caption(f"📊 Current selection: **{band}** ({current_hours:.1f} h/day)")
```

**Visual Enhancement:**
```
─────●──────────────────────  6.0 h/day
 📊 Current: 4-8h band (mid-range)
 ✨ Suggested: 4-8h band (for safety, consider high end: 8h)
```

---

## Implementation Priority

### 🔥 **Critical** (Fix Now)
1. **Standardize band-to-numeric conversion** (Recommendation #1)
   - Creates single source of truth
   - Prevents future inconsistencies
   - Estimated effort: 2-3 hours

### ⚠️ **Important** (Fix Soon)
2. **Clarify advisory trigger logic** (Recommendation #2, Solution A)
   - Prevents user confusion
   - Improves advisory accuracy
   - Estimated effort: 1-2 hours

3. **Expand advisory context** (Recommendation #3)
   - Improves UX for comparison scenarios
   - Ensures hours guidance is always available
   - Estimated effort: 1-2 hours

### 💡 **Enhancement** (Consider Later)
4. **Add visual band indicator** (Recommendation #4)
   - Nice-to-have UX improvement
   - Helps users understand band ranges
   - Estimated effort: 1 hour

---

## Testing Recommendations

### Test Scenario 1: Band Consistency
1. Complete GCP with "4-8h" selection
2. Navigate to Quick Estimate
3. **Verify**: Slider initializes to expected value (6.0 with current logic)
4. **Verify**: Advisory shows/doesn't show based on LLM suggestion
5. **Verify**: Hours used in cost calculation match slider value

### Test Scenario 2: Advisory Trigger
1. Complete GCP with "1-3h" selection (LLM suggests "4-8h")
2. Navigate to Quick Estimate
3. **Verify**: Advisory shows (genuine under-selection)
4. Accept LLM suggestion (8.0)
5. **Verify**: Advisory disappears
6. Adjust slider to 7.0
7. **Verify**: Advisory doesn't reappear (user made conscious choice)

### Test Scenario 3: Facility Comparison
1. Complete GCP with assisted living recommendation
2. Navigate to Quick Estimate (Assisted Living tab)
3. Enable "Compare In-Home Care"
4. **Verify**: Hours advisory shows (if LLM has suggestion)
5. **Verify**: In-home costs use hours from advisory decision

---

## Conclusion

The care hours recommendation system is **architecturally sound** but has **implementation inconsistencies** that create user confusion. The primary issues are:

1. **Multiple conversion functions** with different logic
2. **Mid-range vs high-end ambiguity** in band interpretation
3. **Limited context** for hours advisory (in-home only)

All issues are **fixable with surgical changes** - no major refactoring needed. Prioritize Recommendations #1 and #2 for immediate impact.

---

## Code References

**Files to modify:**
- `products/cost_planner_v2/quick_estimate.py` (lines 241-298)
- `products/cost_planner_v2/ui_helpers.py` (lines 57-76, 306-450)
- `products/gcp_v4/modules/care_recommendation/logic.py` (lines 1180-1360)

**New file to create:**
- `products/cost_planner_v2/utils/hours_helpers.py` (canonical mappings)

**Session state keys to track:**
- `gcp.hours_user_band` - User's selected band from GCP
- `gcp.hours_llm` - LLM's suggested band
- `comparison_inhome_hours` - Numeric hours for slider
- `_hours_nudge_key` - Advisory dismissal tracking

---

**Evaluation completed**: Ready for review and prioritization
