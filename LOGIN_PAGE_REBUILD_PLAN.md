# Login Page Rebuild Plan

**Branch:** `dev`  
**Status:** Planning Phase  
**Goal:** Replace stub login page with production-ready implementation matching app design patterns

---

## Current State Analysis

### What Exists Now

**Location:** `pages/stubs.py` (line 218)

```python
def render_login():
    # intentionally disabled (will be rebuilt as its own page)
    return
```

**Current Issues:**
- ✅ Function exists but does nothing (returns immediately)
- ✅ Links still present in UI (Welcome page, header)
- ✅ Route `?page=login` exists but renders blank
- ✅ No authentication flow
- ✅ No visual design
- ✅ Inconsistent with app design system

### Authentication Architecture (Already in Place)

**Core Auth System:** `core/state.py`
```python
# Toggle-based auth (no real OAuth/passwords)
authenticate_user(name, email)  # Sets auth state
logout_user()                    # Clears auth state
is_authenticated()               # Check auth state
get_user_name()                  # Get user name
```

**User Identity:** `core/session_store.py`
- Anonymous users: `anon_{uuid}` (12-char hex)
- Authenticated users: Custom UID or email-based
- Persistent storage: `data/users/{uid}.json`
- Session storage: `.cache/session_{id}.json`

**Auth State Structure:**
```python
st.session_state.ctx["auth"] = {
    "is_authenticated": False,
    "user_id": None,
    "role": "guest",
    "name": None,
    "email": None,
}
```

---

## Design Pattern Analysis

### App Design System (From Welcome & Professionals Pages)

**Layout Components:**
- `render_header_simple()` - Single-line header with logo + nav
- `render_footer_simple()` - Minimal footer
- Container-based sections with consistent padding
- CSS variable system (`var(--bg)`, `var(--ink)`, `var(--brand-700)`, etc.)

**Typography Patterns:**
```css
/* Hero title - large, bold */
font-size: clamp(3.4rem, 5.4vw, 4.6rem);
font-weight: 700;
line-height: 1.04;
letter-spacing: -0.01em;

/* Subtitle - readable, balanced */
font-size: clamp(1.125rem, 2vw, 1.25rem);
line-height: 1.6;
color: var(--ink-600);
```

**Card/Form Design:**
- `.card` container with padding
- `.card-head` for titles
- `.card-meta` for descriptions
- `.btn` styles (primary, secondary, ghost)
- Input styling with proper spacing

**Color System:**
- Background: `var(--bg)` (neutral light)
- Text: `var(--ink)`, `var(--ink-600)` (grays)
- Brand: `var(--brand-700)` (blue)
- Success: Green tones
- Neutral/AI: Subtle accents

---

## Proposed Solution

### Option A: Simple Toggle Login (Recommended for MVP)

**Design:** Clean, single-card interface matching app aesthetics

**Features:**
- Name + Email inputs (pre-filled for demo)
- Single "Sign In" button
- Toggle authentication without password
- Success message + redirect to hub
- "Continue as Guest" option (skips auth)
- Back to Welcome link

**Visual Layout:**
```
┌─────────────────────────────────────────┐
│  HEADER (logo + nav)                    │
└─────────────────────────────────────────┘

         ┌─────────────────────────┐
         │   Sign In               │
         │                         │
         │   [Name input]          │
         │   [Email input]         │
         │                         │
         │   [Sign In button]      │
         │   [Continue as Guest]   │
         │                         │
         │   ← Back to Welcome     │
         └─────────────────────────┘

┌─────────────────────────────────────────┐
│  FOOTER                                 │
└─────────────────────────────────────────┘
```

**User Flow:**
1. Click "Log In" from header/welcome
2. Land on clean login page
3. Enter name + email (or use pre-filled demo)
4. Click "Sign In" → Authenticate → Redirect to Lobby
5. OR click "Continue as Guest" → Skip auth → Go to Lobby

**Pros:**
- ✅ Matches existing toggle-auth system
- ✅ No backend/OAuth complexity
- ✅ Clean, consistent with app design
- ✅ Quick to implement (1-2 days)
- ✅ Preserves demo/testing workflow

**Cons:**
- ⚠️ Not real authentication (fine for MVP/demo)
- ⚠️ No password/security (acceptable for prototype)

---

### Option B: Full Auth Page (Future Production)

**Design:** Enterprise-grade with OAuth integration

