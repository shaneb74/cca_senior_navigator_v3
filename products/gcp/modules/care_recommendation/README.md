# Care Recommendation Module

## Overview

The Care Recommendation module is the core assessment component of the Guided Care Plan (GCP) product. It evaluates a senior's care needs across multiple domains and provides personalized recommendations for the most appropriate care setting.

## Features

- **Multi-domain Assessment**: Evaluates cognitive health, mobility, daily living needs, medication complexity, and support networks
- **Weighted Scoring System**: Uses configurable weights and caps for each input domain
- **Decision Tree Logic**: Applies sophisticated conditional logic to determine care tier
- **Dynamic Modifiers**: Adjusts recommendations based on contextual factors
- **Warning Flags**: Identifies high-priority concerns requiring immediate attention
- **Confidence Scoring**: Provides transparency about recommendation reliability

## Care Tiers

The module can recommend the following care levels:

0. **Independent / In-Home**: Minimal to no care needs; can live independently
1. **In-Home Care**: Regular assistance needed but can remain at home
2. **Assisted Living**: Moderate care needs requiring supportive environment
3. **Memory Care**: Cognitive impairment requiring specialized care
4. **High-Acuity Memory Care / Skilled Nursing**: Complex medical and cognitive needs

## Module Structure

```
care_recommendation/
├── __init__.py
├── logic.py           # Core scoring and recommendation logic
├── module.json        # Configuration: questions, scoring, decision tree
└── README.md          # This file
```

## Configuration (`module.json`)

### Sections

The assessment is divided into 4 sections:

1. **About You**: Demographics and living situation
2. **Medication & Mobility**: Medication complexity, mobility level, fall risk, chronic conditions
3. **Daily Living**: ADL/IADL needs, assistance hours, support network
4. **Cognition & Mental Health**: Memory changes, behaviors, mood

### Scoring Logic

Each input is scored based on:

```json
{
  "id": "mobility",
  "domain": "Mobility & Falls",
  "weight": 2,
  "score_cap": null
}
```

- **weight**: Multiplier for the raw score (higher = more impact)
- **score_cap**: Maximum score allowed (prevents over-weighting)
- **domain**: Category for score breakdown tracking

### Decision Tree

The decision tree evaluates conditions in order and returns the first match:

```json
{
  "if": {
    "all": [
      {"eq": ["memory_changes", "severe"]},
      {"eq": ["primary_support", "none"]}
    ]
  },
  "recommendation": "High-Acuity Memory Care",
  "tier": 4
}
```

### Modifiers

Modifiers adjust the tier after initial determination:

```json
{
  "if": {
    "all": [
      {"eq": ["hours_per_day", "24h"]},
      {"neq": ["memory_changes", "severe"]}
    ]
  },
  "action": "decrease_tier",
  "value": 1
}
```

### Flags

Flags identify specific concerns:

```json
"falls_multiple": {
  "if": {"eq": ["falls", "multiple"]},
  "priority": "high",
  "message": "Multiple falls indicate significant fall risk"
}
```

## Logic Implementation (`logic.py`)

### Main Function

```python
derive(manifest: dict, answers: dict, context: dict) -> dict
```

**Returns:**
```python
{
    "tier": str,              # e.g., "Memory Care"
    "score": float,           # Weighted total score
    "points": List[str],      # Summary bullet points
    "confidence": float,      # 0-1 confidence score
    "confidence_label": str,  # "High confidence"
    "flags": dict,            # Active warning flags
    "metadata": dict          # Score breakdown, debugging info
}
```

### Key Functions

- `_score_from_options()`: Scores single-select answers
- `_score_multi()`: Scores multi-select answers with optional cap
- `_eval()`: Evaluates conditional logic expressions
- `_generate_summary_points()`: Creates actionable summary bullets
- `_confidence_label()`: Converts confidence score to label

## Usage

### From Product

```python
from products.gcp.modules.care_recommendation.logic import derive
from core.modules.base import load_module_manifest

manifest = load_module_manifest("gcp", "care_recommendation")
answers = {
    "memory_changes": "moderate",
    "mobility": "walker",
    "help_overall": "some_help",
    # ... other answers
}

result = derive(manifest, answers, {"debug": False})

print(f"Recommendation: {result['tier']}")
print(f"Score: {result['score']}")
print(f"Confidence: {result['confidence_label']}")
for point in result['points']:
    print(f"  • {point}")
```

