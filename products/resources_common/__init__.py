# DEPRECATED: use products.resources.resources_common
# This shim maintains backward compatibility for existing imports
from products.resources.resources_common.coming_soon import render_coming_soon

def describe():
    return {"name": "Resources Common Utilities", "hub": "resources", "status": "utility"}
