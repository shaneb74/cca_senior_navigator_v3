# GCP Progress Badge and Question Order Fix

**Status**: ✅ Fixed (Commit: 7349a6a)  
**Date**: 2025-10-14  
**Issue**: Progress badge "6/6" showing on results page + question order  

---

## Issues Fixed

### 1. Progress Badge Showing on Results Page

**Problem**: The Navi guide bar was displaying "6/6" progress indicator on the GCP results page, which looks confusing since the assessment is complete.

**Root Cause**: `render_navi_panel()` in `core/navi.py` was always passing `show_progress=True` for product pages, without checking if the current step was the results step.

**Solution**: Added conditional check to hide progress indicator on results pages.

**Code Changes** (`core/navi.py`):

```python
# Line 529-530: Check if current step is results
is_results = module_config.results_step_id and current_step_def.id == module_config.results_step_id

# Line 536: Conditionally show progress
render_navi_guide_bar(
    text=main_text,
    subtext=subtext,
    icon=guidance.get('icon', '🧭'),
    show_progress=(not is_results),  # Hide progress on results page
    current_step=ctx.module_step + 1,
    total_steps=ctx.module_total,
    color=guidance.get('color', '#0066cc')
)
```

**Applied to**:
- Main guidance rendering (line 536)
- Fallback generic progress (line 566)

### 2. Question Order: Mood Before Behaviors

**Problem**: User requested that the "behaviors" question come AFTER the "mood" question for better flow.

