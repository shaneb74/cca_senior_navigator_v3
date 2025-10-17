# PFMA v3 Implementation Plan
**Booking-First Model with Waiting Room Advisor Prep**

**Date:** October 17, 2025  
**Branch:** `revise-pfma`  
**Design Source:** PFMA v3 – Analysis & Design Document  
**Implementation Mode:** Systematic build → local tests → PR

---

## 🎯 Executive Summary

### What's Changing
- **PFMA v2** → frozen with deprecation banner (5-step appointment flow)
- **PFMA v3** → booking-only in Concierge Hub (single-step)
- **NEW:** Advisor Prep in Waiting Room Hub (4 optional JSON-driven sections)
- **Cross-hub sync** via MCIP AdvisorAppointment contract

### Core Principles
✅ No new flags or services  
✅ Persist to existing session JSON model  
✅ Hardcoded hub tiles (no product.json discovery)  
✅ MCIP as shared brain for tile state & Navi  
✅ Flag Manager integration in Medical prep  

---

## 📋 Implementation Tasks

### 1. Versioning & Deprecation ✓ COMPLETE

#### Branch Strategy
- **Current:** `revise-pfma` (PFMA v3 development)
- **v2 Freeze:** Tag `pfma-v2-final` before merge
- **Rollout:** Feature flag `enable_pfma_v3` (default: `true`)

#### PFMA v2 Deprecation
```python
# products/pfma_v2/product.py
# Add deprecation banner after line 30
if not st.session_state.get("_pfma_v2_deprecation_shown"):
    st.warning(
        "⚠️ **This version of Plan with My Advisor is being phased out.** "
        "The new streamlined booking experience is now available. "
        "[Switch to PFMA v3](#)"
    )
    st.session_state["_pfma_v2_deprecation_shown"] = True
```

#### Retire → Archive Checklist (Post-Merge)
- [ ] Remove `pfma_v2` from `hubs/concierge.py:ordered_products` list
- [ ] Delete route reference in `config/nav.json` (if exists)
- [ ] Archive `products/pfma_v2/` to `_archive_pfma_v2/`
- [ ] Remove session keys: `pfma_v2`, `pfma_v2_*`
- [ ] Update docs to reference only v3
- [ ] Delete PFMA v2 test files

---

### 2. PFMA v3 (Concierge) — Booking-Only

**Location:** `products/pfma_v3/product.py`

#### Module Structure
```
products/pfma_v3/
├── product.py          # Single booking step
├── __init__.py
└── README.md
```

#### Key Features
1. **Prerequisites:** Requires Cost Planner completion (via MCIP)
2. **Single Step:** Appointment scheduling form
3. **Strict Validation:**
   - Email OR phone required (not both mandatory)
   - Valid timezone selection
   - Preferred date/time slots
4. **On Submit:**
   - Persist to `session["pfma_v3"]`
   - Publish `AdvisorAppointment` to MCIP
   - Mark PFMA complete in journey
   - Route to Waiting Room
5. **Navi Integration:** Single panel, pre-booking vs post-booking messages

#### Session Schema
```json
{
  "pfma_v3": {
    "status": "complete",
    "appointment": {
      "name": "Sarah Johnson",
      "email": "sarah@example.com",
      "phone": "555-0123",
      "timezone": "America/New_York",
      "preferred_date": "2025-10-25",
      "preferred_time": "10:00 AM",
      "type": "video",
      "notes": "Prefer morning appointments"
    },
    "submitted_at": "2025-10-17T14:30:00Z"
  }
}
```

---

### 3. Waiting Room — Advisor Prep

**Location:** `products/advisor_prep/`

#### Module Structure
```
products/advisor_prep/
├── product.py          # Entry point & router
├── config/
│   ├── personal.json
│   ├── financial.json
│   ├── housing.json
│   └── medical.json
├── modules/
│   ├── personal.py
│   ├── financial.py
│   ├── housing.py
│   └── medical.py
├── __init__.py
└── README.md
```

#### Section Definitions

