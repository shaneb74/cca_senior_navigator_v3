# PFMA v2 Architecture Vision

> **Status**: Design Phase - To be implemented AFTER Cost Planner v2 is complete  
> **Priority**: Medium - Refactor for maintainability and consistency  
> **Scope**: Rearchitect PFMA around declarative step-driven engine

---

## Executive Summary

Plan for My Advisor (PFMA) currently uses imperative, step-branching code that makes it difficult to maintain, test, and iterate. This vision document outlines a refactor to align PFMA with the module engine architecture used by GCP and Cost Planner v2, while preserving its unique duck-gamification and appointment scheduling features.

**Key Goals:**
1. **Declarative step definitions** - Schema-driven instead of branching code
2. **Standardized state management** - Dedicated state slices with clean interface
3. **Reusable layout components** - Shared UI patterns (breadcrumbs, navigation, gamification)
4. **Step-level guards** - Clean requirement checking (Cost Planner gate, eligibility)
5. **Content/code separation** - Copy and assets in config, not hardcoded

---

## Current Architecture Analysis

### What PFMA Does Well

✅ **Clear funnel flow**: Intro → Appointment → Verifications → Completion  
✅ **Duck gamification**: Engaging progress visualization  
✅ **Appointment scheduling**: Calendar integration and contact collection  
✅ **Multi-step verifications**: Identity, insurance, veteran status checks  
✅ **Cost Planner gate**: Smart dependency on prerequisite product

### Current Pain Points

❌ **Imperative step branching**: Each step has custom rendering logic  
❌ **Direct state mutation**: `st.session_state["pfma"][key] = value` scattered throughout  
❌ **Duplicated navigation**: Back buttons, continue buttons re-implemented per step  
❌ **Inline requirement checks**: Cost Planner gate logic mixed with rendering  
❌ **Hardcoded copy**: Headlines, bullets, and messages embedded in code  
❌ **Inconsistent styling**: Custom CSS per step instead of shared layout  

### Example of Current Pattern

```python
# Current: Imperative branching per step
def render():
    step = st.session_state.get("pfma_step", "intro")
    
    if step == "intro":
        st.markdown("## Welcome to PFMA")
        st.markdown("Let's schedule your appointment...")
        if st.button("Get Started"):
            st.session_state["pfma_step"] = "appointment"
            st.rerun()
    
    elif step == "appointment":
        st.markdown("## Schedule Your Appointment")
        date = st.date_input("Preferred date")
        time = st.time_input("Preferred time")
        if st.button("Continue"):
            st.session_state["pfma"]["appointment_date"] = date
            st.session_state["pfma"]["appointment_time"] = time
            st.session_state["pfma_step"] = "contact_info"
            st.rerun()
    
    # ... more elif branches for each step
```

**Problems:**
- Each step duplicates button logic
- State mutations scattered across functions
- Adding/reordering steps requires editing multiple branches
- No standardized progress tracking
- Copy changes require code edits

---

## Proposed Architecture: Declarative Step Engine

### Overview

Align PFMA with Cost Planner v2 and GCP's module engine architecture while preserving its unique funnel characteristics:

```
PFMA v2 Architecture
├── Schema Definition (JSON/Python)
│   ├── Step metadata (title, subtitle, icon, duck tier)
│   ├── Fields (questions, validation rules)
│   ├── Guards (prerequisite checks)
│   └── Content (copy, illustrations, CTA text)
│
├── State Management
│   ├── pfma.appointment (date, time, type)
│   ├── pfma.contact (name, email, phone)
│   ├── pfma.verifications (identity, insurance, veteran)
│   └── pfma.progress (step, completion, duck count)
│
├── Layout Components
│   ├── Step shell (breadcrumbs, duck display, navigation)
│   ├── Form renderer (consumes field schema)
│   └── Gamification overlay (duck animations, progress)
│
└── Step Guards
    ├── Cost Planner gate (check prerequisite)
    ├── Eligibility check (verify qualifying criteria)
    └── Completion check (ensure required data)
```

