# Recommended Repository Reorganization Plan
**Date:** November 2, 2025  
**Branch Strategy:** `refactor/flatten-product-paths`  
**Estimated Time:** 20 minutes  
**Risk Level:** LOW  

---

## 🎯 Objective

Flatten product paths by removing the obsolete `concierge_hub` and `waiting_room` directory layers while maintaining the clean separation between products and hubs.

**Key Principle:** Products remain products, hubs remain hubs. We're just removing unnecessary nesting.

---

## 📊 Current State Analysis

### Current Product Structure (Problematic)
```
products/
├── concierge_hub/          ❌ Unnecessary nesting layer
│   ├── gcp_v4/             ✅ Canonical GCP (per copilot-instructions.md)
│   ├── cost_planner_v2/    ✅ Canonical Cost Planner
│   └── pfma_v3/            ✅ Financial Assessment
├── waiting_room/           ❌ Deprecated hub name as folder
│   ├── advisor_prep/
│   ├── home_safety/
│   ├── predictive_health/
│   ├── senior_trivia/
│   └── concierge_clinical_review/
└── [other products]/
```

### Current Hub Structure (Already Clean)
```
hubs/
├── _deprecated_hub_concierge.py      ✅ Already marked deprecated
├── _deprecated_hub_waiting_room.py   ✅ Already marked deprecated
├── hub_lobby.py                      ✅ Active landing page
├── learning.py
├── partners.py
├── professional.py
└── resources.py
```

### Active References Found
- **nav.json**: 14 routes using `products.concierge_hub.*` or `products.waiting_room.*`
- **smoke_imports.py**: 4 import statements
- **mcip.py**: 15 references to "waiting_room" state (but these are state keys, NOT paths)
- **stubs.py**: 1 function `render_waiting_room()` (stub only)

---

## ✅ Target State

### Flattened Product Structure
```
products/
├── gcp_v4/                          # Guided Care Plan (moved from concierge_hub/)
│   ├── modules/
│   │   └── care_recommendation/
│   │       ├── module.json          # Source of truth for GCP questions
│   │       ├── logic.py             # GCP decision engine
│   │       └── ui.py
│   └── product.py
├── cost_planner_v2/                 # Cost Planner (moved from concierge_hub/)
│   ├── modules/
│   ├── utils/                       # Cost calculation engines
│   └── product.py
├── pfma_v3/                         # Financial Assessment (moved from concierge_hub/)
│   └── product.py
├── advisor_prep/                    # Waiting room products (moved up one level)
│   └── product.py
├── home_safety/
│   └── product.py
├── predictive_health/
│   └── product.py
├── senior_trivia/
│   └── product.py
├── concierge_clinical_review/
│   └── product.py
└── [existing products - unchanged]/
    ├── discovery_learning/
    ├── learn_recommendation/
    ├── professionals/
    ├── resources/
    └── trusted_partners/
```

### Hub Structure (No Changes Needed)
```
hubs/
├── hub_lobby.py              # Main landing page (unchanged)
├── learning.py
├── partners.py
├── professional.py
└── resources.py
# Deprecated files will be deleted in Phase 4
```

---

## 🔧 Migration Plan (4 Phases)

### Phase 1: Move Core Products (5 min)
Move the three main products out of `concierge_hub/`:

```bash
# Create backup branch
git checkout -b refactor/flatten-product-paths

# Move core products
git mv products/concierge_hub/gcp_v4 products/gcp_v4
git mv products/concierge_hub/cost_planner_v2 products/cost_planner_v2
git mv products/concierge_hub/pfma_v3 products/pfma_v3

# Remove now-empty concierge_hub directory
rmdir products/concierge_hub/
```

**Verification:**
- [ ] `products/gcp_v4/` exists with all modules intact
- [ ] `products/cost_planner_v2/` exists with utils/ intact
- [ ] `products/pfma_v3/` exists
- [ ] `products/concierge_hub/` no longer exists

---

### Phase 2: Move Waiting Room Products (5 min)
Flatten waiting room products to top-level:

```bash
# Move waiting room products
git mv products/waiting_room/advisor_prep products/advisor_prep
git mv products/waiting_room/home_safety products/home_safety
git mv products/waiting_room/predictive_health products/predictive_health
git mv products/waiting_room/senior_trivia products/senior_trivia
git mv products/waiting_room/concierge_clinical_review products/concierge_clinical_review

# Remove now-empty waiting_room directory
rmdir products/waiting_room/
```

**Verification:**
- [ ] All 5 waiting room products exist at `products/[name]/`
- [ ] `products/waiting_room/` no longer exists

---

### Phase 3: Update References (8 min)

#### 3A. Update nav.json (14 route changes)
Find and replace in `config/nav.json`:

