# 5-Tier System - Quick Reference Card

## The 5 Tiers (Memorize These)

```
┌──────────────────────────────────────────────────────────────┐
│  #1  │  No Care Needed           │  0-8 pts   │  ~$500/mo   │
│  #2  │  In-Home Care             │  9-16 pts  │  ~$3,500/mo │
│  #3  │  Assisted Living          │  17-24 pts │  ~$4,500/mo │
│  #4  │  Memory Care              │  25-39 pts │  ~$6,500/mo │
│  #5  │  Memory Care (High Acuity)│  40-100pts │  ~$9,000/mo │
└──────────────────────────────────────────────────────────────┘
```

## Internal Keys (For Code)

```python
VALID_TIERS = {
    'no_care_needed',           # 0-8
    'in_home',                  # 9-16
    'assisted_living',          # 17-24
    'memory_care',              # 25-39
    'memory_care_high_acuity'   # 40-100
}
```

## Display Names (For UI)

```python
tier_labels = {
    "no_care_needed": "No Care Needed",
    "in_home": "In-Home Care",
    "assisted_living": "Assisted Living",
    "memory_care": "Memory Care",
    "memory_care_high_acuity": "Memory Care (High Acuity)"
}
```

## Boundaries (Important!)

| Boundary | Tier Below | Tier Above |
|----------|------------|------------|
| **8 pts** | No Care Needed | In-Home Care |
| **16 pts** | In-Home Care | Assisted Living |
| **24 pts** | Assisted Living | Memory Care |
| **39 pts** | Memory Care | Memory Care (High Acuity) |

## Quick Tests

### Test 1: Low Score (5 points)
**Expected:** "No Care Needed"
**Message:** "✓ No formal care is needed at this time..."

### Test 2: Boundary (17 points)
**Expected:** "Assisted Living"
**Clarity:** 0% (at boundary)

### Test 3: High Score (45 points)
**Expected:** "Memory Care (High Acuity)"

## Files to Know

| File | What It Does |
|------|--------------|
| `products/gcp_v4/.../logic.py` | **CORE LOGIC** - calculates tier from score |
| `core/mcip.py` | Publishes tier to all products |
| `products/cost_planner_v2/intro.py` | Quick estimate dropdown |
| `...cost_calculator.py` | Pricing by tier |
| `core/modules/engine.py` | Results display |
| `hubs/concierge.py` | Hub messaging |

## Common Tasks

### Add New Tier? (Don't!)
**Current:** 5 tiers is fixed by user requirement
**If you must:** Update all 8 files + tests + docs

### Change Thresholds?
**File:** `products/gcp_v4/modules/care_recommendation/logic.py`
**Constant:** `TIER_THRESHOLDS`
**Also update:** Confidence improvement in `core/modules/engine.py`

### Change Display Name?
**Find & replace in 7 files:**
1. logic.py (tier_labels)
2. mcip.py (tier_map)
3. intro.py (selectbox options + care_type_map)
4. cost_calculator.py (pricing keys)
5. engine.py (mapping dict)
6. concierge.py (tier_map)
7. module.json (intro content)

### Add Validation?
Already done! See `_determine_tier()` in logic.py:
```python
if tier not in VALID_TIERS:
    raise ValueError(f"Invalid tier '{tier}'...")
```

## Debugging

### User sees wrong tier name?
1. Check terminal for ValueError
2. Check MCIP context: `st.write(MCIP.get_care_recommendation())`
3. Check tier_map in the relevant file
4. Verify score calculation

### Cost Planner missing tier?
1. Check `intro.py` selectbox options
2. Check `care_type_map` mapping
3. Check `cost_calculator.py` has pricing for tier

### Hub shows "Independent"?
**Likely:** Legacy data from old session
**Fix:** Clear session state or retake GCP

## Testing Checklist (Minimal)

- [ ] Complete GCP with 5 points → "No Care Needed"
- [ ] Complete GCP with 14 points → "In-Home Care"
- [ ] Complete GCP with 20 points → "Assisted Living"
- [ ] Complete GCP with 30 points → "Memory Care"
- [ ] Complete GCP with 45 points → "Memory Care (High Acuity)"
- [ ] Cost Planner dropdown shows all 5 tiers
- [ ] Hub displays correct tier
- [ ] No terminal errors

## Emergency Contacts

**Full Docs:** `GCP_5_TIER_SYSTEM_IMPLEMENTATION.md`
**Testing:** `GCP_5_TIER_TESTING_GUIDE.md`
**Deployment:** `GCP_5_TIER_DEPLOYMENT_SUMMARY.md`
**Commit:** 72c5f0c, 1314d41
**App:** http://localhost:8501

---

**Pro Tip:** These 5 tier names are **non-negotiable**. Don't add, remove, or rename without updating ALL 8 integration points.

