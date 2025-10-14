# MCIP User Guidance System

**Status:** ✅ Complete  
**Date:** October 14, 2025  
**Purpose:** Make MCIP actively guide users through their journey with dynamic, contextual messaging

---

## Overview

MCIP v2.1 adds **User Guidance** - transforming MCIP from silent backend orchestrator into active journey guide that tells users what to do next and shows dynamic product summaries.

### The Problem

- MCIP orchestrated products but didn't **guide users**
- Product tiles were static, showing the same info regardless of progress
- Users didn't know what to do next or where they were in the journey
- No visible journey progress indicator

### The Solution

Added three new MCIP methods that make it **user-facing**:

1. **`get_recommended_next_action()`** - Tells users what to do next
2. **`get_product_summary()`** - Dynamic tile summaries from MCIP contracts
3. **`render_mcip_journey_status()`** - Visible journey progress banner

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCIP User Guidance                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  get_recommended_next_action()                       │  │
│  │  → Returns: action, reason, route, status            │  │
│  │  → "🧭 Create Your Guided Care Plan"                 │  │
│  │  → "💰 Calculate Your Care Costs"                    │  │
│  │  → "📅 Schedule Your Advisor Appointment"            │  │
│  │  → "🎉 Journey Complete!"                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  get_product_summary(product_key)                    │  │
│  │  → Returns: title, status, summary_line, icon        │  │
│  │  → "✅ Assisted Living (85% confidence)"             │  │
│  │  → "✅ $4,500/month (30 month runway)"               │  │
│  │  → "✅ Phone Appt - Oct 20"                          │  │
│  │  → "🔒 Complete Guided Care Plan first"              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  render_mcip_journey_status()                        │  │
│  │  → Visible banner showing progress                   │  │
│  │  → "Hey Shane! 1/3 complete. Next: Calculate costs" │  │
│  │  → Color-coded by status (purple/blue/amber/green)  │  │
│  │  → Click to navigate to recommended next            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## New MCIP Methods

### 1. `get_recommended_next_action()`

**Purpose:** Tell users what to do next in plain English

**Returns:**
```python
{
    "action": "🧭 Create Your Guided Care Plan",
    "reason": "Get a personalized care recommendation based on your needs.",
    "route": "gcp_v4",
    "status": "getting_started"  # getting_started | in_progress | nearly_there | complete
}
```

**Journey Phases:**

| Completed Products | Status | Action | Icon |
|-------------------|--------|--------|------|
| None | `getting_started` | Create Your Guided Care Plan | 🧭 |
| GCP | `in_progress` | Calculate Your Care Costs | 💰 |
| GCP + Cost Planner | `nearly_there` | Schedule Your Advisor Appointment | 📅 |
| All 3 | `complete` | Journey Complete! | 🎉 |

**Personalization:**
- Includes user name if authenticated: "Hey Shane! 1/3 complete..."
- Shows progress fraction: "1/3 complete", "2/3 complete"
- Provides clear reason for each action

---

### 2. `get_product_summary(product_key)`

**Purpose:** Generate dynamic tile summaries from MCIP contracts

**Returns:**
```python
{
    "title": "Guided Care Plan",
    "status": "complete",  # not_started | unlocked | locked | complete
    "summary_line": "✅ Assisted Living (85% confidence)",
    "icon": "🧭",
    "route": "gcp_v4"
}
```

**Product Summaries:**

#### GCP (Guided Care Plan)
- **Complete:** `"✅ Assisted Living (85% confidence)"`
- **Not Started:** `"Get your personalized care recommendation"`
- **Data Source:** `MCIP.get_care_recommendation()` → tier, tier_score

#### Cost Planner
- **Complete:** `"✅ $4,500/month (30 month runway)"`
- **Unlocked:** `"Calculate your care costs"`
- **Locked:** `"🔒 Complete Guided Care Plan first"`
- **Data Source:** `MCIP.get_financial_profile()` → estimated_monthly_cost, runway_months

