# Navi Display Cleanup Fix

**Date:** October 14, 2025  
**Issue:** Duplicate Navi displays and redundant progress bar

---

## 🐛 Problem

GCP module was showing **TWO separate Navi displays**:

1. **Blue box** (top) - Main Navi panel from `render_navi_panel()`
   - Shows step progress "1/6" on right
   - Correct display with full Navi intelligence

2. **Purple box** (below blue) - Step-specific guidance from `_render_navi_guide_bar()`
   - Showed once on intro, different content on other steps
   - Created confusion with duplicate messaging
   - Was rendered by module engine for step-level guidance

Additionally, there was a **redundant horizontal progress bar** below the header since Navi panel already shows step progress.

---

## ✅ Solution

### **1. Disabled purple Navi guide bar**

**File:** `core/modules/engine.py` (line ~72)

**Change:** Commented out `_render_navi_guide_bar()` call

```python
# DISABLED: Now using main Navi panel (blue box) which shows step progress
# The purple box was duplicate - main Navi panel at page top handles all guidance
# _render_navi_guide_bar(config, step, state, step_index, progress_total)
```

**Rationale:**
- Main Navi panel (blue) already provides contextual guidance
- Purple box was redundant and confusing
- Single source of Navi guidance improves UX consistency

### **2. Removed redundant progress bar**

**File:** `core/modules/engine.py` (line ~122)

**Change:** Removed segmented rail progress bar from `_render_header()`

```python
def _render_header(...) -> None:
    """Render module header without progress bar (Navi panel handles progress)."""
    # Progress bar removed - Navi panel at top now shows step progress (X/Y)
```

**Rationale:**
- Navi panel already shows step progress (e.g., "1/6")
- Horizontal progress bar was duplicate information
- Cleaner header layout without redundant visual elements

---

## 🎨 Visual Changes

### **Before:**
```
┌─────────────────────────────────────────────────────────┐
│ 🤖 Navi: Welcome to the Guided Care Plan        1/6    │ ← Blue (keep)
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│ ✓ Let's figure out what level of care is right for you │ ← Purple (remove)
└─────────────────────────────────────────────────────────┘
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ← Progress bar (remove)
← Back    Welcome to the Guided Care Plan
```

### **After:**
```
┌─────────────────────────────────────────────────────────┐
│ 🤖 Navi: Welcome to the Guided Care Plan        1/6    │ ← Blue only
└─────────────────────────────────────────────────────────┘
← Back    Welcome to the Guided Care Plan
```

---

## 🧪 Testing

**Test Steps:**
1. Navigate to GCP from Concierge Hub
2. Click "Start" on intro page
3. Verify only ONE Navi display (blue box with step count)
4. Verify NO purple box below
5. Verify NO horizontal progress bar below header
6. Progress through multiple steps
7. Confirm Navi box updates with step-specific guidance
8. Confirm step count increments (1/6 → 2/6 → 3/6, etc.)

**Expected Result:**
✅ Single blue Navi panel at top  
✅ Step progress shows "X/Y" on right side of panel  
✅ No duplicate purple box  
✅ No redundant progress bar  
✅ Clean header layout  

---

## 📁 Files Modified

1. **`core/modules/engine.py`**
   - Line ~72: Commented out `_render_navi_guide_bar()` call
   - Line ~122: Removed progress bar HTML from `_render_header()`
   - Added comments explaining why removed

---

## 🔧 Architecture Notes

### **Navi Display Hierarchy:**

```
┌─ Page Level (Product/Hub) ───────────────────────────┐
│  render_navi_panel()                                  │
│  - Shows journey context                             │
│  - Shows step progress (X/Y)                          │
│  - Primary Navi intelligence layer                    │
└───────────────────────────────────────────────────────┘
         ↓
┌─ Module Level (Engine) ───────────────────────────────┐
│  _render_navi_guide_bar() [DISABLED]                  │
│  - Was step-specific guidance                         │
│  - Created duplicate messaging                        │
│  - Now consolidated into main panel                   │
└───────────────────────────────────────────────────────┘
```

**Decision:** Use **single Navi panel** at page level for all guidance, rather than splitting between page-level and step-level displays.

---

## 💡 Future Enhancements

If step-specific guidance is needed in the future:

**Option A:** Embed in main Navi panel (recommended)
- Update `render_navi_panel()` to accept step-specific context
- Keep single source of Navi messaging
- Maintains consistent UX

**Option B:** Use field-level tooltips
- Add `guidance` field to questions in module.json
- Show as inline help text or tooltips
- Keeps step-level hints without duplicate panels

**Option C:** Add collapsible section in main panel
- Main message always visible
- "Learn more" expander for step-specific details
- Preserves single panel architecture

---

## 📊 Impact

**UX Improvements:**
- ✅ Eliminated confusion from duplicate Navi displays
- ✅ Cleaner visual hierarchy
- ✅ Single source of progress information
- ✅ More screen space for actual content

**Code Quality:**
- ✅ Removed redundant rendering logic
- ✅ Clear comments explaining architecture decision
- ✅ Preserved `_render_navi_guide_bar()` function (just disabled) for potential future use

**Performance:**
- ✅ Slightly faster rendering (one less HTML block)
- ✅ Less CSS processing

---

## ✅ Status

**COMPLETE** - Changes tested and working correctly.

- [x] Purple Navi box removed
- [x] Progress bar removed
- [x] Blue Navi panel working with step count
- [x] GCP module rendering cleanly
- [x] Documentation updated

---

**Ready for production! 🎉**