### Debug Mode

Enable debug output for development:

```python
result = derive(manifest, answers, {"debug": True})
```

This prints:
```
=== CARE RECOMMENDATION DEBUG ===
Total score: 18.5 (tier 2)
Recommendation: Assisted Living
Confidence: 87.5%
Flags: ['fall_recent', 'cog_moderate']
Modifiers: ['Tier increased by 1']
=================================
```

## Testing

Run tests with:

```bash
# All tests
pytest tests/test_care_recommendation.py -v

# Specific test class
pytest tests/test_care_recommendation.py::TestDerive -v

# With coverage
pytest tests/test_care_recommendation.py --cov=products.gcp.modules.care_recommendation

# Quick smoke test
python tests/test_care_recommendation.py
```

## Validation

The module validates inputs at multiple levels:

1. **Empty answers**: Returns error state
2. **Missing critical fields**: Returns "Incomplete assessment" with details
3. **Invalid scores**: Defaults to 0 (defensive programming)
4. **Malformed data**: Try/except blocks prevent crashes

## Confidence Calculation

Confidence is calculated as:

```
confidence = (answered_questions / total_questions) × modifier
```

Where modifier is:
- 1.1 if all critical questions answered (capped at 1.0)
- 0.9 if any critical question missing

Critical questions:
- `memory_changes`
- `mobility`
- `help_overall`
- `primary_support`
- `meds_complexity`

## Extending the Module

### Adding New Questions

1. Add to appropriate section in `module.json`:
```json
{
  "id": "new_question",
  "type": "string",
  "select": "single",
  "label": "Your question?",
  "required": true,
  "options": [
    {"label": "Option A", "value": "a", "score": 0},
    {"label": "Option B", "value": "b", "score": 1}
  ]
}
```

2. Add to scoring logic if needed:
```json
{
  "id": "new_question",
  "domain": "New Domain",
  "weight": 1.5
}
```

### Adding New Decision Rules

Add to `decision_tree` array (evaluated in order):

```json
{
  "if": {
    "all": [
      {"eq": ["new_question", "b"]},
      {"gt": ["score", 10]}
    ]
  },
  "recommendation": "Special Care",
  "tier": 3
}
```

### Adding New Flags

Add to `flags` object:

```json
"new_flag": {
  "if": {"eq": ["new_question", "concerning_value"]},
  "priority": "high",
  "message": "This requires immediate attention"
}
```

## Performance Considerations

- **Scoring**: O(n × m) where n = inputs, m = options per input (typically < 100ms)
- **Decision Tree**: O(k) where k = number of rules (evaluated sequentially)
- **Caching**: Module manifest is loaded once per product session
- **Memory**: Minimal; all data structures are dictionaries/lists

## Troubleshooting

### Issue: Recommendation seems incorrect

1. Enable debug mode: `context={"debug": True}`
2. Check score breakdown in `metadata.score_breakdown`
3. Verify matched rule in `metadata.matched_rule_index`
4. Review modifiers in `metadata.modifiers_applied`

### Issue: Low confidence score

- Check `metadata.answered_count` vs `metadata.total_questions`
- Ensure critical questions are answered
- Review answers for empty/null values

### Issue: No recommendation returned

- Check for errors in console
- Verify manifest is valid JSON
- Ensure decision tree has fallback rule

## Future Enhancements

- [ ] Machine learning scoring refinement
- [ ] Geographic/regional customization
- [ ] Cost estimation integration
- [ ] Provider matching based on tier
- [ ] Family/caregiver preference weighting
- [ ] Multi-language support
- [ ] Accessibility improvements

## Changelog

### v1.0 (Current)
- Initial release
- 4-section assessment
- 15 scored inputs across 5 domains
- 8-rule decision tree with 2 modifiers
- 13 warning flags
- Comprehensive test coverage
- Confidence scoring
- Detailed summary generation

## Support

For questions or issues:
- Review test suite: `tests/test_care_recommendation.py`
- Check module manifest: `module.json`
- Enable debug mode for diagnostics
- Contact engineering team

---

**Last Updated**: October 12, 2025  
**Module Version**: v1  
**Compatible With**: GCP Product v2025.10
