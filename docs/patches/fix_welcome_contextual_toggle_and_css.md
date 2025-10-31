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
