Excellent — here’s a **fully detailed, developer-safe Markdown plan** you can drop in `docs/CLEANUP_PLAN.md`.
It’s structured to guide Claude or any collaborator through the cleanup **without losing environment configuration, venv bindings, or terminal preferences.**

---

````markdown
# 🧹 Senior Navigator — Repository Cleanup Plan

**Branch:** `feature/phase5i_repo_cleanup`  
**Owner:** Concierge Care Advisors / Senior Navigator  
**Prepared:** 2025-10-30  
**Goal:** Safely refactor and declutter the repository following the Hub redesign (Phase 5G), while preserving all functional environments and developer workflows.

---

## 🧭 1. Objectives

1. Reorganize directories to reflect the new **multi-hub architecture**.  
2. Eliminate legacy Streamlit pages, unused assets, and redundant core modules.  
3. Maintain full **rollback and recovery capability** throughout cleanup.  
4. Preserve **virtual environments**, **venv config**, **terminal hotkeys**, and all IDE settings.  
5. Document every movement and deletion for PR traceability.

---

## 🧩 2. Pre-Cleanup Safeguards

Before any file movement or deletion:

1. **Create a full repository backup**
   ```bash
   git branch backup/pre_cleanup_$(date +%Y%m%d)
   zip -r backup_repo_$(date +%Y%m%d).zip .
````

2. **Preserve virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip freeze > requirements.lock
   ```

   * Do **not delete** `.venv/`, `.env`, or `.python-version`.
   * Add `.venv` to `.gitignore` (if not already).

3. **Save developer configs**

   ```bash
   mkdir -p dev_backup
   cp ~/.zshrc dev_backup/zshrc_backup_$(date +%Y%m%d)
   cp ~/.bash_profile dev_backup/bash_profile_backup_$(date +%Y%m%d)
   cp ~/.vscode/keybindings.json dev_backup/ || true
   ```

   This prevents loss of terminal shortcuts and VS Code hotkeys.

4. **Snapshot dependencies**

   ```bash
   pip list --format=freeze > dev_backup/pip_list_snapshot.txt
   ```

5. **Tag the current state**

   ```bash
   git tag -a pre_cleanup -m "Snapshot before Phase 5I repo cleanup"
   ```

---

## 🧱 3. Target Structure (Post-Cleanup)

### ✅ Proposed Folder Layout

```
app.py
core/
ui/
hubs/
    concierge/
    professional/
    resources/
shared/
    components/
    tiles/
assets/
    css/
    images/
docs/
    specs/
    cleanup/
tests/
```

**Key ideas:**

* `core/` → state, session, navigation logic only.
* `ui/` → app-wide layout, chrome, and NAVI framework.
* `shared/` → cross-hub components and renderers.
* `hubs/` → hub-specific logic (Concierge, Professional, Resources).
* `assets/` → all visual and style resources.
* `docs/specs/` → feature briefs by phase.
* `tests/` → unified hub smoke tests.

---

## 🧩 4. Cleanup Task Matrix

| Category            | Task                                                                  | Responsible | Tool/Command |
| ------------------- | --------------------------------------------------------------------- | ----------- | ------------ |
| Legacy Pages        | Move `pages/*.py` → `archive/pages_legacy/`                           | Claude      | `git mv`     |
| Product Modules     | Merge all Concierge products under `hubs/concierge/`                  | Claude      | manual       |
| Layout Split        | Move `layout.py` → `ui/layout_base.py` + `ui/nav.py` + `ui/footer.py` | Claude      | manual       |
| Core Simplification | Merge `core/state_bootstrap.py` into `core/state.py`                  | Claude      | manual       |
| Static Assets       | Move `static/images` → `assets/images`                                | Claude      | `git mv`     |
| CSS                 | Merge `dashboard.css` and `modules.css` → `assets/css/global.css`     | Claude      | manual       |
| Logging             | Centralize in `core/log.py`                                           | Claude      | manual       |
| Tests               | Add `tests/test_hubs_smoke.py`                                        | Claude      | pytest       |
| Docs                | Create `docs/cleanup/CHANGELOG_CLEANUP.md`                            | ChatGPT     | automated    |
| Backup              | Create `backup_repo_YYYYMMDD.zip`                                     | All         | script       |

---

## 🔒 5. Safety Mechanisms

* **Backup branch:** `backup/pre_cleanup_*` (never delete).
* **Rollback command:**

  ```bash
  git checkout backup/pre_cleanup_YYYYMMDD
  ```
* **Restore venv:**

  ```bash
  python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.lock
  ```
* **Auto-sync protection:** disable GitHub Actions auto-deploy during cleanup:

  ```bash
  touch .no_ci
  ```

---

## 🧾 6. Developer Environment Preservation

* Retain `.vscode/` folder (if exists).
* Keep `Makefile` and `.env` untouched.
* Maintain `openai_api_key` and other secrets in `.env`; never commit.
* Keep `requirements.lock` under version control for reproducibility.
* Verify that `PYTHONPATH` still resolves `/core` and `/ui`.

---

## ⚙️ 7. Verification Steps

| Check             | Command                 | Expected                       |
| ----------------- | ----------------------- | ------------------------------ |
| Import Resolution | `pytest --collect-only` | All imports resolve cleanly    |
| UI Launch         | `streamlit run app.py`  | Lobby and hubs render normally |
| CSS Integrity     | manual visual QA        | All tiles and borders intact   |
| Navigation        | clickthrough            | No missing routes              |
| Docs Index        | open `docs/specs/`      | All Phase 5+ briefs present    |

---

## 📦 8. Deliverables

| Output                                | Description              |
| ------------------------------------- | ------------------------ |
| `docs/CLEANUP_PLAN.md`                | This plan                |
| `backup_repo_YYYYMMDD.zip`            | Full pre-cleanup archive |
| `docs/cleanup/CHANGELOG_CLEANUP.md`   | Commit-by-commit summary |
| `tests/test_hubs_smoke.py`            | Sanity test suite        |
| `feature/phase5i_repo_cleanup` branch | All refactor commits     |

---

## 🧭 9. Commit Template

```
chore(cleanup): refactor repository structure for hub alignment

- Moved legacy pages to archive/
- Split layout into modular ui/
- Relocated static → assets/
- Preserved venv + dev config
- Created backup branch and zip archive
```

---

## 🧩 10. Phase Sequence

| Phase | Focus                                          | Status      |
| ----- | ---------------------------------------------- | ----------- |
| 5G    | Journey Hierarchy & Visual Identity            | ✅           |
| 5H    | Extend layout to Professional & Resources Hubs | ⏳           |
| 5I    | Repository Cleanup (this document)             | 🚀 upcoming |
| 5J    | CI/CD Stabilization & Code Health              | 🔜 next     |

---

## ✅ Expected Outcome

* Clean, modular repository consistent with the new hub design.
* Safe backups for rollback.
* Maintained venv, configs, and dev shortcuts.
* Simplified onboarding for new developers.
* Clear documentation hierarchy for future phases.

---

**End of File**

```

---

Would you like me to generate a matching **Claude execution command** (like for the earlier phases) so he can safely start the cleanup using this plan — with backups and without deleting anything yet?
```
