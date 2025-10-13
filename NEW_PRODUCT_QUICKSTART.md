# New Product Quick-Start Guide

**How to create a new MCIP product using the extensible module framework**

---

## Prerequisites

✅ You've read `EXTENSIBILITY_AUDIT.md`  
✅ You understand the GCP care_recommendation module structure  
✅ You have a clear product concept with:
- Step-by-step workflow (intro, questions, results)
- Outcome logic (what gets calculated/recommended)
- Flag triggers (what additional services should appear)

---

## 5-Step Process

### Step 1: Create Product Directory Structure

```bash
mkdir -p products/YOUR_PRODUCT_NAME
touch products/YOUR_PRODUCT_NAME/product.py
touch products/YOUR_PRODUCT_NAME/module_config.py
touch products/YOUR_PRODUCT_NAME/module_config.json
touch products/YOUR_PRODUCT_NAME/logic.py
```

**Example for Cost Planner:**
```
products/cost_planner/
├── product.py           # Entry point
├── module_config.py     # Config loader
├── module_config.json   # Steps/fields definition
└── logic.py             # Outcomes calculation
```

---

### Step 2: Implement `product.py` (Entry Point)

**Template:**
```python
# products/YOUR_PRODUCT_NAME/product.py
from core.modules.engine import run_module
from products.YOUR_PRODUCT_NAME.module_config import get_config
from layout import render_shell_end, render_shell_start


def render() -> None:
    """Render YOUR_PRODUCT_NAME using the module engine."""
    config = get_config()
    
    render_shell_start("", active_route="YOUR_ROUTE_KEY")
    
    # Run the module with the engine
    module_state = run_module(config)
    
    render_shell_end()
```

**Real Example (Cost Planner):**
```python
# products/cost_planner/product.py
from core.modules.engine import run_module
from products.cost_planner.module_config import get_config
from layout import render_shell_end, render_shell_start


def render() -> None:
    """Render Cost Planner using the module engine."""
    config = get_config()
    
    render_shell_start("", active_route="cost")
    
    module_state = run_module(config)
    
    render_shell_end()
```

---

### Step 3: Define `module_config.json` (Steps & Fields)

**Structure:**
```json
{
  "product": "YOUR_PRODUCT_KEY",
  "state_key": "YOUR_STATE_KEY",
  "version": "2025.10.1",
  "steps": [
    {
      "id": "intro",
      "title": "Your Product Title",
      "subtitle": "Brief description\n\nMore details here.",
      "fields": [],
      "show_progress": false,
      "next_label": "Get Started"
    },
    {
      "id": "step_1",
      "title": "Step 1 Title",
      "subtitle": "Instructions for this step",
      "fields": [
        {
          "key": "field_1",
          "label": "Question Text",
          "type": "radio",
          "required": true,
          "options": [
            {"label": "Option 1", "value": "opt1"},
            {"label": "Option 2", "value": "opt2"}
          ]
        },
        {
          "key": "field_2",
          "label": "Another Question",
          "type": "number",
          "required": true,
          "min": 0,
          "max": 100000,
          "help": "Enter whole dollar amount"
        }
      ],
      "show_progress": true
    },
    {
      "id": "results",
      "title": "Your Results",
      "subtitle": "Here's what we found:",
      "fields": [],
      "show_progress": true
    }
  ],
  "results_step_id": "results"
}
```

**Field Types Available:**
- `radio` - Single choice (rendered as pills)
- `multiselect` - Multiple choices (checkboxes)
- `number` - Numeric input
- `text` - Short text input
- `textarea` - Long text input
- `slider` - Range slider
- `date` - Date picker

**Field Properties:**
- `key` - State key (where value is stored)
- `label` - Question text displayed to user
- `type` - Field type (see above)
- `required` - Boolean (blocks Continue if empty)
- `help` - Helper text below field
- `options` - Array of choices (for radio/multiselect)
- `min`, `max`, `step` - Numeric constraints
- `default` - Default value
- `visible_if` - Conditional visibility (e.g., `{"key": "other_field", "eq": "some_value"}`)
- `write_key` - Alternate state key (if different from `key`)

---

### Step 4: Implement `module_config.py` (Config Loader)

