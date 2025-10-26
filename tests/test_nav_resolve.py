"""Test navigation module resolution."""

import json
import importlib
import sys
from pathlib import Path


def test_nav_modules_resolve():
    """Verify all modules in nav.json can be imported."""
    # Add project root to path
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    nav_path = project_root / "config" / "nav.json"
    
    with open(nav_path, encoding="utf-8") as f:
        nav = json.load(f)
    
    # Collect all module paths
    modules = []
    
    def walk(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "module" and isinstance(value, str):
                    modules.append(value)
                else:
                    walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)
    
    walk(nav)
    
    # Try to import each module
    bad = []
    for mod_path in set(modules):
        # Module path format: "package.module:function"
        pkg = mod_path.split(":", 1)[0]
        try:
            importlib.import_module(pkg)
        except Exception as e:
            bad.append((mod_path, str(e)))
    
    assert not bad, f"Unresolved modules: {bad}"


if __name__ == "__main__":
    test_nav_modules_resolve()
    print("✓ All navigation modules resolve successfully")
