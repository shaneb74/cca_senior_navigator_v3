# DEPRECATED: use products.resources.dme
# This shim maintains backward compatibility for existing imports
from products.resources.dme.product import render as render

def describe():
    return {"name": "Find DME (Durable Medical Equipment)", "hub": "resources", "status": "placeholder"}
