# Meet Navi 🤖

**Your AI Care Navigator**

---

## What is Navi?

**Navi** is your friendly AI guide through the senior care journey. She's the personality behind the Senior Navigator platform - always there to help, guide, and celebrate your progress.

### The Name

**Navi** = **Navi**gator 🧭

Short, friendly, and memorable. Navi is not just software - she's your companion through an important journey.

---

## What Navi Does

### 1. **Guides You Through Products** 🎯

Navi tells you exactly what to do next:
- "🤖 Navi: Hey Sarah! Create Your Guided Care Plan"
- "🤖 Navi: 1/3 complete. Calculate Your Care Costs"
- "🤖 Navi: 2/3 complete. Schedule Your Advisor Appointment"
- "🤖 Navi says: Journey Complete! 🎉"

### 2. **Shows Dynamic Summaries** 📊

Navi pulls real data from your completed products:
- **GCP Complete:** "✅ Assisted Living (85% confidence)"
- **Cost Planner Complete:** "✅ $4,500/month (30 month runway)"
- **PFMA Complete:** "✅ Phone Appt - Oct 20"

### 3. **Celebrates Achievements** 🏆

Navi awards badges as you progress:
- 🧭 **Care Navigator** - Complete Guided Care Plan
- 💰 **Financial Planner** - Complete Cost Planner
- 📅 **Appointment Setter** - Schedule with advisor

Plus confetti when you finish! 🎉

### 4. **Remembers Everything** 💾

Navi tracks your entire journey:
- Which products you've completed
- What's unlocked and ready
- Your personalized recommendations
- Your next best step

### 5. **Personalizes Your Experience** 👋

When you're logged in:
- "Hey Sarah!" instead of "Hey there!"
- "Sarah's Journey Summary" in exports
- Your name in journey status

---

## Technical Architecture

### Code Name: MCIP

**Behind the scenes**, Navi is powered by the **Master Care Intelligence Panel (MCIP)**:

```
User sees: "🤖 Navi says: Complete your care plan"
Code uses:  MCIP.get_recommended_next_action()
```

**MCIP** is the technical engine. **Navi** is the friendly personality.

### Navi's Brain

Navi reads from three data contracts:
1. **CareRecommendation** - GCP results (tier, confidence, flags)
2. **FinancialProfile** - Cost estimates (monthly cost, runway)
3. **AdvisorAppointment** - PFMA booking (date, time, type)

All stored in `st.session_state["mcip"]`

### Intelligence Layer

Navi provides three key guidance methods:

```python
# What should user do next?
MCIP.get_recommended_next_action()
→ {
    "action": "🧭 Create Your Guided Care Plan",
    "reason": "Get a personalized care recommendation",
    "route": "gcp_v4",
    "status": "getting_started"
}

# What's the product summary?
MCIP.get_product_summary("cost_v2")
→ {
    "title": "Cost Planner",
    "status": "complete",
    "summary_line": "✅ $4,500/month (30 month runway)",
    "icon": "💰"
}

# How far along?
MCIP.get_journey_progress()
→ {
    "completed_count": 2,
    "completed_products": ["gcp", "cost_planner"]
}
```

---

## Where You'll See Navi

### 1. **Journey Status Banner** (Concierge Hub)

Purple → Blue → Amber → Green banner showing:
- "🤖 Navi: [guidance message]"
- Progress fraction (1/3, 2/3)
- Achievement badges
- Next action button

### 2. **Product Tiles** (Concierge Hub)

Dynamic summaries on each tile:
- Before: "Estimate monthly costs and runway"
- After: "✅ $4,500/month (30 month runway)"

### 3. **Export Page**

- "Powered by 🤖 Navi - Your AI Care Navigator"
- "Navi's Recommendation: Assisted Living"
- Footer: "🤖 Navi here! Your progress is always saved..."

### 4. **Future Features**

Coming soon:
- Navi chat interface (AI advisor)
- Navi tips and hints throughout products
- Navi onboarding tutorial
- "Ask Navi" help button

---

## Design Principles

### 1. **Helpful, Not Pushy**

Navi suggests, doesn't demand:
- ✅ "Create Your Guided Care Plan"
- ❌ "You must complete GCP now!"

### 2. **Positive & Encouraging**

Navi celebrates progress:
- "Great job! 1/3 complete"
- "Almost done! 2/3 complete"
- "Journey Complete! 🎉"

### 3. **Clear & Actionable**

Every Navi message has a purpose:
- What to do: "Calculate Your Care Costs"
- Why to do it: "Understand the financial side of your care plan"
- How to do it: [→ Button to navigate]

### 4. **Personalized**

Navi uses your name and context:
- "Hey Sarah! Let's create your care plan"
- "Based on your Assisted Living recommendation"

### 5. **Consistent Personality**

Navi's voice across all touchpoints:
- 🤖 emoji (robot = AI)
- Short, friendly sentences
- Always guiding forward

---

## User Journey with Navi

### First Visit (Not Authenticated)

