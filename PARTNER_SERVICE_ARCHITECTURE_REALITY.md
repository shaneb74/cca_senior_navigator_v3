# Partner & Service Architecture - Current State Analysis

## Discovery Summary
After code inspection, here's what **actually exists** vs what we thought:

---

## What We Have

### 1. **Partner Registry** (`config/partners.json`)
✅ EXISTS - Partner metadata with:
- Partner details (name, category, states, image)
- Unlock requirements (`unlock_requires: ["gcp:>=50", "flag:meds_management_needed"]`)
- Primary CTA routes (`"/partner/connect?id=omcare"`)
- Lock messages for when requirements not met

**Purpose:** Data-driven partner catalog

### 2. **Partner Hub** (`hubs/partners.py`)
✅ EXISTS - Page that:
- Loads partners from `partners.json`
- Filters by search/category/state
- Shows tiles (locked/unlocked based on `unlock_requires`)
- Calls `tile_requirements_satisfied()` to check unlock status

**Purpose:** Browse/discover partners, see what's available

**KEY:** Partners are **auto-hidden** if unlock requirements not met (via `locked=True`)

### 3. **Additional Services Registry** (`core/additional_services.py`)
✅ EXISTS - Service configs with:
- Service metadata (title, subtitle, CTA)
- Partner references (`"go": "partner_omcare"`)
- Visibility conditions (`visible_when` with flag rules)
- Hub assignments

**Purpose:** Contextual service recommendations in hubs

### 4. **Partner Connect Handler** (`/partner/connect`)
❌ DOES NOT EXIST - No page/route to actually handle:
- Partner connection requests
- Lead form submission
- Scheduling/booking
- Handoff to partner

**Impact:** Partners have CTAs pointing to non-existent routes!

---

## The Architecture Gap

### Current Flow (Broken):
```
User completes GCP
  → Sets flags (meds_management_needed)
  → Goes to Partners Hub
  → Sees Omcare tile (unlocked)
  → Clicks "Schedule demo" 
  → Routes to "/partner/connect?id=omcare"
  → ❌ 404 - Route doesn't exist!
```

### What's Supposed to Happen:
```
User completes GCP
  → Sets flags
  → Additional Services shows personalized tiles
  → Clicks service tile
  → Routes to partner connect page
  → Lead capture / scheduling
  → Handoff to partner CRM
```

---

## Three Paths Forward

### **Option A: Services Display Partners (Recommended)**
**Concept:** Additional services dynamically load and filter partners from `partners.json`

**Implementation:**
```python
# core/additional_services.py
def get_additional_services(ctx, hub):
    tiles = []
    
    # Load partner registry
    partners = load_partners_json()
    
    # Filter partners based on:
    # 1. Hub assignment
    # 2. Flag-based visibility
    # 3. Unlock requirements met
    for partner in partners:
        if should_show_partner(partner, ctx, hub):
            tile = convert_partner_to_tile(partner, ctx)
            tiles.append(tile)
    
    # Add internal services
    for service in REGISTRY:
        if should_show_service(service, ctx, hub):
            tiles.append(service)
    
    return tiles
```

**Pros:**
- ✅ Single source of truth (`partners.json`)
- ✅ No duplication (partners only defined once)
- ✅ Easy to add partners (just edit JSON)
- ✅ Validation ensures partners have handlers

**Cons:**
- ⚠️ Need to build partner connect handler
- ⚠️ Two data sources (partners.json + REGISTRY)

---

### **Option B: Build Partner Connect Handler**
**Concept:** Create actual `/partner/connect` page in nav.json

**Implementation:**
```json
// nav.json
{
  "key": "partner_connect",
  "label": "Partner Connect",
  "module": "pages.partner_connect:render",
  "hidden": true
}
```

```python
# pages/partner_connect.py
def render():
    partner_id = st.query_params.get("id")
    partner_data = load_partner(partner_id)
    
    if not partner_data:
        st.error("Partner not found")
        return
    
    # Show partner details
    st.header(partner_data["name"])
    st.write(partner_data["blurb"])
    
    # Lead capture form
    with st.form("partner_connect_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        
        if st.form_submit_button("Connect"):
            # Submit to partner CRM/webhook
            submit_lead(partner_id, name, email, phone)
            st.success("Connected! Partner will reach out soon.")
```

