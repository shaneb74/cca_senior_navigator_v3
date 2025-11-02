# Journey Completion Evaluation Report
**Date:** November 2, 2025  
**Branch:** feature/dev-work  
**Issue:** Planning journey products not completing properly

---

## Executive Summary

The journey completion system has **two separate tracking mechanisms** that are not synchronized:
1. **MCIP-based tracking** (`core/mcip.py`) - Modern, canonical system
2. **Legacy user_ctx tracking** (`core/events.py`) - Old pattern from Phase Post-CSS

This causes products in the Planning journey (GCP, Cost Planner) to mark complete in MCIP but not update the legacy journey system, leading to tiles staying in the "Active Journey" section instead of moving to "Completed Journeys".

---

## Current Behavior (Problems)

### ✅ Works Correctly
- **Discovery Learning**: Properly completes and moves to "My Completed Journeys"
  - Calls `MCIP.mark_product_complete("discovery_learning")` 
  - Location: `products/discovery_learning/product.py:308`

### ❌ Broken Behavior

#### 1. **Guided Care Plan (GCP)**
**Issue:** Marks complete but stays in Active Journey section

**Completion Points:**
- Primary: `products/gcp_v4/product.py:559` → `MCIP.mark_product_complete("gcp")`
- Secondary: `products/gcp_v4/modules/care_recommendation/logic.py:199,271` → `mark_product_complete(user_ctx, "gcp_v4")`

**Problem:** Uses **BOTH** systems inconsistently:
- Uses MCIP method in main product flow
- Uses legacy `core/events.py` method in recommendation logic
- Key mismatch: `"gcp"` vs `"gcp_v4"` product keys

#### 2. **Cost Planner**
**Issue:** Never marks as complete

**Attempted Completion Points:**
- `products/cost_planner_v2/exit.py:47` → `mark_product_complete(user_ctx, "cost_planner_v2")` ❌ Legacy system only
- `products/cost_planner_v2/hub.py:1394` → `MCIP.mark_product_complete("cost_v2")` ✅ MCIP system

**Problem:** 
- Exit flow uses legacy system with wrong key (`"cost_planner_v2"`)
- Hub uses MCIP with correct key (`"cost_v2"`)
- Hub completion may not be reached in normal flow
- Key normalization in hub_lobby expects `"cost_planner"` or `"cost_v2"`

#### 3. **Learn Recommendation**
**Issue:** Unknown completion status

**Completion Point:**
- `products/learn_recommendation/product.py:330` → `MCIP.mark_product_complete("learn_recommendation")`

**Problem:** Not tracked in hub_lobby's completed tiles builder

---

## Root Cause Analysis

### 1. **Dual Tracking Systems**

#### MCIP System (Canonical)
```python
# Location: core/mcip.py:559-576
@classmethod
def mark_product_complete(cls, product_key: str) -> None:
    journey = st.session_state[cls.STATE_KEY]["journey"]
    if product_key not in journey["completed_products"]:
        journey["completed_products"].append(product_key)
    cls._save_contracts_for_persistence()
```

#### Legacy System (Deprecated)
```python
# Location: core/events.py:73-103
def mark_product_complete(user_ctx: dict, product_key: str) -> dict:
    journeys = user_ctx.setdefault("journeys", {})
    for journey_key, journey_data in journeys.items():
        products = journey_data.get("products", {})
        if product_key in products:
            products[product_key]["completed"] = True
            # Auto-complete journey if all products done
            if all(p.get("completed") for p in products.values()):
                journey_data["completed"] = True
```

**Impact:** Products can be complete in MCIP but not in user_ctx, causing hub_lobby to show them as active.

### 2. **Key Normalization Mismatch**

Hub lobby normalizes keys (`hub_lobby.py:195-209`):
```python
key_map = {
    'gcp_v4': 'gcp',
    'gcp': 'gcp',
    'cost_v2': 'cost_planner',
    'cost_planner': 'cost_planner',
    'cost_intro': 'cost_planner',
    'pfma_v3': 'pfma',
}
```

But products use inconsistent keys:
- GCP: Uses `"gcp"` in MCIP, `"gcp_v4"` in legacy
- Cost Planner: Uses `"cost_v2"` in MCIP, `"cost_planner_v2"` in legacy
- Hub checks: Uses normalized `"cost_planner"` and `"gcp"`

### 3. **Completion Detection Logic**

Hub lobby determines completed tiles (`hub_lobby.py:516`):
```python
for key, title, desc in all_products:
    if _get_product_state(key) == "completed":
        # Add to completed tiles
```

`_get_product_state()` checks MCIP only:
```python
if MCIP.is_product_complete(normalized_key):
    return "completed"
```

**Missing Link:** No connection to legacy `user_ctx` journey system.

### 4. **Filter Logic Removing Completed from Active**

Planning tiles filter (`hub_lobby.py:388`):
```python
# Phase 5K: Filter out completed tiles
tiles = [t for t in tiles if not MCIP.is_product_complete(t.key)]
```

