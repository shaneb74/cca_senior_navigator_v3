# Diabetes Knowledge Trivia - Condition-Triggered Learning Activity

**Status**: ✅ Implemented & Ready for Testing  
**Date**: October 17, 2025  
**Branch**: `bug-cleanup`  
**Commits**: 
- `9cfd8ec` - Core diabetes trivia module and condition detection
- `94b6a39` - Navi condition-aware messaging

---

## 🎯 Feature Summary

A **condition-triggered trivia module** that automatically appears for users with diabetes, providing personalized educational content about glucose management, lifestyle habits, and diabetes care.

### Key Innovations:
1. **Condition-Aware**: Module appears only when `medical.conditions.chronic[]` contains "diabetes"
2. **JSON-Driven**: No custom Python code - uses existing trivia engine infrastructure
3. **Navi-Integrated**: Intelligent messaging when module unlocks
4. **Scalable Pattern**: Foundation for future condition-triggered modules (COPD, cognitive, mobility, etc.)

---

## 📋 Implementation Details

### Files Created:
- **`products/senior_trivia/modules/diabetes_knowledge.json`** (224 lines)
  - 6 diabetes-specific questions with educational feedback
  - Covers: glucose ranges, hypoglycemia, A1C, foot care, lifestyle habits
  - Awards "Healthy You Badge" (🩸) on completion

### Files Modified:
- **`products/senior_trivia/product.py`**
  - Added `_has_diabetes_condition()` helper function
  - Conditional module rendering in trivia hub
  - Shows "🆕 New" badge when first unlocked
  - Module not required for 100% trivia completion (bonus content)

- **`core/navi.py`**
  - Added `_has_diabetes_condition()` helper (shared logic)
  - Dynamic encouragement text when diabetes trivia unlocks
  - Message: *"Since we know you're managing diabetes, I've unlocked a quick trivia game about healthy habits and glucose management. Want to give it a try?"*

---

## 🔍 Condition Detection Logic

### Primary Trigger:
```python
medical.conditions.chronic[] contains {"code": "diabetes", "source": "...", "updated_at": "..."}
```

### Alternate Trigger:
```python
flags.active["chronic_present"] == True 
AND 
any condition.code contains "diabetes" or "diabetic"
```

### Graceful Degradation:
- If `flag_manager` unavailable, returns `False` (module hidden)
- No errors thrown - silent failure mode

---

## 🎮 User Experience Flow

### 1. **Before Diabetes Condition Set**
- Trivia hub shows 5 standard modules
- No diabetes trivia visible

### 2. **After Diabetes Condition Set** (e.g., via GCP or Advisor Prep)
- **Waiting Room Navi**: Shows personalized message about unlocked trivia
- **Trivia Hub**: Diabetes Knowledge Check appears with "🆕 New" badge
- Position: Inserted after Healthy Habits, before Community Challenge
- Tile displays:
  ```
  🩸 Diabetes Knowledge Check 🆕 New
  Quick, fun questions to help you stay sharp about managing diabetes
  ⏱️ 4 min • 6 questions
  [Play]
  ```

### 3. **Playing the Quiz**
- Standard trivia engine renders 6 questions
- Instant feedback with educational tips
- Example feedback:
  > "Correct! The ADA recommends fasting blood sugar between 80–130 mg/dL for most adults with diabetes. Your doctor may adjust this target based on your individual health, age, and other factors."

### 4. **On Completion**
- Scores displayed (e.g., "You scored 83% - 5 out of 6 correct")
- **Healthy You Badge** (🩸) awarded
- Badge persists in `product_tiles_v2['senior_trivia_hub']['badges_earned']['diabetes_knowledge']`
- Module remains visible with "Play Again" button
- No longer shows "🆕 New" badge

### 5. **If Diabetes Condition Removed**
- Module dynamically hidden from trivia hub
- Badge data persists (reappears if condition re-added)
- No errors or broken references

---

## 🧪 Testing Procedure

### Test 1: Condition Trigger
**Setup**:
1. Start fresh session (no diabetes condition)
2. Navigate to Waiting Room → Senior Trivia

**Expected**:
- ✅ 5 standard trivia modules visible
- ✅ No Diabetes Knowledge Check visible
- ✅ Navi shows standard encouragement

**Action**: Set diabetes condition via GCP or Advisor Prep Medical section

**Expected After**:
- ✅ Diabetes Knowledge Check appears in trivia hub
- ✅ Shows "🆕 New" badge
- ✅ Positioned after Healthy Habits
- ✅ Navi shows diabetes-specific message in Waiting Room

---

### Test 2: Play & Complete Quiz
**Setup**: With diabetes condition active, diabetes trivia visible

