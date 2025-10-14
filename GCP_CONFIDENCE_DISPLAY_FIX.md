# GCP Confidence Display Bug Fix

## Issue
The Concierge Hub was showing two different confidence levels for the same care recommendation:
- **Navi V2 Panel**: "Care Plan: assisted_living (100% confidence)"
- **GCP Tile Badge**: "ASSISTED LIVING (21% CONFIDENCE)"

## Root Cause

### Data Structure
The GCP `CareRecommendation` contract has two different fields:
1. **`tier_score`**: Raw scoring calculation (0-100 scale)
   - Example: 21.0 (meaning 21 points out of 100)
   - Set in `logic.py` line 82: `"tier_score": round(total_score, 1)`
   
2. **`confidence`**: Normalized confidence metric (0-1 decimal scale)
   - Example: 1.0 (meaning 100% confidence)
   - Set in `logic.py` line 84: `"confidence": round(confidence, 2)`

### Bug Location
**File**: `core/mcip.py` line 380-381

**Buggy Code**:
```python
confidence_pct = int(rec.tier_score) if rec.tier_score else int(rec.confidence * 100)
```

### Problem
This code incorrectly used `tier_score` (raw score) instead of `confidence` (confidence metric) for the display percentage:

- `rec.tier_score` = 21.0 (already a percentage-like score) → int(21) = **21%** ❌
- `rec.confidence` = 1.0 (decimal 0-1) → int(1.0 * 100) = **100%** ✅

### Why It Worked Elsewhere
The Navi V2 panel (in `core/navi.py` lines 418-423) correctly uses `rec.confidence`:
```python
confidence = int(ctx.care_recommendation.confidence * 100)
context_chips.append({
    'icon': '🧭',
    'label': 'Care',
    'value': tier,
    'sublabel': f'{confidence}%'
})
```

## Solution

### Fix Applied
Changed `core/mcip.py` line 381 to always use `confidence` field:

**Before**:
```python
confidence_pct = int(rec.tier_score) if rec.tier_score else int(rec.confidence * 100)
```

**After**:
```python
# Use confidence (0-1 decimal) not tier_score (raw score 0-100)
confidence_pct = int(rec.confidence * 100)
```

### Rationale
1. **`confidence`** is the user-facing metric designed for display (0-100%)
2. **`tier_score`** is an internal scoring calculation (raw points)
3. All other display locations use `confidence`, not `tier_score`
4. The GCP results page shows confidence, not tier_score

## Impact

### Before Fix
- Navi Panel: 100% confidence ✅
- GCP Tile: 21% confidence ❌
- **Result**: Confusing, contradictory information

### After Fix
- Navi Panel: 100% confidence ✅
- GCP Tile: 100% confidence ✅
- **Result**: Consistent, accurate confidence display

## Testing

### Verification Steps
1. Complete GCP questionnaire
2. Return to Concierge Hub
3. Check Navi V2 panel context chip: Should show "Care: [tier] · [confidence]%"
4. Check GCP tile badge: Should show "[TIER] ([confidence]% CONFIDENCE)"
5. Verify both show **same confidence value**

### Expected Values
For a high-confidence recommendation:
- Both displays: "85-100% confidence"

For a medium-confidence recommendation:
- Both displays: "50-84% confidence"

For a low-confidence recommendation:
- Both displays: "0-49% confidence"

## Related Code

### Confidence Calculation
**File**: `products/gcp_v4/modules/care_recommendation/logic.py`

The confidence is calculated based on flag presence and tier clarity (lines 60-65):
```python
# Calculate confidence (0-1 scale)
top_tier = tier_rankings[0]
confidence = _calculate_confidence(
    top_tier["tier"],
    top_tier["score"],
    tier_rankings,
    flags
)
```

### Display Locations
1. **Navi V2 Panel**: `core/navi.py` line 418
   - Uses: `int(ctx.care_recommendation.confidence * 100)`
   
2. **GCP Tile**: `core/mcip.py` line 381 (FIXED)
   - Now uses: `int(rec.confidence * 100)`
   
3. **GCP Results Page**: `products/gcp_v4/modules/care_recommendation/results.py`
   - Uses: `int(outcome.confidence * 100)`

## Future Considerations

### Data Model Clarity
Consider renaming fields for clarity:
- `tier_score` → `raw_score` or `total_points`
- `confidence` → `confidence_score` or `recommendation_confidence`

### Documentation
Add JSDoc comments to `CareRecommendation` contract:
```python
@dataclass
class CareRecommendation:
    tier: str                    # Recommended care tier
    tier_score: float            # Raw scoring calculation (0-100 points)
    confidence: float            # User-facing confidence (0-1 decimal, display as 0-100%)
    tier_rankings: List[dict]    # Ordered list of all tier scores
    flags: List[str]             # Risk/alert flags
    # ...
```

### API Consistency
Ensure all display code uses `confidence`, not `tier_score`:
```python
# ✅ CORRECT
display_pct = int(rec.confidence * 100)

# ❌ WRONG
display_pct = int(rec.tier_score)  # This is a raw score, not a percentage!
```

## Commit Message
```
fix: Use confidence field instead of tier_score for GCP tile display

- Changed core/mcip.py line 381 to use rec.confidence instead of rec.tier_score
- tier_score is raw scoring calculation (0-100 points), not confidence percentage
- confidence is normalized metric (0-1 decimal) designed for display
- Fixes discrepancy between Navi panel (100%) and tile badge (21%)
- Now both displays show consistent confidence value

Issue: Hub showed two different confidence levels for same recommendation
Root Cause: Incorrect field used for percentage display
Solution: Always use confidence field for user-facing displays
```

## Related Issues
- None currently, but this could have caused user confusion about recommendation quality
- Similar issues could exist if `tier_score` is used elsewhere for display

## Prevention
Add to code review checklist:
- [ ] Display code uses `confidence` field (0-1 decimal)
- [ ] Raw scores (`tier_score`) not used for user-facing percentages
- [ ] All confidence displays multiplied by 100 for percentage
- [ ] Consistent confidence values across all UI components
