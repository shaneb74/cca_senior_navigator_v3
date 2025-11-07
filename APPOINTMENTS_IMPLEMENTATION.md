# Appointments Feature Implementation

**Branch:** `appointments` (based on `cca_crm`)  
**Status:** Phase 1 & 2 Complete ✅  
**Date:** November 6, 2025

## Overview

Comprehensive "Schedule Your Consultation" flow with contextual prefill, relationship fields, post-booking branching, and care preparation preferences.

## Architecture

```
Welcome/Audience → Session State
        ↓
    PFMA v3 (Enhanced)
    - Contextual prefill
    - Relationship fields
    - Appointment booking
        ↓
    Confirmation + Flag Acknowledgments
        ↓
    Care Prep Product (NEW)
    ┌────────────────┴────────────────┐
    ↓                                  ↓
Community Path                    In-Home Path
(AL/MC facilities)                (Home setup)
- Location preferences            - Location (lighter)
- Budget range                    - Timeline
- Move timeline                   - Budget awareness
- Priorities (multiselect)        - Current support
- Room preference                 - Notes
- Pet accommodation
- Additional notes
    ↓                                  ↓
Save to MCIP → Mark Complete → Return to Hub
```

## Phase 1: PFMA Enhancement (Commit 652c317)

### Files Changed
- `products/pfma_v3/product.py` (+216, -45)

### Features Implemented

#### 1. Contextual Prefill
Pulls from session state set by Welcome/Audience pages:
- `relationship_type` → Determines if planning for self
- `person_name` / `planning_for_name` → Care recipient name
- `planning_for_relationship` → "self" vs "someone_else"

**Logic:**
```python
is_self = (relationship_type == "Myself" or planning_for == "self")
default_attendee = person_name if is_self else ""
default_care_recipient = person_name if is_self else ""
```

#### 2. Relationship Fields
**New fields:**
- `attendee_name` - Who will attend the consultation
- `relation` - Dropdown: Self, Spouse/Partner, Daughter/Son, Other Family, Friend/Advocate, Professional
- `care_recipient_name` - Conditional (only shows when relation ≠ Self)

**Privacy messaging:**
```
🔒 We'll never contact this person without your consent.
```

#### 3. Enhanced Validation
- Attendee name required
- Relationship selection required
- Care recipient name required when relation ≠ Self
- Email, phone validation (existing)

#### 4. Flag-Based Post-Booking Branching
After booking confirmation, shows preparation acknowledgments based on care tier:

**Community Path (AL/MC):**
- "Your advisor will match you with communities equipped to handle..."
- Lists 5+ focus areas from care flags (memory care, medication, mobility, etc.)
- Message: "We will be looking for facilities that can handle special situations"

**In-Home Path:**
- "Be prepared to discuss..."
- Lists 6+ discussion topics from care flags
- Message: "Your advisor will help you address each area with practical solutions"

**Care Flags Used:**
- Cognitive: `cog_moderate`, `cog_severe`, `moderate_cognitive_decline`, `memory_care_dx`
- Medication: `medication_management`, `med_complexity`
- Mobility: `mobility_limited`, `fall_risk`, `falls_multiple`
- Behavioral: `behavioral_concerns`, `wandering_risk`
- ADL: `adl_support_high`, `multiple_adl_limitations`
- Support: `no_support`, `limited_support`, `caregiver_strain`
- Nutrition: `nutrition_risk`, `meal_prep_difficulty`

#### 5. CRM Integration Updates
Updated customer creation to use new field structure:
```python
care_recipient_name = form_data.get("care_recipient_name", "").strip()
attendee_name = form_data.get("attendee_name", "").strip()
relation = form_data.get("relation", "Self")
crm_name = care_recipient_name if care_recipient_name else attendee_name
```

---

## Phase 2: Care Prep Product (Commit 29c1575)

### Files Changed
- `products/care_prep/__init__.py` (new)
- `products/care_prep/product.py` (new, 500+ lines)
- `products/pfma_v3/product.py` (routing logic)
- `config/nav.json` (product registration)

### Product Structure

**Location:** `products/care_prep/product.py`  
**Entry Point:** `render()` - Checks tier and routes to appropriate path  
**Navigation:** Hidden product, accessed via PFMA routing

### Features Implemented

#### 1. Unified Branching Architecture
Single product with three paths:
- `_render_community_path()` - AL/MC facility preferences
- `_render_inhome_path()` - In-home care acknowledgments
- `_render_general_path()` - Fallback for unknown tiers

**Branching Logic:**
```python
if tier in ("assisted_living", "memory_care", "memory_care_high_acuity"):
    _render_community_path()
elif tier in ("in_home", "in_home_care"):
    _render_inhome_path()
else:
    _render_general_path()
```

