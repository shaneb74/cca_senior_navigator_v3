# Journey Completion Fix - Implementation Plan
**Date:** November 2, 2025  
**Branch:** feature/dev-work  
**Strategy:** MCIP as Single Source of Truth

---

## Guiding Principles

1. **MCIP is the coordinator** - All completion tracking flows through `core/mcip.py`
2. **Single method for completion** - Only `MCIP.mark_product_complete(key)`
3. **Consistent product keys** - Use normalized keys per `core/flags.py` conventions
4. **Backward compatible** - Handle existing session state gracefully
5. **Surgical commits** - Small, testable changes with clear intent

---

## Phase 1: Standardize Product Keys

### Objective
Establish canonical product keys and update all references to use them consistently.

### Canonical Keys
```python
# Core products (as checked by hub_lobby)
"gcp"              # Guided Care Plan (not gcp_v4)
"cost_planner"     # Cost Planner (not cost_v2, cost_planner_v2)
"pfma"             # My Advisor (not pfma_v3)
"discovery_learning"  # Discovery Journey
"learn_recommendation"  # Learn About My Recommendation
```

### Changes

#### File: `core/mcip.py`
**Action:** Add key normalization helper at top of MCIP class

```python
# Product key normalization map
PRODUCT_KEY_MAP = {
    # GCP aliases
    "gcp_v4": "gcp",
    "gcp": "gcp",
    "guided_care_plan": "gcp",
    
    # Cost Planner aliases
    "cost_v2": "cost_planner",
    "cost_planner_v2": "cost_planner",
    "cost_intro": "cost_planner",
    "cost_planner": "cost_planner",
    
    # PFMA aliases
    "pfma_v3": "pfma",
    "pfma": "pfma",
    "my_advisor": "pfma",
    
    # Learning products
    "discovery_learning": "discovery_learning",
    "learn_recommendation": "learn_recommendation",
}

@classmethod
def _normalize_product_key(cls, product_key: str) -> str:
    """Normalize product key to canonical form.
    
    Args:
        product_key: Raw product key from caller
        
    Returns:
        Normalized canonical key
        
    Examples:
        >>> MCIP._normalize_product_key("gcp_v4")
        "gcp"
        >>> MCIP._normalize_product_key("cost_v2")
        "cost_planner"
    """
    return cls.PRODUCT_KEY_MAP.get(product_key, product_key)
```

**Action:** Update `mark_product_complete()` to normalize keys

```python
@classmethod
def mark_product_complete(cls, product_key: str) -> None:
    """Mark a product as completed.
    
    Args:
        product_key: Product identifier (will be normalized)
    """
    cls.initialize()
    
    # Normalize key to canonical form
    normalized_key = cls._normalize_product_key(product_key)
    
    journey = st.session_state[cls.STATE_KEY]["journey"]
    
    if normalized_key not in journey["completed_products"]:
        journey["completed_products"].append(normalized_key)
        print(f"[MCIP] Product '{product_key}' → '{normalized_key}' marked complete")
    
    # Save journey state for persistence
    cls._save_contracts_for_persistence()
    
    cls._fire_event("mcip.product.completed", {
        "product": normalized_key,
        "original_key": product_key
    })
```

**Action:** Update `is_product_complete()` to normalize keys

```python
@classmethod
def is_product_complete(cls, product_key: str) -> bool:
    """Check if a product is completed.
    
    Args:
        product_key: Product identifier (will be normalized)
        
    Returns:
        True if complete, False otherwise
    """
    cls.initialize()
    
    # Normalize key to canonical form
    normalized_key = cls._normalize_product_key(product_key)
    
    journey = st.session_state[cls.STATE_KEY]["journey"]
    return normalized_key in journey["completed_products"]
```

**Action:** Update `is_product_unlocked()` to normalize keys

```python
@classmethod
def is_product_unlocked(cls, product_key: str) -> bool:
    """Check if a product is unlocked.
    
    Args:
        product_key: Product identifier (will be normalized)
        
    Returns:
        True if unlocked, False otherwise
    """
    normalized_key = cls._normalize_product_key(product_key)
    return normalized_key in cls.get_unlocked_products()
```

