"""
Empty State Component

Renders a styled empty state message for sections with no content yet.
Used for persistent sections that should always be visible.
"""


def render_empty_state(title: str, message: str, icon: str = "📭") -> str:
    """Render an empty state message.
    
    Args:
        title: Section title
        message: Empty state message
        icon: Optional emoji icon (default: 📭)
    
    Returns:
        HTML string for empty state
    """
    return f"""
    <div class="empty-state">
        <div class="empty-state-icon">{icon}</div>
        <div class="empty-state-title">{title}</div>
        <div class="empty-state-message">{message}</div>
    </div>
    """
