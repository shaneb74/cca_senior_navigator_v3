"""
App-wide validation functions.

Runs sanity checks at app startup to catch configuration issues.
"""

import json
from pathlib import Path

# Import FLAG registry without streamlit dependency
try:
    from core.flags import VALID_FLAGS, validate_flags
except ImportError:
    # Fallback if streamlit not available (CLI mode)
    # Load FLAG_REGISTRY directly from the file
    import sys

    # Read flags.py and extract FLAG_REGISTRY keys
    flags_path = Path(__file__).parent / "flags.py"
    VALID_FLAGS: set[str] = set()

    if flags_path.exists():
        # Simple parsing - extract flag IDs from FLAG_REGISTRY dict
        with flags_path.open() as f:
            in_registry = False
            for line in f:
                if "FLAG_REGISTRY:" in line:
                    in_registry = True
                elif in_registry and line.strip().startswith('"') and '": {' in line:
                    # Extract flag ID from line like:  "falls_multiple": {
                    flag_id = line.strip().split('"')[1]
                    VALID_FLAGS.add(flag_id)
                elif in_registry and line.strip() == "}":
                    break  # End of FLAG_REGISTRY

    def validate_flags(flags: list[str], module_name: str = "unknown") -> list[str]:
        """Standalone validation function for CLI mode."""
        invalid = []
        for flag in flags:
            if flag not in VALID_FLAGS:
                invalid.append(flag)
                print(f"⚠️  WARNING: Module '{module_name}' tried to set undefined flag: '{flag}'")
                print("    Valid flags must be registered in core/flags.py FLAG_REGISTRY")
        return invalid


def validate_module_flags(module_path: str, module_name: str) -> tuple[bool, list[str], list[str]]:
    """Validate that all flags in a module.json are registered in FLAG_REGISTRY.

    Args:
        module_path: Path to module.json file
        module_name: Human-readable module name for error messages

    Returns:
        Tuple of (is_valid, all_flags_used, invalid_flags)
        - is_valid: True if all flags are registered
        - all_flags_used: List of all flag IDs used in this module
        - invalid_flags: List of flag IDs not in FLAG_REGISTRY
    """
    path = Path(module_path)

    if not path.exists():
        return True, [], []  # Skip validation if file doesn't exist

    try:
        with path.open() as f:
            data = json.load(f)
    except Exception as e:
        print(f"⚠️  Could not load {module_path}: {e}")
        return True, [], []

    # Extract all flag IDs from options
    flags_used = set()
    for section in data.get("sections", []):
        for question in section.get("questions", []):
            for option in question.get("options", []):
                option_flags = option.get("flags", [])
                flags_used.update(option_flags)

    flags_list = list(flags_used)
    invalid = validate_flags(flags_list, module_name)

    return len(invalid) == 0, flags_list, invalid


def validate_all_modules() -> dict[str, dict]:
    """Validate all module.json files in the workspace.

    Returns:
        Dict mapping module names to validation results:
        {
            "gcp_care_recommendation": {
                "valid": True,
                "flags_used": [...],
                "invalid_flags": []
            },
            ...
        }
    """
    results = {}

    # GCP Care Recommendation module
    gcp_path = "products/gcp_v4/modules/care_recommendation/module.json"
    is_valid, flags_used, invalid = validate_module_flags(gcp_path, "GCP Care Recommendation")
    results["gcp_care_recommendation"] = {
        "valid": is_valid,
        "flags_used": flags_used,
        "invalid_flags": invalid,
        "path": gcp_path,
    }

    # Add other modules here as they are created
    # Example:
    # cost_planner_path = "products/cost_planner_v2/modules/financial_assessment/module.json"
    # is_valid, flags_used, invalid = validate_module_flags(cost_planner_path, "Cost Planner")
    # results["cost_planner_financial"] = {...}

    return results


def get_validation_summary() -> str:
    """Get a human-readable summary of validation results.

    Returns:
        Formatted string with validation summary
    """
    results = validate_all_modules()

    total_modules = len(results)
    valid_modules = sum(1 for r in results.values() if r["valid"])
    invalid_modules = total_modules - valid_modules

    lines = []
    lines.append("=" * 60)
    lines.append("FLAG VALIDATION SUMMARY")
    lines.append("=" * 60)
    lines.append(f"Modules checked: {total_modules}")
    lines.append(f"Valid: {valid_modules} ✅")
    lines.append(f"Invalid: {invalid_modules} ❌")
    lines.append("")

    if invalid_modules > 0:
        lines.append("ISSUES FOUND:")
        lines.append("")
        for module_name, result in results.items():
            if not result["valid"]:
                lines.append(f"❌ {module_name}")
                lines.append(f"   Path: {result['path']}")
                lines.append(f"   Invalid flags: {', '.join(result['invalid_flags'])}")
                lines.append("")
        lines.append("ACTION REQUIRED:")
        lines.append("1. Register these flags in core/flags.py FLAG_REGISTRY, OR")
        lines.append("2. Remove them from the module.json files")
        lines.append("")
    else:
        lines.append("✅ All modules use valid flags!")
        lines.append("")

    lines.append("=" * 60)

    return "\n".join(lines)


def check_flags_at_startup(verbose: bool = False) -> bool:
    """Run flag validation at app startup.

    Args:
        verbose: If True, print detailed validation summary

    Returns:
        True if all validations pass, False otherwise
    """
    results = validate_all_modules()
    all_valid = all(r["valid"] for r in results.values())

    if not all_valid or verbose:
        print(get_validation_summary())

    return all_valid


if __name__ == "__main__":
    # Allow running as script for manual validation
    import sys

    sys.exit(0 if check_flags_at_startup(verbose=True) else 1)
