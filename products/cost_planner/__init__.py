"""Cost Planner - Multi-module financial assessment product.

This product uses a hub-and-spoke architecture:
- Base module: Landing page and module dashboard
- Sub-modules: Independent calculation modules (income, assets, costs, etc.)
- Aggregator: Combines module outcomes into product-level affordability assessment

Authentication required for most modules (except base and recommendation_cost_detail).
"""
