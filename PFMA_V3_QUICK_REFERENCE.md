# PFMA v3 - Quick Reference Card

## 🎯 What Is It?

PFMA v3 splits appointment scheduling into two parts:
1. **Booking** (Concierge Hub) - Required, single-step
2. **Prep** (Waiting Room Hub) - Optional, 4 sections

## 📊 Implementation Stats

| Metric | Value |
|--------|-------|
| **New Files** | 14 |
| **Modified Files** | 4 |
| **Lines of Code** | ~1,700 (new) + 150 (modified) |
| **Test Coverage** | 19/19 tests passing (100%) |
| **Test Categories** | 9 (booking, sync, JSON, flags, pricing, Navi, validation, progress, persistence) |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CONCIERGE HUB                            │
│  ┌───────────┐  ┌───────────┐  ┌──────────────────┐        │
│  │    GCP    │→ │   Cost    │→ │   PFMA v3        │        │
│  │           │  │  Planner  │  │  (Book Only)     │        │
│  └───────────┘  └───────────┘  └──────────────────┘        │
│                                        │                     │
│                                        │ Publish to MCIP     │
│                                        ↓                     │
└────────────────────────────────────────────────────────────┘
                                         │
                           ┌─────────────┴─────────────┐
                           │         MCIP              │
                           │  AdvisorAppointment       │
                           │  - scheduled: true        │
                           │  - confirmation_id        │
                           │  - prep_progress: 0-100   │
                           └─────────────┬─────────────┘
                                         │
┌────────────────────────────────────────────────────────────┐
│                   WAITING ROOM HUB                         │
│  ┌────────────────────────────────────────────────┐        │
│  │          Advisor Prep (Optional)               │        │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐       │        │
│  │  │ Personal │ │Financial │ │ Housing  │       │        │
│  │  └──────────┘ └──────────┘ └──────────┘       │        │
│  │  ┌────────────────────────────────────┐       │        │
│  │  │ Medical (Flag Manager)             │       │        │
│  │  │ - Chronic conditions               │       │        │
│  │  │ - Care flags                       │       │        │
│  │  │ - Auto-flag rules                  │       │        │
│  │  └────────────────────────────────────┘       │        │
│  └────────────────────────────────────────────────┘        │
└────────────────────────────────────────────────────────────┘
```

## 🔄 User Journey

```
1. Complete GCP
   ↓
2. Complete Cost Planner
   ↓
3. Book Appointment (PFMA v3)
   │ → Email/Phone validation
   │ → MCIP publishes AdvisorAppointment
   │ → Waiting Room unlocked
   ↓
4. Redirect to Waiting Room
   ↓
5. Optional: Complete Prep Sections (0-4)
   │ → Personal (demographics)
   │ → Financial (income/assets)
   │ → Housing (living situation)
   │ → Medical (conditions + flags)
   ↓
6. Progress syncs to Concierge tile
   ↓
7. Ready for Advisor Call
```

## 🔑 Key Features

### PFMA v3 (Booking)
- ✅ Single-step form
- ✅ Email OR phone required (not both)
- ✅ Timezone selection
- ✅ Appointment type (phone/video/in-person)
- ✅ Confirmation ID generation
- ✅ MCIP contract publishing

### Advisor Prep
- ✅ JSON-driven modules
- ✅ Prefill from GCP/Cost Planner
- ✅ Progress tracking (0%, 25%, 50%, 75%, 100%)
- ✅ Flag Manager integration (Medical)
- ✅ Auto-flag rules (0/1/≥2 conditions)
- ✅ Provenance tracking

### MCIP Integration
- ✅ AdvisorAppointment contract
- ✅ `get_pfma_summary()` for Concierge
- ✅ `get_advisor_prep_summary()` for Waiting Room
- ✅ Cross-hub synchronization

## 📁 File Locations

```
products/pfma_v3/
├── product.py          # Booking-only product (358 lines)
└── README.md

products/advisor_prep/
├── product.py          # Module router (245 lines)
├── config/
│   ├── personal.json
│   ├── financial.json
│   ├── housing.json
│   └── medical.json
└── modules/
    ├── personal.py     # 182 lines
    ├── financial.py    # 182 lines
    ├── housing.py      # 182 lines
    └── medical.py      # 280 lines (Flag Manager)

