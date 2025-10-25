# DEPRECATED: use products.waiting_room.home_safety
# This shim maintains backward compatibility for existing imports
from products.waiting_room.home_safety.product import render as render

def describe():
    return {"name": "Home Safety", "hub": "waiting_room"}
