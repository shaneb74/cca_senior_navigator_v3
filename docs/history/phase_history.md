Perfect. I’ve got you — here’s the **entire file**, no breaks, no missing sections, no confusion.
Copy **everything below from start to end** and give that to Claude **exactly as-is**.

---

```markdown
# Phase 1A — Lobby Visual Overhaul (CSS Lockdown)

**Date:** 2025-10-29  
**Branch:** `feature/lobby-dashboard`  
**Owner:** Concierge Care Advisors / Senior Navigator  
**Purpose:** Align the *Lobby Hub* visual design with the modernized dashboard style shown in the design reference (v3.2.x).  
**Primary Goal:** Achieve visual consistency — *no logic, routing, or functionality changes.*

---

## 🎯 Objective

Visually modernize the **Lobby Hub (hub_lobby.py)** to match the Senior Navigator design system:
- White background (no gray or gradients)
- Compact, elevated cards
- Consistent typography with `Welcome.py`
- Rounded edges and pill buttons
- Minimal flicker and visual noise
- Maintain all existing page logic, session state, and routing

This update affects **styling only** — not content, data flow, or navigation.

---

## 🧩 File Additions & Structure

Create the following new file:

```

/core/styles/dashboard.css

````

Ensure it is committed to the repository and accessible to all Streamlit pages.

---

## 🎨 CSS SPECIFICATION

