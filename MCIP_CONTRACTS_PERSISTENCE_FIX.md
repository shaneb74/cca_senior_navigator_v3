# MCIP Contracts Persistence Fix + Auto-Unlock Fix

## Problem 1: Session State Lost on Navigation

Session state was being lost when navigating from Cost Planner back to the hub using the "Return to Hub" button.

### Root Cause

The terminal debug output revealed:
```
[MCIP] 'mcip_contracts' in session_state: False
[APP] 'mcip_contracts' in session_state: False
[APP] extract_session_state() returned keys: ['current_route']
[APP] 'mcip_contracts' in extracted user_state: False
```

**The Issue:**
- `mcip_contracts` was **never being created** on initial app load
- `MCIP.initialize()` would create the `mcip` state structure but did NOT call `_save_contracts_for_persistence()`
- Without `mcip_contracts`, persistence system had nothing to save
- On every page navigation, MCIP would reset to defaults because there were no saved contracts to restore from

### Fix #1: Save Contracts on Initialize (Conditional)

Modified `core/mcip.py`'s `initialize()` to save contracts ONLY when creating fresh state:

```python
@classmethod
def initialize(cls) -> None:
    """Initialize MCIP state structure if not exists."""
    # ... setup default_state ...
    
    # Restore from mcip_contracts if exists
    restored_from_contracts = False
    if "mcip_contracts" in st.session_state:
        # ... restore logic ...
        restored_from_contracts = True
    
    # CRITICAL FIX: Only save contracts if we created fresh state
    # If we restored from contracts, those contracts are already the source of truth
    # Saving here would overwrite in-memory updates
    if not restored_from_contracts:
        cls._save_contracts_for_persistence()
```

**Why this matters:**
- If contracts exist → we restored from them → DON'T save (would overwrite any updates)
- If no contracts exist → we created fresh state → DO save (create initial contracts)

This prevents a race condition where:
1. Product updates journey state in memory
2. Navigation happens before save completes
3. Persistence loads old data from file
4. Initialize restores old data and immediately saves it
5. In-memory updates are lost

## Problem 2: Cost Planner Locking After Navigation

When users navigated to Cost Planner, worked in it, then returned to the hub, the Cost Planner would show as "locked" again.

### Root Cause

```
[MCIP]   - journey unlocked: ['gcp']
```

**The Issue:**
- Cost Planner is accessible via direct navigation (nav.json allows it)
- But MCIP's `unlocked_products` list only contains `['gcp']` by default
- When `get_product_summary("cost_v2")` is called, it checks if GCP is complete
- If GCP is not complete, it returns `status: "locked"`
- Hub uses this status to display the lock icon and prevent access
- But the user had JUST been in Cost Planner, so it should stay unlocked!

### Fix #2: Auto-Unlock on Access

Modified `products/cost_planner_v2/product.py` to auto-unlock itself when accessed:

```python
def render():
    # CRITICAL: Ensure cost_planner is unlocked when accessed
    # This handles the case where a user navigates directly to Cost Planner
    # without completing GCP first
    MCIP.initialize()
    unlocked_products = MCIP.get_unlocked_products()
    if "cost_planner" not in unlocked_products and "cost_v2" not in unlocked_products:
        # Auto-unlock cost planner since user is accessing it
        journey = st.session_state["mcip"]["journey"]
        if "cost_planner" not in journey["unlocked_products"]:
            journey["unlocked_products"].append("cost_planner")
        if "cost_v2" not in journey["unlocked_products"]:
            journey["unlocked_products"].append("cost_v2")
        # Save the updated journey state
        MCIP._save_contracts_for_persistence()
    # ... rest of render ...
```

### Fix #3: Check Unlocked List in get_product_summary

Modified `core/mcip.py`'s `get_product_summary()` to check the `unlocked_products` list, not just prerequisite completion:

**Before:**
```python
# Check if GCP is complete
rec = cls.get_care_recommendation()
if rec and rec.tier:
    return {"status": "unlocked", ...}
else:
    return {"status": "locked", ...}
```

**After:**
```python
# Check if product is unlocked (either via GCP completion OR via direct access)
unlocked_products = cls.get_unlocked_products()
is_unlocked = ("cost_planner" in unlocked_products or "cost_v2" in unlocked_products)

# Also check if GCP is complete (legacy check)
rec = cls.get_care_recommendation()
if is_unlocked or (rec and rec.tier):
    return {"status": "unlocked", ...}
else:
    return {"status": "locked", ...}
```

This same fix was applied to PFMA's unlock logic.

### What This Fixes

✅ `mcip_contracts` is **always created** during initialization  
✅ Persistence system always has contracts to save  
✅ On restore, contracts are available even on first load  
✅ Journey state (completed_products, unlocked_products) is preserved  
✅ **Cost Planner auto-unlocks when accessed directly**  
✅ **Cost Planner stays unlocked after returning to hub**  
✅ Care recommendation status is preserved  
✅ Financial profile is preserved  
✅ Navigation between pages maintains state  

## Changed Files

**`core/mcip.py`** (3 changes)
1. Line ~142: Added call to `cls._save_contracts_for_persistence()` after state initialization
   - Ensures `mcip_contracts` exists from the very first page load
2. Line ~620: Modified `get_product_summary()` for Cost Planner to check `unlocked_products` list
   - Respects direct product access, not just prerequisite completion
3. Line ~655: Modified `get_product_summary()` for PFMA to check `unlocked_products` list
   - Consistent unlock behavior across all products

**`products/cost_planner_v2/product.py`** (line ~24)
- Added auto-unlock logic at the start of `render()`
- Ensures Cost Planner unlocks itself when accessed
- Prevents re-locking after navigation back to hub

## Testing

1. ✅ Start fresh app
2. ✅ Navigate through concierge hub
3. ✅ Check debug output - `mcip_contracts` should now exist
4. ✅ Navigate to Cost Planner (without completing GCP)
5. ✅ Cost Planner should auto-unlock
6. ✅ Work in Cost Planner
7. ✅ Click "Return to Hub"
8. ✅ Cost Planner tile should NOT show as locked
9. ✅ State should be preserved (no reset to defaults)

## Debug Output Expected

Before:
```
[MCIP] 'mcip_contracts' in session_state: False
[APP] 'mcip_contracts' in session_state: False
[MCIP]   - journey unlocked: ['gcp']
```

After:
```
[COST_PLANNER] Auto-unlocked cost_planner and cost_v2
[COST_PLANNER] Updated unlocked_products: ['gcp', 'cost_planner', 'cost_v2']
[MCIP] 'mcip_contracts' in session_state: True
[APP] 'mcip_contracts' in session_state: True
[APP] extract_user_state() returned keys: ['progress', 'profile', 'tiles', 'preferences', 'mcip_contracts']
[MCIP]   - journey unlocked: ['gcp', 'cost_planner', 'cost_v2']
```

## Impact

These are **critical fixes** that ensure:
- All MCIP state (journey progress, product completions, recommendations) persists correctly
- Products stay unlocked once accessed, even without completing prerequisites
- Users can navigate freely between products and hubs without losing progress
- Direct navigation to products works correctly (no artificial gates)
