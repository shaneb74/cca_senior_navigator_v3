# Navi Enhancement Proposal: MCIP-Driven Contextual Guidance

**Branch:** `feature/navi-enhancement`  
**Date:** November 2, 2025  
**Status:** Proposal (No Implementation Yet)

---

## Executive Summary

This proposal enhances Navi's contextual intelligence by deepening integration with MCIP (Master Care Intelligence Panel) data and adding page-specific coaching tailored to GCP and Cost Planner workflows. The goal is to make Navi feel more aware, helpful, and responsive to the user's specific situation at every step.

### Core Problems to Solve

1. **Generic Guidance:** Current Navi panels show similar messages regardless of user's care tier, risk flags, or financial situation
2. **Missing Context:** GCP and Cost Planner pages don't leverage known outcomes (care tier, risk flags, cost estimates) to provide targeted coaching
3. **Disconnected Intelligence:** MCIP has rich data (CareRecommendation, FinancialProfile, risk flags) but Navi doesn't fully utilize it for dynamic messaging
4. **One-Size-Fits-All:** Same encouragement/tips regardless of whether user has memory care needs vs. independent living needs

### Proposed Solution

**Phase 1: MCIP Context Integration**
- Deep integration of MCIP contracts into Navi rendering
- Dynamic message generation based on care tier, confidence, flags
- Risk-aware coaching (falls, memory, isolation, etc.)

**Phase 2: Page-Specific Intelligence**
- GCP step-aware guidance referencing previously answered questions
- Cost Planner tier-specific financial coaching
- Context-aware tips based on user's journey position

**Phase 3: Predictive Guidance**
- Next-question previews in GCP
- Financial impact foreshadowing
- Proactive flag-triggered recommendations

---

## Part 1: Current State Analysis

### 1.1 Current Navi Architecture

**Three Rendering Contexts:**

1. **Hub-level (`render_navi_panel` location="hub")**
   - Shows journey progress (0/3, 1/3, 2/3, 3/3)
   - Generic encouragement ("Let's keep going")
   - Next action recommendation (always next incomplete product)
   - Context chips with tier/cost/appointment IF available

2. **Product-level (`render_navi_panel` location="product")**
   - Module progress indicator (Step X of Y)
   - Generic coaching ("I'm here to help")
   - Uses `navi_guidance` from module.json if available

3. **Module-level (`render_module_navi_coach`)**
   - Compact panel at top of module pages
   - Single coaching line
   - Minimal styling, no Why? expansion yet

### 1.2 Current MCIP Data Available

**Rich Data Contracts:**

```python
# CareRecommendation (from GCP)
{
    "tier": "assisted_living",
    "tier_score": 68.5,
    "tier_rankings": [("assisted_living", 68.5), ("memory_care", 45.2), ...],
    "confidence": 0.92,  # 92% of questions answered
    "flags": [
        {"type": "falls_risk", "active": True, "severity": "moderate"},
        {"type": "memory_support", "active": True, "severity": "mild"},
        {"type": "limited_support", "active": True}
    ],
    "rationale": [
        "Needs assistance with bathing and dressing",
        "Recent fall history indicates safety concern",
        "Mild memory issues require monitoring"
    ]
}

# FinancialProfile (from Cost Planner)
{
    "estimated_monthly_cost": 5200,
    "coverage_percentage": 0.68,
    "gap_amount": 1664,
    "runway_months": 36,
    "confidence": 0.85
}

# AdvisorAppointment (from PFMA)
{
    "scheduled": True,
    "date": "Nov 5, 2025",
    "time": "2:00 PM",
    "type": "video",
    "prep_progress": 75
}
```

**Current Usage:** Context chips only (tier name, cost amount, appointment date)

**Opportunity:** Use flags, rationale, confidence, runway for targeted coaching

### 1.3 Current Guidance Sources

**Static Sources:**
- `core/navi_dialogue.py` - Hardcoded journey phase messages
- Module `navi_guidance` blocks in `module.json`
- Generic encouragement templates

**Dynamic Sources:**
- MCIP journey progress (completed_count)
- Next action recommendation (always next product)

**Missing:**
- Risk flag-aware messaging
- Tier-specific coaching
- Financial situation-aware guidance
- Confidence-driven reassurance

---

## Part 2: Enhancement Specifications

### 2.1 Hub-Level Enhancements

#### 2.1.1 Smart Encouragement Based on Flags

**Current:**
```python
encouragement = {
    "icon": "💪",
    "text": "You're making great progress!",
    "status": "in_progress"
}
```

**Proposed - Flag-Aware:**
```python
# If falls_risk flag active
encouragement = {
    "icon": "🛡️",
    "text": "Given the fall risk, finding the right support level is especially important.",
    "status": "urgent"
}

# If memory_support flag active
encouragement = {
    "icon": "🧠",
    "text": "Memory support options will give you peace of mind and safety.",
    "status": "important"
}

# If financial_gap flag from Cost Planner
encouragement = {
    "icon": "💡",
    "text": "We found a funding gap, but your advisor will help you close it.",
    "status": "planning"
}

# If high confidence (>90%) and low risk
encouragement = {
    "icon": "✅",
    "text": "Your plan is crystal clear—let's move forward with confidence.",
    "status": "confident"
}
```

