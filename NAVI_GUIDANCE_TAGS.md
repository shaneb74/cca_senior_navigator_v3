# Navi Guidance Tags in Module Contracts

**Vision:** Embed Navi's contextual guidance directly in module JSON so she stays on-topic and dynamic.

## The Evolution

**Before:**
- Navi guidance lived in separate `navi_dialogue.json`
- Only had broad module-level messages (intro, mobility, cognitive, etc.)
- No question-specific guidance
- Had to manually map step IDs to dialogue keys

**After:**
- **Guidance tags embedded in module JSON**
- Section-level guidance in module schema
- Optional question-level guidance tooltips
- Navi reads directly from module contract
- Self-documenting modules

## Schema Changes

### 1. Section-Level Guidance

Add `navi_guidance` to each section in module schema:

```json
{
  "sections": [
    {
      "id": "about_you",
      "title": "About You",
      "navi_guidance": {
        "text": "Let's start with the basics...",
        "subtext": "I need to understand who we're planning for. This helps me personalize everything.",
        "icon": "👤",
        "color": "#8b5cf6"
      },
      "questions": [...]
    },
    {
      "id": "daily_living",
      "title": "Daily Living",
      "navi_guidance": {
        "text": "Now let's talk about daily activities...",
        "subtext": "I'm asking about bathing, dressing, eating, and mobility. This determines your care level.",
        "icon": "🏠",
        "color": "#3b82f6"
      },
      "questions": [...]
    }
  ]
}
```

### 2. Question-Level Guidance (Optional Tooltips)

Add optional `guidance` field to individual questions:

```json
{
  "questions": [
    {
      "id": "mobility",
      "text": "Can you walk independently?",
      "type": "radio",
      "guidance": {
        "why": "Mobility affects where you can live and how much assistance you need.",
        "tip": "Be honest! If you use a walker or cane, that's important to know.",
        "example": "Think about your daily routine - can you walk to the bathroom, kitchen, and around your home safely?"
      },
      "options": [...]
    },
    {
      "id": "bathing",
      "text": "Can you bathe yourself?",
      "type": "radio",
      "guidance": {
        "why": "Bathing assistance is one of the most common care needs.",
        "tip": "This includes getting in/out of the tub or shower, not just washing."
      },
      "options": [...]
    }
  ]
}
```

### 3. Module-Level Intro/Outro

Add top-level `navi_intro` and `navi_outro`:

```json
{
  "module": "care_recommendation",
  "title": "Guided Care Plan",
  "navi_intro": {
    "text": "Let's figure out what level of care is right for you.",
    "subtext": "I'll ask about daily activities, health, and preferences. This takes about 2 minutes.",
    "icon": "🧭"
  },
  "navi_outro": {
    "text": "🎉 Care Plan Complete! You're doing great.",
    "subtext": "Next: Let's calculate costs so you know what to expect. 💰",
    "icon": "✅"
  },
  "sections": [...]
}
```

## UI Components

### 1. Section-Level Bar (Current Implementation)
Already built - `render_navi_guide_bar()` at top of each section.

### 2. Question Tooltip (NEW)
Small `?` icon next to questions that have guidance:

```python
def render_question_with_guidance(question: dict, state: dict):
    """Render question with optional Navi guidance tooltip."""
    
    # Question label with optional tooltip
    cols = st.columns([10, 1])
    
    with cols[0]:
        st.markdown(f"**{question['text']}**")
    
    with cols[1]:
        guidance = question.get("guidance")
        if guidance:
            with st.popover("?", help="Why we're asking this"):
                st.markdown(f"**🤖 Navi says:**")
                if "why" in guidance:
                    st.markdown(f"**Why:** {guidance['why']}")
                if "tip" in guidance:
                    st.info(f"💡 **Tip:** {guidance['tip']}")
                if "example" in guidance:
                    st.markdown(f"**Example:** {guidance['example']}")
    
    # Render question input
    # ... (existing logic)
```

## Implementation Plan

### Phase 1: Update Module Schema (IMMEDIATE)
1. Extend `ModuleConfig` dataclass with guidance fields
2. Update JSON schema to include `navi_guidance` on sections
3. Add optional `guidance` field to question schema

