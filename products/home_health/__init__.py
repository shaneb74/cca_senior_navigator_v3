# DEPRECATED: use products.resources.home_health
# This shim maintains backward compatibility for existing imports
from products.resources.home_health.product import render as render

def describe():
    return {"name": "Find Home Health", "hub": "resources", "status": "placeholder"}