#### 2.1.2 Context Chips Enhancement

**Current:** Shows tier, cost, appointment as plain values

**Proposed:** Add severity indicators and actionable context

```python
context_chips = [
    {
        "icon": "🧭",
        "label": "Care",
        "value": "Assisted Living",
        "sublabel": "92% confident",
        "badge": "High Confidence",  # NEW
        "badge_color": "green"  # NEW
    },
    {
        "icon": "💰",
        "label": "Cost",
        "value": "$5,200",
        "sublabel": "36 mo runway",
        "badge": "Gap: $1,664/mo",  # NEW - Shows funding gap
        "badge_color": "yellow"
    },
    {
        "icon": "🛡️",  # NEW CHIP
        "label": "Risks",
        "value": "2 active",
        "sublabel": "Falls, Memory",
        "badge": "Action Needed",
        "badge_color": "red"
    }
]
```

#### 2.1.3 Dynamic Reason Text

**Current:** Generic next action reason

**Proposed:** Personalized based on previous outcomes

```python
# After GCP with falls_risk
reason = "Now let's see what fall prevention services cost and how to fund them."

# After GCP with memory_care tier
reason = "Memory Care costs more but provides specialized support. Let's explore your options."

# After Cost Planner with funding gap
reason = "Your advisor will help you close the $1,664/month gap through VA benefits, insurance, and asset strategies."

# After all complete
reason = "You've built a complete plan. Your advisor will refine it and connect you with providers."
```

### 2.2 GCP Module Enhancements

#### 2.2.1 Step-Aware Contextual Coaching

**Current:** Generic "Answer these questions" message

**Proposed:** Reference previous answers and preview impact

**Example: Daily Living Section**
```python
# First question - generic
navi_message = "Let's start with daily activities like bathing, dressing, and mobility."

# After 2-3 answers showing high scores
navi_message = "I'm noticing significant support needs. This will likely point toward assisted care options."

# After 4-5 answers with low scores
navi_message = "So far, minimal assistance needed. In-home care or independent living may be sufficient."
```

**Example: Safety Concerns Section**
```python
# If falls_multiple already answered "yes"
navi_message = "Given the fall history, these safety questions are especially important for finding the right environment."

# If mobility questions showed high_dependence
navi_message = "Mobility challenges increase fall risk. These safety questions help us recommend proper support."
```

**Example: Cognitive Assessment Section**
```python
# If memory questions show decline
navi_message = "Memory support is critical for safety and quality of life. Be honest here—it helps us protect what matters most."

# If no cognitive flags yet
navi_message = "Cognitive function affects care level significantly. Consider recent changes, not just long-standing habits."
```

#### 2.2.2 Results Page Enhancement

**Current:** Shows tier, score, flags with generic descriptions

**Proposed:** Synthesize rationale into narrative coaching

```python
# High-confidence assisted living with falls risk
navi_message = {
    "title": "Your Plan: Assisted Living with Safety Focus",
    "body": "Based on your answers, assisted living provides the right balance of independence and support. The fall risk and mobility needs make a safe environment essential.",
    "next_step": "Let's calculate costs and explore facilities with strong safety protocols.",
    "confidence_note": "92% confidence - we have a clear picture of the needs."
}

# Low-confidence in-home care
navi_message = {
    "title": "Your Plan: In-Home Care (Preliminary)",
    "body": "In-home care looks appropriate, but we only answered 60% of key questions. More answers would refine this recommendation.",
    "next_step": "You can proceed to costs now or go back to complete the assessment.",
    "confidence_note": "60% confidence - consider answering more questions for better accuracy."
}

# Memory care with multiple flags
navi_message = {
    "title": "Your Plan: Memory Care with Specialized Support",
    "body": "Memory decline, wandering risk, and safety concerns indicate specialized memory care is needed. This level provides 24/7 supervision and cognitive programming.",
    "next_step": "Memory care costs more, but financial planning can help make it affordable.",
    "confidence_note": "95% confidence - the assessment clearly shows memory care needs."
}
```

### 2.3 Cost Planner Enhancements

#### 2.3.1 Intro Page Enhancement

**Current:** Generic "Let's look at costs" message

**Proposed:** Tier-specific financial context

```python
# Assisted living tier from GCP
navi_message = {
    "title": "Assisted Living typically costs $4,500 - $6,500/month",
    "body": "I've pre-selected Assisted Living from your Guided Care Plan. We'll calculate your specific costs based on location, room type, and care level.",
    "tip": "Memory support or medication management can add $500-1,000/month."
}

# Memory care tier from GCP
navi_message = {
    "title": "Memory Care typically costs $6,000 - $9,000/month",
    "body": "Memory Care costs more because of specialized staffing, secured environments, and cognitive programming. Let's see what you can afford.",
    "tip": "Some facilities offer shared rooms at lower rates while maintaining quality memory care."
}

# In-home care tier from GCP
navi_message = {
    "title": "In-Home Care costs vary widely by hours needed",
    "body": "From your Guided Care Plan, you need significant daily support. At 8 hours/day, expect $5,000-7,000/month depending on location.",
    "tip": "Veterans may qualify for Aid & Attendance benefits covering up to $2,431/month."
}
```