**Features:**
- Email/password login
- OAuth (Google, Microsoft)
- "Forgot Password" flow
- Account creation wizard
- Email verification
- Terms & privacy acceptance
- Professional vs. Member role selection

**Implementation Timeline:** 2-3 weeks

**Dependencies:**
- OAuth provider setup
- Backend auth service
- Database for credentials
- Email service (verification)
- Security audit

**Recommendation:** Defer to post-MVP. Option A sufficient for demo/pilot.

---

## Implementation Plan (Option A - Recommended)

### Phase 1: Create New Login Page with OAuth Mock-up (6-8 hours)

**File:** `pages/login.py` (NEW - dedicated file, not in stubs)

**Structure:**
```python
"""
Login Page - OAuth Mock-up + Simple Toggle Authentication

Features:
- OAuth buttons (Apple, Google, Facebook) - mock UI only
- Email/name fallback (toggle auth, no real passwords)
- Guest mode option
- Clean design matching app aesthetics

For demo/MVP: All auth is toggle-based (no real OAuth/passwords).
Future: Wire OAuth buttons to real providers.
"""

import streamlit as st

from core.nav import route_to
from core.state import authenticate_user, is_authenticated
from core.ui import img_src
from ui.footer_simple import render_footer_simple
from ui.header_simple import render_header_simple


def render(ctx=None):
    """Render login page with OAuth mock-up and simple auth toggle."""
    
    # If already authenticated, redirect to hub
    if is_authenticated():
        route_to(push=False, page="hub_lobby")
        return
    
    # Render header (with "Log In" link active)
    render_header_simple(active_route="login")
    
    # Inject login-specific CSS
    _inject_login_css()
    
    # Render login form
    _render_login_form()
    
    # Render footer
    render_footer_simple()


def _inject_login_css():
    """Inject login page styles matching app design system."""
    st.markdown(
        """
        <style>
        /* Login container */
        .login-section {
            min-height: 70vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: var(--space-8) var(--space-4);
        }
        
        .login-card {
            background: white;
            border-radius: 12px;
            padding: var(--space-8);
            max-width: 440px;
            width: 100%;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }
        
        .login-title {
            font-size: 2rem;
            font-weight: 700;
            color: var(--ink);
            margin-bottom: var(--space-2);
            text-align: center;
        }
        
        .login-subtitle {
            color: var(--ink-600);
            text-align: center;
            margin-bottom: var(--space-6);
            font-size: 0.95rem;
        }
        
        .oauth-buttons {
            display: flex;
            flex-direction: column;
            gap: var(--space-3);
            margin-bottom: var(--space-4);
        }
        
        .oauth-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 12px 20px;
            border: 1px solid var(--ink-200);
            border-radius: 8px;
            background: white;
            color: var(--ink);
            font-weight: 500;
            font-size: 0.95rem;
            text-decoration: none;
            transition: all 0.2s ease;
            cursor: pointer;
        }
        
        .oauth-btn:hover {
            background: var(--bg);
            border-color: var(--ink-300);
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .oauth-btn--apple {
            background: #000;
            color: white;
            border-color: #000;
        }
        
        .oauth-btn--apple:hover {
            background: #1a1a1a;
            border-color: #1a1a1a;
        }
        
        .oauth-btn--google {
            background: white;
            border-color: #dadce0;
        }
        
        .oauth-btn--facebook {
            background: #1877f2;
            color: white;
            border-color: #1877f2;
        }
        
        .oauth-btn--facebook:hover {
            background: #166fe5;
            border-color: #166fe5;
        }
        
        .oauth-icon {
            width: 20px;
            height: 20px;
            object-fit: contain;
        }
        
        .login-divider {
            text-align: center;
            color: var(--ink-400);
            margin: var(--space-5) 0;
            font-size: 0.875rem;
            position: relative;
        }
        
        .login-divider::before,
        .login-divider::after {
            content: "";
            position: absolute;
            top: 50%;
            width: 40%;
            height: 1px;
            background: var(--ink-200);
        }
        
        .login-divider::before {
            left: 0;
        }
        
        .login-divider::after {
            right: 0;
        }
        
        .guest-text {
            text-align: center;
            color: var(--ink-500);
            font-size: 0.875rem;
            margin-top: var(--space-4);
        }
        
        .back-link {
            text-align: center;
            margin-top: var(--space-4);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_login_form():
    """Render login form with OAuth buttons and email fallback."""
    
    # Use columns to center the form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # Title
        st.markdown(
            '<h1 class="login-title">Sign In</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="login-subtitle">Welcome back to Concierge Care Advisors</p>',
            unsafe_allow_html=True,
        )
        
        # OAuth Buttons (Mock UI - no real OAuth for demo)
        st.markdown('<div class="oauth-buttons">', unsafe_allow_html=True)
        
        # Apple Sign In
        if st.button(
            "🍎 Continue with Apple",
            use_container_width=True,
            key="oauth_apple",
        ):
            # Mock OAuth - just toggle auth with default name
            authenticate_user(name="Demo User", email="demo@apple.com")
            st.success("✅ Signed in with Apple!")
            st.rerun()
        
        # Google Sign In
        if st.button(
            "🔵 Continue with Google",
            use_container_width=True,
            key="oauth_google",
        ):
            # Mock OAuth - just toggle auth with default name
            authenticate_user(name="Demo User", email="demo@gmail.com")
            st.success("✅ Signed in with Google!")
            st.rerun()
        
        # Facebook Sign In
        if st.button(
            "📘 Continue with Facebook",
            use_container_width=True,
            key="oauth_facebook",
        ):
            # Mock OAuth - just toggle auth with default name
            authenticate_user(name="Demo User", email="demo@facebook.com")
            st.success("✅ Signed in with Facebook!")
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Divider
        st.markdown(
            '<div class="login-divider">or sign in with email</div>',
            unsafe_allow_html=True,
        )
        
        # Email/Name form (fallback)
        name = st.text_input(
            "Name",
            value="Sarah",
            placeholder="Enter your name",
            key="login_name",
        )
        
        email = st.text_input(
            "Email",
            value="sarah@example.com",
            placeholder="you@example.com",
            key="login_email",
        )
        
        # Sign In button
        if st.button(
            "Sign In with Email",
            type="primary",
            use_container_width=True,
            key="login_submit",
        ):
            if name and email:
                authenticate_user(name=name, email=email)
                st.success(f"✅ Welcome, {name}!")
                st.rerun()
            else:
                st.error("Please enter both name and email.")
        
        # Guest option
        st.markdown(
            '<p class="guest-text">Don\'t want to sign in?</p>',
            unsafe_allow_html=True,
        )
        
        if st.button(
            "Continue as Guest",
            type="secondary",
            use_container_width=True,
            key="login_guest",
        ):
            route_to(push=False, page="hub_lobby")
        
        # Back link
        st.markdown("---")
        st.markdown('<div class="back-link">', unsafe_allow_html=True)
        if st.button("← Back to Welcome", key="login_back", use_container_width=False):
            route_to(push=False, page="welcome")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
```

