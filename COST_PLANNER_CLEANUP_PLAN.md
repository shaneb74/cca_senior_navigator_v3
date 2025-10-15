# Cost Planner Cleanup Plan

## 🎯 Objective
Remove legacy Cost Planner (non-V2) files that are no longer needed.

## ✅ Files to Keep

### Cost Planner V2 (Active - All Files)
```
products/cost_planner_v2/
├── __init__.py
├── auth.py
├── exit.py
├── expert_review.py
├── hub.py
├── intro.py
├── module_renderer.py
├── product.py
├── triage.py
├── MODULE_DEVELOPMENT_GUIDE.md
├── modules/
│   ├── __init__.py
│   ├── coverage.py
│   ├── income_assets.py
│   └── monthly_costs.py
└── utils/
    ├── __init__.py
    ├── cost_calculator.py
    └── regional_data.py
```

### Config Files
- ✅ `config/cost_planner_v2_modules.json` (Active)
- ✅ `config/regional_cost_config.json` (Shared)
- ⚠️ `config/cost_config.v3.json` (Legacy - consider archiving)

## ❌ Files to Remove

### Legacy Cost Planner Folder (Entire Directory)
```
products/cost_planner/
├── __init__.py                      ❌ Remove
├── README_LEGACY.md                 ❌ Remove (just created, no longer needed)
├── aggregator.py                    ❌ Remove (not used)
├── auth.py                          ❌ Remove (V2 has its own)
├── base_module_config.json          ❌ Remove (old config)
├── base_module_config.py            ❌ Remove (old config loader)
├── cost_estimate.py                 ❌ Remove (old estimator)
├── cost_estimate_v2.py              ❌ Remove (superseded)
├── dev_unlock.py                    ❌ Remove (no longer needed)
├── product.py                       ❌ Remove (old router)
└── modules/
    ├── quick_estimate.py            ❌ Remove (not used)
    └── va_benefits.py               ❌ Remove (not used)
```

### Old Cost Planner Entry File
```
products/cost_planner.py             ❌ Remove (old entry point)
```

### Config File (Optional Archive)
```
config/cost_config.v3.json           ⚠️ Archive or remove
```

## 🔧 Code Changes Needed

### 1. app.py - Remove dev_unlock import
```python
# REMOVE:
from products.cost_planner.dev_unlock import show_dev_controls

# REMOVE:
show_dev_controls()
```

### 2. config/nav.json - Remove legacy cost_planner entry
```json
// REMOVE this entire entry:
{
  "key": "cost",
  "label": "Cost Planner",
  "module": "products.cost_planner.product:render",
  "hidden": true
}
```

### 3. pages/cost_planner.py - Check if it points to old version
(Need to verify what this references)

## 📊 Impact Analysis

### Breaking Changes
- ❌ None - legacy version was hidden and not in use

### References to Clean
- app.py: dev_unlock import
- nav.json: legacy navigation entry
- Any documentation mentioning old version

## 🧪 Verification Steps

After cleanup:
1. ✅ App starts without import errors
2. ✅ Navigation works (cost_v2 still accessible)
3. ✅ No broken imports in codebase
4. ✅ Cost Planner V2 works normally
5. ✅ Search for "cost_planner" (no v2) returns nothing

## 📝 Cleanup Commands

```bash
# 1. Remove legacy folder entirely
rm -rf products/cost_planner/

# 2. Remove old entry point
rm products/cost_planner.py

# 3. Archive old config (optional)
mkdir -p archive/configs/
mv config/cost_config.v3.json archive/configs/cost_config.v3.json

# 4. Clean pycache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
```

## ⚠️ Safety Checks Before Removal

```bash
# Check for any remaining references
grep -r "from products.cost_planner" . --exclude-dir=__pycache__ --exclude-dir=.git --exclude="*.md"
grep -r "import products.cost_planner" . --exclude-dir=__pycache__ --exclude-dir=.git --exclude="*.md"

# Check nav.json
grep -A 5 '"key": "cost"' config/nav.json
```

---

**Status:** Ready to execute cleanup
**Branch:** temp/cost-planner-cleanup
**Risk Level:** Low (legacy code not in use)
