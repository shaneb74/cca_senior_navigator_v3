# DEPRECATED: use products.waiting_room.advisor_prep
# This shim maintains backward compatibility for existing imports
from products.waiting_room.advisor_prep.product import render as render

def describe():
    return {"name": "Advisor Prep", "hub": "waiting_room"}
