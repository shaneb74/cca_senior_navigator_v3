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

**End of Document**

```

---