**Template:**
```python
# products/YOUR_PRODUCT_NAME/module_config.py
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from core.modules.schema import FieldDef, ModuleConfig, StepDef


def _build_field(data: Dict[str, Any]) -> FieldDef:
    """Convert JSON field definition to FieldDef schema."""
    return FieldDef(
        key=data["key"],
        label=data["label"],
        type=data["type"],
        help=data.get("help"),
        required=data.get("required", False),
        options=data.get("options"),
        min=data.get("min"),
        max=data.get("max"),
        step=data.get("step"),
        placeholder=data.get("placeholder"),
        default=data.get("default"),
        visible_if=data.get("visible_if"),
        write_key=data.get("write_key"),
    )


@lru_cache(maxsize=1)
def _load_config_payload() -> Dict[str, Any]:
    """Load module_config.json from disk."""
    path = Path(__file__).with_name("module_config.json")
    with path.open() as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def get_config() -> ModuleConfig:
    """Load YOUR_PRODUCT_NAME module configuration."""
    payload = _load_config_payload()
    
    steps: List[StepDef] = []
    for step_data in payload.get("steps", []):
        fields = [_build_field(f) for f in step_data.get("fields", [])]
        steps.append(
            StepDef(
                id=step_data["id"],
                title=step_data["title"],
                subtitle=step_data.get("subtitle"),
                fields=fields,
                show_progress=step_data.get("show_progress", True),
                next_label=step_data.get("next_label", "Continue"),
                skip_label=step_data.get("skip_label"),
            )
        )
    
    return ModuleConfig(
        product=payload["product"],
        state_key=payload["state_key"],
        version=payload["version"],
        steps=steps,
        results_step_id=payload.get("results_step_id"),
        outcomes_compute=f"products.YOUR_PRODUCT_NAME.logic:derive_outcomes",
    )
```

**Change `YOUR_PRODUCT_NAME` to your actual product folder name.**

---

### Step 5: Implement `logic.py` (Outcomes Calculation)

**Template:**
```python
# products/YOUR_PRODUCT_NAME/logic.py
from typing import Any, Dict
from core.modules.schema import OutcomeContract


def derive_outcomes(*, answers: Dict[str, Any], context: Dict[str, Any]) -> OutcomeContract:
    """Calculate outcomes from user answers.
    
    Args:
        answers: All user responses (from module state)
        context: Product context (product name, version, user info)
    
    Returns:
        OutcomeContract with recommendation, flags, scores
    """
    
    # 1. Extract key answers
    field_1 = answers.get("field_1")
    field_2 = answers.get("field_2", 0)
    
    # 2. Calculate your logic
    score = 0
    if field_1 == "high_risk":
        score += 10
    if field_2 > 50000:
        score += 5
    
    # 3. Determine recommendation tier
    if score >= 10:
        recommendation = "high_priority"
        flags = {"urgent_action_needed": True, "advisor_followup": True}
    elif score >= 5:
        recommendation = "medium_priority"
        flags = {"followup_recommended": True}
    else:
        recommendation = "low_priority"
        flags = {}
    
    # 4. Return OutcomeContract
    return OutcomeContract(
        recommendation=recommendation,
        flags=flags,
        domain_scores={
            "risk_score": score,
            "field_2_value": field_2,
        },
        tags=["completed", "calculated"],
        audit={
            "version": context.get("version"),
            "calculated_by": "YOUR_PRODUCT_NAME.logic",
        },
    )
```

