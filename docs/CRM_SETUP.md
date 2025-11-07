Perfect — here’s the **fully revised `docs/CRM_SETUP.md`** including the new user-role context and all VS Code setup instructions.

You can drop this file directly into your repo at `docs/CRM_SETUP.md` (or root-level if you prefer).

---

````markdown
# 🧩 Senior Navigator CRM – Developer Setup Guide

## 🧭 Context: Two Distinct Apps, Two Distinct Roles

This repository contains **two complementary Streamlit applications** that share a common core, data layer, and visual language — but serve **different users**.

| App | Primary User | Purpose | Typical Actions |
|------|---------------|----------|-----------------|
| **Senior Navigator** (`app.py`) | **Customer / Family Member** | Guided care planning, education, and self-service tools. | Explore care options, complete assessments, view recommendations, save plans. |
| **Advisor CRM** (`crm_app.py`) | **Advisor / Case Manager** | Manage customer data, appointments, notes, and workflow. | Review customer files, schedule consultations, log interactions, manage tasks. |

Both apps share utilities in `core/` and `shared/`, but differ in:

- **Audience tone** → Customer vs. professional.  
- **Data access scope** → Customers only see their own data; advisors can view many.  
- **Authentication model** → Planned: advisor login (CRM) vs. anonymous / limited session (Navigator).  
- **Persistence** → Both apps currently use **fake data connections**: JSON demo files in `data/users/` and `data/users/demo/`.

When extending the system, always clarify:
> “Is this feature for the *customer* or the *advisor*?”

That determines where the code, UI, and data should live.

---

## ⚙️ 1. Prerequisites

1. **Python ≥ 3.11**
2. **Virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
````

3. **Dependencies**

   ```bash
   pip install -r requirements.txt
   ```
4. **VS Code Extensions**

   * Python (ms-python.python)
   * Pylance
   * Ruff or Flake8 (for linting)
   * Streamlit for VS Code (optional live preview)

---

## 🧱 2. Folder layout (after adding the CRM app)

```
repo-root/
├── app.py                       ← existing Senior Navigator app
├── crm_app.py                   ← new Advisor CRM entrypoint
├── apps/
│   ├── navi_core/
│   └── crm/
│       ├── __init__.py
│       └── pages/
│           ├── contacts.py
│           ├── organizations.py
│           ├── deals.py
│           └── tasks.py
├── shared/
│   └── fakedb/
│       ├── __init__.py
│       └── repo.py
└── data/
    ├── users/
    │   └── demo/
    └── crm_demo/
        ├── contacts.jsonl
        ├── organizations.jsonl
        ├── deals.jsonl
        └── tasks.jsonl
```

---

## 🧮 3. Create the fake data layer

**`shared/fakedb/repo.py`**

```python
"""
Lightweight JSON-Lines persistence used by the CRM demo app.
Each entity (contacts, orgs, etc.) is stored in data/crm_demo/<entity>.jsonl
"""
import json
from pathlib import Path
from typing import Any

DATA_ROOT = Path("data/crm_demo")
DATA_ROOT.mkdir(parents=True, exist_ok=True)

def _load(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

def _save(path: Path, rows: list[dict[str, Any]]):
    lines = [json.dumps(r, ensure_ascii=False) for r in rows]
    path.write_text("\n".join(lines), encoding="utf-8")

def list_records(entity: str) -> list[dict[str, Any]]:
    """Return all rows for the given entity (contacts, deals, etc.)."""
    return _load(DATA_ROOT / f"{entity}.jsonl")

def save_record(entity: str, record: dict[str, Any]):
    """Append a record to the entity's JSON-Lines file."""
    path = DATA_ROOT / f"{entity}.jsonl"
    rows = _load(path)
    rows.append(record)
    _save(path, rows)
```

---

## 🧭 4. Scaffold the CRM entrypoint

**`crm_app.py`**