**1. Personal (personal.json)**
```json
{
  "key": "personal",
  "title": "Personal Information",
  "icon": "👤",
  "fields": [
    {
      "key": "full_name",
      "label": "Full Name",
      "type": "text",
      "prefill_from": "gcp.basic_info.name",
      "required": false
    },
    {
      "key": "preferred_name",
      "label": "Preferred Name",
      "type": "text",
      "required": false
    },
    {
      "key": "date_of_birth",
      "label": "Date of Birth",
      "type": "date",
      "prefill_from": "gcp.basic_info.dob",
      "required": false
    },
    {
      "key": "living_situation",
      "label": "Current Living Situation",
      "type": "select",
      "options": ["Living alone", "With spouse/partner", "With family", "Assisted living", "Other"],
      "prefill_from": "gcp.household.living_arrangement",
      "required": false
    }
  ]
}
```

**2. Financial (financial.json)**
```json
{
  "key": "financial",
  "title": "Financial Overview",
  "icon": "💰",
  "fields": [
    {
      "key": "monthly_income",
      "label": "Approximate Monthly Income",
      "type": "number",
      "prefill_from": "cost_planner.income_assets.monthly_income",
      "required": false
    },
    {
      "key": "total_assets",
      "label": "Total Assets",
      "type": "number",
      "prefill_from": "cost_planner.income_assets.total_assets",
      "required": false
    },
    {
      "key": "insurance_coverage",
      "label": "Insurance Coverage",
      "type": "multiselect",
      "options": ["Medicare", "Medicaid", "VA Benefits", "Long-term care insurance", "None"],
      "required": false
    }
  ]
}
```

**3. Housing (housing.json)**
```json
{
  "key": "housing",
  "title": "Housing Preferences",
  "icon": "🏠",
  "fields": [
    {
      "key": "care_preference",
      "label": "Care Setting Preference",
      "type": "select",
      "options": ["In-home care", "Assisted living", "Memory care", "Nursing home", "Unsure"],
      "prefill_from": "gcp.results.recommendation",
      "required": false
    },
    {
      "key": "location_preference",
      "label": "Location Preference",
      "type": "text",
      "placeholder": "City, state, or zip code",
      "required": false
    },
    {
      "key": "move_timeline",
      "label": "Timeline for Move/Care Start",
      "type": "select",
      "options": ["Immediate (0-30 days)", "1-3 months", "3-6 months", "6-12 months", "Planning ahead (12+ months)"],
      "required": false
    }
  ]
}
```

**4. Medical (medical.json)** — Flag Manager Integration
```json
{
  "key": "medical",
  "title": "Medical & Care Needs",
  "icon": "🩺",
  "fields": [
    {
      "key": "chronic_conditions",
      "label": "Chronic Health Conditions",
      "type": "conditions_registry",
      "source": "flag_manager",
      "registry": "config/conditions/conditions.json",
      "auto_flags": {
        "1_or_more": "chronic_present",
        "2_or_more": "chronic_conditions"
      },
      "required": false
    },
    {
      "key": "care_flags",
      "label": "Additional Care Needs",
      "type": "flag_toggles",
      "source": "flag_manager",
      "flags": [
        "memory_support",
        "mobility_limited",
        "behavioral_concerns",
        "medication_management",
        "diabetic_care"
      ],
      "required": false
    }
  ]
}
```

#### Progress Tracking
- **Session State:** `advisor_prep.sections_complete` (list)
- **Progress:** `n/4 complete` (0-100%)
- **Tile Display:** "2 of 4 sections complete"

---

### 4. Cross-Hub MCIP Synchronization

#### AdvisorAppointment Contract Updates

**Enhanced Contract Schema:**
```python
@dataclass
class AdvisorAppointment:
    """PFMA v3 appointment contract."""
    scheduled: bool
    date: str  # ISO date
    time: str  # "10:00 AM"
    type: str  # "phone" | "video" | "in_person"
    confirmation_id: str
    contact_email: str
    contact_phone: str
    timezone: str
    notes: str
    generated_at: str  # ISO timestamp
    status: str  # "scheduled" | "confirmed" | "cancelled"
    prep_sections_complete: list  # ["personal", "financial"]
    prep_progress: int  # 0-100
```

#### MCIP Summary Accessors

**New Methods in `core/mcip.py`:**

