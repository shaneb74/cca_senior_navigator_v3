# Cost Multiplier Flag Matching Fix

## Problem
Cost multipliers weren't showing up in the Cost Planner because the flag names in the FLAG_REGISTRY (from GCP) didn't match the flag names that the Cost Calculator was looking for.

**GCP Flags** (in FLAG_REGISTRY):
- `severe_cognitive_risk`
- `high_mobility_dependence`
- `high_dependence`
- `falls_multiple`
- `chronic_present`
- etc.

**Cost Calculator Expected Flags**:
- `memory_support` (+20%)
- `mobility_limited` (+15%)
- `adl_support_high` (+10%)
- `medication_management` (+8%)
- `behavioral_concerns` (+12%)
- `falls_risk` (+8%)
- `chronic_conditions` (+10%)
- `safety_concerns` (+10%)

## Root Cause
Two separate flag naming conventions:
1. **GCP flags** describe the clinical assessment (e.g., "severe_cognitive_risk")
2. **Cost flags** describe the cost driver (e.g., "memory_support")

The Cost Calculator was checking for cost flag names, but GCP was only setting clinical flag names.

## Solution

### 1. Added Cost Flags to FLAG_REGISTRY (`core/flags.py`)
Added all cost multiplier flags to the central FLAG_REGISTRY so they're recognized as valid flags:

```python
# COST PLANNER FLAGS (for cost multipliers)
"memory_support": {
    "category": "cognitive",
    "severity": "high",
    "description": "Severe memory issues requiring specialized memory care (+20% cost)",
},
"mobility_limited": {
    "category": "mobility",
    "severity": "high",
    "description": "Wheelchair or bedbound requiring lift equipment (+15% cost)",
},
# ... etc
```

### 2. Created Flag Mapping (`products/cost_planner_v2/utils/cost_calculator.py`)
Added `FLAG_MAPPINGS` dict to translate GCP flags to cost flags:

```python
FLAG_MAPPINGS = {
    # Cognitive/Memory flags
    "severe_cognitive_risk": "memory_support",
    "moderate_cognitive_decline": "memory_support",
    
    # Mobility flags
    "high_mobility_dependence": "mobility_limited",
    
    # ADL/Dependence flags
    "high_dependence": "adl_support_high",
    "moderate_dependence": "adl_support_high",
    
    # Behavioral flags
    "mental_health_concern": "behavioral_concerns",
    "high_risk": "behavioral_concerns",
    "moderate_risk": "behavioral_concerns",
    
    # Fall/Safety flags
    "falls_multiple": "falls_risk",
    "high_safety_concern": "falls_risk",
    "moderate_safety_concern": "safety_concerns",
    
    # Chronic conditions
    "chronic_present": "chronic_conditions",
}
```

### 3. Added Normalization Function
Created `_normalize_flags()` to convert GCP flags to cost flags:

```python
def _normalize_flags(gcp_flags: List[str]) -> List[str]:
    """Normalize GCP flags to cost planner flag names."""
    normalized = set()
    
    for flag in gcp_flags:
        # Direct match (cost planner flags)
        if flag in COST_ADJUSTMENTS:
            normalized.add(flag)
        # Mapped GCP flag
        elif flag in FLAG_MAPPINGS:
            normalized.add(FLAG_MAPPINGS[flag])
    
    return list(normalized)
```

### 4. Added Medication Complexity Detection
Since GCP doesn't set a specific medication flag, we check the `meds_complexity` answer directly:

```python
# Check for medication complexity from GCP state
if gcp_rec:
    gcp_state = st.session_state.get('gcp_care_recommendation', {})
    meds_complexity = gcp_state.get('meds_complexity')
    if meds_complexity in ['moderate', 'complex']:
        if 'medication_management' not in flags:
            flags.append('medication_management')
```

### 5. Updated Calculate Function
Modified `calculate_quick_estimate_with_breakdown()` to use normalization:

```python
# Extract flag IDs from flag objects
raw_flags = [f.get('id') if isinstance(f, dict) else f for f in gcp_rec.flags]
# Normalize GCP flags to cost planner flags
flags = _normalize_flags(raw_flags)
```

## Cost Multiplier Table
All add-ons are cumulative (applied to running total):

| Flag/Condition | Add-On | Rationale |
|----------------|--------|-----------|
| **Mobility/Transfer Issues** | 15% | `mobility_limited`, `falls_risk` - Need lift equipment, extra staff |
| **Severe Cognitive Decline** | 20% | `memory_support`, `behavioral_concerns` - Specialized memory care, behavior management |
| **High ADL Support** | 10% | `adl_support_high` - Extensive help with daily activities |
| **Complex Medication** | 8% | `medication_management` - Professional med oversight required |
| **Chronic Conditions** | 12% | `chronic_conditions` - Medical coordination, monitoring |
| **Safety Concerns** | 10% | `safety_concerns` - Enhanced supervision, environmental modifications |
| **High-Acuity Memory Care** | 25% | `memory_care_high_acuity` tier - Always applied for this tier |

## Testing
To test the fix:

1. **Complete GCP** with various flags:
   - Falls: "Multiple falls" → should trigger `falls_risk` (+8%)
   - Mobility: "Wheelchair" → should trigger `mobility_limited` (+15%)
   - Memory: "Often forgets" → should trigger `memory_support` (+20%)
   - Medications: "Complex" → should trigger `medication_management` (+8%)
   - Chronic conditions: Select multiple → should trigger `chronic_conditions` (+10%)

2. **Go to Cost Planner** intro page
3. **Calculate quick estimate**
4. **Verify line items show**:
   - Base cost
   - Regional adjustment
   - **All applicable condition add-ons** (these were missing before)
   - Adjusted total

## Files Changed
- ✅ `core/flags.py` - Added cost multiplier flags to FLAG_REGISTRY
- ✅ `products/cost_planner_v2/utils/cost_calculator.py` - Added flag mapping and normalization
- ✅ `products/cost_planner_v2/intro.py` - Already had display logic for multipliers

## Result
Cost multipliers now correctly appear in the Cost Planner breakdown when user has completed GCP with relevant flags! 🎉
