# GCP Care Recommendation Display Fix

## Issue Summary
The care_recommendation was not displaying on the GCP Product tile results page, and the Cost Planner was not receiving the incoming recommendation from the handoff data.

## Root Cause Analysis

### Issue 1: Recommendation Display Logic
**File:** `core/modules/engine.py` → `_get_recommendation()`

**Problem:** The function was trying to normalize recommendation strings before looking them up in a mapping dictionary. The new `logic_v3.py` returns properly formatted strings like:
- "Independent / In-Home"
- "In-Home Care"
- "Assisted Living"
- "Memory Care"
- "High-Acuity Memory Care"

When normalized, these became keys like `independent___in_home` or `high_acuity_memory_care`, but the mapping didn't have entries for all variations.

**Example:**
```python
# Input: "High-Acuity Memory Care"
# After normalization: "high_acuity_memory_care"
# Mapping had: "memory_care_high_acuity" ❌ (wrong order)
```

### Issue 2: Missing Mapping Entry
The mapping dictionary was missing an entry for `high_acuity_memory_care` (only had `memory_care_high_acuity`).

## Solution Implemented

### 1. Updated `_get_recommendation()` in `core/modules/engine.py`

**Change:** Added logic to detect if the recommendation is already properly formatted (contains capitals, slashes, or hyphens) and use it as-is without normalization.

```python
def _get_recommendation(mod: Dict[str, Any], config: ModuleConfig) -> Optional[str]:
    """Get recommendation text from outcomes or module state."""
    outcome_key = f"{config.state_key}._outcomes"
    outcomes = st.session_state.get(outcome_key, {})
    recommendation = outcomes.get("recommendation")
    
    if recommendation:
        # NEW: If already properly formatted, use as-is
        if any(c.isupper() for c in recommendation) or "/" in recommendation or "-" in recommendation:
            return f"Based on your answers, we recommend {recommendation}."
        
        # Otherwise normalize (backward compatibility with old logic)
        rec_key = recommendation.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
        
        mapping = {
            # ... existing mappings ...
            "high_acuity_memory_care": "High-Acuity Memory Care",  # NEW: Handle both orderings
            # ... rest of mappings ...
        }
        
        pretty = mapping.get(rec_key)
        if not pretty:
            pretty = recommendation.replace("_", " ").replace("/", " / ").title()
        
        return f"Based on your answers, we recommend {pretty}."
```

**Benefits:**
- ✅ Handles new `logic_v3` output directly (no normalization needed)
- ✅ Maintains backward compatibility with old snake_case recommendations
- ✅ Added `high_acuity_memory_care` mapping for completeness

### 2. Added Debug Output

**Purpose:** Help diagnose issues in production if they occur

**Locations:**
1. **`_ensure_outcomes()`** - Logs when outcomes are computed:
   ```python
   print(f"[DEBUG] Outcomes computed successfully:")
   print(f"  Recommendation: {outcome.recommendation}")
   print(f"  Tier: {outcome.summary.get('tier')}")
   print(f"  Score: {outcome.summary.get('total_score')}")
   ```

2. **`_ensure_outcomes()` handoff** - Logs when handoff data is set:
   ```python
   print(f"[DEBUG] Handoff data set for '{state_key}':")
   print(f"  recommendation: {handoff[state_key]['recommendation']}")
   print(f"  flags: {len(handoff[state_key]['flags'])} flags")
   ```

3. **`_render_results_view()`** - Logs what's being rendered:
   ```python
   print(f"[DEBUG] _render_results_view called:")
   print(f"  outcomes exists: {bool(outcomes)}")
   print(f"  recommendation from outcomes: {outcomes.get('recommendation')}")
   print(f"  formatted recommendation: {recommendation}")
   ```

### 3. Created Integration Test

**File:** `products/gcp/modules/care_recommendation/test_integration.py`

**Tests:**
1. ✅ `derive_outcome()` returns valid `OutcomeContract`
2. ✅ OutcomeContract has all required fields
3. ✅ Handoff data structure is correct
4. ✅ Cost Planner can map the recommendation
5. ✅ All 5 tier names map to Cost Planner care types

**Test Results:**
```
✅ INTEGRATION TEST PASSED!
   - derive_outcome() produces valid OutcomeContract
   - Handoff structure is correct
   - All tier names map to Cost Planner care types
```

## Data Flow Verification

### 1. Logic → OutcomeContract
```python
# products/gcp/modules/care_recommendation/logic.py
def derive_outcome(answers, context) -> OutcomeContract:
    # ... scoring logic ...
    return OutcomeContract(
        recommendation=TIER_NAMES[final_tier],  # e.g., "Assisted Living"
        confidence=0.85,
        flags={...},
        tags=[...],
        domain_scores={...},
        summary={...},
        routing={...},
        audit={...}
    )
```

### 2. Engine → Session State & Handoff
```python
# core/modules/engine.py: _ensure_outcomes()
outcome = derive_outcome(answers, context)

# Store in session state
st.session_state[f"{state_key}._outcomes"] = asdict(outcome)

# Set handoff data for Cost Planner
handoff = st.session_state.setdefault("handoff", {})
handoff["gcp"] = {
    "recommendation": outcome.recommendation,  # "Assisted Living"
    "flags": dict(outcome.flags),
    "tags": list(outcome.tags),
    "domain_scores": dict(outcome.domain_scores),
}
```

### 3. Cost Planner → Read Handoff
```python
# products/cost_planner/cost_estimate_v2.py
def get_gcp_recommendation() -> Optional[str]:
    handoff = st.session_state.get("handoff", {}).get("gcp", {})
    return handoff.get("recommendation")  # "Assisted Living"

# Maps to care type
TIER_TO_CARE_TYPE = {
    "Independent / In-Home": "no_care",
    "In-Home Care": "in_home_care",
    "Assisted Living": "assisted_living",  # ✅ Match!
    "Memory Care": "memory_care",
    "High-Acuity Memory Care": "memory_care_high_acuity"
}
```