---

## 1. Declarative Step Schema

### Schema Format: `pfma_steps.json`

```json
{
  "product": "pfma",
  "version": "v2.0",
  "flow_type": "funnel",
  "steps": [
    {
      "id": "intro",
      "type": "info",
      "title": "Meet Your Personal Care Advisor",
      "subtitle": "Get expert guidance tailored to your needs",
      "duck_tier": 0,
      "content": {
        "headline": "Schedule a Free Consultation",
        "body": [
          "Connect with a licensed care advisor who specializes in senior care planning",
          "Get personalized recommendations based on your Guided Care Plan",
          "No pressure, no sales—just expert advice"
        ],
        "illustration": "advisor_welcome.svg",
        "cta_primary": "Schedule My Appointment",
        "cta_secondary": "Learn More"
      },
      "guards": {
        "require_gcp_complete": true,
        "redirect_if_failed": "gcp"
      }
    },
    {
      "id": "appointment",
      "type": "form",
      "title": "Choose Your Appointment Time",
      "subtitle": "Select a convenient time for your consultation",
      "duck_tier": 1,
      "fields": [
        {
          "id": "appointment_date",
          "type": "date",
          "label": "Preferred Date",
          "required": true,
          "min_days_from_today": 1,
          "max_days_from_today": 90,
          "help": "Appointments available Monday-Friday, 9am-5pm PT"
        },
        {
          "id": "appointment_time",
          "type": "time",
          "label": "Preferred Time",
          "required": true,
          "options": ["9:00 AM", "10:00 AM", "11:00 AM", "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM"],
          "help": "30-minute consultation"
        },
        {
          "id": "appointment_type",
          "type": "radio",
          "label": "Preferred consultation method",
          "required": true,
          "options": [
            {"label": "Phone call", "value": "phone"},
            {"label": "Video call (Zoom)", "value": "video"},
            {"label": "In-person (if available)", "value": "in_person"}
          ],
          "default": "phone"
        }
      ],
      "content": {
        "success_message": "Great choice! Let's get your contact information.",
        "availability_note": "If your preferred time isn't available, we'll contact you with alternatives."
      }
    },
    {
      "id": "contact_info",
      "type": "form",
      "title": "Your Contact Information",
      "subtitle": "How should we reach you?",
      "duck_tier": 2,
      "fields": [
        {
          "id": "contact_name",
          "type": "text",
          "label": "Full Name",
          "required": true,
          "validation": "^[A-Za-z\\s]{2,}$"
        },
        {
          "id": "contact_email",
          "type": "email",
          "label": "Email Address",
          "required": true,
          "help": "We'll send a calendar invite and Zoom link if applicable"
        },
        {
          "id": "contact_phone",
          "type": "phone",
          "label": "Phone Number",
          "required": true,
          "help": "For appointment reminders and video call backup"
        },
        {
          "id": "contact_timezone",
          "type": "select",
          "label": "Your Timezone",
          "required": true,
          "options": ["Pacific", "Mountain", "Central", "Eastern"],
          "default": "Pacific"
        }
      ]
    },
    {
      "id": "verifications",
      "type": "checklist",
      "title": "Quick Verifications",
      "subtitle": "Help us prepare for your consultation",
      "duck_tier": 3,
      "fields": [
        {
          "id": "verify_identity",
          "type": "checkbox",
          "label": "I am the primary decision-maker or authorized representative",
          "required": true
        },
        {
          "id": "verify_insurance",
          "type": "checkbox",
          "label": "I have access to insurance and benefit information",
          "required": false,
          "help": "Not required, but helps us provide more accurate guidance"
        },
        {
          "id": "verify_veteran",
          "type": "checkbox",
          "label": "The care recipient is a veteran or military family member",
          "required": false,
          "effects": [
            {
              "when_checked": true,
              "set_flag": "discuss_va_benefits"
            }
          ]
        }
      ],
      "content": {
        "info_note": "These verifications help us tailor the consultation to your specific situation."
      }
    },
    {
      "id": "completion",
      "type": "results",
      "title": "You're All Set! 🎉",
      "subtitle": "Your appointment is confirmed",
      "duck_tier": 4,
      "content": {
        "headline": "Appointment Confirmed",
        "body": [
          "Check your email for calendar invite and confirmation",
          "You'll receive a reminder 24 hours before your appointment",
          "If you need to reschedule, use the link in your confirmation email"
        ],
        "next_steps": [
          {
            "icon": "📧",
            "title": "Check Your Email",
            "description": "Calendar invite sent to {{contact_email}}"
          },
          {
            "icon": "📋",
            "title": "Prepare Questions",
            "description": "Think about specific concerns you'd like to discuss"
          },
          {
            "icon": "💰",
            "title": "Review Cost Estimate",
            "description": "Bring any questions about your financial plan"
          }
        ],
        "cta_primary": "Return to Hub",
        "cta_secondary": "View My Care Plan"
      }
    }
  ],
  "gamification": {
    "duck_tiers": [
      {
        "tier": 0,
        "ducks": 0,
        "label": "Getting Started",
        "color": "#94a3b8"
      },
      {
        "tier": 1,
        "ducks": 1,
        "label": "Appointment Scheduled",
        "color": "#3b82f6"
      },
      {
        "tier": 2,
        "ducks": 2,
        "label": "Contact Provided",
        "color": "#8b5cf6"
      },
      {
        "tier": 3,
        "ducks": 3,
        "label": "Verifications Complete",
        "color": "#10b981"
      },
      {
        "tier": 4,
        "ducks": 5,
        "label": "Ready to Meet!",
        "color": "#f59e0b"
      }
    ],
    "milestone_messages": {
      "tier_1": "🦆 You've earned your first duck! Keep going!",
      "tier_2": "🦆🦆 Two ducks! You're making great progress!",
      "tier_3": "🦆🦆🦆 Three ducks! Almost there!",
      "tier_4": "🦆🦆🦆🦆🦆 Five ducks! You're all set for your consultation!"
    }
  }
}
```

