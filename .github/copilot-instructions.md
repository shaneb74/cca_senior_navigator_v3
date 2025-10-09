# Copilot Instructions for AI Coding Agents

## Project Overview
This is a Streamlit-based web application for senior care navigation, organized around modular hubs, products, and utility pages. The app dynamically loads navigation and page components from configuration files and supports role-based access and feature flags.

## Architecture & Key Components
- **Entry Point:** `app.py` initializes Streamlit, injects custom CSS (`assets/css/theme.css`), manages session state, and loads navigation from `config/nav.json`.
- **Navigation:**
  - Defined in `config/nav.json` (groups, items, roles, flags).
  - Pages are loaded and rendered via `core/nav.py` using dynamic imports (e.g., `pages._stubs:render_welcome`).
- **Session State:**
  - Managed in `core/state.py` (`ensure_session`, `get_user_ctx`).
  - Context (`ctx`) includes `auth` (role, authentication), and `flags`.
- **UI Components:**
  - Custom HTML/CSS via `core/ui.py` (header, footer, containers, image utilities).
  - Images in `static/images/` are referenced using `img_src()`.
- **Products & Hubs:**
  - Product logic (e.g., Guided Care Plan) in `products/gcp.py`.
  - Hub logic in `hubs/` (e.g., `hubs/concierge.py`).
  - Page stubs in `pages/_stubs.py`.
- **Config Data:**
  - GCP product uses JSON config files in `config/gcp/` (`schema.json`, `scoring.json`, `rules.json`, etc.).
  - Validation logic in `core/gcp_validate.py` (run as a module for cross-file checks).

## Developer Workflows
- **Run App:**
  - `streamlit run app.py`
- **Test GCP Validation:**
  - `pytest tests/test_gcp_validation.py` (calls `core.gcp_validate` as a module)
- **Update Navigation:**
  - Edit `config/nav.json` and ensure referenced modules/functions exist.
- **Custom CSS:**
  - Edit `assets/css/theme.css` for UI changes.

## Patterns & Conventions
- **Dynamic Page Loading:**
  - Navigation items specify `module` as `module:function` string; loaded via `importlib`.
- **Role/Flag-Based Access:**
  - Navigation and page rendering respect `roles`, `requires_auth`, and `flags` from config.
- **Session State:**
  - Use `st.session_state` for all persistent user/session data.
- **Image Handling:**
  - Use `core/ui.py:img_src()` for referencing images in markdown/HTML.
- **Testing:**
  - Tests use subprocess to validate config integrity, not direct function calls.

## External Dependencies
- **Streamlit** (UI, session, routing)
- **Pydantic** (data validation, if used in future)

## Integration Points
- **Config Files:**
  - All GCP logic depends on JSON files in `config/gcp/`.
- **Events:**
  - Logging via `core/events.py:log_event` (optional, stubbed if missing).

## Example: Adding a New Page
1. Add entry to `config/nav.json` with `key`, `label`, and `module`.
2. Implement the render function in the specified module (e.g., `pages/_stubs.py:render_new_page`).
3. Restart Streamlit to pick up changes.

---

If any section is unclear or missing, please specify which part needs more detail or examples.
