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


