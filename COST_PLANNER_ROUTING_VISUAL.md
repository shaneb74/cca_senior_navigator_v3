# Cost Planner Routing & GCP Gate - Visual Reference

## Before Fix (BROKEN)

```
┌─────────────────────────────────────────────────────────────┐
│                    CONCIERGE HUB                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────┐             │
│  │  Cost Planner Tile                        │             │
│  │  Check: gcp_progress >= 100 ✅            │             │
│  │  Status: UNLOCKED (shows green)           │             │
│  │  Route: ?page=cost                        │             │
│  └───────────────┬───────────────────────────┘             │
│                  │                                          │
└──────────────────┼──────────────────────────────────────────┘
                   │ Click "Start"
                   ▼
┌─────────────────────────────────────────────────────────────┐
│         products/cost_planner/product.py:render()           │
├─────────────────────────────────────────────────────────────┤
│  OLD CHECK:                                                 │
│  gcp_rec = handoff["gcp"]["recommendation"]                 │
│                                                             │
│  if not gcp_rec:  ❌ FAILS!                                 │
│      Show "GCP Required" gate                               │
│                                                             │
│  Why? handoff might not be written yet from hub entry      │
└─────────────────────────────────────────────────────────────┘

RESULT: User sees "GCP Required" even though GCP is complete!
```

---

## After Fix (WORKING)

```
┌─────────────────────────────────────────────────────────────┐
│                    CONCIERGE HUB                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────┐             │
│  │  Cost Planner Tile                        │             │
│  │  Check: gcp_progress >= 100 ✅            │             │
│  │  Status: UNLOCKED (shows green)           │             │
│  │  Route: ?page=cost                        │             │
│  └───────────────┬───────────────────────────┘             │
│                  │                                          │
└──────────────────┼──────────────────────────────────────────┘
                   │ Click "Start"
                   ▼
┌─────────────────────────────────────────────────────────────┐
│         products/cost_planner/product.py:render()           │
├─────────────────────────────────────────────────────────────┤
│  NEW CHECK:                                                 │
│  gcp_progress = st.session_state["gcp"]["progress"]        │
│                                                             │
│  if gcp_progress < 100:  ✅ PASSES!                         │
│      # Skip gate                                            │
│                                                             │
│  Both use SAME source: session_state["gcp"]["progress"]    │
└─────────────────┬───────────────────────────────────────────┘
                  │ Gate bypassed
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Cost Planner Intro Page                        │
│              (base module, step 0)                          │
└─────────────────────────────────────────────────────────────┘

RESULT: User proceeds directly to Cost Planner! ✅
```

---

## Complete Flow (Both Paths)

```
┌─────────────────────────────────────────────────────────────┐
│                   USER COMPLETES GCP                        │
│              st.session_state["gcp"]["progress"] = 100      │
│         st.session_state["handoff"]["gcp"] = {...}          │
└─────────────┬───────────────────────────────┬───────────────┘
              │                               │
              │ Path A: Hub                   │ Path B: GCP Summary
              │                               │
              ▼                               ▼
┌─────────────────────────────┐   ┌─────────────────────────┐
│  Click "Back to Hub"        │   │  Click "Continue to     │
│  ↓                          │   │  Cost Planner"          │
│  Click Cost Planner Tile    │   │                         │
│  Route: ?page=cost          │   │  Route: ?page=cost      │
└─────────────┬───────────────┘   └───────────┬─────────────┘
              │                               │
              │ BOTH PATHS CONVERGE HERE      │
              └───────────────┬───────────────┘
                              ▼
              ┌───────────────────────────────┐
              │  products/cost_planner/       │
              │  product.py:render()          │
              │                               │
              │  Check: gcp_progress >= 100   │
              │  Result: ✅ PASS              │
              └───────────────┬───────────────┘
                              ▼
              ┌───────────────────────────────┐
              │  Cost Planner Intro           │
              │  (base module, step 0)        │
              └───────────────┬───────────────┘
                              │ Click Continue
                              ▼
              ┌───────────────────────────────┐
              │  Quick Estimate               │
              │  (base module, step 1)        │
              │  - Show GCP recommendation    │
              │  - Care type selector         │
              │  - "See My Estimate" button   │
              └───────────────┬───────────────┘
                              │ Click "See My Estimate"
                              ▼
              ┌───────────────────────────────┐
              │  Cost Breakdown Revealed      │
              │  Button → "Continue to Full   │
              │             Assessment"       │
              └───────────────┬───────────────┘
                              │ Click Continue
                              ▼
              ┌───────────────────────────────┐
              │  Auth Check                   │
              │  if authenticated:            │
              │    → Profile Flags (step 3)   │
              │  else:                        │
              │    → Auth Gate (step 2)       │
              └───────────────┬───────────────┘
                              │ After auth
                              ▼
              ┌───────────────────────────────┐
              │  Profile Flags                │
              │  (base module, step 3)        │
              │  - ZIP code                   │
              │  - Veteran status             │
              │  - Home ownership             │
              │  - Medicaid status            │
              └───────────────┬───────────────┘
                              │ Click Continue
                              ▼
              ┌───────────────────────────────┐
              │  Module Index                 │
              │  (base module, step 4)        │
              │  - Income (always)            │
              │  - Assets (always)            │
              │  - Insurance (always)         │
              │  - VA (if veteran)            │
              │  - Housing (if owner + care)  │
              │  - Medicaid (if enrolled)     │
              └───────────────────────────────┘
```

