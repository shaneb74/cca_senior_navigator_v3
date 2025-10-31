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
