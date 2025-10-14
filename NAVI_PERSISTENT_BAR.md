# Navi Persistent Guide Bar

**Vision:** Navi is not a side quest - she's your digital planning partner sitting at the top of every screen.

## The Concept

**Before:**
- Navi only appeared in the Concierge Hub journey status banner
- Inside products, users were on their own
- Guidance was disconnected from the actual work

**After:**
- **Navi sits at the top of EVERY module, EVERY question**
- Persistent info bar that follows you through the entire journey
- Contextually aware of what you're doing RIGHT NOW
- Gives preemptive guidance about why we're asking each question
- "She knows about them (modules), but they don't need to know about her"

## Architecture

### Hub Level
```
┌─────────────────────────────────────────────────┐
│ 🤖 Navi: Hey Sarah! 1/3 complete.              │
│ Next: Calculate Your Care Costs 💰              │
└─────────────────────────────────────────────────┘
  [Product Tiles Below]
```

### Inside Product - Module Level
```
┌─────────────────────────────────────────────────┐
│ 🤖 Navi: Let's talk about mobility...          │
│ I'm asking this to understand if you need help  │
│ getting around. No judgement - just planning! 😊 │
└─────────────────────────────────────────────────┘
  [Question: Can you walk independently?]
  [ ] Yes, without help
  [ ] Yes, with a walker/cane
  [ ] No, I need wheelchair assistance
```

### Component Structure

**1. Persistent Navi Bar Component**
- File: `core/ui.py` - Add `render_navi_guide_bar()`
- Always visible at top of page
- Compact bar format (not full banner)
- Context-aware messaging

**2. Module-Level Dialogue**
- Extend `config/navi_dialogue.json` with module-specific messages
- Add section: `"module_guidance"` with per-module context
- Messages explain WHY we're asking each question
- Encourage honest answers, reduce anxiety

**3. Integration Points**
- GCP modules (mobility, cognitive, medical, social, living)
- Cost Planner steps (income, assets, expenses)
- PFMA booking flow (select advisor, choose time, confirm)

## Navi Bar States

### 1. Journey Status (Hub)
```
🤖 Navi: Hey Sarah! Create Your Guided Care Plan 🧭
Progress: 0/3 complete
```

### 2. Product Intro (Starting Module)
```
🤖 Navi: Let's figure out what level of care is right for you.
I'll ask about daily activities, health, and preferences. ~2 minutes!
```

### 3. Module Context (During Questions)
```
🤖 Navi: Let's talk about mobility...
I'm asking this to understand your daily movement needs. Be honest!
```

### 4. Module Complete (Finished Section)
```
🤖 Navi: Great! Now let's talk about cognitive health...
This helps me understand if memory support might be helpful.
```

### 5. Product Complete (Done)
```
🤖 Navi: 🎉 Care Plan Complete! You're doing great.
Next: Let's calculate costs so you know what to expect. 💰
```

## Visual Design

### Compact Bar (Not Full Banner)
```css
/* Persistent guide bar - always at top */
.navi-guide-bar {
  background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
  padding: 12px 20px;
  border-radius: 8px;
  margin-bottom: 16px;
  color: white;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.navi-guide-bar .icon {
  font-size: 24px;
  flex-shrink: 0;
}

.navi-guide-bar .content {
  flex: 1;
}

.navi-guide-bar .main-text {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 2px;
}

.navi-guide-bar .sub-text {
  font-size: 12px;
  opacity: 0.9;
}
```

### Responsive Behavior
- Desktop: Full message with icon and subtext
- Mobile: Collapses to single line with expand option
- Always pinned to top (scrolls with content, not sticky)

## Module Dialogue Structure

Add to `config/navi_dialogue.json`:

