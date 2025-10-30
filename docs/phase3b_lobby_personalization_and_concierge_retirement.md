Perfect — that’s exactly the right next milestone.
Here’s the **complete, ready-to-use Markdown brief** for this step, written in the same clean format as your previous ones.

Save it as:
📄 `docs/phase3b_lobby_personalization_and_concierge_retirement.md`

---

```markdown
# Phase 3B — Lobby Personalization, Product Outcomes, and Concierge Retirement

**Date:** 2025-10-29  
**Branch:** `feature/lobby-personalization`  
**Owner:** Concierge Care Advisors / Senior Navigator  
**Purpose:**  
Finalize the Lobby Hub as the *central control center* for the Senior Navigator experience — integrating personalized NAVI guidance, live product outcomes, and preparing to retire the legacy Concierge Hub.

---

## 🎯 Objective

1. Replace the **Concierge Hub** with the **Lobby Hub** as the new user home.  
2. Integrate **personalized NAVI** experience into Lobby.  
3. Surface **product outcomes** directly on tiles for at-a-glance status.  
4. Clean up redundant visual elements (e.g., page titles).  
5. Ensure all navigation, progress, and dynamic product states work seamlessly.

---

## 🧩 Files & Structure

Files affected:
```

/pages/hub_lobby.py
/core/navi.py
/core/products.py
/core/engine.py
/core/mcip.py
/core/nav.json

```

Files deprecated after merge:
```

/pages/hub_concierge.py

````

> ⚠️ Do not delete the Concierge Hub yet — mark as **deprecated** and redirect all routes to Lobby after successful verification.

---

## 🧠 Components

### 1. Remove Redundant Page Title
Remove or comment out:
```python
st.title("Senior Navigator Dashboard")
````

The NAVI header now provides the contextual title and should be the primary visual anchor.

---

### 2. Integrate Personalized NAVI (from Concierge)

Replace the older NAVI calls in `hub_lobby.py`:

```python
from core.navi import render_navi_panel, render_progress
```

With:

```python
from core.navi import render_navi_context
render_navi_context(context="lobby")
```

Requirements:

* Must use the same personalized layout as in Concierge (Phase 3 NAVI style).
* Pull in:

  * User name (“Hi, [FirstName]”)
  * Current step and product completion status
  * Progress bar
  * Primary CTAs (e.g., “Calculate Your Care Costs”, “Ask NAVI”)

NAVI should be **consistent across Lobby and Concierge** to allow seamless replacement.

---

### 3. Display Product Outcomes

Each product tile must show its latest result, based on session state or stored data.

Add this function in `core/products.py`:

```python
def get_product_outcome(product_key: str) -> str:
    """Return outcome summary for the given product."""
    outcomes = st.session_state.get("product_outcomes", {})
    return outcomes.get(product_key, "")
```

Then, modify Lobby tile rendering:

```python
outcome = get_product_outcome(product_key)
if outcome:
    st.markdown(f"<p class='tile-outcome'>{outcome}</p>", unsafe_allow_html=True)
```

#### Outcome Mapping

| Product              | Example Outcome                      |
| -------------------- | ------------------------------------ |
| Guided Care Plan     | “Recommended: Assisted Living”       |
| Cost Planner         | “Estimated cost: $4,500/mo”          |
| Plan With My Advisor | “Next meeting: Nov 3, 10:00am”       |
| AI Advisor (NAVI)    | Always available — “Ask NAVI” button |

---

### 4. Unlock AI Advisor (NAVI)

Update MCIP gating logic:

```python
def get_product_state(product_key: str) -> str:
    if product_key == "ai_advisor":
        return "available"
```

Ensure NAVI is always unlocked and accessible from both the Lobby and all product flows.

---

### 5. Layout Cleanup & Grid Consistency

* Maintain two-column grid for product tiles.
* Ensure NAVI header is flush with top padding.
* “Additional Services” remains at the bottom.
* Confirm hover lift and shadow effects remain per `/core/styles/dashboard.css`.

---

### 6. Redirect Concierge → Lobby

Once visual and functional parity is confirmed:

1. Update `core/nav.json`:

   ```json
   {
     "hubs": [
       { "label": "Lobby", "route": "hub_lobby", "default": true }
     ]
   }
   ```
2. Mark `/pages/hub_concierge.py` as deprecated.
3. Add inline comment:

   ```python
   # DEPRECATED: Functionality migrated to hub_lobby.py (Phase 3B)
   ```

All routes and session restores should direct to the Lobby going forward.

---

## 🧪 Verification Checklist

| Step | Expected Result                                             |
| ---- | ----------------------------------------------------------- |
| 1    | Lobby loads automatically (no manual URL required)          |
| 2    | Personalized NAVI header visible, matches Concierge styling |
| 3    | “Dashboard” title removed                                   |
| 4    | Product tiles show correct outcomes                         |
| 5    | AI Advisor tile is always active                            |
| 6    | Additional Services still renders at bottom                 |
| 7    | Concierge routes correctly redirect to Lobby                |
| 8    | No regressions in MCIP or dynamic loading                   |
| 9    | Layout alignment and white background preserved             |

---

## 🚫 Restrictions for Claude

* ❌ Do not modify CSS files (other than class references if necessary).
* ❌ Do not alter MCIP logic beyond adding AI Advisor override.
* ❌ Do not delete Concierge Hub code — mark as deprecated only.
* ✅ Use existing NAVI personalization helpers from Concierge.
* ✅ Preserve modular architecture (no hard-coded imports).
* ✅ Add docstrings and type hints for new or modified functions.

---

## ✅ Expected Outcome

| Component            | Result                                                                                   |
| -------------------- | ---------------------------------------------------------------------------------------- |
| **Lobby Hub**        | Becomes new personalized home hub                                                        |
| **NAVI Integration** | Matches Concierge design and function                                                    |
| **Product Tiles**    | Display live outcomes and statuses                                                       |
| **AI Advisor**       | Always available and interactive                                                         |
| **Concierge Hub**    | Retired and redirected                                                                   |
| **System**           | Unified, clean, and production-ready foundation for Phase 4 (Waiting Room consolidation) |

---

**End of Document**