#### 2.3.2 Financial Assessment Coaching

**During income/asset collection:**

```python
# If veteran flag active from GCP
navi_message = {
    "icon": "🎖️",
    "text": "Since you're a veteran, we'll check VA Aid & Attendance eligibility—up to $2,431/month.",
    "expandable": "VA A&A Requirements",
    "details": "Must be wartime veteran, need help with daily activities, and meet income/asset limits."
}

# If high dependence but limited income
navi_message = {
    "icon": "💡",
    "text": "High care needs with limited income often qualifies for Medicaid. We'll explore this with your advisor.",
    "expandable": "Medicaid Planning",
    "details": "Medicaid covers nursing home and some assisted living. Asset spend-down strategies can help you qualify faster."
}
```

#### 2.3.3 Results Page (Expert Review) Enhancement

**Current:** Shows cost breakdown and timeline

**Proposed:** Add decision-support coaching based on runway and gap

```python
# Scenario: 36-month runway with $1,664/month gap
navi_message = {
    "title": "You have 3 years of funding, but need to close a $1,664/month gap",
    "body": "Your income covers 68% of costs. The remaining 32% will deplete assets in 36 months without additional funding.",
    "strategies": [
        "VA Aid & Attendance: Could cover up to $2,431/month (check eligibility)",
        "Long-term care insurance: Review policy benefits",
        "Medicaid planning: Start spend-down strategy now to qualify before assets run out",
        "Family contributions: Shared care costs among siblings"
    ],
    "urgency": "moderate",
    "next_step": "Your advisor will create a detailed funding strategy and connect you with resources."
}

# Scenario: 8-month runway with large gap (urgent)
navi_message = {
    "title": "⚠️ Only 8 months of funding available",
    "body": "Current assets will only cover 8 months of care. Immediate financial planning is critical.",
    "strategies": [
        "Emergency Medicaid application (if qualified)",
        "Immediate asset liquidation planning",
        "Family emergency care fund",
        "Lower-cost care options (shared rooms, in-home hybrid)"
    ],
    "urgency": "high",
    "next_step": "Schedule your advisor call ASAP to create an emergency funding plan."
}

# Scenario: 60+ month runway, full coverage
navi_message = {
    "title": "✅ Excellent financial position - 5+ years fully funded",
    "body": "Your income and assets comfortably cover all projected costs with room to spare.",
    "strategies": [
        "Quality-focused facility selection (you can afford premium options)",
        "Asset preservation strategies to extend runway further",
        "Estate planning considerations"
    ],
    "urgency": "low",
    "next_step": "Your advisor will help you choose high-quality care options within your comfortable budget."
}
```

### 2.4 Cross-Product Intelligence

#### 2.4.1 Journey Completion Coaching

**After GCP Complete, Before Cost Planner:**

```python
# Memory care tier + falls risk + veteran
navi_message = {
    "icon": "📊",
    "title": "Next: Calculate Memory Care Costs",
    "body": "Memory Care typically costs $6,000-9,000/month, but as a veteran you may qualify for up to $2,431/month in benefits.",
    "preview": "We'll check VA eligibility, review your assets, and create a funding strategy.",
    "cta": "Start Cost Planning"
}

# Assisted living + high confidence + limited support
navi_message = {
    "icon": "📊",
    "title": "Next: Explore Assisted Living Costs",
    "body": "Assisted Living averages $4,500-6,500/month in your area. We'll see what you can afford and identify funding sources.",
    "preview": "Many families discover they have more resources than expected once we map everything out.",
    "cta": "Start Cost Planning"
}
```

**After Cost Planner Complete, Before PFMA:**

```python
# Large funding gap, moderate runway
navi_message = {
    "icon": "🤝",
    "title": "Next: Schedule Your Advisor Call",
    "body": "Your advisor will create a detailed plan to close the $1,664/month gap through VA benefits, insurance, and asset strategies.",
    "preview": "Come prepared with questions about Medicaid planning, insurance claims, and facility selection.",
    "cta": "Book Appointment"
}

# Fully funded, high confidence
navi_message = {
    "icon": "🤝",
    "title": "Next: Schedule Your Advisor Call",
    "body": "You're in great financial shape. Your advisor will help you choose premium facilities and optimize your care plan.",
    "preview": "Focus on quality, amenities, and location—you have options.",
    "cta": "Book Appointment"
}
```

---

## Part 3: Technical Implementation Strategy

### 3.1 Data Flow Enhancement

**Current Flow:**
```
MCIP.get_care_recommendation() 
    → NaviContext
    → Generic message template
    → Render
```

**Proposed Flow:**
```
MCIP (The Brain):
    - Calculates flags, tier, confidence
    - Publishes CareRecommendation contract
        ↓
NaviContext:
    - Receives MCIP's published contracts
    - Does NOT calculate anything
        ↓
NaviCommunicator (The Translator):
    - READS flags/tier/confidence from NaviContext
    - Selects appropriate user-facing message
    - NEVER modifies or calculates intelligence
        ↓
Navi UI:
    - Renders the selected message
```

