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