#### 2. Community Path Form
**Captures:**
- Location (text input) - "City, state, or 'near family'"
- Move timeline (selectbox) - Immediately, 3 months, 6 months, 1 year, etc.
- Budget range (number inputs) - Min/max monthly budget
- Priorities (multiselect) - Cost, Location, Quality of care, Social activities, etc.
- Room preference (selectbox) - Private, Shared, No preference
- Pet accommodation (checkbox + details)
- Additional notes (text area)

**Focus Areas Display:**
Shows care flags converted to facility requirements:
- "Memory care support with specialized cognitive programs"
- "Professional medication management with trained nursing staff"
- "Fall prevention and mobility assistance..."
- etc.

#### 3. In-Home Path Form (Lighter)
**Captures:**
- Location (text input) - For caregiver availability
- Timeline (selectbox) - When care needs to start
- Budget awareness (radio) - Have budget vs need help
- Budget range (conditional number inputs)
- Current support (selectbox) - None, Family, Professional, etc.
- Notes (text area)

**Discussion Topics Display:**
Shows care flags converted to preparation topics:
- "Medication management – Setting up reliable systems..."
- "Cognitive support – Memory aids and routines..."
- "Home safety modifications – Fall prevention..."
- etc.

#### 4. MCIP Integration
**Saves preferences to appointment notes:**
```python
def _save_to_mcip(preferences: dict):
    appt = MCIP.get_advisor_appointment()
    pref_summary = "\n\n--- Care Preparation Preferences ---\n"
    # Formats all preferences as text
    appt.notes += pref_summary
    MCIP.set_advisor_appointment(appt)
```

**Marks product complete:**
```python
MCIP.mark_product_complete("care_prep")
```

#### 5. PFMA Routing Integration
Updated confirmation screen with conditional routing:

**For AL/MC/In-home tiers:**
- Primary CTA: "Continue to Preferences →" (routes to care_prep)
- Secondary: "Skip & Return to Lobby" (optional step)
- Message: "Let's gather a few preferences to make your consultation more productive"

**For unknown tiers:**
- Single CTA: "Return to Lobby"
- No care_prep routing

---

## Data Flow

### Session State Keys
**Set by Welcome/Audience:**
- `relationship_type` - "Myself" or other
- `person_name` / `planning_for_name` - Care recipient
- `planning_for_relationship` - "self" vs "someone_else"

**Set by GCP:**
- `flags` - List of care assessment flags
- `gcp_care_recommendation` - Care tier recommendation

**Set by PFMA:**
- `attendee_name` - Who's attending consultation
- `relation` - Relationship to care recipient
- `care_recipient_name` - Person needing care

**Set by Care Prep:**
- `care_prep_preferences` - All captured preferences
- `location_preference` - Location for care
- `move_timeline` - When moving/starting care
- `budget_min` / `budget_max` - Budget range
- `housing_priorities` - Preference list
- `has_pet` / `pet_details` - Pet info
- `community_notes` / `inhome_notes` - Additional notes
- `care_prep_complete` - Boolean flag

### MCIP Integration
**Gets:**
- `MCIP.get_care_recommendation()` - Returns care tier for branching
- `MCIP.get_advisor_appointment()` - Gets current appointment

**Sets:**
- `MCIP.set_advisor_appointment(appt)` - Saves updated appointment with preferences
- `MCIP.mark_product_complete("care_prep")` - Marks product completion

---

## Dropdown Options (Standardized)

### Current Housing Type
- Single-family home
- Apartment/Condo
- Senior housing
- Assisted living
- Memory care
- Other

### Move Timeline
- Immediately
- Within 3 months
- Within 6 months
- Within 1 year
- More than 1 year
- Not planning to move / Just exploring options

### Housing Priorities (multiselect)
- Cost
- Location
- Quality of care
- Social activities
- Medical services
- Pet-friendly
- Family proximity
- Safety/security

### Relationship to Care Recipient
- Self
- Spouse/Partner
- Daughter/Son
- Other Family
- Friend/Advocate
- Professional

### Room Preference
- Private room
- Shared room
- No preference

### Current Support (In-home)
- No support currently
- Family provides some help
- Professional caregiver (part-time)
- Professional caregiver (full-time)
- Other

---

## Design Principles

### 1. Acknowledge, Don't Re-Ask
Use GCP assessment flags to show we're prepared, not to interrogate again:
- ✅ "Based on your assessment, your advisor will focus on..."
- ❌ "Do you need help with medication management?"

### 2. Conversational Tone
- "Your advisor will help you..." (supportive)
- "Be prepared to discuss..." (collaborative)
- "Let's gather preferences..." (partnership)

### 3. Unified Architecture
One product with branching, not separate products:
- Easier to maintain
- Consistent user experience
- Shared code for common logic

### 4. Privacy First
- "🔒 We'll never contact this person without your consent"
- Clear about who's attending vs who needs care
- Optional fields marked clearly