```css
/* =======================================
   Senior Navigator — Lobby Dashboard CSS
   ======================================= */

/* ---------- GLOBAL RESET ---------- */
html, body, [data-testid="stAppViewContainer"] {
  background-color: #ffffff !important;
  font-family: "Inter", "Helvetica Neue", sans-serif;
  color: #1e1e1e;
}

/* ---------- CARD GRID ---------- */
.dashboard-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.dashboard-card {
  background: #ffffff;
  border: 1px solid #E6E6E6;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  transition: all 0.2s ease-in-out;
}
.dashboard-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0,0,0,0.08);
}

/* ---------- BUTTONS ---------- */
.btn-pill {
  display: inline-block;
  background-color: #1E5BD7;
  color: #fff !important;
  padding: 0.4rem 1.2rem;
  border-radius: 9999px;
  font-weight: 500;
  border: none;
  transition: all 0.2s ease;
}
.btn-pill:hover { background-color: #154ab0; }

/* ---------- HEADERS ---------- */
h2, h3 {
  font-weight: 700;
  color: #0A1E4A;
  margin-bottom: 0.5rem;
}
.subtext {
  color: #5F6368;
  font-size: 0.9rem;
}

/* ---------- GRADIENT BOX (for FAQ section) ---------- */
.gradient-box {
  background: linear-gradient(135deg, #BFD8FF 0%, #F3D6FF 100%);
  color: #1E1E1E;
  border: none;
}
````

---

## ⚙️ Integration Steps

> These steps are for Claude’s implementation. Do **not** alter logic or routing — apply structure and CSS only.

### 1. Import the CSS in `hub_lobby.py`

Add this near the top of the file, after imports:

```python
st.markdown(
    f"<style>{open('core/styles/dashboard.css').read()}</style>",
    unsafe_allow_html=True
)
```

This ensures the new dashboard styles load when the Lobby page is rendered.

---

### 2. Wrap Existing Product Tiles

Use this structure to render cards with consistent styling:

```python
with st.container():
    st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)

    # Card 1: Guided Care Plan
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.subheader("Guided Care Plan")
    st.markdown('<p class="subtext">Explore and compare care options.</p>', unsafe_allow_html=True)
    st.markdown('<button class="btn-pill">Start</button>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Card 2: Cost Planner
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.subheader("Cost Planner")
    st.markdown('<p class="subtext">Estimate and plan financial coverage.</p>', unsafe_allow_html=True)
    st.markdown('<button class="btn-pill">Start</button>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Card 3: Plan With My Advisor
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.subheader("Plan With My Advisor")
    st.markdown('<p class="subtext">Schedule and prepare for your next advisor meeting.</p>', unsafe_allow_html=True)
    st.markdown('<button class="btn-pill">Open</button>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Card 4: FAQs & Answers
    st.markdown('<div class="dashboard-card gradient-box">', unsafe_allow_html=True)
    st.subheader("FAQs & Answers")
    st.markdown('<p class="subtext">Instant help from NAVI AI.</p>', unsafe_allow_html=True)
    st.markdown('<button class="btn-pill">Open</button>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
```

---

### 3. Verify Before Commit

Before committing:

* Confirm the background is **pure white (#ffffff)**.
* Ensure cards use soft shadows with hover lift.
* Verify no layout flicker between page loads.
* Confirm all routing remains functional.
* Test in Chrome and Safari.

---

### ✅ Expected Output

Once applied:

* The Lobby Hub visually matches the Senior Navigator design.
* The look aligns with **Welcome.py** and upcoming dashboard refactors.
* The structure will serve as the foundation for **Phase 1B** (interactive tile behavior).

---

**End of Document**

```
```
Perfect 👌 — great call. This will keep Claude on the rails and protect all the careful work you’ve already locked down.

Here’s the **complete, one-file Markdown brief** for Phase 2B.
Just drop this into your repo as `docs/phase2b_dynamic_module_system.md` and tell Claude to follow it *exactly*.

---

```markdown
# Phase 2B — Dynamic Module System (Architecture Integration)

**Date:** 2025-10-29  
**Branch:** `feature/dynamic-module-system`  
**Owner:** Concierge Care Advisors / Senior Navigator  
**Purpose:** Implement a dynamic “Lobby → Product → Module” hierarchy that automatically loads product modules without hard-coded imports.  
**Primary Goal:** Introduce modular rendering logic only — no visual, CSS, or routing changes.

---

## 🎯 Objective

Create a **lightweight registry system** so that:
- The Lobby renders product tiles dynamically (complete from Phase 2A).  
- Each product page renders its modules automatically via a shared registry.  
- The system is extensible — adding a new module requires no manual imports or page updates.  

**Absolutely no:**
- CSS edits  
- Changes to NAVI, header, or footer  
- Removal of existing module logic  

---

## 🧩 Files & Structure

New file:  
```

/core/modules_registry.py

```

Modified files:  
```

/core/products.py
/pages/hub_lobby.py
/pages/product_guided_care_plan.py
/pages/product_cost_planner.py
/pages/product_plan_with_my_advisor.py

````

---

## 🧱 System Design

### 1. Module Registry

`core/modules_registry.py`
```python
# =====================================
#  Senior Navigator — Module Registry
# =====================================
from typing import Callable, Dict

# Registry maps product_key → list[module_render_functions]
MODULE_REGISTRY: Dict[str, list[Callable]] = {}

def register_module(product_key: str, render_fn: Callable):
    """Register a module render() function under a product."""
    MODULE_REGISTRY.setdefault(product_key, []).append(render_fn)

def get_modules_for_product(product_key: str):
    """Return all render functions for a product."""
    return MODULE_REGISTRY.get(product_key, [])
````

Each module registers itself with a simple call in its `__init__.py`:

```python
from core.modules_registry import register_module
from . import render as render_fn
register_module("cost_planner", render_fn)
```

---

### 2. Render Integration in `core/products.py`

Add:

```python
from core.modules_registry import get_modules_for_product

def render_product(product_key: str):
    """Render all modules associated with a product."""
    modules = get_modules_for_product(product_key)
    if not modules:
        st.info("No modules registered for this product.")
        return
    for render_fn in modules:
        try:
            render_fn()
        except Exception as e:
            st.error(f"Error rendering module: {e}")
```

---

### 3. Update Product Pages

Example (`pages/product_guided_care_plan.py`):

```python
import streamlit as st
from core.products import render_product

def render():
    st.title("Guided Care Plan")
    render_product("guided_care_plan")
```

Repeat for Cost Planner and Plan With My Advisor.

---

### 4. Preserve Lobby Behavior

Ensure `hub_lobby.py` still renders product tiles using the current dynamic tile loading logic from Phase 2A.
Do not change button actions or routes.

---

## 🧪 Verification Checklist

| Step | Expected Result                                                      |
| :--: | :------------------------------------------------------------------- |
|   1  | Run `streamlit run app.py`                                           |
|   2  | Go to `?page=hub_lobby` → Products display normally                  |
|   3  | Click Guided Care Plan → All associated modules render automatically |
|   4  | Click Cost Planner → Financial Assessment modules load               |
|   5  | Click Plan With My Advisor → Scheduling modules load                 |
|   6  | No CSS or layout changes                                             |
|   7  | No errors in console/logs                                            |

---

## 🚫 Restrictions for Claude

* ❌ Do not modify any existing module logic or render functions.
* ❌ Do not touch `core/nav.py` or `app.py`.
* ❌ No changes to visual presentation or CSS.
* ✅ Commit only to files listed above.
* ✅ Ensure imports are explicit and relative (paths must work in the existing package structure).
* ✅ All new functions must include docstrings and type hints.

---

## 🧾 Deliverables

| File                              | Lines | Purpose                            |
| --------------------------------- | ----- | ---------------------------------- |
| `core/modules_registry.py`        | ~40   | Registry system for module mapping |
| `core/products.py`                | +25   | Render integration                 |
| `product_guided_care_plan.py`     | +10   | Dynamic render hook                |
| `product_cost_planner.py`         | +10   | Dynamic render hook                |
| `product_plan_with_my_advisor.py` | +10   | Dynamic render hook                |

Total change: ≈ 95 lines.

---

## ✅ Expected Outcome

* Lobby Hub stays visually identical.
* Product pages load their modules automatically.
* Future modules can be added with a single registration call.
* Architecture prepares for Phase 3 (interactive tile states and progress sync).

---

Perfect — here’s your **Phase 2B Addendum Brief**, designed to append directly to the bottom of your existing Markdown file
(`docs/phase2b_dynamic_module_system.md`).
Copy everything below and paste it *after* the last line of the current document.

---

````markdown
---

# 🔧 Phase 2B Addendum — Adaptation to Existing Architecture

**Revision Date:** 2025-10-29  
**Purpose:** Align the Dynamic Module System design with the *existing* Senior Navigator architecture (engine-based module discovery and JSON configs).

---

## 🧠 Context

During Phase 2B review, it was identified that the repository **already includes**:
- `core/engine.py` → Handles dynamic module discovery and loading  
- `products/*/modules/*/config.py` → JSON-driven module definitions  
- `core/base.py` → Central rendering pipeline for modules  

Because this architecture already provides a dynamic system, Phase 2B must **adapt**—not replace—the existing logic.

---

## 🧩 Implementation Scope (Adapted)

### 1. Extend Existing Engine

- Add a new helper in `core/engine.py`:
  ```python
  def load_modules_for_product(product_key: str):
      """Return module metadata + render functions for a given product."""
      # Reuse existing discovery logic to filter by product_key
      ...
````

* This should reference each product’s existing `config.py` for module order, titles, and visibility flags.

### 2. Update Lobby → Product → Module Integration

* In `hub_lobby.py`:
  Replace any temporary static lists with calls to
  `engine.load_modules_for_product(product_key)`
* In `core/products.py`:
  Use `engine.load_modules_for_product()` inside `render_product()`
  instead of manual imports or registries.
* Ensure product pages (`guided_care_plan`, `cost_planner`, `plan_with_my_advisor`) call `render_product()` unchanged.

### 3. JSON Schema Consistency

* Do **not** change the existing JSON schema in `config.py`.
* Maintain backwards compatibility with current keys:

  ```json
  {
    "module_id": "financial_assessment",
    "title": "Financial Assessment",
    "enabled": true,
    "weight": 10
  }
  ```

### 4. No New Files

❌ Do *not* create `modules_registry.py`.
✅ Modify only:

```
core/engine.py
core/products.py
pages/hub_lobby.py
pages/product_*.py
```

---

## 🧪 Verification Checklist

| Step | Expected Result                                                             |
| ---- | --------------------------------------------------------------------------- |
| 1    | Lobby displays product tiles dynamically (unchanged UI)                     |
| 2    | Each product page loads its modules via `engine.load_modules_for_product()` |
| 3    | No hard-coded imports remain in `products.py` or product pages              |
| 4    | Existing module configs load normally                                       |
| 5    | No changes to CSS or visual layout                                          |
| 6    | No runtime errors in logs                                                   |

---

## 🧭 Developer Notes

* This update is an **architectural alignment**, not a refactor.
* Focus on integration within existing APIs and data structures.
* Keep commit scope tight (≈ 40–60 lines modified across 4 files).
* Include docstrings and type hints for any new functions.

---

**End of Addendum**

```

---

# ✅ Implementation Status

**Date Implemented:** 2025-10-29  
**Branch:** `feature/dynamic-module-system`  
**Status:** **COMPLETE**

## Summary

After architectural review, it was determined that the Senior Navigator codebase **already implements** the dynamic module system described in Phase 2B. The existing architecture provides:

### ✅ Already Implemented

1. **Dynamic Module Engine** (`core/modules/engine.py`)
   - `run_module(config)` - Handles module execution and navigation
   - `load_modules_for_product(product_key)` - NEW: Explicit module discovery helper
   - JSON-driven module configurations (`products/*/modules/*/config.py`)

2. **Dynamic Product Tiles** (`hubs/hub_lobby.py`)
   - Uses `ProductTileHub` objects (not hard-coded)
   - Tiles registered in `config/nav.json`
   - Dynamic routing via `?page=` query params

3. **Module-to-Product Integration** (`products/concierge_hub/*/product.py`)
   - Products call `run_module(config)` from engine
   - No manual module imports required
   - State management handled by engine

### 📝 Changes Made

| File | Lines | Change |
|------|-------|--------|
| `core/modules/engine.py` | +97 | Added `load_modules_for_product()` helper for explicit discovery |
| `hubs/hub_lobby.py` | +11 | Added architecture documentation in docstring |

**Total**: +108 lines (documentation + 1 new helper function)

### 🧪 Verification

- ✅ Lobby renders product tiles dynamically
- ✅ Products load modules via engine (GCP, Cost Planner, PFMA)
- ✅ No hard-coded imports or registries
- ✅ Module configs load from JSON
- ✅ Navigation works via `config/nav.json`

### 📋 Conclusion

The dynamic module system architecture **was already complete**. Phase 2B requirements were met by the existing `core/modules/engine.py` system. The new `load_modules_for_product()` function makes the dynamic architecture more explicit for future developers but does not change any runtime behavior.

**No breaking changes. No CSS changes. No visual changes.**

---

**End of Implementation Notes**

```

---

Once added, just tell Claude:

> “Please follow the *Phase 2B Addendum* section in `docs/phase2b_dynamic_module_system.md` — adapt to the existing `engine.py`-based architecture as specified.”

That will keep him perfectly aligned with your live architecture and prevent redundant systems.
```


**End of Document**


```
Perfect. Here’s the **complete Markdown brief** for the next step — fully ready for Claude.
Save this as:
📄 `docs/phase3a_navi_lobby_integration.md`

---

```markdown
# Phase 3A — NAVI Integration + Additional Services + MCIP Product Flow Logic

**Date:** 2025-10-29  
**Branch:** `feature/lobby-navi-integration`  
**Owner:** Concierge Care Advisors / Senior Navigator  
**Purpose:** Transform the Lobby Hub into the central, guided user experience — integrating NAVI, dynamic product availability (via MCIP logic), and the “Additional Services” section.  

---

## 🎯 Objective

Enhance the Lobby (`hub_lobby.py`) to:
- Display **NAVI guidance + progress tracking** at the top of the page  
- Dynamically show available **Product Tiles** based on MCIP logic  
- Include a new **Additional Services** section at the bottom (ported from Concierge)  
- Maintain Phase 1A/2A visual consistency and dynamic loading (no regressions)

---

## 🧩 Files & Structure

Files affected:
```

/pages/hub_lobby.py
/core/engine.py
/core/mcip.py
/core/navi.py
/core/products.py

````

No new files should be added in this phase.  
All changes must be integrated into existing modules and respect current architecture.

---

## 🧠 Components

### 1. NAVI Integration

Embed NAVI guidance and progress elements into the Lobby Hub layout.

```python
from core.navi import render_navi_panel, render_progress

def render():
    # --- NAVI Context ---
    render_navi_panel(context="lobby")
    render_progress(context="lobby")

    # --- Product Tiles (from engine) ---
    render_dynamic_products()
````

#### Requirements:

* Use existing NAVI helper functions; do **not** reimplement NAVI logic.
* NAVI must appear **above the product grid** and **below the header**.
* Use `.navi-panel` spacing (already defined in CSS).
* NAVI progress must reflect active MCIP completion status.

---

### 2. MCIP Logic — Product Availability

Integrate MCIP-based gating logic into product rendering.
Products must only appear when their MCIP tier is allowed.

Add to `core/engine.py`:

```python
from core.mcip import CareRecommendation

def get_available_products(context: dict) -> list:
    """Return list of product keys user is eligible for."""
    rec = CareRecommendation(context)
    return rec.allowed_tiers or []
```

Then in `hub_lobby.py`:

```python
allowed_products = engine.get_available_products(st.session_state)
render_dynamic_products(allowed=allowed_products)
```

#### Behavior:

* If `allowed_tiers` returns `['gcp', 'cost_planner']`, only those appear.
* “Plan with My Advisor” should unlock once both prior products complete.
* Ensure session context carries completion flags for each product.

---

### 3. Product Flow Logic (MCIP Integration)

Each product tile now carries a state:

| State       | Display                         |
| ----------- | ------------------------------- |
| `locked`    | Greyed-out tile with lock icon  |
| `available` | Active tile with "Start" button |
| `completed` | Highlighted checkmark overlay   |

Add a simple state determination in `core/products.py`:

```python
def get_product_state(product_key: str) -> str:
    if product_key in st.session_state.get("completed_products", []):
        return "completed"
    elif product_key in st.session_state.get("available_products", []):
        return "available"
    return "locked"
```

Visuals remain consistent — use a light overlay and icon glyphs only (no new CSS colors).

---

### 4. Additional Services Section

At the end of the Lobby, port the existing section from `hub_concierge.py`:

```python
def render_additional_services():
    st.markdown("### Explore More Services")
    st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)

    services = [
        {"title": "Clinical Review", "desc": "Discuss health conditions and care options", "route": "clinical_review"},
        {"title": "Trusted Partners", "desc": "Connect with vetted local providers", "route": "trusted_partners"},
        {"title": "VA & Benefits", "desc": "Explore veterans’ benefit assistance", "route": "va_benefits"}
    ]

    for s in services:
        st.markdown(f'''
            <div class="dashboard-card">
              <h3>{s["title"]}</h3>
              <p class="subtext">{s["desc"]}</p>
              <button class="btn-pill" onclick="window.location.href='?page={s["route"]}'">Open</button>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
```

Append this after the product grid render in `hub_lobby.py`.

---

## ⚙️ Implementation Sequence

1. **Enable NAVI Context**
   Add NAVI render calls to the top of the Lobby.
2. **MCIP Gating**
   Integrate `get_available_products()` from `core/engine.py`.
3. **Tile State Logic**
   Apply state-dependent rendering (locked, available, completed).
4. **Render Additional Services**
   Port the Concierge section exactly as shown above.
5. **Verify Session Persistence**
   Confirm state transitions when completing modules (MCIP context updates allowed_tiers).

---

## 🧪 Verification Checklist

| Step                | Expected Result                                  |
| ------------------- | ------------------------------------------------ |
| Load Lobby          | NAVI visible and progress bar active             |
| MCIP Context        | Only eligible products displayed                 |
| Locked State        | Non-eligible tiles appear dimmed                 |
| Completed State     | Tiles show “Completed” styling                   |
| Additional Services | Section visible with working routes              |
| Visual              | Layout matches Phase 1A white-background design  |
| Performance         | No flicker or layout shifts                      |
| Routing             | All buttons route correctly through `route_to()` |

---

## 🚫 Restrictions for Claude

* ❌ No CSS or layout changes outside `dashboard.css` rules
* ❌ Do not modify `base.py` or NAVI logic
* ❌ Do not remove Concierge code
* ✅ Add docstrings + type hints for all new functions
* ✅ Ensure compatibility with existing JSON-driven module structure

---

## ✅ Expected Outcome

| Component               | Result                                   |
| ----------------------- | ---------------------------------------- |
| **Lobby**               | Now includes NAVI + progress tracker     |
| **Product Tiles**       | MCIP-controlled availability and states  |
| **Additional Services** | Displayed dynamically at bottom          |
| **User Experience**     | Seamless single hub for all interactions |
| **System Architecture** | Fully unified, dynamic, and extensible   |

---

**End of Document**

```

---

Once saved, tell Claude:
> “Follow the `docs/phase3a_navi_lobby_integration.md` brief exactly — include NAVI integration, MCIP-based gating, and the Additional Services section.”  

This keeps the next phase structured, precise, and architecturally consistent.
```
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
```markdown
# Phase 3C — Lobby Finalization & Navigation Cleanup

**Date:** 2025-10-29  
**Branch:** `feature/lobby-finalization`  
**Owner:** Concierge Care Advisors / Senior Navigator  
**Purpose:** Remove legacy duplication between *Lobby* and *Dashboard*, finalize navigation routes, and confirm full transition from the retired Concierge Hub.

---

## 🎯 Objective

Ensure that:
- The **Lobby** is the single unified hub (replacing Dashboard and Concierge).
- All navigation routes, returns, and highlights correctly point to the Lobby.
- Only one active tab (“Lobby”) appears highlighted in the top navigation.
- All product tiles and modules route back to Lobby.

---

## 🧩 Files & Structure

Modified files:

```

/core/nav.py
/core/nav.json
/core/routing.py (if applicable)
/pages/hub_lobby.py

````

---

## 🧱 Implementation Steps

### 1️⃣ Remove Duplicate “Dashboard” Entry
In `/core/nav.json`:
- Keep **Lobby** entry:
  ```json
  {
    "key": "lobby",
    "title": "Lobby",
    "module": "pages.hub_lobby",
    "icon": "house"
  }
````

* Remove (or comment out) the **Dashboard** entry if it references `hub_lobby` or similar.

---

### 2️⃣ Update Active Highlight Logic

In `/core/nav.py`, update the highlight detection:

```python
# Old:
if current_page in ["lobby", "dashboard"]:
    highlight("Lobby")

# New:
if current_page == "lobby":
    highlight("Lobby")
```

✅ Result: Only “Lobby” will appear as the active tab.

---

### 3️⃣ Route Mapping Cleanup

Search across the repository for:

```python
route_to("dashboard")
```

and replace with:

```python
route_to("lobby")
```

This ensures:

* Guided Care Plan
* Cost Planner
* Advisor Prep / Plan with My Advisor
* AI Advisor

…all return to the Lobby page upon completion.

---

### 4️⃣ Default Page Behavior

In `/core/routing.py` or equivalent:

* Ensure that if a user logs in or reloads, they’re directed to **Lobby**, not Dashboard or Concierge.

Example:

```python
if user_authenticated and not current_page:
    route_to("lobby")
```

---

### 5️⃣ Navigation Order

Reorder `nav.json` so that “Lobby” appears right after “Welcome”:

```json
[
  { "key": "welcome", "title": "Welcome", "module": "pages.welcome" },
  { "key": "lobby", "title": "Lobby", "module": "pages.hub_lobby" },
  ...
]
```

---

## ✅ Verification Checklist

| Step | Expected Result                               |
| ---- | --------------------------------------------- |
| 1    | “Lobby” appears once in nav                   |
| 2    | No “Dashboard” tab visible                    |
| 3    | Lobby routes correctly from all product tiles |
| 4    | Only Lobby tab is highlighted when active     |
| 5    | `route_to("lobby")` works for all flows       |
| 6    | Default login → Lobby                         |
| 7    | NAVI header loads correctly on Lobby          |

---

## 🚫 Restrictions

* ❌ No CSS or UI changes (visuals are already approved).
* ❌ No new pages or routes.
* ✅ Only modify navigation and routing logic.
* ✅ All tests must pass before commit.
* ✅ Maintain `hub_lobby.py` as the single hub entry.

---

## 🧾 Deliverables

| File                  | Change                 | Purpose                     |
| --------------------- | ---------------------- | --------------------------- |
| `/core/nav.json`      | Remove Dashboard entry | Simplify nav                |
| `/core/nav.py`        | Update highlight logic | Proper tab highlighting     |
| `/core/routing.py`    | Update default route   | Lobby becomes default       |
| `/pages/hub_lobby.py` | Confirm return routing | Unified navigation endpoint |

---

### 🧠 Notes for Developer

Once merged:

* All prior references to “Concierge” or “Dashboard” should redirect to “Lobby”.
* The user should never see two highlighted tabs.
* This completes the **Concierge retirement** and **Lobby promotion**.

---

**End of Document**

```Perfect 👍 — here’s the **full Markdown brief** for Claude to follow exactly.

---

````markdown
# Phase 3C — Concierge Hub Retirement & Unified Lobby Routing

**Date:** 2025-10-29  
**Branch:** `feature/retire-concierge-hub`  
**Owner:** Concierge Care Advisors / Senior Navigator  
**Purpose:** Fully retire the legacy *Concierge Hub* and route all product modules and flows through the unified *Lobby Hub* (`hub_lobby.py`).  
**Primary Goal:** Simplify navigation, maintain NAVI continuity, and ensure all completion redirects return to the Lobby.

---

## 🎯 Objective

Remove `hub_concierge.py` and migrate all routing logic, session state, and NAVI context to the unified **Lobby Hub**.

This includes:
- Updating every product module to return to `hub_lobby` after completion.
- Repointing all NAVI and session references from “concierge” to “lobby”.
- Removing Concierge Hub from navigation and tests.

**This is a functional routing and context consolidation phase only.**  
No UI redesign or CSS modification.

---

## 🧩 Files to Modify

| File | Purpose |
|------|----------|
| `/pages/hub_concierge.py` | Archive (rename `_deprecated_hub_concierge.py`) |
| `/pages/hub_lobby.py` | Confirm dynamic routing integration |
| `/core/nav.json` | Remove `hub_concierge` entry, verify `hub_lobby` |
| `/core/routes.json` | Replace any `hub_concierge` references |
| `/core/progress.yaml` | Replace `"ConciergeHub"` with `"Lobby"` |
| `/core/guidance.yaml` | Update NAVI context mappings from “concierge” to “lobby” |
| `/products/*/modules/*` | Update all redirects and navigation targets |
| `/tests/test_hub_concierge.py` | Mark skipped or remove |
| `/tests/test_hub_lobby.py` | Add or expand routing coverage |

---

## 🔄 Redirect Mapping

### Update all `route_to()` or navigation calls

| Old Target | New Target |
|-------------|-------------|
| `route_to("hub_concierge")` | `route_to("hub_lobby")` |
| `page="hub_concierge"` | `page="hub_lobby"` |
| `url="?page=hub_concierge"` | `url="?page=hub_lobby"` |

Applies to:

- Guided Care Plan (end-of-flow summary)
- Cost Planner (post-calculation screen)
- Financial Assessments (after submit)
- Plan with My Advisor (appointment scheduled)
- AI Advisor (exit navigation)
- Any legacy “Back to Concierge” buttons or links

> ✅ **Use routing helper** — `route_to("hub_lobby")`  
> ❌ **No hard-coded URLs**

---

## 🧠 NAVI Context Migration

### In `guidance.yaml`
Replace:
```yaml
context: concierge
````

with:

```yaml
context: lobby
```

Ensure all relevant guidance prompts continue to work:

* Welcome back messages
* Empathy-based follow-ups
* Milestone triggers

### In `progress.yaml`

Rename any “ConciergeHub” entries to “LobbyHub” to maintain progress tracking continuity.

---

## 🗂️ Navigation Cleanup

### In `nav.json`

Remove the legacy Concierge entry:

```json
{
  "id": "hub_concierge",
  "label": "Concierge Hub",
  "module": "pages.hub_concierge",
  "group": "hubs"
}
```

Replace with:

```json
{
  "id": "hub_lobby",
  "label": "Dashboard",
  "module": "pages.hub_lobby",
  "group": "hubs"
}
```

### Breadcrumb & Button Updates

Search for:

* “Back to Concierge Hub”
* “Return to Concierge”
  Replace with:
* “Back to Dashboard”
* “Return to Lobby”

---

## 🧪 Testing Plan

### Functional Tests

| Area                         | Test                                               |
| ---------------------------- | -------------------------------------------------- |
| GCP → Lobby                  | Complete flow, verify redirect and NAVI continuity |
| Cost Planner → Lobby         | Validate navigation after calculation              |
| Financial Assessment → Lobby | Confirm proper return                              |
| Advisor → Lobby              | Return to dashboard after scheduling               |
| AI Advisor → Lobby           | Confirm non-locked access and correct routing      |

### Regression Tests

| Component | Expectation                                      |
| --------- | ------------------------------------------------ |
| NAVI      | Personalized responses persist through all flows |
| Session   | `_navi_context` and `_completed_pages` persist   |
| Progress  | Stage updates correctly from product to lobby    |
| Routing   | No broken links or blank screens                 |
| Visual    | Lobby loads white background, correct layout     |

### Cross-Browser

Confirm routing and NAVI behavior in:

* ✅ Chrome
* ✅ Safari

---

## 🚫 Restrictions

* ❌ Do not modify MCIP logic or scoring.
* ❌ Do not change product or module content.
* ❌ No CSS edits.
* ✅ Maintain all data flow and progress state.
* ✅ Keep NAVI identical across Lobby and modules.
* ✅ All redirects must pass automated tests.

---

## ✅ Deliverables

| File                           | Change                                   | Lines |
| ------------------------------ | ---------------------------------------- | ----- |
| `_deprecated_hub_concierge.py` | Archived file                            | —     |
| `hub_lobby.py`                 | Updated return targets, context handling | +25   |
| `nav.json`                     | Removed Concierge entry                  | -8    |
| `guidance.yaml`                | Updated context references               | +10   |
| `progress.yaml`                | Updated identifiers                      | +6    |
| `products/*`                   | Updated `route_to()` targets             | ~+40  |
| `tests/test_hub_lobby.py`      | Expanded coverage                        | +12   |

Estimated total: **~90–120 lines changed.**

---

## ✅ Expected Outcome

* The Concierge Hub is **fully retired.**
* All user flows return to the Lobby Hub.
* NAVI context and session state remain intact.
* The Lobby becomes the **single, unified user dashboard.**
* Codebase is ready for **Phase 4C — Contextual Learning & Optional Education Step.**

---

**End of Document**

```

---

Once this is in place:
1. Save it as → `docs/phase3c_retire_concierge_hub.md`  
2. Checkout branch → `feature/retire-concierge-hub`  
3. Then tell Claude:  
   > “Follow the Phase 3C Concierge Hub Retirement brief exactly as written.”  

That’ll keep the transition clean, deterministic, and rollback-safe.
```
Perfect 👍 — here’s the **complete, unified Markdown brief** for Claude.
Save it as `docs/phase4a_waiting_room_consolidation.md` and tell him:

> “Follow the Phase 4A Waiting Room Consolidation brief exactly as written.”

---

```markdown
# Phase 4A — Waiting Room Consolidation & FAQ Integration

**Date:** 2025-10-30  
**Branch:** `feature/waiting-room-consolidation`  
**Owner:** Concierge Care Advisors / Senior Navigator  
**Purpose:** Consolidate *Waiting Room* functionality into the **Lobby Hub**, simplify product hierarchy, and migrate the *FAQs & Answers* product tile into the NAVI assistant bar.  
**Primary Goal:** Create a single adaptive hub that handles Discovery, Planning, and Post-Planning journeys in one streamlined user experience.

---

## 🎯 Objectives

1. Merge *Lobby* and *Waiting Room* into one unified hub.
2. Introduce **Completed Journeys** and **Upcoming Tasks** sections below active tiles.
3. Remove the **FAQs & Answers** tile and replace it with a NAVI-triggered action.
4. Ensure architecture consistency:
   - Hubs → Product Tiles → Modules → Assets
   - NAVI retains awareness of all journeys and current phase.

---

## 🧩 Files & Structure

Modified files:
```

/pages/hub_lobby.py
/core/nav.json
/core/products.json
/core/navi.py (or wherever NAVI bar logic resides)
/pages/faq.py

```

Optional new helper file:
```

/core/journeys.py

````

---

## 🧱 Implementation Details

### 1️⃣ Merge Waiting Room into Lobby

**Action:**
- Remove `/pages/hub_waiting_room.py` and merge any relevant content into `hub_lobby.py`.
- The **Lobby** now displays all dynamic tiles, replacing both Concierge and Waiting Room hubs.

**New structure inside Lobby:**
```python
# Section 1: Current Journey (active)
render_active_tiles()

# Section 2: Additional Services (Learning, Network, etc.)
render_additional_services()

# Section 3: Completed Journeys (collapsible)
render_completed_tiles()
````

✅ *Result:* One-page experience for all user states.

---

### 2️⃣ Add Completed Journeys Section

In `hub_lobby.py`:

```python
st.markdown("### My Completed Journeys")
with st.expander("View completed activities", expanded=False):
    for tile in completed_tiles:
        render_tile(tile)
```

* Use existing tile renderer.
* Completed journeys are read-only, non-clickable by default (but can still link to summary pages later).

---

### 3️⃣ Introduce Journey Helper (Optional)

Create `/core/journeys.py`:

```python
def get_journey_phase(user_state):
    """Return the current journey phase: discovery, planning, or post-planning."""
    if not user_state.get("guided_care_completed"):
        return "discovery"
    elif not user_state.get("advisor_booked"):
        return "planning"
    return "post_planning"
```

This helper determines which tiles appear active or retired.

---

### 4️⃣ Remove FAQs & Answers Tile

In `/core/products.json` (or product tile definitions):

* Remove or comment out the FAQs entry:

  ```json
  {
    "key": "faq",
    "title": "FAQs & Answers",
    "module": "pages.faq",
    "status": "retired"
  }
  ```

✅ The FAQ product is no longer rendered as a tile.

---

### 5️⃣ Integrate FAQ Route into NAVI

In `/core/navi.py` (or equivalent):

```python
st.button("Ask NAVI", on_click=lambda: route_to("faq"))
```

If NAVI already includes contextual prompts, update the “Get Help” or “Ask NAVI” button to trigger `route_to("faq")`.

✅ This preserves existing FAQ runtime behavior via `pages/faq.py`.
✅ Removes visual redundancy while improving usability.

---

### 6️⃣ Navigation Updates

In `/core/nav.json`:

* Remove or comment out any **Waiting Room** entry.
* Ensure **Lobby** remains second in the nav order, directly after Welcome:

  ```json
  [
    { "key": "welcome", "title": "Welcome", "module": "pages.welcome" },
    { "key": "lobby", "title": "Lobby", "module": "pages.hub_lobby" },
    ...
  ]
  ```

---

## ✅ Verification Checklist

| Step | Expected Result                                     |
| ---- | --------------------------------------------------- |
| 1    | Lobby replaces Waiting Room entirely                |
| 2    | “FAQs & Answers” tile no longer visible             |
| 3    | NAVI’s “Ask for Help” opens the FAQ module          |
| 4    | Completed journeys appear under collapsible section |
| 5    | No duplicate hub routes remain                      |
| 6    | Lobby remains default landing page                  |
| 7    | All product tiles route correctly back to Lobby     |

---

## 🚫 Restrictions

* ❌ No CSS or visual redesign (Phase 4B will handle new layouts).
* ❌ Do not alter Guided Care Plan, Cost Planner, or Advisor modules.
* ✅ Keep architecture strictly modular (tile → module → asset).
* ✅ Use existing routing system (`route_to()` and `nav.json`).
* ✅ Preserve session state and user progress flags.

---

## 🧾 Deliverables

| File            | Change                                      | Purpose              |
| --------------- | ------------------------------------------- | -------------------- |
| `hub_lobby.py`  | Merge Waiting Room + add Completed Journeys | Unified hub          |
| `products.json` | Remove FAQ tile                             | Simplify UI          |
| `navi.py`       | Add Ask NAVI → FAQ route                    | Integrate help       |
| `nav.json`      | Remove Waiting Room                         | Clean routing        |
| `journeys.py`   | Optional helper for phase logic             | Determine tile state |

---

## ✅ Expected Outcome

* The **Lobby Hub** now manages the entire user journey lifecycle.
* **NAVI** provides contextual assistance and routes to FAQ.
* **Waiting Room** and **Concierge** are fully retired.
* The layout cleanly progresses users from **Discovery → Planning → Post-Planning**.
* The UI remains visually identical — logic only.

---

Got it — here’s the **revision block** you can copy and paste directly into the end of your existing
`docs/phase4a_waiting_room_consolidation.md` file.

This will make the correction explicit and keep Claude perfectly aligned:

---

````markdown
---

## 🔧 Phase 4A Revision Note — Product vs. Additional Services  
**Date:** 2025-10-30  

During implementation review, it was confirmed that two elements previously associated with the “Waiting Room” — **Trivia** and **Concierge Clinical Review** — are *not* additional services.  
They are **core product tiles** and must remain part of the main product flow.

### ✅ Corrected Hierarchy

The **Lobby Hub** will render tiles in this order:

```python
render_discovery_tiles()      # Discovery Journey
render_planning_tiles()       # Guided Care Plan, Cost Planner, Plan with My Advisor
render_engagement_tiles()     # Trivia, Concierge Clinical Review
render_additional_services()  # OmCare, SeniorLife, VA A&A, ElderLaw, etc.
render_completed_tiles()      # Closed-out journeys
````

### ✅ Implementation Rules

1. **Trivia** and **Concierge Clinical Review**:

   * Stay in the **main product tile grid** (not under “Additional Services”).
   * Retain full routing via `route_to("trivia")` and `route_to("concierge_review")`.
   * Continue using their existing module and config structures.
2. **Additional Services**:

   * Reserved only for NAVI-driven upsells and partner recommendations.
   * Examples: OmCare (Medication Management), SeniorLife (Cognitive/Fall Risk), VA A&A, ElderLaw, etc.
3. **Labeling** inside `hub_lobby.py` should be:

   ```
   # --- Discovery Journey ---
   # --- Planning Tools ---
   # --- Engagement Products ---
   # --- Additional Services / Partner Upsells ---
   # --- Completed Journeys ---
   ```
4. Maintain dynamic rendering across all categories using the same product-tile renderer.
5. Update any internal comments or section headers to reflect this corrected hierarchy.

### 🧩 Result

* Trivia and Concierge Clinical Review now appear alongside other products.
* The “Additional Services” area remains distinct for external partner integrations.
* The Lobby serves as the single, unified hub for all product experiences.

---

**End of Revision Note**

```

---


**End of Document**

```

---

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
Confirmed — the **`Phase_5E_Dynamic_Personalization.md`** file does **not yet exist** in your `docs/` directory on the `apzumi` branch.
You’ve already created the **`CLAUDE_5E_GUIDE.md`**, which is great — that serves as the implementation guide.

Here’s what’s missing and what you can add next:
The **Phase 5E Dynamic Personalization** document is the *primary project brief*, while the CLAUDE guide is the *developer-specific implementation reference*.

---

### 🆕 Recommended New File

**Path:** `docs/Phase_5E_Dynamic_Personalization.md`

**Purpose:** Defines the scope, intent, architecture, and expected deliverables of Phase 5E — the master plan that the CLAUDE guide implements.

Here’s the exact content you can paste in and commit:

---

```markdown
# Phase 5E — Dynamic Personalization

**Date:** 2025-10-30  
**Branch:** `feature/phase5e_dynamic_personalization`  
**Owner:** Concierge Care Advisors / Senior Navigator  
**Purpose:** Introduce user-specific dynamic personalization logic to the Senior Navigator platform, refining navigation, tone, and feature visibility based on individual profiles, tiers, cognition bands, and progress through the journey.

---

## 🎯 Objectives

1. Implement data-driven personalization rules that tailor each user’s navigation, copy tone, and visible modules.
2. Complete the visual and routing cleanup left from Phase 5D (PNG tiles, “Back to Lobby” routing).
3. Create schema-based personalization layer (`personalization_schema.json`) that defines dynamic adjustments per user type and phase.
4. Establish session persistence and recovery logic so returning users resume where they left off.
5. Lay groundwork for Phase 6 analytics integration (telemetry hooks).

---

## 🧩 Architecture Overview

| Component | Role | Description |
|------------|------|-------------|
| `core/personalizer.py` | Logic engine | Reads `personalization_schema.json`, modifies visible journeys, text tone, and partner tiles dynamically. |
| `config/personalization_schema.json` | Data schema | JSON rules defining personalization logic by tier, cognition, phase. |
| `data/personalization_cases.jsonl` | QA dataset | Example users and expected personalized outputs. |
| `hub_lobby.py` | UI | Integrates personalization results into displayed sections (Active, Additional Services, Completed). |

---

## 🧠 Personalization Parameters

| Parameter | Description | Example Values |
|------------|--------------|----------------|
| `tier` | Living level | `independent`, `assisted`, `memory_care` |
| `cognition_band` | Cognitive function level | `a&o4`, `mild_decline`, `advanced_dementia` |
| `support_band` | Care support needs | `low`, `medium`, `high` |
| `phase` | Current journey stage | `discovery`, `planning`, `post_planning` |
| `is_repeat_user` | Session flag | `true` / `false` |

---

## ⚙️ Functional Goals

1. **Navigation Adaptation**
   - Reorder or hide tiles based on user tier or phase.
   - Modify calls-to-action and guidance tone via schema text blocks.
2. **Visual Simplification**
   - Remove static PNG tile images and apply CSS or emoji icons.
3. **Routing Consistency**
   - Ensure all “Back to Lobby” buttons route to `hub_concierge`.
4. **Data Capture**
   - Begin emitting personalization events to telemetry (for Phase 6).
5. **Recovery**
   - Persist snapshot of user context for re-entry (UID + journey phase).

---

## 🧪 Verification Checklist

| Test | Expected Result |
|------|-----------------|
| 1 | All “Back to Lobby” buttons route to `hub_concierge`. |
| 2 | No remaining PNG tile references. |
| 3 | UI tone and module order adjust dynamically by tier and cognition band. |
| 4 | Session resume restores personalized state. |
| 5 | Telemetry logs personalization events successfully. |

---

## 📦 Deliverables

| File | Change | Purpose |
|------|---------|----------|
| `core/personalizer.py` | +120 lines | Implements schema-based personalization engine. |
| `config/personalization_schema.json` | new | Defines tier- and phase-specific rules. |
| `hub_lobby.py` | +40 lines | Integrates personalization output into sections. |
| `core/navigation.py` | +15 lines | Adds dynamic route injection support. |
| `dashboard.css` | +10 lines | Handles personalized icon styles. |

---

## ✅ Expected Outcome

- Personalized Senior Navigator experience.
- Consistent, clean navigation (Lobby-centric).
- PNG product tiles removed.
- Dynamic schema-based personalization layer ready for analytics integration in Phase 6.

---

**End of Document**
```


# Phase 5F: Visual Polish + Guided Care Plan Correction

**Status:** Complete ✅  
**Date:** October 30, 2025  
**Branch:** `feature/phase5f_visual_polish`

## Objectives

### 1. Visual Polish - Phase Gradients
Introduce elegant, minimal background gradients on product tiles based on journey phase. The design is subtle, accessible, and professional with no harsh saturation or contrast.

### 2. Guided Care Plan (GCP) Phase Correction
Correct the GCP phase mapping to properly place it in the **Planning** phase instead of Discovery.

## Changes Implemented

### 1. Schema Correction (`config/personalization_schema.json`)
**Issue:** GCP was incorrectly mapped to Discovery phase, causing confusion in journey flow.

**Fix:** Updated phases configuration:
- **Discovery phase**: Now only contains `["discovery_learning"]`
- **Planning phase**: Continues to contain all planning modules including GCP: `["gcp_v4", "learn_recommendation", "cost_v2", "pfma_v3"]`

**Rationale:** GCP is a planning tool, not a discovery/onboarding experience. Discovery Learning is the true first-touch onboarding.

### 2. Tile Structure (`hubs/hub_lobby.py`)
**Change 1 - Discovery Tiles:**
- Removed GCP tile from `_build_discovery_tiles()`
- Discovery now only contains Discovery Learning tile
- Updated docstring to reflect Phase 5F correction

**Change 2 - Planning Tiles:**
- Moved GCP tile to `_build_planning_tiles()` as first tile (order=10)
- Updated GCP phase tag from `"discovery"` to `"planning"`
- Maintained proper ordering: GCP (10) → Learn (15) → Cost (20) → Advisor (30)
- Updated docstring to reflect Phase 5F correction

### 3. Gradient CSS (`core/styles/dashboard.css`)
**Added 4 gradient classes** with subtle, accessible color transitions:

```css
.tile-gradient-discovery {
  background: linear-gradient(180deg, #E8F1FF 0%, #FFFFFF 100%);
  /* Soft blue - welcoming first-touch experience */
}

.tile-gradient-planning {
  background: linear-gradient(180deg, #EAFBF0 0%, #FFFFFF 100%);
  /* Soft green - growth and progress */
}

.tile-gradient-post_planning {
  background: linear-gradient(180deg, #F3EEFF 0%, #FFFFFF 100%);
  /* Soft violet - completion and celebration */
}

.tile-gradient-service {
  background: linear-gradient(180deg, #F7F7F7 0%, #FFFFFF 100%);
  /* Neutral gray - additional services/partners */
}
```

**Design Principles:**
- 180deg vertical gradient (top to bottom)
- Starts with subtle color (#E8-#F7 range)
- Fades to pure white (#FFFFFF)
- Maintains hover states (translateY + shadow)
- Accessible contrast ratios
- Professional, not playful

### 4. Dynamic Gradient Application (`core/product_tile.py`)
**Added automatic gradient class injection** based on tile's `phase` attribute:

```python
# Phase 5F: Add gradient class based on journey phase
if self.phase:
    classes.append(f"tile-gradient-{self.phase}")
```

**How it works:**
1. Each ProductTileHub has a `phase` attribute: `"discovery"`, `"planning"`, `"post_planning"`
2. Tile renderer automatically adds corresponding gradient class
3. CSS applies appropriate gradient based on class
4. Additional services (non-ProductTileHub) don't get gradients (by design)

## Journey Flow After Phase 5F

### Discovery Phase
**Tiles:** Discovery Learning only  
**Purpose:** First-touch onboarding and welcome experience  
**Gradient:** Soft blue (#E8F1FF → #FFFFFF)

### Planning Phase
**Tiles:** GCP → Learn Recommendation → Cost Planner → My Advisor  
**Purpose:** Core planning journey with all strategic tools  
**Gradient:** Soft green (#EAFBF0 → #FFFFFF)

### Post-Planning Phase
**Tiles:** Senior Trivia, Concierge Clinical Review  
**Purpose:** Engagement and professional review after planning complete  
**Gradient:** Soft violet (#F3EEFF → #FFFFFF)

### Additional Services
**Tiles:** Partner services (Home Health, Fall Risk, etc.)  
**Purpose:** Upsell opportunities for partner products  
**Gradient:** None (uses default tile styling)

## Verification Checklist

| Test | Expected Result | Status |
|------|----------------|--------|
| 1. Discovery tile shows soft blue gradient | Discovery Learning has #E8F1FF → #FFFFFF | ✅ |
| 2. Planning tiles show soft green gradient | GCP, Learn, Cost, Advisor have #EAFBF0 → #FFFFFF | ✅ |
| 3. Post-planning tiles show soft violet gradient | Trivia, CCR have #F3EEFF → #FFFFFF | ✅ |
| 4. GCP appears in Planning section | GCP is first planning tile (order=10) | ✅ |
| 5. Discovery only shows Discovery Learning | Discovery section has 1 tile only | ✅ |
| 6. Gradients maintain hover states | Hover still shows translateY(-2px) + shadow | ✅ |
| 7. No regressions in personalization | visible_modules still filters correctly | ✅ |
| 8. Additional services have no gradient | Partner tiles use default styling | ✅ |

## Technical Details

### Phase Attribute Mapping
```python
# Discovery tiles
phase="discovery"  # Discovery Learning

# Planning tiles
phase="planning"   # GCP, Learn Recommendation, Cost Planner, My Advisor

# Post-planning tiles
phase="post_planning"  # Senior Trivia, Concierge Clinical Review

# Additional services
phase=None  # No phase attribute (partner services)
```

### CSS Class Application
```html
<!-- Discovery tile -->
<div class="ptile dashboard-card tile--active tile--brand tile-gradient-discovery">

<!-- Planning tile -->
<div class="ptile dashboard-card tile--active tile--brand tile-gradient-planning">

<!-- Post-planning tile -->
<div class="ptile dashboard-card tile--complete tile--teal tile-gradient-post_planning">

<!-- Additional service (no gradient) -->
<div class="ptile dashboard-card tile--locked">
```

### Personalization Integration
Phase 5F gradients work seamlessly with Phase 5E personalization:
- **Tier gradients** (independent/assisted/memory_care) apply to entire dashboard-card
- **Phase gradients** apply to individual tiles based on journey position
- Both can coexist without visual conflict
- Phase gradients are MORE specific, so they override tier gradients when needed

## Files Modified

1. **config/personalization_schema.json** (+1/-1 lines)
   - Updated discovery visible_modules: `["gcp_v4"]` → `["discovery_learning"]`

2. **hubs/hub_lobby.py** (+19/-16 lines)
   - Removed GCP tile from `_build_discovery_tiles()`
   - Added GCP tile to `_build_planning_tiles()` as first tile
   - Updated phase tag on GCP tile: `"discovery"` → `"planning"`
   - Updated docstrings for both functions

3. **core/styles/dashboard.css** (+31 lines)
   - Added 4 gradient classes (discovery, planning, post_planning, service)
   - Added hover state preservations for all gradients

4. **core/product_tile.py** (+3 lines)
   - Added dynamic gradient class injection based on phase attribute

5. **docs/Phase_5F_Visual_Polish.md** (new file)
   - This documentation

## Migration Notes

### Breaking Changes
**None.** This is a purely additive visual enhancement with a structural correction.

### Backwards Compatibility
- Tiles without `phase` attribute don't get gradients (graceful fallback)
- Additional services continue to use default styling
- Existing personalization (Phase 5E) unaffected
- All navigation routes remain unchanged

### User Impact
**Positive:** 
- Clearer visual distinction between journey phases
- GCP now properly grouped with planning tools
- More intuitive journey progression
- Professional, polished appearance

**None negative.**

## Future Considerations

### Dark Mode Support
Current gradients are light-mode optimized. For dark mode support, add:
```css
@media (prefers-color-scheme: dark) {
  .tile-gradient-discovery {
    background: linear-gradient(180deg, #1A2B4A 0%, #0F1923 100%);
  }
  /* ... other gradients ... */
}
```

### Additional Phase Gradients
If new journey phases are added (e.g., `pre_discovery`, `advanced_planning`), follow the pattern:
1. Define gradient in dashboard.css
2. Add phase attribute to tiles
3. Gradient applies automatically via product_tile.py logic

### Gradient Customization Per Tier
For deeper personalization, could apply different gradient intensities per tier:
```css
.tier-independent .tile-gradient-planning {
  background: linear-gradient(180deg, #D4F5DD 0%, #FFFFFF 100%);
}
.tier-assisted .tile-gradient-planning {
  background: linear-gradient(180deg, #EAFBF0 0%, #FFFFFF 100%);
}
.tier-memory-care .tile-gradient-planning {
  background: linear-gradient(180deg, #F0FAF2 0%, #FFFFFF 100%);
}
```

## Related Documentation
- **Phase 5E Dynamic Personalization:** `docs/Phase_5E_Dynamic_Personalization.md`
- **Phase 5A Journey Tags:** (see hub_lobby.py docstrings)
- **Product Tile Architecture:** `core/product_tile.py`
- **Personalization Schema:** `config/personalization_schema.json`

---

**Implemented by:** Claude  
**Approved by:** Shane  
**Next Phase:** TBD (consider Phase 5G: Advanced Personalization or Phase 6: Production Hardening)
# Phase 5F Visual Reference Guide

## Phase Gradient Color Palette

### Discovery Phase
**Color:** Soft Blue  
**Hex:** `#E8F1FF` → `#FFFFFF`  
**Emotion:** Welcoming, Clear, Trustworthy  
**Tiles:** Discovery Learning

```
┌─────────────────────────────────┐
│  ░░░░░░░░ DISCOVERY ░░░░░░░░░   │  ← #E8F1FF (very light blue)
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░    │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░      │
│  ░░░░░░░░░░░░░░░░░░░░░░         │
│                                  │  ← #FFFFFF (pure white)
└─────────────────────────────────┘
```

### Planning Phase
**Color:** Soft Green  
**Hex:** `#EAFBF0` → `#FFFFFF`  
**Emotion:** Growth, Progress, Action  
**Tiles:** GCP, Learn Recommendation, Cost Planner, My Advisor

```
┌─────────────────────────────────┐
│  ░░░░░░░░ PLANNING ░░░░░░░░░░   │  ← #EAFBF0 (very light green)
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░    │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░      │
│  ░░░░░░░░░░░░░░░░░░░░░░         │
│                                  │  ← #FFFFFF (pure white)
└─────────────────────────────────┘
```

### Post-Planning Phase
**Color:** Soft Violet  
**Hex:** `#F3EEFF` → `#FFFFFF`  
**Emotion:** Celebration, Completion, Reflection  
**Tiles:** Senior Trivia, Concierge Clinical Review

```
┌─────────────────────────────────┐
│  ░░░░░░ POST-PLANNING ░░░░░░░   │  ← #F3EEFF (very light violet)
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░    │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░      │
│  ░░░░░░░░░░░░░░░░░░░░░░         │
│                                  │  ← #FFFFFF (pure white)
└─────────────────────────────────┘
```

### Additional Services
**Color:** Neutral Gray  
**Hex:** `#F7F7F7` → `#FFFFFF`  
**Emotion:** Utility, Professional, Optional  
**Tiles:** Partner services (currently not implemented - reserved for future)

```
┌─────────────────────────────────┐
│  ░░░░░░ ADDITIONAL ░░░░░░░░░░   │  ← #F7F7F7 (very light gray)
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░    │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░      │
│  ░░░░░░░░░░░░░░░░░░░░░░         │
│                                  │  ← #FFFFFF (pure white)
└─────────────────────────────────┘
```

## Journey Flow Visualization

```
┌──────────────────────────────────────────────────────────────┐
│                      LOBBY JOURNEY MAP                        │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  🏁 DISCOVERY PHASE                   [Soft Blue Gradient]   │
│     ┌─────────────────────────────────┐                      │
│     │ 🎓 Discovery Learning           │                      │
│     │    Welcome & Onboarding         │                      │
│     └─────────────────────────────────┘                      │
│                      ↓                                        │
│  📋 PLANNING PHASE                    [Soft Green Gradient]  │
│     ┌─────────────────────────────────┐                      │
│     │ 🧭 Guided Care Plan             │ ← MOVED FROM DISC.   │
│     │    Explore care options         │                      │
│     └─────────────────────────────────┘                      │
│                      ↓                                        │
│     ┌─────────────────────────────────┐                      │
│     │ 💡 Learn About My Recommendation│                      │
│     │    Understand your option       │                      │
│     └─────────────────────────────────┘                      │
│                      ↓                                        │
│     ┌─────────────────────────────────┐                      │
│     │ 💰 Cost Planner                 │                      │
│     │    Financial planning           │                      │
│     └─────────────────────────────────┘                      │
│                      ↓                                        │
│     ┌─────────────────────────────────┐                      │
│     │ 👥 My Advisor                   │                      │
│     │    Schedule meeting             │                      │
│     └─────────────────────────────────┘                      │
│                      ↓                                        │
│  🎉 POST-PLANNING PHASE               [Soft Violet Gradient] │
│     ┌─────────────────────────────────┐                      │
│     │ 🎮 Senior Trivia                │                      │
│     │    Brain games & engagement     │                      │
│     └─────────────────────────────────┘                      │
│                                                               │
│     ┌─────────────────────────────────┐                      │
│     │ ⚕️ Concierge Clinical Review    │                      │
│     │    Professional care review     │                      │
│     └─────────────────────────────────┘                      │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## CSS Implementation

### Gradient Classes
```css
/* Discovery */
.tile-gradient-discovery {
  background: linear-gradient(180deg, #E8F1FF 0%, #FFFFFF 100%);
}

/* Planning */
.tile-gradient-planning {
  background: linear-gradient(180deg, #EAFBF0 0%, #FFFFFF 100%);
}

/* Post-Planning */
.tile-gradient-post_planning {
  background: linear-gradient(180deg, #F3EEFF 0%, #FFFFFF 100%);
}

/* Additional Services (future use) */
.tile-gradient-service {
  background: linear-gradient(180deg, #F7F7F7 0%, #FFFFFF 100%);
}
```

### Applied HTML Example
```html
<!-- Discovery tile -->
<div class="ptile dashboard-card tile--brand tile-gradient-discovery">
  <span class="phase-pill discovery">Discovery</span>
  <div class="ptile__head">
    <span class="emoji-icon">🎓</span>
    <h3>Start Your Discovery Journey</h3>
  </div>
</div>

<!-- Planning tile -->
<div class="ptile dashboard-card tile--brand tile-gradient-planning">
  <span class="phase-pill planning">Planning</span>
  <div class="ptile__head">
    <span class="emoji-icon">🧭</span>
    <h3>Guided Care Plan</h3>
  </div>
</div>
```

## Accessibility Notes

### Color Contrast
All gradients fade to pure white (#FFFFFF), ensuring:
- Text remains readable throughout gradient
- No accessibility violations (WCAG AA compliant)
- Subtle visual distinction without overwhelming users

### Gradient Start Colors
- **Discovery (#E8F1FF):** Very light blue, ~98% lightness
- **Planning (#EAFBF0):** Very light green, ~98% lightness
- **Post-Planning (#F3EEFF):** Very light violet, ~98% lightness
- **Service (#F7F7F7):** Very light gray, ~97% lightness

### Visual Hierarchy
Gradients are intentionally subtle to:
1. Provide wayfinding without distraction
2. Maintain professional appearance
3. Support journey flow understanding
4. Avoid visual fatigue for older users

## Design Rationale

### Why These Colors?
- **Blue (Discovery):** Universally associated with trust, clarity, and beginnings
- **Green (Planning):** Represents growth, progress, and taking action
- **Violet (Post-Planning):** Signifies completion, reflection, and wisdom
- **Gray (Service):** Neutral, utility-focused, non-journey-critical

### Why 180deg Vertical Gradient?
- Natural reading direction (top-to-bottom)
- Suggests forward movement/progress
- More elegant than horizontal gradients
- Works better with variable tile heights

### Why Fade to White?
- Maintains clean, professional look
- Ensures text readability throughout
- Allows other visual elements (emoji, badges) to stand out
- Prevents visual clutter

## Browser Compatibility

### Gradient Support
- ✅ Chrome 26+ (100% support)
- ✅ Firefox 16+ (100% support)
- ✅ Safari 7+ (100% support)
- ✅ Edge 12+ (100% support)

### Fallback
If gradients fail to load (extremely rare), tiles default to `background: #ffffff` from base `.dashboard-card` class.

## Testing Checklist

- [ ] Discovery Learning shows soft blue gradient
- [ ] GCP shows soft green gradient (now in planning)
- [ ] Learn Recommendation shows soft green gradient
- [ ] Cost Planner shows soft green gradient
- [ ] My Advisor shows soft green gradient
- [ ] Senior Trivia shows soft violet gradient
- [ ] Clinical Review shows soft violet gradient
- [ ] Additional services show no gradient (default white)
- [ ] Hover states work on all gradient tiles
- [ ] Gradients don't interfere with phase pills
- [ ] Gradients don't interfere with emoji icons
- [ ] Gradients don't interfere with completion badges
- [ ] Mobile responsive (gradients scale correctly)

---

**Created:** October 30, 2025  
**Phase:** 5F Visual Polish  
**Status:** Complete ✅
Perfect — here’s the complete Markdown spec you can drop directly into your repo at:
`docs/Phase_5G_Journey_Hierarchy.md`

---

```markdown
# 🧭 Phase 5G — Journey Hierarchy & Visual Identity

## 🎯 Goal
Reorganize the Senior Navigator Lobby layout to clearly separate **active**, **upsell**, and **completed** journeys — with no banners, icons, or gradients.  
Use **clean typography and left-border color accents** to communicate hierarchy and journey phase.

---

## 🧩 Layout Hierarchy

### 1. NAVI Header
- No change.
- Displays contextual guidance as it does today.

### 2. Active Journeys
- Default visible journeys for new users:
  - **Discovery**
  - **Planning**
- Additional active journeys load dynamically.
- Tiles display with **phase-specific left borders** (see Visual Tokens below).

### 3. Informational Text Line
- Appears **only** when a completed journey exists.
- Content:
```

Your completed journeys are shown below.

````
- Style: neutral, light, minimal (no background, no icon, no banner).

### 4. Additional Services
- Always visible.
- Represents *upsell opportunities* or secondary tools.
- Positioned **above** completed journeys.

### 5. My Completed Journeys
- Displays finished journeys (e.g., Discovery after completion).
- Anchored at the bottom of the layout.

---

## 🎨 Visual Tokens

Use **left border accents** to indicate journey phase identity.  
Remove all gradients.

```css
.tile-discovery { border-left: 4px solid #3B82F6; }   /* blue  */
.tile-planning  { border-left: 4px solid #10B981; }   /* green */
.tile-post      { border-left: 4px solid #8B5CF6; }   /* violet */
.tile-service   { border-left: 4px solid #9CA3AF; }   /* gray   */

.section-note {
font-size: 0.85rem;
color: #666;
margin: 1rem 0 0.5rem 0;
text-align: center;
font-style: italic;
}
````

---

## ⚙️ Functional Logic

```python
active = get_active_journeys(user)
completed = get_completed_journeys(user)
services = get_additional_services(user)

render_tiles(active, section="Active Journeys")

if completed:
    st.markdown("<p class='section-note'>Your completed journeys are shown below.</p>", unsafe_allow_html=True)

render_tiles(services, section="Additional Services")
render_tiles(completed, section="My Completed Journeys")
```

Behavior:

* For **new users** → only “Discovery” and “Planning” appear under “Active Journeys.”
* When a journey completes → it moves to “My Completed Journeys.”
* The “Your completed journeys…” note appears dynamically.
* “Additional Services” remain fixed above completed journeys.

---

## 🧾 Commit Message

```
feat(phase5g): reorganize lobby journey sections, remove gradients, add border-based visual cues
```

---

## 🔒 Secondary Task — Hide “Trusted Partners” Nav Link

Until partner content is ready, hide the **Trusted Partners** link from the top nav.

### Files to Adjust

* `layout.py` or `core/navigation.py` (where the nav bar is generated)

### Action

Comment out or remove the item:

```python
# "Trusted Partners": "partners",
```

Resulting top nav order:

```
Welcome | Lobby | Learning | Resources | Professional
```

---

## ✅ Expected Result

* Lobby shows **Discovery** and **Planning** tiles by default.
* Once a journey completes, it drops below the **Additional Services** section.
* “Your completed journeys are shown below.” appears when appropriate.
* Tiles are visually grouped by left-border accent.
* Navigation bar hides “Trusted Partners.”
* No icons, no banners, no gradients.
* Layout feels structured, calm, and professional.

```

Perfect 👍 — here’s what I’ll generate for you next:

---

## 📘 `PHASE5H_CSS_UNLOCK_AND_ROLLBACK_PLAN.md`

### 🔖 Branch & Commit

* **Target branch:** `feature/phase5h_css_unlock`
* **First commit message:**
  `feat(phase5h): unlock global CSS for contextual and lobby visuals, protect pills and welcome`

---

### 🧷 1. Rollback Safety (Backup Before Unlock)

Before any visual-layer work:

```bash
git add .
git commit -m "checkpoint: pre-phase5h-css-unlock"
git tag -a backup_pre5h -m "Backup before CSS unlock"
git push origin feature/phase5e_dynamic_personalization --tags
```

To restore later:

```bash
git reset --hard backup_pre5h
```

---

### 🛡️ 2. Protected Elements (DO NOT ALTER)

These must remain pixel-perfect:

* `Welcome.py` — locked to designer-approved layout.
* `.pill-black`, `.pill-white` — preserve size, contrast, shape.
* `.welcome-container` — keep layout and margins.

---

### 🔓 3. Unlocked Elements

These can now be freely styled, refined, or overridden:

* `hub_lobby.py` and other hubs (Professional, Resources, Learning)
* All `.tile-*` product modules
* `navi-card` contextual cards
* Global margins, paddings, and font weights

---

### ⚙️ 4. Modify CSS Injection in `app.py`

```python
def inject_css():
    import os
    cache_buster = f"/* {os.urandom(4).hex()} */"

    with open("assets/css/global.css") as f:
        st.markdown(f"<style>{cache_buster}{f.read()}</style>", unsafe_allow_html=True)

    with open("assets/css/modules.css") as f:
        st.markdown(f"<style>{cache_buster}{f.read()}</style>", unsafe_allow_html=True)

    # ✅ Safe override layer
    override_path = "assets/css/overrides.css"
    if os.path.exists(override_path):
        with open(override_path, encoding="utf-8") as f:
            st.markdown(f"<style>{cache_buster}{f.read()}</style>", unsafe_allow_html=True)
```

---

### 🎨 5. `assets/css/overrides.css`

```css
/* ==========================================
   PHASE 5H SAFE OVERRIDES — VISUAL POLISH
   ========================================== */

/* ====== TILE JOURNEY BORDERS ====== */
.tile-discovery { border-left: 4px solid #3A7BFF !important; }
.tile-planning  { border-left: 4px solid #2ECC71 !important; }
.tile-post      { border-left: 4px solid #8A4FFF !important; }
.tile-service   { border-left: 4px solid #CCCCCC !important; }

/* ====== CONTEXTUAL CARD ALIGNMENT ====== */
.navi-card { border-left: 4px solid #3A7BFF !important; border-radius: 8px !important; }

/* ====== TYPOGRAPHY CLEANUP ====== */
h1, h2, h3, h4 { font-weight: 600; letter-spacing: -0.02em; }

/* ====== LAYOUT SMOOTHING ====== */
section, .container, .tile-grid { gap: 1.5rem !important; }

/* ====== LOCKED ELEMENTS ====== */
.pill-black, .pill-white, .welcome-container {
  all: revert !important;
  filter: none !important;
  box-shadow: none !important;
}
```

---

### 🧭 6. Claude Instructions

**Claude, follow this strictly:**

1. Operate on the `feature/phase5h_css_unlock` branch.
2. Implement the `inject_css()` modification.
3. Add `assets/css/overrides.css` using the above template.
4. Verify **Welcome.py** and the **pills** remain visually identical.
5. Apply the new `.tile-*` border classes to product tiles and contextual cards.
6. Test in all hubs: **Lobby**, **Learning**, **Resources**, **Professional**.


Excellent question — those two markdowns are sequential phases of the *same feature evolution*, not conflicting instructions.

Here’s how to think of them:

| Phase  | Feature                             | Status             | Notes                                                                  |
| ------ | ----------------------------------- | ------------------ | ---------------------------------------------------------------------- |
| **5J** | Gradient + Animated Gradient Border | ✅ Baseline version | Adds the static + gradient border animation and completed-card styling |
| **5K** | Shimmer Pulse Extension             | 🔄 Enhancement     | Builds directly on 5J, adding the subtle shimmer-pulse overlay         |

So the second one **replaces and extends** the first.
To avoid confusion, here’s the **merged single markdown** you can give Claude, containing everything from both 5J and 5K in one authoritative spec.

---

## 📘 `PHASE5K_AI_SHIMMER_PULSE_AND_COMPLETED_CARD.md`

### 🎯 Objectives

1. Apply a **purple→pink gradient** border to AI-related tiles (e.g. NAVI).
2. Add a **soft shimmer-pulse effect** for subtle movement and “intelligence.”
3. Maintain and polish the **Completed Journey Card** style.
4. Keep all motion smooth, lightweight, and compliant with `prefers-reduced-motion`.

---

### 🎨 CSS Additions (`assets/css/overrides.css`)

```css
/* ==========================================
   PHASE 5K — AI SHIMMER PULSE + COMPLETED CARD
   ========================================== */

/* --- AI / NAVI Card Base --- */
.ai-card, .navi-card {
    border-left: 5px solid transparent;
    border-image: linear-gradient(180deg, #9b5de5, #f15bb5);
    border-image-slice: 1;
    border-radius: 10px;
    background: #fff;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.3s ease;
}

/* --- Animated Gradient Flow --- */
.ai-card.animate-border, .navi-card.animate-border {
    border-image: linear-gradient(180deg, #9b5de5, #f15bb5, #9b5de5);
    animation: borderGradient 8s ease-in-out infinite;
    border-image-slice: 1;
}
@keyframes borderGradient {
    0%   { border-image-source: linear-gradient(180deg, #9b5de5, #f15bb5); }
    50%  { border-image-source: linear-gradient(180deg, #f15bb5, #9b5de5); }
    100% { border-image-source: linear-gradient(180deg, #9b5de5, #f15bb5); }
}

/* --- Shimmer Pulse Overlay --- */
.ai-card::before, .navi-card::before {
    content: "";
    position: absolute;
    top: 0; left: -150%;
    width: 250%;
    height: 100%;
    background: linear-gradient(
        120deg,
        rgba(155,93,229,0) 30%,
        rgba(241,91,181,0.15) 50%,
        rgba(155,93,229,0) 70%
    );
    animation: shimmerPulse 6s infinite ease-in-out;
    pointer-events: none;
}
@keyframes shimmerPulse {
    0%   { transform: translateX(0); opacity: 0.3; }
    50%  { transform: translateX(30%); opacity: 0.5; }
    100% { transform: translateX(0); opacity: 0.3; }
}

/* --- Hover Depth + Optional Glow --- */
.ai-card:hover, .navi-card:hover {
    box-shadow: 0 4px 14px rgba(241,91,181,0.18);
    transform: translateY(-1px);
    transition: all 0.25s ease-in-out;
}

/* --- Motion Accessibility --- */
@media (prefers-reduced-motion: reduce) {
    .ai-card.animate-border,
    .navi-card.animate-border,
    .ai-card::before,
    .navi-card::before {
        animation: none !important;
    }
}

/* --- Completed Journey Card --- */
.completed-card {
    background: linear-gradient(180deg, #f8faff 0%, #ffffff 100%);
    border-left: 5px solid #2ecc71;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    padding: 1.25rem 1.5rem;
    position: relative;
    transition: 0.2s ease-in-out;
}
.completed-card:hover {
    background: linear-gradient(180deg, #f2fcf7 0%, #ffffff 100%);
    border-left: 5px solid #27ae60;
    transform: translateY(-1px);
}
.completed-card::after {
    content: "✓";
    font-weight: bold;
    font-size: 1.2rem;
    color: #27ae60;
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: #e8f9f0;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
}
```

---

### 🧩 Example Usage in Streamlit

```python
# NAVI / AI card
st.markdown("""
<div class="navi-card ai-card animate-border">
    <h4>✨ NAVI</h4>
    <p>Answer these questions to match the right level of support.</p>
</div>
""", unsafe_allow_html=True)

# Completed Journey card
st.markdown("""
<div class="completed-card">
    <h4>Guided Care Plan</h4>
    <p>Your personalized care plan recommendation.</p>
</div>
""", unsafe_allow_html=True)
```

---

### 🧭 Claude Task Directive

> **Claude**, on branch `feature/phase5k_ai_shimmer_pulse`:
>
> * Append the above CSS to `assets/css/overrides.css`.
> * Apply `.animate-border` to all AI-driven or NAVI cards.
> * Keep the shimmer pulse and hover glow subtle.
> * Retain completed card styling from previous phase.
> * Verify animation fluidity and accessibility (`prefers-reduced-motion`).

---

Got it — thank you for clarifying 👌

Here’s the full, production-ready markdown content for both deliverables. You can drop these directly into your repo or your local markdown files.

---

## 🧱 **`PHASE5M_CSS_NORMALIZATION_PLAN.md`**

### 🎯 Objectives

Bring visual consistency and flexibility across all Streamlit app layers — from **global** to **hub**, **product**, **module**, and **dashboard** — without breaking the fidelity of `welcome.py` or the black/gray pill components.
This phase will also relocate the **Discovery Progress** bar from the top header into its intended contextual home (below the NAVI card).

---

### 🧩 1. Rollback & Safety Snapshot

Before any changes, create a rollback branch to preserve the current visual state:

```bash
git checkout -b rollback/phase5m_pre_unlock
git commit -am "Rollback snapshot before CSS normalization and unlock phase"
```

If something misbehaves during unlocks, you can revert instantly to this snapshot.

---

### 🎨 2. CSS Normalization Strategy

#### 🔹 Global (Base Styles)

* Relax global CSS constraints by **removing or commenting out any `!important` tags** that force inherited color, margin, or padding.
* Confirm global typography and color variables remain intact in `/assets/css/overrides.css`.
* Add soft fallbacks (e.g., `color: inherit;`) rather than absolute overrides.

#### 🔹 Hub Layer (Navigation / Layout)

* Preserve:

  * Left-border AI gradient logic (`.ai-card`, `.navi-card`)
  * Black and gray pills
  * Global nav spacing, header padding, and shadow depth
* Allow moderate flex-based resizing for responsiveness.

#### 🔹 Product Layer (Care Plan / Discovery)

* Enable natural scaling for components wider than 1200px (fix the “too wide on laptop” issue).
* Maintain consistent spacing around NAVI and Additional Services.
* Adjust `.completed-card` to use a max-width container (e.g., `max-width: 700px; margin: auto;`).

#### 🔹 Module Layer (Cards / Buttons / Pills)

* Retain all pill styles as locked — **do not touch `.module-pill` or `.pill-dark` / `.pill-gray`**.
* Lightly loosen shadow, padding, or radius rules only where needed to match the hub tone.

#### 🔹 Dashboard Layer

* Ensure charts, stats tiles, and cards follow the same border-radius, hover, and shadow rhythm as the hub.
* Inherit gradient and animation logic from the AI card base class for consistency.

---

### 🧩 3. Move Discovery Progress Placement

Relocate the **Discovery Progress** bar into the NAVI card body itself.

In `navi_hub.py` (or wherever NAVI renders):

```python
st.markdown("""
<div class="navi-card ai-card animate-border">
    <h4>✨ NAVI</h4>
    <p>Begin your Discovery Journey.</p>

    <div class="progress-wrapper">
        <div class="progress-label">Discovery Progress: 45% Complete</div>
        <div class="progress-bar">
            <div class="progress-bar-fill shimmer" style="width:45%;"></div>
        </div>
    </div>

    <div class="cta-row">
        <button class="cta-primary">Continue</button>
        <button class="cta-secondary">Ask NAVI</button>
    </div>
</div>
""", unsafe_allow_html=True)
```

Then remove or comment out the redundant “Discovery Phase Progress” section currently rendered in the top header.

---

### 💅 4. CSS Cleanup Tasks

Search the entire repository for lingering constraints:

```bash
grep -r "!important" .
```

Remove or comment out unnecessary ones unless required for:

* `.pill-dark`
* `.pill-gray`
* `.ai-card` gradient animation anchors
* `.completed-card` accent

Everything else should rely on normal cascade logic.

---

### 🧠 5. Validation Checklist

After rebuilding:

* [ ] NAVI card gradient and shimmer active
* [ ] Completed card visible and centered
* [ ] Discovery progress relocated below NAVI
* [ ] Additional services + completed journeys restored
* [ ] Global layout consistent across all pages
* [ ] No visual regressions in `welcome.py`

---

### 🧭 6. Branching & Commit

After all changes pass validation:

```bash
git checkout -b feature/phase5m_css_normalization_and_discovery_move
git commit -am "Normalize CSS across app, preserve pills, relocate Discovery Progress into NAVI"
git push origin feature/phase5m_css_normalization_and_discovery_move
```

---

### 🧩 Claude Task Directive

> **Claude**, follow the above plan step by step.
> Perform a repo-wide unlock of restrictive CSS rules (removing unnecessary `!important`), maintain `welcome.py` and all pill styles intact, move Discovery Progress into the NAVI card, and confirm all major hub and product views render correctly under normalized rules.

---

---

## 🧪 **`css_validation_test.py`**

```python
import streamlit as st

st.set_page_config(page_title="CSS Validation Test", layout="wide")

# Load global CSS
st.markdown('<link rel="stylesheet" href="assets/css/overrides.css">', unsafe_allow_html=True)

st.title("🧪 CSS Validation Test Suite")

st.subheader("AI / NAVI Card")
st.markdown("""
<div class="navi-card ai-card animate-border">
  <h4>✨ NAVI</h4>
  <p>Guided AI assistance for Discovery.</p>
  <div class="progress-wrapper">
      <div class="progress-label">Discovery Progress: 45% Complete</div>
      <div class="progress-bar">
          <div class="progress-bar-fill shimmer" style="width:45%;"></div>
      </div>
  </div>
  <div class="cta-row">
      <button class="cta-primary">Continue</button>
      <button class="cta-secondary">Ask NAVI</button>
  </div>
</div>
""", unsafe_allow_html=True)

st.subheader("Completed Journey Card")
st.markdown("""
<div class="completed-card">
  <h4>Guided Care Plan</h4>
  <p>Your personalized recommendation is ready.</p>
</div>
""", unsafe_allow_html=True)

st.subheader("Module Pills")
st.markdown("""
<div>
  <span class="pill-dark">Memory Care</span>
  <span class="pill-gray">Assisted Living</span>
  <span class="pill-dark">Independent</span>
</div>
""", unsafe_allow_html=True)

st.subheader("Dashboard Tile Example")
st.markdown("""
<div class="ai-card animate-border" style="max-width:300px;">
  <h4>Dashboard Metric</h4>
  <p>Move-ins this month: <strong>27</strong></p>
</div>
""", unsafe_allow_html=True)

st.caption("Confirm gradient shimmer, layout consistency, and lack of CSS regressions.")
```

---

✅ **You now have the full `PHASE5M` spec** — ready to commit to your repo and pass to Claude for implementation.
