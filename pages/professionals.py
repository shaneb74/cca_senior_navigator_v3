from pages.welcome import render_welcome_card
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple


def _page_content(ctx=None):
    render_welcome_card(
        active="pro",
        title="Support your patients and families with coordinated care.",
        placeholder="Patient or client name",
        note="You can assess multiple clients and invite colleagues on the next step.",
        image_path="static/images/contextual_professional.png",
        submit_route="hub_professional",
    )


def render(ctx=None):
    # Render with simple header/footer
    render_header_simple(active_route="professionals")
    _page_content(ctx)
    render_footer_simple()