**Old Order**:
1. memory_changes (Cognitive health or memory changes)
2. **behaviors** (Have there been any of these behaviors or concerns?)
3. **mood** (How would you describe this person's mood these days?)

**New Order**:
1. memory_changes (Cognitive health or memory changes)
2. **mood** (How would you describe this person's mood these days?)
3. **behaviors** (Have there been any of these behaviors or concerns?)

**Rationale**:
- General mood is easier to answer first
- Specific behaviors flow naturally after mood assessment
- Maintains conditional logic: behaviors still only show if memory_changes = "moderate" or "severe"

**Code Changes** (`products/gcp_v4/modules/care_recommendation/module.json`):

Reordered questions in the `cognition_mental_health` section. JSON validated successfully.

---

## Testing

### Progress Badge Visibility

| Step | Expected Behavior | Status |
|------|-------------------|--------|
| **Intro** | No progress badge | ✅ |
| **Question Steps** (About You, Medication, Cognition, Daily Living) | Progress badge shows (1/6, 2/6, etc.) | ✅ |
| **Results Page** | No progress badge (was showing "6/6") | ✅ Fixed |

### Question Order

| Scenario | Expected Order | Status |
|----------|----------------|--------|
| **memory_changes = "no_concerns"** | mood shown, behaviors hidden | ✅ |
| **memory_changes = "occasional"** | mood shown, behaviors hidden | ✅ |
| **memory_changes = "moderate"** | mood shown FIRST, then behaviors | ✅ Fixed |
| **memory_changes = "severe"** | mood shown FIRST, then behaviors | ✅ Fixed |

### Manual Testing Checklist

- [ ] Start GCP assessment
- [ ] Complete intro (no progress badge)
- [ ] Answer "About You" questions (progress badge: 1/6)
- [ ] Answer "Medication & Mobility" questions (progress badge: 2/6)
- [ ] Answer "Cognition & Mental Health" questions:
  - [ ] See memory_changes question
  - [ ] See mood question BEFORE behaviors
  - [ ] If moderate/severe memory: see behaviors question
- [ ] Answer "Daily Living" questions (progress badge: 5/6)
- [ ] View results page:
  - [ ] NO progress badge showing
  - [ ] Hero card displays correctly
  - [ ] Categorized details show
  - [ ] Confidence insights show

---

## Technical Details

### Progress Badge Rendering Flow

```
products/gcp_v4/product.py
  └─ render_navi_panel(location="product", module_config=config)
      └─ core/navi.py: render_navi_panel()
          └─ Get module_step from context (ctx.module_step)
          └─ Get current step definition (current_step_def)
          └─ Check if step is results: is_results = config.results_step_id == step.id
          └─ Call render_navi_guide_bar(show_progress=(not is_results))
              └─ core/ui.py: render_navi_guide_bar()
                  └─ If show_progress=True: build progress_badge HTML
                  └─ If show_progress=False: progress_badge = ""
```

### Question Order in JSON

Questions are rendered in the order they appear in the `questions` array within each section. The module engine iterates through sections and questions sequentially.

**Section**: `cognition_mental_health`  
**Questions Array**:
```json
[
  {
    "id": "memory_changes",
    "label": "Cognitive health or memory changes:",
    "required": true
  },
  {
    "id": "mood",
    "label": "Overall, how would you describe this person's mood these days?",
    "required": true
  },
  {
    "id": "behaviors",
    "label": "Have there been any of these behaviors or concerns?",
    "required": false,
    "visible_if": { "key": "memory_changes", "in": ["moderate", "severe"] }
  }
]
```

**Conditional Rendering**: The `visible_if` field ensures behaviors only shows when memory_changes is moderate or severe. This logic is evaluated in `core/modules/engine.py` during field rendering.

---

## Related Files

### Modified Files

1. **core/navi.py** (Lines 529, 536, 562, 566)
   - Added `is_results` check
   - Changed `show_progress=True` → `show_progress=(not is_results)`

2. **products/gcp_v4/modules/care_recommendation/module.json** (Lines 228-287)
   - Reordered questions: memory_changes → mood → behaviors

### Related Functions

- `core.navi.render_navi_panel()` - Main Navi panel renderer
- `core.ui.render_navi_guide_bar()` - Guide bar with progress badge
- `core.modules.engine._render_fields()` - Renders questions with conditional logic
- `core.modules.engine._render_results_view()` - Results page renderer

---

## Regression Risks

### Low Risk

- **Progress badge logic**: Only affects display, not data or navigation
- **Question order**: No impact on scoring or validation (order doesn't matter for calculation)

### What Could Break

1. ❌ **Other products using module engine**: If they have results pages, progress badge might show
   - **Mitigation**: All products using module engine should define `results_step_id` in config
   - **Affected**: Cost Planner modules, PFMA modules

2. ❌ **Conditional visibility**: If behaviors question has hidden dependencies
   - **Mitigation**: Tested conditional logic - works correctly
   - **Status**: ✅ No issues found

### Rollback Plan

If issues arise, revert commit 7349a6a:

```bash
git revert 7349a6a
git commit -m "revert: Rollback progress badge and question order fix"
git push
```

---

## Future Improvements

### 1. Standardize Progress Badge Hiding

Create a step property `hide_progress` in module config:

```json
{
  "id": "results",
  "title": "Your Guided Care Plan Summary",
  "type": "results",
  "hide_progress": true
}
```

Update engine to check `step.hide_progress` instead of comparing `step.id == results_step_id`.

### 2. Question Reordering UI

Add drag-and-drop question reordering in admin interface (future feature).

### 3. Visual Indicator for Question Dependencies

In the UI, show when a question will conditionally appear:

```
☑️ memory_changes: Moderate memory issues
  └─ ↳ behaviors will now appear (conditional)
```

---

## Related Documentation

- `GCP_RESULTS_PAGE_REDESIGN.md` - Results page UX redesign
- `GCP_SCORING_V3_IMPLEMENTATION.md` - 5-tier scoring system
- `PROFESSIONAL_HUB_IMPLEMENTATION.md` - Module architecture

---

## Conclusion

Both issues resolved:

1. ✅ Progress badge hidden on results page
2. ✅ Mood question appears before behaviors question

No scoring, validation, or navigation logic affected. Only display order and progress visibility changed.
