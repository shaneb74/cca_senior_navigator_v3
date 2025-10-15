# Cost Planner V2 - Module Development Guide

## 🎯 Overview

The Cost Planner V2 uses a **JSON-driven module system** that allows you to create new financial assessment modules without writing Python code. All module configuration, fields, validation, and logic are defined in a single JSON file.

## 📂 File Structure

```
config/
  └── cost_planner_v2_modules.json       # Master module configuration (V2)
  └── cost_config.v3.json                # Old Cost Planner config (not used)
products/
  ├── cost_planner/                      # ⚠️ LEGACY - Not actively used
  └── cost_planner_v2/                   # ✅ ACTIVE - Current version
      ├── MODULE_DEVELOPMENT_GUIDE.md    # This guide
      ├── module_renderer.py             # Dynamic renderer (reads JSON)
      ├── product.py                     # Product router
      ├── hub.py                         # Module dashboard
      └── modules/
          ├── income_assets.py           # Legacy hardcoded module
          ├── monthly_costs.py           # Legacy hardcoded module
          └── coverage.py                # Legacy hardcoded module
```

**Important:** Do not confuse this with `products/cost_planner/` (old/unused version).

## 🚀 Quick Start: Adding a New Module

### Example: "Monthly Expenses" Module

This example shows the complete workflow for adding a new financial assessment module.

### Step 1: Define Module in JSON

Edit `config/cost_planner_v2_modules.json` and add your module to the `modules` array:

```json
{
  "key": "monthly_expenses",
  "title": "Monthly Expenses",
  "icon": "💳",
  "description": "Current household expenses and budget",
  "estimated_time": "3-4 min",
  "required": false,
  "sort_order": 4,
  "sections": [
    {
      "id": "housing_costs",
      "title": "Housing Costs",
      "icon": "🏠",
      "help_text": "Include mortgage/rent, property taxes, insurance",
      "layout": "two_column",
      "fields": [
        {
          "key": "monthly_housing",
          "label": "Monthly Housing Cost",
          "type": "currency",
          "min": 0,
          "max": 20000,
          "step": 100,
          "default": 0,
          "help": "Total monthly housing payment",
          "column": 1
        }
        // ... more fields
      ],
      "summary": {
        "type": "calculated",
        "label": "Total Housing",
        "formula": "sum(monthly_housing, property_taxes, hoa_fees)",
        "display_format": "${:,.0f}/mo"
      }
    }
  ],
  "output_contract": {
    "monthly_housing": "number",
    "total_monthly_expenses": "calculated"
  }
}
```

### Step 2: Register Module in Hub

Edit `products/cost_planner_v2/hub.py`:

```python
# Add to session state initialization
st.session_state.cost_v2_modules = {
    "income_assets": {...},
    "monthly_costs": {...},
    "coverage": {...},
    "monthly_expenses": {"status": "not_started", "progress": 0, "data": None}  # NEW
}

# Add module tile
_render_module_tile(
    module_key="monthly_expenses",
    title="💳 Monthly Expenses",
    description="Current household expenses and budget",
    icon="💳",
    estimated_time="3-4 min"
)
```

### Step 3: Update Product Router

Edit `products/cost_planner_v2/product.py`:

The router now automatically detects JSON-defined modules and uses the dynamic renderer. No code changes needed if you follow the JSON structure!

### Step 4: Test Your Module

1. Start the app: `streamlit run app.py`
2. Navigate to Cost Planner V2
3. Click your new module tile
4. Fill out the form
5. Verify data saves correctly

## 📋 Data Contract Reference

### Module Definition

```json
{
  "key": "string",                    // Unique identifier (snake_case)
  "title": "string",                  // Display title
  "icon": "emoji",                    // Icon (emoji or unicode)
  "description": "string",            // Short description (1-2 lines)
  "estimated_time": "string",         // e.g., "3-5 min"
  "required": boolean,                // Is module required?
  "sort_order": number,               // Display order (1, 2, 3...)
  "dependencies": {                   // Optional dependencies
    "requires_gcp": boolean,
    "recommended_gcp": boolean
  },
  "sections": [...],                  // See Section Definition
  "output_contract": {...},           // See Output Contract
  "insights": [...]                   // See Insights
}
```