**Files Modified:** 1
- `core/mcip.py`

**Commit Message:**
```
feat(mcip): add product key normalization for consistent completion tracking

- Add PRODUCT_KEY_MAP for canonical key mapping
- Update mark_product_complete() to normalize keys before storing
- Update is_product_complete() to normalize keys before checking
- Update is_product_unlocked() to normalize keys before checking
- Handles aliases: gcp_v4→gcp, cost_v2→cost_planner, pfma_v3→pfma

Fixes key mismatch issues preventing proper completion detection.
```

---

## Phase 2: Remove Legacy Completion Calls

### Objective
Replace all `core/events.py::mark_product_complete()` calls with `MCIP.mark_product_complete()`.

### Changes

#### File: `products/gcp_v4/modules/care_recommendation/logic.py`
**Lines:** 196-200, 268-272

**Current Code:**
```python
# Phase Post-CSS: Mark GCP product as complete when summary is ready
from core.events import mark_product_complete
user_ctx = st.session_state.get("user_ctx", {})
user_ctx = mark_product_complete(user_ctx, "gcp_v4")
st.session_state["user_ctx"] = user_ctx
```

**Replace With:**
```python
# Mark GCP as complete in MCIP
from core.mcip import MCIP
MCIP.mark_product_complete("gcp_v4")  # Will normalize to "gcp"
print("[GCP_SUMMARY] Marked GCP complete via MCIP")
```

**Action:** Apply this change at BOTH locations (lines ~196-200 and ~268-272)

#### File: `products/cost_planner_v2/exit.py`
**Lines:** 44-48

**Current Code:**
```python
# Phase Post-CSS: Mark cost planner product as complete
from core.events import mark_product_complete
user_ctx = st.session_state.get("user_ctx", {})
user_ctx = mark_product_complete(user_ctx, "cost_planner_v2")
st.session_state["user_ctx"] = user_ctx
```

**Replace With:**
```python
# Mark Cost Planner as complete in MCIP
from core.mcip import MCIP
MCIP.mark_product_complete("cost_planner_v2")  # Will normalize to "cost_planner"
print("[COST_EXIT] Marked Cost Planner complete via MCIP")
```

**Files Modified:** 2
- `products/gcp_v4/modules/care_recommendation/logic.py`
- `products/cost_planner_v2/exit.py`

**Commit Message:**
```
fix(completion): replace legacy mark_product_complete with MCIP method

GCP:
- Remove core.events import in care_recommendation/logic.py
- Use MCIP.mark_product_complete("gcp_v4") at both completion points
- Key will normalize to canonical "gcp"

Cost Planner:
- Remove core.events import in exit.py
- Use MCIP.mark_product_complete("cost_planner_v2")
- Key will normalize to canonical "cost_planner"

All products now use single completion coordination through MCIP.
```

---

## Phase 3: Add Missing Product to Completed Tiles

### Objective
Ensure `learn_recommendation` appears in "My Completed Journeys" when finished.

### Changes

#### File: `hubs/hub_lobby.py`
**Lines:** 507-512

**Current Code:**
```python
# Check each major product for completion
all_products = [
    ("discovery_learning", "Discovery Journey", "Your introduction to care planning"),
    ("gcp_v4", "Guided Care Plan", "Your personalized care recommendation"),
    ("cost_v2", "Cost Planner", "Your financial plan and projections"),
    ("pfma_v3", "My Advisor", "Your advisor consultation"),
]
```

**Replace With:**
```python
# Check each major product for completion
all_products = [
    ("discovery_learning", "Discovery Journey", "Your introduction to care planning"),
    ("gcp", "Guided Care Plan", "Your personalized care recommendation"),
    ("learn_recommendation", "Learn About My Recommendation", "Understanding your care option"),
    ("cost_planner", "Cost Planner", "Your financial plan and projections"),
    ("pfma", "My Advisor", "Your advisor consultation"),
]
```

