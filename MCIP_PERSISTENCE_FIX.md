# MCIP Persistence Fix

**Date:** October 14, 2025  
**Issue:** KeyError: 'journey' when loading app with session persistence  
**Status:** ✅ Fixed  
**Commit:** c050af5

## Problem

When session persistence was enabled, the app crashed on startup with:
```python
KeyError: 'journey'
  File "core/mcip.py", line 297, in get_journey_progress
    journey = st.session_state[cls.STATE_KEY]["journey"]
```

## Root Cause

1. **session_store** was persisting the entire `mcip` key to disk
2. On app restart, partial MCIP state loaded from disk
3. MCIP state might have contracts but missing `journey` or `events` keys
4. `MCIP.initialize()` checked if key exists but didn't validate structure
5. Hub tried to access `journey` → KeyError

## Solution

### Separation of Concerns

**Contracts** (should persist):
- `care_recommendation` - From GCP
- `financial_profile` - From Cost Planner
- `advisor_appointment` - From PFMA

**Runtime State** (should NOT persist):
- `journey` - Derived from progress + contracts
- `events` - Event log (transient)
- Internal tracking - Reconstructed on load

### Implementation

#### 1. Session Store Changes

```python
# Before
USER_PERSIST_KEYS = {
    'mcip',  # ❌ Entire MCIP state
    ...
}

# After
USER_PERSIST_KEYS = {
    'mcip_contracts',  # ✅ Only contracts
    ...
}
```

#### 2. MCIP Initialization

```python
@classmethod
def initialize(cls) -> None:
    # Create default structure
    default_state = {...}
    
    if cls.STATE_KEY not in st.session_state:
        # Fresh init
        st.session_state[cls.STATE_KEY] = default_state
        
        # Restore contracts from persistence
        if "mcip_contracts" in st.session_state:
            contracts = st.session_state["mcip_contracts"]
            st.session_state[cls.STATE_KEY]["care_recommendation"] = contracts.get("care_recommendation")
            # ... restore other contracts
    else:
        # Fill in missing keys (defensive)
        for key in default_state:
            if key not in existing:
                existing[key] = default_state[key]
```

#### 3. Contract Persistence

```python
@classmethod
def _save_contracts_for_persistence(cls) -> None:
    """Save contracts to mcip_contracts key for session_store."""
    st.session_state["mcip_contracts"] = {
        "care_recommendation": st.session_state[cls.STATE_KEY].get("care_recommendation"),
        "financial_profile": st.session_state[cls.STATE_KEY].get("financial_profile"),
        "advisor_appointment": st.session_state[cls.STATE_KEY].get("advisor_appointment"),
    }

# Called in all publish methods:
def publish_care_recommendation(cls, recommendation):
    st.session_state[cls.STATE_KEY]["care_recommendation"] = asdict(recommendation)
    cls._save_contracts_for_persistence()  # ← Save for persistence
    ...
```

## Persistence Flow

### Before Fix
```
1. GCP completes → MCIP.publish_care_recommendation()
2. MCIP stores in st.session_state["mcip"]["care_recommendation"]
3. session_store saves entire st.session_state["mcip"] to disk
   ↓ (includes journey, events, everything)
4. App restart
5. session_store loads entire "mcip" from disk
6. Partial structure loaded (maybe missing journey)
7. Hub calls MCIP.get_journey_progress()
8. ❌ KeyError: 'journey'
```

### After Fix
```
1. GCP completes → MCIP.publish_care_recommendation()
2. MCIP stores in st.session_state["mcip"]["care_recommendation"]
3. MCIP calls _save_contracts_for_persistence()
4. Contracts saved to st.session_state["mcip_contracts"]
5. session_store saves only "mcip_contracts" to disk
   ↓ (clean contracts only, no runtime state)
6. App restart
7. session_store loads "mcip_contracts" from disk
8. MCIP.initialize() creates fresh structure
9. MCIP.initialize() restores contracts from "mcip_contracts"
10. Journey/events reconstructed from contracts + progress
11. Hub calls MCIP.get_journey_progress()
12. ✅ Works! Journey exists with correct structure
```

## Testing

### Test 1: Fresh Start
```bash
python clear_data.py --clear-all
streamlit run app.py
# ✅ MCIP initializes with defaults
```

### Test 2: Complete GCP → Restart
```bash
streamlit run app.py
# Complete GCP assessment
# Check: .cache/session_*.json and data/users/anon_*.json created
# Restart app (Ctrl+C, then streamlit run app.py)
# ✅ Care recommendation preserved, hub shows correct status
```

### Test 3: Partial State Load
```bash
# Manually edit data/users/anon_*.json
# Add partial mcip_contracts (only care_recommendation, no financial_profile)
streamlit run app.py
# ✅ MCIP initializes properly, fills in missing keys
```

## Benefits

1. **Crash Prevention** - Defensive initialization prevents KeyError
2. **Clean Separation** - Contracts vs runtime state clearly separated
3. **Smaller Files** - Only contracts persisted (not events/journey)
4. **Correct Reconstruction** - Journey derived from source of truth (progress + contracts)
5. **Migration Safe** - Handles both old (full mcip) and new (mcip_contracts) formats

## Files Changed

- `core/session_store.py` - Changed USER_PERSIST_KEYS
- `core/mcip.py` - Enhanced initialize(), added _save_contracts_for_persistence()

## Backward Compatibility

If user has old format (full `mcip` in persistence):
- ✅ Still works - initialize() fills in missing keys defensively
- Next save will use new format (mcip_contracts)
- Old format gradually phased out

## Related

- Session persistence: `SESSION_PERSISTENCE_IMPLEMENTATION.md`
- MCIP architecture: (original MCIP design docs)
- Testing guide: `SESSION_PERSISTENCE_TESTING_GUIDE.md`
