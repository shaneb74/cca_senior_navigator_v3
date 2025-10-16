# Button Styling Fix - White-on-White Secondary Buttons

**Branch:** `navi-redesign-2`  
**Status:** ✅ Complete  
**Commit:** `9acef28`

## Problem

Streamlit's secondary buttons (`st.button()` with default kind) were rendering with white background and black text on white pages, creating invisible or very low-contrast buttons. This affected:

- **AI Advisor** - Question chips were nearly invisible
- **FAQs** - Suggested question buttons had poor contrast
- **General navigation** - Any secondary button on white backgrounds

## Solution

Added targeted CSS in `assets/css/global.css` to recolor **only** the white-on-white secondary buttons while preserving all existing styled buttons (especially the black/gray radio pills in GCP, Cost Planner, and PFMA).

### CSS Approach

```css
:root {
  --chip-bg: #E9F1FF;           /* subtle blue — matches "Questions I've Asked" banner */
  --chip-bg-hover: #DCE8FF;     /* ~6-8% darker for hover */
  --chip-text: #0D1F4B;         /* app navy */
  --chip-ring: rgba(13,31,75,.35); /* focus ring */
}

/* Only apply to white-on-white secondary buttons */
button[kind="secondary"][data-testid="stBaseButton-secondary"] {
  background-color: var(--chip-bg) !important;
  color: var(--chip-text) !important;
  border: 1px solid transparent !important;
  border-radius: 10px;
  padding: 10px 14px;
  transition: background-color .12s ease, box-shadow .12s ease;
}
```

### Key Features

1. **Precise Targeting**
   - Uses `button[kind="secondary"][data-testid="stBaseButton-secondary"]`
   - Only affects Streamlit's default secondary buttons
   - Does NOT affect custom-styled buttons

2. **Exclusion Safeguard**
   - Explicitly excludes `.mod-actions` buttons (GCP/Cost Planner/PFMA pills)
   - Preserves existing dark/neutral styled buttons
   - No regression to module question selectors

3. **Accessibility**
   - Clear hover state with darker blue + subtle shadow
   - `focus-visible` ring for keyboard navigation
   - Disabled state with reduced opacity

4. **Visual Consistency**
   - Matches the subtle blue (#E9F1FF) from "Questions I've Asked" banner
   - Complements Navi's signature blue (#4A90E2)
   - Professional, minimal visual treatment

## What Changed

### Before
```
┌─────────────────────────────┐
│ [  Invisible Button  ]      │  ← White text on white bg
│                             │
│ Hard to see, poor UX        │
└─────────────────────────────┘
```

### After
```
┌─────────────────────────────┐
│ ┌───────────────────┐       │
│ │ Visible Button    │       │  ← Subtle blue bg, navy text
│ └───────────────────┘       │
│                             │
│ Clear, accessible, on-brand │
└─────────────────────────────┘
```

## Affected Pages

### ✅ Fixed (Improved Contrast)
- **AI Advisor** (`pages/ai_advisor.py`)
  - Question chips now have subtle blue background
  - Hover state provides visual feedback
  - Matches banner styling

- **FAQs** (any FAQ pages)
  - Suggested questions visible
  - Clear call-to-action buttons

- **General UI** (anywhere secondary buttons appear on white)
  - Consistent treatment across app
  - No more invisible buttons

### ✅ Preserved (No Changes)
- **Guided Care Plan** question selectors
  - Black/gray radio-style pills unchanged
  - Module actions unaffected

- **Cost Planner** question selectors
  - Dark themed option buttons unchanged
  - Navigation buttons unaffected

- **PFMA** question selectors
  - Existing styling preserved
  - No visual regressions

## CSS Variables

```css
--chip-bg: #E9F1FF;           /* Base background - subtle blue */
--chip-bg-hover: #DCE8FF;     /* Hover state - 6-8% darker */
--chip-text: #0D1F4B;         /* Text color - app navy */
--chip-ring: rgba(13,31,75,.35); /* Focus ring - accessible */
```

These can be adjusted globally if needed for brand updates.

## Testing Checklist

- [x] AI Advisor question chips have blue background
- [x] Hover state shows darker blue + shadow
- [x] Focus state shows keyboard ring
- [x] GCP radio pills unchanged (black/gray)
- [x] Cost Planner radio pills unchanged
- [x] PFMA radio pills unchanged
- [x] No layout shifts anywhere
- [x] Disabled buttons show reduced opacity
- [x] Mobile responsive (no breakage)

## Technical Details

### Why CSS Instead of config.toml?

Streamlit's `config.toml` theme settings control primary button colors but don't reliably control secondary buttons. CSS gives us:

1. **Precise control** - Target exact button types
2. **Exclusion rules** - Preserve existing styled buttons  
3. **States** - Hover, focus, disabled
4. **Consistency** - Guaranteed rendering across all pages

### Selector Specificity

The selector `button[kind="secondary"][data-testid="stBaseButton-secondary"]` is specific enough to:
- Target only Streamlit's secondary buttons
- Avoid conflict with custom buttons
- Be overridden by `.mod-actions` exclusion rule

### !important Usage

Used strategically to override Streamlit's inline styles:
- `background-color` - Override white default
- `color` - Override black default
- `border` - Remove Streamlit's default border

The `.mod-actions` exclusion uses `initial` to restore original values.

## Migration Notes

### If You Need to Adjust Colors

Edit the CSS variables in `assets/css/global.css`:

```css
:root {
  --chip-bg: #YOUR_COLOR;       /* Change base background */
  --chip-bg-hover: #YOUR_COLOR; /* Change hover state */
  --chip-text: #YOUR_COLOR;     /* Change text color */
}
```

### If You Need to Exclude More Areas

Add specific exclusion rules:

```css
/* Example: Exclude custom area */
.my-custom-area button[kind="secondary"][data-testid="stBaseButton-secondary"] {
  background-color: initial !important;
  color: initial !important;
  border: initial !important;
  padding: initial !important;
}
```

## Related Files

- **`assets/css/global.css`** - Main CSS file with button styling
- **`pages/ai_advisor.py`** - Primary beneficiary (question chips)
- **`assets/css/modules.css`** - Module-specific button styles (preserved)

## Acceptance Criteria

✅ All white-on-white buttons now have subtle blue fill  
✅ Hover and focus states are visible and accessible  
✅ Black and gray pills in GCP/Cost Planner/PFMA remain untouched  
✅ No layout shifts or regressions anywhere in the app  
✅ Consistent with Navi's brand colors  
✅ Professional, minimal visual treatment  

## Before/After Screenshots

### AI Advisor Question Chips

**Before:**
- White buttons on white background
- Low contrast, hard to see
- Poor user experience

**After:**
- Subtle blue background (#E9F1FF)
- Clear navy text (#0D1F4B)
- Matches banner styling
- Professional appearance

---

**Status:** ✅ Ready for testing and merge
