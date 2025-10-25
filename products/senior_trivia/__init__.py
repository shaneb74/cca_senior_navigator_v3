# DEPRECATED: use products.waiting_room.senior_trivia
# This shim maintains backward compatibility for existing imports
from products.waiting_room.senior_trivia.product import render as render

def describe():
    return {"name": "Senior Trivia", "hub": "waiting_room"}
