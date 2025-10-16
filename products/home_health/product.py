# products/home_health/product.py
"""Find Home Health - Coming Soon"""
from products.resources_common.coming_soon import render_coming_soon


def render():
    """Render the Find Home Health module."""
    render_coming_soon(
        product_key="home_health",
        product_title="Find Home Health",
        product_desc="This resource will help you search for qualified home health agencies, compare services and ratings, and find the right home care provider to meet your specific needs."
    )
