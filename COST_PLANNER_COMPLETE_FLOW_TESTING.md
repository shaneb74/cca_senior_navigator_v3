# Cost Planner - Complete Flow Testing Guide

## Implementation Summary

Complete Cost Planner flow with authentication gate, profile flags collection, and conditional module visibility has been implemented.

## User Flow Overview

```
1. GCP Complete (prerequisite)
   ↓
2. Cost Planner Intro
   ↓ Continue
3. Quick Estimate
   - See GCP recommendation
   - Select care type
   - Click "See My Estimate" → View costs
   - Click "Continue to Full Assessment"
   ↓
4. Authentication Check
   - IF NOT authenticated → Auth Gate (Step 3)
   - IF authenticated → Skip to Profile Flags (Step 4)
   ↓
5. Auth Gate (if needed)
   - Show "Authentication Required" message
   - Mock Login button
   - After login → Profile Flags
   ↓
6. Profile Flags
   - Collect: ZIP code, Veteran status, Home ownership, Medicaid status
   - All required fields
   - Continue → Module Index
   ↓
7. Module Index
   - Show regional pricing banner (if ZIP provided)
   - Display available modules with status
   - Conditional visibility based on flags
   - Navigate to individual modules
```

## Module Visibility Rules

### Always Visible (Enabled=True)

**1. Income Sources** 💰
- **Condition:** Always available
- **Description:** Track all income sources
- **Gating:** None

**2. Assets & Savings** 💎
- **Condition:** Always available
- **Description:** Document all assets
- **Gating:** None

**3. Health Insurance & Benefits** 🏥
- **Condition:** Always available
- **Description:** Review insurance coverage
- **Gating:** None

### Conditionally Visible

**4. Housing & Home Equity** 🏡
- **Condition:** `home_owner=true AND gcp_recommendation != "In-Home Care"`
- **Logic:**
  ```python
  enabled = home_owner and not is_in_home_care
  ```
- **Display States:**
  - ✓ Available (green) - If home_owner=true AND not In-Home Care
  - ✗ Not available (red) - If home_owner=false OR is In-Home Care
- **Rationale:** Home equity planning not relevant if:
  - Don't own home
  - Staying in current home (In-Home Care)

**5. VA Benefits** 🎖️
- **Condition:** `veteran_status=true`
- **Logic:**
  ```python
  enabled = veteran_status
  ```
- **Display States:**
  - ✓ Available (green) - If veteran_status=true
  - ✗ Veteran status required (red) - If veteran_status=false
- **Rationale:** Only veterans can apply for VA Aid & Attendance

**6. Medicaid Navigator** 🏛️
- **Condition:** `medicaid_status=true`
- **Logic:**
  ```python
  enabled = medicaid_status
  ```
- **Display States:**
  - ✓ Currently enrolled (green) - If medicaid_status=true
  - ✗ Medicaid enrollment required (red) - If medicaid_status=false
- **Rationale:** Navigator helps current Medicaid recipients optimize benefits

## Test Scenarios

### Scenario 1: Unauthenticated User - Auth Gate Blocks

**Setup:**
1. Clear session state: `st.session_state.clear()`
2. Complete GCP → Get recommendation: "Assisted Living"
3. Navigate to Cost Planner

**Steps:**
1. ✅ See intro page
2. ✅ Click Continue → See Quick Estimate
3. ✅ See "Your Care Recommendation: Assisted Living"
4. ✅ Care type pre-selected to "Assisted Living"
5. ✅ Click "See My Estimate" → Cost breakdown appears
6. ✅ Button changes to "Continue to Full Assessment"
7. ✅ Click "Continue to Full Assessment"

**Expected: Auth Gate**
```
🔒 Authentication Required

This section requires you to log in to:
- Save your progress
- Access personalized financial calculations
- Securely store sensitive financial data

For Development: Click below to simulate authentication.

[🔓 Mock Login]  *Real authentication will be integrated in production*
```

