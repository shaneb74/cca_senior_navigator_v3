# V2 System Implementation Status

> **Unified architecture for GCP v4, Cost Planner v2, PFMA v2, and MCIP v2**

---

## Phase 1: Foundation ✅ COMPLETE

### What We Built

**MCIP Core (`core/mcip.py`)**
- MCIP conductor class - sees all hubs, manages journey
- Data contracts: CareRecommendation, FinancialProfile, AdvisorAppointment
- State management in `st.session_state["mcip"]`
- Helper methods: publish/get recommendations, unlock products, track completion

**Event System (`core/mcip_events.py`)**
- MCIPEventBus for pub/sub pattern
- Default listeners for recommendation, flags, financial, appointment events
- Integrated with app.py at startup

**Status**: ✅ Committed (commit 19fd2c8)

---

## Phase 2: GCP v4 Integration 🔄 IN PROGRESS

### Architecture Document ✅ COMPLETE

**GCP_V4_ARCHITECTURE.md** (commit edd781b)
- Preserves JSON-driven module architecture
- Updates logic.py output to match CareRecommendation schema
- Adds structured flags with CTAs
- Product layer publishes to MCIP
- Migration strategy for parallel v3/v4 operation

### Implementation Plan

**Next Steps (Ready to Build):**

1. **Create Directory Structure**
   ```
   products/gcp_v4/
   ├── __init__.py
   ├── product.py (new - MCIP publishing)
   └── modules/
       └── care_recommendation/
           ├── __init__.py
           ├── module.json (copy from v3)
           ├── config.py (copy from v3)
           ├── logic.py (update output format)
           └── flags.py (new - flag schema)
   ```

2. **Files to Create**
   - `flags.py` - Flag definitions with CTAs
   - `product.py` - MCIP publishing layer
   - Update `logic.py` - Return CareRecommendation-compatible dict

3. **Files to Copy (Unchanged)**
   - `module.json` - Questions already work
   - `config.py` - Module config loader already works

4. **Register Route**
   - Add `gcp_v4` to config/nav.json (hidden: true for testing)

**Estimated Time**: 2-3 hours

---

## Phase 3: Cost Planner v2 📋 PENDING

### Architecture Documents ✅ COMPLETE

- **COST_PLANNER_V2_ARCHITECTURE.md** - 86% code reduction strategy
- **COST_PLANNER_V2_STATUS.md** - Implementation tracking
- **COST_PLANNER_V2_QUICKSTART.md** - Developer guide
- **COST_PLANNER_V2_AUTH_INTEGRATION.md** - Auth flow patterns

### Core Extensions ✅ COMPLETE

- `core/modules/registry.py` - Custom step renderers
- `core/modules/hub.py` - ModuleHub component
- `core/modules/loader.py` - Module discovery

### Implementation Plan

**Pending**:
1. Update `core/modules/engine.py` to support custom renderers
2. Create `products/cost_planner_v2/` structure
3. Implement module hub with GCP gate
4. Create 6 financial modules
5. Publish FinancialProfile to MCIP

**Estimated Time**: 1 week

---

## Phase 4: PFMA v2 📞 PENDING

### Architecture Document ✅ COMPLETE

**PFMA_V2_ARCHITECTURE_VISION.md**
- Declarative step-driven funnel
- PFMAState helper for clean state management
- Step shell components (breadcrumbs, duck gamification)
- 62% code reduction

### Implementation Plan

**Pending**:
1. Create `products/pfma_v2/pfma_steps.json` schema
2. Implement `products/pfma_v2/engine.py` step runner
3. Create layout components
4. Publish AdvisorAppointment to MCIP

**Estimated Time**: 1 week

---

## Phase 5: Hub Integration 🏠 PENDING

### Updates Needed

**Concierge Hub (`hubs/concierge.py`)**
- Read MCIP for product unlocking
- Read MCIP for completion status
- Apply silver gradient to recommended tile
- Never read product state directly

**Other Hubs**
- Subscribe to MCIP events for flag-based content

**Estimated Time**: 2-3 days

---

## Integration Contracts

### Data Flows

