# Flag Registry Documentation

This document describes all feature and condition flags available in the Senior Navigator system. Flags are set by assessment modules (primarily GCP) and drive personalization across the platform.

**Last Updated:** October 23, 2025  
**Source:** `core/flags.py`

---

## Overview

Flags serve multiple purposes:
- **Additional Services Personalization** - Recommend relevant services based on user needs
- **Navi Guidance** - Provide context-aware recommendations and questions
- **Cost Adjustments** - Apply cost multipliers in Cost Planner for specialized care needs
- **Resource Routing** - Direct users to appropriate learning resources and partner services

---

## Cognitive & Memory Flags

**Flags in this category:** `mild_cognitive_decline`, `moderate_cognitive_decline`, `severe_cognitive_risk`, `behavioral_concerns`, `memory_support`

### `mild_cognitive_decline`
- **Category:** Cognitive
- **Severity:** Low
- **Description:** Occasional forgetfulness or mild memory issues
- **Impact:** May trigger memory support service recommendations

### `moderate_cognitive_decline`
- **Category:** Cognitive
- **Severity:** Moderate
- **Description:** Moderate memory or thinking difficulties
- **Impact:** Influences care tier calculation; may recommend memory care assessment

### `severe_cognitive_risk`
- **Category:** Cognitive
- **Severity:** High
- **Description:** Severe memory issues, dementia, or Alzheimer's diagnosis
- **Impact:** Strong indicator for memory care tier; triggers specialized support recommendations

---

## Fall & Safety Flags

**Flags in this category:** `moderate_safety_concern`, `high_safety_concern`, `falls_multiple`, `falls_risk`, `safety_concerns`

### `moderate_safety_concern`
- **Category:** Safety
- **Severity:** Moderate
- **Description:** One fall in past year or behavioral safety concerns
- **Impact:** Recommends fall prevention services and home safety assessment

### `high_safety_concern`
- **Category:** Safety
- **Severity:** High
- **Description:** Multiple falls or significant safety risks
- **Impact:** Influences care tier; recommends urgent safety interventions

### `falls_multiple`
- **Category:** Safety
- **Severity:** High
- **Description:** Multiple falls in the past year
- **Impact:** Strong indicator for higher care tier; triggers fall prevention services

### `falls_risk`
- **Category:** Safety
- **Severity:** High
- **Description:** Multiple falls requiring enhanced safety measures
- **Cost Impact:** +8% care cost multiplier
- **Impact:** Applied in Cost Planner for enhanced safety monitoring

### `safety_concerns`
- **Category:** Safety
- **Severity:** Moderate
- **Description:** Safety monitoring needed
- **Cost Impact:** +10% care cost multiplier
- **Impact:** Applied in Cost Planner for additional supervision

---

## Mobility Flags

**Flags in this category:** `moderate_mobility`, `high_mobility_dependence`, `mobility_limited`

### `moderate_mobility`
- **Category:** Mobility
- **Severity:** Moderate
- **Description:** Uses cane or walker for mobility
- **Impact:** Recommends mobility aids and physical therapy services

### `high_mobility_dependence`
- **Category:** Mobility
- **Severity:** High
- **Description:** Wheelchair-bound or bedbound
- **Impact:** Strong indicator for higher care tier; recommends specialized mobility equipment

### `mobility_limited`
- **Category:** Mobility
- **Severity:** High
- **Description:** Wheelchair or bedbound requiring lift equipment
- **Cost Impact:** +15% care cost multiplier
- **Impact:** Applied in Cost Planner for specialized mobility support

---

## ADL (Activities of Daily Living) Flags

**Flags in this category:** `moderate_dependence`, `high_dependence`, `adl_support_high`, `veteran_aanda_risk`

### `moderate_dependence`
- **Category:** ADL
- **Severity:** Moderate
- **Description:** Needs regular assistance with daily activities
- **Impact:** Influences care hours recommendation; suggests in-home care services

### `high_dependence`
- **Category:** ADL
- **Severity:** High
- **Description:** Needs extensive full-time support with ADLs
- **Impact:** Strong indicator for higher care tier; recommends 24-hour care

### `adl_support_high`
- **Category:** ADL
- **Severity:** High
- **Description:** Extensive ADL support required
- **Cost Impact:** +10% care cost multiplier
- **Impact:** Applied in Cost Planner for additional caregiver hours

