# DEPRECATED: use products.resources.med_manage
# This shim maintains backward compatibility for existing imports
from products.resources.med_manage.product import render as render

def describe():
    return {"name": "Medication Management", "hub": "resources", "status": "placeholder"}