**Implementation Notes:**

1. **OAuth Mock Behavior:**
   - Buttons look like real OAuth (Apple black, Google white, Facebook blue)
   - Clicking any OAuth button → Instant "sign in" with default demo user
   - No redirect to external provider (pure mock for demo)
   - Uses same `authenticate_user()` toggle as email flow

2. **Visual Hierarchy:**
   - OAuth buttons first (most prominent)
   - Divider: "or sign in with email"
   - Email/name form (fallback)
   - Guest option at bottom
   - Back link last

3. **Real OAuth Future:**
   - Replace button clicks with OAuth redirect flow
   - Add state parameter for CSRF protection
   - Handle callback from provider
   - Exchange auth code for tokens
   - Extract user profile from ID token

**Tasks:**
- [ ] Create `pages/login.py`
- [ ] Implement OAuth mock-up buttons (Apple, Google, Facebook)
- [ ] Add CSS for OAuth button styling
- [ ] Implement email/name fallback form
- [ ] Add redirect logic (if authenticated → hub)
- [ ] Add guest mode option
- [ ] Add back navigation
- [ ] Test all sign-in flows

---

### Phase 2: Remove Stub & Clean Up Old Login Code (1 hour)

**Files to Clean Up:**

1. **`pages/stubs.py`** - Delete stub function:
```python
# DELETE THIS (lines 218-220):
def render_login():
    # intentionally disabled (will be rebuilt as its own page)
    return
```

2. **`assets/images/login.png`** - DELETE (unused image referenced in waiting_room stub)
   - Currently only used in `render_waiting_room()` stub
   - Not needed for new login page design