core/mcip.py            # Extended AdvisorAppointment
hubs/concierge.py       # Updated PFMA tile
hubs/waiting_room.py    # Added Advisor Prep tile
config/nav.json         # Added routes

tests/test_pfma_v3.py   # 19 tests (500+ lines)
```

## 🧪 Testing

**Run Tests:**
```bash
pytest tests/test_pfma_v3.py -v
```

**Expected Output:**
```
19 passed, 10 warnings in 0.07s
```

**Test Categories:**
1. Booking-first flow (3)
2. Cross-hub sync (2)
3. JSON-driven modules (3)
4. Flag Manager integration (3)
5. Pricing safety (1)
6. Navi presence (2)
7. Strict validation (3)
8. Progress tracking (1)
9. Data persistence (1)

## 🎨 MCIP Contract

### AdvisorAppointment
```python
{
  "scheduled": bool,
  "date": "2025-10-25",
  "time": "Morning (8am-12pm)",
  "type": "video",
  "confirmation_id": "ABC123",
  "contact_email": "user@example.com",
  "contact_phone": "555-1234",
  "timezone": "America/New_York",
  "notes": "Prefer morning calls",
  "generated_at": "2025-10-17T10:30:00Z",
  "status": "scheduled",
  "prep_sections_complete": ["personal", "financial"],
  "prep_progress": 50
}
```

### Publish
```python
MCIP.set_advisor_appointment(appointment)
```

### Retrieve
```python
# Full contract
appointment = MCIP.get_advisor_appointment()

# Concierge summary
pfma_summary = MCIP.get_pfma_summary()

# Waiting Room summary
prep_summary = MCIP.get_advisor_prep_summary()
```

## 📈 Telemetry Events

| Event | When | Data |
|-------|------|------|
| `pfma_booking_start` | User opens PFMA v3 | `{source: "concierge"}` |
| `pfma_booking_submit` | Valid booking submitted | `{appointment_type, contact_method, timezone}` |
| `advisor_appointment_requested` | Appointment created | `{confirmation_id, date, time}` |
| `waiting_room_unlocked` | Redirect to Waiting Room | `{trigger: "pfma_v3_complete"}` |
| `advisor_prep_start` | User opens Advisor Prep | `{source: "waiting_room"}` |
| `advisor_prep_section_complete` | Section completed | `{section, progress}` |
| `advisor_prep_complete` | All 4 sections done | `{sections_completed, completion_time}` |
| `flag_activated` | Medical flag toggled on | `{flag_code, source, method}` |
| `flag_deactivated` | Medical flag toggled off | `{flag_code, source}` |

## 🚦 Deprecation Plan

### PFMA v2 Retirement

1. **Week 1:** Add deprecation banner to v2
2. **Week 2:** Archive `products/pfma/` → `archive/products/pfma_v2/`
3. **Week 3:** Remove nav.json route
4. **Week 4:** Delete archived files

### Feature Flag (Optional)
```python
# core/feature_flags.py
pfma_v3_enabled = True  # Default: v3 for all users
```

## ✅ Acceptance Criteria

- [x] Booking-first flow works
- [x] Cross-hub sync via MCIP
- [x] JSON-driven modules
- [x] Flag Manager integration
- [x] Pricing stack unchanged
- [x] Navi presence (one per view)
- [x] Strict validation
- [x] 19/19 tests passing
- [x] Telemetry events
- [x] Documentation complete

## 📞 Support

**Questions?**
- See: `PFMA_V3_IMPLEMENTATION_PLAN.md` (technical details)
- See: `PFMA_V3_PR_PACKAGE.md` (comprehensive PR docs)
- Run: `pytest tests/test_pfma_v3.py -v` (verify functionality)

## 🎉 Status

**✅ READY FOR PRODUCTION**

All tests passing, documentation complete, zero breaking changes.

---

**Last Updated:** October 17, 2025  
**Branch:** `revise-pfma`  
**Version:** 3.0.0
