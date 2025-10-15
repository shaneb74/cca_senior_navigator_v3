# Additional Services Governance System

## Problem Statement

**Current Risk:** Developers can add services to `REGISTRY` that reference partners we don't have contracts with, or create placeholder services without real fulfillment paths.

**Example of Going Rogue:**
```python
# ❌ BAD: Developer adds unvetted service
{
    "key": "mystery_service",
    "title": "Amazing New Care Solution",
    "go": "partner_nonexistent",  # ← No actual partner!
    "visible_when": [{"includes": {"path": "flags", "value": "any_flag"}}],
}
```

---

## Solution: Multi-Layer Validation

### Layer 1: Partner Registry Validation

**Enforce:** All partner services must reference actual partners in `config/partners.json`

**Implementation:**

```python
# core/service_validators.py (NEW FILE)

import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

def load_partner_registry() -> Set[str]:
    """Load all valid partner IDs from config/partners.json"""
    partners_file = Path("config/partners.json")
    if not partners_file.exists():
        return set()
    
    with partners_file.open() as f:
        partners = json.load(f)
    
    return {p["id"] for p in partners}


def validate_service_registry(services: List[Dict]) -> Tuple[bool, List[str]]:
    """Validate that all partner services reference real partners.
    
    Returns:
        (is_valid, list_of_errors)
    """
    partner_ids = load_partner_registry()
    errors = []
    
    for service in services:
        service_type = service.get("type", "partner")
        go_route = service.get("go", "")
        service_key = service.get("key", "unknown")
        
        # Partner services must reference real partners
        if service_type == "partner":
            # Extract partner ID from go route
            # Patterns: "partner_omcare", "svc_seniorlife_ai", etc.
            if go_route.startswith("partner_"):
                partner_key = go_route.replace("partner_", "")
            elif go_route.startswith("svc_"):
                partner_key = go_route.replace("svc_", "")
            else:
                partner_key = go_route
            
            # Check if partner exists
            if partner_key not in partner_ids:
                errors.append(
                    f"Service '{service_key}' references partner '{partner_key}' "
                    f"which doesn't exist in config/partners.json"
                )
        
        # Internal services must have valid routes
        elif service_type == "internal":
            if not go_route:
                errors.append(
                    f"Internal service '{service_key}' has no 'go' route defined"
                )
    
    return len(errors) == 0, errors
```

### Layer 2: Service Type Enforcement

**Enforce:** Services must declare their type and follow type-specific rules

```python
# Extended service config schema
VALID_SERVICE_TYPES = {
    "partner",      # Must reference config/partners.json
    "internal",     # Must route to internal page
    "utility",      # Built-in tools (FAQ, Learning Center)
    "placeholder"   # Explicitly marked as coming soon
}

def validate_service_types(services: List[Dict]) -> Tuple[bool, List[str]]:
    """Ensure all services have valid types."""
    errors = []
    
    for service in services:
        service_key = service.get("key", "unknown")
        service_type = service.get("type")
        
        if not service_type:
            errors.append(
                f"Service '{service_key}' missing required 'type' field. "
                f"Must be one of: {VALID_SERVICE_TYPES}"
            )
        elif service_type not in VALID_SERVICE_TYPES:
            errors.append(
                f"Service '{service_key}' has invalid type '{service_type}'. "
                f"Must be one of: {VALID_SERVICE_TYPES}"
            )
        
        # Placeholders must have deployment_status
        if service_type == "placeholder":
            if "deployment_status" not in service:
                errors.append(
                    f"Placeholder service '{service_key}' must include "
                    f"'deployment_status' field (e.g., 'coming_soon', 'in_negotiation')"
                )
    
    return len(errors) == 0, errors
```

### Layer 3: Deployment Gates

**Enforce:** Services require approval flags to be visible in production

```python
# In additional_services.py REGISTRY, add deployment control

{
    "key": "new_partner_service",
    "type": "partner",
    "title": "New Partner",
    "go": "partner_newpartner",
    "deployment_status": "staging",  # ← NEW: Controls production visibility
    "approval_date": "2025-10-20",   # ← NEW: When approved for production
    "contract_id": "CNT-2025-042",   # ← NEW: Links to contract
    "visible_when": [...],
}

# In get_additional_services()
def get_additional_services(hub: str, limit: Optional[int] = None) -> List[Tile]:
    # ... existing code ...
    
    for tile in REGISTRY:
        # Production gate: Check deployment status
        if not _is_production_ready(tile):
            continue  # Skip services not approved for production
        
        # ... rest of filtering logic ...
```

```python
def _is_production_ready(tile: Dict) -> bool:
    """Check if service is approved for production deployment."""
    
    # Check deployment status
    status = tile.get("deployment_status", "production")
    
    # In development mode, show all services
    if st.session_state.get("dev_mode", False):
        return True
    
    # In production, only show approved services
    if status not in ["production", "live"]:
        return False
    
    # Optional: Check approval date
    approval_date = tile.get("approval_date")
    if approval_date:
        from datetime import datetime
        approved = datetime.fromisoformat(approval_date)
        if datetime.now() < approved:
            return False  # Not yet approved
    
    return True
```

