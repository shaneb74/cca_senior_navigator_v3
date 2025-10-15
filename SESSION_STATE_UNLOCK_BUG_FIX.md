# 🐛 Session State & Unlock Logic Bug - Root Cause & Fix

**Date**: October 15, 2025  
**Issue**: Cost Planner locks after completing GCP, forgetting completion state  
**Status**: ✅ Root Cause Identified - Ready for Fix

---

## 🎯 Problem Summary

**User Experience**:
1. User completes GCP care_recommendation module
2. Returns to Concierge Hub → Cost Planner unlocked ✅
3. Starts Cost Planner, completes some steps
4. Returns to Concierge Hub → **Cost Planner LOCKED again** ❌
5. Says "Complete Guided Care Plan first" (but it WAS complete!)

**Impact**: **CRITICAL** - Breaks core product flow, blocks demo/production use

---

## 🔬 Root Cause Analysis

### The Architecture Mismatch

Your app has **TWO completion tracking systems** that don't talk to each other:

#### ✅ **System 1: MCIP (Modern, Working)**
```python
# core/mcip.py
st.session_state["mcip"] = {
    "journey": {
        "completed_products": ["gcp"],  # ← GCP marked complete here
        "unlocked_products": ["gcp", "cost_planner", "pfma"]
    },
    "care_recommendation": { ... }  # ← Full CareRecommendation contract
}
```

- **Used by**: GCP v4, Cost Planner v2, PFMA v2 (modern products)
- **Publishing**: `MCIP.mark_product_complete("gcp")` ✅
- **Checking**: `MCIP.is_product_complete("gcp")` ✅
- **Persistence**: Saved via `_save_contracts_for_persistence()` ✅

#### ❌ **System 2: Legacy Session State (Old, Broken)**
```python
# What the unlock logic expects (but doesn't exist)
st.session_state["gcp"] = {
    "progress": 100  # ← UNLOCK CHECKS HERE, BUT IT'S EMPTY!
}
```

