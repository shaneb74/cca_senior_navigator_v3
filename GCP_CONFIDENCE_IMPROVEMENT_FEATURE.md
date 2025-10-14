# GCP Confidence Improvement Feature

## Overview
Added an interactive confidence improvement component to the GCP results page that educates users about their confidence score and provides actionable steps to improve it.

## User Problem Solved
**Before**: Users saw a confidence score (e.g., 85%) but didn't know:
- Why it wasn't 100%
- What factors affected it
- How to improve it

**After**: Users see a clear breakdown showing:
- Exactly what's affecting their confidence
- Specific actions they can take
- A button to go back and improve their answers

## Feature Design

### When It Appears
- **Only shows when confidence < 100%**
- Appears on the results page, right after the care recommendation
- Does not show for perfect 100% confidence scores

### Visual Layout

```
---
### 💡 Improve Your Recommendation Confidence

┌──────────────────────┐  ┌──────────────────────┐
│ QUESTION COMPLETENESS │  │ RECOMMENDATION CLARITY│
│      85%              │  │       67%             │
│ 17 of 20 answered     │  │ 17.0 points in AL    │
└──────────────────────┘  └──────────────────────┘

**How to improve:**

┌─────────────────────────────────────────────────┐
│ 📝 Answer 3 missed questions                    │
│ Complete all required questions to increase      │
│ confidence by up to 30%.                         │
│ [High Impact]                                    │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ 🎯 Your score is near a tier boundary           │
│ Answering more questions accurately could        │
│ strengthen your Assisted Living recommendation   │
│ or reveal if another tier is a better fit.      │
│ [Medium Impact]                                  │
└─────────────────────────────────────────────────┘

        [📝 Review & Improve]
```

### Confidence Breakdown Cards

#### Card 1: Question Completeness (60% weight)
Shows:
- Percentage of required questions answered
- Count (e.g., "17 of 20 answered")
- Color-coded:
  - Green (≥90%): `#22c55e`
  - Amber (70-89%): `#f59e0b`
  - Red (<70%): `#ef4444`

#### Card 2: Recommendation Clarity (40% weight)
Shows:
- How clear-cut the recommendation is
- User's score and tier
- Color-coded same as completeness
- Based on distance from tier boundaries

### Improvement Suggestions

#### Suggestion 1: Missed Questions (High Impact)
**Shown when**: User hasn't answered all required questions

**Message**:
```
📝 Answer X missed question(s)
Complete all required questions to increase confidence by up to 30%.
[High Impact]
```

**Impact**: Up to 30% confidence increase (60% weight × 50% gap = 30% max)

#### Suggestion 2: Boundary Clarity (Medium Impact)
**Shown when**: User's score is near a tier boundary (< 3 points away)

**Message**:
```
🎯 Your score is near a tier boundary
Answering more questions accurately could strengthen your [Tier] 
recommendation or reveal if another tier is a better fit.
[Medium Impact]
```

**Impact**: Up to 20% confidence increase (40% weight × 50% gap = 20% max)

### Action Button

**"📝 Review & Improve" Button**
- Primary button style (prominent)
- Centered on page
- Only shown if there are unanswered questions
- Action: Returns user to first question page to review/complete answers

## Technical Implementation

### Function: `_render_confidence_improvement()`
**Location**: `core/modules/engine.py` (lines 694-873)

**Parameters**:
- `outcomes`: Dict with confidence, tier_score, tier from GCP logic
- `config`: ModuleConfig with steps and fields
- `state`: Module state with user answers

**Logic Flow**:
1. Check if confidence < 100% (exit early if 100%)
2. Calculate completeness (answered/total required questions)
3. Calculate boundary clarity (distance from tier boundaries)
4. Render two breakdown cards (completeness + clarity)
5. Build actionable suggestions based on gaps
6. Show "Review & Improve" button if unanswered questions exist

### Integration Point
**File**: `core/modules/engine.py`
**Function**: `_render_results_view()`
**Line**: 907 (after summary points, before CTAs)

```python
# Render confidence improvement guidance
_render_confidence_improvement(outcomes, config, mod)
```

### Button Behavior
```python
if st.button("📝 Review & Improve", ...):
    # Reset to first question step (skip intro)
    question_steps = [i for i, s in enumerate(config.steps) if s.fields]
    if question_steps:
        st.session_state[f"{config.state_key}._step"] = question_steps[0]
        st.rerun()
```

