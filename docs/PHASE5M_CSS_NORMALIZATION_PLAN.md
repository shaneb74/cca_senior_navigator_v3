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
