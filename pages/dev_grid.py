from core.base_hub import _inject_hub_css_once, render_dashboard_body
from core.product_tile import ProductTileHub
from layout import render_page

__all__ = ["render"]


def render(ctx=None):
    _inject_hub_css_once()

    tiles = [
        ProductTileHub(
            key="t1",
            title="Tile One",
            desc="Simple smoke test tile.",
            blurb="If you see this beside Tile Two on desktop, grid works.",
            primary_label="Do thing",
            primary_go="noop",
            variant="brand",
            order=10,
            visible=True,
            locked=False,
        ),
        ProductTileHub(
            key="t2",
            title="Tile Two",
            desc="Another test tile.",
            blurb="Two tiles should sit side-by-side (span 6 cols each).",
            primary_label="Another thing",
            primary_go="noop",
            variant="teal",
            order=20,
            visible=True,
            locked=False,
        ),
    ]

    body_html = render_dashboard_body(
        title="Grid Sanity Check",
        subtitle="Should be 2×2 on desktop (two tiles next to each other).",
        chips=[{"label": "Dev test"}, {"label": "No data", "variant": "muted"}],
        hub_guide_block="",
        cards=tiles,
        additional_services=[],
    )

    render_page(body_html=body_html, active_route=None)
