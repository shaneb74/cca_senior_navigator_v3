# components/cards.py
"""
Service Card Component

Phase 5L: Lightweight HTML renderer for additional services cards.
Used by hub_lobby.py to display partner/upsell modules in a dynamic grid.
"""


def render_service_card(key: str, title: str, desc: str, cta: str, route: str, visible: bool = True) -> str:
    """
    Render a simple service card with title, description, and CTA link.
    
    Phase 5L: Clean, minimal design for partner/upsell modules.
    
    Args:
        key: Unique identifier for the service (used as HTML id)
        title: Service title
        desc: Service description
        cta: Call-to-action button text
        route: URL route (query param format like "?page=ai_health_check")
        visible: Whether card should be displayed (default: True)
    
    Returns:
        HTML string for the service card
    """
    if not visible:
        return ""
    
    return f"""
    <div class="service-card" id="{key}">
        <div class="service-card-content">
            <h4>{title}</h4>
            <p>{desc}</p>
            <a class="service-cta" href="{route}">{cta}</a>
        </div>
    </div>
    """