Discovery tiles filter (`hub_lobby.py:280`):
```python
if MCIP.is_product_complete("discovery_learning"):
    return []  # Don't show in active tiles
```

**Works for Discovery, fails for Planning:**
- Discovery Learning: ✅ Uses `"discovery_learning"` consistently
- GCP/Cost Planner: ❌ Key mismatches prevent filtering

---

## Data Flow Diagram

```
User completes product
         ↓
Product calls completion method
         ↓
    ┌────┴────┐
    ↓         ↓
MCIP System   Legacy System (user_ctx)
    ↓         ↓
journey/      journeys/{journey_key}/
completed_    products/{product_key}/
products[]    completed: true
    ↓         ↓
Hub checks    Hub checks ???
MCIP only     (not implemented)
    ↓
Show in Active or Completed section
```

**Problem:** Hub only checks MCIP, but some products only update legacy system.

---

## Product-by-Product Status

| Product | MCIP Complete? | Legacy Complete? | Hub Shows | Issue |
|---------|---------------|------------------|-----------|-------|
| Discovery Learning | ✅ Yes | ❌ No | Completed | Works (MCIP only) |
| GCP v4 | ✅ Yes (as "gcp") | ⚠️ Partial (as "gcp_v4") | **Active** | Key mismatch + dual calls |
| Learn Recommendation | ✅ Yes | ❌ No | **Not tracked** | Missing from completed builder |
| Cost Planner v2 | ⚠️ Maybe (as "cost_v2") | ❌ No (as "cost_planner_v2") | **Active** | Exit uses legacy, hub uses MCIP |
| PFMA v3 | ✅ Yes (as "pfma_v3") | ❌ No | Unknown | Not tested |

---

## Code Locations Reference

### Completion Calls
- **Discovery Learning**: `products/discovery_learning/product.py:308`
- **GCP (MCIP)**: `products/gcp_v4/product.py:559`
- **GCP (Legacy)**: `products/gcp_v4/modules/care_recommendation/logic.py:199,271`
- **Cost Planner (MCIP)**: `products/cost_planner_v2/hub.py:1394`
- **Cost Planner (Legacy)**: `products/cost_planner_v2/exit.py:47`
- **Learn Recommendation**: `products/learn_recommendation/product.py:330`
- **PFMA v3**: `products/pfma_v3/product.py:323`

### Completion Systems
- **MCIP System**: `core/mcip.py:559-590`
- **Legacy System**: `core/events.py:73-103`

### Hub Detection
- **State Getter**: `hubs/hub_lobby.py:188-220`
- **Completed Builder**: `hubs/hub_lobby.py:496-535`
- **Render Logic**: `hubs/hub_lobby.py:800-1038`

---

## Recommended Solution

### Strategy: **Standardize on MCIP System**

The MCIP system is:
- ✅ Modern and well-documented
- ✅ Used by most products
- ✅ Has persistence layer
- ✅ Includes event firing
- ✅ Already checked by hub_lobby

**Action Items:**

1. **Remove all calls to legacy `mark_product_complete(user_ctx, ...)`**
   - Replace with `MCIP.mark_product_complete(...)`

2. **Standardize product keys** (use normalized keys everywhere):
   - GCP: Use `"gcp"` (not `"gcp_v4"`)
   - Cost Planner: Use `"cost_planner"` (not `"cost_v2"` or `"cost_planner_v2"`)
   - PFMA: Use `"pfma"` (not `"pfma_v3"`)

3. **Add missing products to completed tiles builder**:
   - Add `learn_recommendation` to `all_products` list

4. **Verify completion points**:
   - Ensure Cost Planner exit flow calls MCIP method
   - Remove duplicate completion calls in GCP

5. **Deprecate legacy system**:
   - Mark `core/events.py::mark_product_complete()` as deprecated
   - Add migration note for any remaining user_ctx data

6. **Add journey-level completion** (optional):
   - Use `core/journeys.py::mark_journey_complete()` when all products in journey done
   - Currently not implemented but infrastructure exists

---

## Testing Checklist

After fixes, verify:

- [ ] Discovery Learning completes → moves to Completed Journeys
- [ ] GCP completes → moves to Completed Journeys  
- [ ] Learn Recommendation completes → moves to Completed Journeys (if tracked)
- [ ] Cost Planner completes → moves to Completed Journeys
- [ ] PFMA completes → moves to Completed Journeys
- [ ] Tiles disappear from Active sections when complete
- [ ] "My Completed Journeys" shows all finished products
- [ ] Restart functionality still works (GCP, Cost Planner)
- [ ] Key normalization works for all product aliases

---

## Impact Assessment

**Files to Modify:** ~5-7 files
**Risk Level:** Medium (core completion logic)
**Testing Required:** Full integration test of all products
**Backward Compatibility:** May need session state migration for existing users

---

## Next Steps

1. **Review this evaluation** with team
2. **Approve solution strategy** (MCIP standardization)
3. **Create implementation plan** with surgical commits
4. **Update tests** for new completion flow
5. **Document key naming conventions** in `core/mcip.py`

---

**End of Evaluation Report**
