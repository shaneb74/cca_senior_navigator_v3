# Cost Planner Architecture Overview

## 🎯 Two Separate Systems

### ⚠️ Cost Planner (Legacy - NOT ACTIVE)
- **Location:** `products/cost_planner/`
- **Config:** `config/cost_config.v3.json`
- **Status:** Hidden in navigation, not actively used
- **Architecture:** Hardcoded Python modules
- **Purpose:** Historical reference, potential rollback

### ✅ Cost Planner V2 (ACTIVE)
- **Location:** `products/cost_planner_v2/`
- **Config:** `config/cost_planner_v2_modules.json`
- **Status:** Currently deployed and in use
- **Architecture:** JSON-driven with dynamic rendering
- **Purpose:** Production financial assessment tool

## 📋 Quick Reference

| Feature | Legacy (cost_planner) | V2 (cost_planner_v2) |
|---------|----------------------|---------------------|
| **Config File** | `cost_config.v3.json` | `cost_planner_v2_modules.json` |
| **Navigation Key** | `cost` | `cost_v2` |
| **Status** | Hidden/Inactive | Active |
| **Module System** | Python hardcoded | JSON-driven |
| **Adding Modules** | Edit Python code | Edit JSON only |
| **Maintenance** | Difficult | Easy |
| **Documentation** | None | MODULE_DEVELOPMENT_GUIDE.md |

## 🚀 For Developers

### Working on Cost Planning Features?
**Always use Cost Planner V2:**
```
cd products/cost_planner_v2/
# Read the guide
cat MODULE_DEVELOPMENT_GUIDE.md
```

### Need to Reference Old Code?
```
cd products/cost_planner/
# See legacy README
cat README_LEGACY.md
```

## 🔧 Navigation Configuration

In `config/nav.json`:

```json
{
  "products": [
    {
      "key": "cost",
      "label": "Cost Planner",
      "module": "products.cost_planner.product:render",
      "hidden": true    // ← Old version (hidden)
    },
    {
      "key": "cost_v2",
      "label": "Cost Planner v2",
      "module": "products.cost_planner_v2.product:render",
      "hidden": true    // ← Active version (hidden from direct access)
    }
  ]
}
```

**Note:** Both are marked "hidden" because they're accessed through the Concierge Hub, not directly from navigation.

## 📁 File Organization

```
cca_senior_navigator_v3/
├── config/
│   ├── cost_config.v3.json              # OLD - Legacy config
│   └── cost_planner_v2_modules.json     # NEW - Active config
│
└── products/
    ├── cost_planner/                    # OLD - Legacy folder
    │   ├── README_LEGACY.md            # ⚠️ Warning about legacy status
    │   ├── product.py
    │   └── modules/
    │
    └── cost_planner_v2/                 # NEW - Active folder
        ├── MODULE_DEVELOPMENT_GUIDE.md  # Complete documentation
        ├── module_renderer.py           # JSON → UI engine
        ├── product.py                   # Router
        ├── hub.py                       # Dashboard
        └── modules/                     # Module implementations
```

## 🎓 Common Confusions to Avoid

### ❌ Don't Do This:
- Edit `products/cost_planner/` (it's legacy)
- Use `cost_config.v3.json` for new features
- Assume both systems work together (they don't)
- Mix configs between versions

### ✅ Do This Instead:
- Edit `products/cost_planner_v2/` only
- Use `cost_planner_v2_modules.json`
- Treat them as completely separate systems
- Follow the MODULE_DEVELOPMENT_GUIDE.md

## 🔍 How to Tell Which Version You're Looking At

### In Code:
```python
# Legacy version
from products.cost_planner import product

# Active V2 version
from products.cost_planner_v2 import product
```

### In Config:
```json
// Legacy
"config/cost_config.v3.json"

// Active V2
"config/cost_planner_v2_modules.json"
```

### In URLs/Session State:
```python
# Legacy
st.session_state.product = "cost"

# Active V2
st.session_state.product = "cost_v2"
```

## 🚨 Migration Status

**No active migration needed.** The systems are completely separate:
- Legacy version is dormant (not receiving updates)
- V2 is the active development target
- No data flows between them
- No shared session state

## 📞 Need Help?

- **For V2 features:** Read `products/cost_planner_v2/MODULE_DEVELOPMENT_GUIDE.md`
- **For legacy questions:** See `products/cost_planner/README_LEGACY.md`
- **For architecture:** This document

---

**Last Updated:** October 14, 2025
**Maintainer:** Development Team
**Version:** Cost Planner V2 (Active)
