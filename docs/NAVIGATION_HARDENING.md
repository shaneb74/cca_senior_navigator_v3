# Navigation Hardening Implementation

## Overview

This document describes the URL-driven routing system with browser back/forward support and state safety implemented for the Senior Navigator application.

## Goals Achieved

1. ✅ **Browser Back/Forward Support** - URL query params drive routing, enabling native browser navigation
2. ✅ **Consistent Back Button** - Universal back functionality with history stack and fallback
3. ✅ **State Safety** - No blanket state clears; URL hydration preserves context across reruns

## Architecture

### Route Model

Routes are represented as query parameters following this canonical structure:

```
?page=hub_concierge                                           # Hub page
?page=product&product=cost_planner_v2                         # Product landing
?page=module&product=cost_planner_v2&module=intro            # Product module
?page=module&product=cost_planner_v2&module=assessments&step=va_benefits  # Module step
```

**Query Parameter Keys:**
- `page` - Top-level page/hub identifier
- `product` - Product identifier (for multi-module products)
- `module` - Module within a product
- `step` - Step within a module
- `uid` - User/session identifier (preserved across all navigation)

### Core Components

#### 1. URL Helpers (`core/url_helpers.py`)

Central navigation utilities:

- **`get_route_from_qp()`** - Extract route from query params
- **`set_route_qp(**parts)`** - Update query params with route info
- **`current_route()`** - Get current route (URL-first, session fallback)
- **`route_to(push=True, **parts)`** - Navigate with history tracking
- **`can_go_back()`** - Check if navigation stack has entries
- **`go_back()`** - Pop from history stack and navigate
- **`back_fallback()`** - Default fallback route (concierge hub)

#### 2. App Entry Point (`app.py`)

Hydrates route from URL once at startup:

```python
from core.url_helpers import current_route as get_current_route

if not st.session_state.get("_hydrated_from_qp"):
    st.session_state["current_route"] = get_current_route()
    st.session_state["_hydrated_from_qp"] = True
```

#### 3. Header with Back Button (`ui/header_simple.py`)

Provides universal back navigation:

```python
from core.url_helpers import can_go_back, go_back, back_fallback, route_to

def render_back_button(title: str = ""):
    """Render back button with optional title."""
    cols = st.columns([1, 12])
    with cols[0]:
        if st.button("← Back", key="global_back_btn"):
            if can_go_back():
                go_back()
            else:
                route_to(push=False, **back_fallback())
```

#### 4. Navigation Module (`core/nav.py`)

Updated to use URL-driven routing:

```python
from core.url_helpers import route_to as url_route_to

def route_to(key: str, **context) -> None:
    """Navigate with URL updates and history tracking."""
    uid = st.query_params.get("uid")
    route_params = {"page": key}
    if uid:
        route_params["uid"] = uid
    url_route_to(**route_params)
```

## Usage Patterns

### Basic Page Navigation

```python
from core.url_helpers import route_to

# Navigate to hub
route_to(page="hub_concierge")

# Navigate to product
route_to(page="product", product="cost_planner_v2")

# Navigate to module
route_to(page="module", product="cost_planner_v2", module="intro")

# Navigate to specific step
route_to(page="module", product="cost_planner_v2", module="assessments", step="va_benefits")
```

### Reading Current Route

```python
from core.url_helpers import current_route

route = current_route()
step = route.get("step", "intro")  # Get step with default
module = route.get("module")
product = route.get("product")
```

### Back Navigation

```python
from ui.header_simple import render_back_button

# In any page/module
render_back_button("Cost Planner")  # With title
render_back_button()                # Without title
```

### Navigation Without History Push

```python
from core.url_helpers import route_to

# Navigate without adding to history (e.g., redirects, fallbacks)
route_to(push=False, page="hub_concierge")
```

## State Management Rules

### ✅ DO

1. **Initialize with `setdefault`:**
   ```python
   st.session_state.setdefault("cp", {})
   st.session_state["cp"].setdefault("profile", {})
   ```

2. **Namespace state by product/module:**
   ```python
   st.session_state["cost_planner"] = {"answers": {}, "profile": {}}
   st.session_state["gcp"] = {"step": 1, "answers": {}}
   ```

3. **Read route from URL:**
   ```python
   route = current_route()
   step = route.get("step", "intro")
   ```

4. **Use `route_to()` for all navigation:**
   ```python
   route_to(page="module", product="cost_planner_v2", module="intro")
   ```

### ❌ DON'T

1. **Never call `st.session_state.clear()`** - This loses all state
2. **Don't mutate route directly** - Always use `route_to()`
3. **Don't hardcode steps** - Read from URL query params
4. **Don't mix navigation methods** - Use `route_to()` consistently

## Testing

### Navigation Module Resolution Test

Verifies all nav.json module paths can be imported:

```bash
python tests/test_nav_resolve.py
```

Expected output:
```
✓ All navigation modules resolve successfully
```

## Browser History Behavior

### Forward Navigation
1. User clicks "Continue" → `route_to(page="next_page")`
2. Previous route pushed to `_nav_stack`
3. URL updated: `?page=next_page`
4. Browser history records new URL

### Back Navigation (In-App Button)
1. User clicks "← Back" button
2. Check `_nav_stack` for history
3. If stack has entries → pop and navigate
4. If stack empty → navigate to fallback (hub)
5. URL updated and rerun triggered

### Back Navigation (Browser Button)
1. User clicks browser back button
2. Browser navigates to previous URL in history
3. App hydrates from new URL query params
4. Session state preserved (not cleared)

## Migration Path for Existing Products

### Cost Planner V2

Current state: Uses `st.session_state.cost_v2_step` for step tracking

Migration approach:
1. Read step from URL first: `route.get("step", "intro")`
2. Replace `st.rerun()` with `route_to()` calls
3. Update step transitions to use `route_to()`
4. Remove manual query param manipulation

Example before:
```python
st.session_state.cost_v2_step = "assessments"
st.rerun()
```

Example after:
```python
route_to(page="module", product="cost_planner_v2", module="assessments")
```

### GCP V4

Similar approach - migrate from session-based step tracking to URL-driven.

## Benefits

1. **Shareable URLs** - Users can bookmark/share specific steps
2. **Browser Navigation** - Back/Forward buttons work natively
3. **State Preservation** - No state loss on rerun/navigation
4. **Consistent UX** - Universal back button across all pages
5. **Debuggable** - Current state visible in URL

## Known Limitations

1. **Deep Links** - Require authentication/prerequisite checks
2. **Stack Limits** - Navigation stack grows unbounded (could add max size)
3. **External Links** - href links bypass history stack (by design)

## Future Enhancements

1. **Stack Size Limit** - Cap `_nav_stack` at N entries
2. **Route Validation** - Validate step sequences (e.g., can't skip to step 5)
3. **Route Persistence** - Save route to user profile for resume
4. **Route Analytics** - Track navigation patterns for UX optimization

## References

- Implementation: `core/url_helpers.py`
- Entry Point: `app.py` (URL hydration)
- Header Component: `ui/header_simple.py`
- Navigation Module: `core/nav.py`
- Test Suite: `tests/test_nav_resolve.py`
