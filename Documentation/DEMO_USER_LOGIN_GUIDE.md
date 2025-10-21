# Demo User Login System for Testing & Development

**Quick access to persistent test user profiles**

---

## Overview

The login page now supports **demo/test user profiles** with **fixed UIDs** that persist across app restarts. This solves the testing problem where each app restart creates a new anonymous UID and "loses" your test data.

---

## How to Use

### Option 1: From Welcome Page

1. Navigate to `http://localhost:8501/`
2. Click **"Demo/Test Login 🧪"** button in hero section
3. Select a demo user from the login page
4. Your UID will be consistent across sessions!

### Option 2: Direct Login URL

Navigate directly to login page:
```
http://localhost:8501/?page=login
```

### Option 3: Demo User Direct Links

Skip login page and go straight to a demo user:
```
http://localhost:8501/?page=login&demo_user=demo_john
http://localhost:8501/?page=login&demo_user=demo_sarah
http://localhost:8501/?page=login&demo_user=demo_mary
```

---

## Demo Users

### 👤 Sarah Demo
- **UID:** `demo_sarah_test_001`
- **Email:** `sarah@demo.test`
- **Purpose:** Empty profile - fresh start for testing
- **Use Case:** Testing new user flows, onboarding

### 👤 John Test
- **UID:** `demo_john_cost_planner`
- **Email:** `john@demo.test`
- **Purpose:** For Cost Planner testing (persistent UID)
- **Use Case:** Cost Planner assessments, persistence testing

### 👤 Mary Complete
- **UID:** `demo_mary_full_data`
- **Email:** `mary@demo.test`
- **Purpose:** Complete assessments - for expert review testing
- **Use Case:** Testing with pre-filled data, expert review flows

---

## Key Benefits

### ✅ Fixed UIDs
Each demo user has a **consistent UID** that never changes:
- `demo_sarah_test_001`
- `demo_john_cost_planner`
- `demo_mary_full_data`

### ✅ Persistent Across Restarts
1. Login as "John Test"
2. Fill out Cost Planner assessments
3. Stop app (Ctrl+C)
4. Restart app
5. Login as "John Test" again
6. **All data restored!**

### ✅ No Need to Bookmark URLs
- The demo UID is set automatically on login
- URL automatically includes the UID: `?uid=demo_john_cost_planner`
- Just login as the same demo user to restore data

### ✅ Separate Test Profiles
- Each demo user has its own data file
- Test different scenarios without conflict
- Clean slate vs. pre-filled data options

---

## File Structure

Demo user data files are stored like regular users:

```
data/
└── users/
    ├── demo_sarah_test_001.json
    ├── demo_john_cost_planner.json
    └── demo_mary_full_data.json
```

Each file contains the full user state:
```json
{
  "uid": "demo_john_cost_planner",
  "created_at": 1729267200.0,
  "last_updated": 1729267800.0,
  "profile": {},
  "cost_v2_modules": {
    "income": { ... },
    "assets": { ... }
  },
  "cost_v2_quick_estimate": { ... }
}
```

---

## Testing Workflows

### Workflow 1: Fresh Testing (Sarah Demo)

**Use Case:** Testing new user experience, onboarding flows

1. Navigate to login page
2. Click **"Sarah Demo"** button
3. Empty profile → fresh state
4. Fill out assessments
5. Data persists to `demo_sarah_test_001.json`
6. Restart app → Login as Sarah → Data restored

**UID:** `demo_sarah_test_001`

---

### Workflow 2: Cost Planner Testing (John Test)

**Use Case:** Testing Cost Planner assessments, persistence, expert review

1. Navigate to login page
2. Click **"John Test"** button
3. Go to Cost Planner
4. Fill out financial assessments
5. Restart app multiple times
6. Login as John each time → **Always same data**

**UID:** `demo_john_cost_planner`

**Persistent Data:**
- Income assessment
- Assets assessment
- VA benefits
- Health insurance
- Life insurance
- Expert review results

---

### Workflow 3: Pre-filled Data Testing (Mary Complete)

**Use Case:** Testing expert review, recommendations, complete user journeys

1. Navigate to login page
2. Click **"Mary Complete"** button
3. **NOTE:** Profile starts empty (you can pre-fill data manually once)
4. After filling data once, it persists forever
5. Use for testing downstream flows with complete data

