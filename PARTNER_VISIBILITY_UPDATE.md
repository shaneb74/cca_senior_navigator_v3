# Partner Visibility System Update

## Overview
Updated the partner visibility system to support flag-based rendering. Partners can now be hidden by default (`visible: false`) and only appear when specific GCP flags are triggered.

## Changes Made

### 1. `config/partners.json` - Visibility Flags
**What Changed:**
Added `"visible": false` to 4 partners:
- ✅ **hpone** (HealthPlanOne) - `visible: false`
- ✅ **omcare** (Omcare) - `visible: false`
- ✅ **seniorlife_ai** (SeniorLife.AI) - `visible: false`
- ✅ **ncoa** (National Council on Aging) - `visible: false`

**Still Visible by Default:**
- ✅ **lantern** (Lantern) - Always visible (no `visible` field = default true)
- ✅ **home_instead** (Home Instead) - Always visible (no `visible` field = default true)

**Logic:**
```json
{
  "id": "omcare",
  "visible": false,  // Hidden by default
  "unlock_requires": [
    "gcp:complete",
    "flag:moderate_dependence|high_dependence|..."  // Only show if flags match
  ]
}
```

### 2. `core/additional_services.py` - Dynamic Visibility Logic
**What Changed:**

#### A. Removed Hardcoded Partner Filter
**Before:**
```python
# Only load Omcare and SeniorLife.AI dynamically (for now)
if partner_id not in ["omcare", "seniorlife_ai"]:
    continue
```

**After:**
```python
# Load ALL partners from partners.json
# (no filter - visibility controlled by visible flag + unlock_requires)
```

#### B. Added Visibility Check
**New Logic:**
```python
is_visible_by_default = partner.get("visible", True)

if not is_visible_by_default:
    # Hidden by default - only show if unlock requirements met
    if not _partner_unlocked(partner, ctx):
        continue
else:
    # Visible by default - still check unlock requirements
    if not _partner_unlocked(partner, ctx):
        continue
```

#### C. Dynamic Personalization
**New Logic:**
```python
if not is_visible_by_default:
    partner_tile["personalization"] = "personalized"  # Flag-triggered (blue gradient)
else:
    partner_tile["personalization"] = "navi"  # Always visible (green gradient)
```

#### D. Updated REGISTRY Skip List
**Before:**
```python
if tile.get("key") in ["omcare", "seniorlife_ai"]:
    continue
```

**After:**
```python
partner_keys = ["hpone", "omcare", "seniorlife_ai", "lantern", "ncoa", "home_instead"]
if tile.get("key") in partner_keys:
    continue
```

## Behavior Summary

### Hidden Partners (visible: false)
These partners **ONLY** appear when their `unlock_requires` conditions are met:

#### **hpone** (HealthPlanOne)
- **Unlock:** `gcp:>=50` (GCP at least 50% complete)
- **Triggers:** User reaches halfway through GCP
- **Styling:** Blue gradient + "🤖 Navi Recommended"

#### **omcare** (Omcare)
- **Unlock:** `gcp:complete` AND medication-related flags
- **Flags:** `moderate_dependence|high_dependence|chronic_present|geo_isolated|moderate_cognitive_decline|severe_cognitive_risk|no_support|high_mobility_dependence|mild_cognitive_decline|moderate_mobility|limited_support`
- **Triggers:** User completes GCP + has medication management needs
- **Styling:** Blue gradient + "🤖 Navi Recommended"

#### **seniorlife_ai** (SeniorLife.AI)
- **Unlock:** `gcp:complete` AND mobility/safety flags
- **Flags:** `falls_multiple|moderate_safety_concern|high_safety_concern|mild_cognitive_decline|moderate_cognitive_decline|severe_cognitive_risk|mental_health_concern`
- **Triggers:** User completes GCP + has fall risk or cognitive concerns
- **Styling:** Blue gradient + "🤖 Navi Recommended"

#### **ncoa** (National Council on Aging)
- **Unlock:** None specified (but hidden by default)
- **Note:** May need to add unlock_requires if this should appear conditionally
- **Current Status:** Will never appear (no unlock logic)

### Visible Partners (no visible field = true)
These partners **ALWAYS** appear in Additional Services:

#### **lantern** (Lantern)
- **Unlock:** `gcp:>=50` (still applies for progressive disclosure)
- **Display:** Always in Additional Services once GCP 50%+ complete
- **Styling:** Green gradient + "✨ Curated by Navi" (if we add this variant)

#### **home_instead** (Home Instead)
- **Unlock:** None (always unlocked)
- **Display:** Always in Additional Services
- **Styling:** Standard tile (no special gradient/label)

## Visual Styling Matrix

