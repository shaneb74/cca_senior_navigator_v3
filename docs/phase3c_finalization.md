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

```