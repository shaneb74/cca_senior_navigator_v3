# Authentication Integration Guide for Cost Planner v2

## Overview

Real login and signup pages now exist in the application. Cost Planner v2 will use these pages for authentication gates while maintaining the existing mock/dev auth system.

---

## Available Authentication Pages

### Login Page
- **Route Key**: `login`
- **URL**: `?page=login`
- **File**: `pages/login.py`
- **Navigation**: `route_to("login")`

### Signup Page
- **Route Key**: `signup`
- **URL**: `?page=signup`
- **File**: `pages/signup.py`
- **Navigation**: `route_to("signup")`

### Navigation Config
Both pages are registered in `config/nav.json`:
```json
{
  "key": "login",
  "label": "Log in",
  "module": "pages.login:render",
  "hidden": true
},
{
  "key": "signup",
  "label": "Sign up",
  "module": "pages.signup:render",
  "hidden": true
}
```

---

## Integration Pattern for Cost Planner v2

### Module Hub Authentication Gate

**File**: `products/cost_planner_v2/hub.py`

```python
"""Module selection hub for Cost Planner v2."""

import streamlit as st
from core.modules.hub import ModuleHub
from core.nav import route_to
from products.cost_planner_v2.auth import is_authenticated
from products.cost_planner_v2.profile import get_user_profile


def render_module_hub() -> None:
    """Render the Cost Planner module selection dashboard."""
    
    # Authentication gate - route to real login/signup pages
    if not is_authenticated():
        _render_auth_required()
        return
    
    # Rest of hub rendering...
    st.markdown("### 💰 Cost Planner")
    # ... module tiles, etc.


def _render_auth_required() -> None:
    """Show auth requirement with navigation to login/signup."""
    st.warning("🔒 **Sign in Required**")
    st.markdown(
        """
        To access your personalized financial assessment, please sign in or create a free account.
        
        **Benefits of signing in:**
        - Securely save your financial information
        - Resume your assessment anytime
        - Access detailed benefit eligibility tools
        - Receive personalized recommendations
        """
    )
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Hub", use_container_width=True):
            route_to("hub_concierge")
    with col2:
        if st.button("Sign In →", type="primary", use_container_width=True):
            route_to("login")
    
    st.markdown("---")
    st.caption("Don't have an account?")
    if st.button("Create Free Account", use_container_width=True):
        route_to("signup")
```

### Individual Module Authentication

**Pattern for protected modules**:

```python
def _render_sub_module(module_key: str) -> None:
    """Render a specific calculation sub-module."""
    
    # Check authentication before loading module
    if not is_authenticated():
        st.warning("🔒 **Sign in Required**")
        st.markdown(f"The **{module_key.title()}** module requires authentication.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Hub", use_container_width=True):
                st.query_params["cost_module"] = "hub"
                st.rerun()
        with col2:
            if st.button("Sign In →", type="primary", use_container_width=True):
                route_to("login")
        return
    
    # Load and render module...
    config = load_product_module_config("cost_planner_v2", module_key)
    run_module(config)
```

---

## Auth Utility Module

**File**: `products/cost_planner_v2/auth.py`

```python
"""Authentication utilities for Cost Planner v2.

Currently uses mock/dev auth but integrates with real login/signup pages.
"""

import streamlit as st
from core.nav import route_to


def is_authenticated() -> bool:
    """Check if user is authenticated.
    
    Returns:
        True if user is signed in, False otherwise
    """
    # Check mock auth state (dev mode)
    auth_state = st.session_state.get("auth", {})
    return bool(auth_state.get("is_authenticated", False))


def get_user_email() -> str:
    """Get authenticated user's email.
    
    Returns:
        User email or empty string if not authenticated
    """
    auth_state = st.session_state.get("auth", {})
    return auth_state.get("email", "")


def get_user_name() -> str:
    """Get authenticated user's name.
    
    Returns:
        User name or "Guest" if not authenticated
    """
    auth_state = st.session_state.get("auth", {})
    return auth_state.get("name", "Guest")


def require_auth(redirect_to_login: bool = True) -> bool:
    """Require authentication, optionally redirecting to login.
    
    Args:
        redirect_to_login: If True, auto-navigate to login page
    
    Returns:
        True if authenticated, False otherwise
    """
    if is_authenticated():
        return True
    
    if redirect_to_login:
        st.info("Redirecting to sign in...")
        route_to("login")
        return False
    
    return False


def mock_login_button() -> None:
    """Show mock login controls in sidebar (dev mode only).
    
    Displays toggle for testing authenticated vs. unauthenticated states.
    """
    import os
    
    # Only show in dev mode
    if os.getenv("STREAMLIT_ENV") == "production":
        return
    
    with st.sidebar:
        st.markdown("### 🔧 Dev: Mock Auth")
        
        current_auth = is_authenticated()
        
        if current_auth:
            user_email = get_user_email()
            st.success(f"✅ Signed in as: {user_email or 'test@example.com'}")
            
            if st.button("Sign Out (Mock)", use_container_width=True):
                st.session_state["auth"] = {"is_authenticated": False}
                st.rerun()
        else:
            st.warning("❌ Not signed in")
            
            if st.button("Mock Sign In", use_container_width=True):
                st.session_state["auth"] = {
                    "is_authenticated": True,
                    "email": "dev@example.com",
                    "name": "Dev User",
                    "role": "user",
                }
                st.rerun()
            
            # Also show real login button
            if st.button("Go to Real Login Page", use_container_width=True):
                route_to("login")


def check_module_access(module_key: str) -> bool:
    """Check if user has access to a specific module.
    
    Modules requiring authentication will show auth gate if user not signed in.
    
    Args:
        module_key: Module identifier (e.g., "income", "assets")
    
    Returns:
        True if user has access, False if auth gate was shown
    """
    # Define which modules require auth (most do, except quick_estimate)
    PUBLIC_MODULES = ["quick_estimate"]
    
    if module_key in PUBLIC_MODULES:
        return True
    
    if not is_authenticated():
        st.warning("🔒 **Authentication Required**")
        st.markdown(
            f"""
            The **{module_key.replace('_', ' ').title()}** module requires a free account.
            
            Sign in to access your personalized financial assessment.
            """
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", use_container_width=True):
                st.query_params["cost_module"] = "hub"
                st.rerun()
        with col2:
            if st.button("Sign In →", type="primary", use_container_width=True):
                route_to("login")
        
        st.markdown("---")
        if st.button("Create Free Account", use_container_width=True):
            route_to("signup")
        
        return False
    
    return True
```