```bash
# Automated replacement
sed -i '' \
  -e 's|products\.concierge_hub\.gcp_v4|products.gcp_v4|g' \
  -e 's|products\.concierge_hub\.cost_planner_v2|products.cost_planner_v2|g' \
  -e 's|products\.concierge_hub\.pfma_v3|products.pfma_v3|g' \
  -e 's|products\.waiting_room\.advisor_prep|products.advisor_prep|g' \
  -e 's|products\.waiting_room\.home_safety|products.home_safety|g' \
  -e 's|products\.waiting_room\.predictive_health|products.predictive_health|g' \
  -e 's|products\.waiting_room\.senior_trivia|products.senior_trivia|g' \
  -e 's|products\.waiting_room\.concierge_clinical_review|products.concierge_clinical_review|g' \
  config/nav.json
```

**Manual verification required:**
- [ ] `gcp` route (line ~100): `products.gcp_v4.product:render`
- [ ] `gcp_intro` route (line ~112): `products.gcp_v4.product:render`
- [ ] `cost_planner` route (line ~130): `products.cost_planner_v2.product:render`
- [ ] `cost_planner_intro` route (line ~136): `products.cost_planner_v2.intro:render`
- [ ] `cost_planner_quick` route (line ~142): `products.cost_planner_v2.quick_estimate:render`
- [ ] `pfma` route (line ~154): `products.pfma_v3.product:render`
- [ ] `financial_assessment` route (line ~160): `products.pfma_v3.product:render`
- [ ] `advisor_prep` route (line ~166): `products.advisor_prep.product:render`
- [ ] `home_safety` route (line ~190): `products.home_safety.product:render`
- [ ] `predictive_health` route (line ~214): `products.predictive_health.product:render`
- [ ] `senior_trivia` route (line ~220): `products.senior_trivia.product:render`
- [ ] `concierge_clinical_review` routes (lines ~226, 232, 238): `products.concierge_clinical_review.product:render`

#### 3B. Update Test Imports
Edit `tests/smoke_imports.py`:

**Before:**
```python
from products.concierge_hub.gcp_v4.modules.care_recommendation import config, logic
from products.concierge_hub.cost_planner_v2.utils import cost_calculator
from products.waiting_room import advisor_prep
from products.concierge_hub import pfma_v3
from products.waiting_room.senior_trivia import product as senior_trivia_product
```

**After:**
```python
from products.gcp_v4.modules.care_recommendation import config, logic
from products.cost_planner_v2.utils import cost_calculator
from products import advisor_prep
from products import pfma_v3
from products.senior_trivia import product as senior_trivia_product
```

#### 3C. Check for Any Other Import References
```bash
# Search for remaining old path references
grep -r "products\.concierge_hub" --include="*.py" .
grep -r "products\.waiting_room" --include="*.py" .
grep -r "from products.concierge_hub" --include="*.py" .
grep -r "from products.waiting_room" --include="*.py" .
```

**Expected:** Only matches in `docs/history/` and `REORG_PLAN.md` (documentation only)

**Verification:**
- [ ] All Python imports updated
- [ ] No active code references old paths
- [ ] nav.json validates as valid JSON
- [ ] smoke_imports.py runs without errors

---

### Phase 4: Cleanup (2 min)

```bash
# Delete deprecated hub files (already marked as deprecated)
git rm hubs/_deprecated_hub_concierge.py
git rm hubs/_deprecated_hub_waiting_room.py

# Archive old reorg plan (replaced by this document)
git mv pages/REORG_PLAN.md docs/history/REORG_PLAN_original.md
```

**Verification:**
- [ ] No deprecated hub files in `hubs/`
- [ ] Old reorg plan archived to history

---

## 🧪 Testing Checklist

### Manual Route Testing (15 min)
Test all affected routes in browser:

**Core Products:**
- [ ] `?page=gcp` - GCP intro loads
- [ ] `?page=gcp_intro` - GCP module renders
- [ ] Complete GCP flow → verify recommendation saves
- [ ] `?page=cost_planner` - Cost Planner loads
- [ ] `?page=cost_planner_intro` - Intro renders
- [ ] `?page=cost_planner_quick` - Quick estimate renders
- [ ] Complete Cost Planner → verify totals calculate
- [ ] `?page=pfma` - Financial assessment loads
- [ ] `?page=financial_assessment` - Assessment renders

**Waiting Room Products:**
- [ ] `?page=advisor_prep` - Advisor prep loads
- [ ] `?page=home_safety` - Home safety loads
- [ ] `?page=predictive_health` - Predictive health loads
- [ ] `?page=senior_trivia` - Senior trivia loads
- [ ] `?page=concierge_clinical_review` - Clinical review loads

### Automated Testing
```bash
# Run smoke tests
python tests/smoke_imports.py

# Expected output: All imports successful, no ModuleNotFoundError
```