**Critical Boundary:**
- MCIP = Intelligence creation (the brain)
- Navi = Intelligence consumption and communication (the translator)
- Navi UI = Message presentation (the display)

### 3.2 Architectural Separation: MCIP vs. Navi

**Critical Principle:** MCIP (Multi-Contextual Intelligence Panel) is the brain and coordinator. Navi is the consumer that uses MCIP's intelligence to communicate with users.

**Why "Multi-Contextual":** MCIP is the only system with cross-boundary visibility—it sees across GCP assessment context, Cost Planner financial context, PFMA advisor context, and journey progression context. While each product owns its domain, MCIP coordinates intelligence across these boundaries.

```
┌─────────────────────────────────────────────────────────────┐
│          MCIP (The Multi-Contextual Brain)                   │
│  • Calculates all flags from GCP answers                    │
│  • Runs deterministic scoring rules                         │
│  • Evaluates care tiers and confidence                      │
│  • Publishes standardized contracts (CareRecommendation)    │
│  • OWNS all intelligence about user's care needs            │
│  • Cross-boundary visibility across all product contexts    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Publishes contracts
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Navi Intelligence (The Communicator)            │
│  • READS flags/outcomes from MCIP                           │
│  • Selects appropriate coaching messages                    │
│  • Prioritizes which context to emphasize                   │
│  • Generates user-facing dialogue                           │
│  • NEVER calculates flags or modifies intelligence          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Navi UI Layer                             │
│  • Renders coaching panels                                  │
│  • Displays messages from Navi Intelligence                 │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 New Communication Functions

```python
# core/navi_intelligence.py (NEW FILE)

class NaviCommunicator:
    """
    Navi's communication layer - consumes MCIP intelligence and presents it to users.
    
    NEVER calculates flags or determines care needs - only reads from MCIP.
    """
    
    @staticmethod
    def get_hub_encouragement(ctx: NaviContext) -> dict:
        """Generate flag-aware encouragement by reading MCIP's published flags.
        
        Reads from:
        - ctx.care_recommendation.flags (published by MCIP)
        - ctx.care_recommendation.tier (calculated by MCIP)
        - ctx.financial_profile (published by Cost Planner via MCIP)
        
        Returns: User-facing encouragement message
        
        Priority order:
        1. Urgent flags (falls + memory + multiple risks)
        2. Financial urgency (low runway from MCIP)
        3. High confidence + low risk (positive reinforcement)
        4. Generic progress encouragement
        """
        # Read flags from MCIP (never calculate them)
        flags = ctx.care_recommendation.flags if ctx.care_recommendation else []
        
        # Message selection logic (presentation layer only)
        has_falls_risk = any(f['type'] == 'falls_risk' and f.get('active') for f in flags)
        has_memory_support = any(f['type'] == 'memory_support' and f.get('active') for f in flags)
        
        # ... select appropriate message based on MCIP's intelligence
        
    @staticmethod
    def get_gcp_step_coaching(step_id: str, ctx: NaviContext) -> dict:
        """Generate step-aware coaching by reading GCP progress from MCIP.
        
        Reads from:
        - MCIP's published partial assessment state
        - Cumulative score patterns (if MCIP exposes them)
        
        Returns: Step-specific coaching message
        """
        
    @staticmethod
    def get_cost_planner_intro(ctx: NaviContext) -> dict:
        """Generate tier-specific intro by reading MCIP's care recommendation.
        
        Reads from:
        - ctx.care_recommendation.tier (MCIP's published tier)
        - ctx.care_recommendation.flags (MCIP's published flags)
        
        Returns: Tier-specific financial context message
        """
        tier = ctx.care_recommendation.tier if ctx.care_recommendation else None
        flags = ctx.care_recommendation.flags if ctx.care_recommendation else []
        
        # Map MCIP's tier to user-facing cost expectations
        # ... message generation logic
        
    @staticmethod
    def get_financial_strategy_advice(ctx: NaviContext) -> dict:
        """Generate funding strategy by reading MCIP's financial profile.
        
        Reads from:
        - ctx.financial_profile.runway_months (MCIP's calculation)
        - ctx.financial_profile.gap_amount (MCIP's calculation)
        - ctx.care_recommendation.flags (veteran status, etc.)
        
        Returns: Funding strategy coaching message
        
        Urgency mapping:
        - Critical: runway < 12 months (from MCIP)
        - Urgent: runway 12-24 months
        - Moderate: runway 24-48 months
        - Comfortable: runway 48+ months
        """
        
    @staticmethod
    def get_next_product_preview(ctx: NaviContext) -> dict:
        """Generate next product preview by reading MCIP's journey state.
        
        Reads from:
        - ctx.progress (MCIP's journey coordination)
        - ctx.next_action (MCIP's recommendation)
        - ctx.care_recommendation (for context)
        
        Returns: Preview message with personalized context
        """
