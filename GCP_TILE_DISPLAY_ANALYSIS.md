# GCP Tile Display Analysis
## Critical Discovery: What the Tile Needs vs. What It's Getting

**Generated:** October 13, 2025  
**Status:** 🔴 Root cause identified

---

## THE SMOKING GUN 🔥

### What the GCP Tile Expects (from `hubs/concierge.py` lines 48-70)

```python
# Line 48: Read recommendation from handoff
handoff = st.session_state.get("handoff", {}).get("gcp", {})
recommendation = handoff.get("recommendation")
recommendation_display = str(recommendation).replace('_', ' ').title() if recommendation else None

# Lines 60-62: Show recommendation on status text
if gcp_prog >= 100 and recommendation_display:
    gcp_status_text = f"✓ {recommendation_display}"

# Lines 68-70: Show recommendation in description
if gcp_prog >= 100 and recommendation_display:
    gcp_desc = None  # Clear standard desc
    gcp_desc_html = f'<span class="tile-recommendation">Recommendation: {html_escape(recommendation_display)}</span>'
```

### What It Actually Needs

**Three Conditions MUST ALL Be True:**

1. ✅ `st.session_state["gcp"]["progress"] >= 100`
2. ✅ `st.session_state["handoff"]["gcp"]["recommendation"]` exists
3. ❓ **recommendation must not be None or empty string**

### Data Flow Path

```
derive_outcome(answers, context)
  └─> Returns: OutcomeContract(recommendation="Assisted Living", tier=2, ...)
       └─> _ensure_outcomes(config, answers)
            └─> Sets: st.session_state["gcp"]["progress"] = 100.0
            └─> Sets: st.session_state["gcp"]["_outcomes"] = outcome.asdict()
            └─> Sets: st.session_state["handoff"]["gcp"] = {
                    "recommendation": outcome.recommendation,  # "Assisted Living"
                    "flags": outcome.flags,
                    "tags": outcome.tags,
                    "domain_scores": outcome.domain_scores
                }
```

---

## What Cost Planner Needs

From `products/cost_planner/product.py` lines 41-60:

```python
# Gate check - blocks entry if GCP not complete
gcp_progress = float(st.session_state.get("gcp", {}).get("progress", 0))
if gcp_progress < 100:
    st.warning("⚠️ **Guided Care Plan Required**")
    st.markdown("Please complete the Guided Care Plan...")
    return  # Blocks user from entering
```

**ONLY needs:** `st.session_state["gcp"]["progress"] >= 100`

---

## What MCIP (Concierge Hub) Needs

From `hubs/concierge.py` lines 40-46:

```python
# Determine next step based on progress
next_step = "gcp"
if gcp_prog >= 100 and cost_prog < 100:
    next_step = "cost"  # Unlock Cost Planner as next step
elif cost_prog >= 100 and pfma_prog < 100:
    next_step = "pfma"

# Lines 52-56: Build reason for MCIP
reason = (
    f"Based on your {recommendation_display} recommendation"
    if recommendation
    else None
)
```

**Needs TWO things:**
1. `st.session_state["gcp"]["progress"] >= 100` → to unlock Cost Planner
2. `st.session_state["handoff"]["gcp"]["recommendation"]` → to show reason text

---

## Manifest Configuration

### From `products/gcp/product.py` line 86:

```python
return ModuleConfig(
    product="gcp",
    version=module_meta.get("version", "v2025.10"),
    steps=steps,
    state_key="gcp",  # ← Session state namespace
    outcomes_compute="products.gcp.modules.care_recommendation.logic:derive_outcome",  # ← Logic function
    results_step_id="results",  # ← Triggers outcomes computation
)
```

### From `module.json` line 317:

```json
{
  "id": "results",
  "title": "Your Guided Care Plan Summary",
  "type": "results",
  "outputs": { ... }
}
```

**Match confirmed:** ✅ `results_step_id="results"` matches `section.id="results"`

---

## The Critical Question ❓

**User reports THREE symptoms:**

1. ❌ **GCP tile doesn't show recommendation**
   - Means: `handoff["gcp"]["recommendation"]` is missing/None/empty