### Phase 2: Update GCP care_recommendation.json (HIGH)
1. Add `navi_intro` and `navi_outro` at module level
2. Add `navi_guidance` to each section:
   - about_you
   - daily_living
   - mobility
   - cognitive_health
   - medical_needs
   - social_preferences
   - living_preferences
3. Add question-level `guidance` to key questions (10-15 most important)

### Phase 3: Update Module Engine (HIGH)
1. Read `navi_guidance` from current section
2. Pass to `_render_navi_guide_bar()`
3. Fall back to dialogue JSON if no guidance in module
4. Update question rendering to show guidance tooltips

### Phase 4: Update Other Products (MEDIUM)
1. Cost Planner v2: Add guidance tags to financial questions
2. PFMA v2: Add guidance to booking steps
3. Future modules: Guidance becomes standard practice

### Phase 5: Deprecate Static Dialogue (LOW)
1. Keep `navi_dialogue.json` for journey-level messages
2. Move module-specific guidance into module JSON
3. Modules become self-contained with their own guidance

## Example: GCP care_recommendation.json

```json
{
  "module_id": "care_recommendation",
  "title": "Guided Care Plan",
  "description": "Personalized care level recommendation",
  "state_key": "gcp_state",
  "product": "gcp_v4",
  
  "navi_intro": {
    "text": "Let's figure out what level of care is right for you.",
    "subtext": "I'll ask about daily activities, health, and preferences. This takes about 2 minutes.",
    "icon": "🧭",
    "color": "#8b5cf6"
  },
  
  "navi_outro": {
    "text": "🎉 Care Plan Complete! You're doing great.",
    "subtext": "Next: Let's calculate costs so you know what to expect. 💰",
    "icon": "✅",
    "color": "#10b981"
  },
  
  "steps": [
    {
      "id": "intro",
      "type": "intro",
      "title": "Let's Create Your Care Plan",
      "subtitle": "Answer a few questions to get your personalized recommendation.",
      "show_progress": false
    },
    {
      "id": "about_you",
      "type": "form",
      "title": "About You",
      "subtitle": "Tell me who we're planning for.",
      "show_progress": true,
      "navi_guidance": {
        "text": "Let's start with the basics...",
        "subtext": "I need to understand who we're planning for. This helps me personalize everything.",
        "icon": "👤"
      },
      "fields": [
        {
          "id": "age",
          "label": "What is your age?",
          "type": "number",
          "required": true,
          "guidance": {
            "why": "Age affects care eligibility and costs. Some benefits are age-restricted.",
            "tip": "If planning for someone else, enter their age."
          }
        },
        {
          "id": "gender",
          "label": "Gender",
          "type": "radio",
          "required": true,
          "options": ["Male", "Female", "Non-binary", "Prefer not to say"],
          "guidance": {
            "why": "Some care facilities have gender-specific wings or programs."
          }
        }
      ]
    },
    {
      "id": "daily_living",
      "type": "form",
      "title": "Daily Living Activities",
      "subtitle": "How independent are you with everyday tasks?",
      "show_progress": true,
      "navi_guidance": {
        "text": "Now let's talk about daily activities...",
        "subtext": "I'm asking about bathing, dressing, eating, and mobility. This determines your care level.",
        "icon": "🏠"
      },
      "fields": [
        {
          "id": "bathing",
          "label": "Can you bathe yourself independently?",
          "type": "radio",
          "required": true,
          "options": [
            "Yes, without help",
            "Yes, with some assistance",
            "No, I need full assistance"
          ],
          "guidance": {
            "why": "Bathing assistance is one of the most common care needs.",
            "tip": "This includes getting in/out of the tub or shower, not just washing.",
            "example": "Think about the last time you bathed. Did you need help getting in the shower? Did someone help you wash?"
          }
        },
        {
          "id": "dressing",
          "label": "Can you dress yourself independently?",
          "type": "radio",
          "required": true,
          "options": [
            "Yes, without help",
            "Yes, with some assistance",
            "No, I need full assistance"
          ],
          "guidance": {
            "why": "Dressing ability indicates fine motor skills and cognitive function.",
            "tip": "Include putting on shoes, buttons, zippers - not just pulling clothes on."
          }
        },
        {
          "id": "eating",
          "label": "Can you eat independently?",
          "type": "radio",
          "required": true,
          "options": [
            "Yes, without help",
            "Yes, with some assistance (cutting food, opening containers)",
            "No, I need to be fed"
          ],
          "guidance": {
            "why": "Eating independence affects dining options and care level.",
            "tip": "This includes using utensils, not just chewing and swallowing."
          }
        },
        {
          "id": "mobility",
          "label": "How is your mobility?",
          "type": "radio",
          "required": true,
          "options": [
            "I can walk independently",
            "I use a walker or cane",
            "I use a wheelchair",
            "I'm bedbound"
          ],
          "guidance": {
            "why": "Mobility affects where you can live and how much assistance you need.",
            "tip": "Be honest! If you use a walker or cane, that's important to know.",
            "example": "Think about your daily routine - can you walk to the bathroom, kitchen, and around your home safely?"
          }
        }
      ]
    },
    {
      "id": "cognitive_health",
      "type": "form",
      "title": "Cognitive Health",
      "subtitle": "Let's talk about memory and mental health.",
      "show_progress": true,
      "navi_guidance": {
        "text": "Now let's talk about cognitive health...",
        "subtext": "This helps me understand if memory support or mental health assistance might be helpful.",
        "icon": "🧠"
      },
      "fields": [
        {
          "id": "memory_concerns",
          "label": "Do you have memory concerns?",
          "type": "radio",
          "required": true,
          "options": [
            "No memory issues",
            "Occasional forgetfulness",
            "Frequent memory problems",
            "Diagnosed with dementia/Alzheimer's"
          ],
          "guidance": {
            "why": "Memory care requires specialized facilities and trained staff.",
            "tip": "It's okay to be honest. Early intervention helps!",
            "example": "Do you forget appointments? Lose track of conversations? Get confused about time or place?"
          }
        },
        {
          "id": "mental_health",
          "label": "Are you experiencing depression or anxiety?",
          "type": "radio",
          "required": true,
          "options": [
            "No concerns",
            "Mild symptoms",
            "Moderate symptoms",
            "Severe symptoms"
          ],
          "guidance": {
            "why": "Mental health support is part of holistic senior care.",
            "tip": "Many seniors experience depression. You're not alone!"
          }
        }
      ]
    }
  ],
  
  "results_step_id": "recommendation",
  "outcome_contract": {
    "type": "CareRecommendation",
    "fields": [
      "recommended_tier",
      "confidence_score",
      "rationale",
      "assessment_summary"
    ]
  }
}
```