---

## 2. State Management: Clean Interface

### State Structure

```python
# Organized state slices
st.session_state["pfma"] = {
    "appointment": {
        "date": "2025-10-20",
        "time": "10:00 AM",
        "type": "phone",
        "confirmed": True,
        "confirmation_id": "PFMA-2025-12345"
    },
    "contact": {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "(555) 123-4567",
        "timezone": "Pacific"
    },
    "verifications": {
        "identity": True,
        "insurance": True,
        "veteran": False
    },
    "progress": {
        "current_step": "completion",
        "step_index": 4,
        "completed_steps": ["intro", "appointment", "contact_info", "verifications"],
        "duck_tier": 4,
        "status": "completed"
    },
    "flags": {
        "discuss_va_benefits": False,
        "has_cost_plan": True
    }
}
```

### State Management Helper

```python
# products/pfma_v2/state.py

from typing import Any, Dict, Optional
import streamlit as st


class PFMAState:
    """Clean interface for PFMA state management."""
    
    STATE_KEY = "pfma"
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize PFMA state structure if not exists."""
        if cls.STATE_KEY not in st.session_state:
            st.session_state[cls.STATE_KEY] = {
                "appointment": {},
                "contact": {},
                "verifications": {},
                "progress": {
                    "current_step": "intro",
                    "step_index": 0,
                    "completed_steps": [],
                    "duck_tier": 0,
                    "status": "new"
                },
                "flags": {}
            }
    
    @classmethod
    def save_step(cls, step_id: str, payload: Dict[str, Any]) -> None:
        """Save step data to appropriate state slice.
        
        Args:
            step_id: Step identifier (e.g., "appointment", "contact_info")
            payload: Data to save (e.g., {"date": "2025-10-20", "time": "10:00 AM"})
        """
        cls.initialize()
        
        # Route payload to correct state slice
        if step_id in ["appointment"]:
            st.session_state[cls.STATE_KEY]["appointment"].update(payload)
        elif step_id in ["contact_info"]:
            st.session_state[cls.STATE_KEY]["contact"].update(payload)
        elif step_id in ["verifications"]:
            st.session_state[cls.STATE_KEY]["verifications"].update(payload)
        else:
            # Generic storage for other steps
            st.session_state[cls.STATE_KEY][step_id] = payload
    
    @classmethod
    def get_step_data(cls, step_id: str) -> Dict[str, Any]:
        """Get data for a specific step.
        
        Args:
            step_id: Step identifier
        
        Returns:
            Dict with step data or empty dict if not found
        """
        cls.initialize()
        
        if step_id == "appointment":
            return st.session_state[cls.STATE_KEY]["appointment"]
        elif step_id == "contact_info":
            return st.session_state[cls.STATE_KEY]["contact"]
        elif step_id == "verifications":
            return st.session_state[cls.STATE_KEY]["verifications"]
        else:
            return st.session_state[cls.STATE_KEY].get(step_id, {})
    
    @classmethod
    def advance_step(cls, next_step_id: str, step_index: int) -> None:
        """Advance to next step and update progress.
        
        Args:
            next_step_id: ID of next step
            step_index: Index of next step
        """
        cls.initialize()
        progress = st.session_state[cls.STATE_KEY]["progress"]
        
        # Mark current step as completed
        current_step = progress["current_step"]
        if current_step not in progress["completed_steps"]:
            progress["completed_steps"].append(current_step)
        
        # Advance
        progress["current_step"] = next_step_id
        progress["step_index"] = step_index
        
        # Update status
        if step_index > 0 and progress["status"] == "new":
            progress["status"] = "in_progress"
    
    @classmethod
    def set_duck_tier(cls, tier: int) -> None:
        """Update duck gamification tier.
        
        Args:
            tier: Duck tier level (0-4)
        """
        cls.initialize()
        st.session_state[cls.STATE_KEY]["progress"]["duck_tier"] = tier
    
    @classmethod
    def set_flag(cls, flag_key: str, value: bool) -> None:
        """Set a boolean flag.
        
        Args:
            flag_key: Flag identifier
            value: Boolean value
        """
        cls.initialize()
        st.session_state[cls.STATE_KEY]["flags"][flag_key] = value
    
    @classmethod
    def mark_complete(cls) -> None:
        """Mark PFMA as completed."""
        cls.initialize()
        st.session_state[cls.STATE_KEY]["progress"]["status"] = "completed"
    
    @classmethod
    def get_progress(cls) -> Dict[str, Any]:
        """Get progress information.
        
        Returns:
            Dict with progress data
        """
        cls.initialize()
        return st.session_state[cls.STATE_KEY]["progress"]
```

