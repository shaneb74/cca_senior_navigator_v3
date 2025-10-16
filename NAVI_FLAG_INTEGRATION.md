# Navi AI Advisor - Flag Integration

**Branch:** `navi-redesign-2`  
**Status:** ✅ Complete  
**Commit:** `0b8e0bb`

## Overview

The AI Advisor now dynamically suggests questions based on flags set by the Guided Care Plan and Cost Planner. This creates a **context-aware FAQ experience** that responds to the user's journey through the platform.

## How It Works

### 1. Registry Flags
All questions are tagged with `registry_flags` from the central `FLAG_REGISTRY` in `core/flags.py`:

```python
"fall_risk": {
    "question": "How do I prevent falls at home?",
    "registry_flags": [
        "falls_multiple",
        "falls_risk", 
        "moderate_safety_concern",
        "high_safety_concern"
    ],
    ...
}
```

### 2. Dynamic Suggestion Engine
The `_get_suggested_questions()` function filters questions based on active flags:

**Priority Logic:**
1. **Flag-matched questions** (highest priority) - Questions where user has ≥1 active registry flag
2. **Always-available questions** (medium priority) - Questions with empty `registry_flags` array
3. **Unmatched questions** (lowest priority) - Questions whose flags aren't active

**Display Logic:**
- Top 3 flag-matched questions always shown first
- 3-6 total questions displayed as chips
- Questions prioritized by number of matching flags
- Excludes recently asked questions

### 3. Flag Sources
Flags are aggregated from:
- **Guided Care Plan (GCP)** - ADL, cognitive, safety, mobility flags
- **Cost Planner** - Financial, caregiver, geographic flags
- **PFMA** (if applicable) - Additional financial flags

Retrieved via `flags.get_all_flags()` which reads from MCIP.

## Question Flag Mapping

### Always Available (Empty Flags)
- **Getting Started** - Basic onboarding
- **Medicare Coverage** - General benefits info
- **Next Steps** - General planning guidance
- **Costs & Funding** - General cost/affordability questions
- **Medicaid Coverage** - General Medicaid info

### Cognitive Flags
**Questions:** Memory Care Options  
**Triggers:** `mild_cognitive_decline`, `moderate_cognitive_decline`, `severe_cognitive_risk`, `memory_support`

### Safety Flags
**Questions:** Fall Prevention  
**Triggers:** `falls_multiple`, `falls_risk`, `moderate_safety_concern`, `high_safety_concern`

### Health Flags
**Questions:** Medication Management  
**Triggers:** `medication_management`, `chronic_present`, `chronic_conditions`

### ADL/Dependence Flags
**Questions:** VA Benefits, Family Conversations  
**Triggers:** `veteran_aanda_risk`, `moderate_dependence`, `high_dependence`, `adl_support_high`

### Caregiver Support Flags
**Questions:** Family Conversations  
**Triggers:** `no_support`, `limited_support`

## User Experience Flow

### Scenario 1: User Completes GCP with Fall Risk
1. User completes Guided Care Plan
2. GCP sets flags: `falls_multiple`, `moderate_safety_concern`
3. User visits AI Advisor
4. **"How do I prevent falls at home?"** appears as top suggestion
5. User clicks, sees detailed fall prevention guidance

### Scenario 2: User Completes GCP with Memory Issues
1. User completes Guided Care Plan  
2. GCP sets flags: `moderate_cognitive_decline`, `memory_support`
3. User visits AI Advisor
4. **"What's the difference between memory care and assisted living?"** appears as top suggestion
5. User sees memory care guidance immediately

### Scenario 3: User Completes VA Module in Cost Planner
1. User completes VA Benefits module
2. Cost Planner sets flags: `veteran_aanda_risk`, `high_dependence`
3. User visits AI Advisor
4. **"Am I eligible for VA Aid & Attendance benefits?"** appears as top suggestion
5. User gets VA eligibility details

## Technical Details

### Flag Registry Reference
All flags defined in `core/flags.py`:
```python
FLAG_REGISTRY = {
    "falls_multiple": {
        "category": "safety",
        "severity": "high",
        "description": "Multiple falls in recent period"
    },
    ...
}
```

### Question Database Structure
```python
QUESTION_DATABASE = {
    "question_key": {
        "question": "Display text",
        "topic": "Category tag",
        "keywords": ["matching", "terms"],
        "registry_flags": ["flag1", "flag2"],  # <-- NEW
        "response": "Markdown response..."
    }
}
```

### Suggestion Algorithm
```python
def _get_suggested_questions(exclude=None):
    # 1. Get active flags from user journey
    active_flags = flags.get_all_flags()
    
    # 2. Categorize questions
    flag_matched = []      # Has matching flags
    always_available = []  # Empty registry_flags
    flag_unmatched = []    # Has flags but none match
    
    # 3. Build priority pool
    priority_pool = flag_matched + always_available
    
    # 4. Shuffle and return 3-6 questions
    return [top flag matches] + [shuffled rest]
```

## Testing Strategy

### Manual Testing
1. **Test Base Questions:**
   - Visit AI Advisor before completing GCP
   - Should see "Getting Started", "Medicare", "Next Steps"

2. **Test Fall Risk Flow:**
   - Complete GCP with multiple falls reported
   - Should see "How do I prevent falls at home?" at top

3. **Test Memory Care Flow:**
   - Complete GCP with cognitive concerns
   - Should see "What's the difference between memory care and assisted living?"

4. **Test VA Benefits Flow:**
   - Complete VA Benefits module in Cost Planner
   - Should see "Am I eligible for VA Aid & Attendance benefits?"

5. **Test Question Rotation:**
   - Ask several questions
   - Should see new suggestions (exclude recently asked)

### Flag Validation
Run flag validation to ensure all registry_flags are defined:
```bash
python -m core.flags validate
```

## Benefits

### For Users
- **Personalized Experience** - Relevant questions surface automatically
- **Guided Discovery** - Learn about resources as they become relevant
- **Reduced Overwhelm** - Don't see irrelevant questions until needed

### For Platform
- **Higher Engagement** - Context-aware suggestions increase clicks
- **Better Conversion** - Users discover relevant products naturally
- **Educational Flow** - Users learn as they progress through journey

## Future Enhancements

### Phase 1 (Current)
- ✅ Tag all questions with registry flags
- ✅ Filter suggestions by active flags
- ✅ Prioritize flag-matched questions

### Phase 2 (Potential)
- Add question scoring based on flag severity
- Track which flags lead to which questions (analytics)
- A/B test suggestion order strategies

### Phase 3 (Potential)
- Add timestamp-based relevance (recent flags = higher priority)
- Multi-flag requirement logic ("show if flags A AND B")
- Progressive disclosure (hide advanced questions until basics answered)

## Related Files

- **`pages/ai_advisor.py`** - Main AI Advisor implementation
- **`core/flags.py`** - FLAG_REGISTRY and flag aggregation
- **`config/nav.json`** - Navigation config (FAQs route)
- **`pages/_stubs.py`** - Page routing stubs
- **`NAVI_AI_ADVISOR_REDESIGN.md`** - Full redesign documentation

## Commit History

1. **db6555a** - Initial AI Advisor redesign (12 questions, clean layout)
2. **4030819** - Reverse chronological display (newest first)
3. **8dd5bb8** - Navi's distinctive banner with left border
4. **0b8e0bb** - Dynamic flag integration ✨ **(current)**

---

**Questions?** Check FLAG_REGISTRY in `core/flags.py` for all available flags.