---

## Session State Structure

```javascript
st.session_state = {
  // GCP product state
  "gcp": {
    "progress": 100,              // ← Hub & Cost Planner both check this
    "_step": 5,
    "answers": {
      "care_type": "assisted_living",
      // ... other answers
    }
  },
  
  // Handoff data (written by module engine)
  "handoff": {
    "gcp": {
      "recommendation": "Assisted Living",  // ← Only written after completion
      "confidence": "High",
      "reasoning": "...",
      // ... other handoff data
    }
  },
  
  // Cost Planner product state
  "cost": {
    "progress": 0,
    "_step": 0,
    "answers": {}
  },
  
  // Auth state (mock)
  "auth": {
    "is_authenticated": false,
    "user_email": null
  }
}
```

---

## Key Insight: Why progress > handoff

**Module Progress (`st.session_state["gcp"]["progress"]`):**
- Set automatically by module engine on every step
- Increments: 0 → 20 → 40 → 60 → 80 → 100
- **Always reliable** - guaranteed to exist
- Updated in real-time as user progresses

**Handoff Data (`st.session_state["handoff"]["gcp"]`):**
- Written explicitly by module logic
- Only written when summary screen renders
- Requires `save_to_handoff()` call in module code
- **May not exist** if user exits before summary

**Conclusion:**
✅ Use `progress >= 100` for completion checks (reliable)  
❌ Don't use `handoff.recommendation` for gates (unreliable)

---

## Testing Matrix

| Entry Path | GCP Status | Gate Check | Expected Result | Status |
|-----------|-----------|-----------|----------------|--------|
| Hub tile | progress=0 | `< 100` | Show GCP Required | ✅ Pass |
| Hub tile | progress=100 | `>= 100` | Show Intro | 🧪 Test |
| GCP Summary CTA | progress=100 | `>= 100` | Show Intro | 🧪 Test |
| Direct URL | progress=0 | `< 100` | Show GCP Required | ✅ Pass |
| Direct URL | progress=100 | `>= 100` | Show Intro | 🧪 Test |

---

## Code Comparison

### OLD (Broken)
```python
# products/cost_planner/product.py line 39-42
gcp_handoff = st.session_state.get("handoff", {}).get("gcp", {})
gcp_rec = gcp_handoff.get("recommendation")

if not gcp_rec:
    # Show gate
```

**Problem:** Depends on handoff being written (unreliable)

### NEW (Fixed)
```python
# products/cost_planner/product.py line 39-42
gcp_progress = float(st.session_state.get("gcp", {}).get("progress", 0))

if gcp_progress < 100:
    # Show gate
```

**Solution:** Same check as hub tile (single source of truth)

---

## Deployment Checklist

- [x] Code fix implemented
- [x] Syntax validated (`py_compile` passed)
- [ ] Test Path A (Hub → Cost Planner)
- [ ] Test Path B (GCP Summary → Cost Planner)
- [ ] Test direct URL entry (unauthenticated)
- [ ] Verify gate shows when GCP not complete
- [ ] Verify gate bypassed when GCP complete
- [ ] Document in release notes

---

**Summary:** Single source of truth (`gcp_progress >= 100`) eliminates routing inconsistency. Both entry paths now use identical completion check.
