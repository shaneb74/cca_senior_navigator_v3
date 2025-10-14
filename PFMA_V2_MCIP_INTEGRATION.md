# PFMA v2 - MCIP Integration

**Status:** ✅ Complete  
**Date:** October 14, 2025  
**Files:** `products/pfma_v2/product.py`  
**Route:** `?page=pfma_v2`

---

## Overview

**PFMA v2 (Plan with My Advisor)** is the third and final product in the core journey trio, completing the user's transition from self-guided planning to advisor consultation.

### Journey Position

```
GCP v4 → Cost Planner v2 → PFMA v2
   ↓           ↓              ↓
Understand   Understand    Execute
Care Needs   Finances      The Plan
```

**Purpose:** Bridge the gap between self-service planning and professional guidance by:
1. Booking advisor appointments
2. Verifying all gathered information
3. Preparing users for productive consultations
4. Publishing complete journey data to MCIP

---

## MCIP v2 Integration

### Prerequisites (Gate)

**Requires:** Cost Planner v2 completion

```python
def _check_prerequisites() -> bool:
    financial = MCIP.get_financial_profile()
    return financial is not None
```

**Gate Display:**
- Shows progress: GCP ✅ | Cost Planner ⏳
- Friendly messaging: "Complete Cost Planner first for best conversation"
- Navigation buttons: "Back to Hub" | "Start Cost Planner"

---

### Reading from MCIP

**Context Display at Top:**
```python
care_rec = MCIP.get_care_recommendation()
financial = MCIP.get_financial_profile()

# Shows: "Planning for Dorothy: Care Level: Assisted Living | Estimated Cost: $4,500/month"
```

**Used Throughout Product:**
- Step 2: Shows care recommendation with rationale
- Step 5: Shows complete journey summary (all 3 products)
- Completion: Displays tier, costs, and appointment details together

---

### Publishing to MCIP

**When:** User completes all 4 steps and reaches completion screen

**What's Published:**
```python
AdvisorAppointment(
    scheduled=True,
    date="2025-10-20",  # User's selected date
    time="Morning (9 AM - 12 PM)",  # User's selected time window
    type="phone_call",  # phone_call | video_call | in_person
    confirmation_id="PFMA-20251014-143522",  # Unique ID
    generated_at="2025-10-14T14:35:22Z",
    status="scheduled"
)
```

**Actions:**
```python
# 1. Publish appointment
MCIP.publish_appointment(appointment)

# 2. Mark PFMA complete in journey
MCIP.mark_product_complete("pfma")

# 3. Fire events
# - "mcip.appointment.scheduled" event
# - Updates journey state
```

---

## Product Flow

### Step 0: Introduction

**Purpose:** Orient user to PFMA process

**Content:**
- Welcome message with personalization
- Overview of 4 steps
- Duck system explanation (earn 1 duck per step)
- CTA: "Let's Get Started"

---

### Step 1: Book Appointment (🦆 Duck 1)

**Purpose:** Schedule advisor consultation

**Data Collected:**
- **Contact Method:** Phone Call | Video Call | In-Person Meeting
- **Preferred Date:** Next 30 days via date picker
- **Time Window:** Morning | Afternoon | Evening
- **Phone Number:** For callback
- **Email:** For confirmation
- **Special Notes:** Topics to discuss (optional)

**Validation:**
- Date must be 1-30 days in future
- Phone or email required
- Method selected

**Duck Award:** On first completion of this step

---

### Step 2: Verify Care Needs (🦆 Duck 2)

**Purpose:** Confirm GCP recommendations before advisor call

**MCIP Integration:**
- Reads `MCIP.get_care_recommendation()`
- Shows tier, confidence, and rationale
- Allows user to note changes since assessment

**Data Collected:**
- **Care Confirmed:** Yes | No, needs have changed
- **Changes Description:** (if needs changed)

**UI Enhancement:**
- Expandable rationale section
- Confidence percentage display
- Personalized tier display ("Assisted Living" not "assisted_living")

**Duck Award:** On second step completion

---

### Step 3: Verify Household & Legal (🦆 Duck 3)

**Purpose:** Confirm household and legal arrangements

**Data Collected:**
- **Living Situation:** Living alone | With spouse | With family | Assisted living | Memory care | Other
- **Power of Attorney:** Yes | No | In progress
- **Advance Directives:** Yes | No | In progress