```

### 3.4 Responsibilities Matrix

| Responsibility | MCIP | Navi Communicator | Navi UI |
|---|---|---|---|
| Calculate flags from GCP answers | ✅ Yes | ❌ Never | ❌ No |
| Evaluate care tier | ✅ Yes | ❌ Never | ❌ No |
| Calculate financial runway | ✅ Yes | ❌ Never | ❌ No |
| Store journey state | ✅ Yes | ❌ No | ❌ No |
| Publish standardized contracts | ✅ Yes | ❌ No | ❌ No |
| Read published contracts | ➖ N/A | ✅ Yes | ❌ No |
| Select coaching message | ❌ No | ✅ Yes | ❌ No |
| Prioritize multiple flags | ❌ No | ✅ Yes | ❌ No |
| Generate user-facing text | ❌ No | ✅ Yes | ❌ No |
| (Optional) Enhance with LLM | ❌ No | ✅ Yes | ❌ No |
| Render coaching panel | ❌ No | ❌ No | ✅ Yes |

**Key Insight:** Navi Intelligence is purely a **presentation/communication layer** that translates MCIP's technical intelligence into user-friendly coaching. It NEVER creates or modifies the underlying intelligence.

### 3.3 Module JSON Enhancement

**Add `dynamic_guidance` blocks:**

```json
{
  "sections": [
    {
      "id": "daily_living",
      "dynamic_guidance": {
        "trigger_conditions": [
          {
            "when": "bathing='full_help' AND dressing='full_help'",
            "message": "Significant daily support needs—this points toward assisted care.",
            "icon": "🛁"
          },
          {
            "when": "bathing='no_help' AND dressing='no_help'",
            "message": "Strong independence with daily activities so far.",
            "icon": "✅"
          }
        ],
        "cumulative_score_guidance": {
          "high": "High support needs emerging—assisted living likely appropriate.",
          "medium": "Moderate needs—in-home care or assisted living possible.",
          "low": "Low support needs—independent living or minimal in-home care likely sufficient."
        }
      }
    }
  ]
}
```

### 3.5 Integration with Existing Navi Rendering

**Minimal changes to existing UI:**

```python
# core/navi.py - render_navi_panel()

# BEFORE
encouragement = {
    "icon": "💪",
    "text": "You're making great progress!",
    "status": "in_progress"
}

# AFTER - call Navi Communicator (reads from MCIP)
from core.navi_intelligence import NaviCommunicator

encouragement = NaviCommunicator.get_hub_encouragement(ctx)
# ctx.care_recommendation comes from MCIP (already calculated)
# NaviCommunicator just reads it and selects appropriate message
# Returns: {"icon": "🛡️", "text": "Given the fall risk...", "status": "urgent"}
```

**No UI component changes needed** - just smarter content generation using MCIP's intelligence

### 3.6 Optional: LLM Enhancement Layer

Since Navi is the communication layer, this is where LLM enhancement can optionally happen:

```python
class NaviCommunicator:
    @staticmethod
    def get_hub_encouragement(ctx: NaviContext) -> dict:
        """Generate encouragement - optionally enhanced with LLM."""
        
        # Read MCIP's intelligence (source of truth)
        flags = ctx.care_recommendation.flags if ctx.care_recommendation else []
        tier = ctx.care_recommendation.tier if ctx.care_recommendation else None
        
        # Generate base message (deterministic)
        base_message = _select_message_from_template(flags, tier)
        
        # Optional: Enhance with LLM (if feature flag enabled)
        if FEATURE_LLM_NAVI in ["assist", "adjust"]:
            # LLM reads same MCIP data and humanizes the message
            enhanced = NaviLLMEngine.humanize_message(
                base_message=base_message,
                mcip_context={
                    "tier": tier,
                    "flags": flags,
                    "confidence": ctx.care_recommendation.confidence
                }
            )
            # LLM makes it warmer/clearer but doesn't change the facts
            return enhanced
        
        return base_message
