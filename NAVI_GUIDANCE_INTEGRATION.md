# Navi Module Guidance Integration

**Date:** January 2025  
**Status:** ✅ Complete  
**Commit:** a342d78  
**Branch:** feature/cost_planner_v2

## Overview

Enabled Navi to dynamically inject contextual messages from `module.json` guidance rules. Navi now reads the `navi_guidance` blocks in each section and adapts its messaging to provide context-aware assistance throughout the GCP questionnaire.

## Problem

Navi was using generic messages ("Let's work through this together") instead of the rich contextual guidance defined in `module.json`. The guidance rules existed but weren't being extracted or displayed.

## Solution

### 1. Extract Guidance from module.json

**File:** `products/gcp_v4/modules/care_recommendation/config.py`

Updated `_convert_section_to_step()` to extract `navi_guidance` from each section and pass it to `StepDef`:

```python
def _convert_section_to_step(section: Dict[str, Any]) -> StepDef:
    # ...
    navi_guidance = section.get("navi_guidance")  # Extract from JSON
    
    return StepDef(
        id=section_id,
        title=title,
        # ...
        navi_guidance=navi_guidance,  # Pass to StepDef
    )
```

This ensures all guidance data flows from `module.json` → `StepDef` → Navi renderer.

### 2. Intelligent Message Display

**File:** `core/navi.py`

Enhanced `render_navi_panel()` to intelligently build messages from guidance fields with priority order:

#### Main Text Priority
1. **section_purpose** - What this section assesses (e.g., "Understand demographics and living context")
2. **encouragement** - Motivational text (e.g., "These basic details help us tailor our recommendation")
3. Fallback to section title

#### Subtext Priority
1. **why_this_matters** - Educational context (e.g., "Age and living situation help us understand support networks")
2. **what_happens_next** - Preview of upcoming steps
3. **time_estimate** - Time remaining (for intro/info pages)
4. **context_note** - Additional details (e.g., "ADLs = bathing, dressing, eating, toileting")

#### Additional Features
- **Encouragement banners**: If `section_purpose` is used as main text, show `encouragement` as `st.info()` banner
- **Support messages**: Display `support_message` for sensitive topics (mental health, cognitive decline)
- **Red flag warnings**: Show `red_flags` in expandable warning box for clinicians

## module.json Guidance Structure

### Section-Level Guidance
```json
{
  "id": "about_you",
  "title": "About You",
  "navi_guidance": {
    "section_purpose": "Understand demographics and living context",
    "why_this_matters": "Age and living situation help us understand support networks",
    "red_flags": ["Living alone + very isolated", "Living alone + 85+"],
    "encouragement": "These basic details help us tailor our recommendation"
  }
}
```

### Question-Level Guidance (Future Enhancement)
```json
{
  "id": "age_range",
  "label": "What is this person's age range?",
  "navi_guidance": {
    "why_asked": "Age influences care needs and options",
    "tip": "Higher age groups often need more support"
  }
}
```

## Examples of Navi Messages

### Example 1: "About You" Section
**Main Message:** 🤖 Navi: Understand demographics and living context  
**Subtext:** 💡 Age and living situation help us understand support networks and care accessibility  
**Progress:** Step 2/6

**Info Banner:** 💬 These basic details help us tailor our recommendation

### Example 2: "Cognition & Mental Health" Section
**Main Message:** 🤖 Navi: Evaluate cognitive function and mental health status  
**Subtext:** 💡 Memory issues and mood changes determine if specialized care (like Memory Care) is needed  
**Progress:** Step 4/6

**Info Banner:** 💙 Remember: Cognitive decline is common and there are specialized care options designed to help

**Expandable Warning:**
> ⚠️ **Important Considerations**
> Watch for these combinations:
> - Severe memory + wandering
> - Severe memory + aggression
> - Low mood + isolation

### Example 3: "Daily Living" Section
**Main Message:** 🤖 Navi: Determine level of assistance needed for daily activities (ADLs and IADLs)  
**Subtext:** 💡 The amount of help needed with daily tasks is the primary driver of care recommendations  
**Progress:** Step 5/6

**Context Note:** ADLs = bathing, dressing, eating, toileting. IADLs = cooking, finances, transportation

## Benefits

### For Users
✅ **Contextual Help** - Understand why each question matters  
✅ **Educational** - Learn about care assessment process  
✅ **Reassuring** - Supportive messages for sensitive topics  
✅ **Progress Clarity** - See how far along they are