**Pros:**
- ✅ Partners work as-is (CTAs already point to correct route)
- ✅ Central lead capture mechanism
- ✅ Easy to add integrations (webhooks, CRM)

**Cons:**
- ⚠️ Still need to solve duplication (partners.json vs REGISTRY)
- ⚠️ Requires building new page

---

### **Option C: Merge Partners into REGISTRY**
**Concept:** Remove `partners.json`, define everything in REGISTRY

**Implementation:**
```python
# core/additional_services.py
REGISTRY = [
    {
        "key": "omcare",
        "type": "partner",
        "partner_id": "omcare",  # Links to CRM/webhook config
        "title": "Omcare Medication Management",
        "category": "medication",
        "states": ["US"],
        "unlock_requires": ["gcp:complete", "flag:meds_management_needed"],
        "visible_when": [...],
        "cta": "Schedule demo",
        "handler": "partner_connect",  # Generic handler
    },
    # ... more partners
]
```

**Pros:**
- ✅ Single source of truth (only REGISTRY)
- ✅ No duplication
- ✅ Unified validation

**Cons:**
- ❌ Removes clean separation (partners.json was pure data)
- ❌ Couples partner metadata to service logic
- ❌ Loses Partner Hub (or requires rebuilding it)

---

## Recommended Solution

### **Hybrid: Option A + Option B**

**Phase 1:** Build `/partner/connect` handler
- Generic page that works for ALL partners
- Reads partner data from `partners.json`
- Shows partner details + lead capture form
- Submits to partner webhook/CRM

**Phase 2:** Additional Services loads partners
- `get_additional_services()` reads both REGISTRY and `partners.json`
- Filters partners based on unlock requirements + visibility rules
- Converts partners to service tiles
- Returns unified list

**Phase 3:** Validation ensures consistency
- Check: All partners with unlock requirements have connect handler (generic)
- Check: Service visibility rules match partner unlock requirements
- Check: No orphaned partners (partners that can't be shown anywhere)

---

## Implementation Priority

### ✅ **Immediate (Blocking Production)**
1. Build `/partner/connect` handler page
2. Add route to `nav.json`
3. Test: Partner Hub → Click partner → Lead form works

### 🟡 **Phase 2 (Enhancement)**
1. Additional Services loads partners dynamically
2. Merge partner tiles into hub service displays
3. Validate visibility vs unlock compatibility

### 🟢 **Phase 3 (Polish)**
1. Partner CRM integrations (webhooks)
2. Lead tracking/analytics
3. Partner dashboard for leads

---

## Key Insight from Your Question

> "We don't need to unlock them, we should hide them until they are unlocked, but that is also a partner tile config."

**You're right!** The current architecture already does this:
- Partners have `unlock_requires` metadata
- Partner Hub checks `tile_requirements_satisfied()`
- If requirements not met → `locked=True` → Tile shows with lock icon
- If requirements met → `locked=False` → Tile is interactive

**The issue:** Even when unlocked, clicking the tile goes to a non-existent route!

**Solution:** Build the missing `/partner/connect` handler so unlocked tiles actually work.

---

## Action Items

### For Validation System:
1. ✅ Keep orphaned partner check
2. ✅ Verify all partners with CTAs have handlers
3. 🟡 Add visibility vs unlock compatibility check
4. 🟡 Warn about state restrictions

### For Partner Architecture:
1. 🔴 **Build `/partner/connect` handler** (blocking!)
2. 🟡 Additional Services loads partners dynamically
3. 🟡 Unified service/partner display in hubs

### For You:
**Question:** Do you want to:
- **A)** Build generic `/partner/connect` handler now (quick fix)?
- **B)** Merge partners into Additional Services (architectural change)?
- **C)** Keep separate but wire them together (hybrid)?

I recommend **A** for MVP, then **C** for long-term architecture.
