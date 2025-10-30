Perfect clarification — here’s the **fully updated Phase 5D Markdown brief**, rewritten cleanly with your new intent:

---

```markdown
# Phase 5D — Journey Alignment, Navigation Fixes & Section Finalization

**Date:** 2025-10-30  
**Branch:** `feature/phase5d_journey_alignment`  
**Owner:** Concierge Care Advisors / Senior Navigator  
**Purpose:** Unify navigation, finalize section structure within the Lobby Hub, and ensure all product tiles are correctly associated with their respective journeys.  
**Primary Goal:** Deliver a stable, complete Lobby experience with clear hierarchy, correct routing, and accurate phase attribution.

---

## 🎯 Objective
This phase completes the transition from Concierge → Lobby by:

1. Fixing all “Back to Hub” navigation links to route to the Lobby.  
2. Finalizing the Lobby Hub structure (NAVI Header → Active Journey → Additional Services → My Completed Journey).  
3. Ensuring all product tiles are correctly mapped to their Journey phase.  
4. **Retiring Advisor Prep entirely** (no replacement tile).  
5. **Renaming Plan for My Advisor (PFMA)** → **My Advisor**, inheriting existing appointment scheduling functionality.  
6. Ensuring that after an appointment is completed, navigation returns to the Lobby and marks the **Planning Journey** complete.  
7. Removing the standalone **FAQ tile** (NAVI Header now hosts FAQs & Answers).  
8. Ensuring completed journeys appear below Additional Services.  

No new visual design changes are introduced beyond what is required for layout consistency.

---

## 🧩 Lobby Hub Structure

```

Lobby Hub (hub_lobby.py)
│
├── 1️⃣ NAVI Header Zone
│  • Persistent across app
│  • Contains phase-aware guidance and FAQs link
│
├── 2️⃣ Active Journey Section
│  • Displays tiles for current journeys (Discovery → Planning → Post-Planning)
│  • Each tile has phase pill (🔵 Discovery | 🟢 Planning | 🟣 Post-Planning)
│
├── 3️⃣ Additional Services Section (🧠 Dynamic / Personalized)
│  • Generated via MCIP v2 and partner API
│  • Examples: Medication Management, Cognitive Screening, VA Benefits
│
└── 4️⃣ ⭐ My Completed Journey Section
  • Appears only after at least one product is complete
  • Displays dimmed cards with ✓ Completed badge and optional “Review Again” button
  • Positioned **below Additional Services**

```

---

## 🔄 Journey Associations

| Journey Phase | Product Tiles | Notes |
|:--|:--|:--|
| **Discovery** | Start Your Discovery Journey | (Discovery Learning tile only) |
| **Planning** | Guided Care Plan, Learn About My Recommendation, Cost Planner, My Advisor (formerly PFMA) | Advisor Prep retired entirely. My Advisor inherits appointment scheduling. Once appointment completes, return to Lobby and mark Planning Journey complete. |
| **Post-Planning** | Senior Trivia, Concierge Clinical Review | No change. |
| **Additional Services** | Dynamic MCIP + Partner API Tiles | Personalized service recommendations. |
| **Completed Journey** | Auto-filled once a product is marked complete | Appears below Additional Services. |

---

## ⚙️ Navigation Fixes

1. All “Back to Hub” buttons in product modules must route to `?page=hub_lobby`, not `welcome.py`.  
2. Confirm buttons and links in these modules are updated:  
 • Guided Care Plan  
 • Learn About My Recommendation  
 • Cost Planner  
 • My Advisor (renamed from PFMA)  
 • Senior Trivia  
 • Concierge Clinical Review  
3. Ensure session state and progress persistence across navigation transitions.  

---

## 🧱 Implementation Details

**Files to modify**
```

pages/hub_lobby.py
pages/product_guided_care_plan.py
pages/product_learn_about_recommendation.py
pages/product_cost_planner.py
pages/product_plan_with_my_advisor.py   → renamed to product_my_advisor.py
pages/product_trivia.py
pages/product_concierge_clinical_review.py
core/journeys.py
core/navigation.py

````

**Code guidelines**
```python
# Example: replace legacy Back-to-Hub links
st.link_button("← Back to Lobby", "?page=hub_lobby")

# Example: mark journey complete after appointment
mark_journey_complete("planning")
````

---

## 🧪 Verification Checklist

| Test | Expected Result                                                                                      |
| :--- | :--------------------------------------------------------------------------------------------------- |
| 1    | All “Back to Hub” buttons return to Lobby (not Welcome).                                             |
| 2    | NAVI Header renders correctly with FAQs link.                                                        |
| 3    | Each tile shows correct journey pill color and label.                                                |
| 4    | Advisor Prep tile is completely removed.                                                             |
| 5    | My Advisor (former PFMA) functions for appointment scheduling and returns to Lobby after completion. |
| 6    | Completed Journey section appears below Additional Services.                                         |
| 7    | No routing errors or lost state between modules.                                                     |

---

## 🧾 Deliverables

| File               | Change      | Purpose                                       |
| :----------------- | :---------- | :-------------------------------------------- |
| `hub_lobby.py`     | +120 lines  | Section realignment + completed journey logic |
| `navigation.py`    | +30 lines   | Navigation update to Lobby                    |
| `journeys.py`      | +40 lines   | Phase association and progress tracking       |
| Product pages (x6) | +10–15 each | Back to Lobby navigation                      |
| `dashboard.css`    | +15 lines   | Completed Journey visual styles               |

Total expected: ≈ 270–300 lines added / modified.

---

## ✅ Expected Outcome

* Lobby Hub is the single central hub for all navigation.
* Each product correctly returns to Lobby.
* Journey phases are cleanly defined and visually cohesive.
* NAVI Header is active and FAQ tile removed.
* Advisor Prep is **retired entirely** (removed from UI and routing).
* Plan for My Advisor (PFMA) is renamed **My Advisor** and inherits appointment scheduling.
* After appointment completion, user returns to Lobby and Planning Journey is marked complete.
* “My Completed Journey” appears only when relevant and always below Additional Services.

---

**End of Document**

```

```