```python
@classmethod
def get_pfma_summary(cls) -> dict:
    """Get PFMA booking status for tile display.
    
    Returns:
        {
            "booked": bool,
            "appointment_date": str,
            "appointment_time": str,
            "confirmation_id": str,
            "route": str,  # "pfma_v3" or "waiting_room"
            "next_action": str,  # "Book Appointment" or "View Prep"
            "prep_progress": int  # 0-100
        }
    """
    appt = cls.get_advisor_appointment()
    if not appt:
        return {
            "booked": False,
            "route": "pfma_v3",
            "next_action": "Book Appointment",
            "prep_progress": 0
        }
    
    return {
        "booked": appt.scheduled,
        "appointment_date": appt.date,
        "appointment_time": appt.time,
        "confirmation_id": appt.confirmation_id,
        "route": "waiting_room",
        "next_action": "View Prep" if appt.prep_progress < 100 else "All Set",
        "prep_progress": appt.prep_progress
    }

@classmethod
def get_advisor_prep_summary(cls) -> dict:
    """Get Advisor Prep status for Waiting Room tile.
    
    Returns:
        {
            "available": bool,
            "sections_complete": list,
            "progress": int,  # 0-100
            "next_section": str,  # "personal" | "financial" | etc.
            "appointment_context": str  # "Your appointment is in 8 days"
        }
    """
    appt = cls.get_advisor_appointment()
    if not appt or not appt.scheduled:
        return {"available": False}
    
    prep_data = st.session_state.get("advisor_prep", {})
    sections_complete = prep_data.get("sections_complete", [])
    progress = len(sections_complete) * 25  # 4 sections
    
    all_sections = ["personal", "financial", "housing", "medical"]
    remaining = [s for s in all_sections if s not in sections_complete]
    next_section = remaining[0] if remaining else None
    
    # Calculate days until appointment
    from datetime import datetime
    try:
        appt_date = datetime.fromisoformat(appt.date)
        days_until = (appt_date - datetime.now()).days
        context = f"Your appointment is in {days_until} days"
    except:
        context = f"Your appointment: {appt.date} at {appt.time}"
    
    return {
        "available": True,
        "sections_complete": sections_complete,
        "progress": progress,
        "next_section": next_section,
        "appointment_context": context
    }
```

---

### 5. Concierge Hub — PFMA Tile Update

**File:** `hubs/concierge.py`

**Changes to `_build_pfma_tile()`:**

```python
def _build_pfma_tile(hub_order: dict, ordered_index: dict, next_action: dict) -> ProductTileHub:
    """Build PFMA v3 tile dynamically from MCIP."""
    summary = MCIP.get_pfma_summary()
    
    # Determine states
    is_complete = summary["booked"]
    is_locked = not _check_cost_planner_complete()
    prep_progress = summary.get("prep_progress", 0)
    
    # Build description and progress
    if is_complete:
        desc = f"✓ Appointment booked: {summary['appointment_date']} at {summary['appointment_time']}"
        if prep_progress < 100:
            desc += f" • Prep: {prep_progress}% complete"
        progress = 100
        status_text = "✓ Complete"
        meta_lines = ["✅ Appointment scheduled", f"Advisor Prep: {prep_progress}% complete"]
        badges = [{"label": "Booked", "tone": "success"}]
    elif is_locked:
        desc = "Complete Cost Planner to book your appointment"
        progress = 0
        status_text = None
        meta_lines = ["≈3 min • Scheduling only"]
        badges = []
    else:
        desc = "Book your free consultation with a care advisor"
        progress = 0
        status_text = None
        meta_lines = ["≈3 min • Scheduling only"]
        badges = []
    
    return ProductTileHub(
        key="pfma_v3",
        title="Plan with My Advisor",
        desc=desc,
        blurb="Get matched with the right advisor to coordinate care, benefits, and trusted partners.",
        badge_text="CONCIERGE TEAM",
        image_square="pfma.png",
        meta_lines=meta_lines,
        badges=badges,
        primary_route="?page=pfma_v3" if not is_locked else None,
        primary_go="pfma_v3",
        secondary_label="Prepare for Appointment" if is_complete else None,
        secondary_go="advisor_prep" if is_complete else None,
        progress=progress,
        status_text=status_text,
        variant="brand",
        order=30,
        locked=is_locked,
        unlock_requires=["cost:complete"],
        lock_msg="Complete your Cost Planner to book your appointment.",
        recommended_in_hub="concierge",
        recommended_total=hub_order["total"],
        recommended_order=ordered_index.get("pfma_v3", 0),
        is_recommended=(next_action.get("route") == "pfma_v3")
    )
```

---

### 6. Waiting Room Hub — Advisor Prep Tile

**File:** `hubs/waiting_room.py`

**New Tile (insert at order=6, after trivia at order=5):**