### 4. Results Page → Display Recommendation
```python
# core/modules/engine.py: _render_results_view()
recommendation = _get_recommendation(mod, config)
# Returns: "Based on your answers, we recommend Assisted Living."

st.markdown(f"<h3 class='h3 rec-line'>{H(recommendation)}</h3>", 
            unsafe_allow_html=True)
```

## Verification Steps

### Manual Testing Checklist

1. **Start Streamlit app:**
   ```bash
   streamlit run app.py
   ```

2. **Complete GCP assessment:**
   - Navigate to "Guided Care Plan" tile
   - Answer all questions (any scenario)
   - Advance to results page

3. **Check results page:**
   - ✅ Recommendation displays: "Based on your answers, we recommend [Tier Name]."
   - ✅ Summary points display
   - ✅ No error messages

4. **Check console output:**
   Look for `[DEBUG]` lines:
   ```
   [DEBUG] Outcomes computed successfully:
     Recommendation: Assisted Living
     Tier: 2
     Score: 31
     Flags: 6 flags
   
   [DEBUG] Handoff data set for 'gcp':
     recommendation: Assisted Living
     flags: 6 flags
     domain_scores: 8 domains
   
   [DEBUG] _render_results_view called:
     outcomes exists: True
     recommendation from outcomes: Assisted Living
     formatted recommendation: Based on your answers, we recommend Assisted Living.
   ```

5. **Check session state:**
   Use Streamlit's session state inspector or add debug output:
   ```python
   import streamlit as st
   st.write("Handoff data:", st.session_state.get("handoff", {}))
   ```

6. **Navigate to Cost Planner:**
   - Click "Cost Planner" from results page or nav
   - ✅ Should see GCP recommendation used
   - ✅ Cost estimate should reflect the care tier

### Automated Testing

**Run integration test:**
```bash
python products/gcp/modules/care_recommendation/test_integration.py
```

**Expected output:**
```
✅ INTEGRATION TEST PASSED!
```

## Files Modified

| File | Change | Purpose |
|------|--------|---------|
| `core/modules/engine.py` | Updated `_get_recommendation()` | Handle properly-formatted strings from logic_v3 |
| `core/modules/engine.py` | Added debug output in `_ensure_outcomes()` | Track outcomes computation |
| `core/modules/engine.py` | Added debug output in `_render_results_view()` | Track results rendering |
| `products/gcp/modules/care_recommendation/test_integration.py` | Created new file | Verify full data flow |

## Known Working Configurations

### Tier Names (from logic.py)
```python
TIER_NAMES = {
    0: "Independent / In-Home",
    1: "In-Home Care",
    2: "Assisted Living",
    3: "Memory Care",
    4: "High-Acuity Memory Care"
}
```

### Cost Planner Mappings (from cost_estimate_v2.py)
```python
TIER_TO_CARE_TYPE = {
    "Independent / In-Home": "no_care",
    "In-Home Care": "in_home_care",
    "Assisted Living": "assisted_living",
    "Memory Care": "memory_care",
    "High-Acuity Memory Care": "memory_care_high_acuity"
}
```

### Handoff Data Structure
```python
st.session_state["handoff"]["gcp"] = {
    "recommendation": str,           # e.g., "Assisted Living"
    "flags": dict,                   # e.g., {"cognitive_risk": True, ...}
    "tags": list,                    # e.g., ["moderate_needs", ...]
    "domain_scores": dict            # e.g., {"cognitive": 9, ...}
}
```

## Troubleshooting

### Issue: Recommendation not displaying
**Check:**
1. Console for `[DEBUG] Outcomes computed successfully` - if missing, scoring logic failed
2. `st.session_state.get("gcp._outcomes")` - should exist after completing assessment
3. Console for `[DEBUG] _render_results_view called` - verify outcomes exist

### Issue: Cost Planner not receiving recommendation
**Check:**
1. `st.session_state.get("handoff", {}).get("gcp")` - should have `recommendation` key
2. Console for `[DEBUG] Handoff data set for 'gcp'` - verify handoff was created
3. Recommendation string matches TIER_TO_CARE_TYPE keys exactly (case-sensitive)

### Issue: Error during outcomes computation
**Check:**
1. Streamlit UI for error message: `DEBUG: Error computing outcomes: [Type]: [Message]`
2. Check that all required question IDs from module.json are answered
3. Verify `outcomes_compute` path in product.py is correct: `"products.gcp.modules.care_recommendation.logic:derive_outcome"`

## Next Steps

After verifying the fix works in the live app:

1. **Remove debug output** (or wrap in environment check):
   ```python
   import os
   DEBUG = os.getenv("DEBUG_GCP", "false").lower() == "true"
   
   if DEBUG:
       print(f"[DEBUG] Outcomes computed successfully...")
   ```

2. **Document for care coordinators:**
   - Update user docs with new tier names
   - Explain what each recommendation means
   - Provide examples of typical scores for each tier

3. **Monitor production:**
   - Track recommendation distribution (tier 0-4 percentages)
   - Monitor Cost Planner handoff success rate
   - Collect feedback on recommendation accuracy

## Success Criteria

- [x] Integration test passes (all 5 tests)
- [ ] Recommendation displays on GCP results page
- [ ] Console shows [DEBUG] output with correct data
- [ ] Cost Planner receives and maps recommendation correctly
- [ ] No errors in Streamlit console during GCP flow

---

**Status:** Ready for live testing in Streamlit app

**Next Action:** Run `streamlit run app.py` and complete a GCP assessment to verify display and handoff
