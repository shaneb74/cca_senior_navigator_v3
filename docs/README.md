# Documentation Map

## Canonical Documentation (Indexed)

These are the source-of-truth docs for developers and AI coding agents:

- **REPO_STRUCTURE.md** - High-level repository organization
- **ARCHITECTURE.md** - System architecture and design decisions  
- **CONTRIBUTING.md** - Development guidelines and workflows
- **VERIFICATION_REPORT.md** (root) - Current repo health status

## Legacy / Session Notes (Ignored by Copilot)

Historical development notes, fix logs, and session documentation:

- **docs/legacy/** - Ad-hoc session notes, implementation logs, fix documentation
  - Ignored by Copilot via `.copilotignore`
  - Excluded from VS Code search via `.vscode/settings.json`
  - Preserved for historical reference but not indexed for coding context

These files document specific fixes and development sessions but are not needed for ongoing development context.

---

## Prototype Key Handling (LLM Shadow Mode)

**For local development and testing only.**

The LLM client (`ai/llm_client.py`) uses a priority-based key resolution:

1. **Streamlit secrets** (`st.secrets["OPENAI_API_KEY"]`) - Preferred for Cloud
2. **Environment variable** (`OPENAI_API_KEY`) - Local development
3. **Embedded fallback** - Prototype testing (assembled at runtime)

⚠️ **Before production deployment:**
- Set `ALLOW_EMBEDDED_FALLBACK = False` in `ai/llm_client.py`
- Remove the `_K1`, `_K2`, `_K3`, `_K4` chunks
- Ensure secrets are properly configured in deployment environment

The embedded fallback allows the app to run immediately for testing without requiring external secret setup. Priority order ensures production secrets always take precedence.
