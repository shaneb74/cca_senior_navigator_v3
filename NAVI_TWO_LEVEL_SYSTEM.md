# Navi's Two-Level Guidance System

**Vision:** Navi provides guidance at BOTH the journey level (hub) and the module level (questions).

## The Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HUB / JOURNEY LEVEL                       │
│  "Where am I in the journey? What's next?"                   │
│                                                               │
│  Source: config/navi_dialogue.json                           │
│  Used by: hubs/concierge.py, core/ui.py (journey status)    │
│                                                               │
│  🤖 Navi: Hey Sarah! 1/3 complete.                          │
│  Next: Calculate Your Care Costs 💰                          │
│                                                               │
│  [GCP Tile] ✅ Assisted Living (85% confidence)             │
│  [Cost Tile] 🔒 Calculate your care costs                   │
│  [PFMA Tile] 🔒 Schedule advisor appointment                │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    [User clicks Cost Tile]
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   MODULE / QUESTION LEVEL                    │
│  "What am I doing RIGHT NOW? Why this question?"             │
│                                                               │
│  Source: products/cost_planner_v2/config.json (embedded)    │
│  Used by: core/modules/engine.py (module rendering)         │
│                                                               │
│  🤖 Navi: Let's start with income...                        │
│  I need to know your reliable monthly income. This includes  │
│  Social Security, pensions, investments, etc.                │
│  [Progress: 1/4]                                             │
│                                                               │
│  Q: What is your total monthly income? [?]                   │
│     ├─ Why: Understanding income helps calculate runway      │
│     ├─ Tip: Include ALL sources: SS, pensions, etc.         │
│     └─ Example: $3,500 Social Security + $2,000 pension     │
│                                                               │
│  [Input field]                                               │
└─────────────────────────────────────────────────────────────┘
```

## Level 1: Hub / Journey Guidance

**Purpose:** High-level navigation and journey status

**Source:** `config/navi_dialogue.json`

**Structure:**
```json
{
  "journey_phases": {
    "getting_started": { 
      "messages": {...},
      "context_boost": [...]
    },
    "in_progress": {...},
    "nearly_there": {...},
    "complete": {...}
  },
  "product_gates": {
    "cost_locked": {
      "message": "Hold on! Complete your care plan first...",
      "action": "Complete Guided Care Plan"
    }
  },
  "product_intros": {
    "gcp_start": {
      "welcome": "Let's figure out what level of care is right for you."
    }
  }
}
```

**Used By:**
- `hubs/concierge.py` - Product tiles with lock messages
- `core/ui.py:render_mcip_journey_status()` - Journey status banner
- `pages/_stubs.py:render_export_results()` - Export page

**What It Tells Users:**
- ✅ "You've completed GCP! 1/3 done."
- 🔒 "Cost Planner locked - complete GCP first"
- 🎉 "Journey complete! All 3 products done."
- 📤 "Share your results with family"

## Level 2: Module / Question Guidance

**Purpose:** Contextual guidance within a product module

**Source:** Module JSON files (e.g., `products/gcp_v4/modules/care_recommendation/config.json`)

**Structure:**
```json
{
  "navi_intro": {
    "text": "Let's figure out what level of care is right for you.",
    "subtext": "I'll ask about daily activities, health, and preferences.",
    "icon": "🧭"
  },
  "steps": [
    {
      "id": "daily_living",
      "navi_guidance": {
        "text": "Now let's talk about daily activities...",
        "subtext": "This determines your care level.",
        "icon": "🏠"
      },
      "fields": [
        {
          "id": "bathing",
          "label": "Can you bathe yourself?",
          "guidance": {
            "why": "Bathing assistance is a common care need.",
            "tip": "Include getting in/out of tub.",
            "example": "Think about last time you bathed..."
          }
        }
      ]
    }
  ],
  "navi_outro": {
    "text": "🎉 Care Plan Complete!",
    "subtext": "Next: Let's calculate costs.",
    "icon": "✅"
  }
}
```

**Used By:**
- `core/modules/engine.py:_render_navi_guide_bar()` - Section guidance
- `core/modules/components.py` (future) - Question tooltips

**What It Tells Users:**
- 🏠 "Let's talk about daily living - this determines care level"
- 💡 "Why am I asking about bathing? It's a common care need."
- 📝 "Be honest - there's no wrong answer!"
- ✅ "Section complete! Moving to cognitive health..."

## When to Use Each Level

### Use Hub/Journey Guidance (`navi_dialogue.json`) When:
- ❌ Showing overall journey progress
- ❌ Explaining why products are locked
- ❌ Welcoming users to start a product
- ❌ Celebrating journey completion
- ❌ Providing context boost (what we know so far)
- ❌ Guiding users to next product

### Use Module/Question Guidance (embedded JSON) When:
- ✅ Starting a new section within a module
- ✅ Explaining why a specific question matters
- ✅ Providing tips for answering a question
- ✅ Giving examples to clarify a question
- ✅ Celebrating section completion
- ✅ Transitioning between sections

## Why Both Are Needed

**Hub Guidance** answers: "Where am I going?"
- Cross-product navigation
- Journey-level progress
- Product unlocking logic
- Next action recommendations

**Module Guidance** answers: "What am I doing?"
- In-question context
- Section-level flow
- Question-specific help
- Learning as you go

## Example User Flow

### Starting from Hub
```
[Concierge Hub]
🤖 Navi (Hub): Hey Sarah! Create Your Guided Care Plan 🧭
              I'm here to guide you through your senior care journey.
              