### 5. Optional Flow
Care prep is optional (can skip from PFMA):
- Primary path encourages completion
- Secondary escape hatch to lobby
- Advisor still contacts regardless

---

## Testing Checklist

### Phase 1 (PFMA) Testing
- [ ] Contextual prefill works from Welcome/Audience
- [ ] Planning for self: attendee = care recipient
- [ ] Planning for someone else: separate fields
- [ ] Validation prevents submission without required fields
- [ ] Care recipient field shows/hides based on relationship
- [ ] Privacy message displays correctly
- [ ] CRM customer creation uses correct name fields
- [ ] Post-booking branching shows correct path (AL/MC vs in-home)
- [ ] Flag acknowledgments display relevant care areas
- [ ] MCIP appointment saved with all fields

### Phase 2 (Care Prep) Testing
- [ ] Routing from PFMA works for AL/MC/in-home tiers
- [ ] Community path displays for AL/MC tiers
- [ ] In-home path displays for in-home tiers
- [ ] General path displays for unknown tiers
- [ ] Focus areas show correct flags on community path
- [ ] Discussion topics show correct flags on in-home path
- [ ] All form fields save to session state
- [ ] Preferences save to MCIP appointment notes
- [ ] Product marked complete in MCIP
- [ ] "Skip" button works (returns to lobby)
- [ ] "Back to Hub" button works after completion
- [ ] Budget fields conditional on budget_known radio
- [ ] Pet details conditional on has_pet checkbox
- [ ] Form submission shows success message + balloons

### Integration Testing
- [ ] Complete flow: Welcome → Audience → GCP → PFMA → Care Prep → Lobby
- [ ] Session state persists across navigation
- [ ] MCIP data available throughout flow
- [ ] Care flags correctly identified and displayed
- [ ] Both paths (self vs someone else) work end-to-end
- [ ] Skip care_prep still allows return to lobby
- [ ] Advisor appointment notes contain all captured data

---

## Future Enhancements

### Short-term
1. **MCIP Dataclass Update** - Add structured fields to AdvisorAppointment:
   - `attendee_name: str`
   - `attendee_relation: str`
   - `care_recipient_name: str`
   - `care_type: str` (community vs in-home)
   - `preferences: dict`

2. **Validation Enhancement** - Add business logic:
   - Email format validation with regex
   - Phone format validation (US phone numbers)
   - Budget max > budget min check
   - Timeline logic (can't be "immediately" if just exploring)

3. **UI Polish**:
   - Add loading states for form submission
   - Better mobile responsiveness
   - Progress indicator for multi-step flow
   - Tooltip explanations for complex fields

### Long-term
1. **Community Matching Integration**:
   - Pass care_prep preferences to smart matching algorithm
   - Pre-filter communities based on budget, location, priorities
   - Show "Your advisor found X matching communities" on confirmation

2. **Calendar Integration**:
   - Real advisor availability calendar
   - Book specific time slots (not just preferences)
   - Send calendar invites automatically

3. **Follow-up Reminders**:
   - Email confirmation of appointment
   - 24-hour reminder before consultation
   - Prep checklist email with what to bring/discuss

4. **Advisor Dashboard**:
   - View all pending consultations
   - See captured preferences before call
   - One-click access to matched communities or care plans

---

## Commit History

```
29c1575 (HEAD -> appointments) Phase 2: Create unified care_prep product with branching
652c317 Phase 1: Enhance PFMA with relationship fields and flag-based prep
59aa275 (cca_crm) Integrate CRM data sources: QuickBase, Navigator app, and demo users
```

## Files Changed Summary

### Phase 1
- `products/pfma_v3/product.py` - 1 file, +216/-45 lines

### Phase 2
- `products/care_prep/__init__.py` - New file
- `products/care_prep/product.py` - New file, 500+ lines
- `products/pfma_v3/product.py` - Routing logic
- `config/nav.json` - Product registration
- Total: 4 files, +584/-14 lines

### Combined Total
- 5 files changed
- 800+ lines added
- 59 lines deleted

---

## Success Criteria Met

✅ **Contextual Prefill** - Auto-fills from Welcome/Audience  
✅ **Relationship Fields** - Who's attending vs who needs care  
✅ **Post-Booking Branching** - Different paths for AL/MC vs in-home  
✅ **Flag Acknowledgments** - Conversational enumeration, not re-asking  
✅ **Unified Architecture** - One product with branching logic  
✅ **Privacy Messaging** - Clear consent messaging throughout  
✅ **Optional Flow** - Can skip care_prep and still book appointment  
✅ **MCIP Integration** - Saves all data for advisor review  
✅ **Consistent Dropdowns** - Reuses existing preference options  
✅ **Clean Code** - All syntax validated, pre-commit hooks passed  

---

**Status:** Ready for testing and refinement ✅