**Why This Matters:**
- Advisors need to know decision-making authority
- Legal docs affect Medicaid planning
- Living situation impacts care options

**Duck Award:** On third step completion

---

### Step 4: Verify Benefits & Coverage (🦆 Duck 4)

**Purpose:** Confirm insurance and benefits for funding discussion

**Data Collected:**

**Insurance:**
- ☐ Medicare
- ☐ Medicaid
- ☐ Long-term care insurance
- ☐ Private health insurance

**Veterans Benefits:**
- ☐ Veteran or surviving spouse
- If yes: VA benefits status (Not enrolled | Enrolled | Receiving benefits | Applied - pending)

**Why This Matters:**
- Determines funding options
- Affects cost estimates
- VA A&A benefits eligibility

**Duck Award:** On final step completion (triggers balloons!)

---

### Step 5: Completion & MCIP Publishing

**Purpose:** Confirm submission and publish to MCIP

**Display:**
1. **Success Banner:** "You're All Set! 🎉 All 4 ducks earned! 🦆🦆🦆🦆"
2. **Appointment Summary:** Method, date, time, contact info
3. **Special Requests:** (expandable if provided)
4. **MCIP Journey Summary:** 3-column grid showing all products
5. **What's Next:** 4-step guide for preparation

**MCIP Actions (Automatic):**
```python
# Only runs once (checked via published_to_mcip flag)
if not pfma.get("published_to_mcip"):
    _publish_to_mcip()
    pfma["published_to_mcip"] = True
```

**Journey Summary Display:**
```
Guided Care Plan          Cost Planner             Advisor Appointment
✅ Assisted Living        ✅ $4,500/month          ✅ Phone Call
Confidence: 85%           Runway: 30 months        Confirmation: PFMA-20251014-143522
```

**Progress Bar:** "3/3 Products Complete" (100%)

---

## Duck System

**Gamification:** Earn ducks to encourage completion

### How It Works

- **4 Total Ducks:** One per step (Steps 1-4)
- **Awarded Once:** Can revisit steps without re-awarding
- **Visual Display:** Sidebar shows 🦆🦆🦆🦆 or 🦆🦆⚪⚪
- **Progress Bar:** 0%, 25%, 50%, 75%, 100%
- **Balloons:** Triggered on each duck award

### Duck Logic

```python
# Award duck only if moving to next step for first time
if pfma.get("ducks_earned", 0) == 0:  # On step 1 completion
    pfma["ducks_earned"] = 1
    st.balloons()

if pfma.get("ducks_earned", 0) == 1:  # On step 2 completion
    pfma["ducks_earned"] = 2
    st.balloons()

# Etc...
```

### Sidebar Display

```
🦆 Your Progress
Ducks Earned: 3/4

🦆🦆🦆⚪

[====== 75%]
```

---

## State Management

### Session State Structure

```python
st.session_state["pfma_v2"] = {
    "step": 0,  # Current step (0-5)
    "ducks_earned": 0,  # Ducks collected (0-4)
    "published_to_mcip": False,  # Published flag
    "appointment": {
        "method": "Phone Call",
        "date": "2025-10-20",
        "time_window": "Morning (9 AM - 12 PM)",
        "phone": "555-1234",
        "email": "user@example.com",
        "notes": "Want to discuss Medicaid"
    },
    "verifications": {
        "care_confirmed": "Yes, this is accurate",
        "care_changes": "",
        "living_situation": "Living alone",
        "has_poa": "Yes",
        "has_advance_directive": "No",
        "has_medicare": True,
        "has_medicaid": False,
        "has_ltc_insurance": False,
        "has_private_insurance": True,
        "is_veteran": False,
        "va_benefits_status": None
    }
}
```

---

## Navigation Flow

### Entry Points

1. **Concierge Hub:** "Plan with My Advisor" tile (shown after Cost Planner complete)
2. **Cost Planner Completion:** "Schedule Advisor Meeting" button
3. **Direct URL:** `?page=pfma_v2`
4. **Additional Services:** "PFMA" product tile

### Exit Points

1. **Completion:** "← Return to Hub" button → Concierge Hub
2. **Gate (blocked):** "← Back to Hub" or "Start Cost Planner →"
3. **Any step:** "← Back to Hub" button

