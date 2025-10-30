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


