# Single-Page Assessments Implementation Guide

**Date:** October 18, 2025  
**Status:** ✅ Fully Implemented  
**Affected Assessments:** Income, Assets, VA Benefits, Health Insurance, Life Insurance, Medicaid Navigation

---

## Overview

All 6 financial assessments now use **single-page rendering** - users see ALL input fields on one screen, well-organized into logical sections displayed in a clean 2-column layout.

### What Changed:

**BEFORE (Multi-Step Flow):**
```
Assessment Intro Screen
   ↓ [Continue]
Section 1 Input Screen  
   ↓ [Continue]
Section 2 Input Screen
   ↓ [Continue]
Results Screen
```

**AFTER (Single-Page):**
```
┌─────────────────────────────────────────────────┐
│ Assessment Title & Description                  │
├─────────────────────────────────────────────────┤
│ Navi Panel (guidance & encouragement)           │
├─────────────────────────────────────────────────┤
│ Section 1        │ Section 2                    │
│ [input fields]   │ [input fields]               │
├──────────────────┴──────────────────────────────┤
│ Section 3 (if applicable, spans full width)     │
├─────────────────────────────────────────────────┤
│ Summary Card (calculated total)                 │
├─────────────────────────────────────────────────┤
│ [Back] [Save] [Expert Review]                  │
└─────────────────────────────────────────────────┘
```

**NO MORE CLICKS** between sections - everything visible at once!

---

## Implementation Details

### Code Configuration

**File:** `products/cost_planner_v2/assessments.py`

**Dictionary:** `_SINGLE_PAGE_ASSESSMENTS`

```python
_SINGLE_PAGE_ASSESSMENTS: dict[str, dict[str, Any]] = {
    "income": { ... },
    "assets": { ... },
    "va_benefits": { ... },           # ← NEW
    "health_insurance": { ... },       # ← NEW
    "life_insurance": { ... },         # ← NEW
    "medicaid_navigation": { ... },    # ← NEW
}
```

### Routing Logic

```python
def _render_assessment(assessment_key: str, product_key: str) -> None:
    assessment_config = _load_assessment_config(assessment_key, product_key)
    
    # Check if this assessment should use single-page rendering
    if assessment_key in _SINGLE_PAGE_ASSESSMENTS:
        _render_single_page_assessment(
            assessment_key=assessment_key,
            assessment_config=assessment_config,
            product_key=product_key,
            settings=_SINGLE_PAGE_ASSESSMENTS[assessment_key],
        )
        return
    
    # Otherwise use multi-step flow (deprecated for financial assessments)
    run_assessment(assessment_key, assessment_config, product_key)
```

**Result:** When user clicks "Start" on any of the 6 assessments, they get the single-page layout.

---

## JSON Structure Requirements

For an assessment to work with single-page rendering, the JSON must follow this structure:

### Required Sections:

```json
{
  "key": "assessment_name",
  "title": "Assessment Title",
  "icon": "🎯",
  "sections": [
    {
      "id": "intro",
      "type": "intro",           // ← MUST have type="intro"
      "help_text": "...",
      "fields": []               // ← MUST be empty
    },
    {
      "id": "section1",
      // NO type property!       // ← MUST NOT have type property
      "title": "Section 1",
      "fields": [ /* ... */ ]    // ← MUST have fields array
    },
    {
      "id": "section2",
      // NO type property!
      "title": "Section 2", 
      "fields": [ /* ... */ ]
    },
    {
      "id": "results",
      "type": "results",         // ← MUST have type="results"
      "fields": []               // ← MUST be empty
    }
  ],
  "summary": {
    "type": "calculated",
    "formula": "sum(...)"
  }
}
```

### Section Filtering Logic:

```python
# Single-page renderer extracts field sections:
field_sections = [
    s for s in sections 
    if s.get("fields")                           # Must have fields
    and s.get("type") not in ["intro", "results"] # Must NOT be intro/results
]
```

**Result:** Sections with `fields` and without `type` property get rendered in 2-column layout.

---

## Visual Layout

### 2-Column Grid

Sections are displayed in pairs:

```
┌─────────────────────────┬─────────────────────────┐
│ Section 1               │ Section 2               │
│ ├─ Field 1              │ ├─ Field 1              │
│ ├─ Field 2              │ ├─ Field 2              │
│ └─ Field 3              │ └─ Field 3              │
└─────────────────────────┴─────────────────────────┘

┌─────────────────────────┬─────────────────────────┐
│ Section 3               │ Section 4               │
│ ├─ Field 1              │ (empty if odd number)   │
│ └─ Field 2              │                         │
└─────────────────────────┴─────────────────────────┘
```

### Styling:

- ✅ White card background
- ✅ Each section has icon + title
- ✅ Fields have inline help text
- ✅ Compact spacing
- ✅ Consistent with Income/Assets

### Example (VA Benefits):

