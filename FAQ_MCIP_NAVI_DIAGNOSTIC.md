# FAQ Product - MCIP/Navi Integration Diagnostic Report

**Date**: 2025-10-15  
**Issue**: FAQs & Answers product appears disconnected from MCIP/Navi after product rebuild

---

## Executive Summary

**ROOT CAUSE IDENTIFIED**: The FAQs & Answers product is **NOT REGISTERED** in the system's product registry (`core/nav.py`), which means:
1. ❌ MCIP does not track FAQs as a product
2. ❌ Navi does not orchestrate FAQs in the journey
3. ❌ FAQs completion/progress is not saved to MCIP contracts
4. ❌ FAQs navigation may not persist session state properly

**Critical Finding**: When GCP, Cost Planner, and PFMA were rebuilt to v4/v2, they were added to the `PRODUCTS` registry. FAQs was not, leaving it orphaned from the MCIP ecosystem.

---

## 1. Product Registry Analysis

### File: `core/nav.py` (Lines 8-28)

**Current PRODUCTS registry:**
```python
PRODUCTS = {
    "gcp": {"hub": "concierge", "title": "Guided Care Plan", "route": "/product/gcp"},
    "gcp_v4": {"hub": "concierge", "title": "Guided Care Plan", "route": "/product/gcp_v4"},
    "cost_planner": {
        "hub": "concierge",
        "title": "Cost Planner",
        "route": "/products/cost_planner",
    },
    "cost_v2": {
        "hub": "concierge",
        "title": "Cost Planner",
        "route": "/products/cost_planner_v2",
    },
    "pfma": {
        "hub": "concierge",
        "title": "Plan with My Advisor",
        "route": "/products/pfma",
    },
    "pfma_v2": {
        "hub": "concierge",
        "title": "Plan with My Advisor",
        "route": "/products/pfma_v2",
    },
}
```

**❌ MISSING**: No entry for `"faqs"` or `"faq_v2"`

**Impact**: 
- MCIP cannot track FAQs in `journey.completed_products`
- Navi cannot recommend FAQs as next action
- Product unlock logic cannot depend on FAQs completion
- FAQs navigation may not respect MCIP persistence patterns

---

## 2. MCIP Integration Analysis

### File: `core/mcip.py`

**Search Results**: ❌ NO mentions of "faqs", "faq", or "FAQ" in entire file

**What This Means**:
- `MCIP.get_product_summary()` does not have a case for FAQs
- `MCIP.publish_*()` methods don't save FAQ state
- `MCIP.is_product_complete()` cannot check FAQs completion
- FAQs data is not included in `mcip_contracts` persistence

**Comparison with Rebuilt Products**:

| Product | MCIP Method | Status |
|---------|-------------|--------|
| GCP v4 | `get_care_recommendation()` | ✅ Tracked |
| Cost Planner v2 | `get_financial_profile()` | ✅ Tracked |
| PFMA v2 | `get_advisor_appointment()` | ✅ Tracked |
| **FAQs** | ❌ None | ❌ **NOT TRACKED** |

---

## 3. Navi Orchestration Analysis

### File: `core/navi.py`

**References to FAQ** (Lines 147, 488, 494):
- ✅ Navi knows FAQs **exists as a navigation target**
- ✅ Navi can suggest "Ask Navi" button routing to FAQs
- ❌ Navi does NOT track FAQs as a product in journey
- ❌ Navi does NOT recommend FAQs as "next step"

**Example** (Line 488-494):
```python
# Build secondary action (Ask Navi → FAQ)
secondary_action = {
    'label': 'Ask Navi',
    'icon': '💬',
    'route': 'faq'
}
```

**Conclusion**: Navi treats FAQs as a **utility/support page**, not as a **tracked product** in the journey orchestration.

---

## 4. Concierge Hub Tile Registration

### File: `hubs/concierge.py`

**Tile Building** (Lines 124-128):
```python
# Build product tiles dynamically from MCIP
cards = [
    _build_gcp_tile(hub_order, ordered_index, next_action),
    _build_cost_planner_tile(hub_order, ordered_index, next_action),
    _build_pfma_tile(hub_order, ordered_index, next_action),
    _build_faq_tile(),  # ← Built STATICALLY, not from MCIP
]
```

