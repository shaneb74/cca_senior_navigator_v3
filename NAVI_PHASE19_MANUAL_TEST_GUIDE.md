# Navi Phase 19: Manual Testing Guide

## Overview
Phase 19 implements Navi as the **single intelligence layer** for the entire application. This guide provides step-by-step manual testing procedures to validate the complete implementation.

---

## Pre-Test Setup

1. **Start the application:**
   ```bash
   streamlit run app.py
   ```

2. **Clear browser cache** and start fresh session

3. **Have this checklist ready** for tracking results

---

## Test Categories

### A. Placement & Presence ✅

**Objective:** Verify Navi appears under header, above content on all pages

#### Test A1: Concierge Hub Placement
- [ ] Navigate to Concierge Care Hub
- [ ] **VERIFY:** Page header appears first
- [ ] **VERIFY:** Navi panel appears immediately below header
- [ ] **VERIFY:** Product tiles appear below Navi
- [ ] **VERIFY:** Additional Services rail on right side
- [ ] **VERIFY:** No visual overlap between header and Navi
- [ ] **VERIFY:** No Hub Guide component visible (deprecated)

**Expected Layout:**
```
┌─────────────────────────────────────┐
│ Page Header (Site nav, logo, etc.) │
├─────────────────────────────────────┤
│ Navi Panel                          │
│  - Journey status                   │
│  - Progress indicator               │
│  - Suggested questions (3 chips)    │
│  - Context boost bullets            │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Product Tiles                       │
│  - GCP tile                         │
│  - Cost Planner tile                │
│  - PFMA tile                        │
└─────────────────────────────────────┘
```

#### Test A2: GCP Product Placement
- [ ] Click on Guided Care Plan tile
- [ ] **VERIFY:** Product header appears first
- [ ] **VERIFY:** Navi panel appears immediately below header
- [ ] **VERIFY:** Module content (questions) appears below Navi
- [ ] **VERIFY:** No separate progress bar above Navi
- [ ] **VERIFY:** Navi shows module guidance and step progress

**Expected Layout:**
```
┌─────────────────────────────────────┐
│ Product Header                      │
├─────────────────────────────────────┤
│ Navi Panel                          │
│  - Module guidance                  │
│  - Section progress (Step X of Y)   │
│  - Contextual help                  │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Module Content                      │
│  - Questions/forms                  │
│  - Navigation buttons               │
└─────────────────────────────────────┘
```

#### Test A3: Cost Planner Placement
- [ ] Navigate back to hub
- [ ] Click on Cost Planner tile (or complete GCP first if gated)
- [ ] **VERIFY:** Navi panel appears under header
- [ ] **VERIFY:** Module hub content below Navi

#### Test A4: PFMA Placement
- [ ] Navigate to PFMA (complete prerequisites if needed)
- [ ] **VERIFY:** Navi panel appears under header
- [ ] **VERIFY:** Appointment booking flow below Navi
- [ ] **VERIFY:** No "duck progress" sidebar (deprecated)

---

### B. Dynamic Suggestions ✅

**Objective:** Verify Navi shows 3 context-aware question chips

#### Test B1: Default Questions (No Flags)
- [ ] Start fresh session (clear state)
- [ ] Navigate to Concierge Hub
- [ ] **VERIFY:** Navi shows 3 question chips
- [ ] **VERIFY:** Questions are generic/starter questions
- [ ] **Example:** "How do I get started?", "What care options exist?"

#### Test B2: Veteran Flag Questions
- [ ] Complete GCP with veteran status selected
- [ ] Return to Concierge Hub
- [ ] **VERIFY:** One of 3 questions relates to VA benefits
- [ ] **Example:** "Can I use VA benefits to pay for care?"

#### Test B3: Fall Risk Flag Questions
- [ ] Complete GCP with fall risk indicators
- [ ] Return to Concierge Hub
- [ ] **VERIFY:** One of 3 questions relates to fall prevention
- [ ] **Example:** "What services help prevent falls?"

#### Test B4: Memory Concerns Flag Questions
- [ ] Complete GCP with memory/cognitive concerns
- [ ] Return to Concierge Hub
- [ ] **VERIFY:** One of 3 questions relates to memory care
- [ ] **Example:** "What's the difference between AL and Memory Care?"

#### Test B5: Multiple Flags Prioritization
- [ ] Complete GCP with multiple flags (veteran + fall_risk + memory_concerns)
- [ ] Return to Concierge Hub
- [ ] **VERIFY:** Still shows exactly 3 questions
- [ ] **VERIFY:** Questions are unique (no duplicates)
- [ ] **VERIFY:** Questions reflect highest priority flags

#### Test B6: Question Chip Interaction
- [ ] Click on a suggested question chip
- [ ] **VERIFY:** Question moves to "Questions I've asked" history
- [ ] **VERIFY:** Answer appears below
- [ ] **VERIFY:** Suggested questions refill to remain 3

---

