# GCP Test Tool - Implementation Summary

## Overview
Created a comprehensive testing tool for the Guided Care Plan (GCP) v4 module that replicates all assessment logic for validation purposes.

## What Was Built

### 1. GCP Test Tool (`products/resources/gcp_test_tool/product.py`)
A complete testing interface that:
- **Replicates ALL GCP v4 sections:**
  - About You (age, living situation, isolation)
  - Medication & Mobility (meds complexity, mobility aid, falls, chronic conditions)
  - Cognition & Mental Health (memory changes, mood, behaviors, diagnosis confirmation)
  - Daily Living (help level, BADLs, IADLs, primary support, hours per day)
  - Move Preferences (willingness to relocate)

- **Uses EXACT GCP logic:**
  - Calls `derive_outcome()` directly from GCP v4 logic module
  - Applies cognitive gates, behavior gates, and scoring
  - Shows tier recommendations with full transparency

- **Provides comprehensive diagnostics:**
  - Tier score and rankings
  - Cognitive gate analysis (pass/fail + reasoning)
  - Behavior gate status (enabled/disabled)
  - Allowed tiers after gates applied
  - Flag activation details
  - Complete rationale breakdown

- **Validation features:**
  - Save test cases to JSON for regression testing
  - Copy results to clipboard
  - Compare against real advisor assessments

## Architecture

### Input Form Structure
```
📋 About You
  - Age range (4 options: <65, 65-74, 75-84, 85+)
  - Living situation (alone, with spouse, with family, AL)
  - Geographic isolation (accessible, somewhat, very)

💊 Medication & Mobility
  - Medication complexity (none, simple, moderate, complex)
  - Mobility level (independent, walker, wheelchair, bedbound)
  - Fall history (none, one, multiple)
  - Chronic conditions (multi-select: 9 options + custom)

🧠 Cognition & Mental Health
  - Memory changes (no concerns, occasional, moderate, severe)
  - Mood (great, mostly good, okay, low)
  - Behaviors (multi-select: 9 risky behaviors)
  - Diagnosis confirmation (only if severe memory changes)

🏠 Daily Living
  - Overall help needed (independent, some, daily, full support)
  - BADLs (multi-select: 7 activities)
  - IADLs (multi-select: 7 activities)
  - Primary support provider (family, paid, community, none)
  - Hours per day (5 bands: <1h, 1-3h, 4-8h, 12-16h, 24h)

🏡 Move Preferences (optional)
  - Willingness to move (1-4 scale)
```

### Results Display Structure
```
📊 GCP Recommendation Results
  ├── 🎯 Primary Recommendation
  │   ├── Recommended tier
  │   ├── Tier score (points)
  │   └── Confidence (%)
  │
  ├── 📈 All Tier Rankings
  │   └── All 5 tiers with scores
  │
  ├── 🚪 Gate Analysis
  │   ├── Cognitive Gate (pass/fail + bands)
  │   └── Behavior Gate (enabled/disabled + risky behaviors)
  │
  ├── 💡 Rationale
  │   └── Human-readable reasoning
  │
  └── 🚩 Flags
      └── All activated flags with messages
```

## Integration Points

### 1. Routing (`config/nav.json`)
```json
{
  "key": "gcp_test_tool",
  "label": "GCP Test Tool",
  "module": "products.resources.gcp_test_tool.product:render",
  "hidden": true
}
```

### 2. Testing Tools Hub (`hubs/testing_tools.py`)
- Added GCP Test Tool tile (order: 5, before Care Hours Calculator)
- Purple variant with "Testing" and "Internal" badges
- Direct route: `?page=gcp_test_tool`

### 3. File Structure
```
products/resources/gcp_test_tool/
├── __init__.py
├── product.py (main implementation)
└── gcp_validation_cases.json (auto-created on first save)
```

## Testing Strategy

### Validation Cases
The tool saves test cases in JSON format:
```json
{
  "timestamp": "2025-11-03T...",
  "inputs": {
    "age_range": "75_84",
    "living_situation": "alone",
    "memory_changes": "moderate",
    ...
  },
  "results": {
    "tier": "assisted_living",
    "tier_score": 22.5,
    "confidence": 0.87,
    "cognitive_gate_pass": true,
    "cognition_band": "moderate",
    "support_band": "high",
    ...
  },
  "notes": "Real case from advisor Sarah..."
}
```

### Use Cases