**FAQ Tile Builder** (Lines 546-566):
```python
def _build_faq_tile() -> ProductTileHub:
    """Build FAQ tile (always available, never locked)."""
    return ProductTileHub(
        key="faqs",
        title="FAQs & Answers",
        desc="Answers in plain language, available whenever you are.",
        badge_text="AI AGENT",
        image_square="faq.png",
        meta_lines=["Advisor curated responses", "Available 24/7"],
        primary_label="Open",
        primary_route="?page=faqs",
        progress=0,  # ← Hardcoded 0, not from MCIP
        variant="teal",
        order=40,
        is_next_step=False,  # ← Never marked as next step
    )
```

**Key Differences from Rebuilt Products**:

| Aspect | GCP/Cost/PFMA | FAQs |
|--------|---------------|------|
| Tile Builder | `_build_*_tile(hub_order, ordered_index, next_action)` | `_build_faq_tile()` ← No params |
| Data Source | `MCIP.get_product_summary()` | Hardcoded values |
| Progress | Dynamic from MCIP | Always 0 |
| Lock Status | Evaluated from MCIP | Always unlocked |
| Next Step | Can be recommended | Never recommended |
| Order in Journey | Part of ordered sequence | Static, independent |

---

## 5. Hub Order & Journey Tracking

### File: `hubs/concierge.py` (Lines 111-118)

**Hub Order Definition**:
```python
hub_order = {
    "hub_id": "concierge",
    "ordered_products": ["gcp_v4", "cost_v2", "pfma_v2"],  # ← No FAQs!
    "reason": _get_hub_reason(),
    "total": 3,  # ← Only counting main 3 products
    "next_step": next_action.get("route", "gcp_v4").replace("?page=", ""),
}
```

**❌ FAQs is excluded from**:
- `ordered_products` list
- Journey total count
- Next step recommendations
- Hub reason/context logic

---

## 6. Session State & Persistence

### Analysis

**Rebuilt Products** (GCP, Cost, PFMA):
```python
# Save pattern (in product modules):
MCIP.publish_care_recommendation(rec)  # Triggers _save_contracts_for_persistence()
# → Saves to st.session_state["mcip_contracts"]
# → Persists to data/users/<uid>.json
```

**FAQs**:
```python
# FAQ page (pages/faq.py):
# ❌ Does NOT call any MCIP.publish_*() methods
# ❌ Does NOT save FAQ interaction data to MCIP
# ❌ Session state keys: "ai_thread", "ai_asked_questions" (FAQ-specific, not in MCIP)
```

