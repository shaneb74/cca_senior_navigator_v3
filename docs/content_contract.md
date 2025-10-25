# Content Contract System

The Content Contract System provides a centralized pipeline for processing JSON content with token interpolation, validation, and optional overrides. This replaces scattered string replacement code throughout the application.

## Key Principles

- **JSON is the source of truth** for all user-facing copy
- **No runtime mutation** of JSON files
- **All personalization happens at render-time** through token interpolation
- **Immutable view-models** for UI consumption
- **Support for editor-friendly overrides** without code changes

## Token Specification (v1)

Allowed tokens in copy strings (titles, subtitles, bullets, labels, paragraphs):

| Token | Description | Example |
|-------|-------------|---------|
| `{NAME}` | First name of care recipient; fallback "you" | "About Mary" |
| `{NAME_POS}` | Possessive form; fallback "your" | "Mary's care plan" |
| `{ZIP}` | 5-digit ZIP if present; else "your area" | "Providers in 90210" |
| `{TIER}` | Recommended tier label if present | "Assisted Living recommended" |
| `{HOURS}` | Integer hours if present | "40 hours per week" |
| `{STATE}` | Two-letter state if present | "California (CA)" |
| `{RELATION}` | "you" if self, else "your loved one" | "your loved one" |

### Rules

- **Do not introduce new tokens** without updating this spec
- **Unknown tokens** log a warning and are left untouched
- **Header names** are truncated at 20 characters (body text keeps full names)

## Basic Usage

```python
from core.content_contract import resolve_content, build_token_context

# Load your JSON content
spec = load_json("module.json")
overrides = load_json_if_exists("module.overrides.json")  # Optional
ctx = build_token_context(st.session_state)

# Resolve with interpolation
resolved = resolve_content(spec, overrides, ctx)

# Use in UI
st.title(resolved["copy"]["title"])  # Tokens already interpolated
```

## Module Integration

For modules, use the convenience function:

```python
from core.content_contract import resolve_module_content

# Resolves module.json + optional module.overrides.json
resolved = resolve_module_content("products/gcp_v4/modules/care_recommendation/")

# Extract interpolated content
title = resolved["module"]["display"]["title"]
subtitle = resolved["module"]["display"]["subtitle"]
```

## Override System

Create a `module.overrides.json` file alongside your `module.json` to override specific strings without touching the base file:

**module.json** (base):
```json
{
  "module": {
    "display": {
      "title": "Care Assessment for {NAME}",
      "subtitle": "We'll match {NAME} to the best care options."
    }
  }
}
```

**module.overrides.json** (local edits):
```json
{
  "module": {
    "display": {
      "subtitle": "Let's find the perfect care setting for {NAME}."
    }
  }
}
```

**Result** (resolved):
```json
{
  "module": {
    "display": {
      "title": "Care Assessment for Mary",
      "subtitle": "Let's find the perfect care setting for Mary."
    }
  }
}
```

## Editor Guidelines

### Safe Edits

✅ **You can safely edit**:
- Any string in JSON files
- Add tokens like `{NAME}`, `{NAME_POS}` anywhere in copy
- Create `module.overrides.json` files for local testing
- Use Markdown in longer text blocks

### Do Not

❌ **Do not**:
- Invent new tokens (ask engineering to add them to the spec)
- Edit the base JSON files in production without review
- Assume tokens work in non-copy fields (like IDs or configuration)

### Examples

**Good token usage**:
```json
{
  "copy": {
    "title": "About {NAME}",
    "subtitle": "Tell us about {NAME_POS} current situation.",
    "description": "This helps us match {NAME} to the right care level.",
    "bullets": [
      "Daily activities {NAME} needs help with",
      "Health conditions affecting {NAME_POS} independence",
      "Safety concerns in {NAME_POS} current living situation"
    ]
  }
}
```

**Complex example with fallbacks**:
```json
{
  "copy": {
    "welcome": "Welcome to care planning for {RELATION}",
    "location_note": "We'll find options in {ZIP} and throughout {STATE}",
    "recommendation": "Based on the assessment, {TIER} is recommended for {NAME}"
  }
}
```

When tokens are missing, they fall back gracefully:
- `{NAME}` → "you"
- `{NAME_POS}` → "your" 
- `{RELATION}` → "you" or "your loved one"
- `{ZIP}` → "your area"
- etc.

## Technical Details

### Token Context Building

The system builds token context from:
1. **Session state**: `person_a_name`, `relationship_type`, etc.
2. **User snapshot**: Backup source for location/demographic data
3. **Care state**: GCP recommendations, cost planner data

### Validation

Basic validation checks:
- `copy` sections contain strings or lists of strings
- `view` sections contain rendering hints
- Unknown top-level keys generate warnings only

### Immutability

The system **never mutates** input JSON:
- `interpolate()` returns new objects
- `resolve_content()` creates deep copies
- Original JSON files remain unchanged

### Performance

- Lightweight validation (warnings, not errors)
- Efficient string replacement
- Optional override loading
- Minimal object copying

## Migration Guide

### Before (scattered replacements)
```python
# In various files
title = step.title.replace("{NAME}", person_name or "you")
subtitle = config.get("subtitle", "").replace("{NAME}", person_name or "you")
label = question["label"].replace("{NAME_POS}", f"{person_name}'s" if person_name else "your")
```

### After (centralized pipeline)
```python
# In module config
from core.content_contract import resolve_module_content

resolved = resolve_module_content(module_dir)
title = resolved["sections"][0]["title"]  # Already interpolated
subtitle = resolved["module"]["display"]["subtitle"]  # Already interpolated
label = resolved["sections"][0]["questions"][0]["label"]  # Already interpolated
```

## Testing

Run the test suite to verify functionality:
```bash
python -m pytest tests/test_content_contract.py -v
```

Key test scenarios:
- Token interpolation with real names
- Fallback behavior with missing data
- Immutability (no mutation of input objects)
- Possessive edge cases ("James" → "James's")
- Override merging
- Unknown token warnings