```
┌─────────────────────────────────────────────────────┐
│ 🎖️ VA Benefits                                      │
│ Veterans Affairs benefits including disability...   │
├─────────────────────────────────────────────────────┤
│ Navi: "Benefit amounts will auto-populate..."       │
├─────────────────────────────────────────────────────┤
│ 🏅 VA Disability        │ 🤝 Aid & Attendance      │
│ ├─ Do you receive VA?   │ ├─ Do you receive A&A?  │
│ ├─ Disability rating    │ ├─ Monthly A&A amount   │
│ ├─ Dependents status    │ ├─ Household status     │
│ └─ Monthly amount       │ └─ Notes                │
│   (auto-calculated!)    │                         │
├─────────────────────────┴─────────────────────────┤
│ Summary: $2,156.95/month                          │
├─────────────────────────────────────────────────────┤
│ [← Back] [Save VA Benefits] [🚀 Expert Review →]  │
└─────────────────────────────────────────────────────┘
```

---

## Assessment Configurations

### 1. Income (4 field sections)

**Sections:**
- Household Context
- Social Security & Pensions
- Employment & Other Income
- Additional Income Sources

**Layout:** 2 columns × 2 rows

**Summary:** Total monthly income (calculated)

---

### 2. Assets (4 field sections)

**Sections:**
- Primary Residence
- Bank Accounts & Investments
- Retirement Accounts
- Other Assets

**Layout:** 2 columns × 2 rows

**Summary:** Net assets (total value - total debt)

---

### 3. VA Benefits (2 field sections) ⭐ NEW

**Sections:**
- VA Disability Compensation
- Aid & Attendance

**Layout:** 2 columns × 1 row

**Summary:** Total monthly VA benefits (calculated)

**Special Feature:** Auto-populates disability amount based on rating + dependents using 2025 official rates

---

### 4. Health Insurance (2 field sections) ⭐ NEW

**Sections:**
- Medical Plan
- Supplemental Coverage

**Layout:** 2 columns × 1 row

**Summary:** Annual out-of-pocket max (calculated)

**Fields:** Plan type (9 options including Medicare, Medicaid, VA, TRICARE), deductibles, premiums, supplemental coverage

---

### 5. Life Insurance (2 field sections) ⭐ NEW

**Sections:**
- Life Insurance
- Annuities

**Layout:** 2 columns × 1 row

**Summary:** Total accessible value (calculated)

**Note:** Only permanent life insurance with cash value (term life excluded)

---

### 6. Medicaid Navigation (3 field sections) ⭐ NEW

**Sections:**
- Status & Pathway
- Income & Assets Context
- Functional/Clinical Needs

**Layout:** 2 columns for first row, 1 column for second row (3 sections total)

**Summary:** Text description of assessment purpose (not calculated)

**Fields:** State selection (50 states + DC), Medicaid status, asset position, spend-down strategies, ADL/IADL tracking

---

## How to Test

### Step 1: Run the App

```bash
streamlit run app.py
```

### Step 2: Navigate to Assessments

1. Click "Cost Planner v2" from main menu
2. Click "Financial Assessments" button
3. You'll see the assessment hub with 6 cards

### Step 3: Test Each Assessment

**For VA Benefits:**
1. Click "Start" on VA Benefits card
2. **Verify:** You see ALL fields on one screen
   - ✅ VA Disability section on left
   - ✅ Aid & Attendance section on right
   - ✅ NO "Continue" button between sections
   - ✅ Summary card at bottom
   - ✅ Save button visible immediately

3. **Test auto-population:**
   - Select "Do you receive VA Disability?" → "Yes"
   - Select disability rating → "70%"
   - Select dependents → "Veteran with spouse"
   - **Verify:** Monthly amount auto-populates to **$1,908.95**

4. Click "Save VA Benefits Information"
5. **Verify:** Success message appears, data persists

**For Health Insurance:**
1. Click "Start" on Health Insurance card
2. **Verify:** Medical Plan and Supplemental Coverage sections side-by-side
3. Select plan type, enter deductibles
4. **Verify:** Summary shows annual OOP max
5. Save and verify persistence

**For Life Insurance:**
1. Click "Start" on Life Insurance card
2. **Verify:** Life Insurance and Annuities sections side-by-side
3. Enter cash values
4. **Verify:** Summary calculates total accessible value
5. Save and verify persistence

**For Medicaid Navigation:**
1. Click "Start" on Medicaid Navigation card
2. **Verify:** All 3 sections visible (first 2 side-by-side, third full-width)
3. Select state, Medicaid status
4. **Verify:** No summary calculation (text type summary)
5. Save and verify persistence

### Step 4: Visual Consistency Check

Compare any new assessment to Income or Assets:
- ✅ Same white card background
- ✅ Same section header styling (icon + title)
- ✅ Same field label styling
- ✅ Same inline help text formatting
- ✅ Same summary card styling
- ✅ Same button layout

---

## Troubleshooting

### Issue: Assessment still shows multi-step flow

**Possible Causes:**

1. **Browser cache:** Clear browser cache and hard reload (Cmd+Shift+R on Mac)

