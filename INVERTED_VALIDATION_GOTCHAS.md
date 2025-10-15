# Inverted Validation Architecture - Gotchas & Solutions

## Architecture Overview
**Partner-Driven Model:** Partners define unlock requirements, services register to handle them.
**Key Validation:** Ensure no "orphaned partners" (partners users can unlock but can't access).

---

## Potential Gotchas

### 1. Route Matching Ambiguity ⚠️ MEDIUM RISK
**Problem:** Multiple route formats could reference same partner
```python
# Partner CTA
"primary_cta": {"route": "/partner/connect?id=omcare"}

# Service could use:
"go": "partner_omcare"  # Prefixed
"go": "omcare"          # Direct
"go": "/partner/connect?id=omcare"  # Full URL
```

**Impact:** Validator might not recognize match → false positive "orphaned partner"

**Solutions:**
- **Quick Fix:** Standardize on ONE format (e.g., always `partner_{id}`)
- **Robust Fix:** Enhance `extract_partner_key()` to normalize all variants
```python
def extract_partner_key(go_route: str) -> Optional[str]:
    # Handle all variants, return normalized partner ID
    if "id=" in go_route:
        return go_route.split("id=")[-1]
    # ... other patterns
```

**Status:** ✅ IMPLEMENTED - `extract_partner_key()` handles multiple formats

---

### 2. Dynamic/Wildcard Routes 🔮 FUTURE RISK
**Problem:** Service handles multiple partners via pattern
```python
# Generic handler
{"key": "telehealth_hub", "go": "/partner/telehealth/{partner_id}"}
```

**Impact:** Validator won't detect wildcard handler → reports false orphans

**Solutions:**
- **Option A:** Explicit metadata
```python
{"key": "telehealth_hub", "handles_partners": ["omcare", "teladoc", "mdlive"]}
```
- **Option B:** Pattern matching in validator
```python
if "{partner_id}" in service_route:
    # Matches all partners in category
```

**Status:** 🟡 NOT IMPLEMENTED - Add if dynamic routes become a pattern

---

### REALITY CHECK: Current State
**Discovery:** Partners in `config/partners.json` have CTAs pointing to `/partner/connect?id=...` but:
- ❌ NO `/partner/connect` route handler exists in `nav.json`
- ❌ NO actual page to handle partner connections
- ✅ Services in REGISTRY reference partners (e.g., `"go": "partner_omcare"`)
- ✅ BUT services are also just tiles, not actual delivery mechanisms

**Implication:** Right now, partners are **display-only** - they show unlock status but clicking through goes nowhere!

**Solution Path:**
1. **Option A - Simple:** Services ARE the partner tiles (merge them)
2. **Option B - Full:** Build actual `/partner/connect` handler page
3. **Option C - Hybrid:** Additional services filter and display partner tiles from `partners.json`

---

### 3. Service Visibility vs Partner Unlocks ⚠️ HIGH RISK  
**Problem:** Partner unlocks at 50% GCP, service only shows at 100%
```json
// Partner
"unlock_requires": ["gcp:>=50"]

// Service
"visible_when": "gcp:complete AND flags.meds_management_needed"
```

**Impact:** User sees partner tile, clicks, service isn't available → broken experience

**Solutions:**
- **Validation Rule:** Service visibility must be LESS OR EQUAL restrictive than partner unlock
- **Runtime Check:** Before showing partner, verify service is actually visible
```python
def validate_visibility_compatibility(partner, service):
    # Parse unlock_requires and visible_when
    # Ensure service.visible_when is subset of partner.unlock_requires
```

**Status:** 🔴 NOT IMPLEMENTED - **CRITICAL for v2**

---

### 4. Geographic Restrictions Mismatch ⚠️ MEDIUM RISK
**Problem:** Partner has state restrictions, service doesn't check
```json
{"id": "omcare", "states": ["CA", "NY", "TX"]}
```

**Impact:** FL user sees partner, clicks, gets "not available in your state" error

**Solutions:**
- **Option A:** Service inherits partner's state restrictions
```python
if partner_data.get("states"):
    if user_state not in partner_data["states"]:
        hide_service()
```
- **Option B:** Add geographic rules to service `visible_when`
```python
"visible_when": "user.state in ['CA', 'NY', 'TX']"
```

**Status:** 🟡 NOT IMPLEMENTED - Add geographic filtering to `get_additional_services()`

---

### 5. CTA Route vs Service Route Divergence 🐛 LOW RISK
**Problem:** Partner CTA goes to one place, service goes elsewhere
```json
// Partner
"primary_cta": {"route": "/partner/connect?id=omcare"}

// Service
"go": "/products/medication_mgmt"  // Different!
```

**Impact:** Validation passes but they don't actually connect

**Solutions:**
- Add route equivalence check
```python
def validate_route_equivalence(partner_route, service_route):
    partner_id = extract_from_route(partner_route)
    service_id = extract_from_route(service_route)
    return partner_id == service_id
```

**Status:** 🟡 NOT IMPLEMENTED - Consider for strict mode

---

### 6. External Links with Unlock Requirements 🤔 UX ISSUE
**Problem:** Partner has external link but requires GCP completion
```json
{
    "unlock_requires": ["gcp:>=50"],
    "primary_cta": {"route": "https://external.com/article"}
}
```

**Impact:** User must do work just to see an external link (frustrating)

**Solutions:**
- **Validation Warning:** Flag this pattern as potential UX issue
```python
if route.startswith("http") and unlock_requires:
    warnings.append(f"Partner '{name}' is external link but has unlock requirements")
```

**Status:** 🟡 NOT IMPLEMENTED - Add to validation warnings

---

### 7. Circular Service Dependencies 🔄 LOW RISK
**Problem:** Service A unlocks B, B unlocks A
```python
{"key": "service_a", "visible_when": "flags.service_b_complete"}
{"key": "service_b", "visible_when": "flags.service_a_complete"}
```

**Impact:** Deadlock - neither ever shows

**Solutions:**
- Build dependency graph validator (like flag validators)
```python
def detect_circular_dependencies(services):
    # Parse visible_when conditions
    # Build directed graph
    # Check for cycles
```

**Status:** 🔴 NOT IMPLEMENTED - Consider if complex conditional logic grows

---

## Implementation Priorities

### Phase 1 (Current) ✅
- [x] Basic orphaned partner detection
- [x] Route extraction with multiple format support
- [x] Partner coverage report

### Phase 2 (Critical) 🔴
- [ ] **Service visibility vs partner unlock compatibility check**
- [ ] Geographic filtering in `get_additional_services()`
- [ ] External link + unlock requirements warning

### Phase 3 (Enhancement) 🟡
- [ ] Dynamic route pattern matching
- [ ] Strict CTA route equivalence check
- [ ] Circular dependency detection

---

## Testing Scenarios

### Test Case 1: Orphaned Partner
```json
// partners.json
{"id": "new_partner", "unlock_requires": ["gcp:>=50"]}

// REGISTRY - empty (no service handles it)
```
**Expected:** ❌ Validation fails with "ORPHANED PARTNER" error

### Test Case 2: Route Format Variants
```python
# Partner CTA
"route": "/partner/connect?id=omcare"

# Services using different formats
"go": "partner_omcare"  ✅ Should match
"go": "omcare"          ✅ Should match
"go": "/partner/connect?id=omcare"  ✅ Should match
```
**Expected:** ✅ All recognized as handling same partner

### Test Case 3: Visibility Mismatch
```json
// Partner
"unlock_requires": ["gcp:>=50"]

// Service
"visible_when": "gcp:complete AND flags.high_needs"
```
**Expected:** ⚠️ Warning - service MORE restrictive than partner

### Test Case 4: External Link with Unlock
```json
{
    "id": "educational_resource",
    "unlock_requires": ["gcp:complete"],
    "primary_cta": {"route": "https://external.com/guide"}
}
```
**Expected:** ⚠️ Warning - external link shouldn't require unlock

---

## Architecture Decision Records

### ADR-001: Why Inverted Validation?
**Context:** Need to prevent "rogue services" - services we can't deliver
**Decision:** Validate partners have service handlers, not vice versa
**Rationale:** 
- Partner = user-facing promise ("we offer this")
- Service = delivery mechanism ("we can fulfill this")
- User sees partner → Must be able to access it
- Orphaned partner = broken user experience

**Alternatives Considered:**
- Forward validation (services must reference real partners) - Doesn't prevent orphans
- Manual review only - Human error prone
- Runtime-only checks - Catches errors too late

### ADR-002: External Link Exception
**Context:** Some partners are just educational content (NCOA, articles)
**Decision:** Skip validation for external links (routes starting with "http")
**Rationale:** We're not "delivering" external content, just linking to it
**Caveat:** Should warn if external link has unlock requirements (UX smell)

### ADR-003: Service Type Enforcement
**Context:** Need to distinguish partner services from internal features
**Decision:** Require explicit `type` field on all services
**Rationale:** Makes intent clear, enables type-specific validation rules

---

## Conclusion

**Overall Assessment:** ✅ Architecturally sound concept with manageable gotchas

**Biggest Risks:**
1. 🔴 **Service visibility vs partner unlock mismatch** - Could ship
2. ⚠️ Geographic restrictions not enforced at service level
3. 🟡 Future: Dynamic routes need pattern matching

**Recommendation:**
- ✅ **Ship Phase 1** (current implementation) for orphaned partner detection
- 🔴 **Phase 2 REQUIRED** before production: Visibility compatibility check
- 🟡 **Phase 3** as enhancement: Pattern matching, circular dependency detection

**Next Steps:**
1. Run validation: `python3 -m core.service_validators`
2. Fix any orphaned partners found
3. Implement Phase 2 visibility compatibility check
4. Add to CI/CD pipeline (pre-commit hook)