### `veteran_aanda_risk`
- **Category:** ADL
- **Severity:** Moderate
- **Description:** Veteran with Aid & Attendance benefit eligibility indicators
- **Impact:** Triggers VA benefits assessment and eligibility guidance

---

## Mental Health Flags

**Flags in this category:** `moderate_risk`, `high_risk`, `mental_health_concern`

### `moderate_risk`
- **Category:** Mental Health
- **Severity:** Moderate
- **Description:** Emotional ups and downs, occasionally feeling down
- **Impact:** Recommends mental health support services and social engagement activities

### `high_risk`
- **Category:** Mental Health
- **Severity:** High
- **Description:** Frequently feeling down or depressed
- **Impact:** Recommends urgent mental health evaluation and counseling services

### `mental_health_concern`
- **Category:** Mental Health
- **Severity:** High
- **Description:** Significant mental health concerns requiring attention
- **Impact:** Triggers mental health service recommendations and specialist referrals

---

## Health & Medical Flags

**Flags in this category:** `chronic_present`, `chronic_conditions`, `medication_management`, `diabetic_care`, `wound_care`, `oxygen_therapy`, `hospice_palliative`

### `chronic_present`
- **Category:** Health
- **Severity:** Moderate
- **Description:** One or more chronic health conditions present
- **Impact:** Recommends disease management and regular health monitoring

### `chronic_conditions`
- **Category:** Health
- **Severity:** Moderate
- **Description:** Multiple chronic conditions requiring coordinated care
- **Cost Impact:** +10% care cost multiplier
- **Impact:** Applied in Cost Planner for care coordination

### `medication_management`
- **Category:** Health
- **Severity:** Moderate
- **Description:** Complex medication regimen requiring professional management
- **Cost Impact:** +8% care cost multiplier
- **Impact:** Recommends medication management services; applied in Cost Planner

### `diabetic_care`
- **Category:** Health
- **Severity:** Moderate
- **Description:** Diabetes management and monitoring requiring specialized care
- **Cost Impact:** +5% care cost multiplier
- **Impact:** Recommends diabetes management services; applied in Cost Planner

### `wound_care`
- **Category:** Health
- **Severity:** Moderate
- **Description:** Specialized wound care requiring skilled nursing
- **Cost Impact:** +8% care cost multiplier
- **Impact:** Recommends skilled nursing services; applied in Cost Planner

### `oxygen_therapy`
- **Category:** Health
- **Severity:** Moderate
- **Description:** Supplemental oxygen therapy requiring equipment and monitoring
- **Cost Impact:** +5% care cost multiplier
- **Impact:** Recommends respiratory therapy services; applied in Cost Planner

### `hospice_palliative`
- **Category:** Health
- **Severity:** High
- **Description:** End-of-life or comfort-focused palliative care
- **Cost Impact:** +15% care cost multiplier
- **Impact:** Triggers hospice care recommendations and end-of-life planning resources

---

## Behavioral Flags

**Flags in this category:** `behavioral_concerns`

### `behavioral_concerns`
- **Category:** Cognitive
- **Severity:** High
- **Description:** Behavioral issues requiring specialized management (wandering, aggression, etc.)
- **Cost Impact:** +12% care cost multiplier
- **Impact:** Influences memory care tier decision; applied in Cost Planner for specialized behavioral support

---

## Caregiver & Support System Flags

**Flags in this category:** `has_partner`, `no_support`, `limited_support`

### `has_partner`
- **Category:** Caregiver
- **Severity:** Low
- **Description:** Lives with spouse or partner (potential support system)
- **Impact:** May reduce recommended care hours; considered in cost calculations

### `no_support`
- **Category:** Caregiver
- **Severity:** High
- **Description:** No regular caregiver support available
- **Impact:** Increases recommended care hours; influences care tier

### `limited_support`
- **Category:** Caregiver
- **Severity:** Moderate
- **Description:** Limited caregiver support (1-3 hours/day)
- **Impact:** Influences care hours recommendation and respite care suggestions

---

## Geographic Flags

**Flags in this category:** `low_access`, `very_low_access`, `geo_isolated`

### `low_access`
- **Category:** Geographic
- **Severity:** Low
- **Description:** Somewhat isolated location with limited service access
- **Impact:** Recommends telehealth options and mobile services

### `very_low_access`
- **Category:** Geographic
- **Severity:** Moderate
- **Description:** Very isolated location with minimal service access
- **Impact:** Prioritizes in-home care options and telehealth services