### Step Navigation

```
Step 0 (Intro) → Step 1 (Appointment) → Step 2 (Care) → Step 3 (Household) → Step 4 (Benefits) → Step 5 (Complete)
     ↓                ↓                     ↓               ↓                    ↓                     ↓
"Get Started"    "Book Appt"          "Continue"       "Continue"           "Complete"          "Return to Hub"
```

**Back Buttons:** Every step has "← Back" to previous step

---

## Personalization

### User Name Integration

```python
person_name = st.session_state.get("person_name", "your loved one")

# Used in:
# - Introduction: "get you ready to meet with a live advisor who can help you implement the care plan for Dorothy"
# - MCIP Context: "Planning for Dorothy: Care Level: Assisted Living"
# - Completion: "about Dorothy's care"
```

### Care Tier Display

```python
# Transform MCIP tier to user-friendly display
care_rec.tier  # "assisted_living"
tier_display = care_rec.tier.replace("_", " ").title()  # "Assisted Living"
```

### Cost Display

```python
# Format financial data
cost_display = f"${financial.estimated_monthly_cost:,.0f}/month"  # "$4,500/month"
```

---

## MCIP Data Contract

### Reads From MCIP

| Data | Source | Used In |
|------|--------|---------|
| CareRecommendation | `MCIP.get_care_recommendation()` | Gate, Step 2, Completion |
| FinancialProfile | `MCIP.get_financial_profile()` | Gate, Context, Completion |
| (AdvisorAppointment) | `MCIP.get_advisor_appointment()` | Completion summary |

### Writes To MCIP

| Data | Method | When |
|------|--------|------|
| AdvisorAppointment | `MCIP.publish_appointment(appointment)` | Step 5 completion (once) |
| Product Complete | `MCIP.mark_product_complete("pfma")` | Step 5 completion (once) |

### Events Fired

| Event | Payload | Triggered By |
|-------|---------|--------------|
| `mcip.appointment.scheduled` | date, time, type, confirmation_id | `MCIP.publish_appointment()` |
| `mcip.product.completed` | product: "pfma" | `MCIP.mark_product_complete()` |

---

## Testing Checklist

### Gate Testing

- [ ] Navigate to `?page=pfma_v2` without completing Cost Planner
- [ ] Verify gate displays with "Complete Cost Planner first" message
- [ ] Check progress display shows GCP ✅ and Cost Planner ⏳
- [ ] Click "Start Cost Planner" → Routes to Cost Planner v2
- [ ] Complete Cost Planner → Return to PFMA v2
- [ ] Verify gate no longer shows, intro page displays

### Flow Testing

- [ ] Complete Step 0 (Intro) → Step 1 appears
- [ ] Fill appointment form (all fields)
- [ ] Submit Step 1 → Duck 1 awarded 🦆 + balloons
- [ ] Check sidebar shows 1/4 ducks (25%)
- [ ] Complete Step 2 (Care verification) → Duck 2 awarded
- [ ] Complete Step 3 (Household/Legal) → Duck 3 awarded
- [ ] Complete Step 4 (Benefits) → Duck 4 awarded + balloons
- [ ] Check sidebar shows 4/4 ducks (100%)
- [ ] Reach Step 5 (Completion)

### MCIP Integration Testing

- [ ] On Step 5, verify MCIP context shows all 3 products
- [ ] Check appointment published: `MCIP.get_advisor_appointment()`
- [ ] Verify PFMA marked complete: `MCIP.is_product_complete("pfma")`
- [ ] Check journey progress: `MCIP.get_journey_progress()` shows 3/3
- [ ] Verify events fired in `st.session_state["mcip"]["events"]`

### Back Navigation Testing

- [ ] From any step, click "← Back" → Previous step appears
- [ ] Data persists when navigating back
- [ ] Ducks don't re-award when revisiting completed steps

### Data Persistence Testing

- [ ] Fill appointment form partially
- [ ] Navigate away from PFMA v2
- [ ] Return to PFMA v2
- [ ] Verify form data persisted

### Personalization Testing