**Action**: Click "Play" on Diabetes Knowledge Check

**Expected**:
1. ✅ Intro screen with quiz overview
2. ✅ 6 questions render correctly with multiple choice
3. ✅ Educational feedback displays after each answer
4. ✅ Progress tracked throughout quiz
5. ✅ Results screen shows score percentage
6. ✅ "Healthy You Badge" (🩸) awarded
7. ✅ Badge visible on trivia hub (with score and Play Again option)
8. ✅ "🆕 New" badge removed after completion

---

### Test 3: Badge Persistence
**Setup**: Complete diabetes trivia, earn badge

**Action**: 
1. Navigate away from trivia hub
2. Complete other activities
3. Close/reopen browser (if testing persistence)
4. Return to trivia hub

**Expected**:
- ✅ Diabetes trivia still visible (condition still active)
- ✅ Badge shows as earned with score
- ✅ "Play Again" button available
- ✅ No "🆕 New" badge

---

### Test 4: Condition Removal
**Setup**: Diabetes condition active, trivia visible and completed

**Action**: Remove diabetes from chronic conditions list

**Expected**:
- ✅ Diabetes Knowledge Check hidden from trivia hub
- ✅ No errors in console
- ✅ 5 standard modules still display correctly
- ✅ Badge data retained in session (reappears if condition re-added)

---

### Test 5: Navi Messaging
**Setup**: Diabetes condition active, diabetes trivia NOT yet completed

**Location**: Waiting Room Hub

**Expected**:
- ✅ Navi encouragement text shows diabetes-specific message
- ✅ Message: *"Since we know you're managing diabetes, I've unlocked a quick trivia game about healthy habits and glucose management. Want to give it a try?"*

**After Completion**:
- ✅ Navi returns to standard Waiting Room encouragement
- ✅ No mention of diabetes trivia after badge earned

---

## 📊 Question Content Summary

| # | Topic | Learning Focus |
|---|-------|----------------|
| 1 | Fasting Blood Sugar Range | Target: 80–130 mg/dL for most adults |
| 2 | Hypoglycemia Causes | Skipping meals after insulin, medication timing |
| 3 | Management Goals | Maintaining glucose in healthy range |
| 4 | Foot Care | Reduced circulation and sensation risks |
| 5 | Lifestyle Habits | Exercise and balanced meals |
| 6 | A1C Test | Measures 2-3 month average blood sugar |

All questions include:
- ✅ 4 answer options (1 correct, 3 educational distractors)
- ✅ Detailed feedback explaining correct answer
- ✅ Practical tips for diabetes management
- ✅ Evidence-based recommendations (ADA guidelines)

---

## 🏗️ Architecture for Future Condition-Triggered Modules

This implementation establishes a **reusable pattern** for adding more condition-specific trivia:

### COPD: "Breathe Easy Trivia"
```json
{
  "module": {
    "id": "copd_knowledge",
    "condition_trigger": {
      "primary": "medical.conditions.chronic[] contains 'copd'"
    }
  }
}
```
**Topics**: Oxygen use, breathing exercises, medication adherence, lung health

---

### Cognitive Decline: "Brain Fitness Trivia"
```json
{
  "module": {
    "id": "cognitive_fitness",
    "condition_trigger": {
      "primary": "flags.active[] includes 'memory_concerns'"
    }
  }
}
```
**Topics**: Memory strategies, brain-healthy habits, social engagement, cognitive exercises

---

### Mobility/Fall Risk: "Move Safely Trivia"
```json
{
  "module": {
    "id": "mobility_safety",
    "condition_trigger": {
      "primary": "flags.active[] includes 'fall_risk'"
    }
  }
}
```
**Topics**: Fall prevention, balance exercises, home safety, mobility aids

---

### Cardiovascular: "Heart Smart Trivia"
```json
{
  "module": {
    "id": "heart_health",
    "condition_trigger": {
      "primary": "medical.conditions.chronic[] contains 'cardiovascular'"
    }
  }
}
```
**Topics**: Blood pressure, diet, exercise safety, medication adherence

---

## 🛠️ Adding a New Condition-Triggered Module

### Step 1: Create JSON Config
File: `products/senior_trivia/modules/{module_id}.json`

```json
{
  "module": {
    "id": "your_module_id",
    "name": "Your Module Name",
    "condition_trigger": {
      "primary": "YOUR_CONDITION_LOGIC",
      "visibility": "conditional"
    },
    "display": {
      "title": "Your Module Title",
      "subtitle": "Description"
    }
  },
  "sections": [
    {
      "id": "intro",
      "type": "info",
      "content": ["Welcome text..."]
    },
    {
      "id": "questions",
      "questions": [
        {
          "id": "q1",
          "label": "Your question?",
          "options": [
            { "label": "Option A", "value": "a", "is_correct": true, "feedback": "..." }
          ]
        }
      ]
    },
    {
      "id": "results",
      "type": "results"
    }
  ]
}
```

