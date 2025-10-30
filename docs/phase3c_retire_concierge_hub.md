Perfect 👍 — here’s the **full Markdown brief** for Claude to follow exactly.

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
