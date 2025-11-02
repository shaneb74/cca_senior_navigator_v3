Repo Reorg Plan — README for AI Assistant (REORG_PLAN.md)

Here’s a .md file you can drop into your repo root and open with Claude 4.5 or Codex in VS Code to guide the automated reorganization safely.

# Concierge Care Advisors — Repo Reorganization Plan
**Objective:** Align `cca_senior_navigator_v3` to the new normalized hub structure and retire legacy hubs.

---

## 1️⃣ Overview

We are reorganizing the app into **audience-oriented hubs** and cleaning up deprecated structures.
This document describes the intended final structure, migration rules, and verification steps for refactoring.

---

## 2️⃣ Target Folder Structure



hubs/
└── lobby_hub/
├── hub_layout.py
├── hub_config.py
├── navi/
│ ├── ai_advisor.py
│ ├── persona_profiles.py
│ ├── conversation_flows.py
│ ├── memory_store.py
│ ├── ui.py
│ ├── config.py
│ └── init.py
└── product_tiles/
├── guided_care_plan/
│ ├── modules/
│ │ └── care_recommendation/
│ │ ├── decision_engine.py
│ │ ├── ui.py
│ │ └── init.py
│ ├── config.py
│ └── init.py
├── cost_planner/
│ ├── modules/
│ │ ├── intro/
│ │ ├── quick_estimate/
│ │ └── financial_assessment/
│ │ └── assessments/
│ ├── config.py
│ └── init.py
├── my_advisor/
│ ├── modules/
│ │ └── appointment_booking/
│ ├── config.py
│ └── init.py
└── understanding_my_recommendation/
├── modules/
│ └── explanation/
├── config.py
└── init.py
mcip/
├── manager.py
├── state/
│ └── user_progress.json
└── init.py


---

## 3️⃣ Migration Tasks

### 🧹 Remove or rename
| Old Path | Action |
|-----------|--------|
| `waiting_room_hub/` | Archive or delete (merged into Lobby). |
| `concierge_hub/` | Rename to `lobby_hub/`. Update all imports. |

### 🧠 Extract system layers
| Source | Destination | Purpose |
|---------|--------------|----------|
| `utils/mcip.py` or similar | `mcip/manager.py` | Orchestrates tile unlocking and journey logic. |
| `ai_assistant.py`, `chat.py`, `navi_agent.py` | `lobby_hub/navi/` | Centralize AI advisor logic. |

### 🧩 Reassign tiles
| Tile | Source | Destination |
|------|---------|-------------|
| `concierge_clinical_review` | from `waiting_room_hub/` | to `lobby_hub/product_tiles/concierge_clinical_review/` |
| `senior_brain_games` | from `waiting_room_hub/` | to `lobby_hub/product_tiles/senior_brain_games/` |

---

## 4️⃣ Update Imports

Search and replace examples:
```bash
# Replace old imports
find . -type f -name "*.py" -exec sed -i '' \
    -e 's/from concierge_hub/from hubs.lobby_hub/g' \
    -e 's/from waiting_room_hub/# deprecated waiting_room_hub removed/g' \
    {} +

5️⃣ Update Hub Configuration

Edit hubs/lobby_hub/hub_config.py:

from mcip.manager import JourneyManager

JOURNEYS = [
    {"step": 0, "title": "Discovery", "tiles": ["discovery"]},
    {"step": 1, "title": "Planning", "tiles": [
        "guided_care_plan", "cost_planner",
        "understanding_my_recommendation", "my_advisor"
    ]},
    {"step": 2, "title": "Engagement", "tiles": [
        "concierge_clinical_review", "senior_brain_games"
    ]}
]

MCIP = JourneyManager(JOURNEYS)

6️⃣ Verification Checklist

 All imports under hubs/ resolve correctly.

 MCIP state file is writable and imported in hub_layout.py.

 Navi assistant loads from hubs/lobby_hub/navi/ and can be called globally.

 Old hubs (waiting_room_hub, concierge_hub) fully removed.