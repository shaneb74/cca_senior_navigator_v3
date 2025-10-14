"""Module hub component for displaying sub-module selection dashboard.

Provides a reusable component for products that have multiple sub-modules,
displaying them as tiles with progress tracking, conditional visibility,
and lock/unlock logic.
"""

from typing import Any, Callable, Dict, List, Optional
import streamlit as st
from core.product_tile import ModuleTileCompact


class ModuleHub:
    """Dashboard for selecting and navigating between product sub-modules.
    
    Displays tiles for each module with:
    - Progress tracking from session state
    - Conditional visibility based on profile/flags
    - Lock/unlock logic with messages
    - Navigation to module pages
    - Required vs. optional badge display
    
    Example usage:
        
        modules = [
            {
                "id": "income",
                "title": "Income Sources",
                "description": "Social Security, pensions, etc.",
                "icon": "💰",
                "required": True,
                "visible_if": lambda: True,
                "unlock_if": lambda: True,
            },
            {
                "id": "va_benefits",
                "title": "VA Benefits",
                "description": "Veterans benefits",
                "icon": "🎖️",
                "required": False,
                "visible_if": lambda: is_veteran(),
                "unlock_if": lambda: income_complete(),
                "lock_msg": "Complete Income module first",
            },
        ]
        
        hub = ModuleHub(
            product_key="cost_planner",
            modules=modules,
            base_route="?page=cost&cost_module=",
            title="Financial Assessment",
        )
        hub.render()
    """
    
    def __init__(
        self,
        product_key: str,
        modules: List[Dict[str, Any]],
        base_route: str,
        title: str = "Select a Module",
        subtitle: Optional[str] = None,
        columns: int = 2,
    ):
        """Initialize module hub.
        
        Args:
            product_key: Product identifier (e.g., "cost_planner_v2")
            modules: List of module definitions with keys:
                - id: Module identifier (required)
                - title: Display title (required)
                - description: Short description (optional)
                - icon: Emoji or icon (optional)
                - required: Whether module is required (default: False)
                - visible_if: Callable returning bool for visibility (default: always visible)
                - unlock_if: Callable returning bool for unlocked state (default: always unlocked)
                - lock_msg: Message to show when locked (optional)
            base_route: Base URL for module navigation (e.g., "?page=cost&cost_module=")
            title: Hub title
            subtitle: Optional subtitle/instructions
            columns: Number of columns for tile layout (default: 2)
        """
        self.product_key = product_key
        self.modules = modules
        self.base_route = base_route
        self.title = title
        self.subtitle = subtitle
        self.columns = columns
        
        # Validate modules
        for i, module in enumerate(modules):
            if "id" not in module:
                raise ValueError(f"Module at index {i} missing required 'id' field")
            if "title" not in module:
                raise ValueError(f"Module '{module['id']}' missing required 'title' field")
    
    def render(self) -> None:
        """Render the module hub with tiles."""
        st.markdown(f"### {self.title}")
        if self.subtitle:
            st.caption(self.subtitle)
        
        # Filter visible modules
        visible_modules = [
            m for m in self.modules
            if m.get("visible_if", lambda: True)()
        ]
        
        if not visible_modules:
            st.warning("⚠️ No modules available. Please update your profile or complete prerequisites.")
            return
        
        # Calculate required vs optional counts
        required_count = len([m for m in visible_modules if m.get("required", False)])
        optional_count = len(visible_modules) - required_count
        
        # Show summary
        if required_count > 0:
            summary_parts = [f"{required_count} required module{'s' if required_count != 1 else ''}"]
            if optional_count > 0:
                summary_parts.append(f"{optional_count} optional")
            st.caption(f"📊 {' • '.join(summary_parts)}")
        
        st.markdown("---")
        
        # Render tiles in grid layout
        for i in range(0, len(visible_modules), self.columns):
            cols = st.columns(self.columns)
            for j, col in enumerate(cols):
                if i + j < len(visible_modules):
                    module = visible_modules[i + j]
                    with col:
                        self._render_module_tile(module)
        
        st.markdown("---")
    
    def _render_module_tile(self, module: Dict[str, Any]) -> None:
        """Render a single module tile.
        
        Args:
            module: Module definition dict
        """
        module_id = module["id"]
        state_key = f"{self.product_key}.{module_id}"
        
        # Get progress from session state
        module_state = st.session_state.get(state_key, {})
        progress = float(module_state.get("progress", 0))
        
        # Check if locked
        is_locked = not module.get("unlock_if", lambda: True)()
        lock_msg = module.get("lock_msg", "Complete required modules first")
        
        # Build title with icon
        icon = module.get("icon", "")
        title = f"{icon} {module['title']}" if icon else module["title"]
        
        # Determine badge
        badge_text = None
        if module.get("required", False):
            badge_text = "Required"
        
        # Create tile
        tile = ModuleTileCompact(
            key=module_id,
            title=title,
            blurb=module.get("description"),
            progress=progress,
            locked=is_locked,
            lock_msg=lock_msg if is_locked else None,
            primary_route=f"{self.base_route}{module_id}",
            badge_text=badge_text,
        )
        tile.render()
    
    def get_visible_modules(self) -> List[Dict[str, Any]]:
        """Get list of currently visible modules.
        
        Returns:
            List of module dicts that pass visibility check
        """
        return [
            m for m in self.modules
            if m.get("visible_if", lambda: True)()
        ]
    
    def get_completed_count(self) -> int:
        """Get count of completed visible modules.
        
        Returns:
            Number of modules with progress >= 100
        """
        count = 0
        for module in self.get_visible_modules():
            state_key = f"{self.product_key}.{module['id']}"
            module_state = st.session_state.get(state_key, {})
            if float(module_state.get("progress", 0)) >= 100:
                count += 1
        return count
    
    def get_required_completed_count(self) -> int:
        """Get count of completed required modules.
        
        Returns:
            Number of required modules with progress >= 100
        """
        count = 0
        for module in self.get_visible_modules():
            if not module.get("required", False):
                continue
            state_key = f"{self.product_key}.{module['id']}"
            module_state = st.session_state.get(state_key, {})
            if float(module_state.get("progress", 0)) >= 100:
                count += 1
        return count
    
    def all_required_completed(self) -> bool:
        """Check if all required modules are completed.
        
        Returns:
            True if all required visible modules have progress >= 100
        """
        required_modules = [m for m in self.get_visible_modules() if m.get("required", False)]
        if not required_modules:
            return True  # No required modules
        
        for module in required_modules:
            state_key = f"{self.product_key}.{module['id']}"
            module_state = st.session_state.get(state_key, {})
            if float(module_state.get("progress", 0)) < 100:
                return False
        
        return True


__all__ = ["ModuleHub"]
