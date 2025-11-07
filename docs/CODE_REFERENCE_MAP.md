# Code Reference Map - Where to Find Everything

**Purpose**: Quick lookup for locating specific functionality in the Python prototype.

**Last Updated**: 2025-11-07

---

## 🔍 Finding Specific Features

### GCP (Guided Care Plan) Assessment

#### Main Orchestration
- **File**: `products/gcp_v4/modules/care_recommendation/logic.py`
- **Function**: `derive_outcome(answers, context, config)`
- **Lines**: 1081-1400+
- **What it does**: Main entry point that orchestrates entire GCP assessment flow

#### Answer Flow Breakdown

| Stage | Lines | What Happens | Key Variables |
|-------|-------|--------------|---------------|
| **1. Score Calculation** | 1115-1120 | Sums `option.score` from each answer | `total_score`, `scoring_details` |
| **2. Tier Mapping** | 1120-1125 | Maps score → tier using thresholds | `tier_from_score` |
| **3. Cognitive Gate** | 1140-1150 | Checks if cognition level + diagnosis allow MC | `passes_cognitive_gate`, `cog_band` |
| **4. Support Band** | 1150-1160 | Calculates support needs (low/med/high/24h) | `sup_band` |
| **5. Allowed Tiers** | 1160-1170 | Builds set of permitted tiers after gates | `allowed_tiers` |
| **6. Behavior Gate** | 1170-1185 | Blocks MC for moderate×high without risky behaviors | Modified `allowed_tiers` |
| **7. Deterministic Choice** | 1185-1200 | Chooses final deterministic tier | `det_tier` |
| **8. LLM Request** | 1240-1280 | Requests LLM tier suggestion (if enabled) | `llm_tier`, `llm_conf` |
| **9. Adjudication** | Calls line 83 | Chooses between LLM and deterministic | `final_tier`, `decision_info` |

#### Adjudication Policy (LLM-First)
- **File**: `products/gcp_v4/modules/care_recommendation/logic.py`
- **Function**: `_choose_final_tier(det_tier, allowed_tiers, llm_tier, llm_conf, bands, risky)`
- **Lines**: 83-170
- **Logic**:
  ```python
  if llm_tier and llm_tier in allowed_tiers:
      return llm_tier, {"source": "llm"}  # LLM wins
  else:
      return det_tier, {"source": "fallback"}  # Deterministic wins
  ```

#### Gate Functions
- **File**: `products/gcp_v4/modules/care_recommendation/logic.py`
- **Cognitive Gate**: `cognitive_gate(answers, flags)` - Line ~900
- **Cognition Band**: `cognition_band(answers, flags)` - Line ~950
- **Support Band**: `support_band(answers, flags)` - Line ~1000
- **MC Behavior Gate**: `mc_behavior_gate_enabled()` - Uses feature flag

#### Score Calculation
- **File**: `products/gcp_v4/modules/care_recommendation/logic.py`
- **Function**: `_calculate_score(answers, module_data)`
- **Lines**: ~800-850
- **What it does**: 
  1. Iterates through all answers
  2. Looks up option in module.json
  3. Sums `option.score` values
  4. Returns `(total_score, details)`

---

### LLM Integration

#### LLM Tier Suggestion
- **File**: `ai/gcp_navi_engine.py`
- **Function**: `get_llm_tier_suggestion(answers, det_tier, allowed_tiers, bands)`
- **Lines**: ~50-250
- **What it receives**:
  - `answers`: Dict of user responses (SAME as used in deterministic)
  - `det_tier`: Deterministic tier result ("assisted_living")
  - `allowed_tiers`: Post-gate allowed tiers (["in_home", "assisted_living"])
  - `bands`: {"cog": "moderate", "sup": "high"}
- **What it returns**: `(llm_tier, confidence)` or `(None, None)` on timeout