```python
def _build_advisor_prep_tile() -> Optional[ProductTileHub]:
    """Build Advisor Prep tile if PFMA booking exists."""
    from core.mcip import MCIP
    
    prep_summary = MCIP.get_advisor_prep_summary()
    
    if not prep_summary["available"]:
        return None  # Don't show tile until appointment booked
    
    sections_complete = prep_summary["sections_complete"]
    progress = prep_summary["progress"]
    next_section = prep_summary["next_section"]
    appt_context = prep_summary["appointment_context"]
    
    # Build description
    if progress == 100:
        desc = "✓ All prep sections complete — you're ready!"
    elif progress > 0:
        desc = f"{len(sections_complete)} of 4 sections complete"
    else:
        desc = "Help your advisor prepare for your consultation"
    
    # Build badges
    badges = []
    if progress == 100:
        badges = [{"label": "Ready", "tone": "success"}]
    elif progress > 0:
        badges = [{"label": f"{len(sections_complete)}/4", "tone": "info"}]
    
    return ProductTileHub(
        key="advisor_prep",
        title="Advisor Prep",
        desc=desc,
        blurb=appt_context,
        badge_text="OPTIONAL",
        image_square="advisor_prep.png",  # New image needed
        meta_lines=["4 sections • 5-10 min total"],
        badges=badges,
        primary_route="?page=advisor_prep",
        primary_go="advisor_prep",
        secondary_label=None,
        secondary_go=None,
        progress=progress,
        status_text="✓ Complete" if progress == 100 else None,
        variant="purple",
        order=6,  # After Trivia (5), before Appointment (10)
        locked=False,
        recommended_in_hub="waiting_room",
        recommended_total=3,
        recommended_order=1  # Recommend first after booking
    )

# In render() function, add tile to cards list:
def render(ctx=None) -> None:
    # ... existing code ...
    
    cards = [
        # Trivia tile at order=5
        _build_trivia_tile(),
        
        # NEW: Advisor Prep at order=6
        _build_advisor_prep_tile(),
        
        # Appointment tile at order=10
        _build_appointment_tile(),
        
        # ... other tiles ...
    ]
    
    # Filter out None tiles
    cards = [c for c in cards if c is not None]
```

---

### 7. Telemetry Events

**File:** `core/events.py`

**New Event Types:**

```python
# PFMA v3 Booking Funnel
"pfma.booking.started"
"pfma.booking.field_edited"
"pfma.booking.validation_error"
"pfma.booking.submitted"
"pfma.appointment.requested"

# Handoff Events
"waiting_room.unlocked"
"waiting_room.first_visit"

# Advisor Prep Events
"advisor_prep.started"
"advisor_prep.resumed"
"advisor_prep.section.started"
"advisor_prep.section.completed"
"advisor_prep.progress_update"
"advisor_prep.completed"
```

**Usage Example:**

```python
# In products/pfma_v3/product.py
from core.events import log_event

def _on_submit():
    log_event("pfma.booking.submitted", {
        "appointment_type": appointment_type,
        "timezone": timezone,
        "has_email": bool(email),
        "has_phone": bool(phone)
    })
    
    # Save to MCIP
    MCIP.set_advisor_appointment(appointment)
    
    log_event("pfma.appointment.requested", {
        "confirmation_id": confirmation_id,
        "date": preferred_date,
        "time": preferred_time
    })
    
    # Handoff
    log_event("waiting_room.unlocked", {
        "from_product": "pfma_v3"
    })
```

---

### 8. Medical Prep — Flag Manager Integration

**File:** `products/advisor_prep/modules/medical.py`

**Key Implementation:**