### C. Next-Best Action ✅

**Objective:** Verify Navi recommends correct next step based on progress

#### Test C1: Start Journey (0% Complete)
- [ ] Fresh session, Concierge Hub
- [ ] **VERIFY:** Navi shows "Start Guided Care Plan" or similar
- [ ] **VERIFY:** Next action button routes to GCP
- [ ] **VERIFY:** Progress shows 0/3 products complete

#### Test C2: After GCP Complete (33% Complete)
- [ ] Complete GCP module
- [ ] Return to Concierge Hub
- [ ] **VERIFY:** Navi shows "Calculate Costs" or similar
- [ ] **VERIFY:** Next action button routes to Cost Planner
- [ ] **VERIFY:** Progress shows 1/3 products complete
- [ ] **VERIFY:** Context boost shows care recommendation summary

#### Test C3: After Cost Planner Complete (67% Complete)
- [ ] Complete Cost Planner
- [ ] Return to Concierge Hub
- [ ] **VERIFY:** Navi shows "Book Advisor" or similar
- [ ] **VERIFY:** Next action button routes to PFMA
- [ ] **VERIFY:** Progress shows 2/3 products complete
- [ ] **VERIFY:** Context boost shows care tier + budget range

#### Test C4: Journey Complete (100%)
- [ ] Complete PFMA
- [ ] Return to Concierge Hub
- [ ] **VERIFY:** Navi shows completion message
- [ ] **VERIFY:** Navi suggests exploring services or resources
- [ ] **VERIFY:** Progress shows 3/3 products complete
- [ ] **VERIFY:** Confetti animation appears (gamification)

---

### D. Additional Services ✅

**Objective:** Verify flag-to-service mapping drives recommendations

#### Test D1: Veteran Flag → VA Benefits Service
- [ ] Complete GCP with veteran status
- [ ] Return to Concierge Hub
- [ ] **VERIFY:** Additional Services rail includes "Veterans Benefits" card
- [ ] **VERIFY:** Service appears in priority order (top 5)

#### Test D2: Fall Risk → Omcare Service
- [ ] Complete GCP with fall risk indicators
- [ ] Return to Concierge Hub
- [ ] **VERIFY:** Additional Services rail includes "Omcare" card
- [ ] **VERIFY:** Service appears in recommended order

#### Test D3: Mobility Concerns → Omcare Service
- [ ] Complete GCP with mobility concerns
- [ ] Return to Concierge Hub
- [ ] **VERIFY:** Additional Services rail includes "Omcare" card

#### Test D4: Multiple Flags → Prioritized Services
- [ ] Complete GCP with veteran + fall_risk + memory_concerns + financial_assistance_needed
- [ ] Return to Concierge Hub
- [ ] **VERIFY:** Additional Services shows up to 5 services
- [ ] **VERIFY:** Services are unique (no duplicates)
- [ ] **VERIFY:** Services match flag-to-tag mapping
- [ ] **VERIFY:** Order is meaningful (highest priority first)

#### Test D5: No Flags → Default Services
- [ ] Complete GCP with minimal flags
- [ ] Return to Concierge Hub
- [ ] **VERIFY:** Additional Services shows default recommendations
- [ ] **VERIFY:** At least some services appear (not empty)

---

### E. Navigation & Routing ✅

**Objective:** Verify navigation uses canonical routes and preserves context

#### Test E1: Back to Hub from FAQs
- [ ] Navigate to Concierge Hub
- [ ] Click on FAQ tile or link
- [ ] Click "Back to Hub" link in Navi or page
- [ ] **VERIFY:** Routes to **Concierge Care Hub**, not Welcome page
- [ ] **VERIFY:** Session context preserved (progress, flags)

#### Test E2: Back to Hub from Products
- [ ] Navigate to GCP product
- [ ] Look for "Back to Hub" or home navigation
- [ ] Click it
- [ ] **VERIFY:** Routes to Concierge Care Hub
- [ ] **VERIFY:** Progress saved and displayed

#### Test E3: Canonical Route IDs
- [ ] Inspect Navi's next action buttons
- [ ] **VERIFY:** Routes use clean IDs like "gcp_v4", "cost_v2", "pfma_v2"
- [ ] **VERIFY:** No hard-coded URLs like "?page=gcp_v4"
- [ ] **VERIFY:** No HTTP URLs in navigation

#### Test E4: Browser Back/Forward
- [ ] Navigate: Hub → GCP → Hub → Cost Planner
- [ ] Use browser back button twice
- [ ] **VERIFY:** Returns to Hub, then GCP correctly
- [ ] Use browser forward button
- [ ] **VERIFY:** Returns to Cost Planner
- [ ] **VERIFY:** Session state preserved throughout

---

### F. Regression Checks ✅

**Objective:** Verify deprecated components removed and no visual issues

