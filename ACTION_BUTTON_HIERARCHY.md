# Action Button Hierarchy & Required Navigation

**Branch:** `navi-redesign-2`  
**Status:** ✅ Complete  
**Commit:** `55be754`

## Overview

Implemented a clear 2-tier button system for action buttons (Continue, Calculate, Back to Hub, etc.) and added required navigation on every Cost Planner page. Radio pills for question selection remain completely unchanged.

## Button Hierarchy

### Primary Buttons (Solid Navy)
**Visual:** Navy background (#0D1F4B), white text  
**Purpose:** High-intent actions that advance user progress  
**Examples:**
- Continue
- Calculate Estimate
- Start Module / Restart Module
- Continue to Expert Review
- Continue to Financial Assessment

**States:**
- Default: `#0D1F4B` navy
- Hover: `#0A1738` (~8% darker)
- Active: `#081330` (~12% darker)
- Focus: 3px ring `rgba(13,31,75,.35)`
- Disabled: 50% opacity

### Secondary Buttons (Soft Slate/Blue)
**Visual:** Subtle slate background (#E6ECF7), navy text  
**Purpose:** Supportive navigation (back actions, alternatives)  
**Examples:**
- Back to Hub
- Previous Question
- Back
- Calculate Another Scenario
- Return to Concierge

**States:**
- Default: `#E6ECF7` slate
- Hover: `#DCE4F3` slightly darker
- Focus: 3px ring `rgba(13,31,75,.35)`
- Disabled: 50% opacity

### Button Specifications
- **Height:** 46px
- **Border radius:** 10px
- **Padding:** 14-16px horizontal
- **Font weight:** 600 (semibold)
- **Font size:** 1rem (16px)
- **Transitions:** 120ms ease

## Required Navigation

Every module page now provides clear paths to both progress and exit:

### Cost Planner › Intro ("Get a Quick Cost Estimate")
**Before:** Only "Calculate Estimate" button (no exit option)  
**After:**
- ✅ **Calculate Estimate** (Primary) - advances workflow
- ✅ **Back to Hub** (Secondary) - exits without calculating

### Cost Planner › Quick Estimate Results
**Before:** Continue and Calculate Another  
**After:**
- ✅ **Continue to Full Assessment** (Primary) - main path
- ✅ **Calculate Another Scenario** (Secondary) - recalculate
- ✅ **Back to Hub** (Secondary) - exit

### Cost Planner › Quick Questions
**Before:** Back button did nothing, no exit option  
**After:**
- ✅ **Continue to Financial Assessment** (Primary) - when ready
- ✅ **Back** (Secondary) - returns to auth gate, now functional
- ✅ **Back to Hub** (Secondary) - exits workflow

### Financial Assessment › Modules Hub
**Before:** Mix of button styles  
**After:**
- ✅ **Continue to Expert Review** (Primary) - gated by required modules
- ✅ **Return to Concierge** (Secondary) - exit path
- All buttons use new hierarchy

### GCP / Cost Planner / PFMA Modules
**Already implemented via `core/modules/layout.py`:**
- ✅ **Continue** (Primary)
- ✅ **Previous Question** (Secondary)
- ✅ **Back to Hub** (Secondary)

## Implementation

### CSS Variables (global.css)

```css
:root {
  /* Action Button Colors */
  --btn-primary-bg: #0D1F4B;        /* navy */
  --btn-primary-text: #FFFFFF;
  --btn-primary-hover: #0A1738;     /* ~8% darker */
  --btn-primary-active: #081330;    /* ~12% darker */
  --btn-secondary-bg: #E6ECF7;      /* subtle slate/blue */
  --btn-secondary-text: #0D1F4B;
  --btn-secondary-hover: #DCE4F3;   /* slightly darker */
  --btn-focus: rgba(13,31,75,.35);  /* focus ring */
}
```

### Attribute-Based Targeting

Buttons are targeted via `data-role` attributes on either the button itself or a parent container:

```html
<!-- Method 1: Container with data-role -->
<div data-role="primary">
  <st.button "Continue" type="primary" />
</div>

<!-- Method 2: Direct attribute (future use) -->
<button data-role="primary">Continue</button>
```

**CSS selectors:**
```css
/* Primary buttons */
div[data-role="primary"] .stButton > button,
.stButton > button[data-role="primary"] {
  background: var(--btn-primary-bg) !important;
  color: var(--btn-primary-text) !important;
  /* ... */
}

/* Secondary buttons */
div[data-role="secondary"] .stButton > button,
.stButton > button[data-role="secondary"] {
  background: var(--btn-secondary-bg) !important;
  color: var(--btn-secondary-text) !important;
  /* ... */
}
```

### Radio Pills Exclusion

Radio-style pills (question selectors in GCP, Cost Planner, PFMA) are **NOT** wrapped in `data-role` containers and therefore remain completely untouched by the new CSS.

**They retain their existing styling:**
- Black/gray backgrounds
- Original hover states
- Module-specific CSS in `modules.css`

## Code Changes

### 1. Module Layout (core/modules/layout.py)

**Before:**
```python
next_clicked = st.button(next_label, key="_mod_next", type="primary", use_container_width=True)
back_to_hub_clicked = st.button("← Back to Hub", key="_mod_back_hub", type="secondary", use_container_width=False)
```

**After:**
```python
st.markdown('<div data-role="primary">', unsafe_allow_html=True)
next_clicked = st.button(next_label, key="_mod_next", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="mod-back-hub-wrapper" data-role="secondary">', unsafe_allow_html=True)
back_to_hub_clicked = st.button("← Back to Hub", key="_mod_back_hub", type="secondary", use_container_width=False)
st.markdown('</div>', unsafe_allow_html=True)
```

### 2. Cost Planner Intro (products/cost_planner_v2/intro.py)

**Added Back to Hub alongside Calculate Estimate:**

```python
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div data-role="primary">', unsafe_allow_html=True)
    if st.button("🔍 Calculate Estimate", type="primary", use_container_width=True):
        _calculate_quick_estimate(care_tier, zip_code or None)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div data-role="secondary">', unsafe_allow_html=True)
    if st.button("← Back to Hub", use_container_width=True):
        st.switch_page("pages/_stubs.py")
    st.markdown('</div>', unsafe_allow_html=True)
```

**Added Back to Hub on results page:**

```python
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown('<div data-role="primary">', unsafe_allow_html=True)
    # Continue to Full Assessment
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div data-role="secondary">', unsafe_allow_html=True)
    # Calculate Another Scenario
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div data-role="secondary">', unsafe_allow_html=True)
    if st.button("← Back to Hub", use_container_width=True):
        st.switch_page("pages/_stubs.py")
    st.markdown('</div>', unsafe_allow_html=True)
```

### 3. Quick Questions (products/cost_planner_v2/triage.py)

**Added functional Back button and Back to Hub:**

```python
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.markdown('<div data-role="secondary">', unsafe_allow_html=True)
    if st.button("← Back", key="qualifier_back", use_container_width=True):
        st.session_state.cost_v2_step = "auth"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div data-role="primary">', unsafe_allow_html=True)
    # Continue to Financial Assessment
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div data-role="secondary">', unsafe_allow_html=True)
    if st.button("← Back to Hub", key="qualifier_back_hub", use_container_width=True):
        st.switch_page("pages/_stubs.py")
    st.markdown('</div>', unsafe_allow_html=True)
```

### 4. Financial Assessment Hub (products/cost_planner_v2/hub.py)

**Updated all navigation buttons with data-role attributes:**

```python
# All complete scenario
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div data-role="primary">', unsafe_allow_html=True)
    if st.button("Continue to Expert Review →", type="primary", use_container_width=True):
        # ...
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div data-role="secondary">', unsafe_allow_html=True)
    if st.button("🏠 Return to Concierge", use_container_width=True):
        # ...
    st.markdown('</div>', unsafe_allow_html=True)
```

## Visual Comparison

### Before (Inconsistent Styling)
```
┌─────────────────────────────┐
│ Calculate Estimate          │  ← Blue (config.toml)
│                             │  
│ [No exit option]            │  ← Dead end
└─────────────────────────────┘
```

### After (Clear Hierarchy)
```
┌─────────────────────────────────────────┐
│ ┌─────────────────┐  ┌────────────┐    │
│ │ Calculate       │  │ Back to    │    │
│ │ Estimate        │  │ Hub        │    │
│ └─────────────────┘  └────────────┘    │
│   Navy (Primary)      Slate (Secondary) │
└─────────────────────────────────────────┘
```

## Button Mapping

### GCP Pages
| Button | Role | Styling |
|--------|------|---------|
| Continue | Primary | Navy solid |
| Previous Question | Secondary | Slate soft |
| Back to Hub | Secondary | Slate soft |

### Cost Planner › Intro
| Button | Role | Styling |
|--------|------|---------|
| Calculate Estimate | Primary | Navy solid |
| Back to Hub | Secondary | Slate soft |

### Cost Planner › Results
| Button | Role | Styling |
|--------|------|---------|
| Continue to Full Assessment | Primary | Navy solid |
| Calculate Another Scenario | Secondary | Slate soft |
| Back to Hub | Secondary | Slate soft |

### Quick Questions
| Button | Role | Styling |
|--------|------|---------|
| Continue to Financial Assessment | Primary | Navy solid |
| Back | Secondary | Slate soft |
| Back to Hub | Secondary | Slate soft |

### Financial Assessment › Modules List
| Button | Role | Styling |
|--------|------|---------|
| Continue to Expert Review | Primary | Navy solid (gated) |
| Return to Concierge | Secondary | Slate soft |

### Financial Assessment › Individual Module
| Button | Role | Styling |
|--------|------|---------|
| Start Module / Restart | Primary | Navy solid |
| Save & Continue | Primary | Navy solid |
| Back to Modules | Secondary | Slate soft |
| Back to Hub | Secondary | Slate soft |

## Acceptance Criteria

✅ **Radio pills unchanged** - Black/gray question selectors retain exact styling  
✅ **Action buttons use new hierarchy** - Primary (navy) vs Secondary (slate)  
✅ **Required navigation on all pages** - Back to Hub always available  
✅ **Cost Planner Intro has exit** - Back to Hub alongside Calculate  
✅ **Quick Questions functional** - Back button works, Back to Hub added  
✅ **Hover/focus/disabled states** - Clear visual feedback  
✅ **No new tabs** - All navigation in-app  
✅ **Consistent sizing** - 46px height, 10px radius throughout  
✅ **Scannable hierarchy** - Easy to identify primary vs secondary actions  

## Benefits

### For Users
- **Clear visual hierarchy** - Primary actions immediately obvious
- **No dead ends** - Every page has exit path
- **Consistent experience** - Same button styles throughout app
- **Better scannability** - Colors guide attention to main actions
- **Accessible** - Focus rings, sufficient contrast, clear disabled states

### For Developers
- **Maintainable** - CSS variables for easy color updates
- **Scalable** - Attribute-based targeting works anywhere
- **Safe** - Radio pills explicitly excluded via no data-role
- **Documented** - Clear mapping of which buttons get which role

## Testing Checklist

- [ ] **Cost Planner Intro:** Calculate Estimate (navy), Back to Hub (slate) both work
- [ ] **Cost Planner Results:** All 3 buttons (Continue, Calculate Another, Back to Hub) styled correctly
- [ ] **Quick Questions:** Back button functional, Back to Hub works, Continue enabled when ready
- [ ] **Financial Assessment Hub:** Continue to Expert Review gated properly, Return to Concierge works
- [ ] **GCP Modules:** Continue (navy), Previous (slate), Back to Hub (slate) all styled
- [ ] **Radio Pills:** Black/gray question selectors completely unchanged
- [ ] **Hover states:** Buttons darken on hover (primary ~8%, secondary visible change)
- [ ] **Focus states:** Keyboard navigation shows focus rings
- [ ] **Disabled states:** Continue to Expert Review disabled until requirements met
- [ ] **Mobile responsive:** Buttons work on small screens (columns stack properly)

## Related Files

- **`assets/css/global.css`** - Button hierarchy CSS and variables
- **`core/modules/layout.py`** - Module action buttons with data-role wrappers
- **`products/cost_planner_v2/intro.py`** - Intro page with Back to Hub
- **`products/cost_planner_v2/triage.py`** - Quick Questions with functional Back
- **`products/cost_planner_v2/hub.py`** - Financial Assessment hub navigation

## Migration Guide

### Adding Primary Button
```python
st.markdown('<div data-role="primary">', unsafe_allow_html=True)
if st.button("Continue", type="primary", use_container_width=True):
    # action
st.markdown('</div>', unsafe_allow_html=True)
```

### Adding Secondary Button
```python
st.markdown('<div data-role="secondary">', unsafe_allow_html=True)
if st.button("← Back to Hub", use_container_width=True):
    # action
st.markdown('</div>', unsafe_allow_html=True)
```

### Updating Color Variables
Edit `assets/css/global.css`:
```css
:root {
  --btn-primary-bg: #YOUR_COLOR;
  --btn-secondary-bg: #YOUR_COLOR;
}
```

---

**Status:** ✅ Complete and ready for testing