```

**Key Principle:** LLM layer (if used) ALSO reads from MCIP, never calculates intelligence. It's just another consumer making the communication more human.

---

## Part 4: Phased Rollout Plan

### Phase 1: Foundation (Week 1)
**Goal:** Infrastructure for MCIP-driven communication

- [ ] Create `core/navi_intelligence.py`
- [ ] Add `NaviCommunicator` class (reads from MCIP, never calculates)
- [ ] Implement stub methods that consume MCIP contracts
- [ ] Wire into `render_navi_panel()` with feature flag
- [ ] Test with existing static messages (no behavior change)
- [ ] Document MCIP → Navi data flow clearly

**Validation:** 
- No visual changes
- NaviCommunicator successfully reads MCIP contracts
- All methods receive NaviContext (with MCIP data) as input
- No flag calculation logic in Navi layer

### Phase 2: Hub Enhancement (Week 1-2)
**Goal:** Smart hub lobby Navi

- [ ] Implement `get_hub_encouragement()` with flag awareness
- [ ] Add context chip badges (confidence, urgency, gaps)
- [ ] Implement `get_next_product_preview()` with outcomes
- [ ] Add dynamic reason text based on previous products

**Validation:** Hub Navi shows different messages for different flag/tier combinations

### Phase 3: GCP Enhancement (Week 2-3)
**Goal:** Step-aware GCP coaching

- [ ] Implement `get_gcp_step_coaching()` with answer analysis
- [ ] Add cumulative score patterns ("high needs emerging...")
- [ ] Enhance results page with narrative synthesis
- [ ] Add "Why this question?" expansions referencing previous answers

**Validation:** GCP Navi adapts messages as user progresses through assessment

### Phase 4: Cost Planner Enhancement (Week 3-4)
**Goal:** Financial intelligence

- [ ] Implement `get_cost_planner_intro()` with tier-specific costs
- [ ] Add `get_financial_strategy_advice()` with runway urgency
- [ ] Enhance expert review with decision-support coaching
- [ ] Add flag-specific financial tips (veteran benefits, Medicaid)

**Validation:** Cost Planner Navi shows relevant strategies based on funding situation

### Phase 5: Polish & Testing (Week 4)
**Goal:** Refinement and edge cases

- [ ] Handle low-confidence scenarios
- [ ] Handle incomplete data gracefully
- [ ] Add debug mode showing which intelligence rules fired
- [ ] User testing and message refinement

---

## Part 5: Success Metrics

### Qualitative Metrics
- User feedback: "Navi understands my situation"
- Perceived helpfulness ratings
- Reduced confusion/questions in user testing

### Quantitative Metrics
- **Completion rates:** Do more users complete GCP + Cost Planner?
- **Time on task:** Does better guidance reduce time spent?
- **Confidence scores:** Do users answer more GCP questions (higher confidence)?
- **Advisor prep quality:** Do users arrive better prepared?

### A/B Testing Scenarios
- Control: Current generic Navi
- Treatment: Enhanced context-aware Navi
- Measure: Completion rates, time to completion, user satisfaction

---

## Part 6: Edge Cases & Considerations

### 6.1 Missing Data Handling

**Scenario:** User skips GCP, goes straight to Cost Planner

**Current:** Cost Planner blocks them (GCP gate)

**With Enhancement:** If gate removed, show generic financial guidance

```python
if not ctx.care_recommendation:
    message = "We'll explore costs for different care levels since you haven't done the Guided Care Plan yet."
else:
    message = f"Based on your {tier} recommendation, here's what to expect..."
```

### 6.2 Low Confidence Scenarios

**Scenario:** User answers only 40% of GCP questions

**Enhancement:** Flag low confidence and encourage completion

```python
if confidence < 0.6:
    navi_message = {
        "icon": "⚠️",
        "text": "We only have 40% of the picture. More answers = better recommendations.",
        "badge": "Low Confidence",
        "cta": "Complete Assessment"
    }
```

### 6.3 Conflicting Signals

**Scenario:** Low scores (independent) but has falls_risk flag

**Enhancement:** Acknowledge contradiction and explain

```python
navi_message = {
    "text": "Daily activities look manageable, but fall risk is a concern. In-home care with safety focus may be ideal.",
    "rationale": "Independence is important, but safety comes first."
}
```

### 6.4 Feature Flag Control

**All enhancements behind feature flag:**

```python
FEATURE_NAVI_INTELLIGENCE = os.getenv("FEATURE_NAVI_INTELLIGENCE", "off")
# off | shadow | on

if FEATURE_NAVI_INTELLIGENCE == "on":
    # Use enhanced intelligence
    encouragement = NaviIntelligenceEngine.get_hub_encouragement(ctx)
elif FEATURE_NAVI_INTELLIGENCE == "shadow":
    # Log enhanced messages but show original
    enhanced = NaviIntelligenceEngine.get_hub_encouragement(ctx)
    print(f"[NAVI_SHADOW] Enhanced: {enhanced}")
    encouragement = original_static_message
else:
    # Original behavior
    encouragement = original_static_message
```

---

## Part 7: Example Scenarios

### Scenario A: High-Risk Memory Care Case

**GCP Outcomes:**
- Tier: memory_care
- Confidence: 0.94
- Flags: memory_support (severe), wandering_risk, falls_risk
- Rationale: "Significant memory decline, wandering episodes, safety concerns"

**Hub Navi (After GCP):**
```
Icon: 🧠
Title: "Memory Care is the safest option for these needs"
Body: "With memory decline, wandering risk, and falls, specialized memory care provides 24/7 supervision and cognitive support."
Encouragement: "This level of care protects safety and dignity—let's see how to make it affordable."
Next Action: "Calculate Memory Care Costs →"
```

**Cost Planner Intro Navi:**
```
Icon: 🏥
Title: "Memory Care typically costs $6,000-9,000/month"
Body: "I've pre-selected Memory Care from your Guided Care Plan. Specialized staffing and secured environments cost more, but financial planning can help."
Tip: "Veterans may qualify for up to $2,431/month in Aid & Attendance benefits to offset costs."
```

**Expert Review Navi (18-month runway, $2,200/month gap):**
```
Icon: ⏰
Title: "⚠️ 18 months of funding - Urgent planning needed"
Body: "Current assets will cover 18 months. We need to act now to extend your runway."
Strategies:
  - "Apply for VA Aid & Attendance immediately ($2,431/mo)"
  - "Medicaid planning: Start spend-down strategy now"
  - "Review long-term care insurance policy"