```
Header: [Log in] button

🤖 Navi: Hey there! 🧭 Create Your Guided Care Plan
Get a personalized care recommendation based on your needs.
[→ Create Your Guided Care Plan]

Tiles:
- GCP: "Get your personalized care recommendation" 🧭
- Cost: "🔒 Complete Guided Care Plan first"
- PFMA: "🔒 Complete Cost Planner first"
```

### After Login

```
Header: 👋 Sarah [Log out]

🤖 Navi: Hey Sarah! 🧭 Create Your Guided Care Plan
Get a personalized care recommendation based on your needs.
[→ Create Your Guided Care Plan]
```

### After GCP Complete

```
🤖 Navi: Hey Sarah! 1/3 complete. 💰 Calculate Your Care Costs
Understand the financial side of your care plan.

Badges: [🧭 ✓ Care Navigator]

[→ Calculate Your Care Costs] [📤 Share My Results]

Tiles:
- GCP: "✅ Assisted Living (85% confidence)" 🧭
- Cost: "Calculate your care costs" 💰 (unlocked, silver gradient)
- PFMA: "🔒 Complete Cost Planner first"
```

### After Cost Planner Complete

```
🤖 Navi: 2/3 complete. 📅 Schedule Your Advisor Appointment
Meet with an advisor to finalize your plan.

Badges: [🧭 ✓ Care Navigator] [💰 ✓ Financial Planner]

[→ Schedule Your Advisor Appointment] [📤 Share My Results]

Tiles:
- GCP: "✅ Assisted Living (85% confidence)" 🧭
- Cost: "✅ $4,500/month (30 month runway)" 💰
- PFMA: "Schedule your advisor appointment" 📅 (unlocked, silver gradient)
```

### Journey Complete

```
🤖 Navi says: 🎉 Journey Complete!
You've completed your care plan, cost analysis, and scheduled appointment.

Badges: [🧭 ✓ Care Navigator] [💰 ✓ Financial Planner] [📅 ✓ Appointment Setter]

🎊 CONFETTI ANIMATION 🎊

[📤 Share My Results]

Tiles:
- GCP: "✅ Assisted Living (85% confidence)" 🧭
- Cost: "✅ $4,500/month (30 month runway)" 💰
- PFMA: "✅ Phone Appt - Oct 20" 📅
```

---

## Implementation Files

**Core Intelligence:**
- `core/mcip.py` - Navi's brain (MCIP methods)

**UI Components:**
- `core/ui.py` - Journey status banner with Navi branding
- `pages/_stubs.py` - Export page with Navi mentions
- `hubs/concierge.py` - Hub that calls Navi for guidance

**Data Contracts:**
- `CareRecommendation` - From GCP
- `FinancialProfile` - From Cost Planner  
- `AdvisorAppointment` - From PFMA

---

## Future: Navi AI Chat

Planned enhancement - conversational Navi:

```
User: "What care level do I need?"
Navi: "Based on your Guided Care Plan, I recommend Assisted Living 
       with 85% confidence. This is because you indicated needing help 
       with bathing and medication management. Would you like to see 
       cost estimates for this level of care?"

User: "Yes"
Navi: "Great! I'll take you to the Cost Planner where we can estimate 
       monthly costs for Assisted Living in your area. Ready?"
```

Integration with:
- FAQ knowledge base
- Product guidance
- Conversational prompts
- Context-aware help

---

## Brand Guidelines

### Voice & Tone

**Navi is:**
- ✅ Helpful & supportive
- ✅ Clear & direct
- ✅ Encouraging & positive
- ✅ Professional but warm

**Navi is NOT:**
- ❌ Bossy or demanding
- ❌ Technical or jargony
- ❌ Overly casual or silly
- ❌ Negative or discouraging

### Writing Style

**Short sentences:**
- "Complete your care plan."
- "Calculate your costs next."

**Action-oriented:**
- Start with verbs: "Create", "Calculate", "Schedule"
- Include "why": "Get a personalized recommendation"

**Positive framing:**
- ✅ "1/3 complete. Great job!"
- ❌ "2/3 remaining. Keep going."

### Visual Identity

**Emoji:** 🤖 (robot = AI guide)
**Colors:** Status-based gradients (purple/blue/amber/green)
**Typography:** Bold for Navi's name, normal for message
**Layout:** Banner format with icon, message, progress

---

## Success Metrics

Track Navi's impact:
- **Engagement:** % users who click Navi's next action buttons
- **Completion:** % users who complete all 3 products
- **Time:** Average days to complete journey (with vs without Navi)
- **Satisfaction:** "Was Navi helpful?" rating
- **Return:** % users who return after leaving mid-journey

---

## Conclusion

**Navi transforms MCIP from backend orchestrator to user-facing AI guide.**

Users don't see "MCIP published your care recommendation."
They see "🤖 Navi: Great job! Here's what I found..."

Technical excellence + friendly personality = Navi. 🤖✨

---

*"Your guide through the senior care journey."*