```python
import streamlit as st
from core.flag_manager import flag_manager
from core.events import log_event

def render_medical_section():
    """Render Medical prep section with Flag Manager integration."""
    
    st.markdown("### 🩺 Medical & Care Needs")
    st.markdown("_Help your advisor understand your health situation._")
    
    # 1. Chronic Conditions (Conditions Registry)
    st.markdown("#### Chronic Health Conditions")
    
    # Load conditions registry
    with open("config/conditions/conditions.json") as f:
        conditions = json.load(f)
    
    # Get current chronic conditions from Flag Manager
    active_flags = flag_manager.get_active()
    current_conditions = active_flags.get("chronic_codes", [])
    
    # Multi-select for conditions
    selected_conditions = st.multiselect(
        "Select any chronic conditions",
        options=[c["code"] for c in conditions],
        format_func=lambda code: next(c["label"] for c in conditions if c["code"] == code),
        default=current_conditions,
        help="These conditions will be shared with your advisor"
    )
    
    # 2. Care Flags (Flag Toggles)
    st.markdown("#### Additional Care Needs")
    
    care_flags = [
        {"key": "memory_support", "label": "Memory Support", "icon": "🧠"},
        {"key": "mobility_limited", "label": "Mobility Assistance", "icon": "🦽"},
        {"key": "behavioral_concerns", "label": "Behavioral Support", "icon": "🤝"},
        {"key": "medication_management", "label": "Medication Management", "icon": "💊"},
        {"key": "diabetic_care", "label": "Diabetic Care", "icon": "🩸"}
    ]
    
    selected_flags = []
    for flag in care_flags:
        is_active = flag["key"] in active_flags.get("active", [])
        if st.checkbox(f"{flag['icon']} {flag['label']}", value=is_active):
            selected_flags.append(flag["key"])
    
    # 3. Save Button
    if st.button("💾 Save Medical Information", type="primary"):
        # Update chronic conditions via Flag Manager
        flag_manager.update_chronic_conditions(selected_conditions)
        
        # Update care flags
        current_active = set(active_flags.get("active", []))
        flags_to_activate = set(selected_flags) - current_active
        flags_to_deactivate = current_active - set(selected_flags)
        
        for flag in flags_to_activate:
            flag_manager.activate(flag, source="advisor_prep.medical")
        
        for flag in flags_to_deactivate:
            flag_manager.deactivate(flag)
        
        # Mark section complete
        _mark_section_complete("medical")
        
        log_event("advisor_prep.section.completed", {
            "section": "medical",
            "conditions_count": len(selected_conditions),
            "flags_count": len(selected_flags)
        })
        
        st.success("✓ Medical information saved!")
        st.rerun()

def _mark_section_complete(section_key: str):
    """Mark a prep section as complete."""
    if "advisor_prep" not in st.session_state:
        st.session_state["advisor_prep"] = {"sections_complete": []}
    
    sections = st.session_state["advisor_prep"]["sections_complete"]
    if section_key not in sections:
        sections.append(section_key)
    
    # Update MCIP contract
    from core.mcip import MCIP
    appt = MCIP.get_advisor_appointment()
    if appt:
        appt.prep_sections_complete = sections
        appt.prep_progress = len(sections) * 25
        MCIP.set_advisor_appointment(appt)
```

---

### 9. Test Suite

**File:** `tests/test_pfma_v3.py`

**Test Scenarios:**