### Section Definition

```json
{
  "id": "string",                     // Section identifier
  "title": "string",                  // Section header
  "icon": "emoji",                    // Section icon
  "help_text": "string",              // Optional help text
  "layout": "single_column|two_column",  // Layout style
  "visible_if": {...},                // Conditional visibility
  "fields": [...],                    // See Field Definition
  "summary": {...},                   // Optional summary metric
  "info_boxes": [...]                 // Optional info messages
}
```

### Field Definition

```json
{
  "key": "string",                    // Field identifier (snake_case)
  "label": "string",                  // Field label
  "description": "string",            // Optional subtitle
  "type": "currency|text|checkbox|select|slider",
  "required": boolean,
  "min": number,                      // For number/currency/slider
  "max": number,                      // For number/currency/slider
  "step": number,                     // For number/currency/slider
  "default": any,                     // Default value
  "help": "string",                   // Tooltip text
  "placeholder": "string",            // For text inputs
  "options": [...],                   // For select fields
  "column": 1|2,                      // For two-column layouts
  "visible_if": {...},                // Conditional visibility
  "validation": {...},                // Validation rules
  "cost": number,                     // For checkbox fields with cost
  "cost_applies_regional_multiplier": boolean
}
```

### Field Types

| Type | Widget | Use Case |
|------|--------|----------|
| `currency` | Number input | Dollar amounts |
| `text` | Text input | ZIP codes, names |
| `checkbox` | Checkbox | Yes/no questions, opt-in services |
| `select` | Dropdown | Multiple choice (one selection) |
| `slider` | Slider | Ranges (hours, percentages) |
| `display_only` | Read-only metric | Calculated values |
| `calculated` | Auto-calculated | Derived values |

### Select Field Options

```json
"options": [
  {"value": "own_with_mortgage", "label": "Own with mortgage"},
  {"value": "own_outright", "label": "Own outright"},
  {"value": "rent", "label": "Rent"}
]
```

### Visibility Conditions

```json
"visible_if": {
  "field": "housing_type",
  "equals": "own_with_mortgage"
}

// OR

"visible_if": {
  "field": "has_ltc_insurance",
  "not_equals": false
}

// OR (for sections)

"visible_if": {
  "condition": "gcp_tier == 'in_home'"
}
```

### Summary Metrics

```json
"summary": {
  "type": "calculated",
  "label": "Total Housing",
  "formula": "sum(monthly_housing, property_taxes, hoa_fees)",
  "display_format": "${:,.0f}/mo"
}
```

### Output Contract

Defines what data the module returns:

```json
"output_contract": {
  "monthly_housing": "number",        // Direct field value
  "property_taxes": "number",
  "total_housing": "calculated",      // Calculated value
  "housing_type": "string",
  "has_mortgage": "boolean",
  "services": "object"                // Complex object
}
```

### Insights (Conditional Messages)

```json
"insights": [
  {
    "condition": "total_monthly_expenses > total_monthly_income",
    "type": "warning",
    "message": "⚠️ **Budget Alert:** Your expenses exceed income."
  },
  {
    "condition": "total_assets > 100000",
    "type": "success",
    "message": "✅ **Strong Position:** You have ${total_assets:,.0f} in assets."
  }
]
```

### Info Boxes (Section-Level)

```json
"info_boxes": [
  {
    "type": "success|info|warning|error",
    "visible_if": {
      "field": "is_veteran",
      "equals": true
    },
    "content": "### ✅ You may be eligible!\n\nBenefits available..."
  }
]
```

## 🎨 Styling & Formatting

### Display Formats

```json
"display_format": "${:,.0f}"      // $1,234
"display_format": "${:,.2f}"      // $1,234.56
"display_format": "{:,.0f}"       // 1,234
"display_format": "{:+.0%}"       // +25%
"display_format": "$/mo"          // Custom text
```

### Layout Options