**Benefits:**
- ✅ Single interface for all state operations
- ✅ No direct `st.session_state` manipulation in step code
- ✅ Easier to test (can mock PFMAState)
- ✅ Consistent state structure
- ✅ Built-in validation and routing

---

## 3. Layout Components: Reusable UI

### Step Shell Component

```python
# products/pfma_v2/components/step_shell.py

from typing import Callable, Optional
import streamlit as st
from products.pfma_v2.state import PFMAState


def render_step_shell(
    step: dict,
    total_steps: int,
    form_content: Callable[[], None],
    show_back: bool = True,
    show_ducks: bool = True
) -> None:
    """Render standardized step layout with breadcrumbs, ducks, and navigation.
    
    Args:
        step: Step schema dict
        total_steps: Total number of steps in flow
        form_content: Function to render step-specific form/content
        show_back: Whether to show back button
        show_ducks: Whether to show duck gamification
    """
    progress = PFMAState.get_progress()
    step_index = progress["step_index"]
    duck_tier = progress["duck_tier"]
    
    # Render breadcrumbs
    _render_breadcrumbs(step_index, total_steps)
    
    # Render duck display
    if show_ducks:
        _render_duck_display(duck_tier, step.get("duck_tier", 0))
    
    # Render step header
    st.markdown(f"### {step['title']}")
    if step.get("subtitle"):
        st.caption(step["subtitle"])
    
    st.markdown("---")
    
    # Render step-specific content
    form_content()
    
    st.markdown("---")
    
    # Render navigation buttons
    _render_navigation(step, show_back)


def _render_breadcrumbs(current: int, total: int) -> None:
    """Render step progress breadcrumbs."""
    segments = []
    for i in range(total):
        if i < current:
            segments.append("✓")  # Completed
        elif i == current:
            segments.append("●")  # Current
        else:
            segments.append("○")  # Upcoming
    
    breadcrumb_html = " ".join(segments)
    st.markdown(
        f'<div style="text-align:center;font-size:1.5rem;color:#3b82f6;">{breadcrumb_html}</div>',
        unsafe_allow_html=True
    )


def _render_duck_display(current_tier: int, step_tier: int) -> None:
    """Render duck gamification display."""
    ducks = "🦆" * current_tier
    target_ducks = "🦆" * step_tier
    
    if step_tier > current_tier:
        st.info(f"Complete this step to earn: {target_ducks}")
    else:
        st.success(f"Your ducks: {ducks}")


def _render_navigation(step: dict, show_back: bool) -> None:
    """Render navigation buttons."""
    from core.nav import route_to
    
    col1, col2 = st.columns(2)
    
    with col1:
        if show_back:
            if st.button("← Back", use_container_width=True):
                # Navigate to previous step (handled by engine)
                st.session_state["_pfma_action"] = "back"
                st.rerun()
    
    with col2:
        cta_label = step.get("content", {}).get("cta_primary", "Continue")
        if st.button(cta_label, type="primary", use_container_width=True):
            # Trigger form validation and advance (handled by engine)
            st.session_state["_pfma_action"] = "next"
            st.rerun()
```