Urgency: HIGH
Next Step: "Schedule advisor call ASAP to implement funding strategy."
```

### Scenario B: Independent Living, Low Risk

**GCP Outcomes:**
- Tier: independent
- Confidence: 0.88
- Flags: None
- Rationale: "Strong independence, no safety concerns, active lifestyle"

**Hub Navi (After GCP):**
```
Icon: ✅
Title: "Independent Living looks like a great fit"
Body: "Strong independence with no major safety concerns. Independent living offers community and services while preserving autonomy."
Encouragement: "You're in great shape—let's see what this costs and plan ahead."
Next Action: "Calculate Costs →"
```

**Cost Planner Intro Navi:**
```
Icon: 🏘️
Title: "Independent Living typically costs $2,500-4,000/month"
Body: "Much more affordable than assisted care. You're paying for community, meals, and activities—not daily care."
Tip: "Focus on location and amenities since care needs are minimal."
```

**Expert Review Navi (72-month runway, fully covered):**
```
Icon: 🎉
Title: "✅ Excellent financial position - 6+ years fully funded"
Body: "Your income covers all costs with plenty of runway. You can focus on quality and location."
Strategies:
  - "Premium facility options within comfortable budget"
  - "Asset preservation to extend runway further"
  - "Estate planning for remaining assets"
Urgency: LOW
Next Step: "Your advisor will help you tour top-rated communities in your preferred area."
```

### Scenario C: Veteran with Assisted Living Needs

**GCP Outcomes:**
- Tier: assisted_living
- Confidence: 0.91
- Flags: veteran_aanda_risk, falls_risk, limited_support
- Rationale: "Needs help with bathing/dressing, fall history, lives alone"

**Hub Navi (After GCP):**
```
Icon: 🎖️
Title: "Assisted Living with VA benefits"
Body: "As a wartime veteran with care needs, you may qualify for Aid & Attendance—up to $2,431/month toward assisted living costs."
Encouragement: "Your service earned these benefits—let's make sure you get them."
Next Action: "Calculate Costs & Check Eligibility →"
```

**Cost Planner Intro Navi:**
```
Icon: 🎖️
Title: "Assisted Living: $4,500-6,500/month (before VA benefits)"
Body: "I've pre-selected Assisted Living. We'll check your VA Aid & Attendance eligibility—this could reduce your out-of-pocket costs significantly."
Tip: "VA benefits stack with other income sources. We'll map everything out."
```

**Expert Review Navi (36-month runway, $1,200/month gap BEFORE VA benefits):**
```
Icon: 🎖️
Title: "VA Aid & Attendance could eliminate your funding gap"
Body: "Before benefits: $1,200/month gap, 36-month runway. With maximum A&A ($2,431/mo): FULLY COVERED with surplus."
Strategies:
  - "Priority 1: Apply for VA Aid & Attendance immediately"
  - "If approved: Choose premium facility within your new budget"
  - "If denied: Backup Medicaid planning strategy"