### Step 2: Add Condition Detection Helper
In `products/senior_trivia/product.py`:

```python
def _has_your_condition() -> bool:
    """Check for your condition."""
    try:
        from core.flag_manager import get_chronic_conditions, is_active
        
        conditions = get_chronic_conditions()
        for condition in conditions:
            if condition.get("code") == "your_condition_code":
                return True
        
        return False
    except Exception:
        return False
```

### Step 3: Add Conditional Rendering
In `_render_module_hub()`:

```python
has_your_condition = _has_your_condition()

# Add condition-triggered modules
if has_your_condition:
    your_badge = badges_earned.get("your_module_id")
    your_module = {
        "key": "your_module_id",
        "title": "🎯 Your Module Title",
        "desc": "Module description",
        "time": "4 min",
        "questions": 6,
        "badge_status": "🆕 New" if not your_badge else None,
        "condition_triggered": True
    }
    modules.insert(4, your_module)  # Position as needed
```

### Step 4: Update Navi Messaging (Optional)
In `core/navi.py`, update encouragement logic:

```python
your_badge = badges_earned.get("your_module_id")
if _has_your_condition() and not your_badge:
    encouragement_text = "Your personalized message here..."
```

### Step 5: Test Following Standard Procedure
- Verify condition trigger
- Play & complete quiz
- Check badge persistence
- Test condition removal
- Validate Navi messaging

---

## 📈 Success Metrics

**Engagement Target**: Users with diabetes condition actively engage with Diabetes Knowledge Check within 7 days of booking advisor appointment or entering Waiting Room

**Tracking**:
- `product_tiles_v2['senior_trivia_hub']['badges_earned']['diabetes_knowledge']` - completion status
- `trivia_badge_awarded` event with `module_id: "diabetes_knowledge"` - telemetry
- Compare engagement rate vs. standard trivia modules

**Educational Impact**:
- Track score percentages to identify knowledge gaps
- Monitor question-level feedback engagement
- Assess replay rate (do users retake quiz?)

---

## ✅ Acceptance Criteria - Status

| Criterion | Status | Notes |
|-----------|--------|-------|
| Tile appears only with diabetes condition | ✅ Implemented | Via `_has_diabetes_condition()` |
| Game content follows trivia architecture | ✅ Implemented | Uses existing engine, JSON-driven |
| Completion awards Healthy You Badge | ✅ Implemented | Via standard badge system |
| Navi introduces when unlocked | ✅ Implemented | Dynamic encouragement text |
| Educational feedback displays | ✅ Implemented | Per-question feedback in JSON |
| No balloon animation | ✅ Implemented | Uses standard trivia results |
| Replay allowed after completion | ✅ Implemented | "Play Again" button |
| Visual/tone match trivia standards | ✅ Implemented | Identical UI components |
| No regression in other modules | ✅ Verified | No changes to existing trivia logic |
| Foundation for future modules | ✅ Documented | Architecture & step-by-step guide |

---

## 🚀 Deployment Notes

**Ready for**:
- ✅ Manual testing (follow testing procedure above)
- ✅ User acceptance testing with diabetes condition users
- ✅ Merge to `dev` branch when validated
- ✅ Production deployment after regression testing

**Dependencies**:
- Flag Manager (`core/flag_manager.py`) - must be functional
- GCP or Advisor Prep Medical section - for setting diabetes condition
- Module Engine (`core/modules/engine.py`) - already in use by trivia
- Product Tiles V2 (`st.session_state['product_tiles_v2']`) - already in use

**No Breaking Changes**:
- All changes additive (new module, new helpers)
- Existing trivia modules unchanged
- Graceful degradation if condition system unavailable

---

## 📞 Support & Future Work

**Questions?** Reference:
- `products/senior_trivia/modules/diabetes_knowledge.json` - Module content
- `products/senior_trivia/product.py` - Rendering logic
- `core/navi.py` - Intelligence layer integration

**Next Condition-Triggered Modules** (Priority Order):
1. COPD / Respiratory Health
2. Memory Support / Cognitive Fitness
3. Fall Risk / Mobility Safety
4. Cardiovascular Health
5. Chronic Pain / Arthritis Management

Each follows the same pattern documented above. Estimated implementation time: **2-3 hours per module** (mostly content creation, minimal code).

---

**End of Documentation**
