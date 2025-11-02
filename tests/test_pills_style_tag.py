"""Test to ensure pill CSS style tag ID remains stable."""
import re
from pathlib import Path


def test_pill_style_id_is_constant():
    """Ensure the style tag ID never changes (cascade anchor)."""
    # Read ui_css.py
    ui_css_path = Path("core/ui_css.py")
    assert ui_css_path.exists(), "core/ui_css.py not found"
    
    ui_css_content = ui_css_path.read_text(encoding="utf-8")
    
    # Verify inject_pill_css function exists
    assert "def inject_pill_css()" in ui_css_content, "inject_pill_css() function not found"
    
    # Verify STYLE_ID constant is present and correct
    STYLE_ID = "cca-pill-css"
    assert STYLE_ID in ui_css_content, f"Style ID '{STYLE_ID}' not found in ui_css.py"
    
    # Ensure PILL_CSS constant exists
    assert "PILL_CSS = r" in ui_css_content or "PILL_CSS=" in ui_css_content, "PILL_CSS constant not found"