**Route Handler:** Already exists in `app.py` or routing system

**Verify Routes:**
- `?page=login` → `pages/login.py`
- Header "Log In" link → `?page=login`
- Welcome page login buttons → `?page=login`

**Tasks:**
- [ ] Delete `render_login()` from `stubs.py`
- [ ] Delete `assets/images/login.png` (optional - only if not used elsewhere)
- [ ] Verify route mapping works
- [ ] Test navigation from header
- [ ] Test navigation from welcome page

---

### Phase 3: Update Header Auth Logic (1 hour)

**File:** `ui/header_simple.py`

**Current:** Always shows "Log In" link

**Enhancement:** Toggle between "Log In" and "Log Out" based on auth state

**Code Change (lines 88-92):**
```python
# Before:
login_href = add_uid_to_href("?page=login")
nav_links_html.append(
    f'<a href="{login_href}" class="nav-link nav-link--login" target="_self">Log In</a>'
)

# After:
from core.state import is_authenticated, get_user_name, logout_user

if is_authenticated():
    user_name = get_user_name()
    display_name = user_name if user_name else "User"
    # Show user name + logout button
    nav_links_html.append(
        f'<span class="nav-link nav-user">{display_name}</span>'
    )
    # Note: Logout needs to be a button, not an <a> link
    # Will handle in Streamlit after header render
else:
    login_href = add_uid_to_href("?page=login")
    nav_links_html.append(
        f'<a href="{login_href}" class="nav-link nav-link--login" target="_self">Log In</a>'
    )
```

**Alternative (Simpler):**
Keep login link always visible, add logout in separate flow (user dropdown menu or account page).

**Tasks:**
- [ ] Update header to show auth state
- [ ] Add logout option (button or account menu)
- [ ] Test toggle flow (login → logout → login)

---

### Phase 4: Welcome Page Integration (30 mins)

**File:** `pages/welcome.py`

**Current:** Has "Professional Login" section with login link

**Enhancement:** Update copy and styling to match new login page

**Lines to Review:** 638-710 (login links and professional section)

**Tasks:**
- [ ] Verify login links work with new page
- [ ] Update copy if needed ("Sign In" vs "Log In")
- [ ] Ensure consistent styling
- [ ] Test click-through flow

---

### Phase 5: Testing & Polish (2 hours)

**Test Scenarios:**

1. **Guest Flow:**
   - Start as anonymous user
   - Navigate to login
   - Click "Continue as Guest"
   - Verify redirect to Lobby
   - Verify still anonymous

2. **Sign In Flow:**
   - Navigate to login
   - Enter name + email
   - Click "Sign In"
   - Verify success message
   - Verify redirect to Lobby
   - Verify auth state persisted

3. **Already Authenticated:**
   - Sign in
   - Navigate to `/login` URL
   - Verify auto-redirect to Lobby
   - No double-login

4. **Logout Flow:**
   - Sign in
   - Find logout option (header or account)
   - Click logout
   - Verify auth cleared
   - Verify redirect to Welcome or Login

5. **Navigation:**
   - Header "Log In" link works
   - Welcome page login buttons work
   - Back button returns to Welcome
   - All links preserve UID query param

6. **Visual Consistency:**
   - Login page matches app design
   - Typography consistent
   - Colors match design system
   - Responsive on mobile
   - Proper spacing/padding

**Edge Cases:**
- [ ] Already authenticated → auto-redirect
- [ ] Empty name/email → validation error
- [ ] Session persistence after login
- [ ] UID preservation across navigation
- [ ] Mobile viewport (responsive design)

---

## Design Specifications

### Layout Measurements

**Login Card:**
- Max width: 420px
- Padding: `var(--space-8)` (approx 48px)
- Border radius: 12px
- Box shadow: `0 4px 20px rgba(0,0,0,0.08)`

**Typography:**
- Title: 2rem (32px), weight 700
- Subtitle: 1rem (16px), weight 400, color `var(--ink-600)`
- Input labels: 0.875rem (14px), weight 600

**Spacing:**
- Section padding: `var(--space-8)` top/bottom
- Input spacing: `var(--space-3)` (12px) between fields
- Button spacing: `var(--space-4)` (16px) below inputs

**Colors:**
- Background: `var(--bg)` (light neutral)
- Card: `white`
- Text: `var(--ink)` (dark gray)
- Subtitle: `var(--ink-600)` (medium gray)
- Primary button: `var(--brand-700)` (blue)
- Secondary button: Ghost style (transparent + border)

