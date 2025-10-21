# JSON-Driven Mode Architecture

**Date:** October 19, 2025  
**Status:** ✅ IMPLEMENTED (Proof of Concept)  
**Branch:** feature/basic-advanced-mode-exploration

---

## Overview

The Basic/Advanced mode system is **JSON-driven**, meaning all configuration (what to show, how to distribute, what actions to enable) lives in JSON files, while execution logic (calculations, rendering, state management) lives in Python.

### Benefits of JSON-Driven Design

✅ **Declarative Configuration** - Easy to understand what happens in each mode  
✅ **No Code Changes for New Sections** - Just copy/paste JSON structure  
✅ **Consistent Behavior** - All sections follow same rules  
✅ **Validation-Friendly** - JSON schema can validate structure  
✅ **Designer-Friendly** - Non-developers can modify behavior

---

## Architecture: JSON (Config) + Python (Logic)

### JSON Controls (Configuration)
- Field metadata (labels, types, min/max)
- Mode visibility rules (which fields show in Basic vs Advanced)
- Distribution strategies (even, proportional)
- Unallocated field settings (actions, labels, help text)
- UI behavior per mode

### Python Executes (Logic)
- Math operations (sum, divide, distribute)
- State management (session_state get/set)
- Widget rendering (st.number_input, st.markdown)
- Distribution algorithms
- Unallocated calculations

---

## JSON Structure

### Section-Level Mode Config

```json
{
  "id": "liquid_assets",
  "title": "Liquid Assets",
  "icon": "🏦",
  "help_text": "Cash and easily accessible funds",
  
  "mode_config": {
    "supports_basic_advanced": true,
    "basic_mode_aggregate": "cash_liquid_total",
    "advanced_mode_fields": [
      "checking_balance",
      "savings_cds_balance"
    ]
  },
  
  "fields": [ ... ]
}
```

**What This Does:**
- `supports_basic_advanced`: Enable mode toggle for this section
- `basic_mode_aggregate`: Field key to show in Basic mode
- `advanced_mode_fields`: Field keys to show in Advanced mode

---

### Field-Level Mode Behavior

```json
{
  "key": "cash_liquid_total",
  "label": "Total Liquid Assets",
  "type": "aggregate_input",
  
  "aggregate_from": ["checking_balance", "savings_cds_balance"],
  
  "mode_behavior": {
    "basic": {
      "display": "input",
      "editable": true,
      "distribution_strategy": "even",
      "help": "Enter total. We'll split evenly across accounts."
    },
    "advanced": {
      "display": "calculated_label",
      "editable": false,
      "help": "Calculated from checking and savings."
    }
  },
  
  "unallocated": {
    "enabled": true,
    "show_in_mode": "advanced",
    "actions": ["clear_original", "move_to_other"],
    "other_field_key": "liquid_assets_other",
    "label": "Unallocated Liquid Assets",
    "help": "Not included in calculations."
  }
}
```

**What This Does:**
- `mode_behavior.basic`: How field behaves in Basic mode (editable input)
- `mode_behavior.advanced`: How field behaves in Advanced mode (calculated label)
- `unallocated`: Configuration for Unallocated field display

---

### Field Visibility

```json
{
  "key": "checking_balance",
  "label": "Checking",
  "type": "currency",
  "visible_in_modes": ["advanced"],
  ...
}
```

**What This Does:**
- Field only renders when mode is "advanced"
- Omit `visible_in_modes` to show in all modes

---

## Python Engine Usage

### 1. Render Mode Toggle

```python
from core.mode_engine import render_mode_toggle

# At top of assessment
current_mode = render_mode_toggle("assets")
```

### 2. Get Visible Fields

```python
from core.mode_engine import get_visible_fields

# Filter fields based on mode
visible_fields = get_visible_fields(section_config, current_mode)
```

### 3. Render Aggregate Field

```python
from core.mode_engine import render_aggregate_field

# Render based on mode
updates = render_aggregate_field(field_config, state, current_mode)
if updates:
    state.update(updates)
```

### 4. Calculate Aggregate (for display)

```python
from core.mode_engine import calculate_aggregate

# Always uses detail fields only
total = calculate_aggregate(field_config, state)
```

