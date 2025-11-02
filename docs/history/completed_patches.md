Excellent — here’s a **fully detailed, developer-safe Markdown plan** you can drop in `docs/CLEANUP_PLAN.md`.
It’s structured to guide Claude or any collaborator through the cleanup **without losing environment configuration, venv bindings, or terminal preferences.**

---

````markdown
# 🧹 Senior Navigator — Repository Cleanup Plan

**Branch:** `feature/phase5i_repo_cleanup`  
**Owner:** Concierge Care Advisors / Senior Navigator  
**Prepared:** 2025-10-30  
**Goal:** Safely refactor and declutter the repository following the Hub redesign (Phase 5G), while preserving all functional environments and developer workflows.

---

## 🧭 1. Objectives

1. Reorganize directories to reflect the new **multi-hub architecture**.  
2. Eliminate legacy Streamlit pages, unused assets, and redundant core modules.  
3. Maintain full **rollback and recovery capability** throughout cleanup.  
4. Preserve **virtual environments**, **venv config**, **terminal hotkeys**, and all IDE settings.  
5. Document every movement and deletion for PR traceability.

---

## 🧩 2. Pre-Cleanup Safeguards

Before any file movement or deletion:

1. **Create a full repository backup**
   ```bash
   git branch backup/pre_cleanup_$(date +%Y%m%d)
   zip -r backup_repo_$(date +%Y%m%d).zip .
````

2. **Preserve virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip freeze > requirements.lock
   ```

   * Do **not delete** `.venv/`, `.env`, or `.python-version`.
   * Add `.venv` to `.gitignore` (if not already).

3. **Save developer configs**

   ```bash
   mkdir -p dev_backup
   cp ~/.zshrc dev_backup/zshrc_backup_$(date +%Y%m%d)
   cp ~/.bash_profile dev_backup/bash_profile_backup_$(date +%Y%m%d)
   cp ~/.vscode/keybindings.json dev_backup/ || true
   ```

   This prevents loss of terminal shortcuts and VS Code hotkeys.

4. **Snapshot dependencies**

   ```bash
   pip list --format=freeze > dev_backup/pip_list_snapshot.txt
   ```

5. **Tag the current state**

   ```bash
   git tag -a pre_cleanup -m "Snapshot before Phase 5I repo cleanup"
   ```

---

## 🧱 3. Target Structure (Post-Cleanup)

### ✅ Proposed Folder Layout

```
app.py
core/
ui/
hubs/
    concierge/
    professional/
    resources/
shared/
    components/
    tiles/
assets/
    css/
    images/
docs/
    specs/
    cleanup/
tests/
```

**Key ideas:**

* `core/` → state, session, navigation logic only.
* `ui/` → app-wide layout, chrome, and NAVI framework.
* `shared/` → cross-hub components and renderers.
* `hubs/` → hub-specific logic (Concierge, Professional, Resources).
* `assets/` → all visual and style resources.
* `docs/specs/` → feature briefs by phase.
* `tests/` → unified hub smoke tests.

---

## 🧩 4. Cleanup Task Matrix

| Category            | Task                                                                  | Responsible | Tool/Command |
| ------------------- | --------------------------------------------------------------------- | ----------- | ------------ |
| Legacy Pages        | Move `pages/*.py` → `archive/pages_legacy/`                           | Claude      | `git mv`     |
| Product Modules     | Merge all Concierge products under `hubs/concierge/`                  | Claude      | manual       |
| Layout Split        | Move `layout.py` → `ui/layout_base.py` + `ui/nav.py` + `ui/footer.py` | Claude      | manual       |
| Core Simplification | Merge `core/state_bootstrap.py` into `core/state.py`                  | Claude      | manual       |
| Static Assets       | Move `static/images` → `assets/images`                                | Claude      | `git mv`     |
| CSS                 | Merge `dashboard.css` and `modules.css` → `assets/css/global.css`     | Claude      | manual       |
| Logging             | Centralize in `core/log.py`                                           | Claude      | manual       |
| Tests               | Add `tests/test_hubs_smoke.py`                                        | Claude      | pytest       |
| Docs                | Create `docs/cleanup/CHANGELOG_CLEANUP.md`                            | ChatGPT     | automated    |
| Backup              | Create `backup_repo_YYYYMMDD.zip`                                     | All         | script       |

