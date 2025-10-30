# Phase 4B — Journey Completion & Education Tile

**Date:** 2025-10-30  
**Branch:** `feature/journey-completion`  
**Owner:** Concierge Care Advisors / Senior Navigator  
**Purpose:** Complete the Lobby Hub transition by adding the *Learn About My Recommendation* product tile, connecting it to the Guided Care Plan completion flow, and retiring the legacy Concierge Hub.

---

## 🎯 Objective

Enhance the user journey to include an educational and empathetic step between the **Guided Care Plan** and **Cost Planner**.  
This new stage helps users understand their recommendation (e.g., Assisted Living, Memory Care, In-Home Care) before cost planning or advisor scheduling.

---

## 🧱 Scope Overview

| Area | Description |
|------|--------------|
| **Lobby Hub** | Add a new product tile titled **“Learn About My Recommendation”** positioned between *Guided Care Plan* and *Cost Planner*. |
| **Guided Care Plan (GCP)** | Update the summary step to redirect to the new tile rather than directly into Cost Planner. |
| **NAVI Integration** | Introduce a small conversational flow within this tile. NAVI asks reflective questions and presents educational content or resources. |
| **Journey System** | Add a lightweight helper `core/journeys.py` that tracks current journey stage: `discovery`, `planning`, `postplanning`. |
| **Concierge Hub Retirement** | Remove any remaining references to `hub_concierge.py`, including routes and nav entries. |
| **Tile Completion Logic** | When Learn About My Recommendation is marked complete, it transitions into the *Completed Journeys* section. |

---

## 🧩 File Changes

| File | Action |
|------|--------|
| `pages/hub_lobby.py` | Add new tile; update ordering and journey logic. |
| `pages/product_learn_about_recommendation.py` | **New file (≈120 lines)** — Implements educational flow and NAVI interaction. |
| `core/journeys.py` | **New file (≈80 lines)** — Tracks and exposes current journey state. |
| `pages/product_guided_care_plan.py` | Update redirect after summary → Lobby with highlighted Learn About My Recommendation tile. |
| `core/nav.json` | Remove `hub_concierge` entry if present. |
| `core/products.py` | Register new product metadata. |

---

## 🧩 Product Tile Specification

### **Tile Title:** Learn About My Recommendation  
**Description:**  
“Understand more about your recommended care type — whether it’s Assisted Living, Memory Care, or In-Home Care. Learn what to expect and how to prepare.”

**CTA:**  
“Continue to Cost Planner”  

**Behavior:**
- Appears once the Guided Care Plan is completed.
- Opens dedicated page: `product_learn_about_recommendation.py`
- NAVI presents short educational dialogue.
- User can continue or mark as complete → returns to Lobby.
- On completion, tile moves to *Completed Journeys.*

---

## 🧩 `core/journeys.py` Example

```python
# ==============================================
# Senior Navigator — Journey State Management
# ==============================================

import streamlit as st

def get_current_journey() -> str:
    """Return the current user journey stage."""
    return st.session_state.get("journey_stage", "discovery")

def set_journey(stage: str):
    """Set current journey stage (discovery, planning, postplanning)."""
    st.session_state["journey_stage"] = stage

def advance_to(stage: str):
    """Helper for transitions."""
    set_journey(stage)
    st.toast(f"Journey advanced to: {stage.title()}")
🧩 product_learn_about_recommendation.py Example
python
Copy code
import streamlit as st
from core.journeys import advance_to

def render():
    st.title("Learn About My Recommendation")
    st.markdown("### Understand what this means for you")

    # NAVI context introduction
    st.markdown("> 👋 Hi, I’m NAVI. Let’s take a moment to talk about what this recommendation means and how you can prepare.")
    
    rec_type = st.session_state.get("recommendation_type", "Assisted Living")

    if rec_type == "Assisted Living":
        st.info("Assisted Living communities support independence while providing help with daily activities, meals, and wellness programs.")
    elif rec_type == "Memory Care":
        st.info("Memory Care communities provide specialized safety, engagement, and structured support for those with cognitive conditions.")
    elif rec_type == "In-Home Care":
        st.info("In-home care allows you to stay where you are while bringing support services directly to your home.")
    else:
        st.info("Here’s what to expect from your next steps.")

    # CTA
    if st.button("Continue to Cost Planner"):
        advance_to("planning")
        st.switch_page("pages/product_cost_planner.py")
⚙️ Integration Notes
Lobby Tile Ordering:

nginx
Copy code
Discovery → Guided Care Plan → Learn About My Recommendation → Cost Planner → My Advisor → Concierge Clinical Review
GCP Summary Redirect:

Instead of routing directly to Cost Planner, use:

python
Copy code
st.switch_page("pages/product_learn_about_recommendation.py")
Concierge Cleanup:

Delete hub_concierge.py

Remove any references in nav.json and header menu

Redirect old Concierge routes → Lobby

🧪 Verification Checklist
Check	Expected Result
Visit Lobby	“Learn About My Recommendation” appears between GCP and Cost Planner
Complete GCP	Redirects to Learn About My Recommendation
Complete Learn About My Recommendation	Tile moves to Completed Journeys
Click Continue	Navigates to Cost Planner
Concierge references	None remain in code or nav
NAVI	Active and contextual on Learn page
Background / Styling	Consistent with existing Lobby CSS
Journey tracking	Updates correctly (Discovery → Planning → Postplanning)

✅ Expected Outcome
After Phase 4B:

Lobby Hub fully replaces Concierge.

Guided Care → Learn → Cost Planner → My Advisor forms a smooth, empathetic journey.

“Learn About My Recommendation” bridges understanding and confidence.

Journey stages tracked for future personalization.

NAVI remains central, contextual, and human-like in guidance.

End of Document

yaml
Copy code
