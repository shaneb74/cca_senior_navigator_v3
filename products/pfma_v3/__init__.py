# DEPRECATED: use products.concierge_hub.pfma_v3
# This shim maintains backward compatibility for existing imports
from products.concierge_hub.pfma_v3.product import render as render

def describe():
    return {"name": "PFMA v3", "hub": "concierge"}
