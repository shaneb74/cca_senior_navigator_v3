# DEPRECATED: use products.waiting_room.predictive_health
# This shim maintains backward compatibility for existing imports
from products.waiting_room.predictive_health.product import render as render

def describe():
    return {"name": "Predictive Health", "hub": "waiting_room"}
