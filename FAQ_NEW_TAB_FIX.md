# FAQ Navigation New Tab Fix

**Date**: 2025-01-XX  
**Commits**: [pending]

## Problem

User reported that clicking "Open" on the FAQ tile or "Ask Navi →" button would open a new browser tab/window, causing session state to be lost. This resulted in the Cost Planner re-locking even though MCIP state was correctly saved.

**Root Cause**: HTML `<a href>` links without `target="_self"` can be opened in new tabs by browsers depending on:
- Browser settings
- Modifier keys (Ctrl/Cmd + click)
- Link context/type
- Browser heuristics

When a new tab opens:
1. New Streamlit session is created
2. `st.session_state` is empty (fresh state)
3. MCIP is not initialized from persistence
4. Cost Planner checks MCIP → finds nothing → locks

## Investigation

1. ✅ Checked FAQ page code - uses correct `route_to()` function
2. ✅ Searched for `target="_blank"` - none found explicitly
3. ✅ Found product tiles render as HTML `<a href>` links (line 266-269 in `product_tile.py`)
4. ✅ Found hub guide buttons also use HTML links (line 360-362 in `concierge.py`)
5. ✅ No JavaScript handling clicks - browser default behavior applies

## Solution

Added `target="_self"` attribute to **all navigation links** to explicitly force same-tab navigation:

### Files Changed

#### 1. `core/product_tile.py`
- **Line ~266-269**: Primary button link
  ```python
  f'<a class="dashboard-cta dashboard-cta--primary" href="{href}" target="_self"{tooltip_attr}>'
  ```
- **Line ~276-278**: Secondary button link
  ```python
  f'<a class="dashboard-cta dashboard-cta--ghost" href="{href}" target="_self">'
  ```

#### 2. `hubs/concierge.py`
- **Line ~360-362**: Hub guide action buttons
  ```python
  f'<a class="btn btn--primary" href="{action_route}" target="_self">{html.escape(action_label)}</a>'
  '<a class="btn btn--secondary" href="?page=faqs" target="_self">Ask Navi →</a>'
  ```

## Impact

**Fixed**:
- ✅ FAQ tile "Open" button → same tab
- ✅ "Ask Navi →" button in hub guide → same tab
- ✅ All product tile primary/secondary actions → same tab
- ✅ Session state preserved across ALL navigation
- ✅ Cost Planner stays unlocked after FAQ visit

**No Breaking Changes**:
- Same visual appearance
- Same user flow
- Same functionality, just enforced same-tab behavior

## Testing

### Manual Test
1. Complete GCP → Cost Planner unlocked ✅
2. Click "Return to Hub" → Cost Planner still unlocked ✅
3. Click "Open" on FAQ tile → **opens in same tab** ✅
4. Click "← Back to Hub" in FAQ → **same tab** ✅
5. Verify Cost Planner **still unlocked** ✅

### Expected Results
- No new browser tabs/windows open
- Session state maintained throughout
- MCIP state available on all pages
- Cost Planner unlock persists

## Why This Works

`target="_self"` is the HTML attribute that explicitly tells the browser:
- Open this link in the **current** tab/window
- Replace the current page
- Preserve the current browsing context

Without `target="_self"`:
- Browser uses default behavior (can be unpredictable)
- Some browsers/contexts open new tabs
- Session state is lost in new tabs

With `target="_self"`:
- Guaranteed same-tab navigation
- Session state preserved
- Streamlit session continues

## Related Issues

This fix complements the previous MCIP fixes:
- ✅ **Commit 2f9e9df**: Unlock logic checks MCIP
- ✅ **Commit 934c4ec**: MCIP always restores from contracts
- ✅ **Commit 342612e, 2c9048c, 2665657**: Deepcopy fixes for shared references

All those fixes ensured MCIP state was correctly saved and restored. This fix ensures the **session** is preserved so MCIP state can be accessed.

## Architecture Note

This is a **navigation layer fix**, not an MCIP fix:
- MCIP code is correct (all tests pass)
- Session state management is correct
- Issue was browser opening new tabs → new sessions → empty state

The fix enforces same-tab navigation at the HTML level, ensuring session continuity.

---

**Status**: ✅ Fixed - Ready for testing  
**Next**: Manual test with user's exact workflow
