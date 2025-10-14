# GCP Flag Mapping Reference

## Overview
This document maps the flags set by the GCP v4 module (in `module.json`) to the questions and services they trigger in Navi's intelligence layer.

## Flag Sources
Flags are set when users answer questions in the GCP module (`products/gcp_v4/modules/care_recommendation/module.json`). Each answer option can set one or more flags.

## GCP Module Flags → Navi Questions

### Safety & Mobility Flags (Priority 1 - Urgent)

| GCP Flag | When Set | Navi Question Triggered |
|----------|----------|------------------------|
| `falls_multiple` | Multiple falls in past 6 months | "How can I reduce fall risk at home?" |
| `high_safety_concern` | Multiple falls | "How can I reduce fall risk at home?" |
| `moderate_mobility` | Uses cane or walker | "What mobility aids and modifications can help at home?" |
| `high_mobility_dependence` | Wheelchair/scooter or bed-bound | "What mobility aids and modifications can help at home?" |

### Cognitive Flags (Priority 1 - Urgent)

| GCP Flag | When Set | Navi Question Triggered |
|----------|----------|------------------------|
| `severe_cognitive_risk` | Severe memory issues or dementia diagnosis | "What's the difference between Memory Care and Assisted Living?" |
| `moderate_cognitive_decline` | Moderate memory/thinking issues | "What's the difference between Memory Care and Assisted Living?" |
| `mild_cognitive_decline` | Occasional forgetfulness | (No specific question, but tracked) |
| `moderate_safety_concern` | Behavioral concerns (wandering, aggression, etc.) + cognitive decline | "What specialized care is available for dementia or Alzheimer's?" |

### Veteran Flags (Priority 2 - Important Benefits)

| GCP Flag | When Set | Navi Question Triggered |
|----------|----------|------------------------|
| `veteran_aanda_risk` | User needs help with any ADLs/IADLs | "Am I eligible for VA Aid & Attendance benefits?" |

### Dependence & Care Flags (Priority 2)

| GCP Flag | When Set | Navi Question Triggered |
|----------|----------|------------------------|
| `moderate_dependence` | Needs occasional/regular help | "What level of in-home care or facility care do I need?" |
| `high_dependence` | Needs extensive/full-time support | "What level of in-home care or facility care do I need?" |

### Medical & Medication Flags

| GCP Flag | When Set | Navi Question Triggered |
|----------|----------|------------------------|
| `chronic_present` | Has any chronic conditions | "Who can help manage medications safely?" |

### Mental Health Flags

| GCP Flag | When Set | Navi Question Triggered |
|----------|----------|------------------------|
| `mental_health_concern` | Feeling down a lot | "How do I find emotional support and mental health services?" |
| `high_risk` | Low mood score | "How do I find emotional support and mental health services?" |
| `moderate_risk` | Ups and downs in mood | (Tracked but no specific question) |

### Location & Access Flags

| GCP Flag | When Set | Navi Question Triggered |
|----------|----------|------------------------|
| `geo_isolated` | Very isolated location | "What services are available in remote or rural areas?" |
| `very_low_access` | Very isolated from services | "What services are available in remote or rural areas?" |
| `low_access` | Somewhat isolated | (Tracked but no specific question) |

### Support Flags

| GCP Flag | When Set | Navi Question Triggered |
|----------|----------|------------------------|
| `no_support` | No regular support | "How do I find and hire reliable caregivers?" |
| `limited_support` | Less than 1 hour/day of support | "How do I find and hire reliable caregivers?" |

## GCP Module Flags → Additional Services

### Service Mapping

| GCP Flag | Service Recommended | Service Key |
|----------|---------------------|-------------|
| `veteran_aanda_risk` | Veterans Benefits | `veterans_benefits` |
| `falls_multiple`, `high_safety_concern` | OMCare (Fall Prevention) | `omcare` |
| `moderate_mobility`, `high_mobility_dependence` | OMCare (Mobility Aids) | `omcare` |
| `moderate_cognitive_decline`, `severe_cognitive_risk` | Memory Care Specialists | `memory_care_specialists` |
| `moderate_safety_concern` | Memory Care Specialists | `memory_care_specialists` |
| `financial_strain`, `low_runway`, `financial_gap` | Financial Planning | `financial_planning` |
| `mental_health_concern`, `high_risk` | Mental Health Services | `mental_health_services` |
| `moderate_dependence`, `high_dependence` | Home Modifications | `home_modifications` |

### Default Services
If no flags match, Navi recommends:
- SeniorLife AI (always shown)
- OMCare
- Facility Tours

## Implementation Notes

### Flag Format in MCIP
The GCP module publishes flags as a `List[Dict[str, Any]]`:
```python
flags = [
    {"falls_multiple": True},
    {"high_safety_concern": True},
    {"moderate_mobility": True}
]
```

### Flag Aggregation
`core/flags.py:get_all_flags()` merges the list of dicts into a single dict:
```python
flags = {
    "falls_multiple": True,
    "high_safety_concern": True,
    "moderate_mobility": True
}
```

### Question Generation
`core/navi.py:NaviOrchestrator.get_suggested_questions()` uses the merged flags to determine which 3 questions to show.

### Service Recommendations
`core/navi.py:NaviOrchestrator.get_additional_services()` uses the merged flags to determine which services to recommend (max 5).

## Testing

To verify flag mapping:
1. Complete GCP module with specific answers
2. Check Navi panel for relevant questions
3. Navigate to FAQ page - should see 3 question chips
4. Check Additional Services section for relevant partners

## Related Files
- GCP Module Config: `products/gcp_v4/modules/care_recommendation/module.json`
- Flag Aggregation: `core/flags.py`
- Navi Logic: `core/navi.py`
- FAQ Questions: `pages/faq.py`
- MCIP Contracts: `core/mcip.py`