#### LLM Client
- **File**: `ai/llm_client.py`
- **Function**: `complete(prompt, model, timeout, temperature)`
- **Lines**: ~30-150
- **What it does**: 
  - Wraps OpenAI API
  - Handles timeout (15s default)
  - Parses JSON responses
  - Returns result or raises TimeoutError

#### LLM Mediator
- **File**: `ai/llm_mediator.py`
- **Function**: `llm_tier_adjudication(...)`
- **Lines**: ~50-200
- **What it does**:
  - Orchestrates LLM request
  - Builds context from answers
  - Constructs prompt
  - Validates response
  - Returns tier or None

#### Hours LLM Engine
- **File**: `ai/hours_engine.py`
- **Functions**: 
  - `generate_hours_advice(answers, det_hours)` - Line ~100
  - `calculate_baseline_hours_weighted(answers)` - Line ~200
- **What it does**:
  - Calculates deterministic hours first
  - Requests LLM hours band suggestion
  - Returns both for comparison

---

### Cost Planner

#### Main Product Entry
- **File**: `products/cost_planner_v2/product.py`
- **Function**: `render_cost_planner()`
- **Lines**: 1-406
- **Workflow Steps**:
  - Line ~50: Intro
  - Line ~100: Auth gate
  - Line ~150: Triage (assessment selection)
  - Line ~200: Financial assessments
  - Line ~300: Expert review
  - Line ~350: Exit

#### Quick Estimate (Cost Calculator)
- **File**: `products/cost_planner_v2/quick_estimate.py`
- **Function**: `render_quick_estimate()`
- **Lines**: ~50-500+
- **What it does**:
  1. Reads `CareRecommendation` from MCIP (line ~100)
  2. Extracts tier and hours_llm_band (line ~120)
  3. Gets ZIP code from user (line ~150)
  4. Looks up regional pricing (line ~180)
  5. Calculates monthly cost (line ~200)
  6. Displays breakdown (line ~250)

#### Cost Calculator Utility
- **File**: `products/cost_planner_v2/utils/cost_calculator.py`
- **Function**: `calculate_monthly_cost(tier, region, hours, modifiers)`
- **Lines**: ~50-200
- **Algorithm**:
  ```python
  if tier == "in_home":
      base = hourly_rate * hours * 30
  else:
      base = region[tier].base_monthly
  
  total = base + modifiers
  total *= region.cost_of_living_multiplier
  ```

#### Regional Pricing Lookup
- **File**: `products/cost_planner_v2/utils/regional_pricing.py`
- **Function**: `get_pricing_for_zip(zip_code)`
- **Lines**: ~20-80
- **Fallback Strategy**:
  1. Exact ZIP match (98001)
  2. Prefix match (900xx → 900)
  3. State match
  4. Default national pricing

#### GCP Integration (Hours Extraction)
- **File**: `products/cost_planner_v2/quick_estimate.py`
- **Lines**: ~100-130
- **Code**:
  ```python
  rec = MCIP.get_care_recommendation()
  if rec and rec.hours_llm_band:
      hours = convert_band_to_hours(rec.hours_llm_band)  # "4-8h" → 6.0
  else:
      hours = default_hours
  ```

---

### MCIP (Master Care Intelligence Panel)

#### Main Coordinator
- **File**: `core/mcip.py`
- **Class**: `MCIP` (singleton)
- **Lines**: 1-1083
- **Key Methods**:
  - `initialize()` - Line ~50
  - `publish_care_recommendation(rec)` - Line ~200
  - `publish_financial_profile(profile)` - Line ~280
  - `get_care_recommendation()` - Line ~350
  - `get_financial_profile()` - Line ~380
  - `mark_product_complete(product_key)` - Line ~450
  - `unlock_product(product_key)` - Line ~500

#### Contract Definitions
- **File**: `core/mcip.py`
- **Dataclasses**:
  - `CareRecommendation` - Line ~100 (15 fields)
  - `FinancialProfile` - Line ~180 (7 fields)
  - `AdvisorAppointment` - Line ~240 (12 fields)

