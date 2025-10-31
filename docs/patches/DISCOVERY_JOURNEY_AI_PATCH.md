Here’s the full Markdown implementation document — ready for commit as
`docs/patches/DISCOVERY_JOURNEY_AI_PATCH.md`.

---

````markdown
# 🌟 Patch: Discovery Journey AI-Enhanced Onboarding Page
**Branch:** `feature/post_css`  
**Goal:** Replace the static, text-heavy Discovery Journey intro with a lightweight, Navi-guided experience that includes embedded AI/FAQ functionality.

---

## 🎯 Problem Summary
The current Discovery Journey page is overly long, static, and visually uninviting.  
It needs to:
- Introduce the app’s purpose and modules in simple terms.  
- Use **Navi AI** to provide contextual Q&A within the page.  
- Retain completion logic and seamless navigation back to the Lobby.  

---

## ✅ Objectives
- Replace banners and blocks of dense text.  
- Add a **Navi-guided introduction** (friendly, conversational).  
- Embed a **mini LLM search box** for contextual FAQs.  
- Maintain progress tracking and the “Complete Discovery Journey” action.  
- Keep the layout clean, modern, and mobile-friendly.

---

## 1️⃣ `pages/discovery_journey.py`
Replace the existing body content with:

```python
import streamlit as st
from components.navi_box import render_navi_message
from components.llm_search import render_llm_search

st.markdown("### 🌟 Welcome to Your Discovery Journey")

render_navi_message(
    "Hi, I’m Navi. I’ll walk you through what this app can do — and answer any questions along the way."
)

st.write("""
This is your introduction to how **Senior Navigator** works — including:
- How to start your Discovery Journey
- What the Guided Care Plan does
- How DALL·E generates helpful visuals
- What to expect from your advisor experience
""")

# --- Embedded Navi mini search ---
with st.expander("💬 Ask Navi a Question", expanded=False):
    render_llm_search(
        placeholder="Ask about Guided Care, Cost Planner, or how DALL·E helps visualize care...",
        context_scope="discovery",
        show_examples=True
    )

# --- Quick FAQ section ---
st.markdown("#### Quick Answers")
faq_items = [
    ("⏱️ How long does this take?", "Most families complete Discovery in about 10–15 minutes."),
    ("🧭 What happens next?", "You’ll move on to your Guided Care Plan, where Navi personalizes your recommendations."),
    ("🎨 What’s DALL·E for?", "It helps create visuals that make your care journey more understandable and human.")
]
for q, a in faq_items:
    with st.expander(q):
        st.write(a)

# --- Completion ---
st.success("When you're ready, click below to mark this step finished.")
if st.button("✅ Complete Discovery Journey"):
    st.session_state["journey_discovery_complete"] = True
    st.switch_page("pages/hub_lobby.py")
````

---

## 2️⃣ New helper: `components/llm_search.py`

```python
import streamlit as st
from utils.ai_client import query_navi_llm

def render_llm_search(placeholder="Ask Navi...", context_scope="discovery", show_examples=True):
    query = st.text_input(placeholder, key=f"navi_query_{context_scope}")
    if show_examples:
        st.caption("Examples: *'What does the Cost Planner do?'*, *'How long does this take?'*, *'Who is DALL·E?'*")

    if query:
        with st.spinner("Navi is thinking..."):
            response = query_navi_llm(query, context=context_scope)
            st.markdown(f"**Navi:** {response}")
```

✅ This uses the same LLM backend as other Navi modules and keeps UI simple.

---

## 3️⃣ Optional Styling (`z_overrides.css`)

Append this snippet if visual polish is needed:

```css
/* === Discovery Journey Enhancements === */
.stExpander {
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  background-color: #fafbfc;
}
.stExpander:hover {
  border-color: #d1d5db;
}
```

---

## 4️⃣ Commit Message

```
feat(ui): simplify Discovery Journey and embed Navi mini AI search
- Replace dense text with concise Navi-led introduction
- Add expandable FAQs and inline LLM search component
- Retain completion button and progress tracking
- Update styling for clean, mobile-friendly experience
```

---

## 5️⃣ Verification Checklist

| Check             | Expected Result                             |
| ----------------- | ------------------------------------------- |
| Discovery intro   | Short, conversational copy displayed        |
| Navi AI search    | Appears inside expander, functional         |
| FAQ expanders     | Expand/collapse smoothly                    |
| Completion button | Marks journey as complete, returns to Lobby |
| Style             | Matches new tokenized look, no overflow     |

---

## ✅ Final Outcome

* Discovery Journey becomes **interactive, friendly, and AI-aware**.
* Navi’s presence is consistent but unobtrusive.
* Page remains simple, modern, and readable.
* Ready for future expansion (embedded DALL·E cards, CarePlan prompts).

---

**© 2025 Concierge Care Advisors — Senior Navigator™ Guided Experience**

```
