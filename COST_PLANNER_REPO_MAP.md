# Cost Planner Repository Map

```
cca_senior_navigator_v3/
│
├── 📋 DOCUMENTATION (Root Level)
│   ├── COST_PLANNER_ARCHITECTURE.md        ← Read this for overview
│   ├── COST_PLANNER_QUICK_REF.md           ← Quick reference cheat sheet
│   ├── COST_PLANNER_SEPARATION_COMPLETE.md ← Implementation details
│   └── COST_PLANNER_SEPARATION_SUMMARY.md  ← Executive summary
│
├── ⚙️ CONFIG FILES
│   ├── config/
│   │   ├── cost_config.v3.json                ⚠️ LEGACY - Old Cost Planner
│   │   ├── cost_planner_v2_modules.json       ✅ ACTIVE - V2 modules (4 modules)
│   │   ├── regional_cost_config.json          ← Regional pricing data
│   │   └── nav.json                           ← Navigation config
│   │       ├── "cost" → products.cost_planner (hidden, legacy)
│   │       └── "cost_v2" → products.cost_planner_v2 (active)
│
└── 💻 PRODUCT CODE
    ├── products/
    │   │
    │   ├── cost_planner/                      ⚠️ LEGACY FOLDER - DO NOT USE
    │   │   ├── README_LEGACY.md               ← ⚠️ READ THIS FIRST!
    │   │   ├── product.py                     (Old router)
    │   │   ├── modules/                       (Old modules)
    │   │   └── [other legacy files...]
    │   │
    │   └── cost_planner_v2/                   ✅ ACTIVE FOLDER - USE THIS
    │       ├── MODULE_DEVELOPMENT_GUIDE.md    ← Complete developer guide
    │       │
    │       ├── 🎛️ CORE FILES
    │       │   ├── product.py                 (Router - detects JSON modules)
    │       │   ├── hub.py                     (Dashboard - shows 4 modules)
    │       │   ├── module_renderer.py         (JSON → UI engine)
    │       │   ├── intro.py                   (Welcome screen)
    │       │   ├── triage.py                  (GCP gate check)
    │       │   ├── expert_review.py           (Final review)
    │       │   └── exit.py                    (Completion screen)
    │       │
    │       ├── 📦 MODULES (Legacy Python)
    │       │   └── modules/
    │       │       ├── income_assets.py       (Income & Assets module)
    │       │       ├── monthly_costs.py       (Care Costs module)
    │       │       └── coverage.py            (Coverage module)
    │       │
    │       └── 🛠️ UTILITIES
    │           └── utils/
    │               └── [helper functions]
    │
    └── pages/
        └── cost_planner.py                    (Page stub - links to product)
```

## 🎯 Quick Navigation Guide

### "I want to add a new module"
1. Go to: `config/cost_planner_v2_modules.json`
2. Read: `products/cost_planner_v2/MODULE_DEVELOPMENT_GUIDE.md`
3. Edit: JSON config only (no Python needed!)

### "I want to understand the architecture"
1. Read: `COST_PLANNER_QUICK_REF.md` (2 min)
2. Read: `COST_PLANNER_ARCHITECTURE.md` (5 min)
3. Explore: `products/cost_planner_v2/`

### "I'm confused about which version to use"
**Simple answer:** Always `cost_planner_v2/` (with the "v2" suffix)

### "I found code in cost_planner/ (no v2)"
**Action:** Read `products/cost_planner/README_LEGACY.md` then close that folder

## 🔍 File Search Patterns

```bash
# Find V2 files (ACTIVE)
find products/cost_planner_v2/ -type f -name "*.py"

# Find config
ls config/cost_planner_v2_modules.json

# Find documentation
ls *COST_PLANNER*.md

# Check navigation
grep -A 2 '"cost' config/nav.json
```

## 🚦 Color Legend

- 🟢 **Green (✅)** = Active, use this
- 🔴 **Red (⚠️)** = Legacy, avoid this
- 🔵 **Blue (📋)** = Documentation
- 🟡 **Yellow (⚙️)** = Configuration

## 📊 Statistics

| Metric | Count |
|--------|-------|
| Active modules (V2) | 4 |
| Config files | 2 (1 legacy, 1 active) |
| Documentation files | 5 |
| Python files (V2) | ~15 |
| JSON config lines (V2) | ~970 |

## 🎓 Learning Path

```
Beginner Path:
1. COST_PLANNER_QUICK_REF.md              (Start here!)
2. products/cost_planner_v2/ folder       (Explore)
3. config/cost_planner_v2_modules.json    (View example)

Intermediate Path:
4. COST_PLANNER_ARCHITECTURE.md           (Understand design)
5. MODULE_DEVELOPMENT_GUIDE.md            (Learn to build)
6. module_renderer.py                     (See implementation)

Advanced Path:
7. Build a test module                     (Hands-on)
8. Extend renderer capabilities            (Contribute)
9. Migrate legacy modules to JSON          (Refactor)
```

---

**Key Takeaway:** Everything you need is in `cost_planner_v2/` with config in `cost_planner_v2_modules.json`. Ignore anything without "v2" in the name.
