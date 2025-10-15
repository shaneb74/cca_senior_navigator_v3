# Dynamic Partner Integration - Complete Solution

## Summary
Implemented dynamic partner loading from `partners.json` into Additional Services. Partners are now data-driven with flag-based unlock requirements, eliminating hardcoded partner tiles in REGISTRY.

---

## Architecture

### Data Flow:
```
1. User completes GCP
   ↓
2. GCP sets flags (e.g., moderate_dependence, chronic_present)
   ↓
3. Flags saved to MCIP
   ↓
4. get_additional_services() called
   ↓
5. Loads partners from partners.json
   ↓
6. Checks unlock_requires against GCP progress + flags
   ↓
7. Converts unlocked partners to service tiles
   ↓
8. Merges with static services from REGISTRY
   ↓
9. Returns personalized service tiles
```

---

## Implementation Details

### 1. Partner Loading (`_load_partners()`)
```python
def _load_partners() -> List[Dict[str, Any]]:
    """Load partner configurations from partners.json."""
    # Reads config/partners.json
    # Returns list of partner dicts
```

### 2. Unlock Logic (`_parse_unlock_requirement()`)
Supports multiple requirement formats:

#### GCP Progress:
- `"gcp:complete"` → GCP must be 100% complete
- `"gcp:>=50"` → GCP must be at least 50% complete

#### Flag-Based (OR Logic):
- `"flag:moderate_dependence"` → Single flag must be True
- `"flag:flag1|flag2|flag3"` → ANY flag must be True

#### Combined (AND Logic):
```json
"unlock_requires": [
  "gcp:complete",  // AND
  "flag:moderate_dependence|high_dependence|chronic_present"  // AND (any of these)
]
```

### 3. Partner Conversion (`_convert_partner_to_tile()`)
Converts partner JSON to service tile format:

**Input (partners.json):**
```json
{
  "id": "omcare",
  "name": "Omcare",
  "headline": "Home Health & Medication Management Hub",
  "unlock_requires": ["gcp:complete", "flag:moderate_dependence|..."],
  "primary_cta": {"label": "Schedule demo", "route": "/partner/connect?id=omcare"}
}
```

**Output (service tile):**
```python
{
  "key": "partner_omcare",
  "type": "partner",
  "title": "Omcare",
  "subtitle": "Home Health & Medication Management Hub",
  "cta": "Schedule demo",
  "go": "/partner/connect?id=omcare",
  "order": 500,
  "personalization": "personalized",
  "partner_id": "omcare"
}
```

### 4. Integration (`get_additional_services()`)
```python
def get_additional_services(hub: str = "concierge", limit: Optional[int] = None):
    # 1. Load partners from partners.json
    partners = _load_partners()
    
    # 2. Filter to only Omcare and SeniorLife.AI (for now)
    for partner in partners:
        if partner_id not in ["omcare", "seniorlife_ai"]:
            continue
        
        # 3. Check unlock requirements
        if not _partner_unlocked(partner, ctx):
            continue
        
        # 4. Convert to tile and add to results
        tiles.append(_convert_partner_to_tile(partner, order))
    
    # 5. Add static services from REGISTRY (skip hardcoded partners)
    for tile in REGISTRY:
        if tile.get("key") not in ["omcare", "seniorlife_ai"]:
            tiles.append(tile)
    
    return sorted(tiles)
```

---

## Current Configuration

### Omcare (11 Medication Flags)
**File:** `config/partners.json`

```json
"unlock_requires": [
  "gcp:complete",
  "flag:moderate_dependence|high_dependence|chronic_present|geo_isolated|
   moderate_cognitive_decline|severe_cognitive_risk|no_support|
   high_mobility_dependence|mild_cognitive_decline|moderate_mobility|limited_support"
]
```

**Triggers on:**
- ✅ ADL/IADL dependence (medication management)
- ✅ Chronic conditions (medication regimens)
- ✅ Cognitive decline (adherence risk)
- ✅ Lack of caregiver support
- ✅ Mobility limitations (pharmacy access)
- ✅ Geographic isolation (medication delivery)

### SeniorLife.AI (7 Fall/Cognitive Flags)
**File:** `config/partners.json`

```json
"unlock_requires": [
  "gcp:complete",
  "flag:falls_multiple|moderate_safety_concern|high_safety_concern|
   mild_cognitive_decline|moderate_cognitive_decline|severe_cognitive_risk|
   mental_health_concern"
]
```

