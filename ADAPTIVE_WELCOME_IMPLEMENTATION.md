# Adaptive Welcome Page Implementation

**Date:** October 14, 2025  
**Status:** ✅ Complete  
**Branch:** feature/cost_planner_v2

## Overview

Implemented adaptive welcome page behavior that dynamically adjusts hero buttons and navigation based on user authentication state and planning context. This creates a personalized experience that guides users to the right place based on their journey progress.

## Problem Statement

The welcome page previously showed the same static buttons to all users:
- **Start Now** → Always routed to contextual welcome
- **Log In** → Always visible

This didn't account for:
1. Authenticated users who should see "Continue where you left off"
2. Users who already provided planning context (shouldn't see contextual welcome again)
3. Integration with Navi's intelligent routing recommendations

## Solution Architecture

### Three Welcome States

| Auth State | Planning Context | Primary Button | Secondary Button | Navigation Behavior |
|-----------|------------------|----------------|------------------|---------------------|
| Not logged in | N/A | "Start Now" | "Log In" | → contextual welcome |
| Logged in | No context | "Start Planning" | None | → contextual welcome |
| Logged in | Has context | "Continue where you left off" | None | → Navi's recommended route |

### Planning Context Detection

The system checks two session state keys:
```python
has_planning_context = (
    st.session_state.get("planning_for_name")  # New canonical key
    or st.session_state.get("person_name")     # Legacy fallback
)
```

### Navi Integration

For authenticated users with planning context:
```python
next_action = MCIP.get_recommended_next_action()
primary_route = next_action.get("route", "hub_concierge")
```

MCIP determines the next route based on journey progress:
- **Getting Started**: No products completed → `gcp_v4`
- **In Progress**: GCP done → `cost_v2`
- **Nearly There**: GCP + Cost Planner done → `pfma_v2`
- **Complete**: All done → `hub_concierge`

## Implementation Details

### 1. Updated `pages/welcome.py`

#### Added MCIP Import
```python
from core.mcip import MCIP
from core.state import is_authenticated
```

#### Dynamic Button Generation
Modified `_welcome_body()` to accept parameters:
```python
def _welcome_body(
    primary_label: str = "Start Now",
    primary_route: str = "someone_else",
    show_secondary: bool = True,
) -> str:
```

Generates CTA HTML dynamically:
```python
cta_html = f'<a href="?page={primary_route}" class="btn btn--primary wl-btn">{html.escape(primary_label)}</a>'
if show_secondary:
    cta_html += '\n<a href="?page=login" class="btn btn--secondary">Log in</a>'
```

#### Adaptive Render Logic
Updated `render()` function:
```python
def render(ctx: Optional[dict] = None) -> None:
    authenticated = is_authenticated()
    has_planning_context = (
        st.session_state.get("planning_for_name") 
        or st.session_state.get("person_name")
    )
    
    if not authenticated:
        primary_label = "Start Now"
        primary_route = "someone_else"
        show_secondary = True
    elif authenticated and not has_planning_context:
        primary_label = "Start Planning"
        primary_route = "someone_else"
        show_secondary = False
    else:
        next_action = MCIP.get_recommended_next_action()
        primary_label = "Continue where you left off"
        primary_route = next_action.get("route", "hub_concierge")
        show_secondary = False
    
    render_page(
        body_html=_welcome_body(
            primary_label=primary_label,
            primary_route=primary_route,
            show_secondary=show_secondary,
        ),
        active_route="welcome"
    )
```

#### Enhanced Planning Context Storage
Updated form submission handler in `render_welcome_card()`:
```python
if submitted:
    # Store relationship context
    if safe_active == "someone":
        st.session_state["planning_for_relationship"] = "someone_else"
    elif safe_active == "self":
        st.session_state["planning_for_relationship"] = "self"
    
    # Store name if provided
    if name_value and name_value.strip():
        st.session_state["planning_for_name"] = name_value.strip()
        st.session_state["person_name"] = name_value.strip()  # Legacy compatibility
```

### 2. Updated `pages/someone_else.py`

Added context check to skip contextual welcome for authenticated users:
```python
def _page_content(ctx=None):
    if is_authenticated():
        has_context = (
            st.session_state.get("planning_for_name")
            or st.session_state.get("person_name")
        )
        if has_context:
            # Skip contextual welcome - go directly to Navi's recommended route
            next_action = MCIP.get_recommended_next_action()
            route_to(next_action.get("route", "hub_concierge"))
            return
    
    render_welcome_card(...)
```

### 3. Updated `pages/self.py`

Identical context check logic as `someone_else.py`:
```python
def _page_content(ctx=None):
    if is_authenticated():
        has_context = (...)
        if has_context:
            next_action = MCIP.get_recommended_next_action()
            route_to(next_action.get("route", "hub_concierge"))
            return
    
    render_welcome_card(...)
```

## Session State Keys

### New Canonical Keys
- `planning_for_name`: Name of care recipient (preferred)
- `planning_for_relationship`: "someone_else" or "self"

### Legacy Keys (Maintained for Compatibility)
- `person_name`: Name of care recipient (fallback)

## User Experience Flow

### First-Time Visitor (Unauthenticated)
1. Land on welcome page
2. See "Start Now" + "Log In" buttons
3. Click "Start Now"
4. Route to contextual welcome (someone_else or self)
5. Enter name and relationship
6. Continue to Concierge Hub

### Returning User (Authenticated, No Context)
1. Land on welcome page
2. See "Start Planning" button (no Log In)
3. Click "Start Planning"
4. Route to contextual welcome
5. Enter name and relationship
6. Continue to recommended product

### Returning User (Authenticated, Has Context)
1. Land on welcome page
2. See "Continue where you left off" button
3. Click button
4. **Skip contextual welcome entirely**
5. Route directly to Navi's recommendation:
   - GCP not done → `gcp_v4`
   - GCP done → `cost_v2`
   - GCP + Cost done → `pfma_v2`
   - All done → `hub_concierge`

### Edge Case: Authenticated User Manually Navigates to Contextual Welcome
1. User clicks "For someone" card on welcome page
2. System detects authentication + context
3. **Automatically redirects** to Navi's recommendation
4. **Prevents seeing contextual welcome again**

## Benefits

### 1. Personalization
- Buttons adapt to user's authentication state
- Language changes based on journey progress
- No redundant information collection

### 2. Intelligent Routing
- Leverages MCIP's recommendation engine
- Guides users to next-best action
- Maintains journey momentum

### 3. Context Preservation
- Planning context stored once, used everywhere
- Eliminates re-asking for same information
- Smooth experience across sessions

### 4. Clean UI
- Login button hidden when not needed
- Single, focused CTA for authenticated users
- No visual clutter

## Testing Scenarios

### Scenario 1: Unauthenticated User
1. Open app → see "Start Now" + "Log In"
2. Click "Start Now"
3. Enter name on contextual welcome
4. Verify routes to hub_concierge
5. Verify `planning_for_name` and `planning_for_relationship` set

### Scenario 2: Authenticated User, No Context
1. Log in via login page
2. Return to welcome
3. See "Start Planning" (no Log In button)
4. Click "Start Planning"
5. Enter name on contextual welcome
6. Verify routes to recommended product

### Scenario 3: Authenticated User, Has Context
1. Log in (already has planning context from previous session)
2. Return to welcome
3. See "Continue where you left off"
4. Click button
5. **Verify skips contextual welcome**
6. Verify routes to MCIP recommended route (gcp_v4, cost_v2, pfma_v2, or hub_concierge)

### Scenario 4: Manual Navigation to Contextual Welcome
1. Log in with planning context
2. Manually click "For someone" card on welcome page
3. Verify automatic redirect to recommended route
4. Verify contextual welcome form never displays

### Scenario 5: Journey Progress Routing
1. Complete GCP
2. Log out and log back in
3. Click "Continue where you left off"
4. Verify routes to `cost_v2` (Cost Planner)
5. Complete Cost Planner
6. Return to welcome
7. Click "Continue where you left off"
8. Verify routes to `pfma_v2` (PFMA)

## Files Modified

```
pages/welcome.py
├── Added MCIP import
├── Enhanced _welcome_body() with parameters
├── Added adaptive render() logic
└── Updated planning context storage

pages/someone_else.py
├── Added authentication check
├── Added context detection
└── Added automatic routing for existing context

pages/self.py
├── Added authentication check
├── Added context detection
└── Added automatic routing for existing context
```

## Acceptance Criteria

✅ **AC1**: Hero buttons dynamically change based on authentication and planning context  
✅ **AC2**: Authenticated users skip contextual welcome if planning context is known  
✅ **AC3**: Authenticated users with context route directly to Navi's recommended hub  
✅ **AC4**: Unauthenticated users still see Start Now + Log In flow  
✅ **AC5**: Button visibility and labels transition smoothly (no flicker)  

## Dependencies

- `core/mcip.py` - MCIP.get_recommended_next_action()
- `core/state.py` - is_authenticated()
- `core/nav.py` - route_to()

## Future Enhancements

1. **Profile Module Integration**: Sync planning context to user profile for cross-device persistence
2. **Context Editing**: Allow users to change planning context without losing progress
3. **Multiple Care Recipients**: Support planning for multiple people simultaneously
4. **Onboarding Skip Logic**: Skip entire onboarding flow for returning power users
5. **Analytics Integration**: Track button click rates by state for optimization

## Notes

- Planning context is stored in session state (not persisted to database yet)
- Authentication system is currently in development mode (simulated auth)
- Legacy `person_name` key maintained for backward compatibility
- All routing uses canonical route keys from `nav.json`

## Related Documentation

- COST_PLANNER_V2_AUTH_INTEGRATION.md - Authentication system
- GCP_INTEGRATION_FINAL_FIX.md - MCIP integration patterns
- NAVI_GUIDANCE_INTEGRATION.md - Navi's recommendation system

---

**Implementation Complete:** All acceptance criteria met. Ready for testing and deployment.