### Layer 4: Startup Validation

**Run validation checks at app startup (in dev mode)**

```python
# In app.py, add service validation

if st.session_state.get("dev_mode", False):
    from core.service_validators import (
        validate_service_registry,
        validate_service_types
    )
    from core.additional_services import REGISTRY
    
    # Validate partner references
    is_valid, errors = validate_service_registry(REGISTRY)
    if not is_valid:
        st.error("⚠️ ADDITIONAL SERVICES VALIDATION FAILED:")
        for error in errors:
            st.error(f"  • {error}")
    
    # Validate service types
    is_valid, errors = validate_service_types(REGISTRY)
    if not is_valid:
        st.error("⚠️ SERVICE TYPE VALIDATION FAILED:")
        for error in errors:
            st.error(f"  • {error}")
```

---

## Updated Service Schema (With Governance)

```python
# REQUIRED FIELDS for all services
{
    "key": str,                    # Unique identifier
    "type": str,                   # "partner" | "internal" | "utility" | "placeholder"
    "title": str,                  # Display name
    "go": str,                     # Route or partner ID
    "visible_when": List[Rule],    # Visibility rules
    
    # GOVERNANCE FIELDS (for partners)
    "deployment_status": str,      # "staging" | "production" | "deprecated"
    "approval_date": str,          # ISO date when approved
    "contract_id": str,            # Reference to partner contract
    "partner_contact": str,        # Email of partner liaison
    
    # OPTIONAL FIELDS
    "subtitle": str,
    "cta": str,
    "order": int,
    "hubs": List[str],
    "tags": List[str],
}
```

---

## Approval Workflow

### Step 1: Developer Adds Service (Staging)
```python
{
    "key": "new_care_service",
    "type": "partner",
    "deployment_status": "staging",  # ← NOT visible in production
    "go": "partner_newcare",
    "title": "New Care Service",
    # ... rest of config
}
```

### Step 2: Partner Contract Signed
- Update `config/partners.json` with partner details
- Add `contract_id` to service config

### Step 3: QA Testing in Dev Mode
- Enable dev mode: `?dev=true`
- Test service visibility, routing, and user flow
- Verify partner integration works

### Step 4: Production Approval
```python
{
    "key": "new_care_service",
    "type": "partner",
    "deployment_status": "production",  # ← NOW visible in production
    "approval_date": "2025-10-20",
    "contract_id": "CNT-2025-042",
    "go": "partner_newcare",
    # ...
}
```

---

## CLI Validation Tool

```bash
# Validate all services before deployment
python3 -m core.service_validators

# Output:
# ============================================================
# ADDITIONAL SERVICES VALIDATION
# ============================================================
# Partner References: ✅ PASS (all partners exist)
# Service Types: ✅ PASS (all types valid)
# Deployment Status: ✅ PASS (all production services approved)
# 
# Services by Status:
#   - Production: 8
#   - Staging: 2
#   - Deprecated: 0
# ============================================================
```

---

## Benefits

| Layer | Prevents | How |
|-------|----------|-----|
| **Partner Registry** | Referencing non-existent partners | Validates against `config/partners.json` |
| **Type Enforcement** | Ambiguous service categories | Requires explicit type declaration |
| **Deployment Gates** | Unapproved services in production | Requires `deployment_status: "production"` |
| **Startup Validation** | Catching errors before users see them | Runs checks in dev mode on app load |

---

## Example: Catching Rogue Service

### Developer Adds This:
```python
{
    "key": "mystery_ai_tool",
    "type": "partner",
    "title": "Mystery AI Care Tool",
    "go": "partner_mysteryai",  # ← Doesn't exist!
    "deployment_status": "production",
    "visible_when": [{"includes": {"path": "flags", "value": "any_flag"}}],
}
```

### Validation Catches It:
```
❌ SERVICE VALIDATION FAILED:
  • Service 'mystery_ai_tool' references partner 'mysteryai' 
    which doesn't exist in config/partners.json

ACTION REQUIRED:
  1. Add partner to config/partners.json with contract details, OR
  2. Change deployment_status to "staging" until partner is onboarded, OR
  3. Remove service from REGISTRY
```

---

## Enforcement Checklist

- [ ] Create `core/service_validators.py`
- [ ] Add `deployment_status` field to all partner services
- [ ] Add `contract_id` field linking to partner contracts
- [ ] Run validation in `app.py` dev mode startup
- [ ] Create CLI tool: `python3 -m core.service_validators`
- [ ] Document approval workflow in NEW_PRODUCT_QUICKSTART.md
- [ ] Add pre-commit hook to run validation
- [ ] Create partner onboarding checklist template

---

## Summary

**Problem:** Developers could add services without real partners  
**Solution:** Multi-layer validation + deployment gates  
**Result:** All production services guaranteed to have:
- ✅ Real partner in config/partners.json
- ✅ Valid contract reference
- ✅ Explicit approval for production
- ✅ Validated type and routing

**Rogue services are blocked at:** Development → Validation → Staging → Production gate
