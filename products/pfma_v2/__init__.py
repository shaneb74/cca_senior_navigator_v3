"""
PFMA v2 - Plan with My Advisor

MCIP v2 Integration:
- Gates on Cost Planner completion (via MCIP)
- Reads care recommendation and financial profile for context
- Publishes AdvisorAppointment to MCIP when complete
- Marks PFMA complete in journey
"""

from products.pfma_v2.product import render

__all__ = ["render"]