2. **Session state:** Reset session state:
   ```python
   # In Streamlit, click hamburger menu → "Clear cache" → Rerun
   ```

3. **Assessment not in dict:** Verify assessment key is in `_SINGLE_PAGE_ASSESSMENTS`
   ```bash
   grep -A 5 "va_benefits" products/cost_planner_v2/assessments.py
   ```

4. **JSON structure:** Verify field sections don't have `type` property
   ```bash
   python -c "import json; print([s.get('type', 'NONE') for s in json.load(open('products/cost_planner_v2/modules/assessments/va_benefits.json'))['sections']])"
   # Should output: ['intro', 'NONE', 'NONE', 'results']
   ```

### Issue: Sections not rendering side-by-side

**Possible Causes:**

1. **Screen too narrow:** Single-page layout requires minimum width (desktop/tablet)

2. **Section count:** Verify assessment has 2+ field sections:
   ```bash
   python -c "import json; field_sections = [s for s in json.load(open('products/cost_planner_v2/modules/assessments/va_benefits.json'))['sections'] if s.get('fields') and s.get('type') not in ['intro', 'results']]; print(f'{len(field_sections)} field sections')"
   ```

3. **Layout property:** Sections should have `"layout": "single_column"` (not required but recommended)

### Issue: Summary not calculating

**Possible Causes:**

1. **Missing summary config:** Verify JSON has `summary` object with `formula`
   ```bash
   python -c "import json; print(json.load(open('products/cost_planner_v2/modules/assessments/va_benefits.json')).get('summary'))"
   ```

2. **Invalid formula:** For calculated summaries, use `sum(field1, field2, ...)`
   ```json
   "summary": {
     "type": "calculated",
     "formula": "sum(va_disability_monthly, aid_attendance_monthly)",
     "label": "Total Monthly VA Benefits",
     "display_format": "${:,.2f}/month"
   }
   ```

3. **Text summary:** Some assessments (like Medicaid Navigation) use `type: "text"` with no calculation

---

## Comparison: Old vs New User Experience

### Before Implementation:

**User clicks "Start" on VA Benefits:**
```
Screen 1: Intro
"Review your VA benefits..."
[Continue]
  ↓
Screen 2: VA Disability section
"Do you receive VA Disability?"
[rating dropdown]
[dependents dropdown]
[Continue]
  ↓
Screen 3: Aid & Attendance section
"Do you receive A&A?"
[monthly amount input]
[Continue]
  ↓
Screen 4: Results
"Total: $2,156.95/month"
[Save & Exit]
```

**Total clicks:** 4 (Continue, Continue, Continue, Save)

---

### After Implementation:

**User clicks "Start" on VA Benefits:**
```
Single Screen:
┌─────────────────────────────────────────────────┐
│ Help text at top                                │
├─────────────────────────────────────────────────┤
│ VA Disability      │ Aid & Attendance           │
│ [all fields]       │ [all fields]               │
├─────────────────────────────────────────────────┤
│ Summary: $2,156.95/month                        │
├─────────────────────────────────────────────────┤
│ [Back] [Save] [Expert Review]                  │
└─────────────────────────────────────────────────┘
```

**Total clicks:** 1 (Save)

**Result:** 75% reduction in clicks, instant overview of all data points!

---

## Developer Notes

### Adding New Single-Page Assessment

To add a new assessment to single-page rendering:

**1. Create JSON with proper structure:**
```json
{
  "key": "new_assessment",
  "sections": [
    {"id": "intro", "type": "intro", "fields": []},
    {"id": "section1", "title": "...", "fields": [...]},
    {"id": "section2", "title": "...", "fields": [...]},
    {"id": "results", "type": "results", "fields": []}
  ],
  "summary": {
    "type": "calculated",
    "formula": "sum(...)"
  }
}
```

**2. Add to `_SINGLE_PAGE_ASSESSMENTS` dict:**
```python
"new_assessment": {
    "save_label": "Save Information",
    "success_message": "Assessment saved.",
    "navi": {
        "title": "Assessment Title",
        "reason": "Why we're collecting this data",
        "encouragement": {
            "icon": "🎯",
            "text": "Helpful tip for user",
            "status": "getting_started",
        },
    },
    "expert_requires": ["income", "assets"],
    "expert_disabled_text": "Complete required assessments first.",
}
```

**3. Test:**
- Verify single-page layout renders
- Check 2-column layout
- Validate summary calculation
- Test save/persistence
- Compare styling to Income/Assets

---

## Summary

✅ **All 6 financial assessments use single-page rendering**  
✅ **No more multi-step flows with "Continue" buttons**  
✅ **All input fields visible on one screen**  
✅ **Sections organized in clean 2-column layout**  
✅ **Consistent styling across all assessments**  
✅ **VA Benefits includes auto-population feature**  
✅ **Better UX: 75% reduction in clicks**  

**Status:** Fully implemented and ready for testing!

---

**Last Updated:** October 18, 2025  
**Branch:** `assessment-updates`  
**Commits:** `06d5cf8` (auto-population), `6728b08` (error handling)