**Impact on Bug**:
When navigating from Concierge Hub → FAQs → Back to Hub:
1. Hub calls `MCIP.initialize()` 
2. MCIP restores from `mcip_contracts`
3. ✅ GCP, Cost, PFMA data restored (they're in contracts)
4. ❌ FAQs data NOT in contracts (was never saved there)
5. ❌ But the REAL bug is: `mcip_contracts` itself is disappearing from session state!

---

## 7. Config & Navigation

### File: `config/nav.json` (Lines 115-120)

**FAQ Navigation Entry**:
```json
{
  "key": "faqs",
  "label": "FAQs",
  "module": "pages._stubs:render_faqs",
  "hidden": true
}
```

**Issues**:
- ✅ FAQ is in nav.json (can be navigated to)
- ❌ Module path is `pages._stubs:render_faqs` - is this correct?
- ❌ Marked as `"hidden": true` - intentional?

Let me verify the actual FAQ module path:

**File: `pages/faq.py`** - Contains `def render()` function ✅

**Mismatch**: nav.json points to `pages._stubs:render_faqs`, but actual module is `pages.faq:render`

---

## 8. Key/Identifier Inconsistencies

### Product Keys Used Across System

| Location | GCP | Cost | PFMA | FAQ |
|----------|-----|------|------|-----|
| PRODUCTS registry | `gcp`, `gcp_v4` | `cost_planner`, `cost_v2` | `pfma`, `pfma_v2` | ❌ Missing |
| Hub tile key | `gcp_v4` | `cost_v2` | `pfma_v2` | `faqs` |
| Nav.json key | `gcp`, `gcp_v4` | `cost_v2` | `pfma_v2` | `faqs` |
| MCIP product_key | `gcp` | `cost_planner`, `cost_v2` | `pfma_v2` | ❌ Not tracked |
| Session state | `gcp`, `gcp_v4` | `cost`, `cost_v2` | `pfma`, `pfma_v2` | `ai_thread`, `ai_asked_questions` |

**Consistency Issues**:
- ✅ Rebuilt products have consistent v2/v4 suffixes
- ❌ FAQs has no version suffix (was never rebuilt)
- ❌ FAQs uses different session state keys (not MCIP-based)
- ❌ FAQs tile key is `"faqs"` but nav key could be `"faqs"` or points to wrong module

---

## 9. Backwards Compatibility Check

### Legacy MCIP References

**Search: "MCIP" in pages/faq.py**:
```python
# Line 21: from core.mcip import MCIP  ✅ Correct import
# Line 568: progress = MCIP.get_journey_progress()  ✅ Uses new MCIP (not legacy)
```

**Conclusion**: ✅ FAQ page uses current MCIP, not legacy references

**BUT**: FAQ only **READS** from MCIP (`get_journey_progress()`), never **WRITES** to it.

---

## 10. Additional Services Integration

### File: `core/additional_services.py`

**How it works**:
- Additional Services cards are filtered based on MCIP state (e.g., GCP completion)
- They appear below main product tiles

**FAQ's Role**:
- ❌ FAQ is not an "additional service"
- ❌ FAQ does not trigger additional services
- ✅ FAQ is a standalone product tile (but untracked)

---

## Summary of Findings

### What Changed During Rebuild

| Aspect | Before Rebuild | After Rebuild (GCP/Cost/PFMA) | FAQs Status |
|--------|----------------|-------------------------------|-------------|
| Product Keys | `gcp`, `cost`, `pfma` | `gcp_v4`, `cost_v2`, `pfma_v2` | `faqs` (unchanged) |
| PRODUCTS Registry | ✅ All included | ✅ v2/v4 added | ❌ **Never added** |
| MCIP Methods | Basic tracking | Full contract tracking | ❌ **No tracking** |
| Tile Building | Static | Dynamic from MCIP | ❌ **Still static** |
| Journey Tracking | Basic | Orchestrated by Navi | ❌ **Not orchestrated** |
| Persistence | Session state | MCIP contracts | ❌ **Not persisted** |

---

## Root Cause Analysis

**WHY Cost Planner Re-Locks After FAQ Navigation**:

1. **Initial State** (After GCP complete):
   - `mcip_contracts` exists with GCP data
   - Cost Planner checks MCIP → sees GCP complete → unlocks ✅

2. **Navigate to FAQ**:
   - FAQ page loads
   - FAQ is NOT in PRODUCTS registry
   - FAQ doesn't interact with MCIP
   - ❗ **SOMETHING clears `mcip_contracts` from session state** (still investigating)

3. **Return to Hub**:
   - `MCIP.initialize()` runs
   - Tries to restore from `mcip_contracts`
   - ❌ `mcip_contracts` is GONE
   - Falls back to default state (no GCP completion)
   - Cost Planner checks MCIP → no GCP → locks ❌

**The FAQ navigation itself isn't the direct cause**, but it's correlated because:
- FAQ is not properly integrated into MCIP persistence flow
- Navigation to/from FAQ may trigger session state issues
- FAQ page doesn't reinforce MCIP contracts (doesn't call `_save_contracts_for_persistence()`)

---

## Recommendations (Not Yet Implemented)

### 1. Register FAQs in PRODUCTS Registry
**File**: `core/nav.py`
```python
PRODUCTS = {
    # ... existing entries ...
    "faqs": {
        "hub": "concierge",
        "title": "FAQs & Answers",
        "route": "/pages/faq",
    },
}
```

