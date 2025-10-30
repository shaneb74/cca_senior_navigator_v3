# Phase 5F: Visual Polish + Guided Care Plan Correction

**Status:** Complete ✅  
**Date:** October 30, 2025  
**Branch:** `feature/phase5f_visual_polish`

## Objectives

### 1. Visual Polish - Phase Gradients
Introduce elegant, minimal background gradients on product tiles based on journey phase. The design is subtle, accessible, and professional with no harsh saturation or contrast.

### 2. Guided Care Plan (GCP) Phase Correction
Correct the GCP phase mapping to properly place it in the **Planning** phase instead of Discovery.

## Changes Implemented

### 1. Schema Correction (`config/personalization_schema.json`)
**Issue:** GCP was incorrectly mapped to Discovery phase, causing confusion in journey flow.

**Fix:** Updated phases configuration:
- **Discovery phase**: Now only contains `["discovery_learning"]`
- **Planning phase**: Continues to contain all planning modules including GCP: `["gcp_v4", "learn_recommendation", "cost_v2", "pfma_v3"]`

**Rationale:** GCP is a planning tool, not a discovery/onboarding experience. Discovery Learning is the true first-touch onboarding.

### 2. Tile Structure (`hubs/hub_lobby.py`)
**Change 1 - Discovery Tiles:**
- Removed GCP tile from `_build_discovery_tiles()`
- Discovery now only contains Discovery Learning tile
- Updated docstring to reflect Phase 5F correction

**Change 2 - Planning Tiles:**
- Moved GCP tile to `_build_planning_tiles()` as first tile (order=10)
- Updated GCP phase tag from `"discovery"` to `"planning"`
- Maintained proper ordering: GCP (10) → Learn (15) → Cost (20) → Advisor (30)
- Updated docstring to reflect Phase 5F correction

### 3. Gradient CSS (`core/styles/dashboard.css`)
**Added 4 gradient classes** with subtle, accessible color transitions:

```css
.tile-gradient-discovery {
  background: linear-gradient(180deg, #E8F1FF 0%, #FFFFFF 100%);
  /* Soft blue - welcoming first-touch experience */
}

.tile-gradient-planning {
  background: linear-gradient(180deg, #EAFBF0 0%, #FFFFFF 100%);
  /* Soft green - growth and progress */
}

.tile-gradient-post_planning {
  background: linear-gradient(180deg, #F3EEFF 0%, #FFFFFF 100%);
  /* Soft violet - completion and celebration */
}

.tile-gradient-service {
  background: linear-gradient(180deg, #F7F7F7 0%, #FFFFFF 100%);
  /* Neutral gray - additional services/partners */
}
```

