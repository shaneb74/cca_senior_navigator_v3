# products/dme/product.py
"""Find DME (Durable Medical Equipment) - Coming Soon"""

from products.resources_common.coming_soon import render_coming_soon


def render():
    """Render the Find DME module."""
    render_coming_soon(
        product_key="dme",
        product_title="Find DME",
        product_desc="This resource will help you discover what durable medical equipment you may need, learn about coverage options through Medicare and insurance, and find local suppliers for mobility aids, bathroom safety equipment, and more.",
    )