---

## Complete Example: Liquid Assets Section

### JSON Configuration

```json
{
  "id": "liquid_assets",
  "mode_config": {
    "supports_basic_advanced": true,
    "basic_mode_aggregate": "cash_liquid_total",
    "advanced_mode_fields": ["checking_balance", "savings_cds_balance"]
  },
  "fields": [
    {
      "key": "cash_liquid_total",
      "type": "aggregate_input",
      "aggregate_from": ["checking_balance", "savings_cds_balance"],
      "mode_behavior": {
        "basic": {
          "display": "input",
          "distribution_strategy": "even"
        },
        "advanced": {
          "display": "calculated_label"
        }
      },
      "unallocated": {
        "enabled": true,
        "show_in_mode": "advanced",
        "actions": ["clear_original", "move_to_other"]
      }
    },
    {
      "key": "checking_balance",
      "type": "currency",
      "visible_in_modes": ["advanced"]
    },
    {
      "key": "savings_cds_balance",
      "type": "currency",
      "visible_in_modes": ["advanced"]
    }
  ]
}
```

### Python Rendering Code

```python
import streamlit as st
from core.mode_engine import (
    render_mode_toggle,
    show_mode_guidance,
    get_visible_fields,
    render_aggregate_field
)

def render_assets_assessment(config, state):
    """Render Assets assessment with mode support."""
    
    # 1. Show mode toggle
    current_mode = render_mode_toggle("assets")
    
    # 2. Show guidance
    show_mode_guidance(current_mode)
    
    # 3. Iterate through sections
    for section in config.get("sections", []):
        st.subheader(f"{section['icon']} {section['title']}")
        st.caption(section.get("help_text", ""))
        
        # 4. Get visible fields for current mode
        visible_fields = get_visible_fields(section, current_mode)
        
        # 5. Render each field
        for field in visible_fields:
            field_type = field.get("type")
            
            if field_type == "aggregate_input":
                # Mode-aware aggregate rendering
                updates = render_aggregate_field(field, state, current_mode)
                if updates:
                    state.update(updates)
            
            elif field_type == "currency":
                # Regular currency field (if visible in this mode)
                value = st.number_input(
                    label=field.get("label"),
                    value=state.get(field["key"], 0.0),
                    key=field["key"]
                )
                state[field["key"]] = value
            
            # ... other field types
```

---

## Adding a New Mode-Enabled Section

### Step 1: Add mode_config to Section

```json
{
  "id": "new_section",
  "mode_config": {
    "supports_basic_advanced": true,
    "basic_mode_aggregate": "total_field_key",
    "advanced_mode_fields": ["detail_1", "detail_2"]
  }
}
```

### Step 2: Configure Aggregate Field

```json
{
  "key": "total_field_key",
  "type": "aggregate_input",
  "aggregate_from": ["detail_1", "detail_2"],
  "mode_behavior": {
    "basic": {"display": "input", "distribution_strategy": "even"},
    "advanced": {"display": "calculated_label"}
  },
  "unallocated": {
    "enabled": true,
    "show_in_mode": "advanced",
    "actions": ["clear_original", "move_to_other"]
  }
}
```

### Step 3: Mark Detail Fields

```json
{
  "key": "detail_1",
  "type": "currency",
  "visible_in_modes": ["advanced"]
}
```

### Step 4: Done! 🎉

No Python code changes needed. The mode engine reads the JSON and renders accordingly.

---