**Design Principles:**
- 180deg vertical gradient (top to bottom)
- Starts with subtle color (#E8-#F7 range)
- Fades to pure white (#FFFFFF)
- Maintains hover states (translateY + shadow)
- Accessible contrast ratios
- Professional, not playful

### 4. Dynamic Gradient Application (`core/product_tile.py`)
**Added automatic gradient class injection** based on tile's `phase` attribute:

```python
# Phase 5F: Add gradient class based on journey phase
if self.phase:
    classes.append(f"tile-gradient-{self.phase}")
```

**How it works:**
1. Each ProductTileHub has a `phase` attribute: `"discovery"`, `"planning"`, `"post_planning"`
2. Tile renderer automatically adds corresponding gradient class
3. CSS applies appropriate gradient based on class
4. Additional services (non-ProductTileHub) don't get gradients (by design)

## Journey Flow After Phase 5F

### Discovery Phase
**Tiles:** Discovery Learning only  
**Purpose:** First-touch onboarding and welcome experience  
**Gradient:** Soft blue (#E8F1FF → #FFFFFF)

### Planning Phase
**Tiles:** GCP → Learn Recommendation → Cost Planner → My Advisor  
**Purpose:** Core planning journey with all strategic tools  
**Gradient:** Soft green (#EAFBF0 → #FFFFFF)

### Post-Planning Phase
**Tiles:** Senior Trivia, Concierge Clinical Review  
**Purpose:** Engagement and professional review after planning complete  
**Gradient:** Soft violet (#F3EEFF → #FFFFFF)

### Additional Services
**Tiles:** Partner services (Home Health, Fall Risk, etc.)  
**Purpose:** Upsell opportunities for partner products  
**Gradient:** None (uses default tile styling)

## Verification Checklist

| Test | Expected Result | Status |
|------|----------------|--------|
| 1. Discovery tile shows soft blue gradient | Discovery Learning has #E8F1FF → #FFFFFF | ✅ |
| 2. Planning tiles show soft green gradient | GCP, Learn, Cost, Advisor have #EAFBF0 → #FFFFFF | ✅ |
| 3. Post-planning tiles show soft violet gradient | Trivia, CCR have #F3EEFF → #FFFFFF | ✅ |
| 4. GCP appears in Planning section | GCP is first planning tile (order=10) | ✅ |
| 5. Discovery only shows Discovery Learning | Discovery section has 1 tile only | ✅ |
| 6. Gradients maintain hover states | Hover still shows translateY(-2px) + shadow | ✅ |
| 7. No regressions in personalization | visible_modules still filters correctly | ✅ |
| 8. Additional services have no gradient | Partner tiles use default styling | ✅ |

## Technical Details

### Phase Attribute Mapping
```python
# Discovery tiles
phase="discovery"  # Discovery Learning

# Planning tiles
phase="planning"   # GCP, Learn Recommendation, Cost Planner, My Advisor

# Post-planning tiles
phase="post_planning"  # Senior Trivia, Concierge Clinical Review

# Additional services
phase=None  # No phase attribute (partner services)
```

### CSS Class Application
```html
<!-- Discovery tile -->
<div class="ptile dashboard-card tile--active tile--brand tile-gradient-discovery">

<!-- Planning tile -->
<div class="ptile dashboard-card tile--active tile--brand tile-gradient-planning">

<!-- Post-planning tile -->
<div class="ptile dashboard-card tile--complete tile--teal tile-gradient-post_planning">

<!-- Additional service (no gradient) -->
<div class="ptile dashboard-card tile--locked">
```

### Personalization Integration
Phase 5F gradients work seamlessly with Phase 5E personalization:
- **Tier gradients** (independent/assisted/memory_care) apply to entire dashboard-card
- **Phase gradients** apply to individual tiles based on journey position
- Both can coexist without visual conflict
- Phase gradients are MORE specific, so they override tier gradients when needed

## Files Modified

1. **config/personalization_schema.json** (+1/-1 lines)
   - Updated discovery visible_modules: `["gcp_v4"]` → `["discovery_learning"]`

2. **hubs/hub_lobby.py** (+19/-16 lines)
   - Removed GCP tile from `_build_discovery_tiles()`
   - Added GCP tile to `_build_planning_tiles()` as first tile
   - Updated phase tag on GCP tile: `"discovery"` → `"planning"`
   - Updated docstrings for both functions

3. **core/styles/dashboard.css** (+31 lines)
   - Added 4 gradient classes (discovery, planning, post_planning, service)
   - Added hover state preservations for all gradients

4. **core/product_tile.py** (+3 lines)
   - Added dynamic gradient class injection based on phase attribute

5. **docs/Phase_5F_Visual_Polish.md** (new file)
   - This documentation

## Migration Notes

### Breaking Changes
**None.** This is a purely additive visual enhancement with a structural correction.

### Backwards Compatibility
- Tiles without `phase` attribute don't get gradients (graceful fallback)
- Additional services continue to use default styling
- Existing personalization (Phase 5E) unaffected
- All navigation routes remain unchanged

### User Impact
**Positive:** 
- Clearer visual distinction between journey phases
- GCP now properly grouped with planning tools
- More intuitive journey progression
- Professional, polished appearance

**None negative.**

## Future Considerations

### Dark Mode Support
Current gradients are light-mode optimized. For dark mode support, add:
```css
@media (prefers-color-scheme: dark) {
  .tile-gradient-discovery {
    background: linear-gradient(180deg, #1A2B4A 0%, #0F1923 100%);
  }
  /* ... other gradients ... */
}
```

### Additional Phase Gradients
If new journey phases are added (e.g., `pre_discovery`, `advanced_planning`), follow the pattern:
1. Define gradient in dashboard.css
2. Add phase attribute to tiles
3. Gradient applies automatically via product_tile.py logic

### Gradient Customization Per Tier
For deeper personalization, could apply different gradient intensities per tier:
```css
.tier-independent .tile-gradient-planning {
  background: linear-gradient(180deg, #D4F5DD 0%, #FFFFFF 100%);
}
.tier-assisted .tile-gradient-planning {
  background: linear-gradient(180deg, #EAFBF0 0%, #FFFFFF 100%);
}
.tier-memory-care .tile-gradient-planning {
  background: linear-gradient(180deg, #F0FAF2 0%, #FFFFFF 100%);
}
```

## Related Documentation
- **Phase 5E Dynamic Personalization:** `docs/Phase_5E_Dynamic_Personalization.md`
- **Phase 5A Journey Tags:** (see hub_lobby.py docstrings)
- **Product Tile Architecture:** `core/product_tile.py`
- **Personalization Schema:** `config/personalization_schema.json`

---

**Implemented by:** Claude  
**Approved by:** Shane  
**Next Phase:** TBD (consider Phase 5G: Advanced Personalization or Phase 6: Production Hardening)