**UID:** `demo_mary_full_data`

**Future Enhancement:** Could pre-seed this user with sample data in JSON file

---

## Developer Tips

### Tip 1: Bookmark Demo User URLs

While not required, you can bookmark the direct URL:
```
http://localhost:8501/?uid=demo_john_cost_planner&page=hub_concierge
```

This skips login and goes straight to the hub with John's data.

---

### Tip 2: Inspect Demo User Data

Check what data is saved:
```bash
# View all Cost Planner data for John
cat data/users/demo_john_cost_planner.json | jq '.cost_v2_modules'

# View quick estimate
cat data/users/demo_john_cost_planner.json | jq '.cost_v2_quick_estimate'

# View all keys
cat data/users/demo_john_cost_planner.json | jq 'keys'
```

---

### Tip 3: Reset Demo User Data

To start fresh with a demo user:
```bash
# Delete the data file
rm data/users/demo_john_cost_planner.json

# Or edit it directly
code data/users/demo_john_cost_planner.json
```

Next login will create a new empty file.

---

### Tip 4: Create New Demo Users

Add to `DEMO_USERS` dict in `pages/login.py`:

```python
DEMO_USERS = {
    # Existing users...
    
    "demo_veteran": {
        "name": "Bob Veteran",
        "email": "bob@demo.test",
        "uid": "demo_bob_veteran_test",
        "description": "For testing VA benefits flows",
    },
}
```

The button will appear automatically on login page.

---

## Login Page Features

### Visual Layout

```
┌─────────────────────────────────────┐
│ 🔐 Login Options                    │
├─────────────────┬───────────────────┤
│ Quick Login     │ Demo Users        │
│                 │ (Fixed UIDs)      │
│ [Log in as      │ [👤 Sarah Demo]   │
│  Sarah]         │ [👤 John Test]    │
│                 │ [👤 Mary Complete]│
└─────────────────┴───────────────────┘

💡 Developer Notes
- Fixed UIDs persist across restarts
- Bookmark URLs maintain demo UID
- Data files: data/users/{uid}.json

🔍 Current Session Info
Current UID: demo_john_cost_planner
Authenticated: Yes
```

### Demo User Button Tooltips

Hover over a demo user button to see:
- Full description
- UID string
- Use case

Example:
```
👤 John Test
Tooltip: "For Cost Planner testing (persistent UID)
         UID: demo_john_cost_planner"
```

---

## Session State After Login

When you login as a demo user, the session state is set:

```python
st.session_state = {
    "anonymous_uid": "demo_john_cost_planner",
    "auth": {
        "is_authenticated": True,
        "user_id": "demo_john_cost_planner",
        "name": "John Test",
        "email": "john@demo.test"
    },
    "persistence_loaded": True,
    # ... all user data loaded from file ...
    "cost_v2_modules": { ... },
    "cost_v2_quick_estimate": { ... },
}
```

URL becomes:
```
http://localhost:8501/?uid=demo_john_cost_planner&page=hub_concierge
```

---

## Comparison: Anonymous vs Demo Users

### Anonymous User (Default Behavior)

```
Session 1:
- UID: anon_d2c42550e6a3 (random)
- Fill out data
- Data saved to: data/users/anon_d2c42550e6a3.json

App Restart (no bookmark):
- UID: anon_9cb5f556f4fd (NEW random)
- Different user → Different file
- Data "lost" (still exists, different UID)
```

### Demo User (New Behavior)

```
Session 1:
- Login as "John Test"
- UID: demo_john_cost_planner (fixed)
- Fill out data
- Data saved to: data/users/demo_john_cost_planner.json

App Restart:
- Login as "John Test" again
- UID: demo_john_cost_planner (SAME)
- Same user → Same file
- Data restored! ✅
```

---

## Use Cases

### For Developers

**Testing Persistence:**
```bash
# 1. Login as John Test
# 2. Fill Cost Planner assessments
# 3. Check data saved:
cat data/users/demo_john_cost_planner.json | jq '.cost_v2_modules'

# 4. Restart app
# 5. Login as John Test
# 6. Verify data restored (check UI)
```