### Accessibility

**Requirements:**
- [ ] Proper heading hierarchy (h1 for title)
- [ ] Label association for inputs
- [ ] Focus states for interactive elements
- [ ] Keyboard navigation support
- [ ] ARIA labels where needed
- [ ] Color contrast ratios meet WCAG AA

**Implementation:**
- Use Streamlit's built-in accessibility
- Add `aria-label` to custom elements
- Ensure tab order is logical
- Test with keyboard-only navigation

---

## File Structure (After Implementation)

```
pages/
├── login.py           # NEW - Dedicated login page
├── stubs.py           # MODIFIED - Remove render_login()
├── welcome.py         # MODIFIED - Update login links (minimal)
└── professionals.py   # No changes

ui/
├── header_simple.py   # MODIFIED - Auth-aware navigation
└── footer_simple.py   # No changes

core/
├── state.py           # No changes (auth already exists)
└── session_store.py   # No changes (persistence ready)
```

---

## Implementation Timeline

| Phase | Task | Time | Dependencies |
|-------|------|------|--------------|
| **1** | Create `pages/login.py` | 4-6h | Design specs, CSS system |
| **2** | Remove stub, verify routes | 1h | Phase 1 complete |
| **3** | Update header auth logic | 1h | Phase 1 complete |
| **4** | Welcome page integration | 30m | Phase 1 complete |
| **5** | Testing & polish | 2h | All phases complete |
| **Total** | | **8.5-10.5 hours** | ~1-2 days |

---

## Success Criteria

### Functional Requirements
- ✅ Login page renders correctly
- ✅ Auth toggle works (sign in/out)
- ✅ Guest mode works (skip auth)
- ✅ Redirect to Lobby after login
- ✅ Auto-redirect if already authenticated
- ✅ Session persistence across page loads
- ✅ UID preservation in URLs

### Visual Requirements
- ✅ Matches app design system
- ✅ Typography consistent with Welcome/Professionals
- ✅ Responsive on mobile/tablet/desktop
- ✅ Proper spacing and alignment
- ✅ Clean, uncluttered layout

### UX Requirements
- ✅ Clear call-to-action (Sign In button)
- ✅ Guest option visible and accessible
- ✅ Back navigation works
- ✅ Success feedback after login
- ✅ Error handling for invalid inputs
- ✅ Smooth page transitions

---

## Future Enhancements (Post-MVP)

### Phase 2: Real Authentication
- OAuth integration (Google, Microsoft)
- Email/password with bcrypt hashing
- JWT token management
- Refresh token flow
- "Remember me" functionality

### Phase 3: Account Features
- Password reset flow
- Email verification
- Account settings page
- Profile management
- Role-based access control

### Phase 4: Professional Portal
- Separate professional login
- Organization-level accounts
- Multi-user management
- Admin dashboard
- Audit logging

### Phase 5: Security Hardening
- Rate limiting
- CAPTCHA for bot protection
- 2FA/MFA support
- Session timeout
- Device fingerprinting

---

## Questions for Review

1. **Auth Flow:** Should guests be allowed to skip login entirely, or require sign-in for certain features?
2. **Redirect Behavior:** After login, go to Lobby or return to previous page?
3. **Header Design:** Show user name in header, or just "Log Out" link?
4. **Professional Mode:** Should professionals use same login page or separate flow?
5. **Session Timeout:** Should sessions expire after inactivity? If so, how long?

---

## Recommendation

**Proceed with Option A (Simple Toggle Login)**

**Rationale:**
- ✅ Matches current auth architecture (no backend changes needed)
- ✅ Clean, professional design consistent with app
- ✅ Quick implementation (1-2 days)
- ✅ Sufficient for MVP/demo/pilot
- ✅ Easy to replace with real auth later

**Next Steps:**
1. Review this plan
2. Approve design specs
3. Create feature branch: `feature/login-page-rebuild`
4. Implement Phase 1 (core login page)
5. Test and iterate
6. Merge to dev

**Estimated Delivery:** 1-2 days after approval

---

## Notes

- All code uses existing auth system (`core/state.py`)
- No database or backend changes required
- Preserves demo/testing workflow
- Compatible with existing UID persistence
- Easy to extend with real auth later
- Maintains clean separation of concerns