- **Used by**: Tile unlock logic in `core/product_tile.py`
- **Publishing**: **NOBODY** (GCP v4 doesn't write here anymore)
- **Checking**: `_get_progress(state, "gcp")` → `state["gcp"]["progress"]` ❌
- **Result**: Returns 0, thinks GCP incomplete, locks Cost Planner

---

## 📋 The Broken Data Flow

### What Happens Now (Broken)

```python
# 1. User completes GCP care_recommendation module
# products/gcp_v4/product.py (line 168)
MCIP.publish_care_recommendation(recommendation)  # ✅ Publishes to MCIP
MCIP.mark_product_complete("gcp")                # ✅ Marks complete in MCIP

# Result: st.session_state["mcip"]["journey"]["completed_products"] = ["gcp"] ✅
# Result: st.session_state["gcp"] = {}  ← EMPTY! ❌

# 2. User returns to Concierge Hub
# hubs/concierge.py (line 233)
summary = MCIP.get_product_summary("gcp_v4")  # ✅ Returns "complete"
is_complete = (summary["status"] == "complete")  # ✅ True

# GCP tile shows as complete ✅

# 3. Cost Planner tile checks if it should be locked
# hubs/concierge.py (line 246)
summary = MCIP.get_product_summary("cost_v2")
is_locked = (summary["status"] == "locked")  # ✅ MCIP says unlocked!

# Cost Planner tile created with locked=False ✅

# 4. Tile rendering checks unlock requirements
# core/product_tile.py (line 286)
unlock_requires=["gcp:complete"]  # "gcp" must have progress == 100

# 5. ProductTileHub renders HTML
# core/product_tile.py (line 221-230) - Checks if locked
if self.locked:
    # Don't render action buttons

# 6. THE BUG: Tile checks unlock_requires AGAIN at render time
# core/product_tile.py (line 105-107)
def tile_is_unlocked(tile, state):
    reqs = tile.unlock_requires  # ["gcp:complete"]
    return all(_evaluate_requirement(r, state) for r in reqs)

# 7. Requirement evaluation looks in WRONG PLACE
# core/product_tile.py (line 59-87)
def _evaluate_requirement(req, state):
    key, spec = req.split(":", 1)  # key="gcp", spec="complete"
    
    if key in ("gcp", "cost", "pfma"):
        prog = _get_progress(state, key)  # ← LOOKS IN state["gcp"]["progress"]
        if spec == "complete":
            return prog >= 100  # ← CHECKS FOR 100

# 8. Progress getter returns 0
# core/product_tile.py (line 52-56)
def _get_progress(state, key):
    return float(state.get(key, {}).get("progress", 0))  # ← state["gcp"] is {}
    # Returns: 0.0 ❌

# 9. Requirement fails, tile locks
# Result: Cost Planner shows as locked ❌
```

---

## 🔧 Why This Worked Before (But Doesn't Now)

### Legacy GCP (Old Architecture)
```python
# Old products wrote to session state directly
st.session_state["gcp"] = {
    "progress": 100,
    "care_tier": "in_home",
    "confidence": 0.95
}

# Unlock checks worked because data was in expected location
_get_progress(st.session_state, "gcp")  # → 100 ✅
```

### Modern GCP v4 (New Architecture)
```python
# New products publish to MCIP, don't write to session state
MCIP.publish_care_recommendation(recommendation)
# st.session_state["gcp"] = {}  ← EMPTY! ❌

# Unlock checks fail because data is in different location
_get_progress(st.session_state, "gcp")  # → 0 ❌
```

---

## 💡 Why It Works "Sometimes"

You said:
> "Module-to-module navigation within tiles works correctly"

**Why**: Internal product navigation (e.g., Cost Planner step 1 → step 2) doesn't check unlock requirements. Only hub-to-product navigation does.

**Also**: If you happen to have old session data in `st.session_state["gcp"]` from before the MCIP migration, the unlock check would work (by accident).

---

## 🎯 The Fix Strategy

### Option 1: Update Unlock Logic to Check MCIP (RECOMMENDED)

**Change**: Make `_evaluate_requirement` check MCIP first, fall back to legacy state

```python
# core/product_tile.py (line 59)
def _evaluate_requirement(req: str, state: Mapping[str, Any]) -> bool:
    if ":" not in req:
        return False

    key, spec = req.split(":", 1)
    key = key.strip()
    spec = spec.strip()

    # NEW: Check MCIP first for modern products
    if key in ("gcp", "cost", "pfma", "cost_planner", "pfma_v2"):
        # Try MCIP first (v2 architecture)
        from core.mcip import MCIP
        
        # Map keys to MCIP product IDs
        product_map = {
            "gcp": "gcp",
            "cost": "cost_planner",
            "cost_planner": "cost_planner",
            "pfma": "pfma_v2",
            "pfma_v2": "pfma_v2"
        }
        product_id = product_map.get(key, key)
        
        if spec == "complete":
            # Check MCIP first
            if MCIP.is_product_complete(product_id):
                return True
            
            # Fall back to legacy session state
            prog = _get_progress(state, key)
            return prog >= 100
        
        if spec.startswith(">="):
            # For progress checks, try both sources
            # MCIP doesn't track partial progress, so check legacy state
            prog = _get_progress(state, key)
            try:
                threshold = float(spec[2:].strip())
                return prog >= threshold
            except Exception:
                return False
        
        if spec == "scheduled":
            # Check MCIP appointment
            if key in ("pfma", "pfma_v2"):
                appt = MCIP.get_advisor_appointment()
                if appt and appt.scheduled:
                    return True
            
            # Fall back to legacy
            return state.get(key, {}).get("appointment") == "scheduled"

    # ... rest of function unchanged ...
```

**Benefits**:
- ✅ Works with both modern (MCIP) and legacy (session state) products
- ✅ Single point of fix (one file)
- ✅ Backward compatible
- ✅ Future-proof (can phase out legacy checks later)

**Drawbacks**:
- ❌ Adds MCIP dependency to product_tile.py (coupling)

---

### Option 2: Write to Both Systems (Bridge Pattern)

**Change**: Make GCP v4 write to BOTH MCIP and legacy session state

```python
# products/gcp_v4/product.py
def _publish_to_mcip(outcome, module_state: dict) -> None:
    # ... existing MCIP publishing ...
    
    # ALSO write to legacy session state for backward compatibility
    st.session_state["gcp"] = {
        "progress": 100,
        "care_tier": outcome_data["tier"],
        "confidence": outcome_data["confidence"],
        "tier_score": outcome_data["tier_score"],
        "completed_at": datetime.utcnow().isoformat()
    }
```

**Benefits**:
- ✅ Minimal changes (one file)
- ✅ No coupling between systems
- ✅ Works with existing unlock logic

**Drawbacks**:
- ❌ Maintains dual state (confusing, error-prone)
- ❌ Need to do this for Cost Planner v2 and PFMA v2 too
- ❌ Technical debt (two sources of truth)

---

### Option 3: Update Hub to Pass MCIP Completion to Tiles

**Change**: Make concierge.py determine lock state using MCIP, don't rely on unlock_requires

```python
# hubs/concierge.py (line 246)
def _build_cost_planner_tile(...):
    summary = MCIP.get_product_summary("cost_v2")
    
    # Determine lock state from MCIP, not from unlock_requires
    gcp_complete = MCIP.is_product_complete("gcp")
    is_locked = not gcp_complete
    
    return ProductTileHub(
        key="cost_v2",
        locked=is_locked,  # ← Explicitly set based on MCIP
        unlock_requires=[],  # ← Remove this (not needed)
        ...
    )
```

**Benefits**:
- ✅ Each hub controls its own unlock logic
- ✅ No changes to product_tile.py
- ✅ Clear separation of concerns

**Drawbacks**:
- ❌ Need to update every hub
- ❌ Loses declarative `unlock_requires` pattern
- ❌ Duplicate unlock logic across hubs

---

## 🏆 RECOMMENDED SOLUTION

**Use Option 1** (Update Unlock Logic to Check MCIP)

### Why:
1. **Single source of truth**: MCIP is the authoritative completion tracker
2. **Minimal changes**: One file (`core/product_tile.py`)
3. **Backward compatible**: Falls back to legacy state if MCIP empty
4. **Future-proof**: New products can use MCIP exclusively
5. **Maintains patterns**: Keeps declarative `unlock_requires` system

### Implementation Steps:

1. **Update `_evaluate_requirement` function** (core/product_tile.py, line 59)
   - Add MCIP import
   - Check `MCIP.is_product_complete()` before checking session state
   - Map keys to MCIP product IDs
   - Fall back to legacy `_get_progress()` for partial progress

2. **Add product key mappings**
   - `"gcp"` → MCIP `"gcp"`
   - `"cost"` or `"cost_planner"` → MCIP `"cost_planner"`
   - `"pfma"` or `"pfma_v2"` → MCIP `"pfma_v2"`

3. **Test completion flow**
   - Complete GCP → verify MCIP marks `"gcp"` complete
   - Return to hub → verify Cost Planner unlocked
   - Start Cost Planner → verify progress tracked
   - Return to hub → verify Cost Planner STAYS unlocked
   - Complete Cost Planner → verify PFMA unlocks

---

## 📝 Code Changes Required

### File 1: `core/product_tile.py`

**Location**: Line 59-100  
**Function**: `_evaluate_requirement()`

**Before**:
```python
def _evaluate_requirement(req: str, state: Mapping[str, Any]) -> bool:
    """
    Supported patterns:
      'gcp:complete'           -> progress == 100
      'cost:>=50'              -> progress >= 50
      'pfma:scheduled'         -> state['pfma']['appointment'] == 'scheduled'
      'care_tier:in_home|al|mc|mc_ha'
      'auth:required'          -> state['auth']['is_authenticated'] is True
    """
    if ":" not in req:
        return False

    key, spec = req.split(":", 1)
    key = key.strip()
    spec = spec.strip()

    if key in ("gcp", "cost", "pfma"):
        prog = _get_progress(state, key)
        if spec == "complete":
            return prog >= 100
        if spec.startswith(">="):
            try:
                return prog >= float(spec[2:].strip())
            except Exception:
                return False
        if spec == "scheduled":
            return state.get(key, {}).get("appointment") == "scheduled"
        return False
    # ... rest of function ...
```

**After**:
```python
def _evaluate_requirement(req: str, state: Mapping[str, Any]) -> bool:
    """
    Supported patterns:
      'gcp:complete'           -> MCIP.is_product_complete("gcp") OR progress == 100
      'cost:>=50'              -> progress >= 50
      'pfma:scheduled'         -> MCIP appointment OR state['pfma']['appointment']
      'care_tier:in_home|al|mc|mc_ha'
      'auth:required'          -> state['auth']['is_authenticated'] is True
    
    NOTE: Checks MCIP first for modern products, falls back to legacy session state.
    """
    if ":" not in req:
        return False

    key, spec = req.split(":", 1)
    key = key.strip()
    spec = spec.strip()

    # Check product completion/progress
    if key in ("gcp", "cost", "pfma", "cost_planner", "pfma_v2"):
        # Map keys to MCIP product IDs
        product_map = {
            "gcp": "gcp",
            "cost": "cost_planner",
            "cost_planner": "cost_planner",
            "pfma": "pfma_v2",
            "pfma_v2": "pfma_v2"
        }
        
        if spec == "complete":
            # FIRST: Check MCIP (authoritative source for modern products)
            try:
                from core.mcip import MCIP
                product_id = product_map.get(key, key)
                if MCIP.is_product_complete(product_id):
                    return True
            except Exception:
                pass  # Fall back to legacy check
            
            # FALLBACK: Check legacy session state (for old products or during migration)
            prog = _get_progress(state, key)
            return prog >= 100
        
        if spec.startswith(">="):
            # Partial progress checks (MCIP doesn't track these, use legacy state)
            prog = _get_progress(state, key)
            try:
                threshold = float(spec[2:].strip())
                return prog >= threshold
            except Exception:
                return False
        
        if spec == "scheduled":
            # FIRST: Check MCIP appointment
            if key in ("pfma", "pfma_v2"):
                try:
                    from core.mcip import MCIP
                    appt = MCIP.get_advisor_appointment()
                    if appt and appt.scheduled:
                        return True
                except Exception:
                    pass
            
            # FALLBACK: Check legacy session state
            return state.get(key, {}).get("appointment") == "scheduled"
        
        return False

    # ... rest of function unchanged (care_tier, auth, flag checks) ...
```

**Lines changed**: ~40 lines  
**Risk level**: Low (fallback logic ensures backward compatibility)

---

## 🧪 Testing Plan

### Test Case 1: Fresh User (No Legacy State)
```
1. Start app with clean session
2. Complete GCP care_recommendation
3. Return to Concierge Hub
   ✅ EXPECT: Cost Planner unlocked
4. Start Cost Planner, complete step 1
5. Return to Concierge Hub
   ✅ EXPECT: Cost Planner STILL unlocked
6. Resume Cost Planner
   ✅ EXPECT: Starts at step 2
7. Complete Cost Planner
8. Return to Concierge Hub
   ✅ EXPECT: PFMA unlocked
```

### Test Case 2: Migration User (Has Legacy State)
```
1. Load session with old st.session_state["gcp"] = {"progress": 100}
2. Also load MCIP with completed_products = ["gcp"]
3. Go to Concierge Hub
   ✅ EXPECT: Cost Planner unlocked (both systems agree)
4. Complete Cost Planner
   ✅ EXPECT: PFMA unlocks correctly
```

### Test Case 3: Partial Progress
```
1. Start GCP, answer 50% of questions
2. Return to Concierge Hub
   ✅ EXPECT: Cost Planner LOCKED (GCP not complete)
3. Resume GCP, complete remaining 50%
4. Return to Concierge Hub
   ✅ EXPECT: Cost Planner UNLOCKED
```

### Test Case 4: Multiple Browser Tabs
```
1. Open app in Tab A
2. Complete GCP
3. Open app in Tab B (same session)
   ✅ EXPECT: Cost Planner unlocked in BOTH tabs
4. Start Cost Planner in Tab A
5. Refresh Tab B
   ✅ EXPECT: Cost Planner shows progress in Tab B
```

---

## 🚀 Deployment Checklist

- [ ] **Backup current code** (commit everything)
- [ ] **Create feature branch** (`fix/unlock-logic-mcip-integration`)
- [ ] **Update `_evaluate_requirement`** in `core/product_tile.py`
- [ ] **Test locally** with fresh session (no legacy state)
- [ ] **Test with legacy session data** (backward compatibility)
- [ ] **Verify all 3 products** (GCP → Cost Planner → PFMA)
- [ ] **Test cross-tab session persistence**
- [ ] **Review error handling** (MCIP import, None checks)
- [ ] **Commit with clear message**
- [ ] **Push to dev branch**
- [ ] **Test in deployed environment**
- [ ] **Monitor MCIP state** (use debug_gcp.py or add logging)

---

## 📊 Impact Assessment

### High Impact (Fixed by this change)
- ✅ Cost Planner unlock after GCP completion
- ✅ PFMA unlock after Cost Planner completion
- ✅ Progress persistence across sessions
- ✅ Cross-tab session consistency

### Medium Impact (Improved)
- ✅ Cleaner architecture (single source of truth)
- ✅ Future products can rely on MCIP exclusively
- ✅ Easier debugging (check one place for completion state)

### Low Impact (No change)
- ⚠️ Internal product navigation (already works)
- ⚠️ Legacy products (will continue using session state)

---

## 🔮 Future Considerations

### Phase 2: Remove Legacy Session State
Once all products use MCIP:
1. Remove `_get_progress()` fallback in `_evaluate_requirement()`
2. Remove legacy session state writes
3. Simplify unlock logic (MCIP only)

### Phase 3: Centralized Unlock Configuration
Move unlock requirements to config file:
```json
// config/product_unlock_rules.json
{
  "cost_v2": {
    "requires": ["gcp:complete"],
    "lock_msg": "Complete Guided Care Plan first"
  },
  "pfma_v2": {
    "requires": ["cost_v2:complete"],
    "lock_msg": "Complete Cost Planner first"
  }
}
```

---

## ✅ Acceptance Criteria

1. **GCP completion persists**: After completing GCP, Cost Planner unlocks and STAYS unlocked
2. **Cost Planner completion persists**: After completing Cost Planner, PFMA unlocks and STAYS unlocked
3. **Progress tracking works**: Partial progress tracked, resumable
4. **Backward compatible**: Works with legacy session data (no breaking changes)
5. **Cross-tab consistent**: Session state synced across multiple tabs
6. **Error resilient**: Handles missing MCIP data gracefully (falls back to legacy)

---

**Status**: ✅ Ready for Implementation  
**Estimated Effort**: 1-2 hours (including testing)  
**Risk Level**: Low (fallback logic ensures safety)  
**Priority**: **CRITICAL** (blocking demo/production)

---

**Next Step**: Review this analysis, then implement Option 1 (Update Unlock Logic to Check MCIP)