#### Product Key Normalization
- **File**: `core/mcip.py`
- **Lines**: ~550-580
- **Mapping**:
  ```python
  KEY_MAP = {
      "gcp_v4": "gcp",
      "gcp": "gcp",
      "guided_care_plan": "gcp",
      "cost_v2": "cost_planner",
      "cost_planner_v2": "cost_planner",
      "pfma_v3": "pfma"
  }
  ```

#### Journey Management
- **File**: `core/mcip.py`
- **Methods**:
  - `get_completed_products()` - Line ~600
  - `get_unlocked_products()` - Line ~630
  - `_update_unlocked_products(completed_key)` - Line ~680
- **Unlock Rules**:
  ```python
  RULES = {
      "gcp": ["cost_planner"],
      "cost_planner": ["pfma"],
      "pfma": ["partner_connection"]
  }
  ```

---

### JSON Configuration

#### GCP Module Configuration
- **File**: `products/gcp_v4/modules/care_recommendation/module.json`
- **Size**: ~2500 lines
- **Structure**:
  ```json
  {
    "module_id": "care_recommendation",
    "version": "4.0",
    "sections": [
      {
        "section_id": "adls",
        "fields": [
          {
            "field_id": "adl_bathing",
            "type": "radio",
            "options": [
              {"value": "independent", "score": 0, "flags": []},
              {"value": "frequent", "score": 15, "flags": ["adl_assistance"]}
            ]
          }
        ]
      }
    ],
    "tier_thresholds": {
      "independent": {"min": 0, "max": 20},
      "in_home": {"min": 21, "max": 40},
      "assisted_living": {"min": 41, "max": 70},
      "memory_care": {"min": 71, "max": 100}
    }
  }
  ```

#### Regional Pricing Configuration
- **File**: `config/regional_cost_config.json`
- **Size**: ~500 lines
- **Structure**:
  ```json
  {
    "regions": {
      "98001": {
        "region_name": "Seattle Metro",
        "cost_of_living_multiplier": 1.35,
        "assisted_living": {
          "base_monthly": 5500,
          "medical_addon": 800
        },
        "in_home_care": {
          "hourly_rate": 28.50
        }
      }
    },
    "default_region": { /* fallback */ }
  }
  ```

#### Cost Planner Modules
- **File**: `config/cost_planner_v2_modules.json`
- **Size**: ~300 lines
- **What it defines**: Financial assessment module configurations

---

### Feature Flags

#### Flag Registry
- **File**: `core/flags.py`
- **Lines**: 1-200
- **Global Flags**:
  - `FEATURE_LLM_NAVI` - Line ~20 (off/shadow/assist/adjust)
  - `FEATURE_GCP_LLM_TIER` - Line ~40 (off/shadow/replace)
  - `FEATURE_GCP_HOURS` - Line ~60 (off/shadow/assist)
  - `FEATURE_GCP_MC_BEHAVIOR_GATE` - Line ~80 (True/False)

#### Flag Manager
- **File**: `core/flag_manager.py`
- **Function**: `get_flag(flag_name, default)`
- **Lines**: ~30-80
- **Usage**:
  ```python
  from core.flag_manager import get_flag
  
  llm_mode = get_flag("FEATURE_GCP_LLM_TIER", "off")
  if llm_mode == "replace":
      # Use LLM
  ```

---

### State Management

#### Session Store
- **File**: `core/session_store.py`
- **Lines**: 1-300
- **Key Concepts**:
  - `USER_PERSIST_KEYS` - Line ~30 (what to save)
  - `save_state()` - Line ~100
  - `extract_state()` - Line ~150
  - `restore_state()` - Line ~200

#### State Bootstrap
- **File**: `core/state_bootstrap.py`
- **Function**: `initialize_session_state()`
- **Lines**: ~50-200
- **What it does**: Sets up initial session state on app load

---

## 🎯 Quick Lookup Table