## Benefits

### For Users
✅ **Context at every step** - Navi explains WHY each question matters
✅ **Reduced anxiety** - Tooltips provide reassurance and examples
✅ **Better answers** - Guidance helps users understand what we're asking
✅ **Learning** - Users understand the assessment process

### For Developers
✅ **Self-documenting modules** - Guidance lives with the questions
✅ **Single source of truth** - No separate dialogue JSON to maintain
✅ **Easy to update** - Change guidance when you change questions
✅ **Portable** - Module JSON contains everything needed

### For System
✅ **Dynamic guidance** - Navi automatically picks up new questions
✅ **Consistent structure** - All modules follow same pattern
✅ **Extensible** - Easy to add guidance to new modules
✅ **Testable** - Can validate guidance exists for all questions

## Migration Path

1. **Phase 1 (Now):** Add schema support for guidance tags
2. **Phase 2 (Next):** Update GCP care_recommendation.json
3. **Phase 3 (Soon):** Update engine to read and render guidance
4. **Phase 4 (Later):** Migrate Cost Planner and PFMA
5. **Phase 5 (Future):** Deprecate module_guidance from navi_dialogue.json

## Future: AI-Generated Guidance

When we add LLM integration:

```python
# Module defines the WHAT, AI provides the HOW
module_question = {
    "id": "mobility",
    "text": "Can you walk independently?",
    "guidance_prompt": "Explain why mobility matters for senior care planning"
}

# LLM generates contextual guidance on the fly
navi_guidance = await NaviAI.generate_guidance(
    question=module_question,
    user_context={
        "age": 78,
        "previous_answers": {...}
    }
)

# Result: Personalized explanation
# "Sarah, at 78, mobility is crucial because..."
```

---

**Bottom Line:** Every module becomes **self-aware** with embedded Navi guidance. She knows exactly what to say at every step because it's written right into the module contract. No more manual mapping, no more separate dialogue files - just contextual, helpful guidance wherever you are. 🤖✨
