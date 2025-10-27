#!/usr/bin/env python3
"""CI Guard - Prevent CSS/HTML regressions in Advisor and FAQ."""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# CSS scoping rules
DANGEROUS_CSS_PATTERNS = [
    (r"^\s*input\[type=['\"]radio['\"]\]", "Global radio selector (must scope under .mod-radio-pills)"),
    (r"^\s*\[data-testid=['\"]stRadio['\"]\](?!\s)", "Global stRadio selector (must scope under .mod-radio-pills)"),
    (r"^\s*\.stButton\s+button(?!\s*\{)", "Global stButton selector (scope to .mod-choices or module)"),
    (r"^\s*\.stMarkdown(?!\s)", "Global stMarkdown selector (scope to .sn-app .mod-wrap)"),
]

# HTML wrapper patterns that should NOT exist in Advisor/FAQ render code
BANNED_HTML_WRAPPERS = [
    (r'<div\s+class=["\']chat-bubble__content["\']', "Legacy chat-bubble__content wrapper"),
    (r'<div\s+class=["\']chat-sources["\']', "Legacy chat-sources wrapper"),
    (r'<span\s+class=["\']chat-source-pill["\']', "Legacy chat-source-pill wrapper"),
    (r'unsafe_allow_html\s*=\s*True', "unsafe_allow_html=True in Advisor render"),
]


def check_css_scope(file_path: Path) -> list[str]:
    """Check CSS file for dangerous global selectors."""
    errors = []
    content = file_path.read_text()
    
    for line_num, line in enumerate(content.split("\n"), 1):
        for pattern, description in DANGEROUS_CSS_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                errors.append(f"{file_path}:{line_num} - {description}\n  {line.strip()}")
    
    return errors


def check_html_wrappers(file_path: Path) -> list[str]:
    """Check Python files for banned HTML wrapper patterns."""
    errors = []
    content = file_path.read_text()
    
    for line_num, line in enumerate(content.split("\n"), 1):
        for pattern, description in BANNED_HTML_WRAPPERS:
            if re.search(pattern, line, re.IGNORECASE):
                errors.append(f"{file_path}:{line_num} - {description}\n  {line.strip()}")
    
    return errors


def main():
    """Run all CI guards."""
    all_errors = []
    
    # Check CSS files
    css_files = [
        REPO_ROOT / "assets" / "css" / "global.css",
        REPO_ROOT / "assets" / "css" / "modules.css",
    ]
    
    for css_file in css_files:
        if css_file.exists():
            errors = check_css_scope(css_file)
            if errors:
                all_errors.append(f"\n❌ CSS Scope Violations in {css_file.name}:")
                all_errors.extend(errors)
    
    # Check Advisor/FAQ Python files
    advisor_files = [
        REPO_ROOT / "products" / "concierge_hub" / "ai_advisor" / "__init__.py",
        REPO_ROOT / "products" / "global" / "ai" / "advisor_service.py",
        REPO_ROOT / "pages" / "faq.py",
    ]
    
    for py_file in advisor_files:
        if py_file.exists():
            errors = check_html_wrappers(py_file)
            if errors:
                all_errors.append(f"\n❌ HTML Wrapper Violations in {py_file.name}:")
                all_errors.extend(errors)
    
    # Report results
    if all_errors:
        print("=" * 80)
        print("🚨 CI GUARD FAILURES DETECTED")
        print("=" * 80)
        for error in all_errors:
            print(error)
        print("\n" + "=" * 80)
        print("Fix these violations before merging.")
        print("=" * 80)
        sys.exit(1)
    else:
        print("✅ All CI guards passed - no CSS/HTML regressions detected")
        sys.exit(0)


if __name__ == "__main__":
    main()