| Partner | Visible | Unlock | Gradient | Label |
|---------|---------|--------|----------|-------|
| **hpone** | ❌ false | GCP 50% | 🔵 Blue | 🤖 Navi Recommended |
| **omcare** | ❌ false | GCP complete + flags | 🔵 Blue | 🤖 Navi Recommended |
| **seniorlife_ai** | ❌ false | GCP complete + flags | 🔵 Blue | 🤖 Navi Recommended |
| **ncoa** | ❌ false | None (never shows) | N/A | N/A |
| **lantern** | ✅ true | GCP 50% | 🟢 Green | ✨ Curated by Navi |
| **home_instead** | ✅ true | None | None | None |

## User Experience Flow

### Scenario 1: User with Medication Needs
1. **Start:** Additional Services shows Lantern + Home Instead
2. **GCP 50%:** hpone appears (blue gradient)
3. **GCP 100% + meds flags:** omcare appears (blue gradient)
4. **Result:** 4 partners visible (2 blue, 1 green, 1 standard)

### Scenario 2: User with Fall Risk
1. **Start:** Additional Services shows Lantern + Home Instead
2. **GCP 50%:** hpone appears (blue gradient)
3. **GCP 100% + fall flags:** seniorlife_ai appears (blue gradient)
4. **Result:** 4 partners visible (2 blue, 1 green, 1 standard)

### Scenario 3: User with No Special Needs
1. **Start:** Additional Services shows Lantern + Home Instead
2. **GCP 50%:** hpone appears (blue gradient)
3. **GCP 100%:** No new partners (didn't trigger omcare/seniorlife flags)
4. **Result:** 3 partners visible (1 blue, 1 green, 1 standard)

## Configuration Guidelines

### To Make a Partner Hidden (Flag-Triggered):
```json
{
  "id": "partner_name",
  "visible": false,
  "unlock_requires": [
    "gcp:complete",
    "flag:your_flag_name|another_flag"
  ]
}
```

### To Make a Partner Always Visible:
```json
{
  "id": "partner_name",
  // NO visible field (defaults to true)
  "unlock_requires": [
    "gcp:>=50"  // Optional progressive disclosure
  ]
}
```

### To Make a Partner Completely Open:
```json
{
  "id": "partner_name"
  // NO visible field
  // NO unlock_requires
}
```

## Testing Checklist

### Basic Visibility
- [ ] **Before GCP:** Only Lantern + Home Instead visible
- [ ] **GCP 50%:** hpone appears (if visible logic works)
- [ ] **GCP 100% + no flags:** No additional partners beyond hpone
- [ ] **GCP 100% + meds flags:** omcare appears
- [ ] **GCP 100% + fall flags:** seniorlife_ai appears

### Styling
- [ ] **Flag-triggered partners:** Blue gradient + "🤖 Navi Recommended"
- [ ] **Always visible partners:** Standard or green gradient
- [ ] **Home Instead:** No special styling (baseline)

### Edge Cases
- [ ] NCOA never appears (no unlock logic)
- [ ] Multiple flag-triggered partners can appear simultaneously
- [ ] Partners collapse when GCP progress decreases (if that's possible)

## Future Enhancements

### Phase 2: Green Gradient for Always-Visible
Add "navi" personalization styling:
```python
if not is_visible_by_default:
    partner_tile["personalization"] = "personalized"  # Blue
else:
    partner_tile["personalization"] = "navi"  # Green (NEW!)
```

```css
/* Add to hubs.css */
.service-tile-navi {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.navi-label {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  content: "✨ Curated by Navi";
}
```

### Phase 3: NCOA Conditional Logic
Add unlock requirements to NCOA:
```json
{
  "id": "ncoa",
  "visible": false,
  "unlock_requires": [
    "gcp:complete",
    "flag:financial_concern|medicaid_eligible"  // Add relevant flags
  ]
}
```

### Phase 4: Regional Filtering
Add state-based visibility:
```python
user_state = ctx.get("state")
partner_states = partner.get("states", [])
if "US" not in partner_states and user_state not in partner_states:
    continue
```

## Code Locations

### Key Files Modified
- `config/partners.json` - Added `visible: false` to 4 partners
- `core/additional_services.py` - Lines 673-710 (visibility logic)
- `core/additional_services.py` - Lines 712-720 (REGISTRY skip list)

### Related Files (No Changes)
- `core/base_hub.py` - Already supports personalization variants
- `assets/css/hubs.css` - Already has `.service-tile-personalized` styling
- `core/partner_connection.py` - Generic renderer works regardless of visibility

## Status
✅ **COMPLETE** - All partners configured with visibility flags
🟡 **TESTING NEEDED** - Verify flag-based rendering works end-to-end
⏳ **FUTURE** - Add green gradient for always-visible partners

## Summary
- **4 partners hidden by default** (hpone, omcare, seniorlife_ai, ncoa)
- **2 partners always visible** (lantern, home_instead)
- **Flag-triggered partners** get blue gradient + "Navi Recommended" label
- **Always-visible partners** use standard styling (green gradient pending)
- **NCOA** currently never appears (needs unlock logic)