```python
import streamlit as st

st.set_page_config(page_title="Advisor CRM Dashboard", layout="wide")

st.sidebar.title("CRM Navigation")
page = st.sidebar.radio("Go to", ["Contacts", "Organizations", "Deals", "Tasks"])

if page == "Contacts":
    import apps.crm.pages.contacts as contacts
    contacts.render()
elif page == "Organizations":
    import apps.crm.pages.organizations as orgs
    orgs.render()
elif page == "Deals":
    import apps.crm.pages.deals as deals
    deals.render()
else:
    import apps.crm.pages.tasks as tasks
    tasks.render()
```

---

## 👥 5. Add the first CRM page

**`apps/crm/pages/contacts.py`**

```python
import streamlit as st
from shared.fakedb.repo import list_records, save_record

def render():
    st.title("Contacts")

    contacts = list_records("contacts")
    if contacts:
        st.dataframe(contacts, use_container_width=True)
    else:
        st.info("No contacts yet.")

    st.subheader("Add New Contact")
    with st.form("add_contact"):
        first = st.text_input("First name")
        last = st.text_input("Last name")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Save")
        if submitted and first and email:
            new_contact = {
                "id": f"c{len(contacts)+1:03d}",
                "first_name": first,
                "last_name": last,
                "email": email,
            }
            save_record("contacts", new_contact)
            st.success("Contact saved!")
            st.experimental_rerun()
```

Duplicate this page to create `organizations.py`, `deals.py`, and `tasks.py` (change entity names and fields accordingly).

---

## 🧪 6. Add demo data

Create `data/crm_demo/contacts.jsonl` (and similar for orgs, deals, tasks):

```json
{"id":"c001","first_name":"Mary","last_name":"Jones","email":"mary@example.com","org_id":"o001"}
{"id":"c002","first_name":"John","last_name":"Lee","email":"john@seniorcare.org","org_id":"o002"}
```

---

## 🚀 7. Run the CRM app in VS Code

1. Open the repo in VS Code.
2. Select the `.venv` interpreter.
3. Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run CRM (Streamlit)",
      "type": "python",
      "request": "launch",
      "module": "streamlit",
      "args": ["run", "crm_app.py", "--server.port=8502"],
      "console": "integratedTerminal"
    }
  ]
}
```

4. Press **F5** or choose *Run → Start Debugging*.

Your CRM app should open at **[http://localhost:8502](http://localhost:8502)**

---

## 🖥️ 8. Running both apps side by side

| App                  | Command                    | Port | Role     | Purpose                                  |
| -------------------- | -------------------------- | ---- | -------- | ---------------------------------------- |
| **Senior Navigator** | `streamlit run app.py`     | 8501 | Customer | Guided care planning                     |
| **Advisor CRM**      | `streamlit run crm_app.py` | 8502 | Advisor  | Manage customers, appointments, workflow |

They share the same Python environment and internal modules.

---

## 🔜 9. Next steps and roadmap

### Phase 1 – Functional Prototype

* Build CRUD pages for all entities using the fake JSONL store.
* Add Pandas-based filtering and search.

### Phase 2 – Enhanced UX

* Use shared `ui/` components for consistent look and feel.
* Add “Linked Customer” views (open `data/users/demo/*`).

### Phase 3 – Authentication & Roles

* Introduce an advisor login stub (basic password or token).
* Add `st.session_state["role"]` and conditional rendering.
* Later: integrate real RBAC or SSO.

### Phase 4 – Real Data Backend

* Replace `shared/fakedb/repo.py` with a real `shared/db/` layer (SQLModel + Alembic).
* Migrate JSON demo data into tables.
* Add audit trails, concurrency safety, and data-sharing controls.

---

## ✅ Summary

You now have:

* A **Customer-facing Navigator** (`app.py`)
* An **Advisor-facing CRM** (`crm_app.py`)
* A **shared fake data layer** that persists to JSON files for quick demos
* A consistent setup experience inside VS Code

This setup preserves your existing demo data (`data/users/`, `data/users/demo/`) and extends it naturally for advisor workflows — paving the way for real multi-user, database-backed capabilities later on.


```