## Confidence Calculation Recap

### Formula
```python
completeness = answered_questions / total_required_questions  # 0-1
boundary_confidence = min(distance_from_boundary / 3.0, 1.0)  # 0-1

confidence = (completeness * 0.6) + (boundary_confidence * 0.4)
confidence = max(0.5, confidence)  # Minimum 50%
```

### Tier Boundaries
```python
TIER_THRESHOLDS = {
    "independent": (0, 8),         # 0-8 points
    "in_home": (9, 16),            # 9-16 points
    "assisted_living": (17, 24),   # 17-24 points
    "memory_care": (25, 100),      # 25+ points
}
```

### Boundary Distance Calculation
```python
distance_from_min = user_score - tier_min
distance_from_max = tier_max - user_score
distance_from_boundary = min(distance_from_min, distance_from_max)

# 3+ points from boundary = full boundary confidence
boundary_clarity_pct = min(int((distance_from_boundary / 3.0) * 100), 100)
```

## Example Scenarios

### Scenario 1: High Completeness, Low Clarity
**Data**:
- Answered: 20/20 questions (100% completeness)
- Score: 17.0 (Assisted Living, right at boundary)
- Distance from boundary: 0 points

**Calculation**:
- Completeness contribution: 1.0 × 0.6 = 0.6
- Boundary contribution: 0.0 × 0.4 = 0.0
- Total confidence: 0.6 = **60%**