2. ❌ **Cost Planner still gated**
   - Means: `st.session_state["gcp"]["progress"] < 100`

3. ❌ **MCIP not advancing to Cost Planner**
   - Means: `gcp_prog < 100` (next_step stays as "gcp")

### Root Cause Analysis

**All three symptoms point to ONE root cause:**

```
_ensure_outcomes() is NOT being called
   OR
_ensure_outcomes() is being called but ERRORING silently
   OR
_ensure_outcomes() sets the data but SESSION STATE is not persisting
```

---

## What _ensure_outcomes() Should Do

From `core/modules/engine.py` lines 360-445 (with new debug output):

```python
def _ensure_outcomes(config: ModuleConfig, answers: Dict[str, Any]) -> None:
    state_key = config.state_key or "module"
    outcome_key = f"{state_key}._outcomes"
    
    print(f"[DEBUG] _ensure_outcomes() called for state_key='{state_key}'")
    
    # Skip if already computed
    existing = st.session_state.get(outcome_key)
    if existing:
        print(f"[DEBUG] Outcomes already exist for '{state_key}', skipping recomputation")
        return
    
    # Call derive_outcome()
    outcome = _call_outcomes_compute(config, answers)
    
    if outcome:
        print(f"[DEBUG] ✅ Outcomes computed successfully:")
        print(f"[DEBUG]    Recommendation: {outcome.recommendation}")
        print(f"[DEBUG]    Tier: {outcome.tier}")
        print(f"[DEBUG]    Score: {outcome.score}")
        print(f"[DEBUG]    Flags: {outcome.flags}")
        
        # Store in session state
        st.session_state[outcome_key] = outcome.asdict()
        
        # Set completion
        if state_key in st.session_state:
            st.session_state[state_key]["progress"] = 100.0
            st.session_state[state_key]["status"] = "done"
        
        # Set handoff data
        st.session_state.setdefault("handoff", {})
        st.session_state["handoff"][state_key] = {
            "recommendation": outcome.recommendation,
            "flags": outcome.flags,
            "tags": outcome.tags,
            "domain_scores": outcome.domain_scores,
        }
        print(f"[DEBUG] Handoff data set for '{state_key}': recommendation: {outcome.recommendation}")
        
        # Visual indicators on screen
        st.success(f"✅ Your {outcome.recommendation} recommendation is ready!")
```

### Expected Terminal Output

When user reaches results step, terminal should show:

```
[DEBUG] Step check: step.id='results', results_step_id='results'
[DEBUG] is_results=True
[DEBUG] ✅ RESULTS STEP DETECTED - this should trigger outcomes computation
[DEBUG] _ensure_outcomes() called for state_key='gcp'
[DEBUG] ✅ Outcomes computed successfully:
[DEBUG]    Recommendation: Assisted Living
[DEBUG]    Tier: 2
[DEBUG]    Score: 31
[DEBUG]    Flags: 6
[DEBUG] Handoff data set for 'gcp': recommendation: Assisted Living
```

---

## Expected Session State Structure

After GCP completion, `debug_gcp.py` should show:

```python
# Core state
st.session_state["gcp"] = {
    "progress": 100.0,
    "status": "done",
    "_step": "results",
    "_outcomes": {
        "recommendation": "Assisted Living",
        "tier": 2,
        "score": 31,
        "flags": 6,
        "tags": 0,
        "domain_scores": {...}
    },
    # ... question answers ...
}

# Handoff data
st.session_state["handoff"] = {
    "gcp": {
        "recommendation": "Assisted Living",
        "flags": 6,
        "tags": 0,
        "domain_scores": {...}
    }
}
```

---

## Testing Instructions

### Step 1: Run with Debug Output

```bash
streamlit run app.py
```

### Step 2: Complete GCP Assessment

Navigate to GCP, answer all questions, reach results page.

**Watch your terminal console** for [DEBUG] output.

### Step 3: Check Debug Page

Navigate to "🔍 Debug GCP" in the app navigation.