8. ✅ Click "🔓 Mock Login"
9. ✅ Should rerun and progress to Profile Flags

**Validation:**
- [ ] Auth gate shows when unauthenticated
- [ ] Mock Login button works
- [ ] After login, moves to Profile Flags

### Scenario 2: Authenticated User - Skips Auth Gate

**Setup:**
1. Mock login first: `st.session_state["auth"] = {"is_authenticated": True}`
2. Complete GCP → Get recommendation: "Memory Care"
3. Navigate to Cost Planner

**Steps:**
1-6. ✅ Same as Scenario 1 through "See My Estimate"
7. ✅ Click "Continue to Full Assessment"

**Expected: Profile Flags (Skip Auth)**
```
A Few Quick Questions

These help us show you the most relevant financial planning modules...

ZIP Code (for regional pricing): [________]
Is the care recipient a military veteran? ○ Yes ○ No
Does the care recipient own their home? ○ Yes ○ No
Is the care recipient currently receiving Medicaid? ○ Yes ○ No/Not sure

[Continue]
```

**Validation:**
- [ ] Auth gate skipped (already authenticated)
- [ ] Lands directly on Profile Flags
- [ ] All 4 fields present and required

### Scenario 3: Module Visibility - All Flags True

**Profile Flags:**
- ZIP: 98101
- Veteran: **Yes**
- Home Owner: **Yes**
- Medicaid: **Yes**

**GCP Recommendation:** "Assisted Living" (NOT In-Home Care)

**Expected Module Index:**

```
📍 Regional Pricing for ZIP 98101: +15% adjustment

### Your Financial Planning Modules

┌─────────────────────────────────────┐
│ 🏡 Housing & Home Equity            │
│ ✓ Available                         │ ← GREEN (home_owner=true AND not In-Home)
│ [Start Module]                      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 💰 Income Sources                   │
│ [Start Module]                      │ ← Always visible
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 💎 Assets & Savings                 │
│ [Start Module]                      │ ← Always visible
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🎖️ VA Benefits                      │
│ ✓ Available                         │ ← GREEN (veteran=true)
│ [Start Module]                      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🏥 Health Insurance & Benefits      │
│ [Start Module]                      │ ← Always visible
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🏛️ Medicaid Navigator               │
│ ✓ Currently enrolled                │ ← GREEN (medicaid=true)
│ [Start Module]                      │
└─────────────────────────────────────┘
```

**Validation:**
- [ ] All 6 modules visible
- [ ] Housing: GREEN ✓ Available
- [ ] VA Benefits: GREEN ✓ Available
- [ ] Medicaid: GREEN ✓ Currently enrolled
- [ ] All have "Start Module" buttons (not disabled)

### Scenario 4: Module Visibility - All Flags False

**Profile Flags:**
- ZIP: 98101
- Veteran: **No**
- Home Owner: **No**
- Medicaid: **No**

**GCP Recommendation:** "Memory Care"

**Expected Module Index:**

```
┌─────────────────────────────────────┐
│ 🏡 Housing & Home Equity            │
│ ✗ Home ownership required •         │ ← RED (home_owner=false)
│   Not for In-Home Care              │
│ [Not Available]  (disabled)         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 💰 Income Sources                   │
│ [Start Module]                      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 💎 Assets & Savings                 │
│ [Start Module]                      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🎖️ VA Benefits                      │
│ ✗ Veteran status required           │ ← RED (veteran=false)
│ [Not Available]  (disabled)         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🏥 Health Insurance & Benefits      │
│ [Start Module]                      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🏛️ Medicaid Navigator               │
│ ✗ Medicaid enrollment required      │ ← RED (medicaid=false)
│ [Not Available]  (disabled)         │
└─────────────────────────────────────┘
```

**Validation:**
- [ ] 3 modules enabled (Income, Assets, Insurance)
- [ ] 3 modules disabled (Housing, VA, Medicaid)
- [ ] Disabled modules show RED ✗ with reason
- [ ] Disabled modules have gray "Not Available" button

