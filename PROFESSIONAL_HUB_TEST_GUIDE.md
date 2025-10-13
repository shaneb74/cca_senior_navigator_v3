# Professional Hub Testing Guide

## Quick Start Testing

### Test 1: Professional Mode Activation
**Expected Behavior:** One-click access to Professional Hub with fake authentication

1. Start the app: `streamlit run app.py`
2. Navigate to the welcome page (should load by default)
3. Scroll to the bottom of the page
4. Locate the **Professional Login** section (white card with centered text)
5. Click the **"For Professionals"** button (primary blue button)

**✅ Expected Result:**
- App should immediately switch to professional mode
- Browser should navigate to Professional Hub page
- URL should show: `?page=hub_professional`
- No reload, no flash, seamless transition

### Test 2: Professional Hub Content Verification
**Expected Behavior:** Hub displays MCIP panel and 6 product tiles

**Check the following:**

**A. MCIP Panel (Chips at top):**
- [ ] "Pending: 7" chip visible
- [ ] "New referrals: 3" chip visible (muted style)
- [ ] "Updates needed: 5" chip visible
- [ ] "Last login: 2025-10-12 14:30" chip visible (muted style)

**B. Product Tiles (6 cards in grid):**

**Tile 1: Professional Dashboard**
- [ ] Badge: "7 new" (blue/brand color)
- [ ] Description: "At-a-glance priorities and recent activity..."
- [ ] Meta: "7 pending actions", "3 new referrals today"
- [ ] Button: "Open Dashboard"

**Tile 2: Client List / Search**
- [ ] No badge
- [ ] Description: "Find clients and open their profiles..."
- [ ] Meta: "Search by name, ID, or case number", "Quick filters..."
- [ ] Button: "Find a Client"

**Tile 3: Case Management & Referrals**
- [ ] Badge: "5 due" (gray/neutral color)
- [ ] Description: "Create, track, and update cases..."
- [ ] Meta: "5 cases need updates", "Automated status tracking"
- [ ] Button: "Manage Cases"

**Tile 4: Scheduling + Analytics**
- [ ] Badge: "3 due today" (purple/AI color)
- [ ] Description: "Manage appointments and view engagement..."
- [ ] Meta: "Calendar integration available", "Weekly performance reports"
- [ ] Button: "View Schedule"

**Tile 5: Health Assessment Access**
- [ ] No badge
- [ ] Description: "Open assessment summaries and recidivism-risk flags..."
- [ ] Meta: "Risk scores and alerts included", "Historical comparison views"
- [ ] Button: "View Assessments"

**Tile 6: Advisor Mode Navi (CRM Query Engine)**
- [ ] Badge: "Beta" (purple/AI color)
- [ ] Description: "Professional-grade CRM queries..."
- [ ] Meta: "Natural language queries", "Export to reports..."
- [ ] Button: "Open CRM"

### Test 3: Header Navigation Changes
**Expected Behavior:** Header updates to show Professional link and Logout button

**Check the header:**
- [ ] "Professional" link now visible in navigation menu (between "Trusted Partners" and auth button)
- [ ] "Logout" button visible (replaced "Log in or sign up")
- [ ] Logout button styled as secondary (gray background)
- [ ] All other nav links still present (Welcome, Concierge, Waiting Room, Learning, Trusted Partners)

### Test 4: Navigation While in Professional Mode
**Expected Behavior:** Can navigate to other pages while maintaining professional role

1. While in Professional Hub, click "Welcome" in header
   - [ ] Should navigate to welcome page
   - [ ] Professional link still visible in header
   - [ ] Logout button still visible

2. Click "Concierge" in header
   - [ ] Should navigate to Concierge hub
   - [ ] Professional link still visible in header
   - [ ] Logout button still visible

3. Click "Professional" in header
   - [ ] Should navigate back to Professional Hub
   - [ ] Hub content should display correctly

### Test 5: Logout Flow
**Expected Behavior:** Logout returns to member mode and welcome page

1. While in professional mode (on any page), click **"Logout"** in header

**✅ Expected Result:**
- App switches back to member mode
- Browser navigates to welcome page
- URL shows: `?page=welcome`
- Professional link NO LONGER in header
- "Log in or sign up" button restored in header

2. Try to access Professional Hub directly
   - Manually change URL to `?page=hub_professional`
   - [ ] Should auto-switch back to professional mode (safety fallback)
   - [ ] Hub should display correctly

### Test 6: Mobile Responsive Check (Optional)
**Expected Behavior:** Layout adapts to mobile screens

1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M / Cmd+Shift+M)
3. Select iPhone or Android device
4. Repeat Tests 1-5

**Check:**
- [ ] Professional Login section readable and button accessible
- [ ] Professional Hub tiles stack vertically
- [ ] MCIP chips wrap properly
- [ ] Header navigation toggles to hamburger menu
- [ ] Logout button accessible in mobile menu

## Common Issues & Troubleshooting

### Issue: Button doesn't do anything when clicked
**Possible Causes:**
- JavaScript disabled in browser
- Query parameters not being processed
- Session state not initializing

**Solution:**
- Check browser console for errors (F12 → Console)
- Verify query params in URL bar after clicking
- Restart Streamlit app

### Issue: Professional Hub shows but MCIP panel or tiles are missing
**Possible Causes:**
- `render_dashboard_body` function not working
- `ProductTileHub` component not rendering
- CSS not loading

**Solution:**
- Check Streamlit console output for errors
- Verify `core/base_hub.py` and `core/product_tile.py` exist
- Check browser console for CSS loading issues

### Issue: Logout button doesn't work
**Possible Causes:**
- Query parameter handler not detecting `logout=1`
- `switch_to_member()` not being called
- Rerun not triggering

**Solution:**
- Check URL after clicking logout (should show `?page=welcome&logout=1`)
- Verify `core/state.py` has `switch_to_member()` function
- Check Streamlit console for errors

### Issue: Professional link doesn't appear in header
**Possible Causes:**
- `is_professional()` returning False
- Header not re-rendering after role switch
- CSS hiding the link

**Solution:**
- Add `st.write(st.session_state.get("user_role"))` to debug
- Verify role is set to "professional" after button click
- Check browser DevTools → Elements to see if link is in DOM

### Issue: Role resets after page refresh
**Expected Behavior:** This is normal for development
- Session state is NOT persisted across browser refreshes
- F5/Reload will reset to member mode
- This will be fixed with real authentication + cookies/localStorage

## Success Criteria

All tests pass if:
1. ✅ One-click button activates professional mode instantly
2. ✅ Professional Hub displays with MCIP panel and 6 tiles
3. ✅ Header shows Professional link and Logout button
4. ✅ Can navigate between pages while maintaining role
5. ✅ Logout returns to member mode and welcome page
6. ✅ No console errors, no broken links, no layout issues

## Video Recording Checklist

If recording a demo, show:
1. Welcome page → scroll to Professional Login section
2. Click "For Professionals" button
3. Professional Hub loads with full content
4. Point out MCIP chips and count them (4 chips)
5. Scroll through all 6 product tiles
6. Show header with Professional link and Logout
7. Click Professional link to confirm navigation works
8. Click Logout button
9. Confirm return to welcome page in member mode
10. Verify Professional link is gone from header

---

**Test Duration:** ~5 minutes for full manual test  
**Automated Test:** Not yet implemented  
**Last Updated:** October 13, 2025
