Perfect 👍 — here’s your complete **Phase 5A.1 Markdown Brief** (copy → paste → commit as
`docs/phase5a1_hotfix_navi_and_pills.md` before telling Claude to run it).

---

````markdown
# Phase 5A.1 — Hotfix: NAVI Tone, Phase Pills, and Hub Routing

**Date:** 2025-10-30  
**Branch:** `feature/navi-journey-intelligence`  
**Owner:** Concierge Care Advisors / Senior Navigator  
**Purpose:** Resolve Phase 5A regressions — fix hub routing, missing phase pills, and inactive NAVI tone context.

---

## 🎯 Objective

1. Fix all “Back to Hub” buttons so they route to **hub_lobby.py** instead of **welcome.py**.  
2. Render visible **phase pills** (Discovery / Planning / Post-Planning) on product tiles.  
3. Activate **phase-aware NAVI tone and guidance** in live chat.  
4. Add a visible **journey progress bar** for testing phase-completion logic.

---

## 🧩 Files & Expected Changes

| File | Action | Purpose |
|------|---------|---------|
| `pages/hub_lobby.py` | +40 lines | Add phase pill markup and progress bar |
| `core/styles/dashboard.css` | +20 lines | Ensure `.phase-pill` styling |
| `navi_core/context_manager.py` | +10 lines | Inject `get_phase_tone()` into session |
| `navi_core/llm.py` | +8 lines | Apply tone context in prompt |
| `pages/product_discovery_learning.py` | – | Fix return button routing to Lobby |

---

## 🧱 Implementation Details

### 1️⃣ Back to Hub Routing
Search globally for:
```python
st.switch_page("pages/welcome.py")
````

Replace **every occurrence** with:

```python
st.switch_page("pages/hub_lobby.py")
```

Confirm navigation functions in **Discovery Learning**, **Learn About My Recommendation**, and all Planning modules.

---

### 2️⃣ Phase Pills on Tiles

In `hub_lobby.py`, for each product tile block:

```python
phase = "planning"  # or discovery / postplanning
st.markdown(f'<span class="phase-pill {phase}">{phase.title()}</span>', unsafe_allow_html=True)
```

Add CSS import at top of file:

```python
st.markdown(f"<style>{open('core/styles/dashboard.css').read()}</style>", unsafe_allow_html=True)
```

#### Add to `dashboard.css`

```css
.phase-pill {
  position:absolute;
  top:0.75rem;
  right:1rem;
  padding:0.25rem 0.75rem;
  border-radius:9999px;
  font-size:0.75rem;
  font-weight:600;
  color:#fff;
}
.phase-pill.discovery { background-color:#5BA3FF; }
.phase-pill.planning { background-color:#4BBE83; }
.phase-pill.postplanning { background-color:#B974E4; }
```

---

### 3️⃣ Activate NAVI Tone Context

In `navi_core/context_manager.py`:

```python
from core.journeys import get_current_journey, get_phase_tone

def apply_phase_context():
    phase = get_current_journey()
    tone = get_phase_tone(phase)
    st.session_state["journey_stage"] = phase
    st.session_state["navi_tone"] = tone
```

Call this inside NAVI startup logic or before rendering chat.

---

### 4️⃣ Inject Tone into LLM Prompt

In `navi_core/llm.py`:

```python
def call_navi_llm(context, user_prompt):
    tone = st.session_state.get("navi_tone", "neutral")
    full_context = f"You are NAVI. Respond in a {tone} tone. " + context
    return openai_chat(full_context, user_prompt)
```

Optional debug during testing:

```python
st.caption(f"Phase: {st.session_state.get('journey_stage')} | Tone: {st.session_state.get('navi_tone')}")
```

---

### 5️⃣ Journey Progress Bar (Temporary UI)

At top of `hub_lobby.py`, beneath NAVI header:

```python
from core.journeys import get_phase_completion
completion = get_phase_completion(st.session_state.get("journey_stage", "discovery"))
st.progress(completion)
```

Verify progress changes after completing Discovery and Planning tiles.

---

## 🧪 Validation Checklist

| Step | Expected Result                                      |
| :--: | ---------------------------------------------------- |
|   1  | “Back to Hub” buttons open Lobby (not Welcome)       |
|   2  | Phase pills visible (top-right) with correct colors  |
|   3  | NAVI tone changes across phases (visible in caption) |
|   4  | Progress bar updates as journeys advance             |
|   5  | No layout flicker or CSS conflicts                   |
|   6  | All modules still route correctly                    |

---

## ✅ Expected Outcome

After Phase 5A.1 deployment:

* Navigation returns users to Lobby seamlessly
* Phase pills clearly indicate each journey stage
* NAVI adopts the correct tone for Discovery, Planning, and Post-Planning
* Progress visualization operational for QA validation

---

**End of Document**

```

---

Then tell Claude:  
> “Follow the Phase 5A.1 Hotfix brief exactly as written.”  

That’ll get your phase pills, tone context, and routing fixed without any other code touches.
```