### Scenario 5: Home Decision Gating - In-Home Care

**Profile Flags:**
- ZIP: 98101
- Veteran: No
- Home Owner: **Yes** ← Important!
- Medicaid: No

**GCP Recommendation:** "In-Home Care" ← Important!

**Expected:**
```
┌─────────────────────────────────────┐
│ 🏡 Housing & Home Equity            │
│ ✗ Home ownership required •         │ ← RED even though home_owner=true
│   Not for In-Home Care              │
│ [Not Available]  (disabled)         │
└─────────────────────────────────────┘
```

**Logic:**
```python
# home_owner=true BUT is_in_home_care=true
enabled = home_owner and not is_in_home_care
# = true AND not true
# = true AND false
# = false  ← DISABLED!
```

**Validation:**
- [ ] Housing module disabled despite home_owner=true
- [ ] Reason shows "Not for In-Home Care"
- [ ] This is correct - staying in home, no need to evaluate home equity

### Scenario 6: Module Navigation

**From Module Index:**
1. Click "Start Module" on Income Sources

**Expected:**
```
[← Back to Module Index]  ← At top!

─────────────────────────

⚠️ Module 'income' is not yet implemented

Coming in Phase 2

The Income Sources module is planned but not yet built.

Return to the Module Index to explore other available modules.
```

2. Click "← Back to Module Index"

**Expected:**
- [ ] Returns to Module Index
- [ ] Income Sources now shows "🔄 In Progress" (started flag set)

## Authentication Flow Details

### Auth Check Logic

**Location:** `products/cost_planner/product.py` line 231

```python
if st.button("Continue to Full Assessment", ...):
    # Check if authenticated
    if auth.is_authenticated():
        st.session_state[f"{state_key}._step"] = 3  # Jump to profile_flags
    else:
        st.session_state[f"{state_key}._step"] = 2  # Go to auth_gate
    st.rerun()
```

### Auth Gate Rendering

**Location:** Standard module engine renders step 2 (auth_gate)

**After Render:** `_render_auth_gate_content()` called

```python
def _render_auth_gate_content(context: dict) -> None:
    st.divider()
    
    if auth.is_authenticated():
        st.success("✅ You're signed in! Click Continue to proceed.")
        return
    
    st.warning("🔒 **Authentication Required**")
    st.markdown("""...""")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔓 Sign In (Dev)", ...):
            auth.mock_login()
            st.rerun()
    with col2:
        if st.button("📝 Create Account (Dev)", ...):
            auth.mock_login()
            st.rerun()
```

### Mock Auth Controls (Sidebar)

**Location:** `products/cost_planner/product.py` line 37

```python
# Show mock authentication controls in sidebar (dev mode)
auth.mock_login_button()
```

**Displays:**
```
─────
### 🔧 Dev Tools
✓ Authenticated
*Logged in as: dev@example.com*
[🔓 Mock Logout]
*Mock authentication for development*
```

## Profile Flags Configuration

**Location:** `products/cost_planner/base_module_config.json` step 3

**Fields:**
1. **zip_code** (text, required)
   - For regional pricing calculations
   - Example: 98101

2. **veteran_status** (radio, required)
   - Options: Yes / No
   - Gates VA Benefits module

3. **home_owner** (radio, required)
   - Options: Yes / No
   - Gates Housing module (with care type check)

4. **medicaid_status** (radio, required)
   - Options: Yes / No / Not sure
   - Gates Medicaid Navigator module

**All fields required** - Cannot progress without completing all.

## Module Index Enhancements

### Conditional Display Logic

