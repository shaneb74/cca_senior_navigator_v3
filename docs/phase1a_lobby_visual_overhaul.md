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
