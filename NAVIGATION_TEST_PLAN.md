# Financial Assessments Navigation Test Plan

## Changes Made

### 1. Assessment Page Navigation Buttons (`_render_page_navigation`)
- **"Back to Assessments" button**: Now properly sets query params
  - Sets `page=cost_v2`, `step=assessments`
  - Removes `assessment` param
  - Clears session state properly
  
- **"Go to Next Assessment" button**: Now properly sets query params
  - Sets `page=cost_v2`, `step=assessments`, `assessment={next_key}`
  - Updates session state to match
  
- **"Finish & Review" button**: Now properly sets query params
  - Sets `page=cost_v2`, `step=expert_review`
  - Removes `assessment` param

### 2. Hub Navigation Buttons (`_render_hub_view`)
- **"Back to Quick Assessment" button**: Already correct
  - Sets `page=gcp`
  - Removes `step` and `assessment` params
  
- **"Go to Expert Review" button**: Fixed to properly set query params
  - Sets `page=cost_v2`, `step=expert_review`
  - Removes `assessment` param

### 3. Assessment Cards
- Already preserve UID in hrefs
- Already use proper query param format: `?page=cost_v2&step=assessments&assessment={key}&uid={uid}`

### 4. Browser Navigation
- Hub already checks query params on load and syncs with session state
- URL-driven navigation takes precedence
- Browser back/forward should now work correctly

## Test Checklist

### Basic Navigation Flow
- [ ] Start at hub → Click "Income Sources" card → Assessment loads
- [ ] Click "Back to Assessments" → Returns to hub
- [ ] Click "Assets & Resources" card → Assessment loads
- [ ] Click "Go to Assets & Resources" (from Income) → Next assessment loads
- [ ] Complete all assessments → "Finish & Review" → Expert Review loads
- [ ] Click "Back to Quick Assessment" from hub → GCP loads

### URL Query Params (Check browser address bar)
- [ ] Hub view: `?page=cost_v2&step=assessments&uid={uid}`
- [ ] Income assessment: `?page=cost_v2&step=assessments&assessment=income&uid={uid}`
- [ ] Assets assessment: `?page=cost_v2&step=assessments&assessment=assets&uid={uid}`
- [ ] Expert Review: `?page=cost_v2&step=expert_review&uid={uid}`
- [ ] GCP: `?page=gcp&uid={uid}`

### Browser Navigation
- [ ] Click Income → Use browser back button → Returns to hub
- [ ] Click Assets → Use browser back button → Returns to hub
- [ ] Go Income → Assets → Browser back → Income shows
- [ ] Go Income → Assets → Browser back → Browser back → Hub shows
- [ ] Use browser forward after backing up → Correct page loads

### Session State Preservation
- [ ] Enter data in Income → Navigate away → Return → Data persists
- [ ] Enter data in Assets → Navigate away → Return → Data persists
- [ ] Use browser back/forward → Data persists
- [ ] Refresh page with assessment in URL → Assessment loads with data

### UID Preservation
- [ ] Demo Mary user navigates between assessments → UID maintained
- [ ] Anonymous user navigates between assessments → UID maintained
- [ ] Copy URL from one assessment, paste in new tab → Same session loads

### Edge Cases
- [ ] Direct URL entry: `?page=cost_v2&step=assessments&assessment=income&uid=demo_mary`
- [ ] Missing UID in URL → Session still accessible
- [ ] Invalid assessment key in URL → Error message shows
- [ ] Navigate to Expert Review before completing required assessments → Blocked

## Expected Behavior Summary

1. **All buttons update URL query params** to enable browser navigation
2. **Hub checks query params first** on load to support browser back/forward
3. **Session state syncs with URL** to prevent desync
4. **UID is preserved** in all navigation links
5. **Assessment data persists** across navigation
6. **Browser back/forward works** like a native multi-page app