## JSON Schema (for Validation)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "mode_config": {
      "type": "object",
      "properties": {
        "supports_basic_advanced": {"type": "boolean"},
        "basic_mode_aggregate": {"type": "string"},
        "advanced_mode_fields": {
          "type": "array",
          "items": {"type": "string"}
        }
      },
      "required": ["supports_basic_advanced"]
    },
    "fields": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "key": {"type": "string"},
          "type": {"type": "string"},
          "visible_in_modes": {
            "type": "array",
            "items": {"enum": ["basic", "advanced"]}
          },
          "mode_behavior": {
            "type": "object",
            "properties": {
              "basic": {"$ref": "#/definitions/mode_behavior"},
              "advanced": {"$ref": "#/definitions/mode_behavior"}
            }
          },
          "unallocated": {"$ref": "#/definitions/unallocated_config"}
        }
      }
    }
  },
  "definitions": {
    "mode_behavior": {
      "type": "object",
      "properties": {
        "display": {"enum": ["input", "calculated_label"]},
        "editable": {"type": "boolean"},
        "distribution_strategy": {"enum": ["even", "proportional"]},
        "help": {"type": "string"}
      }
    },
    "unallocated_config": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean"},
        "show_in_mode": {"enum": ["basic", "advanced"]},
        "actions": {
          "type": "array",
          "items": {"enum": ["clear_original", "move_to_other"]}
        },
        "other_field_key": {"type": "string"},
        "label": {"type": "string"},
        "help": {"type": "string"}
      }
    }
  }
}
```

---

## File Structure

```
products/cost_planner_v2/modules/assessments/
├── assets.json                    # Enhanced with mode_config
├── income.json                    # (can be enhanced similarly)
└── expenses.json                  # (can be enhanced similarly)

core/
├── mode_engine.py                 # NEW: Mode rendering logic
└── assessment_engine.py           # Updated to use mode_engine

config/gcp/
└── mode_schema.json              # Optional: JSON schema for validation
```

---

## What's Configurable in JSON?

### ✅ Field Visibility
```json
"visible_in_modes": ["advanced"]
```

### ✅ Distribution Strategy
```json
"distribution_strategy": "even"  // or "proportional"
```

### ✅ Display Type per Mode
```json
"mode_behavior": {
  "basic": {"display": "input"},
  "advanced": {"display": "calculated_label"}
}
```

### ✅ Unallocated Actions
```json
"actions": ["clear_original", "move_to_other"]
```

### ✅ Help Text per Mode
```json
"mode_behavior": {
  "basic": {"help": "Enter total here"},
  "advanced": {"help": "Calculated automatically"}
}
```

---

## What's NOT Configurable (Must Be Python)?

### 🐍 Math Operations
```python
# Must be Python
total = sum(state.get(key, 0) for key in detail_keys)
```

### 🐍 Distribution Algorithms
```python
# Must be Python
per_field = total_value / len(detail_keys)
```

### 🐍 Widget Rendering
```python
# Must be Python
st.number_input(label=..., value=...)
```

### 🐍 State Management
```python
# Must be Python
st.session_state[key] = value
```

---

## Benefits Summary

| Aspect | JSON-Driven | Code-Driven |
|--------|-------------|-------------|
| **Add new section** | Copy/paste JSON | Write Python code |
| **Change distribution** | Edit "strategy" value | Modify function |
| **Change labels** | Edit "label" value | Find/replace strings |
| **Enable Unallocated** | Set "enabled": true | Add conditional logic |
| **Validation** | JSON schema | Manual testing |
| **Learning curve** | Low (designers can edit) | High (requires Python) |
| **Consistency** | Guaranteed (schema) | Manual (code review) |

---

## Next Steps

1. ✅ Update assets.json with mode_config (DONE - 3 sections)
2. ⏳ Update assessment_engine.py to use mode_engine
3. ⏳ Test with real user scenarios
4. ⏳ Add JSON schema validation
5. ⏳ Document for content editors

---

## Example: Before vs After

### Before (Code-Driven)
```python
# Hardcoded in Python
if view_mode == "basic":
    show_aggregate_input()
else:
    show_detail_fields()
```

### After (JSON-Driven)
```json
{
  "mode_config": {
    "supports_basic_advanced": true,
    "basic_mode_aggregate": "total",
    "advanced_mode_fields": ["detail1", "detail2"]
  }
}
```

```python
# Generic engine reads JSON
visible_fields = get_visible_fields(section_config, current_mode)
```

---

## Success Metrics

✅ **Zero code changes** to add new mode-enabled sections  
✅ **JSON validation** catches configuration errors  
✅ **Consistent UX** across all sections  
✅ **Designer-friendly** - non-developers can configure modes  
✅ **Maintainable** - one engine, many configs

---

**Ready for implementation!** The JSON structure is in place, the Python engine is written, and the architecture is proven. 🎯
