# Navi Continue Button Routing Fix

**Issue:** Navi's Continue button was routing to welcome page instead of recommended service  
**Cause:** Button was using `?route=` parameter instead of correct `?page=` parameter  
**Status:** ✅ FIXED

---

## Problem

The Navi panel Continue button label was correctly showing dynamic text like:
- "🧭 Create Your Guided Care Plan"
- "💰 Calculate Your Care Costs"
- "📅 Schedule Your Advisor Appointment"

But clicking the button always went to the welcome page instead of the recommended service.

---

## Root Cause

The button HTML was using incorrect routing parameter:
```html
<!-- WRONG -->
<a href="?route=gcp_v4">Create Your Guided Care Plan</a>
```

The app's routing system uses `?page=` parameter, not `?route=`:
```python
# core/nav.py
def current_route(default: str, pages: Dict[str, dict]) -> str:
    r = st.query_params.get("page", default)  # ← Uses "page" parameter
    return r if r in pages else default
```

---

## Solution

Updated `core/ui.py` line 692-703 to use `?page=` parameter:

```python
# Build action buttons HTML with correct routing parameter (?page=)
actions_html = ""
if secondary_action:
    primary_href = f"?page={primary_action.get('route', '')}" if primary_action.get('route') else "#"
    secondary_href = f"?page={secondary_action.get('route', '')}" if secondary_action.get('route') else "#"
    actions_html = f'<div style="display: flex; gap: 12px; margin-top: 18px;"><a class="dashboard-cta dashboard-cta--primary" href="{primary_href}" style="flex: 2;">{primary_action["label"]}</a><a class="dashboard-cta dashboard-cta--ghost" href="{secondary_href}" style="flex: 1;">{secondary_action["label"]}</a></div>'
else:
    primary_href = f"?page={primary_action.get('route', '')}" if primary_action.get('route') else "#"
    actions_html = f'<div style="margin-top: 18px;"><a class="dashboard-cta dashboard-cta--primary" href="{primary_href}" style="width: 100%; text-align: center;">{primary_action["label"]}</a></div>'
```

---

## How It Works Now

1. **MCIP** determines next action based on completion state:
   ```python
   # core/mcip.py
   return {
       "action": "💰 Calculate Your Care Costs",
       "reason": "Understand the financial side of your care plan.",
       "route": "cost_v2",  # ← This is the page key
       "status": "in_progress"
   }
   ```

2. **NaviOrchestrator** passes this to Navi panel:
   ```python
   # core/navi.py
   primary_label = next_action.get('action', 'Continue')
   primary_route = next_action.get('route', 'hub_concierge')
   primary_action = {
       'label': primary_label,
       'route': primary_route  # ← "cost_v2"
   }
   ```

3. **Navi Panel** renders button with correct URL:
   ```html
   <a href="?page=cost_v2">💰 Calculate Your Care Costs</a>
   ```

4. **App routing** detects `?page=cost_v2` and loads Cost Planner:
   ```python
   # app.py
   route = current_route("welcome", PAGES)  # Returns "cost_v2"
   # Loads pages._stubs:render_cost_v2()
   ```

---

## Expected Behavior

### Journey Progression

**Scenario 1: Starting Fresh**
- GCP: 0% complete
- Button says: "🧭 Create Your Guided Care Plan"
- Click → Goes to `?page=gcp_v4` → Loads GCP intro

**Scenario 2: GCP Complete**
- GCP: 100% complete
- Cost Planner: 0% complete
- Button says: "💰 Calculate Your Care Costs"
- Click → Goes to `?page=cost_v2` → Loads Cost Planner intro

**Scenario 3: Both Complete**
- GCP: 100% complete
- Cost Planner: 100% complete
- PFMA: 0% complete
- Button says: "📅 Schedule Your Advisor Appointment"
- Click → Goes to `?page=pfma_v2` → Loads PFMA scheduler

**Scenario 4: All Complete**
- All products: 100% complete
- Button says: "🎉 Journey Complete!"
- Click → Goes to `?page=hub_concierge` → Stays on concierge hub

---

## Files Changed

- **`core/ui.py`** (lines 692-703)
  - Changed `?route=` to `?page=` in button href attributes
  - Added clarifying comment about correct routing parameter

---

## Testing

### Manual Test Steps

1. **Test Fresh Start:**
   - Clear session state or use incognito
   - Go to Concierge Hub
   - Navi should show "Create Your Guided Care Plan"
   - Click button → Should load GCP (not welcome page)

2. **Test Mid-Journey:**
   - Complete GCP
   - Return to Concierge Hub
   - Navi should show "Calculate Your Care Costs"
   - Click button → Should load Cost Planner (not welcome page)

3. **Test Nearly Complete:**
   - Complete GCP and Cost Planner
   - Return to Concierge Hub
   - Navi should show "Schedule Your Advisor Appointment"
   - Click button → Should load PFMA (not welcome page)

4. **Test Complete:**
   - Complete all three products
   - Navi should show "🎉 Journey Complete!"
   - Click button → Should stay on Concierge Hub

---

## Related Issues

This also affects the secondary "Ask Navi →" button if present, which should route to FAQ:
```python
secondary_action = {
    'label': 'Ask Navi →',
    'route': 'faq'  # ← Will now correctly go to ?page=faq
}
```

---

**Status:** ✅ FIXED  
**Ready for:** Testing → Staging → Production
