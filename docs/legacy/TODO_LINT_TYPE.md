# Linting & Type Checking Follow-ups (Non-blocking)

## Status
These items are **non-blocking** for the repository reorganization. The codebase is functional and production-ready. These are quality-of-life improvements for future development.

---

## Ruff: 261 Remaining Stylistic Issues

**Current State:**
- 1,161 issues auto-fixed ✓
- 261 remaining (mostly whitespace and unused variables)

**Issue Breakdown:**
- **W293** (73 instances): Blank line contains whitespace
- **F841** (4 instances): Local variable assigned but never used
- **ARG003** (1 instance): Unused class method argument
- **E402** (2 instances): Module level import not at top of file
- **E712** (3 instances): Avoid equality comparisons to True
- **B007** (1 instance): Loop control variable not used within loop body

**Options:**

1. **Batch Auto-fix:**
   ```bash
   ruff check . --fix
   git add -u
   git commit -m "style: fix remaining ruff issues"
   ```

2. **Selective Suppression (per file):**
   Add to specific files:
   ```python
   # ruff: noqa: W293  # Allow whitespace in blank lines for readability
   ```

3. **Global Suppression (pyproject.toml):**
   ```toml
   [tool.ruff]
   ignore = ["W293"]  # Whitespace in blank lines
   ```

4. **File-level Ignore:**
   Update `pyproject.toml`:
   ```toml
   [tool.ruff]
   extend-exclude = ["tests/", "debug_*.py", "create_demo_*.py"]
   ```

**Recommendation:** Run `ruff check . --fix` periodically as part of cleanup sprints.

---

## Mypy: Path/Package Conflict + 18 Type Errors

**Current State:**
- Path conflict: `core/products/` vs top-level `products/` prevents full type checking
- 18 type errors found in partial run (optional types, union handling)

**Issue Breakdown:**

1. **Path Conflict:**
   - `core/products/__init__.py` conflicts with `products/__init__.py`
   - Mypy cannot distinguish between the two `products` modules
   
   **Solutions:**
   - **Option A:** Rename `core/products/` to `core/product_base/` or `core/product_models/`
   - **Option B:** Add explicit `mypy_path` in `pyproject.toml`:
     ```toml
     [tool.mypy]
     mypy_path = "."
     explicit_package_bases = true
     namespace_packages = false
     ```

2. **Type Errors (18 instances):**
   
   **products/senior_trivia/scoring.py:25**
   - Issue: `None` has no attribute "steps"
   - Fix: Add Optional type guard:
     ```python
     if module_config is not None and module_config.steps:
         ...
     ```

   **products/gcp_v4/modules/care_recommendation/config.py:159**
   - Issue: Incompatible default (PEP 484 `no_implicit_optional`)
   - Fix: Explicit Optional:
     ```python
     def __init__(self, field_id: str, options: Optional[list[str]] = None):
     ```

   **core/modules/components.py:309, 335**
   - Issue: Type mismatches in component rendering
   - Fix: Add explicit type annotations or use `Any`

   **core/session_store.py:729, 730, 736**
   - Issue: `SessionStateProxy` vs `dict[str, Any]` mismatch
   - Fix: Update type hints to accept both:
     ```python
     def method(state: Union[SessionStateProxy, dict[str, Any]]) -> None:
     ```

   **core/mcip.py:87, 118, 123**
   - Issue: Annotation and union-attr issues
   - Fix: Add proper type guards for Optional/Union types

   **core/flags.py:118-148**
   - Issue: Dict entry type mismatches (str vs FlagValue)
   - Fix: Use TypedDict or refine Flag type definitions

**Recommendation:** 
1. Address path conflict first (rename `core/products/` to `core/product_models/`)
2. Add explicit Optional types where PEP 484 violations occur
3. Use `# type: ignore[attr-defined]` for complex union types that are safe but hard to annotate

---

## Action Plan

### Immediate (Optional):
- [ ] Fix path conflict by renaming `core/products/` → `core/product_models/`
- [ ] Run `ruff check . --fix` to clean up whitespace issues

### Short-term (Next Sprint):
- [ ] Add explicit Optional type hints for PEP 484 violations
- [ ] Remove unused variables (F841 errors)
- [ ] Fix import ordering (E402 errors)

### Long-term (Backlog):
- [ ] Full mypy type coverage with `--strict` mode
- [ ] Add type stubs for external libraries if needed
- [ ] Enable `disallow_untyped_defs = true` incrementally

---

## Testing After Fixes

```bash
# Run full check suite
make check

# Or individual checks
make lint
make type
make smoke
```

---

*Generated: 2025-01-22*  
*Context: Repository reorganization verification*