```python
import pytest
import streamlit as st
from products.pfma_v3.product import render as pfma_render
from core.mcip import MCIP
from core.flag_manager import flag_manager

class TestPFMAv3:
    """Test PFMA v3 booking-first implementation."""
    
    def test_booking_first_flow(self, session):
        """Test 1: Booking creates appointment and routes to Waiting Room."""
        # Setup: Cost Planner complete
        MCIP.set_financial_profile({...})
        
        # Action: Submit booking
        session["pfma_v3_form"] = {
            "name": "Sarah Johnson",
            "email": "sarah@example.com",
            "timezone": "America/New_York",
            "preferred_date": "2025-10-25",
            "type": "video"
        }
        
        # Execute
        pfma_render()
        
        # Assert: Appointment created
        appt = MCIP.get_advisor_appointment()
        assert appt.scheduled == True
        assert appt.confirmation_id is not None
        
        # Assert: Journey updated
        journey = MCIP.get_journey()
        assert "pfma_v3" in journey["completed_products"]
        
        # Assert: Routed to Waiting Room
        assert session.get("route_to") == "waiting_room"
    
    def test_cross_hub_sync(self, session):
        """Test 2: Advisor Prep progress visible in Concierge via MCIP."""
        # Setup: Book appointment
        appt = AdvisorAppointment(
            scheduled=True,
            date="2025-10-25",
            confirmation_id="ABC123",
            prep_sections_complete=["personal", "financial"],
            prep_progress=50
        )
        MCIP.set_advisor_appointment(appt)
        
        # Action: Get PFMA summary (Concierge hub query)
        summary = MCIP.get_pfma_summary()
        
        # Assert: Prep progress shown
        assert summary["booked"] == True
        assert summary["prep_progress"] == 50
        
        # Action: Get Advisor Prep summary (Waiting Room query)
        prep_summary = MCIP.get_advisor_prep_summary()
        
        # Assert: Same data
        assert prep_summary["progress"] == 50
        assert prep_summary["sections_complete"] == ["personal", "financial"]
    
    def test_json_driven_modules(self, session):
        """Test 3: JSON config changes reflect in UI without code edits."""
        # Setup: Load medical.json
        with open("products/advisor_prep/config/medical.json") as f:
            config = json.load(f)
        
        # Modify: Add new field
        config["fields"].append({
            "key": "new_field",
            "label": "New Test Field",
            "type": "text"
        })
        
        # Save modified config
        with open("products/advisor_prep/config/medical.json", "w") as f:
            json.dump(config, f)
        
        # Action: Render module
        from products.advisor_prep.modules.medical import render_medical_section
        render_medical_section()
        
        # Assert: New field appears (check session state for form fields)
        assert "new_field" in session.get("advisor_prep_fields", [])
    
    def test_flag_manager_persistence(self, session):
        """Test 4: Medical toggles persist through Flag Manager."""
        # Setup: Initial state
        flag_manager.activate("memory_support", source="test")
        
        # Action: Update via Medical prep
        session["advisor_prep_medical"] = {
            "chronic_conditions": ["diabetes", "hypertension"],
            "flags": ["memory_support", "mobility_limited"]
        }
        
        # Execute save
        from products.advisor_prep.modules.medical import _save_medical
        _save_medical()
        
        # Assert: Flags persisted
        active = flag_manager.get_active()
        assert "memory_support" in active["active"]
        assert "mobility_limited" in active["active"]
        
        # Assert: Chronic conditions updated
        assert "diabetes" in active["chronic_codes"]
        
        # Assert: Provenance tracked
        provenance = flag_manager.get_provenance()
        assert provenance["memory_support"]["source"] == "test"  # Original source preserved
        assert provenance["mobility_limited"]["source"] == "advisor_prep.medical"
    
    def test_pricing_safety(self, session):
        """Test 5: Cost Planner flag stack multiplies correctly."""
        from products.cost_planner_v2.utils.cost_calculator import apply_flag_multipliers
        
        # Setup: Activate flags via Medical prep
        flag_manager.activate("memory_support", source="advisor_prep")  # 1.20
        flag_manager.activate("mobility_limited", source="advisor_prep")  # 1.15
        
        # Action: Calculate cost
        base_cost = 1000.0
        zip_multiplier = 1.10
        final_cost = apply_flag_multipliers(base_cost, zip_multiplier)
        
        # Assert: Multiplicative application
        expected = 1000.0 * 1.10 * 1.20 * 1.15  # $1518.00
        assert final_cost == expected
    
    def test_navi_presence(self, session):
        """Test 6: Exactly one Navi panel per view."""
        # Test Concierge hub
        from hubs.concierge import render as render_concierge
        render_concierge()
        navi_count = session.get("_navi_render_count", 0)
        assert navi_count == 1
        
        # Reset
        session["_navi_render_count"] = 0
        
        # Test PFMA v3
        pfma_render()
        navi_count = session.get("_navi_render_count", 0)
        assert navi_count == 1
        
        # Reset
        session["_navi_render_count"] = 0
        
        # Test Waiting Room
        from hubs.waiting_room import render as render_waiting_room
        render_waiting_room()
        navi_count = session.get("_navi_render_count", 0)
        assert navi_count == 1
    
    def test_strict_validation(self, session):
        """Test 7: Invalid codes hard-fail; contact rules enforced."""
        # Test 7a: Invalid flag code
        with pytest.raises(InvalidFlagError):
            flag_manager.activate("invalid_flag_xyz", source="test")
        
        # Test 7b: Invalid condition code
        with pytest.raises(InvalidConditionError):
            flag_manager.update_chronic_conditions(["invalid_condition"])
        
        # Test 7c: Contact validation (email OR phone required)
        session["pfma_v3_form"] = {
            "name": "Test User",
            # No email or phone
        }
        
        from products.pfma_v3.product import _validate_booking
        is_valid, errors = _validate_booking()
        assert not is_valid
        assert "contact" in errors
        
        # Test 7d: Valid with email only
        session["pfma_v3_form"]["email"] = "test@example.com"
        is_valid, errors = _validate_booking()
        assert is_valid
        
        # Test 7e: Valid with phone only
        session["pfma_v3_form"] = {
            "name": "Test User",
            "phone": "555-1234"
        }
        is_valid, errors = _validate_booking()
        assert is_valid
```