- [ ] Enter name "Dorothy" in welcome flow
- [ ] Complete GCP v4 → tier = "assisted_living"
- [ ] Complete Cost Planner v2 → cost = $4500
- [ ] Navigate to PFMA v2
- [ ] Verify context shows "Planning for Dorothy: Assisted Living | $4,500/month"
- [ ] Check Step 2 shows "Assisted Living" (not "assisted_living")
- [ ] Verify completion page shows "about Dorothy's care"

---

## Code Architecture

### Universal Product Pattern Compliance

✅ **1. Check prerequisites via MCIP**
```python
if not _check_prerequisites():
    _render_gate()
    return
```

✅ **2. Show friendly gate**
```python
def _render_gate():
    # Show what's completed, what's missing
    # Provide clear path forward
```

✅ **3. Run product logic**
```python
# Multi-step flow with duck gamification
# 5 steps: Intro → Appointment → Verify x3 → Complete
```

✅ **4. Publish to MCIP when complete**
```python
if not pfma.get("published_to_mcip"):
    _publish_to_mcip()
    pfma["published_to_mcip"] = True
```

✅ **5. Mark product complete**
```python
MCIP.mark_product_complete("pfma")
```

### Key Functions

| Function | Purpose |
|----------|---------|
| `render()` | Main entry point, routes to steps |
| `_check_prerequisites()` | Gate logic (requires Cost Planner) |
| `_render_gate()` | Friendly gate display |
| `_initialize_state()` | Setup session state structure |
| `_render_mcip_context()` | Show care + financial context |
| `_render_duck_progress_sidebar()` | Duck display in sidebar |
| `_render_intro()` | Step 0: Introduction |
| `_render_appointment_booking()` | Step 1: Book appointment |
| `_render_verify_care_needs()` | Step 2: Verify GCP data |
| `_render_verify_household_legal()` | Step 3: Verify household/legal |
| `_render_verify_benefits_coverage()` | Step 4: Verify insurance/benefits |
| `_render_completion()` | Step 5: Summary + MCIP publish |
| `_publish_to_mcip()` | Publish AdvisorAppointment |
| `_render_journey_summary()` | 3-column journey display |

---

## Future Enhancements

### Phase 1: Calendar Integration

**Goal:** Real-time advisor availability

**Implementation:**
- Integrate with Calendly or similar API
- Show actual available time slots
- Instant booking confirmation
- Calendar invite emails

---

### Phase 2: Document Upload

**Goal:** Attach relevant documents before call

**Implementation:**
- File upload in Step 1 or Step 5
- Supported: Insurance cards, financial statements, legal docs
- Stored in cloud storage (S3, Google Drive)
- Shared with advisor before call

---

### Phase 3: Pre-Call Checklist

**Goal:** Guided preparation for appointment

**Implementation:**
- New step or email sequence
- Checklist items based on care tier and finances
- Document gathering reminders
- Question preparation worksheet

---

### Phase 4: Post-Call Follow-Up

**Goal:** Capture action items from advisor call

**Implementation:**
- New product: "Post-Advisor Actions"
- Checklist from advisor meeting
- Status tracking for recommendations
- Follow-up appointment scheduling

---

## Summary

✅ **PFMA v2 Complete:**
- Gates on Cost Planner completion via MCIP
- Reads care recommendation and financial profile for context
- Publishes AdvisorAppointment to MCIP on completion
- Marks PFMA complete in journey
- Uses duck gamification (4 ducks, 5 steps)
- Shows complete journey summary at end
- Follows universal product pattern

✅ **Completes Core Journey:**
```
GCP v4 → Cost Planner v2 → PFMA v2
  ↓           ↓              ↓
 MCIP       MCIP           MCIP
  ↓           ↓              ↓
CareRec → FinancialProfile → Appointment
```

✅ **Ready for Integration Testing:**
- Test gate with/without Cost Planner
- Test complete flow with duck awards
- Verify MCIP publishing and journey state
- Check personalization with user name and tier

**Next:** Update Concierge Hub to show all 3 v2 products with MCIP orchestration!

---

**Document Version:** 1.0  
**Last Updated:** October 14, 2025  
**Related Docs:** 
- `MCIP_PRODUCT_MODULE_PATTERN.md`
- `COST_PLANNER_V2_MCIP_INTEGRATION.md`
- `E2E_INTEGRATION_TEST_GUIDE.md`
- `ADDITIONAL_SERVICES_MCIP_INTEGRATION.md`