```
GCP v4 → publishes CareRecommendation → MCIP
                                          ↓
Cost Planner v2 ← reads care_recommendation ← MCIP
Cost Planner v2 → publishes FinancialProfile → MCIP
                                          ↓
PFMA v2 ← reads care_recommendation + financial ← MCIP
PFMA v2 → publishes AdvisorAppointment → MCIP
                                          ↓
All Hubs ← read journey/unlocking/completion ← MCIP
```

### Event Flow

```
MCIP.publish_care_recommendation()
  ↓
mcip.recommendation.updated event fired
  ↓
Hub guide refreshes
Product tiles update (unlocking, gradient)
Cost Planner gate opens
  ↓
User continues to Cost Planner
```

---

## Testing Strategy

### Unit Tests
- [x] MCIP state management
- [ ] GCP v4 logic.py output
- [ ] Cost Planner v2 aggregation
- [ ] PFMA v2 step validation

### Integration Tests
- [ ] GCP → MCIP → Cost Planner flow
- [ ] Cost Planner → MCIP → PFMA flow
- [ ] Hub unlocking logic
- [ ] Event emission and handling

### Persona Tests
- [ ] Independent living path
- [ ] In-home care path
- [ ] Assisted living path
- [ ] Memory care path

### End-to-End Tests
- [ ] Complete user journey (all three products)
- [ ] Flag-based routing
- [ ] Low confidence handling
- [ ] Resume/replay functionality

---

## Migration Strategy

### Parallel Operation

During development, all systems run in parallel:

| Product | v1 Route | v2 Route | Status |
|---------|----------|----------|--------|
| GCP | `?page=gcp` | `?page=gcp_v4` | v4 in dev |
| Cost Planner | `?page=cost` | `?page=cost_v2` | v2 in dev |
| PFMA | `?page=pfma` | `?page=pfma_v2` | v2 not started |

### Cutover Plan

1. **GCP v4** - First to cutover (publishes to MCIP)
2. **Cost Planner v2** - Second (reads MCIP, publishes financial)
3. **PFMA v2** - Third (reads MCIP, completes journey)
4. **Hubs** - Updated throughout to read MCIP

### Feature Flags

```python
# In environment or config
USE_MCIP_V2 = os.getenv("MCIP_V2_ENABLED", "false") == "true"
USE_GCP_V4 = os.getenv("GCP_V4_ENABLED", "false") == "true"
USE_COST_V2 = os.getenv("COST_V2_ENABLED", "false") == "true"
```

---

## Success Metrics

### Code Quality
- ✅ MCIP core: 425 lines (foundation complete)
- ⏳ GCP v4: ~150 lines new code (logic.py + product.py)
- ⏳ Cost Planner v2: 86% reduction (1,160 → 120 lines)
- ⏳ PFMA v2: 62% reduction (400 → 150 lines)

### Architecture
- ✅ Clean boundaries (MCIP → Hubs → Products → Modules)
- ✅ Single source of truth (st.session_state["mcip"])
- ✅ Event-driven updates
- ⏳ No cross-product state reads

### User Experience
- ⏳ Identical UX (no visual changes)
- ⏳ Faster navigation (MCIP orchestration)
- ⏳ Better recommendations (structured flags)
- ⏳ Seamless journey (auto-unlocking)

---

## Current Branch Status

**Branch**: `feature/cost_planner_v2`

**Commits**:
1. `7ff2773` - Core module extensions (registry, hub, loader)
2. `dbeded4` - Cost Planner v2 status doc
3. `478da5c` - Cost Planner v2 quickstart
4. `f787385` - Auth integration docs
5. `6fe6ca5` - PFMA v2 + MCIP v2 architecture docs
6. `19fd2c8` - MCIP v2 core implementation ✅
7. `edd781b` - GCP v4 architecture doc ✅

**Files Changed**: 13 new/modified files, 4,700+ lines added

---

## Next Immediate Action

**Start GCP v4 Implementation:**

1. Create directory: `products/gcp_v4/modules/care_recommendation/`
2. Implement `flags.py` with FLAGS_SCHEMA
3. Copy `module.json` and `config.py` from v3
4. Update `logic.py` output format
5. Create `product.py` with MCIP publishing
6. Register route in `config/nav.json`
7. Test publishing to MCIP

**Once GCP v4 works**: Cost Planner v2 can read from MCIP!

---

## Questions or Blockers?

None currently. Architecture is solid, foundation is built, next steps are clear.

**Ready to implement GCP v4!** 🚀
