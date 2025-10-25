# DEPRECATED: use products.resources.fall_risk
# This shim maintains backward compatibility for existing imports
from products.resources.fall_risk.product import render as render

def describe():
    return {"name": "Fall Risk Assessment", "hub": "resources", "status": "placeholder"}