---

## 4. Step Guards: Prerequisite Checks

### Guard System

```python
# products/pfma_v2/guards.py

from typing import Callable, Dict, Optional
import streamlit as st
from core.nav import route_to


class StepGuard:
    """Guard for checking step prerequisites."""
    
    def __init__(self, guard_config: Dict):
        """Initialize guard with configuration.
        
        Args:
            guard_config: Guard configuration from step schema
        """
        self.config = guard_config
    
    def check(self) -> bool:
        """Check if guard passes.
        
        Returns:
            True if prerequisites met, False otherwise (and handles redirect)
        """
        # Check Cost Planner completion
        if self.config.get("require_cost_planner_complete"):
            cost_state = st.session_state.get("cost_planner", {})
            if cost_state.get("progress", 0) < 100:
                self._show_gate(
                    title="Cost Planner Required",
                    message="Please complete the Cost Planner before scheduling your advisor consultation.",
                    redirect_route="cost",
                    redirect_label="Go to Cost Planner"
                )
                return False
        
        # Check GCP completion
        if self.config.get("require_gcp_complete"):
            gcp_state = st.session_state.get("gcp", {})
            if gcp_state.get("progress", 0) < 100:
                redirect = self.config.get("redirect_if_failed", "gcp")
                self._show_gate(
                    title="Guided Care Plan Required",
                    message="Please complete your Guided Care Plan first to get personalized recommendations.",
                    redirect_route=redirect,
                    redirect_label="Go to Guided Care Plan"
                )
                return False
        
        # Check authentication
        if self.config.get("require_auth"):
            auth_state = st.session_state.get("auth", {})
            if not auth_state.get("is_authenticated"):
                self._show_gate(
                    title="Sign In Required",
                    message="Please sign in to schedule your advisor consultation.",
                    redirect_route="login",
                    redirect_label="Sign In"
                )
                return False
        
        # All guards passed
        return True
    
    def _show_gate(
        self,
        title: str,
        message: str,
        redirect_route: str,
        redirect_label: str
    ) -> None:
        """Show gate UI and provide navigation."""
        st.warning(f"⚠️ **{title}**")
        st.markdown(message)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Hub", use_container_width=True):
                route_to("hub_concierge")
        with col2:
            if st.button(redirect_label, type="primary", use_container_width=True):
                route_to(redirect_route)
```