```json
{
  "module_guidance": {
    "gcp": {
      "intro": {
        "text": "Let's figure out what level of care is right for you.",
        "subtext": "I'll ask about daily activities, health, and preferences. This takes about 2 minutes.",
        "icon": "🧭"
      },
      "mobility": {
        "text": "Let's talk about mobility...",
        "subtext": "I'm asking this to understand your daily movement needs. Be honest - there's no wrong answer!",
        "icon": "🚶"
      },
      "cognitive": {
        "text": "Now let's talk about cognitive health...",
        "subtext": "This helps me understand if memory support or mental health assistance might be helpful.",
        "icon": "🧠"
      },
      "medical": {
        "text": "Let's review medical needs...",
        "subtext": "Understanding your health conditions helps me recommend the right level of care.",
        "icon": "💊"
      },
      "social": {
        "text": "Let's talk about social and emotional needs...",
        "subtext": "Connection and engagement are so important! This helps me understand your social preferences.",
        "icon": "👥"
      },
      "living": {
        "text": "Finally, let's talk about living preferences...",
        "subtext": "Where and how you want to live matters. This helps me match you to the right environment.",
        "icon": "🏠"
      },
      "complete": {
        "text": "🎉 Care Plan Complete! You're doing great.",
        "subtext": "Next: Let's calculate costs so you know what to expect. 💰",
        "icon": "✅"
      }
    },
    "cost_planner": {
      "intro": {
        "text": "Let's figure out the financial side of {tier}.",
        "subtext": "I'll ask about income, assets, and expenses. This helps estimate your monthly costs and how long your money will last.",
        "icon": "💰"
      },
      "income": {
        "text": "Let's start with income...",
        "subtext": "I need to know your reliable monthly income. This includes Social Security, pensions, investments, etc.",
        "icon": "💵"
      },
      "assets": {
        "text": "Now let's talk about assets...",
        "subtext": "Understanding your savings and property helps me calculate your financial runway.",
        "icon": "🏦"
      },
      "expenses": {
        "text": "Finally, current expenses...",
        "subtext": "Knowing what you spend now helps me show you the real cost difference.",
        "icon": "📊"
      },
      "complete": {
        "text": "💰 Cost Estimate Complete! You're almost done.",
        "subtext": "Next: Let's schedule your advisor appointment. 📅",
        "icon": "✅"
      }
    },
    "pfma": {
      "intro": {
        "text": "Time to schedule your advisor appointment!",
        "subtext": "I'll connect you with an expert who can answer questions and help you move forward.",
        "icon": "📅"
      },
      "select_advisor": {
        "text": "Choose your advisor type...",
        "subtext": "Different advisors specialize in different things. Pick the one that fits your needs best!",
        "icon": "👤"
      },
      "choose_time": {
        "text": "Pick a time that works for you...",
        "subtext": "Your advisor will call you at the time you choose. Make sure you have 30-45 minutes free.",
        "icon": "⏰"
      },
      "confirm": {
        "text": "Almost there! Just confirm your details...",
        "subtext": "Double-check everything is correct before we book your appointment.",
        "icon": "✅"
      },
      "complete": {
        "text": "🎉 Congratulations! You did it!",
        "subtext": "Your advisor will call you at the scheduled time. You've completed your entire journey!",
        "icon": "🎉"
      }
    }
  }
}
```

## Implementation Plan

### Phase 1: Core Component (IMMEDIATE)
1. Create `render_navi_guide_bar()` in `core/ui.py`
2. Accept `message_dict` parameter (same format as journey status)
3. Render compact bar at top of page
4. Test in one module first

### Phase 2: Dialogue Integration (HIGH)
1. Extend `config/navi_dialogue.json` with module guidance
2. Add `NaviDialogue.get_module_message(product_key, module_key, context)`
3. Update dialogue loader to support module-level messages

### Phase 3: Product Integration (HIGH)
1. **GCP v4:** Add Navi bar to each module render
2. **Cost Planner v2:** Add Navi bar to each step
3. **PFMA v2:** Add Navi bar to each booking step
4. Pass current module context to Navi

### Phase 4: Context Awareness (MEDIUM)
1. Track which question user is on
2. Update Navi message as user progresses
3. Celebrate section completion
4. Smooth transitions between modules

