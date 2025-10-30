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
