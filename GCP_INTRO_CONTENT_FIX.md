# GCP Intro Content Rendering Fix

## Issue
The GCP intro screen was displaying the title "Welcome to the Guided Care Plan" but not rendering the content array from the module JSON configuration.

## Root Cause
The module engine architecture had three gaps:

1. **Schema Gap**: The `StepDef` dataclass in `core/modules/schema.py` didn't have a `content` field to store content arrays from info-type sections.

2. **Config Converter Gap**: The `_convert_section_to_step()` function in `products/gcp_v4/modules/care_recommendation/config.py` wasn't passing the `content` array when converting info sections to `StepDef` objects.

3. **Rendering Gap**: The module engine in `core/modules/engine.py` wasn't rendering content arrays for info-type pages.

## Solution
Following the existing architecture patterns, I made three targeted fixes:

### 1. Extended StepDef Schema
**File**: `core/modules/schema.py`

Added `content` field to support info-type pages:

```python
@dataclass
class StepDef:
    id: str
    title: str
    subtitle: Optional[str] = None
    icon: Optional[str] = None
    fields: List[FieldDef] = field(default_factory=list)
    content: Optional[List[str]] = None  # NEW: Content array for info-type pages
    next_label: str = "Continue"
    skip_label: Optional[str] = None
    show_progress: bool = True
    show_bottom_bar: bool = True
    summary_keys: Optional[List[str]] = None
    navi_guidance: Optional[Dict[str, str]] = None
```

### 2. Updated Config Converter
**File**: `products/gcp_v4/modules/care_recommendation/config.py`

Modified `_convert_section_to_step()` to pass content array:

```python
# Handle info sections (intro pages)
if section_type == "info":
    return StepDef(
        id=section_id,
        title=title,
        subtitle=description,
        icon=None,
        fields=[],  # No fields for info pages
        content=section.get("content"),  # Pass content array for rendering
        next_label="Start" if section_id == "intro" else "Continue",
        skip_label=None,
        show_progress=False,
        show_bottom_bar=True,
        summary_keys=None,
        navi_guidance=navi_guidance,
    )
```

### 3. Added Content Rendering
**File**: `core/modules/engine.py`

Added `_render_content()` helper function:

```python
def _render_content(content: list[str]) -> None:
    """Render content array for info-type pages.
    
    Args:
        content: List of content lines with markdown support.
                 Empty strings create spacing.
    """
    for line in content:
        if line.strip():
            # Render non-empty lines with markdown
            st.markdown(line)
        else:
            # Empty lines add spacing
            st.markdown("<br/>", unsafe_allow_html=True)
```

Integrated into `run_module()` flow:

```python
# Render header with actual progress
_render_header(step_index, total_steps, title, step.subtitle, progress, progress_total, show_step_dots, step.id == config.steps[0].id)

# Render content array (for info-type pages)
if step.content:
    _render_content(step.content)

new_values = _render_fields(step, state)
```

## Implementation Details

### Markdown Support
The renderer uses `st.markdown()` which supports:
- **Bold text**: `**text**`
- **Bullet points**: `• item` or `- item`
- **Inline formatting**: All standard markdown syntax

### Spacing
Empty strings in the content array create visual spacing using `<br/>` tags:
```json
"content": [
  "First paragraph",
  "",  // Creates spacing
  "Second paragraph"
]
```

### Rendering Order
1. Header (title + subtitle)
2. Content array (if present)
3. Form fields (if present)
4. Action buttons

## JSON Structure
The GCP intro section in `products/gcp_v4/modules/care_recommendation/module.json`:

```json
{
  "id": "intro",
  "title": "Welcome to the Guided Care Plan",
  "type": "info",
  "content": [
    "This personalized assessment will help us recommend the best senior care option...",
    "",
    "**What to expect:**",
    "• 15-20 questions about daily living, health, and support needs",
    "• Questions cover mobility, medications, memory, and care requirements",
    "• A personalized care recommendation at the end",
    "• Unlock detailed cost estimates after completion",
    "",
    "**What we'll ask about:**",
    "• **About You** – Age, living situation, and location",
    "• **Medication & Mobility** – Health needs, fall history, and chronic conditions",
    "• **Cognition & Mental Health** – Memory, mood, and behavioral concerns",
    "• **Daily Living** – Activities of daily living (ADLs) and current support",
    "",
    "**Your honest answers help us determine whether Independent Living, In-Home Care, Assisted Living, or Memory Care is the best fit.**",
    "",
    "You can pause anytime and return later – your progress will be saved automatically."
  ],
  "actions": [
    { "label": "Get Started", "action": "next" },
    { "label": "Back to Concierge Hub", "action": "route", "value": "hub_concierge" }
  ]
}
```

## Testing
1. Navigate to Concierge Hub
2. Click "Find the Right Senior Care" tile
3. Verify intro screen shows:
   - Title: "Welcome to the Guided Care Plan"
   - Full content with markdown formatting (17 lines)
   - Proper spacing between sections
   - Bold text for section headers
   - Bullet points for lists
   - "Get Started" and "Back to Concierge Hub" buttons

## Architecture Compliance
This fix follows existing patterns:
- ✅ Uses existing `st.markdown()` rendering pattern
- ✅ Extends schema without breaking changes
- ✅ Preserves module engine flow
- ✅ No overrides or architectural rewrites
- ✅ Supports all future info-type sections

## Future Extensions
This fix enables content rendering for any info-type section:
- Intro pages
- Instructional pages
- Information screens
- Help pages

Simply add a `content` array to any section with `"type": "info"` in the module JSON.