[User clicks "Start GCP"]
```

### Entering Module
```
[GCP Module - Intro Step]
🤖 Navi (Module): Let's figure out what level of care is right for you.
                 I'll ask about daily activities, health, and preferences. ~2 minutes!
                 
[User clicks "Start"]
```

### During Questions
```
[GCP Module - Daily Living Section]
🤖 Navi (Module): Now let's talk about daily activities...
                 I'm asking about bathing, dressing, eating, and mobility.
                 This determines your care level.
[Progress: 1/5]

Q: Can you bathe yourself independently? [?]
   ↓ [User clicks ?]
   💡 Why: Bathing assistance is one of the most common care needs.
   💡 Tip: This includes getting in/out of tub, not just washing.
   💡 Example: Did you need help getting in the shower last time?
```

### Completing Module
```
[GCP Module - Results Step]
🤖 Navi (Module): 🎉 Care Plan Complete! You're doing great.
                 Next: Let's calculate costs so you know what to expect. 💰
                 
[User clicks "Calculate Costs"]
```

### Back to Hub
```
[Concierge Hub]
🤖 Navi (Hub): Great job, Sarah! 1/3 complete. 💰 Calculate Your Care Costs
              Based on your Assisted Living recommendation, let's figure out the costs.
              
[GCP Tile] ✅ Assisted Living (85% confidence)
[Cost Tile] 🔓 Ready to start! [Start button enabled]
```

## Implementation Status

### ✅ COMPLETE: Hub/Journey Guidance
- [x] `navi_dialogue.json` with journey phases
- [x] `render_mcip_journey_status()` in hub
- [x] Product gates and intros
- [x] Context-aware messaging

### ✅ COMPLETE: Module/Question Schema
- [x] `ModuleConfig.navi_intro` and `navi_outro`
- [x] `StepDef.navi_guidance` for sections
- [x] `FieldDef.guidance` for questions
- [x] Engine reads embedded guidance

### ⏳ TODO: Module JSON Updates
- [ ] Add guidance to GCP `care_recommendation/config.json`
- [ ] Add guidance to Cost Planner steps
- [ ] Add guidance to PFMA booking flow

### ⏳ TODO: Question Tooltip UI
- [ ] Render `?` icon next to questions with guidance
- [ ] Popover showing why/tip/example
- [ ] Accessible keyboard navigation

## File Organization

```
config/
  navi_dialogue.json           # Hub/journey level guidance
  
products/
  gcp_v4/
    modules/
      care_recommendation/
        config.json              # Module-level guidance (embedded)
  cost_planner_v2/
    config.json                  # Module-level guidance (embedded)
  pfma_v2/
    config.json                  # Module-level guidance (embedded)

core/
  navi_dialogue.py               # Loads hub guidance from JSON
  modules/
    engine.py                    # Reads module guidance from config
    schema.py                    # Defines guidance fields
  ui.py                          # Renders both guide bars
```

## Summary

**Two levels, two purposes:**

1. **Hub Guidance** (`navi_dialogue.json`)
   - Journey-level navigation
   - Product gates and intros
   - Overall progress tracking
   - Used by hub and product tiles

2. **Module Guidance** (embedded in module JSON)
   - Section-level context
   - Question-level tooltips
   - In-the-moment help
   - Used by module engine

**Both are essential!** Hub guidance gets you TO the right place. Module guidance helps you WHILE you're there. 🤖✨