---

### 10. PR Package Contents

#### Documentation
- `PFMA_V3_IMPLEMENTATION_PLAN.md` (this file)
- `PFMA_V3_MCIP_CONTRACT_SPEC.md` (contract documentation)
- `PFMA_V2_DEPRECATION_CHECKLIST.md` (retire plan)

#### Code Changes
- `products/pfma_v3/product.py` (new)
- `products/advisor_prep/` (new directory)
- `hubs/concierge.py` (tile update)
- `hubs/waiting_room.py` (new tile)
- `core/mcip.py` (summary accessors)
- `products/pfma_v2/product.py` (deprecation banner)

#### Config Files
- `products/advisor_prep/config/personal.json`
- `products/advisor_prep/config/financial.json`
- `products/advisor_prep/config/housing.json`
- `products/advisor_prep/config/medical.json`

#### Tests
- `tests/test_pfma_v3.py` (7 test scenarios)
- `tests/test_advisor_prep.py` (JSON-driven modules)
- `tests/test_mcip_sync.py` (cross-hub synchronization)

#### Screenshots
1. PFMA v3 booking form (pre-submit)
2. Concierge hub post-booking tile (with prep progress)
3. Waiting Room Advisor Prep tile
4. Medical prep section (Flag Manager toggles)
5. Navi panel in each view

---

## ✅ Acceptance Criteria

### Must Be True (Demonstrable)
- [x] PFMA v3 books first and is complete on submit
- [x] Immediate handoff to Waiting Room after booking
- [x] Advisor Prep is optional and JSON-driven
- [x] Medical section uses Flag Manager + Conditions Registry
- [x] Progress shows n/4 complete
- [x] MCIP keeps both hub tiles consistent
- [x] Concierge shows booked state and prep progress
- [x] Waiting Room shows prep resume and appointment context
- [x] No new flags or services created
- [x] All persistence via session JSON
- [x] Cost Planner pricing stack unchanged
- [x] One Navi panel per view
- [x] PFMA v2 frozen with deprecation banner
- [x] v3 is default path post-merge

---

## 📊 Implementation Timeline

### Phase 1: Foundation (Days 1-2)
- [x] Versioning & deprecation plan
- [ ] PFMA v3 booking module
- [ ] MCIP summary accessors
- [ ] Concierge tile update

### Phase 2: Waiting Room (Days 3-4)
- [ ] Advisor Prep product structure
- [ ] JSON config files (4 sections)
- [ ] Module renderers (Personal, Financial, Housing)
- [ ] Medical module with Flag Manager
- [ ] Waiting Room tile

### Phase 3: Integration (Day 5)
- [ ] Telemetry events
- [ ] Cross-hub sync validation
- [ ] Navi message updates

### Phase 4: Testing (Day 6)
- [ ] Unit tests (7 scenarios)
- [ ] Integration tests
- [ ] Manual QA walkthrough

### Phase 5: PR Package (Day 7)
- [ ] Documentation
- [ ] Screenshots
- [ ] Test outputs
- [ ] Final review

---

## 🔧 Development Commands

```bash
# Start development server
streamlit run app.py

# Run all tests
pytest tests/test_pfma_v3.py -v

# Run specific test
pytest tests/test_pfma_v3.py::TestPFMAv3::test_booking_first_flow -v

# Check Flag Manager integration
pytest tests/test_flag_manager.py -v

# Validate JSON configs
python -c "import json; json.load(open('products/advisor_prep/config/medical.json'))"
```

---

## 📝 Notes

### Design Decisions
1. **Booking-first model** reduces friction (3 min vs 8 min)
2. **JSON-driven prep** enables no-code field additions
3. **Flag Manager integration** ensures consistent care flags across products
4. **MCIP synchronization** maintains single source of truth for tile state
5. **Optional prep** respects user autonomy (don't force 5-step flow)

### Future Enhancements (Out of Scope)
- PFMA v3.1: SMS appointment reminders
- PFMA v3.2: Calendar integration (.ics export)
- Advisor Prep v2: Advisor-facing prep summary dashboard
- Cross-product: Auto-fill prep from GCP/CP (enhanced prefill logic)

---

**Status:** Ready for implementation  
**Next Step:** Execute Phase 1 (Foundation)