**Note:** Update keys to use canonical forms (gcp, cost_planner, pfma) since MCIP normalization will store them that way.

**Files Modified:** 1
- `hubs/hub_lobby.py`

**Commit Message:**
```
fix(hub): add learn_recommendation to completed journeys and use canonical keys

- Add "Learn About My Recommendation" to completed tiles builder
- Update all product keys to canonical forms (gcp, cost_planner, pfma)
- Ensures MCIP completion detection works correctly
- Learn Recommendation now moves to Completed Journeys section
```

---

## Phase 4: Verify Product Completion Calls

### Objective
Ensure all products call `MCIP.mark_product_complete()` with correct keys.

### Audit Results

| Product | File | Line | Current Call | Status |
|---------|------|------|--------------|--------|
| Discovery Learning | `products/discovery_learning/product.py` | 308 | `MCIP.mark_product_complete("discovery_learning")` | ✅ Correct |
| GCP | `products/gcp_v4/product.py` | 559 | `MCIP.mark_product_complete("gcp")` | ✅ Correct |
| Learn Recommendation | `products/learn_recommendation/product.py` | 330 | `MCIP.mark_product_complete("learn_recommendation")` | ✅ Correct |
| Cost Planner | `products/cost_planner_v2/hub.py` | 1394 | `MCIP.mark_product_complete("cost_v2")` | ⚠️ Non-canonical key |
| PFMA | `products/pfma_v3/product.py` | 323 | `MCIP.mark_product_complete("pfma_v3")` | ⚠️ Non-canonical key |

### Changes

#### File: `products/cost_planner_v2/hub.py`
**Line:** 1394

**Current:**
```python
MCIP.mark_product_complete("cost_v2")
```

**Replace With:**
```python
MCIP.mark_product_complete("cost_planner")
print("[COST_HUB] Marked Cost Planner complete")
```

**Note:** While normalization will handle "cost_v2", using canonical key makes code clearer.

#### File: `products/pfma_v3/product.py`
**Line:** 323

**Current:**
```python
MCIP.mark_product_complete("pfma_v3")
```

**Replace With:**
```python
MCIP.mark_product_complete("pfma")
print("[PFMA] Marked PFMA/My Advisor complete")
```

**Files Modified:** 2
- `products/cost_planner_v2/hub.py`
- `products/pfma_v3/product.py`

**Commit Message:**
```
refactor(completion): use canonical product keys in completion calls

- Cost Planner: Use "cost_planner" instead of "cost_v2"
- PFMA: Use "pfma" instead of "pfma_v3"
- Add debug logging for completion tracking
- Improves code clarity and consistency
```

---

## Phase 5: Deprecate Legacy System

### Objective
Mark `core/events.py::mark_product_complete()` as deprecated and add migration notes.

### Changes

#### File: `core/events.py`
**Lines:** 73-103

**Current Function:**
```python
def mark_product_complete(user_ctx: dict, product_key: str) -> dict:
    """Mark a product complete and auto-update its parent journey.
    
    Phase Post-CSS: Consolidates completion logic for products and journeys.
    When all products in a journey are complete, the journey auto-completes.
    
    Args:
        user_ctx: User context dictionary
        product_key: Product identifier (e.g., "cost_planner", "guided_care_plan")
    
    Returns:
        Updated user context
    """
```

**Add Deprecation Notice:**
```python
def mark_product_complete(user_ctx: dict, product_key: str) -> dict:
    """DEPRECATED: Use MCIP.mark_product_complete() instead.
    
    This function is maintained for backward compatibility only.
    All new code should use core.mcip.MCIP.mark_product_complete().
    
    Legacy function that marks a product complete in user_ctx structure.
    
    Args:
        user_ctx: User context dictionary (legacy)
        product_key: Product identifier
    
    Returns:
        Updated user context
        
    Migration:
        # Old way (deprecated)
        user_ctx = mark_product_complete(user_ctx, "gcp_v4")
        st.session_state["user_ctx"] = user_ctx
        
        # New way (correct)
        from core.mcip import MCIP
        MCIP.mark_product_complete("gcp")
    """
    import warnings
    warnings.warn(
        "mark_product_complete() is deprecated. Use MCIP.mark_product_complete() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Keep original implementation for backward compatibility
    journeys = user_ctx.setdefault("journeys", {})
    # ... rest of function unchanged ...
```