```python
# Get GCP recommendation for Home Decision gating
gcp_rec = get_gcp_recommendation()
is_in_home_care = gcp_rec == "In-Home Care"

modules = [
    {
        "key": "housing",
        "enabled": home_owner and not is_in_home_care,
        "condition": "Home ownership required • Not for In-Home Care" 
                     if not (home_owner and not is_in_home_care) 
                     else "Available",
    },
    {
        "key": "va_benefits",
        "enabled": veteran_status,
        "condition": "Veteran status required" if not veteran_status else "Available",
    },
    {
        "key": "medicaid",
        "enabled": medicaid_status,
        "condition": "Medicaid enrollment required" if not medicaid_status else "Currently enrolled",
    },
]
```

### Status Badge Colors

```python
if is_completed:
    status_badge = "✅ Complete"
    status_color = "#10b981"  # Green
elif is_in_progress:
    status_badge = "🔄 In Progress"
    status_color = "#f59e0b"  # Orange
else:
    status_badge = "○ Not Started"
    status_color = "#6b7280"  # Gray
```

### Condition Display Colors

```python
if module["enabled"]:
    condition_html = f"<div style='color: #10b981; ...'>✓ {condition}</div>"  # Green
else:
    condition_html = f"<div style='color: #ef4444; ...'>✗ {condition}</div>"  # Red
```

## Testing Checklist

### Authentication Flow
- [ ] Unauthenticated user sees auth gate
- [ ] Mock Login button works
- [ ] After login, skips auth gate on return
- [ ] Sidebar dev tools show auth status
- [ ] Mock Logout works

### Profile Flags Collection
- [ ] All 4 fields present
- [ ] All fields required
- [ ] Cannot continue without completing all
- [ ] ZIP code validates (optional: format check)
- [ ] Data saved to session state

### Module Visibility - Housing
- [ ] Enabled when home_owner=true AND NOT In-Home Care
- [ ] Disabled when home_owner=false
- [ ] Disabled when In-Home Care recommendation
- [ ] Shows correct condition text (green ✓ or red ✗)

### Module Visibility - VA Benefits
- [ ] Enabled when veteran_status=true
- [ ] Disabled when veteran_status=false
- [ ] Shows "Available" or "Veteran status required"

### Module Visibility - Medicaid
- [ ] Enabled when medicaid_status=true
- [ ] Disabled when medicaid_status=false
- [ ] Shows "Currently enrolled" or "Medicaid enrollment required"

### Module Visibility - Always On
- [ ] Income always visible
- [ ] Assets always visible
- [ ] Insurance always visible

### Regional Pricing Banner
- [ ] Shows when ZIP code entered
- [ ] Displays correct multiplier (+15% for 98101)
- [ ] Shows match type (WA ZIP exact, etc.)

### Module Navigation
- [ ] "Start Module" button navigates to module
- [ ] "Back to Module Index" returns to index
- [ ] Module status updates (Not Started → In Progress)
- [ ] Not-yet-implemented modules show friendly message

## Files Modified

**products/cost_planner/product.py:**
- Line 231: Updated Continue button to check authentication
- Line 345: Added GCP recommendation check for Home Decision gating
- Lines 364-421: Updated module definitions with conditional visibility
- Lines 431-438: Enhanced condition display with color coding

**No other files modified** - Using existing:
- `products/cost_planner/auth.py` - Mock authentication system
- `products/cost_planner/base_module_config.json` - Profile flags already configured
- `core/modules/engine.py` - Standard module rendering

## Next Steps (After Testing)

1. **Build Individual Modules:**
   - Income Sources module
   - Assets & Savings module
   - Health Insurance module
   - VA Benefits module (if veteran)
   - Medicaid Navigator (if enrolled)
   - Housing & Home Equity (if eligible)

2. **Add Module Content:**
   - Create `products/cost_planner/modules/{module_key}/module_config.py`
   - Define module steps, fields, and logic
   - Implement calculations and outcomes

3. **Summary & Results:**
   - Create financial summary page
   - Show total income vs. total costs
   - Identify gaps and recommendations
   - Generate action items

---

**Status:** ✅ Ready for Testing  
**Streamlit:** Running at http://localhost:8501  
**Branch:** dev  
**Date:** 2024-10-12