---

## 5. Content/Code Separation

### Content Config

```python
# products/pfma_v2/content.py

"""
Content configuration for PFMA.

All copy, headlines, and asset references in one place.
Designers can update messaging without touching code.
"""

CONTENT = {
    "intro": {
        "headline": "Meet Your Personal Care Advisor",
        "subheadline": "Get expert guidance tailored to your unique situation",
        "benefits": [
            "Connect with a licensed care advisor who specializes in senior care planning",
            "Get personalized recommendations based on your Guided Care Plan",
            "No pressure, no sales—just expert advice to help you make informed decisions"
        ],
        "illustration": "advisor_welcome.svg",
        "cta_primary": "Schedule My Free Consultation",
        "cta_secondary": "Learn More About Our Advisors"
    },
    "appointment": {
        "headline": "Choose Your Appointment Time",
        "availability_note": "Consultations available Monday-Friday, 9am-5pm Pacific Time",
        "duration_note": "Each consultation lasts approximately 30 minutes",
        "success_message": "Great! Now let's get your contact information so we can confirm your appointment."
    },
    "completion": {
        "headline": "You're All Set! 🎉",
        "confirmation_message": "Your appointment is confirmed. Check your email for details.",
        "next_steps": [
            {
                "icon": "📧",
                "title": "Check Your Email",
                "description": "We've sent a calendar invite to your email address"
            },
            {
                "icon": "📋",
                "title": "Prepare Your Questions",
                "description": "Think about specific concerns you'd like to discuss with your advisor"
            },
            {
                "icon": "💰",
                "title": "Review Your Cost Plan",
                "description": "Your advisor will reference your personalized cost estimate"
            }
        ]
    },
    "duck_milestones": {
        1: "🦆 You've earned your first duck! Keep going!",
        2: "🦆🦆 Two ducks! You're making great progress!",
        3: "🦆🦆🦆 Three ducks! Almost there!",
        4: "🦆🦆🦆🦆🦆 Five ducks! You're ready to meet your advisor!"
    }
}


def get_content(section: str, key: str = None):
    """Get content by section and optional key.
    
    Args:
        section: Content section (e.g., "intro", "appointment")
        key: Optional specific key within section
    
    Returns:
        Content value or entire section dict
    """
    section_content = CONTENT.get(section, {})
    if key:
        return section_content.get(key, "")
    return section_content
```

---

## 6. PFMA v2 Engine

### Main Engine