---

## 🔒 5. Safety Mechanisms

* **Backup branch:** `backup/pre_cleanup_*` (never delete).
* **Rollback command:**

  ```bash
  git checkout backup/pre_cleanup_YYYYMMDD
  ```
* **Restore venv:**

  ```bash
  python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.lock
  ```
* **Auto-sync protection:** disable GitHub Actions auto-deploy during cleanup:

  ```bash
  touch .no_ci
  ```

---

## 🧾 6. Developer Environment Preservation

* Retain `.vscode/` folder (if exists).
* Keep `Makefile` and `.env` untouched.
* Maintain `openai_api_key` and other secrets in `.env`; never commit.
* Keep `requirements.lock` under version control for reproducibility.
* Verify that `PYTHONPATH` still resolves `/core` and `/ui`.

---

## ⚙️ 7. Verification Steps

| Check             | Command                 | Expected                       |
| ----------------- | ----------------------- | ------------------------------ |
| Import Resolution | `pytest --collect-only` | All imports resolve cleanly    |
| UI Launch         | `streamlit run app.py`  | Lobby and hubs render normally |
| CSS Integrity     | manual visual QA        | All tiles and borders intact   |
| Navigation        | clickthrough            | No missing routes              |
| Docs Index        | open `docs/specs/`      | All Phase 5+ briefs present    |

---

## 📦 8. Deliverables

| Output                                | Description              |
| ------------------------------------- | ------------------------ |
| `docs/CLEANUP_PLAN.md`                | This plan                |
| `backup_repo_YYYYMMDD.zip`            | Full pre-cleanup archive |
| `docs/cleanup/CHANGELOG_CLEANUP.md`   | Commit-by-commit summary |
| `tests/test_hubs_smoke.py`            | Sanity test suite        |
| `feature/phase5i_repo_cleanup` branch | All refactor commits     |

---

## 🧭 9. Commit Template

```
chore(cleanup): refactor repository structure for hub alignment

- Moved legacy pages to archive/
- Split layout into modular ui/
- Relocated static → assets/
- Preserved venv + dev config
- Created backup branch and zip archive
```

---

## 🧩 10. Phase Sequence

| Phase | Focus                                          | Status      |
| ----- | ---------------------------------------------- | ----------- |
| 5G    | Journey Hierarchy & Visual Identity            | ✅           |
| 5H    | Extend layout to Professional & Resources Hubs | ⏳           |
| 5I    | Repository Cleanup (this document)             | 🚀 upcoming |
| 5J    | CI/CD Stabilization & Code Health              | 🔜 next     |

---

## ✅ Expected Outcome

* Clean, modular repository consistent with the new hub design.
* Safe backups for rollback.
* Maintained venv, configs, and dev shortcuts.
* Simplified onboarding for new developers.
* Clear documentation hierarchy for future phases.

---

**End of File**

```

---

Would you like me to generate a matching **Claude execution command** (like for the earlier phases) so he can safely start the cleanup using this plan — with backups and without deleting anything yet?
```
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
Perfect — that’s a clean next step. Here’s the full patch documentation, formatted as a Markdown file so you can drop it directly into your repo under something like
`docs/patches/feature_post_css_journey_completion.md`.

It includes **everything from above** (logic, structure, styling, and animation notes) — fully self-contained, so Claude can execute it line-for-line when you open the new branch `feature/post_css`.

---

````markdown
# 🧩 Phase 5K Post-CSS Update — Journey Completion Logic & Active/Completed State

**Branch:** `feature/post_css`  
**Goal:** Fix journey completion logic, ensure product-level dependency tracking, add a subtle “Completed” fade-in badge animation, and maintain existing Navi/Hub visuals.

