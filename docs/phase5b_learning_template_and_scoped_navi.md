Excellent 👍 — here’s the **full Phase 5B Markdown brief** you can drop directly into your repo as
`docs/phase5b_learning_template_and_scoped_navi.md`.

It’s written in Claude-safe format — precise, linear, and locked down (no creative freedom).

---

````markdown
# Phase 5B — Learning Template & Scoped NAVI Chat

**Date:** 2025-10-30  
**Branch:** `feature/learning-template`  
**Owner:** Concierge Care Advisors / Senior Navigator  
**Purpose:** Establish a reusable learning-tile architecture used by both *Discovery* and *Learn About My Recommendation*, introducing a scoped NAVI chat limited to each learning topic.

---

## 🎯 Objective

1. Create a single reusable **Learning Template** component (`core/learning_template.py`).  
2. Use it to power both **Discovery** and **Learn About My Recommendation** product tiles.  
3. Add a **Scoped NAVI Chat** class that constrains NAVI’s context to each lesson topic.  
4. Maintain consistent look, tone, and functionality across all learning experiences.  
5. Record completion to the user’s `journey_stage` and phase progress when a learning tile is finished.  

---

## 🧩 Files & Structure

| File | Action | Purpose |
|------|---------|----------|
| `core/learning_template.py` | **New (~120 lines)** | Core shared learning tile renderer |
| `navi_core/scoped_chat.py` | **New (~90 lines)** | NAVI chat restricted to a single topic |
| `pages/product_discovery_learning.py` | **Modified (+30 lines)** | Switch to `learning_template.render_learning()` |
| `pages/product_learn_about_recommendation.py` | **Modified (+30 lines)** | Switch to `learning_template.render_learning()` |
| `core/journeys.py` | **Modified (+15 lines)** | Add `mark_tile_complete()` helper |
| `core/styles/dashboard.css` | **Modified (+10 lines)** | Add minor style helpers for lesson cards |

---

## 🧱 System Design

### 1️⃣ Learning Template
```python
# core/learning_template.py
import streamlit as st
from navi_core.scoped_chat import ScopedNaviChat
from core.journeys import mark_tile_complete

def render_learning(title:str, intro:str, topic:str, resources:list[str], phase:str):
    """Standardized structure for any NAVI-guided learning experience."""
    st.title(title)
    st.markdown(intro)

    # Resource blocks (video or markdown)
    for r in resources:
        if "youtube" in r:
            st.video(r)
        else:
            st.markdown(f"[Open Resource]({r})")

    # Scoped NAVI chat
    st.markdown("---")
    st.subheader("Ask NAVI a Question")
    ScopedNaviChat(topic_scope=topic).render()

    # Completion
    if st.button("Mark Lesson Complete"):
        mark_tile_complete(topic, phase)
        st.switch_page("pages/hub_lobby.py")
````

---

### 2️⃣ Scoped NAVI Chat

```python
# navi_core/scoped_chat.py
import streamlit as st
from navi_core.llm import call_navi_llm

class ScopedNaviChat:
    """A NAVI chat restricted to a single learning topic."""
    def __init__(self, topic_scope:str):
        self.topic_scope = topic_scope

    def render(self):
        prompt = st.chat_input("Ask NAVI about this topic…")
        if prompt:
            st.chat_message("user").write(prompt)
            reply = self.query_llm(prompt)
            st.chat_message("assistant").write(reply)

    def query_llm(self, user_prompt:str) -> str:
        context = (
            f"You are NAVI, the Senior Navigator assistant. "
            f"Only answer within this topic scope: {self.topic_scope}. "
            f"If the user asks outside scope, gently redirect them."
        )
        return call_navi_llm(context, user_prompt)
```

---

### 3️⃣ Product Tile Integrations

#### Discovery Learning

```python
# pages/product_discovery_learning.py
from core.learning_template import render_learning

def render():
    render_learning(
        title="Start Your Discovery Journey",
        intro="👋 Hi, I’m NAVI. Here’s how Senior Navigator can help you and your family.",
        topic="senior_navigator_overview",
        resources=[
            "https://www.youtube.com/watch?v=example",
            "https://conciergecareadvisors.com/about"
        ],
        phase="discovery"
    )
```

#### Learn About My Recommendation

```python
# pages/product_learn_about_recommendation.py
from core.learning_template import render_learning

def render():
    render_learning(
        title="Learn About Your Recommendation",
        intro="Let’s look at what your care recommendation means and what to expect next.",
        topic="care_recommendation_explainer",
        resources=[
            "https://www.youtube.com/watch?v=example2",
            "https://alz.org/help-support"
        ],
        phase="discovery"
    )
```

---

### 4️⃣ Journey Tracking Helper

```python
# core/journeys.py
def mark_tile_complete(key:str, phase:str):
    """Add a completed tile entry for the phase."""
    completed = st.session_state.setdefault("completed_tiles", [])
    completed.append({"key": key, "phase": phase})
    st.session_state["journey_stage"] = phase
```

---

### 5️⃣ UI Enhancements

Add to `dashboard.css`:

```css
.learning-card {
  background:#fff;
  border-radius:16px;
  padding:1.5rem;
  box-shadow:0 2px 6px rgba(0,0,0,.05);
}
.learning-card h1 {margin-bottom:.75rem;}
```

---

## 🧪 Verification Checklist

| Step | Expected Result                                                    |
| :--: | ------------------------------------------------------------------ |
|   1  | Lobby shows Discovery tile → click opens lesson                    |
|   2  | NAVI chat appears and responds only within topic                   |
|   3  | “Mark Lesson Complete” returns to Lobby and phase progress updates |
|   4  | Learn About My Recommendation uses same template                   |
|   5  | NAVI tone and responses match lesson topic                         |
|   6  | No cross-topic answers (e.g., Cost Planner questions in Discovery) |
|   7  | No CSS or layout regressions                                       |

---

## ✅ Expected Outcome

After Phase 5B:

* Discovery and Learning tiles share one cohesive template
* NAVI is contextually aware of lesson topics
* Educational flow is consistent and LLM-supported
* Completion tracking updates journey progress
* The system is ready for future learning tiles (e.g., VA Benefits, Advisor Prep)

---

**End of Document**

```
