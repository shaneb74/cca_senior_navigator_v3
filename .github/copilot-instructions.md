# Copilot Instructions (Senior Navigator)

## Golden Rules
- Deterministic engines are authoritative:
  - **GCP questions** come from `products/gcp_v4/modules/care_recommendation/module.json` (JSON-driven UI).
  - **GCP logic & flags** live with the module’s Python (do not invent new flags; use `core/flags.py`).
  - **Cost Planner math** stays in `products/cost_planner_v2/utils/*.py` (never change totals without explicit request).
- Feature flags:
  - `FEATURE_LLM_NAVI` controls any LLM use: `off|shadow|assist|adjust` (default: `off`).
- Routing & flow:
  - Keep hub → GCP → Cost Planner → Financial Assessment intact.
  - **Move Preferences** renders only if recommendation ∈ `{assisted_living, memory_care, memory_care_high_acuity}`.
  - Do not remove the global header.

## Canonical Paths (Source of Truth)
- **GCP v4 module.json:** `products/gcp_v4/modules/care_recommendation/module.json`
- **GCP v4 logic:** `products/gcp_v4/modules/care_recommendation/logic.py`
- **Flag registry:** `core/flags.py`
- **Cost Planner v2:** `products/cost_planner_v2/`
- **Path helpers:** `core/paths.py` (use `get_gcp_module_path()` / `get_static()`)

## Acceptance style
- Make small, surgical commits; list files changed + diffstat.
- Use dev-only diagnostics with clear tags (e.g., `[GCP_WARN]`, `[LLM_SHADOW]`) and remove after verification.

## Things to Avoid
- Don't modify calculators or change costs unless told to.
- Don't introduce flags that aren't in `core/flags.py`.
- Don't read or rely on archived/backup content, venvs, or large static blobs.

## Read-only Modules
- Treat `core/session_store.py` as read-only unless the task explicitly requests a persistence migration.
- Never rename `USER_PERSIST_KEYS` entries or change save/extract semantics without a migration plan and test update.
- If changes are required, include `BYPASS_SESSION_STORE_GUARD` in commit message and update `tests/test_persistence_keys_guard.py`.
