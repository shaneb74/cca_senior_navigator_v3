# CSS Architecture (As of 2025-11-01)

## ✅ Current State: WORKING

GCP radio pills are rendering correctly with persistent styling after widget interactions.

## 📁 Active CSS Files

### Loaded by `app.py` (inject_css())

1. **`assets/css/global.css`** — Base typography, layout, app-level styles
2. **`assets/css/modules.css`** — Module-specific styles (contains legacy pill selectors, but overridden by ui_css.py)

### Loaded Dynamically

3. **`core/ui_css.py`** — JavaScript-based CSS injection for radio pills
   - Uses MutationObserver to maintain cascade priority after Streamlit Emotion re-injection
   - **THIS IS THE SOURCE OF TRUTH FOR PILL STYLING**
   - Verified working as of commit `5d91953`

### Not Loaded (Present but Inactive)

4. **`assets/css/tokens.css`** — Design tokens (colors, spacing, typography)
   - Present in repo but NOT loaded by app.py
   - May be used by specific components

5. **`assets/css/products.css`** — Product tile layout & borders
   - Present in repo but NOT loaded by app.py
   - Styles may be duplicated in global.css

6. **`assets/css/hubs.css`** — Legacy hub tile styling
   - Present in repo but NOT loaded by app.py
   - Likely redundant with global.css

### Archived (Removed from Active Directory)

7. **`assets/css/z_overrides.css`** → `archive/css_backup_2025-11-01/z_overrides.css.archived`
   - Was never loaded by app.py
   - Contained overrides that were applied elsewhere or not needed
   - Archived on 2025-11-01 for cleanup

## 🎯 Pill Styling Flow

```
GCP Module Render
    ↓
inject_pill_css() in core/ui_css.py
    ↓
JavaScript MutationObserver watches for Emotion changes
    ↓
Re-applies PILL_CSS after Emotion injection
    ↓
Pills maintain correct styling (black/white, no green artifacts)
```

## 🧹 Redundant Selectors

`assets/css/modules.css` contains 48 `stRadio` selectors that are effectively bypassed by `ui_css.py`.  
These could be removed in a future cleanup IF AND ONLY IF:
- All GCP modules are tested
- Pills persist correctly after interactions
- No regressions in other radio widget usage

## ⚠️ Important Metrics

- **!important declarations**: 537 across all CSS files
- **stRadio selectors**: 48 in modules.css (mostly redundant)
- **CSS files loaded**: 2 (global.css, modules.css)
- **Dynamic CSS injectors**: 1 (core/ui_css.py)

## 🔄 Safe Rollback

If CSS issues arise, restore from backup:

```bash
# Restore all CSS files
cp archive/css_backup_2025-11-01/*.css assets/css/

# Or restore specific files
cp archive/css_backup_2025-11-01/global.css assets/css/
cp archive/css_backup_2025-11-01/modules.css assets/css/
cp archive/css_backup_2025-11-01/z_overrides.css.archived assets/css/z_overrides.css
```

## 📌 Baseline Commit

**Commit `5d91953`**: "chore: mark GCP pills CSS as verified working (2025-11-01)"  
Use this as reference for known-good CSS state.

## 🚀 Future Optimization Opportunities

1. **Remove redundant stRadio selectors** from modules.css (after thorough testing)
2. **Consolidate global.css** to include products.css and hubs.css
3. **Load tokens.css** if design system tokens are standardized
4. **Reduce !important declarations** (currently 537)
5. **Migrate inline styles** to CSS classes where possible

## 🛡️ CSS Loading Guard

The current system is simple and works:
- 2 CSS files loaded in order
- 1 JavaScript injector for pills
- No cascading conflicts

**DO NOT** add new CSS files without updating `app.py` inject_css() function and testing thoroughly.