### For Product Team
✅ **Centralized Content** - All guidance in module.json, not hardcoded  
✅ **Easy Updates** - Change messaging without touching Python code  
✅ **Consistent UX** - Same guidance system across all modules  
✅ **Testable** - Can validate JSON guidance independently

### For Clinicians/Caregivers
✅ **Red Flag Awareness** - Highlight dangerous combinations  
✅ **Context Understanding** - Know what each section assesses  
✅ **Professional Guidance** - Clinically relevant warnings

## Technical Details

### Data Flow
```
module.json
    ↓
config.py (_convert_section_to_step)
    ↓
StepDef.navi_guidance: Dict[str, str]
    ↓
ModuleConfig.steps[i]
    ↓
render_navi_panel(module_config)
    ↓
Navi extracts guidance and renders
    ↓
User sees contextual message
```

### Guidance Fields Supported

| Field | Type | Usage | Priority |
|-------|------|-------|----------|
| `section_purpose` | str | What this section does | Main text (P1) |
| `why_this_matters` | str | Educational context | Subtext (P1) |
| `encouragement` | str | Motivational text | Main text (P2) or info banner |
| `what_happens_next` | str | Preview next steps | Subtext (P2) |
| `time_estimate` | str | Time remaining | Subtext (P3) |
| `context_note` | str | Additional details | Subtext (P4) |
| `support_message` | str | Sensitive topic support | Info banner |
| `red_flags` | list[str] | Warning combinations | Expandable warning |
| `icon` | str | Custom emoji | Panel icon |
| `color` | str | Custom color | Panel background |

### Fallback Behavior

If guidance is missing or incomplete:
1. Use section title as main text
2. Use generic "I'm here to help you through each step" as subtext
3. Default icon: 🧭
4. Default color: #0066cc (CCA blue)

## Future Enhancements

### Question-Level Tooltips
Add tooltip guidance for individual questions:
```python
# In field renderer
if field.guidance:
    st.markdown(f"💡 **Why we ask:** {field.guidance['why_asked']}")
    if field.guidance.get('tip'):
        st.caption(field.guidance['tip'])
```

### Dynamic Encouragement
Show different encouragement based on progress:
```json
"encouragement_by_progress": {
  "0-33": "Great start! Keep going.",
  "34-66": "You're halfway there!",
  "67-100": "Almost done! Just a few more questions."
}
```

### Flag-Based Warnings
Trigger specific warnings when users select risky combinations:
```json
"conditional_warnings": [
  {
    "if": {"age_range": "85_plus", "living_situation": "alone"},
    "show": "⚠️ Living alone at 85+ may require extra safety considerations"
  }
]
```

## Testing

### Manual Test Steps
1. Start GCP (Guided Care Plan)
2. Watch Navi panel on each section
3. Verify messages change per section:
   - **Intro:** "Welcome and set expectations"
   - **About You:** "Understand demographics and living context"
   - **Medication & Mobility:** "Assess physical health, medication needs, and fall risks"
   - **Cognition & Mental Health:** "Evaluate cognitive function and mental health status"
   - **Daily Living:** "Determine level of assistance needed for daily activities"
   - **Results:** "Present personalized care recommendation with confidence score"

4. Check for encouragement banners
5. Check for support messages on sensitive sections
6. Check for red flag warnings (expand to see)

### Validation
```bash
# Validate JSON structure
python3 -m json.tool products/gcp_v4/modules/care_recommendation/module.json

# Verify guidance extraction
python3 -c "
from products.gcp_v4.modules.care_recommendation.config import get_config
config = get_config()
for step in config.steps:
    print(f'{step.id}: {step.navi_guidance}')
"
```

## Related Files
- `core/navi.py` - Navi rendering logic
- `core/modules/schema.py` - StepDef with navi_guidance field
- `products/gcp_v4/modules/care_recommendation/config.py` - Config loader
- `products/gcp_v4/modules/care_recommendation/module.json` - Guidance content
- `config/navi_dialogue.json` - Hub-level dialogue system (separate)

## Documentation
- `GCP_FLAG_MAPPING.md` - Flag-to-guidance mapping
- `.github/copilot-instructions.md` - Project architecture

---

## Summary

**Feature:** Navi now reads and displays contextual guidance from module.json  
**Impact:** Users get context-aware help that adapts to each section  
**Content:** All guidance centralized in JSON, not hardcoded  
**Extensibility:** Easy to add guidance to new sections or update existing  
**Status:** Ready for testing in GCP, can be extended to other modules