**Triggers on:**
- ✅ Fall risk (any level)
- ✅ Cognitive decline (any stage)
- ✅ Mental health/behavioral concerns

---

## What Was Removed

### From `core/additional_services.py` REGISTRY:
- ❌ Hardcoded `omcare` service definition
- ❌ Hardcoded `seniorlife_ai` service definition

These are now dynamically loaded from `partners.json` instead.

### Still in REGISTRY (Not Partners):
- ✅ Internal products (Cost Planner, PFMA)
- ✅ Utility services (Learning Center, FAQ)
- ✅ Placeholder services (commented out)

---

## Benefits

### 1. **Single Source of Truth**
- Partners defined once in `partners.json`
- Used by both Partner Hub AND Additional Services
- No duplication between files

### 2. **Data-Driven Configuration**
- Add new partners by editing JSON (no code changes)
- Update unlock requirements without touching Python
- Partner metadata (rating, tags, CTAs) centralized

### 3. **Flag-Based Personalization**
- Partners automatically show when flags are set
- Supports complex OR logic within requirements
- AND logic across multiple requirements

### 4. **Scalable Architecture**
- Easy to add more partners (just edit JSON)
- Easy to enable partners (remove `if partner_id not in` filter)
- Clear separation: data (JSON) vs logic (Python)

---

## Testing

### Manual Test Flow:
1. ✅ Complete GCP with medication complexity
2. ✅ Check flags set: `moderate_dependence`, `chronic_present`, etc.
3. ✅ Navigate to Concierge Hub
4. ✅ Verify Omcare tile appears in Additional Services
5. ✅ Verify "✨ Personalized for You" label shows
6. ✅ Verify blue gradient overlay
7. ✅ Click tile → Routes to `/partner/connect?id=omcare`

### Validation:
```bash
# Check flag usage
python3 -m core.validators

# Check partner/service alignment
python3 -m core.service_validators
```

---

## Future Enhancements

### Phase 1 (Current): ✅
- [x] Dynamic partner loading from JSON
- [x] Flag-based unlock requirements
- [x] Omcare and SeniorLife.AI integrated
- [x] Personalization labels and gradients

### Phase 2 (Next):
- [ ] Enable all 6 partners dynamically (remove filter)
- [ ] Build `/partner/connect` handler page
- [ ] Lead capture form integration
- [ ] Partner CRM webhooks

### Phase 3 (Future):
- [ ] Geographic filtering (state-based unlock)
- [ ] Partner rating display on tiles
- [ ] A/B testing for partner recommendations
- [ ] Partner analytics dashboard

---

## Configuration Files

### `config/partners.json`
- Partner metadata (name, category, image, CTAs)
- Unlock requirements (GCP progress + flags)
- Lock messages
- Tags and ratings

### `core/additional_services.py`
- Dynamic partner loading logic
- Unlock requirement parsing
- Partner-to-tile conversion
- Service tile registry (non-partner services)

### `core/flags.py`
- Central flag registry (20 flags)
- Flag validation
- Flag aggregation from MCIP

---

## How to Add New Partner

### 1. Get Contract Signed ✍️

### 2. Add to `config/partners.json`:
```json
{
  "id": "new_partner",
  "name": "New Partner Inc",
  "category": "service_type",
  "states": ["US"],
  "image_square": "logos/new_partner.png",
  "headline": "What they do",
  "blurb": "Longer description",
  "tags": ["Tag1", "Tag2"],
  "unlock_requires": [
    "gcp:complete",
    "flag:relevant_flag1|relevant_flag2"
  ],
  "lock_msg": "Complete GCP to unlock",
  "primary_cta": {
    "label": "Connect",
    "route": "/partner/connect?id=new_partner"
  },
  "rating": 4.5
}
```

### 3. Update `get_additional_services()`:
```python
# Remove filter to enable all partners
# if partner_id not in ["omcare", "seniorlife_ai"]:
#     continue
```

### 4. Test:
```bash
# Validate configuration
python3 -m core.service_validators

# Manual test
streamlit run app.py
```

---

## Status
✅ **COMPLETE** - Dynamic partner integration working
- Omcare: 11 flag triggers
- SeniorLife.AI: 7 flag triggers
- Partners loaded from JSON
- Personalization working
- Gradients and labels showing

**Next:** Build `/partner/connect` handler page
