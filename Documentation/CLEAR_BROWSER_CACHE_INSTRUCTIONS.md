# How to Test Demo Profile with Fresh Session

## THE PROBLEM
Your browser has `persistence_loaded = True` cached in sessionStorage, so the app thinks it already loaded user data and skips the `load_user()` function.

## THE SOLUTION
You need a **completely fresh browser session**. Here are 3 ways:

---

## Option 1: Incognito/Private Window (EASIEST)

1. **Open a new incognito window:**
   - **Chrome/Edge**: `Cmd+Shift+N`
   - **Safari**: `Cmd+Shift+N` 
   - **Firefox**: `Cmd+Shift+P`

2. Go to: `http://localhost:8502`

3. Click **"John Test"** button to login

4. **Watch terminal** - you should see:
   ```
   [DEMO] Loading fresh demo profile from: data/users/demo/demo_john_cost_planner.json
   [DEMO] Creating/refreshing working copy at: data/users/demo_john_cost_planner.json
   [DEMO] ✅ Demo profile copied successfully!
   [DEMO] Loaded user data:
     - has mcip_contracts: True
     - care_recommendation tier: assisted_living
     - has tiles: True, keys: ['gcp_v4', 'cost_planner_v2']
   [MCIP] Restored from contracts: tier=assisted_living
   ```

---

## Option 2: Clear Browser Storage (Current Window)

1. **Open Developer Tools:**
   - Press `F12` or `Cmd+Option+I`

2. **Go to Console tab**

3. **Run this command:**
   ```javascript
   sessionStorage.clear(); localStorage.clear(); location.reload();
   ```

4. App will reload with fresh session

5. Login as **"John Test"**

---

## Option 3: Use Different Browser

If you've been testing in Chrome, try Safari or Firefox.

---

## What You Should See

After logging in as John Test with a fresh session:

### In the Terminal:
- `[DEMO]` logs showing profile copy
- `tier=assisted_living` (NOT `tier=None`)
- Tiles with both `gcp_v4` and `cost_planner_v2`

### In the App:
- ✅ GCP tile shows **green checkmark** (complete)
- ✅ Cost Planner tile shows **green checkmark** (complete)
- Welcome screen shows **"Assisted Living"** recommendation
- Both products should be accessible and show data

---

## Still Not Working?

If you still see `tier=None` after trying the above:

1. Check terminal shows `[DEMO]` logs (proves fresh session)
2. Run this to verify demo source is correct:
   ```bash
   cat data/users/demo/demo_john_cost_planner.json | jq .mcip_contracts.care_recommendation.tier
   ```
   Should output: `"assisted_living"`

3. Share the terminal output with me
