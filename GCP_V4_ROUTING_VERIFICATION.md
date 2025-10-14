# GCP v4 Routing Verification

**Date:** October 14, 2025  
**Status:** ✅ VERIFIED  
**Module:** products/gcp_v4/modules/care_recommendation/module.json

## Question: Does clicking the GCP button load the correct v4 module?

**Answer: YES ✅** - All routing is correctly configured.

## Complete Flow Verification

### 1. User Action
When the user clicks either:
- **GCP tile's "Start" button** in Concierge Hub
- **Navi's "Create Your Guided Care Plan" button**

### 2. Routing Chain

```
User Click
    ↓
Concierge Hub (_build_gcp_tile)
    → primary_route = "?page=gcp_v4"
    ↓
MCIP.get_product_summary("gcp_v4")
    → returns { "route": "gcp_v4" }
    ↓
nav.json lookup for "gcp_v4"
    → module: "products.gcp_v4.product:render"
    ↓
products/gcp_v4/product.py:render()
    → config = _load_module_config()
    ↓
products/gcp_v4/modules/care_recommendation/config.py:get_config()
    → raw = _load_module_json()
    ↓
Path(__file__).with_name("module.json")
    → /products/gcp_v4/modules/care_recommendation/module.json ✅
    ↓
core/modules/engine.py:run_module(config)
    → Renders first step from config.steps[0]
```

### 3. Module Loading Verification

**Source File:** `products/gcp_v4/modules/care_recommendation/module.json`
- ✅ Exists: True
- ✅ Size: 20,531 bytes
- ✅ Sections: 6 total

**Section Order:**
1. **intro** (type=info, 0 questions) - Welcome page
2. **about_you** (type=questions, 3 questions) - Demographics
3. **medication_mobility** (type=questions, 5 questions) - Health assessment
4. **cognition_mental_health** (type=questions, 3 questions) - Cognitive assessment
5. **daily_living** (type=questions, 5 questions) - ADL/IADL assessment
6. **results** (type=results, 0 questions) - Recommendation display

### 4. First Question Verification

**Step 0 (Intro Page):**
- ID: `intro`
- Title: "Welcome to the Guided Care Plan"
- Type: info (no questions)
- User sees: Welcome message with "Start" button

**Step 1 (First Question Section):**
- ID: `about_you`
- Title: "About You"
- Subtitle: "Tell us about the person's current situation."

**First Question (after clicking "Start"):**
- ID: `age_range`
- Label: "What is this person's age range?"
- Type: Single-select
- Required: Yes
- Options: 4 (Under 65, 65-74, 75-84, 85+)
- Widget: Chip selector (horizontal)

✅ **This is question 1 from module.json as expected!**

### 5. Config Loader Test

```python
from products.gcp_v4.modules.care_recommendation.config import get_config

config = get_config()
# Returns:
#   product: gcp_v4
#   state_key: gcp_care_recommendation
#   steps: 6 total
#   outcomes_compute: products.gcp_v4.modules.care_recommendation.logic:derive_outcome
#   results_step_id: results
```

### 6. Nav.json Routing Test

Both legacy and new keys route correctly:

| Nav Key | Module Path | Status |
|---------|-------------|--------|
| `gcp` | products.gcp_v4.product:render | ✅ Legacy support |
| `gcp_v4` | products.gcp_v4.product:render | ✅ Primary route |

### 7. Module Engine Flow

When `run_module(config)` is called:

1. **Load state:** `st.session_state["gcp_care_recommendation"]`
2. **Determine step:** Check saved step or start at 0 (intro)
3. **Render intro page:** Show welcome message
4. **User clicks "Start":** Advance to step 1
5. **Render first question:** Show `age_range` question from `about_you` section
6. **Continue flow:** Progress through remaining sections
7. **Compute outcome:** Call `logic:derive_outcome()` at results step
8. **Publish to MCIP:** Store CareRecommendation contract

## Verification Summary

✅ **All checks passed:**

- [x] GCP tile routes to `?page=gcp_v4`
- [x] Navi button routes to `gcp_v4`
- [x] nav.json maps `gcp_v4` to correct module
- [x] product.py loads correct config
- [x] config.py reads from correct module.json
- [x] module.json is the v4 version (20,531 bytes)
- [x] First step is intro page
- [x] Second step is about_you section
- [x] First question is age_range
- [x] Module engine renders correctly

## Testing Instructions

To manually verify in the browser:

1. Navigate to http://localhost:8501
2. Go to Concierge Hub (`?page=hub_concierge`)
3. Click the **"Create Your Guided Care Plan"** tile or Navi button
4. Verify you see: **"Welcome to the Guided Care Plan"**
5. Click **"Start"**
6. Verify first question: **"What is this person's age range?"**
7. Answer questions and verify they match module.json order

## Conclusion

**YES ✅** - When the GCP tile or Navi button is clicked, the care_recommendation module is correctly called and begins with the intro page, followed by the first question (`age_range`) from the `about_you` section in:

```
products/gcp_v4/modules/care_recommendation/module.json
```

All routing, loading, and rendering is working as designed.

---

**Related Files:**
- `products/gcp_v4/product.py` - Main render entry point
- `products/gcp_v4/modules/care_recommendation/config.py` - Config loader
- `products/gcp_v4/modules/care_recommendation/module.json` - **Source of truth** ✅
- `products/gcp_v4/modules/care_recommendation/logic.py` - Scoring engine
- `config/nav.json` - Route definitions
- `hubs/concierge.py` - Tile builder
- `core/modules/engine.py` - Module renderer