---

## 🎯 Overview

Current issues:
- Product tiles (Cost Planner, My Advisor, etc.) do not mark as completed.
- Guided Care Plan completes prematurely or remains in Active Journeys.
- Completed journeys still show under “Active Journeys.”
- Prepare for Appointment button does not trigger correct finalization.

This patch consolidates completion logic, restores automatic journey transitions, and adds a UI animation for completion confirmation.

---

## 1️⃣ `core/events.py` — Product & Journey Completion Logic

```python
from datetime import datetime

def mark_product_complete(user_ctx, product_key: str):
    """Mark a product complete and auto-update its parent journey."""
    journeys = user_ctx.setdefault("journeys", {})

    for journey_key, journey_data in journeys.items():
        products = journey_data.get("products", {})
        if product_key in products:
            products[product_key]["completed"] = True
            journey_data["updated_at"] = datetime.utcnow().isoformat()

            # If all products are now complete, mark journey complete
            if all(p.get("completed") for p in products.values()):
                journey_data["completed"] = True
                journey_data["status"] = "completed"
            break

    return user_ctx
````

Usage example inside any product module (e.g. Cost Planner, My Advisor):

```python
if st.button("Complete Cost Planner"):
    user_ctx = mark_product_complete(user_ctx, "cost_planner")
    save_user(user_ctx)
    go_to_lobby()
```

---

## 2️⃣ `hub_lobby.py` — Active vs Completed Journey Lists

```python
def _build_active_journeys(user_ctx):
    return [
        j for j in user_ctx.get("journeys", {}).values()
        if not j.get("completed")
    ]

def _build_completed_journeys(user_ctx):
    return [
        j for j in user_ctx.get("journeys", {}).values()
        if j.get("completed")
    ]
```

Use in render pipeline:

```python
active = _build_active_journeys(user_ctx)
completed = _build_completed_journeys(user_ctx)
```

---

## 3️⃣ Guided Care Plan Final Step

```python
if st.button("Prepare for Appointment"):
    user_ctx = mark_product_complete(user_ctx, "guided_care_plan")
    save_user(user_ctx)
    go_to_lobby()
```

---

## 4️⃣ `core/nav.py` — Consistent Lobby Routing

```python
import streamlit as st