```python
# products/pfma_v2/engine.py

import json
from pathlib import Path
from typing import Dict, List
import streamlit as st

from products.pfma_v2.state import PFMAState
from products.pfma_v2.guards import StepGuard
from products.pfma_v2.components.step_shell import render_step_shell
from products.pfma_v2.renderers import STEP_RENDERERS


def run_pfma() -> None:
    """Run PFMA funnel using declarative step engine."""
    # Load step schema
    schema = _load_schema()
    
    # Initialize state
    PFMAState.initialize()
    progress = PFMAState.get_progress()
    
    # Get current step
    current_step_id = progress["current_step"]
    step_index = progress["step_index"]
    
    # Find step in schema
    step = _find_step(schema, current_step_id)
    if not step:
        st.error(f"❌ Step '{current_step_id}' not found in schema")
        return
    
    # Check step guards (prerequisites)
    if "guards" in step:
        guard = StepGuard(step["guards"])
        if not guard.check():
            return  # Guard handles UI and redirect
    
    # Render step using shell + renderer
    renderer = STEP_RENDERERS.get(step["type"])
    if not renderer:
        st.error(f"❌ No renderer for step type '{step['type']}'")
        return
    
    # Render with shell
    render_step_shell(
        step=step,
        total_steps=len(schema["steps"]),
        form_content=lambda: renderer(step, schema)
    )
    
    # Handle navigation actions
    _handle_navigation(schema, step, step_index)


def _load_schema() -> Dict:
    """Load PFMA step schema from JSON."""
    schema_path = Path(__file__).parent / "pfma_steps.json"
    with schema_path.open() as f:
        return json.load(f)


def _find_step(schema: Dict, step_id: str) -> Dict:
    """Find step by ID in schema."""
    for step in schema["steps"]:
        if step["id"] == step_id:
            return step
    return None


def _handle_navigation(schema: Dict, current_step: Dict, step_index: int) -> None:
    """Handle navigation actions (back/next)."""
    action = st.session_state.get("_pfma_action")
    if not action:
        return
    
    # Clear action
    del st.session_state["_pfma_action"]
    
    if action == "next":
        # Validate current step data
        if not _validate_step(current_step):
            return
        
        # Advance to next step
        next_index = step_index + 1
        if next_index < len(schema["steps"]):
            next_step = schema["steps"][next_index]
            PFMAState.advance_step(next_step["id"], next_index)
            
            # Update duck tier
            if "duck_tier" in next_step:
                PFMAState.set_duck_tier(next_step["duck_tier"])
        
        st.rerun()
    
    elif action == "back":
        # Go to previous step
        prev_index = max(0, step_index - 1)
        prev_step = schema["steps"][prev_index]
        PFMAState.advance_step(prev_step["id"], prev_index)
        st.rerun()


def _validate_step(step: Dict) -> bool:
    """Validate current step data before advancing."""
    # Get step data
    step_data = PFMAState.get_step_data(step["id"])
    
    # Check required fields
    for field in step.get("fields", []):
        if field.get("required", False):
            field_id = field["id"]
            if field_id not in step_data or not step_data[field_id]:
                st.error(f"❌ {field['label']} is required")
                return False
    
    return True
```

---

## Implementation Plan

### Phase 1: Schema & State (Week 1)
- [ ] Define `pfma_steps.json` schema
- [ ] Implement `PFMAState` class
- [ ] Create content config
- [ ] Write unit tests for state management

### Phase 2: Layout Components (Week 1)
- [ ] Build `render_step_shell()` component
- [ ] Implement breadcrumb renderer
- [ ] Implement duck display component
- [ ] Standardize navigation buttons

### Phase 3: Step Guards (Week 2)
- [ ] Create `StepGuard` class
- [ ] Implement Cost Planner gate
- [ ] Implement GCP gate
- [ ] Implement auth gate

### Phase 4: Step Renderers (Week 2-3)
- [ ] Info page renderer (intro, completion)
- [ ] Form renderer (appointment, contact)
- [ ] Checklist renderer (verifications)
- [ ] Results renderer (completion with next steps)

### Phase 5: Engine Integration (Week 3)
- [ ] Build `run_pfma()` engine
- [ ] Connect to step schema
- [ ] Implement navigation handling
- [ ] Add validation logic

### Phase 6: Migration & Testing (Week 4)
- [ ] Update `products/pfma/product.py` to use v2 engine
- [ ] Migrate existing data format
- [ ] End-to-end testing
- [ ] A/B test with v1

---

## Benefits of v2 Architecture

### For Developers
✅ **Maintainable**: Schema-driven, no branching spaghetti  
✅ **Testable**: Clean state interface, mockable guards  
✅ **Reusable**: Shared components across products  
✅ **Type-safe**: Validated schemas prevent errors  