### `geo_isolated`
- **Category:** Geographic
- **Severity:** High
- **Description:** Geographic isolation requiring special accommodation
- **Impact:** Recommends relocation assessment or specialized rural care services

---

## Preference Flags

**Flags in this category:** `is_move_flexible`

### `is_move_flexible`
- **Category:** Preferences
- **Severity:** Low
- **Description:** Willing to move to facility care (move_preference >= 3 on 1-5 scale)
- **Impact:** Enables Move Preferences module; recommends assisted living/memory care facilities

---

## Cost Model Flags

These flags are applied as **multiplicative cost adjustments** in the Cost Planner, after base cost and ZIP code adjustments. They are applied in the following order:

1. `memory_support` (+20%)
2. `mobility_limited` (+15%)
3. `behavioral_concerns` (+12%)
4. `adl_support_high` (+10%)
5. `chronic_conditions` (+10%)
6. `safety_concerns` (+10%)
7. `medication_management` (+8%)
8. `falls_risk` (+8%)

Additional health-specific multipliers (not in primary chain):
- `diabetic_care` (+5%)
- `wound_care` (+8%)
- `oxygen_therapy` (+5%)
- `hospice_palliative` (+15%)

---

## Flag Usage in Code

### Getting Flag Information
```python
from core.flags import get_flag_info

info = get_flag_info("falls_multiple")
# Returns: {
#   "category": "safety",
#   "severity": "high",
#   "description": "Multiple falls in the past year"
# }
```

### Checking if a Flag is Set
```python
from core.flags import get_flag, has_any_flags, has_all_flags

# Check single flag
if get_flag("high_dependence"):
    # Recommend 24-hour care

# Check if any flag is set
if has_any_flags(["falls_multiple", "high_safety_concern"]):
    # Trigger fall prevention services

# Check if all flags are set
if has_all_flags(["severe_cognitive_risk", "behavioral_concerns"]):
    # Recommend specialized memory care
```

### Getting Flags by Category or Severity
```python
from core.flags import get_flags_by_category, get_flags_by_severity

# Get all cognitive flags
cognitive_flags = get_flags_by_category("cognitive")

# Get all high-severity flags
high_severity_flags = get_flags_by_severity("high")
```

### Validating Flags
```python
from core.flags import validate_flags

flags = ["falls_multiple", "invalid_flag", "high_dependence"]
invalid = validate_flags(flags, module_name="GCP v4")
# Prints warning for "invalid_flag"
# Returns: ["invalid_flag"]
```

---

## Categories

- **cognitive** - Memory, thinking, and cognitive function
- **safety** - Falls, wandering, and safety risks
- **mobility** - Physical movement and transportation
- **adl** - Activities of daily living (bathing, dressing, eating, etc.)
- **mental_health** - Depression, anxiety, emotional well-being
- **health** - Chronic conditions, medical needs, treatments
- **caregiver** - Support system and caregiver availability
- **geographic** - Location and service accessibility
- **preferences** - User preferences and flexibility

## Severity Levels

- **low** - Minimal impact on care needs
- **moderate** - Noticeable impact requiring attention
- **high** - Significant impact requiring specialized care

---

## Adding New Flags

To add a new flag to the system:

1. **Register in `core/flags.py`:**
   ```python
   "new_flag_name": {
       "category": "cognitive|safety|mobility|adl|mental_health|health|caregiver|geographic|preferences",
       "severity": "low|moderate|high",
       "description": "Clear description of what this flag indicates",
       "cost_multiplier": 1.10,  # Optional: if flag affects cost
   }
   ```

2. **Set flag in module** (e.g., `module.json`):
   ```json
   {
     "question_id": "example_question",
     "options": [
       {
         "value": "option_value",
         "flags": ["new_flag_name"]
       }
     ]
   }
   ```

3. **Use flag in product logic:**
   ```python
   if get_flag("new_flag_name"):
       # Apply custom logic
   ```

4. **Update documentation** (this file) with flag details

---

## Notes

- Flags are aggregated from all products (GCP, Cost Planner, PFMA) via `get_all_flags()`
- Cost multipliers are applied in Cost Planner's regional cost calculations
- Flags drive Additional Services recommendations in the navigation system
- All flags must be registered in `FLAG_REGISTRY` before use
- Invalid flags trigger console warnings but do not break execution