1. **Validate Tier Logic:**
   - Input known cases
   - Verify tier matches expected recommendation
   - Check gate behavior (cognitive + behavior gates)

2. **Test Edge Cases:**
   - Moderate cognition + high support WITHOUT risky behaviors (behavior gate)
   - Severe memory WITHOUT formal diagnosis (cognitive gate)
   - 24h support scenarios

3. **Compare with Real Assessments:**
   - Use actual client data (de-identified)
   - Compare GCP recommendation vs advisor judgment
   - Identify discrepancies for model tuning

4. **Regression Testing:**
   - Save known-good test cases
   - Re-run after logic changes
   - Ensure no unexpected behavior changes

## Comparison with Care Hours Calculator

| Feature | Care Hours Calculator | GCP Test Tool |
|---------|----------------------|---------------|
| **Scope** | Hours per day only | Complete care tier recommendation |
| **Sections** | 1 (ADLs, cognition, safety) | 5 (about you, medication, cognition, daily living, move preferences) |
| **Gates** | None (pure calculation) | 2 (cognitive gate + behavior gate) |
| **Output** | Band + exact hours | Tier + score + confidence + gates + flags |
| **LLM** | Baseline vs LLM hours | Deterministic vs LLM tier (future) |
| **Complexity** | Medium | High (full GCP replication) |

## Benefits

1. **Rapid Testing:**
   - No need to run full GCP workflow
   - Instant tier calculation (no page flow)
   - Direct input of edge cases

2. **Transparency:**
   - See EXACT score breakdown
   - Understand gate decisions
   - View all tier rankings (not just top choice)

3. **Validation:**
   - Save test cases for regression
   - Compare against real cases
   - Build dataset for model training

4. **Debugging:**
   - Test specific scenarios
   - Isolate gate behavior
   - Verify flag activation

## Access

- **URL:** `?page=gcp_test_tool`
- **Hub:** Testing Tools Hub (`?page=testing_tools`)
- **Header:** Tools link (visible in header)
- **Status:** Internal tool (marked for removal 2025-12-15)

## Next Steps

1. **Validation Phase:**
   - Collect 20-30 real advisor cases
   - Run through GCP Test Tool
   - Compare tier recommendations vs advisor judgment
   - Calculate agreement rate

2. **Edge Case Testing:**
   - Test all gate combinations
   - Verify behavior gate triggers correctly
   - Ensure cognitive gate blocks MC when appropriate

3. **Regression Suite:**
   - Save known-good test cases
   - Automate re-running after changes
   - Set up CI/CD testing

4. **Model Training:**
   - Use saved cases as training data
   - Compare baseline vs LLM tier recommendations
   - Improve LLM adjudication logic

## Implementation Details

### Key Functions

**`_render_input_form()`**
- Renders all 5 GCP sections as expandable panels
- Uses Streamlit widgets matching GCP UI
- Stores inputs in session state with `gcp_*` prefix

**`_calculate_and_store()`**
- Builds answers dict matching GCP v4 structure
- Calls `derive_outcome()` directly (no simulation)
- Extracts gate results using helper functions
- Stores comprehensive results in session state

**`_render_results()`**
- Displays tier recommendation with metrics
- Shows tier rankings for all 5 tiers
- Analyzes gate decisions with pass/fail
- Lists rationale and flags

**`_save_test_case_with_notes()`**
- Saves inputs + results to JSON
- Allows optional notes for context
- Appends to validation_cases.json

### Dependencies
- `products.gcp_v4.modules.care_recommendation.logic` (core GCP logic)
- `ui.header_simple`, `ui.footer_simple` (chrome)
- `core.ui.render_navi_panel_v2` (Navi guidance)
- `core.product_tile` (for hub tile)

## Files Modified

1. **Created:**
   - `products/resources/gcp_test_tool/product.py` (667 lines)
   - `products/resources/gcp_test_tool/__init__.py`

2. **Modified:**
   - `hubs/testing_tools.py` (added GCP test tool tile)
   - `config/nav.json` (added routing entry)

## Summary

The GCP Test Tool is a comprehensive internal testing interface that replicates the complete Guided Care Plan v4 logic for validation and debugging. It provides transparency into tier calculations, gate decisions, and flag activation, making it easy to test edge cases, validate against real assessments, and build regression test suites.

**Status:** ✅ Complete and ready for validation phase
**Access:** Available via Testing Tools Hub or direct URL `?page=gcp_test_tool`
**Removal:** Scheduled for 2025-12-15 after validation complete