### Hub Navigation Testing
- [ ] Visit hub_lobby (`?page=hub_lobby`)
- [ ] Click GCP tile → should load GCP intro
- [ ] Click Cost Planner tile → should load Cost Planner intro
- [ ] Click Financial Assessment tile → should load PFMA
- [ ] Verify journey progression (MCIP) still works

---

## ⚠️ Important Notes

### What This Does NOT Change

1. **MCIP State Management** ✅
   - The "waiting_room" state keys in `core/mcip.py` are **state keys**, not file paths
   - No changes needed to MCIP logic
   - State structure: `st.session_state["mcip"]["waiting_room"]["advisor_prep_status"]` remains unchanged

2. **Session Store Keys** ✅
   - Per `core/session_store.py` read-only guard
   - No changes to `USER_PERSIST_KEYS` entries
   - Product data persists with same keys

3. **Product Internal Logic** ✅
   - GCP module.json remains authoritative (per copilot-instructions.md)
   - Cost Planner calculation engines unchanged
   - No business logic modifications

4. **Hub Rendering** ✅
   - `hubs/hub_lobby.py` continues to work unchanged
   - Hub tile configuration points to new product paths via nav.json
   - No changes to hub UI/UX

### What IS Changed

1. **File Paths** - Products moved to flatter structure
2. **Import Statements** - Updated to use new paths
3. **nav.json Routes** - Updated module references
4. **Test Files** - Import paths updated

---

## 🔄 Rollback Plan

If issues arise during testing:

```bash
# Rollback to dev branch
git checkout dev

# Delete refactor branch
git branch -D refactor/flatten-product-paths
```

All changes are in a feature branch, so rollback is instant.

---

## 📋 Commit Strategy

```bash
# Phase 1 & 2 (file moves)
git add products/
git commit -m "refactor: flatten product paths - move core and waiting room products

Moved:
- products/concierge_hub/gcp_v4 → products/gcp_v4
- products/concierge_hub/cost_planner_v2 → products/cost_planner_v2
- products/concierge_hub/pfma_v3 → products/pfma_v3
- products/waiting_room/* → products/* (5 products)

Rationale: Remove unnecessary nesting layers. Products are already well-organized
internally; the concierge_hub and waiting_room directories were legacy hub names
that no longer reflect the architecture.

Deleted empty directories:
- products/concierge_hub/
- products/waiting_room/"

# Phase 3 (update references)
git add config/nav.json tests/smoke_imports.py
git commit -m "refactor: update nav routes and test imports for flattened product paths

Updated 14 routes in nav.json:
- products.concierge_hub.* → products.*
- products.waiting_room.* → products.*

Updated 5 import statements in tests/smoke_imports.py

All routes tested and verified working."

# Phase 4 (cleanup)
git add hubs/ docs/history/ pages/
git commit -m "refactor: remove deprecated hub files and archive old reorg plan

Deleted:
- hubs/_deprecated_hub_concierge.py
- hubs/_deprecated_hub_waiting_room.py

Archived:
- pages/REORG_PLAN.md → docs/history/REORG_PLAN_original.md"
```

---

## ✅ Success Criteria

**Branch ready to merge when:**
1. All file moves completed without errors
2. All 14 nav.json routes verified working in browser
3. `python tests/smoke_imports.py` passes
4. Hub lobby tile navigation works correctly
5. MCIP journey progression still functional
6. No Python import errors in console
7. All 3 commits pushed to `refactor/flatten-product-paths` branch

**Merge command (after testing):**
```bash
git checkout dev
git merge refactor/flatten-product-paths --no-ff
git push origin dev
```

---

## 🚫 Why NOT the Original REORG_PLAN?

The original plan proposed moving products **inside** the hub:
```
hubs/lobby_hub/product_tiles/guided_care_plan/
```

**Problems with that approach:**
1. **Violates Separation of Concerns**: Products are not sub-components of hubs
2. **Breaks Copilot Instructions**: Would invalidate documented canonical paths
3. **Increases Coupling**: Hubs should route to products, not contain them
4. **No Clear Benefit**: Doesn't improve maintainability or clarity
5. **Higher Risk**: Requires rewriting product-to-product transitions

**This plan is better because:**
- ✅ Maintains clean separation (products/ vs hubs/)
- ✅ Preserves copilot-instructions.md canonical paths
- ✅ Lower risk (just path renames, no architecture change)
- ✅ Faster execution (20 min vs 2-3 hours)
- ✅ Easier to test and rollback

---

## 📚 References

- **Copilot Instructions**: `.github/copilot-instructions.md` (GCP/Cost Planner canonical paths)
- **Original Plan**: `pages/REORG_PLAN.md` (will be archived)
- **Cleanup Summary**: `CLEANUP_SUMMARY_2025_11.md` (recent successful refactor)
- **Session Store Guard**: `core/session_store.py` (read-only persistence keys)
- **MCIP Documentation**: `core/mcip.py` (journey state management)

---

**Ready to proceed? Start with Phase 1.**
