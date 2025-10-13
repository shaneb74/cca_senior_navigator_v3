# Professional Hub Navigation Debugging Guide

## Issue Encountered
The "For Professionals" button was opening in a new tab (`target="_blank"`) instead of navigating in the same tab, preventing the query parameter from being detected and processed.

## Root Cause
- HTML anchor tags in Streamlit's rendered HTML were being modified (possibly by Streamlit itself or CSS)
- The `target="_blank"` attribute was being added automatically
- This caused the button to open a new tab instead of navigating within the same session

## Solution Applied
Added explicit JavaScript `onclick` handler to:
1. Prevent default link behavior (`event.preventDefault()`)
2. Explicitly set `window.location.href` to the target URL
3. Return `false` to ensure no further event propagation

### Updated Button Code:
```html
<a href="?page=welcome&enable_professional=1" 
   class="btn btn--primary" 
   onclick="event.preventDefault(); window.location.href='?page=welcome&enable_professional=1'; return false;">
   For Professionals
</a>
```

## How It Works Now

### Step-by-Step Flow:

1. **User clicks "For Professionals" button**
   - Button is in the Professional Login section at bottom of welcome page
   - onclick handler fires

2. **JavaScript prevents default behavior**
   - `event.preventDefault()` stops normal anchor click
   - Prevents any `target="_blank"` from taking effect

3. **JavaScript sets window location**
   - `window.location.href='?page=welcome&enable_professional=1'`
   - Navigates in the **same tab** to the welcome page with query parameter

4. **Welcome.py render() function detects parameter**
   ```python
   if st.query_params.get("enable_professional") == "1":
       if not is_professional():
           switch_to_professional()
       st.query_params.clear()
       st.query_params["page"] = "hub_professional"
       st.rerun()
   ```

5. **Role switched and navigation occurs**
   - `switch_to_professional()` sets `st.session_state["user_role"] = "professional"`
   - Query params cleared and set to `page=hub_professional`
   - `st.rerun()` triggers page reload

6. **Professional Hub renders**
   - URL now shows: `?page=hub_professional`
   - `hubs/professional.py` render() function executes
   - MCIP panel and 6 tiles display
   - Header shows Professional link and Logout button

## Testing the Fix

### Manual Test Steps:

1. **Start the app:**
   ```bash
   streamlit run app.py
   ```

2. **Navigate to welcome page:**
   - Should load by default
   - URL: `http://localhost:8501/?page=welcome` (or just `http://localhost:8501`)

3. **Scroll to Professional Login section:**
   - Located at bottom of page
   - White card with centered text

4. **Open browser DevTools:**
   - Press F12 (or Cmd+Option+I on Mac)
   - Go to Console tab

5. **Click "For Professionals" button:**
   - Watch the Console for any errors
   - Watch the Network tab for page reload
   - **Expected:** Page reloads in **same tab**
   - **Expected:** URL changes to `?page=welcome&enable_professional=1` briefly
   - **Expected:** Then immediately to `?page=hub_professional`

6. **Verify Professional Hub loads:**
   - MCIP panel visible at top (4 chips)
   - 6 product tiles visible
   - Header shows "Professional" link
   - Header shows "Logout" button

### Debug Checklist:

- [ ] Button exists in Professional Login section
- [ ] Button has `onclick` handler in HTML
- [ ] Clicking button does NOT open new tab
- [ ] Console shows no JavaScript errors
- [ ] URL changes to include `enable_professional=1` parameter
- [ ] Professional mode activates (check session state if possible)
- [ ] Navigation proceeds to Professional Hub
- [ ] Hub content renders correctly

### Common Issues:

**Issue: Button still opens new tab**
- Check if onclick handler is present in rendered HTML
- Use DevTools → Elements → Find the button
- Look for `onclick="event.preventDefault()..."`
- If missing, check if HTML is being sanitized

**Issue: Query parameter not detected**
- Add debug print in welcome.py render():
  ```python
  st.write("Query params:", dict(st.query_params))
  ```
- Should show: `{'page': 'welcome', 'enable_professional': '1'}`

**Issue: Role not switching**
- Add debug print:
  ```python
  st.write("User role:", st.session_state.get("user_role"))
  ```
- Should show: `professional` after clicking button

**Issue: Hub not loading**
- Check if `hubs/professional.py` exists
- Check if `config/nav.json` has `hub_professional` entry
- Check browser console for import errors

## Alternative Solutions (if current fix doesn't work)

### Option 1: Use JavaScript form submission
Replace anchor with form:
```html
<form method="GET" action="/" onsubmit="window.location.href='?page=welcome&enable_professional=1'; return false;">
  <button type="submit" class="btn btn--primary">For Professionals</button>
</form>
```

### Option 2: Use Streamlit button (outside layout)
Add at end of render() function:
```python
if st.button("🔐 Enable Professional Mode", key="pro_login"):
    switch_to_professional()
    st.query_params.clear()
    st.query_params["page"] = "hub_professional"
    st.rerun()
```

### Option 3: Use st.html with inline script
```python
st.html("""
<div class="professional-login__button">
  <button class="btn btn--primary" onclick="window.parent.location.href='?page=welcome&enable_professional=1'">
    For Professionals
  </button>
</div>
""")
```

## Verification Commands

### Check session state (add to render function temporarily):
```python
st.sidebar.write("DEBUG:")
st.sidebar.write("Role:", st.session_state.get("user_role", "not set"))
st.sidebar.write("Query params:", dict(st.query_params))
st.sidebar.write("Is professional?", is_professional())
```

### Check if button HTML is correct:
```bash
# Start app and view source in browser
# Search for "For Professionals"
# Verify onclick handler is present
```

### Check navigation flow:
```bash
# Add logging to terminal in welcome.py
import sys
print(f"[WELCOME] Query params: {dict(st.query_params)}", file=sys.stderr)
if st.query_params.get("enable_professional") == "1":
    print("[WELCOME] Professional mode activation triggered!", file=sys.stderr)
```

## Success Criteria

✅ **Test passes if:**
1. Button click does NOT open new tab
2. URL changes to `?page=welcome&enable_professional=1` (briefly)
3. Then changes to `?page=hub_professional`
4. Professional Hub loads with full content
5. Header updates to show Professional link and Logout
6. No console errors
7. Flow completes in ~1-2 seconds

## Status

**Current Status:** ✅ Fixed with onclick handler  
**Commit:** `1cc1295` - "Fix Professional Login button to navigate in same tab"  
**Date:** October 13, 2025  
**Tested:** Pending user verification

---

**Next Steps if issue persists:**
1. Check browser console for errors
2. Verify onclick handler in rendered HTML
3. Try alternative solutions above
4. Report specific error messages for further debugging
