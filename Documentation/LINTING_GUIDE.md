# Linting Guide for CCA Senior Navigator v3

## Summary
Ruff linter has been installed and configured. Initial scan found **4,251 linting issues** with **3,508 auto-fixable**.

## Issue Breakdown
- **3,158** - Blank lines with whitespace (W293) - auto-fixable
- **484** - Old-style type annotations (UP006) - auto-fixable (e.g., `Dict` → `dict`)
- **173** - Old-style optional annotations (UP045) - auto-fixable (e.g., `Optional[X]` → `X | None`)
- **118** - Deprecated imports (UP035) - needs manual review (e.g., `typing.Dict`)
- **90** - Unsorted imports (I001) - auto-fixable
- **67** - Unused imports (F401) - auto-fixable
- **58** - Trailing whitespace (W291) - auto-fixable
- **32** - Unused variables (F841) - needs manual review
- **24** - Redundant open modes (UP015) - auto-fixable
- **13** - Bare except clauses (E722) - needs manual review
- Other minor issues

## How to Run Linting

### Option 1: Run the Shell Script (Easiest)
```bash
chmod +x run_linting.sh
./run_linting.sh
```

This will:
1. Auto-fix all fixable issues
2. Format code
3. Show remaining issues

### Option 2: Manual Commands

**Check for issues:**
```bash
./venv/bin/python -m ruff check . --no-cache
```

**Auto-fix issues:**
```bash
./venv/bin/python -m ruff check . --fix --no-cache
```

**Format code:**
```bash
./venv/bin/python -m ruff format . --no-cache
```

**See statistics:**
```bash
./venv/bin/python -m ruff check . --no-cache --statistics
```

### Option 3: VS Code Integration

Install the Ruff extension:
1. Open VS Code
2. Search for "Ruff" in Extensions
3. Install the official Ruff extension by Astral Software
4. It will automatically use the configuration in `.ruff.toml` or `pyproject.toml`

## Configuration Files

### pyproject.toml
Enhanced with comprehensive ruff configuration including:
- Python 3.13 target
- 100 character line length
- Import sorting (isort)
- Modern type annotations (pyupgrade)
- Bug detection (flake8-bugbear)
- Streamlit-specific ignores

### .ruff.toml
Standalone ruff configuration (alternative to pyproject.toml)

## What Was Fixed
- Added `ruff>=0.6.0` to requirements.txt
- Created comprehensive ruff configuration
- Generated linting script for easy execution
- Documented all linting issues and how to fix them

## Known Limitations
Due to macOS file permissions, the auto-fix couldn't run from the terminal session.
You'll need to run the `run_linting.sh` script manually or use VS Code with the Ruff extension.

## Next Steps
1. Run `./run_linting.sh` to auto-fix issues
2. Review remaining issues (especially bare excepts and unused variables)
3. Consider adding pre-commit hooks for automatic linting
4. Install VS Code Ruff extension for real-time linting

## Manual Review Required
After auto-fixing, you'll still have ~743 issues that need manual review:
- **32** unused variables - Remove or prefix with `_`
- **13** bare except clauses - Add specific exception types
- **118** deprecated imports - Update import statements
- Other minor issues requiring human judgment

## Resources
- Ruff Documentation: https://docs.astral.sh/ruff/
- Configuration Reference: https://docs.astral.sh/ruff/configuration/
- Rules Reference: https://docs.astral.sh/ruff/rules/
