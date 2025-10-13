#!/usr/bin/env python3
"""
Add debug_gcp page to nav.json if not already there.
"""

import json
from pathlib import Path

nav_path = Path(__file__).parent / "config" / "nav.json"

with open(nav_path) as f:
    nav_data = json.load(f)

# Find app_utilities group
for group in nav_data["groups"]:
    if group["id"] == "app_utilities":
        # Check if debug_gcp already exists
        existing = [item for item in group["items"] if item.get("key") == "debug_gcp"]
        
        if existing:
            print("✅ debug_gcp already exists in nav.json")
        else:
            # Add debug_gcp entry
            debug_entry = {
                "key": "debug_gcp",
                "label": "🔍 Debug GCP",
                "module": "pages.debug_gcp:render"
            }
            group["items"].append(debug_entry)
            
            # Write back
            with open(nav_path, "w") as f:
                json.dump(nav_data, f, indent=2)
            
            print("✅ Added debug_gcp to nav.json")
            print("   Restart Streamlit to see changes")
        break
else:
    print("❌ Could not find app_utilities group in nav.json")
