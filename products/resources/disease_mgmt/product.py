# products/disease_mgmt/product.py
"""Disease Management Program - Coming Soon"""

from products.resources.resources_common.coming_soon import render_coming_soon


def render():
    """Render the Disease Management Program module."""
    render_coming_soon(
        product_key="disease_mgmt",
        product_title="Disease Management Program",
        product_desc="This resource will provide comprehensive information on chronic disease management programs, care coordination services, and support tools to help you effectively manage ongoing health conditions.",
    )