| Need to understand... | Look at file | Function/Section | Lines |
|-----------------------|--------------|------------------|-------|
| How answers become scores | `logic.py` | `_calculate_score()` | 800-850 |
| How scores become tiers | `logic.py` | `_determine_tier()` | 850-900 |
| Cognitive gate logic | `logic.py` | `cognitive_gate()` | 900-950 |
| Behavior gate logic | `logic.py` | In `derive_outcome()` | 1170-1185 |
| LLM tier suggestion | `ai/gcp_navi_engine.py` | `get_llm_tier_suggestion()` | 50-250 |
| LLM-first adjudication | `logic.py` | `_choose_final_tier()` | 83-170 |
| Cost calculation | `cost_calculator.py` | `calculate_monthly_cost()` | 50-200 |
| Regional pricing lookup | `regional_pricing.py` | `get_pricing_for_zip()` | 20-80 |
| MCIP publishing | `mcip.py` | `publish_care_recommendation()` | 200-250 |
| Journey unlocking | `mcip.py` | `_update_unlocked_products()` | 680-720 |
| Contract schemas | `mcip.py` | Dataclass definitions | 100-260 |
| Feature flag checking | `flag_manager.py` | `get_flag()` | 30-80 |

---

## 📊 File Sizes Reference

| File | Lines | Complexity |
|------|-------|------------|
| `logic.py` (GCP) | 1966 | High - main orchestration |
| `mcip.py` | 1083 | Medium - coordinator |
| `product.py` (Cost) | 406 | Medium - workflow |
| `gcp_navi_engine.py` | ~300 | Medium - LLM integration |
| `hours_engine.py` | ~400 | Medium - hours calculation |
| `cost_calculator.py` | ~200 | Low - pure calculations |
| `module.json` (GCP) | 2500 | N/A - configuration |
| `regional_cost_config.json` | 500 | N/A - configuration |

---

## 🔗 Dependency Chain

```
User Answers
    ↓
Module Engine (collect answers)
    ↓
logic.py::derive_outcome()
    ├─→ Deterministic (always)
    │   ├─→ _calculate_score()
    │   ├─→ _determine_tier()
    │   ├─→ cognitive_gate()
    │   ├─→ support_band()
    │   ├─→ mc_behavior_gate_enabled()
    │   └─→ det_tier
    │
    ├─→ LLM (if enabled)
    │   ├─→ gcp_navi_engine::get_llm_tier_suggestion()
    │   ├─→ llm_mediator::llm_tier_adjudication()
    │   └─→ llm_client::complete()
    │
    └─→ Adjudication
        ├─→ _choose_final_tier()
        └─→ final_tier

final_tier
    ↓
Build CareRecommendation
    ↓
MCIP::publish_care_recommendation()
    ↓
Cost Planner reads from MCIP
    ↓
Calculate costs
    ↓
MCIP::publish_financial_profile()
```

---

## 💡 Tips for Code Navigation

### Finding Answer Usage
1. Search for `answers.get(` or `answers[` in `logic.py`
2. Look at `_calculate_score()` function (line ~800)
3. Check gate functions (lines 900-1050)

### Following LLM Flow
1. Start at `derive_outcome()` line 1240
2. Follow to `ai/gcp_navi_engine.py`
3. Then to `ai/llm_mediator.py`
4. Finally to `ai/llm_client.py`

### Understanding Gates
1. Cognitive gate: Line ~900 in `logic.py`
2. Behavior gate: Line ~1170 in `logic.py`
3. Gate application: Lines 1140-1185

### Tracing Cost Calculation
1. Start: `products/cost_planner_v2/quick_estimate.py` line ~100
2. Get GCP rec: `MCIP.get_care_recommendation()`
3. Calculate: `utils/cost_calculator.py`
4. Lookup pricing: `utils/regional_pricing.py`

---

**Document Version**: 1.0  
**Companion To**: All other architecture documents  
**Last Updated**: 2025-11-07

**Use this document** when you need to find exact code locations in the prototype.
