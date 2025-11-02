# PFMA v3 - Plan with My Advisor

## Overview
Simplified booking-first appointment scheduling for care advisor consultations.

## Changes from v2
- **Single step** (booking only) vs 5-step flow
- **No verification sections** (moved to optional Advisor Prep in Waiting Room)
- **Immediate handoff** to Waiting Room after booking
- **Booking = complete** (no multi-step progress tracking)

## Architecture
- **Product Type:** Single-form product (NOT module-based)
- **Prerequisites:** Cost Planner completion (via MCIP)
- **Integration:** Publishes `AdvisorAppointment` contract to MCIP
- **Handoff:** Routes to Waiting Room for optional Advisor Prep

## User Flow
1. User completes Cost Planner
2. PFMA tile unlocks in Concierge Hub
3. User clicks "Book Appointment"
4. Single booking form with validation
5. Submit → Appointment confirmed → Route to Waiting Room
6. Waiting Room shows optional Advisor Prep sections

## Validation Rules
- **Name:** Required
- **Email OR Phone:** At least one required for confirmation
- **Timezone:** Required
- **Appointment Type:** Required (video | phone | in_person)

## Session State
```json
{
  "pfma_v3_form": {
    "name": "Sarah Johnson",
    "email": "sarah@example.com",
    "phone": "555-0123",
    "timezone": "America/New_York",
    "type": "video",
    "preferred_time": "Morning (8am-12pm)",
    "notes": "Prefer morning appointments"
  }
}
```

## MCIP Contract
Publishes `AdvisorAppointment` with:
- `scheduled: true`
- `confirmation_id: UUID`
- Contact info, timezone, type
- `prep_sections_complete: []` (updated by Advisor Prep)
- `prep_progress: 0` (updated by Advisor Prep)

## Telemetry Events
- `pfma.booking.started`
- `pfma.booking.field_edited`
- `pfma.booking.validation_error`
- `pfma.booking.submitted`
- `pfma.appointment.requested`
- `waiting_room.unlocked`
- `waiting_room.first_visit`