### Phase 5: Polish (LOW)
1. Animation when message changes
2. Collapse/expand on mobile
3. Optional "Why am I seeing this?" info button
4. Accessibility (ARIA labels, screen reader support)

## User Experience Flow

### GCP Example - Full Journey
```
[Starting GCP]
🤖 Navi: Let's figure out what level of care is right for you.
       I'll ask about daily activities, health, and preferences. ~2 minutes!

[Question 1 - Mobility]
🤖 Navi: Let's talk about mobility...
       I'm asking this to understand your daily movement needs. Be honest!

Q: Can you walk independently?
[ ] Yes, without help
[ ] Yes, with a walker/cane
[ ] No, I need wheelchair assistance

[Question 2 - ADLs]
🤖 Navi: Still on mobility...
       Can you do these activities on your own?

Q: Can you bathe, dress, and eat independently?
...

[Section Complete - Moving to Cognitive]
🤖 Navi: Great! Now let's talk about cognitive health...
       This helps me understand if memory support might be helpful.

Q: Do you have memory concerns?
...

[GCP Complete]
🤖 Navi: 🎉 Care Plan Complete! You're doing great.
       Next: Let's calculate costs so you know what to expect. 💰
```

## Technical Notes

### Props for render_navi_guide_bar()
```python
def render_navi_guide_bar(
    text: str,
    subtext: Optional[str] = None,
    icon: str = "🤖",
    show_progress: bool = False,
    current_step: Optional[int] = None,
    total_steps: Optional[int] = None
) -> None:
    """Render persistent Navi guide bar at top of page.
    
    Args:
        text: Main message from Navi
        subtext: Additional context (optional)
        icon: Emoji icon (default: 🤖)
        show_progress: Whether to show progress indicator
        current_step: Current step number (for progress)
        total_steps: Total steps (for progress)
    """
```

### Module Integration Pattern
```python
# At top of every module render function
from core.ui import render_navi_guide_bar
from core.navi_dialogue import NaviDialogue

def render_mobility_module():
    # Get Navi's guidance for this module
    guidance = NaviDialogue.get_module_message("gcp", "mobility")
    render_navi_guide_bar(
        text=guidance["text"],
        subtext=guidance["subtext"],
        icon=guidance["icon"]
    )
    
    # Rest of module render
    st.write("### Mobility Assessment")
    # ... questions ...
```

## Benefits

### For Users
✅ **Never feel lost** - Navi is always there explaining what's happening
✅ **Reduced anxiety** - Understand WHY you're being asked each question
✅ **Encouragement** - Navi celebrates progress and keeps you motivated
✅ **Consistency** - Same friendly voice throughout entire journey

### For System
✅ **Separation of concerns** - Modules don't need to know about Navi
✅ **Centralized messaging** - All guidance in one JSON file
✅ **Easy to update** - Change Navi's personality without touching module code
✅ **Foundation for AI** - Context structure ready for LLM integration

## Future: Dynamic Context

When we add LLM integration, Navi can become truly dynamic:

```python
# Future: LLM-powered context
navi_message = await NaviLLM.get_contextual_guidance(
    user_name="Sarah",
    product="gcp",
    module="mobility",
    question_index=3,
    previous_answers=session_state.gcp_answers,
    sentiment="anxious"  # detected from hesitation
)

# Navi might say:
# "Hey Sarah, I notice you're taking your time here. That's totally fine!
#  This question about walking is just to help me understand your daily
#  routine. There's no wrong answer - be honest about what feels true for you."
```

## Success Metrics

Track how Navi affects user behavior:
- **Completion rates:** Do more users finish with Navi?
- **Time per question:** Does guidance reduce hesitation?
- **Answer quality:** More honest/complete responses?
- **Return rates:** Do users come back more often?
- **Sentiment:** Feedback mentions of "helpful," "clear," "supportive"

---

**Bottom Line:** Navi is not an optional feature - she's the constant companion that makes this journey feel guided, supported, and achievable. She sits at the top of every screen, always there, always helpful, always encouraging. 🤖✨
