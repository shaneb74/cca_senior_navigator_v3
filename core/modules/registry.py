"""Registry for custom step renderers.

Allows products to register custom rendering functions for specific steps
while keeping navigation/state management in the module engine.

Example usage:

    # In product initialization
    from core.modules import registry

    def render_custom_step(config, step, step_index, state):
        st.markdown("Custom UI here")
        # Return state updates or None
        return {"custom_field": "value"}

    registry.register_step_renderer("custom_step_id", render_custom_step)

    # Engine automatically uses custom renderer when step.id matches
"""

from collections.abc import Callable
from typing import Any

# Type alias for renderer function signature
# Args: (config: ModuleConfig, step: StepDef, step_index: int, state: dict)
# Returns: Optional dict with state updates
StepRenderer = Callable[[Any, Any, int, dict[str, Any]], dict[str, Any] | None]

# Global registry of custom renderers
_CUSTOM_RENDERERS: dict[str, StepRenderer] = {}


def register_step_renderer(step_id: str, renderer: StepRenderer) -> None:
    """Register a custom renderer for a step ID.

    The renderer will be called instead of standard field rendering when
    the module engine encounters a step with matching ID.

    Renderer Signature:
        def custom_renderer(
            config: ModuleConfig,
            step: StepDef,
            step_index: int,
            state: Dict[str, Any]
        ) -> Optional[Dict[str, Any]]:
            # Render custom UI with streamlit
            # Return dict of state updates or None
            pass

    Args:
        step_id: Unique identifier for the step (must match StepDef.id)
        renderer: Function implementing custom rendering logic

    Raises:
        ValueError: If step_id is empty or renderer is not callable
    """
    if not step_id or not isinstance(step_id, str):
        raise ValueError("step_id must be a non-empty string")

    if not callable(renderer):
        raise ValueError("renderer must be a callable function")

    _CUSTOM_RENDERERS[step_id] = renderer


def get_step_renderer(step_id: str) -> StepRenderer | None:
    """Get custom renderer for a step ID.

    Args:
        step_id: Step identifier to lookup

    Returns:
        Renderer function if registered, None otherwise
    """
    return _CUSTOM_RENDERERS.get(step_id)


def has_step_renderer(step_id: str) -> bool:
    """Check if a custom renderer is registered for a step ID.

    Args:
        step_id: Step identifier to check

    Returns:
        True if custom renderer exists, False otherwise
    """
    return step_id in _CUSTOM_RENDERERS


def unregister_step_renderer(step_id: str) -> bool:
    """Remove a custom renderer registration.

    Args:
        step_id: Step identifier to unregister

    Returns:
        True if renderer was removed, False if not found
    """
    if step_id in _CUSTOM_RENDERERS:
        del _CUSTOM_RENDERERS[step_id]
        return True
    return False


def clear_registry() -> None:
    """Clear all registered renderers.

    Useful for testing or reinitializing the application.
    """
    _CUSTOM_RENDERERS.clear()


def list_registered_renderers() -> list:
    """Get list of all registered step IDs.

    Returns:
        List of step IDs with custom renderers
    """
    return list(_CUSTOM_RENDERERS.keys())


__all__ = [
    "StepRenderer",
    "register_step_renderer",
    "get_step_renderer",
    "has_step_renderer",
    "unregister_step_renderer",
    "clear_registry",
    "list_registered_renderers",
]