### For Product Teams
✅ **Iterable**: Reorder steps in JSON, no code changes  
✅ **A/B testable**: Swap schemas per user cohort  
✅ **Designer-friendly**: Content changes without deployments  
✅ **Analytics-ready**: Schema tracks funnel metrics  

### For Users
✅ **Consistent**: Same UI patterns as other products  
✅ **Reliable**: Validation prevents broken flows  
✅ **Fast**: Optimized rendering, less custom logic  
✅ **Delightful**: Polished duck gamification  

---

## Migration Strategy

### Running Both Versions

During development, both v1 and v2 will coexist:
- **v1**: `products/pfma/` (current)
- **v2**: `products/pfma_v2/` (new)

Navigation:
- v1: `?page=pfma` (existing)
- v2: `?page=pfma_v2` (parallel)

### Feature Flag

```python
# In config or environment
USE_PFMA_V2 = os.getenv("PFMA_V2_ENABLED", "false") == "true"

# In navigation
if USE_PFMA_V2:
    route = "pfma_v2"
else:
    route = "pfma"
```

### Data Migration

```python
def migrate_pfma_v1_to_v2(v1_state: dict) -> dict:
    """Migrate v1 state format to v2 structure."""
    return {
        "appointment": {
            "date": v1_state.get("appointment_date"),
            "time": v1_state.get("appointment_time"),
            "type": v1_state.get("appointment_type", "phone"),
        },
        "contact": {
            "name": v1_state.get("name"),
            "email": v1_state.get("email"),
            "phone": v1_state.get("phone"),
        },
        "verifications": {
            "identity": v1_state.get("verified_identity", False),
            "insurance": v1_state.get("verified_insurance", False),
            "veteran": v1_state.get("is_veteran", False),
        },
        "progress": {
            "current_step": _map_v1_step(v1_state.get("step", "intro")),
            "step_index": _get_step_index(v1_state.get("step")),
            "completed_steps": v1_state.get("completed_steps", []),
            "duck_tier": _calculate_duck_tier(v1_state),
            "status": v1_state.get("status", "new"),
        },
        "flags": v1_state.get("flags", {}),
    }
```

---

## Open Questions

1. **Calendar Integration**: Keep third-party scheduler or build custom?
2. **Advisor Matching**: Algorithm for matching user to advisor?
3. **Rescheduling Flow**: Allow in-app rescheduling or email-only?
4. **Reminder System**: In-app notifications or email/SMS only?
5. **Completion Rewards**: Additional gamification beyond ducks?

---

## Success Metrics

### Code Quality
- ✅ PFMA product code: 400 lines → ~150 lines (-62%)
- ✅ Zero step-branching logic
- ✅ 100% schema-driven step rendering
- ✅ Reusable layout components

### User Experience
- ✅ Consistent with GCP/Cost Planner UI
- ✅ Duck gamification preserved
- ✅ Clear progress indicators
- ✅ Smooth navigation

### Business Metrics
- ✅ Appointment completion rate (target: >80%)
- ✅ Time to schedule (target: <3 minutes)
- ✅ No-show rate (target: <15%)
- ✅ User satisfaction (target: 4.5+/5)

---

## Summary

PFMA v2 will transform the current imperative, branching codebase into a declarative, schema-driven funnel aligned with the module engine architecture. This makes PFMA:

- **Maintainable**: Easy to update and extend
- **Consistent**: Uses shared layout components
- **Testable**: Clean state interface and guards
- **Flexible**: Product teams can iterate without code changes

**Timeline**: 4 weeks after Cost Planner v2 is complete  
**Status**: Design approved, implementation pending  
**Priority**: Medium - refactor for long-term maintainability

---

**Next**: Complete Cost Planner v2 first, then return to this vision document to implement PFMA v2 🦆