```json
"layout": "single_column"         // Stack fields vertically
"layout": "two_column"            // Split into two columns
"columns": 2                      // Auto-distribute across 2 columns
```

## 🔧 Advanced Features

### Conditional Calculations

For complex calculations, add logic to `module_renderer.py`:

```python
def _calculate_outputs(module_def, data):
    # ... existing code ...
    
    if "total_monthly_expenses" == key:
        output[key] = sum([
            data.get("monthly_housing", 0),
            data.get("utilities", 0),
            # ... all expense fields
        ])
```

### Regional Multipliers

For fields that vary by region:

```json
{
  "key": "service_transportation",
  "type": "checkbox",
  "cost": 200,
  "cost_applies_regional_multiplier": true
}
```

The cost will automatically adjust: `$200 * regional_multiplier`

### Data Lookups

For fields that lookup values from config:

```json
{
  "key": "va_monthly_benefit",
  "type": "calculated",
  "source": "va_benefit_lookup"
}
```

Add lookup logic to `_calculate_field_value()` in `module_renderer.py`.

## 📊 Testing Your Module

### Checklist

- [ ] Module appears in hub dashboard
- [ ] All fields render correctly
- [ ] Labels are clear and visible
- [ ] Help tooltips work
- [ ] Visibility conditions work
- [ ] Summary calculations correct
- [ ] Navigation buttons work
- [ ] Data saves to session state
- [ ] Module shows as "completed"
- [ ] Data passes to Expert Review

### Debug Tips

1. **Module not showing?**
   - Check JSON syntax
   - Verify `sort_order` is unique
   - Check session state initialization

2. **Fields not rendering?**
   - Verify field `type` is supported
   - Check `visible_if` conditions
   - Look for JSON syntax errors

3. **Calculations wrong?**
   - Check `output_contract`
   - Add debug logging to `_calculate_outputs()`
   - Verify field keys match exactly

## 🎓 Learning Path

### Beginner
1. Start with simple module (3-5 fields)
2. Use basic field types (`currency`, `text`, `checkbox`)
3. Add one section with a summary

### Intermediate
4. Add conditional visibility
5. Use two-column layouts
6. Add insights based on data

### Advanced
7. Custom calculations
8. Complex conditional logic
9. Regional multipliers
10. Data lookups

## 📚 Example Modules

### Simple Module: Emergency Fund

```json
{
  "key": "emergency_fund",
  "title": "Emergency Fund",
  "icon": "🆘",
  "sections": [{
    "id": "savings",
    "title": "Emergency Savings",
    "fields": [{
      "key": "emergency_fund_amount",
      "label": "Emergency Fund Balance",
      "type": "currency",
      "default": 0
    }]
  }],
  "output_contract": {
    "emergency_fund_amount": "number"
  }
}
```

### Complex Module: Debt Analysis

```json
{
  "key": "debt_analysis",
  "title": "Debt Analysis",
  "icon": "💳",
  "sections": [
    {
      "id": "credit_cards",
      "title": "Credit Card Debt",
      "layout": "two_column",
      "fields": [
        {"key": "cc_balance", "type": "currency", "column": 1},
        {"key": "cc_min_payment", "type": "currency", "column": 1},
        {"key": "cc_interest_rate", "type": "slider", "min": 0, "max": 30, "column": 2}
      ]
    }
  ]
}
```

## 🚨 Common Pitfalls

1. **Missing quotes in JSON** - Use a JSON validator
2. **Incorrect field keys** - Must match exactly in calculations
3. **Forgetting to add to session state** - Module won't initialize
4. **Wrong visibility condition syntax** - Check examples
5. **Not updating hub tile** - Module won't appear

## 🤝 Contributing

When creating new modules:

1. Follow naming conventions (snake_case)
2. Add help text to all complex fields
3. Test all visibility conditions
4. Document any custom calculations
5. Update this guide with examples

## 📞 Support

Questions? Check:
- This guide (you're reading it!)
- `module_renderer.py` source code
- Existing module examples in JSON
- Copilot instructions file

---

**Last Updated:** October 2025
**Version:** 2.0.0