#### Test F1: No Hub Guide Visible
- [ ] Navigate to Concierge Hub
- [ ] **VERIFY:** No "Hub Guide" component visible
- [ ] **VERIFY:** No guide-level orchestration UI
- [ ] **VERIFY:** Only Navi panel provides guidance

#### Test F2: No Duplicate Progress Indicators
- [ ] Navigate into GCP product
- [ ] **VERIFY:** Only ONE progress indicator visible (in Navi)
- [ ] **VERIFY:** No separate progress bar above or below Navi
- [ ] **VERIFY:** Module steps show in Navi panel only

#### Test F3: No Duck Progress in PFMA
- [ ] Navigate to PFMA
- [ ] **VERIFY:** No "duck progress" sidebar visible
- [ ] **VERIFY:** Progress shown in Navi panel only

#### Test F4: No Visual Overlap
- [ ] Navigate through all pages (Hub, GCP, Cost Planner, PFMA)
- [ ] **VERIFY:** Header and Navi don't overlap
- [ ] **VERIFY:** Navi and content don't overlap
- [ ] **VERIFY:** Consistent spacing throughout

#### Test F5: Product Tiles Still Work
- [ ] On Concierge Hub, click each product tile
- [ ] **VERIFY:** GCP tile opens GCP product
- [ ] **VERIFY:** Cost Planner tile opens Cost Planner (or shows gate)
- [ ] **VERIFY:** PFMA tile opens PFMA (or shows gate)
- [ ] **VERIFY:** FAQ tile opens FAQ page

#### Test F6: Additional Services Rail Works
- [ ] On Concierge Hub, scroll to Additional Services
- [ ] **VERIFY:** Service cards render correctly
- [ ] **VERIFY:** Service descriptions visible
- [ ] **VERIFY:** "Learn More" buttons work
- [ ] **VERIFY:** Services update based on flags

---

## Performance Checks

### P1: Page Load Time
- [ ] Navigate between pages (Hub ↔ Products)
- [ ] **VERIFY:** Pages load within 1-2 seconds
- [ ] **VERIFY:** No visible lag when Navi renders

### P2: State Persistence
- [ ] Complete GCP halfway
- [ ] Close browser
- [ ] Reopen and navigate to Concierge Hub
- [ ] **VERIFY:** Progress persists (session state saved)
- [ ] **VERIFY:** Navi shows correct progress

---

## Edge Cases

### E1: Gate Screens with Navi
- [ ] Navigate to Cost Planner without completing GCP
- [ ] **VERIFY:** Gate screen shows
- [ ] **VERIFY:** Navi still renders above gate
- [ ] **VERIFY:** Navi shows journey status and next action

### E2: Module Hub (Cost Planner Multi-Module)
- [ ] Complete GCP, navigate to Cost Planner
- [ ] **VERIFY:** Navi renders at hub level
- [ ] **VERIFY:** Shows overall hub progress, not individual module
- [ ] **VERIFY:** Guidance reflects multi-module workflow

### E3: Custom Flow (PFMA Multi-Step)
- [ ] Navigate to PFMA
- [ ] **VERIFY:** Navi renders at product level
- [ ] **VERIFY:** Shows step progress (Step X of 5)
- [ ] **VERIFY:** Guidance updates with each step

---

## Success Criteria

✅ **All tests in categories A-F pass**  
✅ **No visual regressions or overlaps**  
✅ **Navigation preserves session context**  
✅ **Dynamic suggestions reflect flags correctly**  
✅ **Additional Services update based on flags**  
✅ **Next-best action updates with progress**  
✅ **Hub Guide completely removed**  
✅ **No duplicate progress indicators**  
✅ **Performance acceptable (<2s page loads)**

---

## Test Results Log

**Tester:** _________________  
**Date:** _________________  
**App Version/Commit:** _________________

### Summary
- Total Tests: _____ / _____
- Passed: _____
- Failed: _____
- Notes:

### Failed Tests (if any)
```
Test ID: [e.g., B3]
Expected: [What should happen]
Actual: [What actually happened]
Screenshots: [Link if available]
```

---

## Next Steps After Testing

1. **If all tests pass:**
   - ✅ Mark Phase 19 complete
   - ✅ Document any observations
   - ✅ Update todo list
   - ✅ Proceed to next phase

2. **If tests fail:**
   - 🔍 Document specific failures
   - 🐛 Create bug report with test ID
   - 🔧 Fix issues
   - 🔁 Re-run affected tests
   - ✅ Re-validate

---

## Automated Test Validation

Before manual testing, run automated checks:

```bash
# Static analysis
python test_navi_e2e.py

# Unit tests (if pytest installed)
pytest tests/test_navi_integration.py -v
```

Both should pass before proceeding with manual testing.

---

## Contact

Questions or issues? Check:
- `NAVI_SINGLE_INTELLIGENCE_LAYER.md` - Architectural spec
- `core/navi.py` - Implementation
- `test_navi_e2e.py` - Automated validation

---

**🎉 Good luck with testing! Navi is ready to guide users through their journey.**
