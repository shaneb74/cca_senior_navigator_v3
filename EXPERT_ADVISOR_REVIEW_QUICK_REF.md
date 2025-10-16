# Expert Advisor Review - Quick Reference

## What Changed?

### Before (Old Design)
- ⚠️ Yellow warning banners for incomplete modules
- ℹ️ Blue info banners for context
- ✅ Green success banners for completed items
- Multiple visual styles competing for attention
- Cluttered layout with mixed messaging

### After (New Design)
- ✨ Single Navi panel with warm, confident guidance
- 📊 Clean 2-column module completion grid
- 💼 Scannable 4-metric executive summary
- 📈 Minimal tab styling for detailed breakdown
- Unified card-based layout (no visual noise)

---

## File Locations

```
products/cost_planner_v2/
├── expert_review.py              ← REDESIGNED (active)
├── expert_review_old.py          ← BACKUP (original)
└── expert_review_redesigned.py   ← SOURCE (before replacement)

assets/css/
└── modules.css                   ← UPDATED (new CSS added at top)
```

---

## CSS Classes Added

```css
/* Section cards */
.section-card

/* Module status items */
.module-status-item
.module-status-item.completed
.module-status-item.optional
.module-status-item.incomplete

/* Module components */
.module-icon
.module-label
.module-status

/* Metrics & tabs */
.section-card [data-testid="stMetricValue"]
.section-card [data-baseweb="tab"]
.section-card [data-baseweb="tab"][aria-selected="true"]

/* Text area */
.section-card textarea
```

---

## Key Functions

### Main Render
```python
def render()
  └── _render_navi_guidance()
  └── _render_module_completion()
  └── _render_executive_summary()
  └── _render_detailed_breakdown()
      ├── _render_financial_overview_tab()
      ├── _render_monthly_costs_tab()
      ├── _render_coverage_tab()
      └── _render_projections_tab()
  └── _render_advisor_notes()
  └── _render_footer_navigation()
```

### Helper Functions
```python
_calculate_financial_metrics(modules)
  → Returns: monthly_cost, monthly_coverage, monthly_gap,
             total_assets, runway_years, runway_display

_render_module_status_item(module)
  → Renders single module status with icon + label
```

---

## Session State Keys

### Read
- `cost_v2_modules` — All module data
- `cost_v2_advisor_notes` — Optional notes

### Module Data Structure
```python
modules = {
    "income": {
        "status": "completed",
        "data": {
            "ss_monthly": 2500,
            "pension_monthly": 1800,
            # ...
        }
    },
    "assets": {
        "status": "completed",
        "data": {
            "checking_savings": 50000,
            "investment_accounts": 150000,
            # ...
        }
    },
    # ... va_benefits, health_insurance, life_insurance, medicaid_navigation
}
```

---

## Navigation Flow

```
[User completes modules]
    ↓
[Hub: "Expert Advisor Review" tile]
    ↓
[Expert Advisor Review page]
    ↓
    ├── ⬅️ Review Modules → Returns to hub
    ├── ✅ Finalize & Continue → Proceeds to exit
    └── 🏠 Return to Hub → Returns to hub
```

---

## Testing Quick Checks

### Visual
1. Open page — No yellow/blue/green banners
2. Navi panel — Single panel at top
3. Module grid — 2 columns on desktop
4. Metrics — 4-column grid
5. Tabs — Minimal styling (no colors)

### Functional
1. Module status — Reflects actual completion
2. Metrics — Calculate from module data
3. Runway — Shows years or "Unlimited"
4. Tabs — Switch content correctly
5. Buttons — Navigate to correct pages

### Responsive
1. Resize to mobile — Module grid stacks
2. Metrics — Collapse to 2x2 or single column
3. Buttons — Remain usable

---

## Quick Fixes

### If Navi doesn't show
```python
# Check core/ui.py has render_navi_panel_v2
from core.ui import render_navi_panel_v2
```

### If metrics are wrong
```python
# Check _calculate_financial_metrics() return values
metrics = _calculate_financial_metrics(modules)
print(metrics)  # Debug
```

### If styling broken
```css
/* Check modules.css has .section-card at top */
.sn-app .section-card { ... }
```

---

## Rollback (If Needed)

```bash
# Restore original version
cp products/cost_planner_v2/expert_review_old.py products/cost_planner_v2/expert_review.py

# Remove CSS (lines 1-108 in modules.css)
# Manually edit or use git checkout
```

---

## Contact / Support

- **Documentation:** `EXPERT_ADVISOR_REVIEW_REDESIGN.md`
- **Original backup:** `expert_review_old.py`
- **Design specs:** See user requirements document (this session)
