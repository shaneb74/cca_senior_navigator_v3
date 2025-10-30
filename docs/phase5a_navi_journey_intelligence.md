Got it ✅ — here’s the **complete Phase 5A Markdown brief** ready for your repo as
`docs/phase5a_navi_journey_intelligence.md`.

Copy and paste it exactly as-is ⬇️

---

````markdown
# Phase 5A — NAVI Journey Intelligence & Learning Tiles

**Date:** 2025-10-30  
**Branch:** `feature/navi-journey-intelligence`  
**Owner:** Concierge Care Advisors / Senior Navigator  
**Purpose:** Expand NAVI’s contextual awareness, integrate the new Discovery and Learning tiles, and add visual “Journey Phase” pills across product tiles for consistency and clarity.  

---

## 🎯 Objective

1. Introduce a **Discovery Learning** tile — the user’s first interaction in the app.  
2. Expand **Learn About My Recommendation** to include richer educational flow.  
3. Enhance NAVI’s empathy and context by syncing her tone and progress tracking with the user’s *current journey phase* (Discovery → Planning → Postplanning).  
4. Add **phase pills** to each product tile for consistent visual cues and progress awareness.  

---

## 🧩 New & Modified Files

| File | Action | Purpose |
|------|---------|---------|
| `pages/product_discovery_learning.py` | **New (≈120 lines)** | Introduces Discovery tile and orientation experience |
| `pages/product_learn_about_recommendation.py` | Modified (+70 lines) | Adds NAVI educational dialog and resource content |
| `core/journeys.py` | Modified (+40 lines) | Adds phase definitions and completion tracking per phase |
| `core/styles/dashboard.css` | Modified (+25 lines) | Adds phase-pill CSS |
| `navi_core/context_manager.py` | Modified (+35 lines) | NAVI tone and context updates based on phase |
| `navi_core/guidance_manager.py` | Modified (+45 lines) | Phase-aware guidance text injection |
| `pages/hub_lobby.py` | Modified (+30 lines) | Adds Discovery tile, injects phase pills for all tiles |

---

## 🧱 System Behavior Overview

### 1. **Journey Phases**
| Phase | Description | Example Tiles |
|:------|:-------------|:--------------|
| `discovery` | User orientation, introduction to NAVI and goals | Discovery Learning, Learn About My Recommendation |
| `planning` | Active decision-making and assessment | Guided Care Plan, Cost Planner, My Advisor |
| `postplanning` | Reflection, follow-up, engagement | Concierge Clinical Review, Additional Services |

`core/journeys.py` additions:
```python
def get_phase_completion(phase: str) -> float:
    """Return percentage of completion within a given journey phase."""
    completed = [p for p in st.session_state.get("completed_tiles", []) if p["phase"] == phase]
    total = [p for p in st.session_state.get("registered_tiles", []) if p["phase"] == phase]
    return len(completed) / len(total) if total else 0.0
````

---

### 2. **Phase Pills (Visual Tags)**

Each product tile displays a small phase label for clarity.

```css
/* ----- JOURNEY PHASE PILLS ----- */
.phase-pill {
  position: absolute;
  top: 0.8rem;
  right: 0.8rem;
  font-size: 0.7rem;
  font-weight: 600;
  color: #fff;
  padding: 0.25rem 0.7rem;
  border-radius: 9999px;
  letter-spacing: 0.03em;
}
.phase-pill.discovery { background-color: #5BA3FF; }
.phase-pill.planning { background-color: #4BBE83; }
.phase-pill.postplanning { background-color: #B974E4; }
```

Example for a Planning tile:

```python
st.markdown('<div class="phase-pill planning">PLANNING</div>', unsafe_allow_html=True)
```

---

### 3. **Discovery Learning Tile**

**Purpose:** Introduce NAVI, explain what to expect, and help the user orient themselves.

`product_discovery_learning.py` outline:

```python
import streamlit as st
from core.journeys import advance_to

def render():
    st.title("Start Your Discovery Journey")
    st.markdown("### Welcome to Senior Navigator!")
    st.markdown("> 👋 Hi, I’m NAVI. Let’s take a quick look at what you can do here.")
    
    st.info("Together, we’ll explore your situation, understand your care options, and help you plan confidently.")

    if st.button("Continue to Guided Care Plan"):
        advance_to("planning")
        st.switch_page("pages/product_guided_care_plan.py")
```

---

### 4. **NAVI Context Enhancements**

NAVI now adjusts tone and progress scope dynamically:

| Phase        | Tone                        | Example Message                                                 |
| :----------- | :-------------------------- | :-------------------------------------------------------------- |
| Discovery    | Encouraging / welcoming     | “You’re just getting started — let’s explore together.”         |
| Planning     | Confident / helpful         | “You’re halfway through your planning journey — nice progress!” |
| Postplanning | Supportive / future-focused | “You’ve completed your planning! Let’s see what comes next.”    |

In `guidance_manager.py`, add:

```python
def get_phase_tone():
    phase = st.session_state.get("journey_stage", "discovery")
    return {
        "discovery": "encouraging",
        "planning": "helpful",
        "postplanning": "supportive"
    }.get(phase, "neutral")
```

---

### 5. **Learn About My Recommendation Enhancements**

Expand to include more NAVI-led education and transitions:

* Additional empathy dialogue.
* Resource linking (VA, Alzheimer’s, etc.).
* Optional “Tell Me More” button that triggers secondary NAVI explanation.

---

## 🧪 Verification Checklist

| Check                               | Expected Result                                              |
| ----------------------------------- | ------------------------------------------------------------ |
| Visit Lobby                         | Discovery tile visible above Guided Care Plan                |
| Complete Discovery                  | Discovery tile moves to Completed Journeys                   |
| GCP → Learn About My Recommendation | Smooth transition; Learn tile appears                        |
| NAVI                                | Tone changes per phase (Discovery → Planning → Postplanning) |
| Phase pills                         | Visible, color-coded, positioned top-right of each tile      |
| CSS                                 | Matches existing dashboard style                             |
| No console errors                   | No new errors introduced                                     |

---

## ✅ Expected Outcome

After Phase 5A:

* NAVI becomes **phase-aware**, contextually guiding users through each journey.
* The **Discovery tile** provides first-touch onboarding.
* **Learn About My Recommendation** deepens understanding after GCP.
* Each tile clearly shows its journey phase.
* The user’s entire experience now has emotional pacing, logical progression, and clear phase transitions.

---

**End of Document**

```

---

Once added to the repo, tell Claude:  
> “Follow the Phase 5A NAVI Journey Intelligence & Learning Tiles brief exactly as written.”  

That will give you:
- The new **Discovery Learning tile**
- Phase-aware NAVI guidance
- Color-coded phase pills
- Updated flow with educational depth and no loss of navigation logic
```
