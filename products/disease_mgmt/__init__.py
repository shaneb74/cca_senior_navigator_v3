# DEPRECATED: use products.resources.disease_mgmt
# This shim maintains backward compatibility for existing imports
from products.resources.disease_mgmt.product import render as render

def describe():
    return {"name": "Disease Management Program", "hub": "resources", "status": "placeholder"}