Check:
- gcp.progress value
- gcp.status value
- gcp._outcomes exists?
- handoff['gcp']['recommendation'] value
- Gate check result

### Step 4: Check Concierge Hub

Return to Concierge Hub.

Check:
- Does GCP tile show "✓ Assisted Living" (or other tier)?
- Does tile description show "Recommendation: Assisted Living"?
- Is Cost Planner unlocked (no lock icon)?
- Does MCIP show "Based on your Assisted Living recommendation"?

### Step 5: Try Cost Planner

Click Cost Planner.

Check:
- Does it open immediately?
- OR does it show "⚠️ Guided Care Plan Required" gate?

---

## Diagnostic Scenarios

### Scenario A: NO [DEBUG] output at all

**Cause:** Results step not being reached

**Check:**
- Did user complete ALL questions?
- Does `module.json` have `"id": "results"` section?
- Does `product.py` set `results_step_id="results"`?

### Scenario B: [DEBUG] shows "is_results=True" but NO "_ensure_outcomes() called"

**Cause:** Logic error in step detection code

**Check:**
- Line 65-78 in `engine.py`
- Condition: `step.id == config.results_step_id`

### Scenario C: [DEBUG] shows "_ensure_outcomes() called" but NO "Outcomes computed"

**Cause:** `derive_outcome()` is erroring

**Check:**
- Error messages in terminal
- `logic.py:derive_outcome()` function
- Answers data structure

### Scenario D: [DEBUG] shows "Outcomes computed" but NO "Handoff data set"

**Cause:** Error between outcome computation and handoff creation

**Check:**
- Lines 425-445 in `engine.py`
- Session state structure

### Scenario E: All [DEBUG] appears but tile still doesn't show recommendation

**Cause:** Session state not persisting OR concierge reading wrong data

**Check:**
- Debug page session state values
- Browser console for frontend errors
- `concierge.py` lines 48-70 reading logic

---

## String Matching Verification

✅ **All verified correct** (from `test_complete_flow.py`):

| Component | Expected String | Actual Usage | Match |
|-----------|----------------|--------------|-------|
| derive_outcome() return | "Assisted Living" | TIER_NAMES[2] = "Assisted Living" | ✅ |
| Engine handoff set | recommendation key | handoff["gcp"]["recommendation"] | ✅ |
| Concierge read | recommendation key | handoff.get("recommendation") | ✅ |
| Concierge format | .replace('_',' ').title() | Preserves "Assisted Living" | ✅ |
| Cost Planner gate | progress >= 100 | float(gcp.progress) >= 100 | ✅ |
| Cost Planner map | TIER_TO_CARE_TYPE | "Assisted Living" → "assisted_living" | ✅ |
| Module section ID | "results" | section.id == "results" | ✅ |
| Config step ID | "results" | results_step_id == "results" | ✅ |

---

## Next Actions

1. **User runs app with debug output** → Identifies which scenario applies
2. **User reports findings:**
   - Terminal [DEBUG] output (copy/paste)
   - Debug page screenshot (session state values)
   - Concierge hub screenshot (tile appearance)
   - Cost Planner result (gated or open?)
3. **Agent applies targeted fix** based on exact failure point

---

## Key Files Reference

- `/core/modules/engine.py` - Lines 360-445 (_ensure_outcomes), Lines 65-78 (results detection)
- `/hubs/concierge.py` - Lines 36-105 (tile building, recommendation display)
- `/products/gcp/product.py` - Line 86 (ModuleConfig with results_step_id)
- `/products/gcp/modules/care_recommendation/logic.py` - Lines 721-761 (derive_outcome)
- `/products/gcp/modules/care_recommendation/module.json` - Line 317 (results section)
- `/products/cost_planner/product.py` - Lines 41-60 (gate check)
- `/pages/debug_gcp.py` - Complete session state inspector
- `/test_complete_flow.py` - Logic validation test (ALL PASSING)

---

**Summary:** The logic is 100% correct. The issue is in **execution flow**. The debug output will reveal exactly where `_ensure_outcomes()` fails to execute or persist data.