**Files Modified:** 1
- `core/events.py`

**Commit Message:**
```
deprecate(events): mark legacy mark_product_complete as deprecated

- Add deprecation warning to core.events.mark_product_complete()
- Document migration path to MCIP.mark_product_complete()
- Keep function for backward compatibility with existing sessions
- All new code should use MCIP coordination
```

---

## Phase 6: Remove Hub Lobby Key Normalization

### Objective
Since MCIP now handles normalization, simplify hub_lobby logic.

### Changes

#### File: `hubs/hub_lobby.py`
**Lines:** 195-209

**Current Code:**
```python
# Normalize product keys (handle aliases)
key_map = {
    'gcp_v4': 'gcp',
    'gcp': 'gcp',
    'cost_v2': 'cost_planner',
    'cost_planner': 'cost_planner',
    'cost_intro': 'cost_planner',
    'pfma_v3': 'pfma',
    'pfma': 'pfma',
}

normalized_key = key_map.get(product_key, product_key)
```

**Replace With:**
```python
# MCIP handles key normalization - pass through directly
# Note: MCIP._normalize_product_key() will handle all aliases
normalized_key = product_key
```

**Alternative (More Explicit):**
```python
# Delegate normalization to MCIP
from core.mcip import MCIP
normalized_key = MCIP._normalize_product_key(product_key)
```

**Recommendation:** Use the explicit version to maintain clear data flow.

**Files Modified:** 1
- `hubs/hub_lobby.py`

**Commit Message:**
```
refactor(hub): delegate product key normalization to MCIP

- Remove local key_map in _get_product_state()
- Use MCIP._normalize_product_key() for consistent normalization
- Single source of truth for product key mapping
- Reduces code duplication
```

---

## Phase 7: Testing & Verification

### Manual Test Checklist

**Setup:**
1. Clear browser cache and session state
2. Start fresh user session

**Test Flow:**
```
┌─────────────────────────────────────┐
│ 1. Discovery Learning               │
│    - Complete the journey           │
│    - Return to Lobby                │
│    ✓ Should appear in "Completed"   │
│    ✓ Should NOT be in "Active"      │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ 2. Guided Care Plan                 │
│    - Complete all questions         │
│    - Reach recommendation page      │
│    - Return to Lobby                │
│    ✓ Should appear in "Completed"   │
│    ✓ Should NOT be in "Planning"    │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ 3. Learn Recommendation (NEW)       │
│    - Complete the learning module   │
│    - Return to Lobby                │
│    ✓ Should appear in "Completed"   │
│    ✓ Should NOT be in "Planning"    │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ 4. Cost Planner                     │
│    - Complete all modules           │
│    - Reach exit/summary page        │
│    - Return to Lobby                │
│    ✓ Should appear in "Completed"   │
│    ✓ Should NOT be in "Planning"    │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ 5. My Advisor (PFMA)                │
│    - Book appointment               │
│    - Complete booking flow          │
│    - Return to Lobby                │
│    ✓ Should appear in "Completed"   │
│    ✓ Should NOT be in "Planning"    │
└─────────────────────────────────────┘
```

### Automated Test Cases

#### Test: Product Key Normalization
```python
def test_mcip_key_normalization():
    """Test that MCIP normalizes product keys correctly."""
    from core.mcip import MCIP
    
    assert MCIP._normalize_product_key("gcp_v4") == "gcp"
    assert MCIP._normalize_product_key("gcp") == "gcp"
    assert MCIP._normalize_product_key("cost_v2") == "cost_planner"
    assert MCIP._normalize_product_key("cost_planner_v2") == "cost_planner"
    assert MCIP._normalize_product_key("pfma_v3") == "pfma"
    assert MCIP._normalize_product_key("unknown") == "unknown"
```