---

## Testing Authentication Flow

### Manual Testing

1. **Start Unauthenticated**:
   ```
   Navigate to: ?page=cost_v2&cost_module=hub
   Should see: Auth gate with "Sign In" button
   ```

2. **Click Sign In**:
   ```
   Should navigate to: ?page=login
   Should see: Real login page
   ```

3. **Click Create Account**:
   ```
   Should navigate to: ?page=signup
   Should see: Real signup page
   ```

4. **Use Mock Auth (Dev Mode)**:
   ```
   In sidebar: Click "Mock Sign In"
   Navigate to: ?page=cost_v2&cost_module=hub
   Should see: Module dashboard (authenticated)
   ```

### Automated Testing

```python
def test_hub_auth_gate():
    """Test that hub shows auth gate when not authenticated."""
    # Clear auth state
    st.session_state["auth"] = {"is_authenticated": False}
    
    # Render hub
    from products.cost_planner_v2.hub import render_module_hub
    render_module_hub()
    
    # Should show auth warning
    assert "Sign in Required" in rendered_output
    # Should have login button
    assert has_button("Sign In")

def test_hub_authenticated_access():
    """Test that authenticated users see module dashboard."""
    # Set auth state
    st.session_state["auth"] = {
        "is_authenticated": True,
        "email": "test@example.com"
    }
    
    # Render hub
    from products.cost_planner_v2.hub import render_module_hub
    render_module_hub()
    
    # Should show modules
    assert "Cost Planner" in rendered_output
    assert has_module_tiles()
```

---

## Migration Notes

### From v1 Auth Pattern

**v1 Pattern** (inline auth UI):
```python
# v1 would render login form directly in page
st.text_input("Email")
st.text_input("Password")
if st.button("Sign In"):
    # Handle login inline
```

**v2 Pattern** (navigate to auth pages):
```python
# v2 redirects to dedicated auth pages
if not is_authenticated():
    if st.button("Sign In"):
        route_to("login")  # Navigate to real page
```

### Benefits of v2 Approach

1. **Separation of Concerns**: Auth logic lives in dedicated pages
2. **Reusability**: All products can use same login/signup pages
3. **Consistency**: Users see same auth experience everywhere
4. **Maintainability**: Update auth UI once, applies everywhere
5. **Security**: Centralized auth validation and session management

---

## Future Enhancements

### OAuth Integration
When real OAuth is implemented:
- `is_authenticated()` checks actual OAuth token
- `get_user_email()` reads from OAuth user profile
- Login/signup pages handle OAuth flow
- **No changes needed to Cost Planner v2 code** - auth.py abstracts all details

### SSO Support
```python
def is_authenticated() -> bool:
    # Check OAuth token
    if oauth_token := st.session_state.get("oauth_token"):
        return validate_oauth_token(oauth_token)
    
    # Check SSO session
    if sso_session := st.session_state.get("sso_session"):
        return validate_sso_session(sso_session)
    
    # Fall back to mock (dev mode)
    return st.session_state.get("auth", {}).get("is_authenticated", False)
```

---

## Summary

✅ **Login Page**: `?page=login` - Use `route_to("login")`  
✅ **Signup Page**: `?page=signup` - Use `route_to("signup")`  
✅ **Auth Check**: `is_authenticated()` from `auth.py`  
✅ **Dev Mode**: `mock_login_button()` in sidebar  
✅ **Module Gate**: `check_module_access(module_key)`  

**Cost Planner v2 is ready to integrate with real authentication pages!**