**Testing Different Scenarios:**
- Use Sarah for testing fresh user flows
- Use John for testing Cost Planner
- Use Mary for testing complete journeys
- Each stays separate

**Debugging:**
- Consistent UID makes debugging easier
- Can trace logs for specific demo user
- Can inspect exact state in JSON file

---

### For QA Testing

**Regression Testing:**
1. Login as John Test (always same UID)
2. Run through Cost Planner test cases
3. Data persists between test runs
4. No need to re-enter data each time

**Multi-scenario Testing:**
- Test different user types simultaneously
- Sarah: New user path
- John: Cost Planner power user
- Mary: Complete profile user

---

### For Demos

**Client Presentations:**
1. Pre-fill Mary Complete with impressive data
2. Login as Mary before demo
3. Show polished expert review
4. No risk of empty state during demo

**Stakeholder Reviews:**
- Consistent experience every time
- No "oops, wrong user" moments
- Professional, predictable demos

---

## Advanced: Pre-seeding Demo Data

### Manual Pre-seed

1. Login as demo user
2. Fill out all desired data
3. User file saved automatically
4. Next login → data already there

### Programmatic Pre-seed

Create a JSON file at `data/users/demo_mary_full_data.json`:

```json
{
  "uid": "demo_mary_full_data",
  "created_at": 1729267200.0,
  "last_updated": 1729267800.0,
  "profile": {
    "name": "Mary Complete",
    "age": 78
  },
  "cost_v2_modules": {
    "income": {
      "status": "completed",
      "progress": 100,
      "data": {
        "ss_monthly": 2500,
        "pension_monthly": 1800,
        "total_monthly_income": 4300
      }
    },
    "assets": {
      "status": "completed",
      "progress": 100,
      "data": {
        "checking_savings": 75000,
        "investment_accounts": 250000,
        "primary_residence_value": 450000
      }
    }
  },
  "cost_v2_quick_estimate": {
    "estimate": {
      "monthly_base": 5400,
      "monthly_adjusted": 6480,
      "annual": 77760,
      "care_tier": "assisted_living",
      "region_name": "San Francisco, CA"
    },
    "care_tier": "assisted_living",
    "zip_code": "94102"
  }
}
```

Next time you login as Mary → fully pre-populated!

---

## Troubleshooting

### Issue: "Data not showing after login"

**Cause:** Data file doesn't exist yet

**Solution:** 
1. Login as demo user
2. Fill out data
3. Data will persist on next login

---

### Issue: "Wrong UID in URL"

**Cause:** Browser cached old session

**Solution:**
1. Clear browser cache
2. Or open incognito window
3. Login as demo user fresh

---

### Issue: "Demo user data corrupted"

**Solution:** Delete and regenerate
```bash
rm data/users/demo_john_cost_planner.json
# Login again → fresh file created
```

---

## Future Enhancements

### Possible Additions

1. **Admin Panel:**
   - View all demo users
   - Reset demo user data
   - Export/import demo data

2. **Data Templates:**
   - Pre-made JSON files for common scenarios
   - "Veteran", "Medicaid User", "High Net Worth", etc.
   - One-click load

3. **Demo Mode Flag:**
   - Visual indicator when using demo user
   - Warning before deleting demo data
   - Separate demo data from real data

4. **Team Sharing:**
   - Share demo user UIDs with team
   - Everyone tests with same data
   - Consistent QA environment

---

## Summary

### Key Benefits

✅ **Fixed UIDs** - No more random UIDs on each restart  
✅ **Persistent Data** - Same user = same data, always  
✅ **Easy Testing** - Click button, get consistent environment  
✅ **No Bookmarks Required** - Just login as same demo user  
✅ **Multiple Profiles** - Test different scenarios separately  

### Quick Reference

| Demo User | UID | Purpose |
|-----------|-----|---------|
| Sarah Demo | `demo_sarah_test_001` | Fresh testing |
| John Test | `demo_john_cost_planner` | Cost Planner |
| Mary Complete | `demo_mary_full_data` | Full journeys |

### Access

1. **Welcome page:** Click "Demo/Test Login 🧪"
2. **Direct:** `http://localhost:8501/?page=login`
3. **Quick:** `http://localhost:8501/?page=login&demo_user=demo_john`

---

**Happy Testing!** 🧪
