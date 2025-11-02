"""Canary test: forbid duplicate radio/pill styles in CSS files."""
import pathlib
import re


def test_no_radio_css_in_assets():
    """Ensure radio/pill styles only live in core/ui_css.py, not in static CSS."""
    css_dir = pathlib.Path("assets/css")
    offenders = []
    
    # Patterns that indicate radio/pill styling
    patterns = [
        r'data-testid="stRadio"',
        r'role="radiogroup"',
        r'input\[type="radio"\]',
        r'\[aria-checked',
    ]
    
    # Check all CSS files in assets/css/
    for p in css_dir.rglob("*.css"):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
            if any(re.search(ptn, text) for ptn in patterns):
                offenders.append(str(p))
        except Exception:
            continue  # Skip files that can't be read
    
    assert not offenders, (
        f"Radio/pill styles must live in core/ui_css.py ONLY. "
        f"Found radio selectors in: {offenders}"
    )