#### PFMA (Plan with My Advisor)
- **Complete:** `"✅ Phone Appt - Oct 20"`
- **Unlocked:** `"Schedule your advisor appointment"`
- **Locked:** `"🔒 Complete Cost Planner first"`
- **Data Source:** `MCIP.get_advisor_appointment()` → type, date

---

### 3. `render_mcip_journey_status()`

**Purpose:** Visible journey progress banner with personalized guidance

**UI Component:** Renders colorful banner at top of hub

**Features:**
- **Personalized Greeting:** Uses auth name if available
- **Progress Indicator:** Shows "1/3", "2/3", or "Complete"
- **Status Colors:**
  - Purple (#8b5cf6): Getting started
  - Blue (#3b82f6): In progress
  - Amber (#f59e0b): Nearly there
  - Green (#10b981): Complete
- **Click to Navigate:** Button to go to recommended next product

**Example Renderings:**

```
┌──────────────────────────────────────────────────────────┐
│ 🧭  Hey Shane! Create Your Guided Care Plan         0/3  │
│     Get a personalized care recommendation               │
│     [→ Create Your Guided Care Plan]                     │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ 💰  Hey Shane! 1/3 complete. Calculate Your Care Costs   │
│     Understand the financial side of your care plan 1/3  │
│     [→ Calculate Your Care Costs]                        │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ 📅  2/3 complete. Schedule Your Advisor Appointment  2/3 │
│     Meet with an advisor to finalize your plan           │
│     [→ Schedule Your Advisor Appointment]                │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ 🎉  Journey Complete!                                    │
│     You've completed your care plan, cost analysis, and  │
│     scheduled your advisor appointment.                  │
└──────────────────────────────────────────────────────────┘
```

---

## Implementation Files

### Modified: `core/mcip.py`

**Added Methods:**
- `get_recommended_next_action()` - 50 lines
- `get_product_summary()` - 120 lines (handles all 3 products)

**Logic:**
- Reads journey state (`completed_products`)
- Pulls data from MCIP contracts (CareRecommendation, FinancialProfile, AdvisorAppointment)
- Generates user-friendly messages
- Determines lock/unlock state for tiles

### Modified: `core/ui.py`

**Added Function:**
- `render_mcip_journey_status()` - 80 lines

**Features:**
- Imports MCIP and state for personalization
- Color-coded gradient backgrounds
- Responsive flexbox layout
- Navigation button integration

---

## Usage Examples

### In Concierge Hub (Phase 4)

```python
from core.ui import render_mcip_journey_status
from core.mcip import MCIP

def render():
    """Concierge Hub with MCIP guidance."""
    
    # Show journey status banner at top
    render_mcip_journey_status()
    
    # Render product tiles with dynamic summaries
    for product_key in ["gcp_v4", "cost_v2", "pfma_v2"]:
        summary = MCIP.get_product_summary(product_key)
        
        if summary:
            render_product_tile(
                title=summary["title"],
                icon=summary["icon"],
                description=summary["summary_line"],
                route=summary["route"],
                locked=(summary["status"] == "locked")
            )
```

### In Product Pages

```python
from core.mcip import MCIP

def render():
    """Product page with contextual messaging."""
    
    # Show where user is in journey
    next_action = MCIP.get_recommended_next_action()
    
    if next_action["status"] == "complete":
        st.success("🎉 Journey complete! You've finished all products.")
    else:
        st.info(f"After this: {next_action['action']}")
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        User Journey                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCIP State Storage                        │
│  • care_recommendation (CareRecommendation)                  │
│  • financial_profile (FinancialProfile)                      │
│  • advisor_appointment (AdvisorAppointment)                  │
│  • journey.completed_products = ["gcp", "cost_planner"]      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                MCIP Guidance Methods                         │
│  get_recommended_next_action()                               │
│    → Reads: completed_products                               │
│    → Returns: "💰 Calculate Your Care Costs"                 │
│                                                              │
│  get_product_summary("cost_v2")                              │
│    → Reads: financial_profile contract                       │
│    → Returns: "✅ $4,500/month (30 month runway)"            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    UI Components                             │
│  render_mcip_journey_status()                                │
│    → Banner: "Hey Shane! 1/3 complete. Next: Calculate..."  │
│                                                              │
│  Concierge Hub Product Tiles                                 │
│    → GCP: "✅ Assisted Living (85% confidence)"              │
│    → Cost: "✅ $4,500/month (30 month runway)"               │
│    → PFMA: "🔒 Complete Cost Planner first"                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Benefits

### 1. **Active User Guidance**
- MCIP tells users exactly what to do next
- No more guessing about journey progression
- Clear calls-to-action at every stage

### 2. **Dynamic Product Tiles**
- Tiles show REAL data from MCIP contracts
- Summary changes based on completion state
- Lock/unlock state managed by MCIP

### 3. **Visible Progress**
- Journey status banner shows "1/3", "2/3" complete
- Color-coded by phase (purple → blue → amber → green)
- Personalized with user name

### 4. **Product-Agnostic Hub**
- Hub doesn't need to know product details
- Reads everything from MCIP
- Easy to add new products later

### 5. **Better UX**
- Users always know where they are
- Clear next steps at every point
- Sense of accomplishment as journey progresses

---

## Testing Checklist

### Guidance Messages

- [ ] Fresh session shows "🧭 Create Your Guided Care Plan"
- [ ] After GCP shows "💰 Calculate Your Care Costs"
- [ ] After Cost Planner shows "📅 Schedule Your Advisor Appointment"
- [ ] After PFMA shows "🎉 Journey Complete!"
- [ ] User name appears in greeting if authenticated
- [ ] Progress fraction shows correctly (1/3, 2/3)

### Product Summaries

#### GCP Tile
- [ ] Not started: Shows "Get your personalized care recommendation"
- [ ] Complete: Shows "✅ Assisted Living (85% confidence)"
- [ ] Tier name formatted correctly (no underscores)
- [ ] Confidence percentage calculated from tier_score

#### Cost Planner Tile
- [ ] Locked: Shows "🔒 Complete Guided Care Plan first"
- [ ] Unlocked: Shows "Calculate your care costs"
- [ ] Complete: Shows "✅ $4,500/month (30 month runway)"
- [ ] Handles zero runway: Shows "Review needed"

#### PFMA Tile
- [ ] Locked: Shows "🔒 Complete Cost Planner first"
- [ ] Unlocked: Shows "Schedule your advisor appointment"
- [ ] Complete: Shows "✅ Phone Appt - Oct 20"
- [ ] Appointment type formatted correctly (Phone/Video/In-Person)

### Journey Status Banner
- [ ] Banner renders with correct color for each phase
- [ ] Icon matches current phase (🧭/💰/📅/🎉)
- [ ] Progress badge shows on right (hidden when complete)
- [ ] Button navigates to correct product
- [ ] Banner responsive on mobile

---

## Next Steps

### Phase 4: Update Concierge Hub
1. Import `render_mcip_journey_status()` and call at top
2. Replace product tile generation with `MCIP.get_product_summary()`
3. Update routes to point to v2 products (gcp_v4, cost_v2, pfma_v2)
4. Remove legacy handoff reads
5. Hub becomes fully polymorphic - reads everything from MCIP

### Phase 5: E2E Testing
Test complete flow with new guidance system:
- Verify guidance messages update at each step
- Check product tiles show correct summaries
- Ensure journey banner displays progress
- Confirm navigation buttons work
- Test with/without authentication

---

## Code Statistics

**Lines Added:**
- `core/mcip.py`: +170 lines (2 new methods)
- `core/ui.py`: +80 lines (1 new component)
- Total: **+250 lines**

**Files Modified:** 2  
**New Components:** 3 (2 methods, 1 UI component)

---

## Conclusion

MCIP v2.1 transforms the system from **backend orchestrator** to **active journey guide**. Users now see:

1. **What to do next** - Clear guidance at every step
2. **Where they are** - Visible progress indicator
3. **What they've accomplished** - Dynamic tile summaries with real data

The hub can now be fully polymorphic - it doesn't need product-specific logic, just reads from MCIP and displays what it finds.

**Status:** ✅ Ready to integrate into Concierge Hub (Phase 4)