def go_to_lobby():
    """Hard redirect to Lobby grid."""
    st.query_params.clear()
    st.query_params["page"] = "hub_lobby"
    st.session_state.pop("redirect_to", None)
    st.session_state.pop("next_page", None)
    st.session_state.pop("route", None)
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()
```

Replace all `go_to_hub()`, `go_to_home()`, or `go_to_welcome()` calls with `go_to_lobby()`.

---

## 5️⃣ CSS — Completion Badge & Fade-In Animation

**File:** `assets/css/overrides.css`

Append:

```css
/* === Journey Completion Badge === */
.completed-badge {
  display: inline-block;
  background: var(--success-bg, #e6f9ee);
  color: var(--success-text, #1b7f3c);
  font-weight: 600;
  border-radius: 20px;
  padding: 4px 10px;
  font-size: 0.85rem;
  opacity: 0;
  transform: translateY(-4px);
  animation: fadeInBadge 0.6s ease-out forwards;
}

@keyframes fadeInBadge {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

Use this in the completion render block:

```python
st.markdown('<span class="completed-badge">✓ Completed</span>', unsafe_allow_html=True)
```

---

## 6️⃣ Commit Message

```
feat(journey): unify completion logic and add fade-in badge
- Implement mark_product_complete() for product dependencies
- Auto-complete parent journey when all child products complete
- Update hub_lobby to separate active and completed journeys
- Fix Prepare for Appointment finalization
- Add CSS fade-in "Completed" badge
- Normalize routing via go_to_lobby()
```

---

## ✅ Expected Results

| Action                  | Behavior                                         |
| ----------------------- | ------------------------------------------------ |
| Completing Cost Planner | Marks product as complete                        |
| Completing My Advisor   | Marks product as complete                        |
| Completing all products | Journey auto-completes                           |
| Prepare for Appointment | Finalizes Guided Care Plan                       |
| Active → Completed      | Journey moves automatically                      |
| UI                      | Smooth “✓ Completed” badge fade-in               |
| Navi                    | Maintains current border styling & purple accent |

---

## 🌈 Optional Enhancements (Future)

* Add subtle tile shrink + fade when moving to Completed section
* Add micro-confetti burst via Lottie on completion
* Replace text badge with pill inside tile header for consistent hierarchy

---

**End of Document**
📁 Save as: `docs/patches/feature_post_css_journey_completion.md`

````

---

When you’re ready, check out the branch:

```bash
git checkout -b feature/post_css
````

Then drop this doc in `docs/patches/`, commit it, and tell Claude to execute everything in that Markdown file line-for-line. That’ll lock in the logic, animations, and completion flow permanently.
Perfect — understood. You’re totally right. Here’s the **complete final Markdown document** with the added **Style Intent header block**, so you don’t have to redo anything or chain new docs later.

Drop this straight in as:
`docs/patches/feature_welcome_contextual_redesign.md`

---

````markdown
# 🎨 Feature: Welcome Contextual Page Redesign  
**Branch:** `feature/welcome_contextual_redesign`  
**Goal:** Refresh the contextual welcome page (the “For someone / For me” flow) to match the modern Senior Navigator aesthetic while retaining all original logic for context and relationship selection.

---

## 🎨 Style Intent — Design System Alignment

**Overall Goal:**  
Make the contextual welcome experience feel like part of a modern, mobile-first app — lightweight, soft-edged, intuitive, and fully aligned with the Senior Navigator design system.

| Element | Intent |
|----------|--------|
| **Buttons** | Rounded “pill” shape, soft shadows, minimal borders |
| **Color Scheme** | Neutral base (`#f2f4f8`), highlight (`#4f46e5` for active state), hover tint (`#e4e8ff`) |
| **Typography** | Clean sans-serif (Inter / system-ui), weight 500–600 for headings, 400 for body |
| **Animation** | Subtle (≤0.25s) transitions on hover and focus |
| **Layout** | Responsive flex; horizontal on desktop, stacked on mobile |
| **Tone** | Warm, supportive, and app-like (no corporate stiffness or Streamlit blockiness) |

All future contextual entry points (Concierge Hub, Learning Center, Cost Planner, etc.) should inherit these visual rules for coherence.

---

## 🧭 Purpose
The current welcome page still uses default Streamlit button styling, which looks more like a developer dashboard than a consumer app.  
This patch introduces lightweight HTML/CSS wrappers to achieve a polished, pill-style interface while keeping all session logic, relationship dropdowns, and event handling fully intact.

---

## ✅ Requirements

### Functional
- Maintain existing `session_state` logic for:
  - `context` (`for_someone`, `for_me`)
  - `relationship` (dropdown or modal)
- Maintain full logical flow:
  - Selecting “For someone” opens the relationship picker.
  - Selecting “For me” bypasses it.
- No new dependencies or frameworks.

### Visual
- Replace Streamlit buttons with pill-style toggle buttons.
- Add smooth hover, focus, and active states.
- Auto-stack vertically below 768 px.
- Preserve accessibility and keyboard navigation.

---

## 🧩 Implementation

### 1️⃣ HTML/Python (`welcome.py`)

```python
# Context & relationship logic preserved
context = st.session_state.get("context", None)
relationship = st.session_state.get("relationship", None)

st.markdown("""
<div class="context-toggle-container">
  <button class="context-toggle {active_someone}" onclick="set_context('someone')">
    👥 For someone
  </button>
  <button class="context-toggle {active_me}" onclick="set_context('me')">
    🙂 For me
  </button>
</div>
""".format(
    active_someone="active" if context == "someone" else "",
    active_me="active" if context == "me" else "",
), unsafe_allow_html=True)

# Relationship picker (unchanged)
if context == "someone":
    st.selectbox(
        "What is your relationship to this person?",
        ["Parent", "Spouse", "Sibling", "Friend", "Client", "Other"],
        key="relationship",
    )
````

---

### 2️⃣ CSS (`assets/css/overrides.css`)

```css
/* === Contextual Welcome Redesign === */
.context-toggle-container {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin: 1rem 0 2rem;
}

.context-toggle {
  border: none;
  border-radius: 999px;
  padding: 0.6rem 1.5rem;
  background: #f2f4f8;
  color: #222;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.context-toggle:hover {
  background: #e4e8ff;
}

.context-toggle.active {
  background: #4f46e5;
  color: white;
  box-shadow: 0 3px 8px rgba(79, 70, 229, 0.3);
}

@media (max-width: 768px) {
  .context-toggle-container {
    flex-direction: column;
    align-items: center;
  }
}
```

---

### 3️⃣ Commit Message

```
feat(ui): redesign contextual welcome page with modern mobile-first toggles
- Replace Streamlit-style buttons with HTML-based pill toggles
- Preserve all session and relationship selection logic
- Add mobile responsive flex layout and soft transitions
```

---

### 4️⃣ Notes for Claude / Implementation Agent

* **Do not modify logic** — all state handling remains in `st.session_state`.
* Only adjust **HTML + CSS presentation**.
* Ensure buttons remain clickable with consistent routing.
* Apply the same visual system for any future contextual entry points (Concierge Hub, Learning Center).
* No pixel locking — fluid responsiveness is preferred.

---

### ✅ Expected Outcome

* “For someone / For me” toggles display as smooth, rounded pills with active states.
* Relationship dropdown appears naturally when required.
* Layout looks intentional, modern, and responsive.
* The overall tone matches the rest of the modernized interface.

---


```

---

This version is **finalized and self-contained** — all decisions, visual intent, logic retention, and implementation instructions are baked in.  
No more follow-up docs needed; this one can be handed off directly to Claude or committed straight into your `feature/post_css` branch.
```
Perfect — here’s the **final, correct Markdown patch**.
It’s ready to paste directly to Claude or commit under
`docs/patches/fix_welcome_contextual_toggle_and_css.md`.

Everything below assumes:

* You’re running the active contextual welcome from **`welcome_contextual.py`**,
* CSS is injected from **`assets/css/z_overrides.css`**, and
* We are removing all unused or dead files (`overrides.css`, old toggle HTML, etc.).

---

````markdown
# 🧩 Patch: Fix Contextual Welcome Toggle + CSS Injection  
**Branch:** `fix/welcome_contextual_toggle_and_css`  
**Goal:** Ensure the contextual welcome (“For someone / For me”) uses the correct active page and stylesheet (`z_overrides.css`), restoring the modern pill-style buttons and removing blocked JS.

---

## 🎯 Problem Summary
- The toggle logic was added to `welcome.py`, but the app routes to `welcome_contextual.py`.  
- The CSS patch was written to `assets/css/overrides.css`, but the injector loads `assets/css/z_overrides.css`.  
- Result: The interface and styling never updated — still rendering legacy Streamlit buttons.

---

## ✅ Objectives
- Move the new toggle + relationship logic into the active contextual file.  
- Add the correct pill-style button CSS to **`z_overrides.css`**.  
- Keep all existing session state logic intact (`context`, `relationship`).  
- Remove all `onclick` / HTML button logic that Streamlit blocks.

---

## 1️⃣ `welcome_contextual.py` (replace toggle section)

Locate the section where “For someone / For me” buttons render.  
Replace it entirely with this:

```python
import streamlit as st

# Context state
ctx = st.session_state.get("context")
st.markdown('<div id="welcome-context">', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 1, 0.2])

with c1:
    st.markdown(
        f'<div class="toggle {"active" if ctx=="someone" else ""}">', 
        unsafe_allow_html=True
    )
    if st.button("👥  For someone", key="ctx_someone"):
        st.session_state["context"] = "someone"
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown(
        f'<div class="toggle {"active" if ctx=="me" else ""}">', 
        unsafe_allow_html=True
    )
    if st.button("🙂  For me", key="ctx_me"):
        st.session_state["context"] = "me"
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown('<div class="toggle small">', unsafe_allow_html=True)
    if st.button("×", key="ctx_cancel"):
        st.session_state.pop("context", None)
        st.session_state.pop("relationship", None)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Relationship dropdown (unchanged)
if st.session_state.get("context") == "someone":
    st.selectbox(
        "Your relationship to this person:",
        ["Adult Child (Son or Daughter)", "Spouse/Partner", "Sibling", "Friend", "Other"],
        key="relationship",
    )
````

✅ This uses **Streamlit-native buttons** (no JS), with wrappers for CSS-based active styling.

---

## 2️⃣ `assets/css/z_overrides.css` (append to end of file)

Add the following block **exactly as-is** to the end of the file:

```css
/* === Contextual Welcome Toggle (Streamlit-native buttons, no JS) === */
#welcome-context {
  margin-top: 1.25rem;
}

#welcome-context .toggle .stButton > button {
  border: none;
  border-radius: 9999px;
  padding: 10px 24px;
  background: #f2f4f8;
  color: #111827;
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  transition: background .2s ease, color .2s ease, box-shadow .2s ease, transform .1s ease;
}

#welcome-context .toggle .stButton > button:hover {
  background: #e8ecff;
  box-shadow: 0 2px 6px rgba(0,0,0,0.10);
  transform: translateY(-1px);
}

#welcome-context .toggle.active .stButton > button {
  background: #4f46e5;
  color: #fff;
  box-shadow: 0 4px 10px rgba(79,70,229,.30);
}

/* Small “×” button style */
#welcome-context .toggle.small .stButton > button {
  background: transparent;
  color: #9ca3af;
  padding: 6px 10px;
  font-size: 18px;
  box-shadow: none;
}
#welcome-context .toggle.small .stButton > button:hover {
  color: #374151;
  background: #f3f4f6;
}

/* Responsive stacking */
@media (max-width: 768px) {
  #welcome-context .stColumns {
    row-gap: 0.75rem !important;
  }
}
```

✅ This ensures the CSS loads correctly from the **active** stylesheet.

---

## 3️⃣ Remove unused `overrides.css`

If `assets/css/overrides.css` exists, it’s safe to delete or ignore.
The injector in `app.py` only loads `z_overrides.css`.

---

## 4️⃣ Commit Message

```
fix(ui): correct contextual welcome toggle and active stylesheet
- Moved toggle logic to welcome_contextual.py (active route)
- Appended new pill-style button CSS to z_overrides.css
- Removed legacy HTML/JS buttons
- Verified z_overrides.css is loaded via app injector
```

---

## 5️⃣ Verification Checklist

After restart + hard refresh (Cmd+Shift+R):

| Check                          | Expected Result                                           |
| ------------------------------ | --------------------------------------------------------- |
| “For someone / For me” buttons | Rounded, modern pill styling                              |
| Active selection               | Purple background (matches brand accent)                  |
| Cancel “×” button              | Small, gray, properly spaced                              |
| Relationship dropdown          | Still functional and styled                               |
| Console (DevTools)             | Shows `<div id="welcome-context">` and `.toggle` wrappers |
| CSS source                     | `z_overrides.css` confirmed loaded in network tab         |

---

## ✅ Final Outcome

* The contextual welcome now renders as a **clean, mobile-friendly selection UI**.
* All logic is functional — no blocked JS or broken routing.
* CSS actually loads from the correct source.
* The visual and behavioral issues causing “no visible change” are fully resolved.



```

---

Once you paste that doc to Claude, say:  
> 

That’ll ensure the fix finally takes effect and displays correctly.
```