**Real Example (Simplified Cost Planner):**
```python
# products/cost_planner/logic.py
from typing import Any, Dict
from core.modules.schema import OutcomeContract


def derive_outcomes(*, answers: Dict[str, Any], context: Dict[str, Any]) -> OutcomeContract:
    """Calculate care affordability from income, assets, and costs."""
    
    # Extract financial data
    monthly_income = float(answers.get("monthly_income", 0))
    ss_benefits = float(answers.get("ss_benefits", 0))
    pension = float(answers.get("pension", 0))
    
    total_income = monthly_income + ss_benefits + pension
    
    monthly_care_cost = float(answers.get("monthly_care_cost", 0))
    liquid_assets = float(answers.get("liquid_assets", 0))
    
    # Calculate deficit and depletion timeline
    monthly_deficit = max(0, monthly_care_cost - total_income)
    
    if monthly_deficit == 0:
        months_until_depletion = 999  # Sustainable indefinitely
    else:
        months_until_depletion = liquid_assets / monthly_deficit if monthly_deficit > 0 else 0
    
    # Determine tier
    if months_until_depletion > 60:
        recommendation = "affordable"
        flags = {}
    elif months_until_depletion > 24:
        recommendation = "at_risk"
        flags = {"financial_planning_needed": True}
    else:
        recommendation = "unsustainable"
        flags = {
            "urgent_financial_planning": True,
            "va_benefits_check": True,
            "medicaid_eligible_check": True,
        }
    
    return OutcomeContract(
        recommendation=recommendation,
        flags=flags,
        domain_scores={
            "total_income": total_income,
            "monthly_care_cost": monthly_care_cost,
            "monthly_deficit": monthly_deficit,
            "months_until_depletion": months_until_depletion,
        },
        tags=["cost_calculated", "affordability_assessed"],
        audit={
            "version": context.get("version"),
            "calculated_by": "cost_planner.logic",
        },
    )
```

---

## Step 6: Register in Navigation

**Edit `config/nav.json`:**
```json
{
  "groups": [
    {
      "label": "Care Products",
      "items": [
        {
          "key": "gcp",
          "label": "Guided Care Plan",
          "module": "products.gcp.product:render"
        },
        {
          "key": "YOUR_ROUTE_KEY",
          "label": "Your Product Name",
          "module": "products.YOUR_PRODUCT_NAME.product:render"
        }
      ]
    }
  ]
}
```

---

## Step 7: Add Product Tile to Hub (Optional)

**Edit `hubs/concierge.py` (temporary hardcoded approach):**
```python
# Add progress tracking
your_product_prog = float(st.session_state.get("YOUR_STATE_KEY", {}).get("progress", 0))

# Add tile rendering
ProductTile(
    key="YOUR_PRODUCT_KEY",
    title="Your Product Name",
    desc="Brief description of what this product does",
    meta=["≈5 min", "Auto-saves"],
    cta="Start",
    go="YOUR_ROUTE_KEY",
    progress=your_product_prog,
).render()
```

**Future: Use dynamic tile registry (see EXTENSIBILITY_AUDIT.md for enhancement pattern).**

---

## Step 8: Add Additional Service Tiles (Optional)

**Edit `core/additional_services.py`:**
```python
REGISTRY: List[Tile] = [
    # ... existing tiles
    {
        "key": "your_service",
        "type": "partner",
        "title": "Your Partner Service",
        "subtitle": "Triggered by your product flags",
        "cta": "Learn more",
        "go": "partner_your_service",
        "order": 10,
        "hubs": ["concierge"],
        "visible_when": [
            {"includes": {"path": "flags", "value": "your_flag_from_logic"}},
        ],
    },
]
```

**How it works:**
- When your `logic.py` sets `flags = {"your_flag_from_logic": True}`
- Engine writes this to `st.session_state["handoff"]["YOUR_STATE_KEY"]["flags"]`
- Additional services aggregates ALL product flags
- Tiles with matching `visible_when` rules appear automatically

---

## Testing Checklist

### ✅ Module Functionality
- [ ] Intro page loads without errors
- [ ] Progress bar shows correctly (0% → 100%)
- [ ] All fields render with correct types
- [ ] Required fields block Continue when empty
- [ ] Save & Continue Later returns to hub
- [ ] Resume functionality restores correct step
- [ ] Results page shows after last step
- [ ] Outcomes are calculated correctly
- [ ] Flags are set in handoff

### ✅ Integration
- [ ] Product tile appears in hub
- [ ] Progress updates in real-time
- [ ] Completion status updates tile badge
- [ ] Additional service tiles appear based on flags
- [ ] Navigation to/from product works

### ✅ Edge Cases
- [ ] Refresh mid-module resumes correctly
- [ ] Browser back button works
- [ ] Multiple products don't interfere with each other
- [ ] Flag aggregation includes all products

---

## Pro Tips