**UI Shows**:
- Completeness card: **100%** (green) ✅
- Clarity card: **0%** (red) ❌
- Suggestion: "🎯 Your score is near a tier boundary..."
- Button: Hidden (all questions answered, can't improve score without changing answers)

### Scenario 2: Low Completeness, High Clarity
**Data**:
- Answered: 14/20 questions (70% completeness)
- Score: 21.0 (Assisted Living, 4 from lower, 3 from upper)
- Distance from boundary: 3 points

**Calculation**:
- Completeness contribution: 0.7 × 0.6 = 0.42
- Boundary contribution: 1.0 × 0.4 = 0.4
- Total confidence: 0.82 = **82%**

**UI Shows**:
- Completeness card: **70%** (amber) ⚠️
- Clarity card: **100%** (green) ✅
- Suggestion: "📝 Answer 6 missed questions"
- Button: "📝 Review & Improve" (shown)

### Scenario 3: Perfect Score
**Data**:
- Answered: 20/20 questions (100% completeness)
- Score: 21.0 (Assisted Living, 3+ from both boundaries)
- Distance from boundary: 3 points

**Calculation**:
- Completeness contribution: 1.0 × 0.6 = 0.6
- Boundary contribution: 1.0 × 0.4 = 0.4
- Total confidence: 1.0 = **100%**

**UI Shows**:
- Nothing! Component doesn't render for 100% confidence ✅

## User Experience Flow

### Initial Results View
1. User completes GCP questionnaire (skips some optional questions)
2. Sees recommendation: "Based on your answers, we recommend Assisted Living."
3. Scrolls down and sees confidence breakdown
4. Reads: "You answered 17 of 20 questions (85% completeness)"
5. Sees actionable suggestion: "Answer 3 missed questions"
6. Clicks "📝 Review & Improve"

### Review & Improve Flow
7. Returns to first question page
8. All previous answers are preserved (pre-filled)
9. User scrolls through questions, finds the 3 unanswered ones
10. Completes the missing questions
11. Clicks "Continue" through to results page
12. Sees updated recommendation (may have changed!)
13. New confidence score: 95% or higher
14. Confidence improvement component now shows better metrics or disappears

## Design Decisions

### Why Not Show at 100%?
- No action to take—would just be informational noise
- Users with 100% confidence don't need reassurance
- Keeps results page clean and focused on the recommendation

### Why Two Separate Cards?
- Educates users that confidence comes from **two factors**
- Allows users to see exactly which factor is affecting them
- Color-coding makes it immediately scannable

### Why "Review & Improve" Not "Complete Missing Questions"?
- Less accusatory tone
- Emphasizes improvement, not failure
- Suggests they can review all answers, not just missing ones
- Encourages thoughtful responses, not just filling blanks

### Why Reset to First Question Page?
- Allows users to review all answers in context
- Easier to find unanswered questions by going through flow
- Avoids complexity of jumping directly to missing questions
- Maintains consistent navigation pattern

## Accessibility

### Color Coding
- Green/Amber/Red scheme also has different intensities
- Percentage numbers are large and prominent
- Works without relying solely on color

### Text Contrast
- All text meets WCAG AA standards
- Labels use medium gray (#64748b) on white
- Percentages use semantic colors with good contrast

### Button Accessibility
- Prominent primary button style
- Clear action label with emoji
- Keyboard accessible
- Visible focus state

## Mobile Responsive

### Card Layout
- Two cards side-by-side on desktop (st.columns([1,1]))
- Stacks vertically on mobile (<640px)
- Cards maintain consistent height

### Suggestion Cards
- Full-width on all screen sizes
- Flex layout wraps on mobile
- Icon stays aligned at top

### Button
- Centered with 2:1:2 column ratio
- Full-width on mobile
- Maintains touch-friendly size (44px min)

## Analytics Opportunities

### Events to Track
1. **Confidence Improvement Shown**: When component renders
   - Metadata: confidence_score, completeness_pct, clarity_pct
   
2. **Review Button Clicked**: When user clicks "Review & Improve"
   - Metadata: missed_questions_count, tier, score
   
3. **Confidence Improved**: When user returns to results with higher confidence
   - Metadata: before_confidence, after_confidence, questions_added

### Success Metrics
- **Engagement Rate**: % of <100% confidence users who click "Review & Improve"
- **Completion Rate**: % who complete missing questions after clicking
- **Confidence Delta**: Average confidence increase after improvement
- **Recommendation Changes**: % of users whose tier changes after improvement

## Future Enhancements

### Phase 2 Ideas
1. **Question-Level Guidance**
   - Show which specific questions were skipped
   - Link directly to those questions
   - Explain why each question matters

2. **Tier Proximity Visualization**
   - Show user's score on a visual scale
   - Indicate boundaries with markers
   - "You're 3 points from Memory Care"

3. **Confidence History**
   - Track confidence over multiple attempts
   - Show improvement progress
   - "You improved from 70% to 95%!"

4. **Smart Suggestions**
   - Prioritize high-impact questions
   - "Answer these 2 questions to reach 90% confidence"
   - Show expected confidence increase per question

5. **Educational Tooltips**
   - "What is boundary clarity?"
   - Hover to learn more about factors
   - Link to help article

## Testing

### Manual Testing Checklist
- [ ] Complete GCP with all questions → No improvement component shows
- [ ] Complete GCP with 3 missing questions → Component shows, completeness < 100%
- [ ] Get score right at boundary (e.g., 17) → Component shows, clarity < 100%
- [ ] Click "Review & Improve" → Returns to first question page
- [ ] Previous answers are preserved (pre-filled)
- [ ] Complete missing questions → Confidence increases on results
- [ ] Mobile view: Cards stack vertically
- [ ] Mobile view: Button is full-width
- [ ] Color coding works (green/amber/red)
- [ ] Button is keyboard accessible

### Edge Cases
1. **All questions answered, low clarity**: Component shows but no button (can't improve by adding questions)
2. **No required questions**: Component doesn't break (total_count = 0 check)
3. **Confidence = 50% (minimum)**: Component shows with both factors low
4. **Tier at extreme (memory_care 25-100)**: Boundary calculation handles large range

## Related Documentation
- `GCP_CONFIDENCE_DISPLAY_FIX.md` - Confidence display consistency fix
- `core/modules/engine.py` - Module engine implementation
- `products/gcp_v4/modules/care_recommendation/logic.py` - Confidence calculation logic

## Commit Message
```
feat: Add confidence improvement guidance to GCP results page

- Added _render_confidence_improvement() function to module engine
- Shows two-factor confidence breakdown (completeness + clarity)
- Displays actionable suggestions with impact levels
- "Review & Improve" button returns user to questions
- Only renders when confidence < 100%
- Color-coded cards (green/amber/red) for quick scanning
- Mobile responsive layout
- Educates users on how to improve their recommendation

User benefit: Understand confidence score and take action to improve it
Impact: Increases engagement, improves data quality, builds trust
```
