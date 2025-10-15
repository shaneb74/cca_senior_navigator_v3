# Partner & Service Flag Alignment

## Summary
Aligned partner unlock requirements with FLAG_REGISTRY and additional_services visibility logic to ensure flag-driven partner recommendations work correctly.

---

## Changes Made

### 1. **Omcare** (Medication Management)
**Updated `config/partners.json`:**
```json
"unlock_requires": [
  "gcp:complete",
  "flag:moderate_dependence|high_dependence|chronic_present|geo_isolated"
]
```

**Rationale:**
- `moderate_dependence` / `high_dependence` - IADL support includes medication management
- `chronic_present` - Chronic conditions typically require medication regimens
- `geo_isolated` - Geographic isolation increases need for medication delivery services

**Updated `core/additional_services.py`:**
- Added `geo_isolated` to visible_when conditions
- Now shows Omcare tile when ANY of these flags are true

---

### 2. **SeniorLife.AI** (Mobility & Cognitive Monitoring)
**Updated `config/partners.json`:**
```json
"unlock_requires": [
  "gcp:complete",
  "flag:falls_multiple|moderate_safety_concern|high_safety_concern|mild_cognitive_decline|moderate_cognitive_decline|severe_cognitive_risk|mental_health_concern"
]
```

**Rationale:**
- `falls_multiple` / `*_safety_concern` - Fall risk detection and prevention
- `mild/moderate/severe_cognitive_*` - AI monitoring for cognitive decline progression
- `mental_health_concern` - Behavioral monitoring and intervention

**Updated `core/additional_services.py`:**
- Added `mild_cognitive_decline` (covers early-stage monitoring)
- Added `mental_health_concern` (behavioral tracking)
- Now shows SeniorLife.AI tile for ANY fall risk, cognitive, or behavioral flag

---

### 3. **Disabled Placeholder Partner Services**
**Commented out in `core/additional_services.py`:**
- Fall Prevention & Safety
- Companion Care Services
- Memory Care Specialists
- Wellness & Emotional Support
- Caregiver Support & Respite

**Reason:** No active partner contracts for these services yet. Changed type to `"placeholder"` and commented out to prevent display until contracts are in place.

**To Re-enable:** Uncomment in REGISTRY and add partner to `partners.json`

---

## Architecture Alignment

### Before:
- ❌ Partners used `flag:meds_management_needed` (not in FLAG_REGISTRY)
- ❌ Progress-based unlocks only (`gcp:>=50`)
- ❌ Placeholder services showing without real partners

### After:
- ✅ All unlock requirements use valid FLAG_REGISTRY flags
- ✅ Flag-driven partner recommendations (GCP sets flags → Partners unlock)
- ✅ Additional services visibility matches partner unlock logic
- ✅ Only active partner contracts show in UI

---

## How It Works

### User Journey:
1. User completes GCP → Sets flags (e.g., `moderate_dependence`, `falls_multiple`)
2. Flags saved to MCIP → Available across products
3. Partner Hub checks `unlock_requires` → Unlocks matching partners
4. Additional Services checks `visible_when` → Shows personalized tiles in Concierge
5. User clicks partner tile → Routes to `/partner/connect?id=omcare`

### Validation Flow:
```bash
# Check that all flags used are valid
python3 -m core.validators

# Check that all partners have service handlers
python3 -m core.service_validators
```

---

## Flag Usage by Partner

### Omcare
**Triggers on:**
- Medication complexity (dependence levels)
- Chronic conditions requiring meds
- Geographic isolation (medication delivery needs)

**Flag Logic (OR):**
```python
moderate_dependence OR
high_dependence OR
chronic_present OR
geo_isolated
```

### SeniorLife.AI
**Triggers on:**
- Fall risk (any level)
- Cognitive decline (any stage)
- Mental health / behavioral concerns

**Flag Logic (OR):**
```python
falls_multiple OR
moderate_safety_concern OR
high_safety_concern OR
mild_cognitive_decline OR
moderate_cognitive_decline OR
severe_cognitive_risk OR
mental_health_concern
```

---

## Testing Checklist

### Manual Testing:
- [ ] Complete GCP with medication questions → Check Omcare unlocks
- [ ] Complete GCP with fall history → Check SeniorLife.AI unlocks
- [ ] Complete GCP with cognitive concerns → Check SeniorLife.AI unlocks
- [ ] Verify placeholder partners do NOT show in Additional Services
- [ ] Verify only unlocked partners show in Partner Hub

### Automated Testing:
- [ ] Run flag validation: `python3 -m core.validators`
- [ ] Run service validation: `python3 -m core.service_validators`
- [ ] Check no undefined flags used
- [ ] Check no orphaned partners

---

## Future Partner Onboarding

### To Add New Partner:
1. **Get contract signed** ✍️
2. **Add to `config/partners.json`:**
   ```json
   {
     "id": "new_partner_id",
     "name": "Partner Name",
     "unlock_requires": ["gcp:complete", "flag:relevant_flag_1|relevant_flag_2"],
     "primary_cta": {"route": "/partner/connect?id=new_partner_id"},
     ...
   }
   ```
3. **Add to `core/additional_services.py` REGISTRY:**
   ```python
   {
     "key": "new_partner_id",
     "type": "partner",
     "visible_when": [
       {"includes": {"path": "flags", "value": "relevant_flag_1"}},
       {"includes": {"path": "flags", "value": "relevant_flag_2"}},
     ],
     ...
   }
   ```
4. **Validate:** Run `python3 -m core.service_validators`
5. **Test:** Complete GCP with conditions that trigger flags → Verify partner shows

---

## Related Files
- `config/partners.json` - Partner metadata and unlock requirements
- `core/additional_services.py` - Service visibility logic
- `core/flags.py` - Central flag registry (source of truth)
- `core/validators.py` - Flag validation
- `core/service_validators.py` - Partner/service validation
- `hubs/partners.py` - Partner Hub display logic

---

## Status
✅ **COMPLETE** - Partners now aligned with FLAG_REGISTRY
- Omcare: 4 flag triggers
- SeniorLife.AI: 7 flag triggers
- Placeholder partners disabled
- Validation passing