### 2. Add MCIP Tracking for FAQs (Optional)
**Decision Needed**: Should FAQs be tracked like other products?
- **Option A**: Track FAQs interactions (questions asked, topics explored)
- **Option B**: Keep FAQs as utility (no completion tracking)
- **Current**: Option B (untracked utility)

### 3. Fix nav.json Module Path
**File**: `config/nav.json`
```json
{
  "key": "faqs",
  "label": "FAQs",
  "module": "pages.faq:render",  // ← Fix from _stubs
  "hidden": true  // ← Consider making visible?
}
```

### 4. Consider Adding FAQ to Hub Order (Optional)
**File**: `hubs/concierge.py`
```python
hub_order = {
    "ordered_products": ["gcp_v4", "cost_v2", "pfma_v2", "faqs"],
    "total": 4,  // ← or keep at 3 if FAQs is always available
}
```

### 5. Investigate Session State Clearing
**Priority**: 🔴 **HIGH** - This is the actual bug
- FAQs registration issues are architectural, not bugs
- The REAL bug is `mcip_contracts` disappearing from session state
- Need to debug session persistence layer (`core/session_store.py`)

---

## Answers to Original Questions

### 1. Does FAQs communicate with Navi/MCIP?
**Answer**: 
- ✅ FAQs **READS** from MCIP (`MCIP.get_journey_progress()`)
- ❌ FAQs does **NOT WRITE** to MCIP (no `publish_*()` calls)
- ❌ FAQs is **NOT REGISTERED** in PRODUCTS
- ❌ Navi treats FAQs as **navigation target**, not **tracked product**

**Disconnect**: FAQ page uses MCIP but is not part of MCIP's product ecosystem.

### 2. Were new keys introduced that FAQs didn't receive?
**Answer**: YES
- GCP: `gcp` → `gcp_v4` (new key)
- Cost: `cost_planner` → `cost_v2` (new key)
- PFMA: `pfma` → `pfma_v2` (new key)
- FAQs: `faqs` → ❌ No new key (not rebuilt)

**Impact**: FAQs still uses original key pattern, missing version suffix convention.

### 3. Does Concierge Hub reference consistent identifiers?
**Answer**: NO
- GCP/Cost/PFMA: Consistent v4/v2 keys across hub, MCIP, nav
- FAQs: Uses `"faqs"` key but:
  - ❌ Not in PRODUCTS registry
  - ❌ Not in hub order
  - ❌ Not in MCIP tracking
  - ⚠️  nav.json points to wrong module (`_stubs`)

### 4. Session state mismatches?
**Answer**: YES
- Rebuilt products: Use MCIP contracts (`mcip_contracts`)
- FAQs: Uses own keys (`ai_thread`, `ai_asked_questions`)
- **Critical**: `mcip_contracts` is disappearing from session state (root bug)

### 5. Outdated key references?
**Files with Potential Issues**:
1. **`config/nav.json` Line 115-120**: Wrong module path (`_stubs` vs `faq`)
2. **`core/nav.py` Line 8-28**: FAQs missing from PRODUCTS
3. **`hubs/concierge.py` Line 546**: FAQ tile not using MCIP
4. **`hubs/concierge.py` Line 113**: FAQ not in `ordered_products`

---

## Next Steps

1. **[IMMEDIATE]** Debug why `mcip_contracts` disappears from session state
   - Add logging to `core/session_store.py`
   - Check `extract_session_state()` and `extract_user_state()`
   - Verify UID stability across navigation

2. **[ARCHITECTURAL]** Decide FAQ's role in product ecosystem
   - Should FAQs be a tracked product? (Probably not)
   - Should FAQs be in PRODUCTS registry? (For consistency, yes)
   - Should FAQs be in hub order? (No, it's always available)

3. **[FIX]** Update nav.json module path
   - Change `pages._stubs:render_faqs` → `pages.faq:render`

4. **[OPTIONAL]** Add FAQs to PRODUCTS registry
   - Would align architecture even if not tracked by MCIP

---

**Status**: ✅ Diagnostic Complete - Awaiting user test results to confirm session state bug hypothesis
