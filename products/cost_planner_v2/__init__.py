# DEPRECATED: use products.concierge_hub.cost_planner_v2
# This shim maintains backward compatibility for existing imports
from products.concierge_hub.cost_planner_v2.product import render as render
from products.concierge_hub.cost_planner_v2.intro import render as intro_render
from products.concierge_hub.cost_planner_v2.quick_estimate import render as quick_estimate_render

def describe():
    return {"name": "Cost Planner v2", "hub": "concierge"}