### 1. **Start Simple**
Begin with 3 steps: intro, one question step, results. Get that working, then add more steps.

### 2. **Clone GCP Structure**
The fastest way to start:
```bash
cp -r products/gcp products/YOUR_PRODUCT_NAME
# Then modify the files
```

### 3. **Use `show_progress: false` for Intro/Results**
Only question steps should contribute to progress bar.

### 4. **Test Flags Early**
Add a simple flag in `logic.py` and verify it appears in:
- `st.session_state["handoff"]["YOUR_STATE_KEY"]["flags"]`
- Additional services context aggregation

### 5. **Debug with Session State**
Add to your intro page:
```python
with st.expander("🔧 Debug State"):
    st.json(st.session_state.get("YOUR_STATE_KEY", {}))
```

### 6. **Leverage Existing Field Types**
Look at `products/gcp/module_config.json` for examples of:
- Radio pills with icons
- Conditional fields (`visible_if`)
- Multi-select with effects (flag triggers)
- Number inputs with validation

---

## Common Patterns

### Pattern 1: Conditional Questions
```json
{
  "key": "has_va_service",
  "label": "Served in the military?",
  "type": "radio",
  "required": true,
  "options": [
    {"label": "Yes", "value": "yes"},
    {"label": "No", "value": "no"}
  ]
},
{
  "key": "va_service_years",
  "label": "Years of service",
  "type": "number",
  "required": true,
  "visible_if": {"key": "has_va_service", "eq": "yes"}
}
```

### Pattern 2: Multi-Select with Flag Effects
```json
{
  "key": "risk_factors",
  "label": "Select all that apply:",
  "type": "multiselect",
  "options": [
    {"label": "High fall risk", "value": "fall_risk"},
    {"label": "Memory issues", "value": "memory"},
    {"label": "Medication complexity", "value": "meds"}
  ],
  "effects": [
    {
      "when_value_in": ["fall_risk"],
      "set_flag": "fall_prevention_needed",
      "flag_message": "Fall prevention assessment recommended"
    },
    {
      "when_value_in": ["memory"],
      "set_flag": "cognitive_assessment_needed"
    }
  ]
}
```

### Pattern 3: Summary Bar (Dev Info)
```json
{
  "id": "step_1",
  "title": "Financial Info",
  "show_bottom_bar": true,
  "summary_keys": ["monthly_income", "liquid_assets"],
  "fields": [...]
}
```

---

## Troubleshooting

### Issue: Module doesn't load
- **Check:** `module_config.json` has valid JSON syntax
- **Check:** All required fields in StepDef are present
- **Check:** `outcomes_compute` path is correct

### Issue: Progress bar stuck at 0%
- **Check:** Steps have `"show_progress": true` (except intro/results)
- **Check:** At least one field is marked `"required": true`

### Issue: Outcomes not calculated
- **Check:** `results_step_id` matches a step's `id`
- **Check:** `logic.py:derive_outcomes()` function signature matches template
- **Check:** Function returns `OutcomeContract` (not dict)

### Issue: Flags don't trigger services
- **Check:** Flag key in `logic.py` matches `visible_when` rule
- **Check:** `handoff` contains your product's flags: `st.session_state["handoff"]["YOUR_STATE_KEY"]`
- **Check:** Additional service context is aggregating flags from all products

### Issue: Save & Continue Later doesn't resume
- **Check:** Tile state is being updated: `st.session_state["tiles"]["YOUR_PRODUCT_KEY"]`
- **Check:** `config.product` matches tile key

---

## Next Steps

1. **Build Cost Planner** - Follow this guide to create the 8-module Cost Planner
2. **Enhance Hub Tiles** - Implement dynamic tile registry pattern (see EXTENSIBILITY_AUDIT.md)
3. **Add Product Orchestration** - For multi-module products, add aggregation layer
4. **Create PFMA** - Personal Functional & Medical Assessment using same pattern

---

**Questions?** Reference:
- `EXTENSIBILITY_AUDIT.md` - Architecture deep-dive
- `products/gcp/` - Working reference implementation
- `core/modules/schema.py` - Data contract definitions
- `core/modules/engine.py` - Engine source code

**Happy building! 🚀**