#### Test: Completion with Aliases
```python
def test_completion_with_aliases(mock_st, session):
    """Test that completion works with any key alias."""
    from core.mcip import MCIP
    
    MCIP.initialize()
    
    # Mark complete with alias
    MCIP.mark_product_complete("gcp_v4")
    
    # Check with canonical key
    assert MCIP.is_product_complete("gcp")
    
    # Check with alias
    assert MCIP.is_product_complete("gcp_v4")
    
    # Verify stored as canonical
    journey = st.session_state["mcip"]["journey"]
    assert "gcp" in journey["completed_products"]
    assert "gcp_v4" not in journey["completed_products"]
```

#### Test: Hub Shows Completed Products
```python
def test_hub_shows_completed_products(mock_st, session):
    """Test that hub correctly shows completed products."""
    from core.mcip import MCIP
    from hubs.hub_lobby import _build_completed_tiles, _build_planning_tiles
    
    MCIP.initialize()
    
    # Mark GCP complete
    MCIP.mark_product_complete("gcp")
    
    # Get tiles
    completed = _build_completed_tiles()
    planning = _build_planning_tiles()
    
    # Verify GCP in completed, not in planning
    completed_keys = [t.key for t in completed]
    planning_keys = [t.key for t in planning]
    
    assert "gcp" in completed_keys
    assert "gcp" not in planning_keys
```

### Test Locations
- `tests/test_mcip.py` - Add normalization and completion tests
- `tests/test_hub_lobby.py` - Add tile filtering tests
- Manual test in local dev environment

---

## Phase 8: Documentation Updates

### Files to Update

#### 1. `core/mcip.py` - Docstring
Add section at top of file:

```python
"""
MCIP (Multi-Channel Integration Protocol) Contract Manager

Central coordinator for product state, journey tracking, and completion status.

Product Completion:
    All products should mark completion through MCIP.mark_product_complete(key).
    Keys are automatically normalized to canonical forms:
    - "gcp_v4", "guided_care_plan" → "gcp"
    - "cost_v2", "cost_planner_v2" → "cost_planner"
    - "pfma_v3", "my_advisor" → "pfma"
    
    Example:
        from core.mcip import MCIP
        MCIP.mark_product_complete("gcp_v4")  # Stored as "gcp"
        
    Hub lobby and all UI components check MCIP for completion state.
    
Contract Structure:
    - care_recommendation: Published GCP results
    - financial_profile: Cost Planner data
    - advisor_appointment: PFMA booking info
    - journey: Unlocked/completed products, recommended next steps
"""
```

#### 2. `.github/copilot-instructions.md`
Add section under "Canonical Paths":

```markdown
## Product Completion (Source of Truth)
- **Completion coordinator:** `core/mcip.py::MCIP.mark_product_complete()`
- **Canonical keys:** `gcp`, `cost_planner`, `pfma`, `discovery_learning`, `learn_recommendation`
- **NEVER use:** Legacy `core/events.py::mark_product_complete()` (deprecated)
- **Key normalization:** Handled automatically by MCIP
```

#### 3. Add to "Things to Avoid":

```markdown
- Don't call `core.events.mark_product_complete()` - use `MCIP.mark_product_complete()` instead
- Don't use versioned product keys (gcp_v4, cost_v2) - MCIP normalizes automatically
```

**Files Modified:** 2
- `core/mcip.py`
- `.github/copilot-instructions.md`

**Commit Message:**
```
docs(mcip): document canonical product keys and completion coordination

- Add product completion section to MCIP docstring
- Document canonical key mappings and normalization
- Update Copilot instructions to use MCIP for completion
- Mark legacy events.py pattern as deprecated
```

---

## Rollout Strategy

### Commit Sequence