Urgency: MODERATE
Next Step: "Your advisor will help you file the VA claim and choose facilities that accept VA benefits."
```

---

## Part 8: Non-Goals (Out of Scope)

### What This Proposal Does NOT Include:

1. **Flag Calculation in Navi:** Navi NEVER calculates flags—that's MCIP's job
   - All intelligence (flags, tier, confidence) comes from MCIP
   - Navi only reads and communicates MCIP's published data
   - Clear architectural boundary maintained

2. **LLM/AI Generation (Phase 1):** Sticking with deterministic message selection for v1
   - AI enhancement can come later as optional layer
   - AI would also read from MCIP (another consumer)
   - Current proposal: Template-based communication reading MCIP contracts

3. **UI Component Redesign:** Using existing Navi panel designs
   - No new visual components
   - Only enhanced content and badges

4. **New Data Collection:** Only using existing MCIP contracts
   - Not adding new questions or assessment steps
   - Not changing GCP/Cost Planner flows
   - Not creating new intelligence—just better communication

5. **Conversational Chat:** Still not building a chatbot
   - Navi remains a coaching panel, not a chat interface
   - FAQ product handles Q&A separately

6. **Real-Time Learning:** Not tracking user behavior patterns
   - Each session is independent
   - No cross-user learning or personalization beyond current session

7. **MCIP Intelligence Modification:** Navi cannot change MCIP's published data
   - Read-only access to MCIP contracts
   - Cannot recalculate tiers or flags
   - Cannot override confidence scores

---

## Part 9: Open Questions & Decisions Needed

### 9.1 Tone & Voice

**Question:** How directive should Navi be?

**Options:**
- **Supportive:** "You might consider..." / "Many families find..."
- **Directive:** "You should..." / "The best option is..."
- **Collaborative:** "Let's explore..." / "We recommend..."

**Recommendation:** Collaborative + Directive for urgent situations
- Default: "Let's see what this costs and create a plan."
- Urgent (low runway): "Schedule your advisor call immediately to avoid running out of funds."

### 9.2 Flag Visibility

**Question:** Should we explicitly show risk flags in Navi, or reference them subtly?

**Options:**
- **Explicit:** "⚠️ Active Risks: Falls, Memory, Isolation"
- **Subtle:** "Given the safety concerns and memory support needs..."
- **Hybrid:** Explicit in hub chips, subtle in coaching text

**Recommendation:** Hybrid approach
- Hub: Show risk chip with count ("2 active risks")
- Coaching: Reference implications, not raw flag names

### 9.3 Cost Preview Accuracy

**Question:** Should GCP show cost ranges before Cost Planner?

**Risk:** Inaccurate estimates could mislead users

**Options:**
- **Generic ranges:** "Assisted Living: $4,500-6,500/month nationally"
- **Region-specific:** "Assisted Living in [user's state]: $5,200-6,800/month"
- **No preview:** Wait until Cost Planner for any cost discussion

**Recommendation:** Generic ranges with disclaimer
- "National average: $4,500-6,500/month. Your personalized estimate comes next."

### 9.4 Confidence Thresholds

**Question:** What confidence level triggers "low confidence" warnings?

**Options:**
- <50%: Very aggressive (warns even with half complete)
- <60%: Moderate (recommended)
- <70%: Conservative (warns unless mostly complete)

**Recommendation:** 60% threshold with soft messaging
- 40-60%: "More answers = better recommendation. You can continue or go back."
- <40%: "We need more information to give you a reliable recommendation."

---

## Part 10: Success Criteria for Launch

### Must-Have (P0)
- [ ] Hub Navi shows different encouragement based on flags (3+ variations working)
- [ ] GCP results page has tier-specific narrative coaching
- [ ] Cost Planner intro references GCP tier with cost context
- [ ] Feature flag controls all enhancements
- [ ] Graceful degradation when MCIP data missing

### Should-Have (P1)
- [ ] Context chips show confidence badges and urgency indicators
- [ ] Expert Review shows funding strategy advice based on runway
- [ ] Next product preview includes outcome-based context
- [ ] Low-confidence scenarios have appropriate warnings

### Nice-to-Have (P2)
- [ ] GCP step-by-step coaching references previous answers
- [ ] Veteran benefits callouts in Cost Planner when flag active
- [ ] Risk flag chip in hub showing count and types
- [ ] Debug mode showing which intelligence rules fired

### Testing Checklist
- [ ] Memory care + falls + veteran path end-to-end
- [ ] Independent living + low risk + fully funded path
- [ ] Assisted living + funding gap + moderate runway path
- [ ] Edge case: Low confidence (<60%) GCP completion
- [ ] Edge case: Cost Planner without GCP completion
- [ ] Edge case: No MCIP data available (new user)

---

## Part 11: Timeline & Resources

### Estimated Effort
- **Phase 1 (Infrastructure):** 2-3 days
- **Phase 2 (Hub Enhancement):** 3-4 days
- **Phase 3 (GCP Enhancement):** 4-5 days
- **Phase 4 (Cost Planner Enhancement):** 3-4 days
- **Phase 5 (Polish & Testing):** 3-4 days

**Total:** ~3-4 weeks for complete implementation

### Dependencies
- No external dependencies
- Uses existing MCIP contracts
- No UI framework changes needed
- Feature flag system already in place

### Risk Factors
- **Low Risk:** Infrastructure changes are minimal
- **Medium Risk:** Message quality requires user testing
- **Low Risk:** Feature flag allows safe rollback

---

## Conclusion

This enhancement makes Navi a more effective communicator of MCIP's intelligence without violating architectural boundaries. By maintaining clear separation—MCIP (Multi-Contextual Intelligence Panel) as the brain that calculates intelligence across all contexts, Navi as the translator that communicates it—we preserve system integrity while dramatically improving user experience.

**Core Value Proposition:**
> "Navi that reads your care intelligence from MCIP and explains it clearly—understanding your care tier, your risks, your financial situation, and coaching you specifically for YOUR journey—not a generic template."

**Architectural Principle:**
> "MCIP (Multi-Contextual Intelligence Panel) is the brain with cross-boundary visibility. Navi is the consumer that reads MCIP's intelligence and communicates it to users through (optionally LLM-enhanced) dialogue."

**Clean Separation:**
- **MCIP owns:** Flag calculation, tier determination, confidence scoring, financial analysis across all contexts
- **Navi owns:** Message selection, communication strategy, user-facing dialogue, (optional) LLM enhancement
- **Navi UI owns:** Visual presentation, panel rendering, styling

**Why "Multi-Contextual":**
MCIP is the only system that sees across boundaries—GCP assessment context, Cost Planner financial context, PFMA advisor context, journey progression context. This cross-contextual intelligence is what enables personalized, situation-aware guidance throughout the user's journey.

**Next Steps:**
1. Review and approve this proposal
2. Refine tone/voice guidelines (Section 9.1)
3. Begin Phase 1 implementation (NaviCommunicator infrastructure)
4. Create message library that maps MCIP states → user messages
5. Document MCIP contract → Navi message mappings
6. Test with various MCIP contract combinations

---

**End of Proposal**
