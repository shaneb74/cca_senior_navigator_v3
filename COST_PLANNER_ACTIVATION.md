# Cost Planner Activation Guide

**Status:** 🔒 **HIDDEN** (Awaiting MCIP approval)  
**Date Hidden:** October 12, 2025

---

## Overview

The Cost Planner additional service tile is currently **hidden from production** until the Medical Care Integration Partner (MCIP) approves its activation.

---

## Current State

### Where It's Hidden
- **File:** `core/additional_services.py`
- **Tile Key:** `cost_planner_recommend`
- **Visibility Rule:** Requires flag `cost_planner_enabled=True`

### Code Location
```python
{
    "key": "cost_planner_recommend",
    "type": "product",
    "title": "Cost Planner",
    "subtitle": "Estimate monthly costs based on your {recommendation} recommendation.",
    "cta": "Start planning",
    "go": "cost_open",
    "order": 15,
    "hubs": ["concierge"],
    "visible_when": [
        # Hidden until MCIP approves activation
        {"includes": {"path": "flags", "value": "cost_planner_enabled"}},
    ],
}
```

---

## How to Enable (When MCIP Approves)

### Option 1: Enable Globally for All Users

Edit `core/additional_services.py` line ~240:

**Change from:**
```python
"visible_when": [
    {"includes": {"path": "flags", "value": "cost_planner_enabled"}},
],
```

**Change to:**
```python
"visible_when": [
    {"min_progress": {"path": "gcp.progress", "value": 100}},
    {"equals": {"path": "cost.progress", "value": 0}},
],
```

This will show Cost Planner to all users who:
- ✅ Completed GCP (100% progress)
- ✅ Haven't started Cost Planner yet (0% progress)

### Option 2: Enable for Specific Users (Beta Testing)

Add the flag to specific user sessions in `core/state.py` or during hub rendering:

```python
# In ensure_session() or user onboarding logic
if user_is_in_beta_group():
    st.session_state.setdefault("handoff", {}).setdefault("flags", {})
    st.session_state["handoff"]["flags"]["cost_planner_enabled"] = True
```

### Option 3: Enable via Feature Flag System (Future)

When you implement a feature flag system:

```python
from core.feature_flags import is_enabled

if is_enabled("cost_planner"):
    # Show tile
    pass
```

---

## Testing the Change

### After Enabling:

1. **Clear Session State:**
   ```python
   # In Streamlit app
   st.cache_data.clear()
   st.cache_resource.clear()
   # Or restart the app
   ```

2. **Complete GCP:**
   - Navigate to Concierge Hub
   - Complete Guided Care Plan (100%)
   - Return to Concierge Hub

3. **Verify Tile Appears:**
   - Look for "Cost Planner" tile in Additional Services section
   - Should show after GCP tile
   - Subtitle should reference your care recommendation

4. **Click Through:**
   - Click "Start planning"
   - Verify it navigates to `/product/cost`
   - Check for any errors in console

---

## Why It's Hidden

The Cost Planner product logic is implemented but requires:
- ✅ **VA Benefits module** - Currently returns placeholder data
- ✅ **Quick Estimate module** - Currently returns placeholder data
- ⏳ **MCIP approval** - Waiting for medical partner sign-off
- ⏳ **Cost calculation validation** - Verify accuracy with real data
- ⏳ **Regional customization** - Adjust for geographic cost variations

---

## Monitoring After Activation

### Week 1 Metrics:
- [ ] Track Cost Planner start rate
- [ ] Monitor completion rate
- [ ] Check for error rates
- [ ] Gather user feedback

### Analytics to Watch:
```python
# Track in core/events.py
log_event("cost_planner.started", {"from": "additional_services"})
log_event("cost_planner.completed", {"total_cost": cost})
log_event("cost_planner.abandoned", {"step": current_step})
```

---

## Rollback Plan

If issues arise after activation:

### Quick Disable:
```python
# In core/additional_services.py
"visible_when": [
    {"includes": {"path": "flags", "value": "cost_planner_disabled_emergency"}},
],
```

This will hide it immediately (default false = hidden).

### Full Revert:
```bash
git revert <commit-hash>
git push origin main
```

---

## Contact

**Questions about activation?**
- Product Owner: _____________
- Technical Lead: Shane
- MCIP Contact: _____________

**Ready to activate?**
1. Get MCIP sign-off
2. Update this document with approval details
3. Follow "How to Enable" steps above
4. Monitor metrics for 48 hours

---

## Sign-Off

**MCIP Approval:** _____________  
**Date:** _____________  
**Activation By:** _____________  
**Date Activated:** _____________  

**Status After Activation:**
- [ ] Tile visible in Concierge Hub
- [ ] Analytics tracking confirmed
- [ ] Error monitoring in place
- [ ] Rollback plan tested

---

*Last Updated: October 12, 2025*