```
1. feat(mcip): add product key normalization for consistent completion tracking
   └─ Phase 1: Core MCIP normalization logic

2. fix(completion): replace legacy mark_product_complete with MCIP method
   └─ Phase 2: Remove legacy calls in GCP and Cost Planner

3. fix(hub): add learn_recommendation to completed journeys and use canonical keys
   └─ Phase 3: Update hub_lobby completed tiles

4. refactor(completion): use canonical product keys in completion calls
   └─ Phase 4: Update remaining products to use canonical keys

5. deprecate(events): mark legacy mark_product_complete as deprecated
   └─ Phase 5: Add deprecation warnings

6. refactor(hub): delegate product key normalization to MCIP
   └─ Phase 6: Remove duplicate normalization in hub

7. docs(mcip): document canonical product keys and completion coordination
   └─ Phase 7 & 8: Testing and documentation
```

### Testing Between Commits

After each commit:
1. Run app locally
2. Test affected product completion
3. Verify hub_lobby shows correct state
4. Check browser console for errors

### Rollback Plan

Each phase is independently reversible:
- Phase 1-2: Revert commits, legacy system still works
- Phase 3-4: Revert commits, old keys still detected
- Phase 5-6: Revert commits, no breaking changes

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Session state migration issues | Low | Medium | MCIP.initialize() handles missing keys |
| Product not marking complete | Low | High | Each phase tested independently |
| Key mismatch after normalization | Low | Low | Comprehensive normalization map |
| Legacy user_ctx conflicts | Low | Low | Deprecated function still works |
| Hub not showing completed products | Medium | High | Test after each commit |

---

## Success Criteria

### Definition of Done

- [ ] All products use `MCIP.mark_product_complete()` exclusively
- [ ] No calls to legacy `core.events.mark_product_complete()`
- [ ] Product keys normalized consistently (gcp, cost_planner, pfma)
- [ ] Learn Recommendation tracked in completed journeys
- [ ] Hub lobby shows completed products in "My Completed Journeys"
- [ ] Hub lobby removes completed products from active sections
- [ ] Tests pass for normalization and completion flow
- [ ] Documentation updated in MCIP and Copilot instructions
- [ ] Manual test flow completed successfully
- [ ] No console errors or warnings

### Verification Commands

```bash
# Check for legacy calls (should return 0 results after Phase 2)
grep -r "from core.events import mark_product_complete" products/

# Check for non-canonical keys in completion calls
grep -r 'mark_product_complete("gcp_v4")' products/
grep -r 'mark_product_complete("cost_v2")' products/
grep -r 'mark_product_complete("pfma_v3")' products/

# Verify MCIP normalization exists
grep -A 5 "def _normalize_product_key" core/mcip.py
```

---

## Timeline Estimate

| Phase | Effort | Risk |
|-------|--------|------|
| Phase 1: Key normalization | 30 min | Low |
| Phase 2: Remove legacy calls | 20 min | Low |
| Phase 3: Update hub completed tiles | 10 min | Low |
| Phase 4: Canonical keys in products | 15 min | Low |
| Phase 5: Deprecate legacy | 10 min | Low |
| Phase 6: Remove hub normalization | 10 min | Low |
| Phase 7: Testing | 45 min | Medium |
| Phase 8: Documentation | 20 min | Low |
| **Total** | **~2.5 hours** | **Low** |

---

## Post-Implementation

### Monitoring

Watch for these in logs after deployment:
```
[MCIP] Product 'gcp_v4' → 'gcp' marked complete
[GCP_SUMMARY] Marked GCP complete via MCIP
[COST_EXIT] Marked Cost Planner complete via MCIP
```

### Future Enhancements

1. **Journey-level completion** - Auto-complete "Discovery" or "Planning" journey when all products done
2. **Completion analytics** - Track which products users complete most/least
3. **Completion badges** - Award achievements for completing journeys
4. **Restart tracking** - Track how often users restart products

---

## Questions for Review

1. Should we add journey-level completion in this PR or defer to future work?
2. Do we want to migrate existing user_ctx data to MCIP, or just handle new sessions?
3. Should `_normalize_product_key()` be public API or internal helper?
4. Any other products besides the 5 tracked ones that need completion handling?

---

**Ready for Review and Approval**
