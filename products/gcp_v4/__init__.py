# DEPRECATED: use products.concierge_hub.gcp_v4
# This shim maintains backward compatibility for existing imports
from products.concierge_hub.gcp_v4.product import render as render

def describe():
    return {"name": "GCP v4", "hub": "concierge"}
