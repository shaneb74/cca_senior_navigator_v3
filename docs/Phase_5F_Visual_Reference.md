# Phase 5F Visual Reference Guide

## Phase Gradient Color Palette

### Discovery Phase
**Color:** Soft Blue  
**Hex:** `#E8F1FF` → `#FFFFFF`  
**Emotion:** Welcoming, Clear, Trustworthy  
**Tiles:** Discovery Learning

```
┌─────────────────────────────────┐
│  ░░░░░░░░ DISCOVERY ░░░░░░░░░   │  ← #E8F1FF (very light blue)
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░    │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░      │
│  ░░░░░░░░░░░░░░░░░░░░░░         │
│                                  │  ← #FFFFFF (pure white)
└─────────────────────────────────┘
```

### Planning Phase
**Color:** Soft Green  
**Hex:** `#EAFBF0` → `#FFFFFF`  
**Emotion:** Growth, Progress, Action  
**Tiles:** GCP, Learn Recommendation, Cost Planner, My Advisor

```
┌─────────────────────────────────┐
│  ░░░░░░░░ PLANNING ░░░░░░░░░░   │  ← #EAFBF0 (very light green)
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░    │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░      │
│  ░░░░░░░░░░░░░░░░░░░░░░         │
│                                  │  ← #FFFFFF (pure white)
└─────────────────────────────────┘
```

### Post-Planning Phase
**Color:** Soft Violet  
**Hex:** `#F3EEFF` → `#FFFFFF`  
**Emotion:** Celebration, Completion, Reflection  
**Tiles:** Senior Trivia, Concierge Clinical Review

```
┌─────────────────────────────────┐
│  ░░░░░░ POST-PLANNING ░░░░░░░   │  ← #F3EEFF (very light violet)
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░    │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░      │
│  ░░░░░░░░░░░░░░░░░░░░░░         │
│                                  │  ← #FFFFFF (pure white)
└─────────────────────────────────┘
```

### Additional Services
**Color:** Neutral Gray  
**Hex:** `#F7F7F7` → `#FFFFFF`  
**Emotion:** Utility, Professional, Optional  
**Tiles:** Partner services (currently not implemented - reserved for future)

```
┌─────────────────────────────────┐
│  ░░░░░░ ADDITIONAL ░░░░░░░░░░   │  ← #F7F7F7 (very light gray)
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░    │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░      │
│  ░░░░░░░░░░░░░░░░░░░░░░         │
│                                  │  ← #FFFFFF (pure white)
└─────────────────────────────────┘
```

## Journey Flow Visualization

```
┌──────────────────────────────────────────────────────────────┐
│                      LOBBY JOURNEY MAP                        │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  🏁 DISCOVERY PHASE                   [Soft Blue Gradient]   │
│     ┌─────────────────────────────────┐                      │
│     │ 🎓 Discovery Learning           │                      │
│     │    Welcome & Onboarding         │                      │
│     └─────────────────────────────────┘                      │
│                      ↓                                        │
│  📋 PLANNING PHASE                    [Soft Green Gradient]  │
│     ┌─────────────────────────────────┐                      │
│     │ 🧭 Guided Care Plan             │ ← MOVED FROM DISC.   │
│     │    Explore care options         │                      │
│     └─────────────────────────────────┘                      │
│                      ↓                                        │
│     ┌─────────────────────────────────┐                      │
│     │ 💡 Learn About My Recommendation│                      │
│     │    Understand your option       │                      │
│     └─────────────────────────────────┘                      │
│                      ↓                                        │
│     ┌─────────────────────────────────┐                      │
│     │ 💰 Cost Planner                 │                      │
│     │    Financial planning           │                      │
│     └─────────────────────────────────┘                      │
│                      ↓                                        │
│     ┌─────────────────────────────────┐                      │
│     │ 👥 My Advisor                   │                      │
│     │    Schedule meeting             │                      │
│     └─────────────────────────────────┘                      │
│                      ↓                                        │
│  🎉 POST-PLANNING PHASE               [Soft Violet Gradient] │
│     ┌─────────────────────────────────┐                      │
│     │ 🎮 Senior Trivia                │                      │
│     │    Brain games & engagement     │                      │
│     └─────────────────────────────────┘                      │
│                                                               │
│     ┌─────────────────────────────────┐                      │
│     │ ⚕️ Concierge Clinical Review    │                      │
│     │    Professional care review     │                      │
│     └─────────────────────────────────┘                      │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## CSS Implementation

### Gradient Classes
```css
/* Discovery */
.tile-gradient-discovery {
  background: linear-gradient(180deg, #E8F1FF 0%, #FFFFFF 100%);
}

/* Planning */
.tile-gradient-planning {
  background: linear-gradient(180deg, #EAFBF0 0%, #FFFFFF 100%);
}

/* Post-Planning */
.tile-gradient-post_planning {
  background: linear-gradient(180deg, #F3EEFF 0%, #FFFFFF 100%);
}

/* Additional Services (future use) */
.tile-gradient-service {
  background: linear-gradient(180deg, #F7F7F7 0%, #FFFFFF 100%);
}
```

### Applied HTML Example
```html
<!-- Discovery tile -->
<div class="ptile dashboard-card tile--brand tile-gradient-discovery">
  <span class="phase-pill discovery">Discovery</span>
  <div class="ptile__head">
    <span class="emoji-icon">🎓</span>
    <h3>Start Your Discovery Journey</h3>
  </div>
</div>

<!-- Planning tile -->
<div class="ptile dashboard-card tile--brand tile-gradient-planning">
  <span class="phase-pill planning">Planning</span>
  <div class="ptile__head">
    <span class="emoji-icon">🧭</span>
    <h3>Guided Care Plan</h3>
  </div>
</div>
```

## Accessibility Notes

### Color Contrast
All gradients fade to pure white (#FFFFFF), ensuring:
- Text remains readable throughout gradient
- No accessibility violations (WCAG AA compliant)
- Subtle visual distinction without overwhelming users

### Gradient Start Colors
- **Discovery (#E8F1FF):** Very light blue, ~98% lightness
- **Planning (#EAFBF0):** Very light green, ~98% lightness
- **Post-Planning (#F3EEFF):** Very light violet, ~98% lightness
- **Service (#F7F7F7):** Very light gray, ~97% lightness

### Visual Hierarchy
Gradients are intentionally subtle to:
1. Provide wayfinding without distraction
2. Maintain professional appearance
3. Support journey flow understanding
4. Avoid visual fatigue for older users

## Design Rationale

### Why These Colors?
- **Blue (Discovery):** Universally associated with trust, clarity, and beginnings
- **Green (Planning):** Represents growth, progress, and taking action
- **Violet (Post-Planning):** Signifies completion, reflection, and wisdom
- **Gray (Service):** Neutral, utility-focused, non-journey-critical

### Why 180deg Vertical Gradient?
- Natural reading direction (top-to-bottom)
- Suggests forward movement/progress
- More elegant than horizontal gradients
- Works better with variable tile heights

### Why Fade to White?
- Maintains clean, professional look
- Ensures text readability throughout
- Allows other visual elements (emoji, badges) to stand out
- Prevents visual clutter

## Browser Compatibility

### Gradient Support
- ✅ Chrome 26+ (100% support)
- ✅ Firefox 16+ (100% support)
- ✅ Safari 7+ (100% support)
- ✅ Edge 12+ (100% support)

### Fallback
If gradients fail to load (extremely rare), tiles default to `background: #ffffff` from base `.dashboard-card` class.

## Testing Checklist

- [ ] Discovery Learning shows soft blue gradient
- [ ] GCP shows soft green gradient (now in planning)
- [ ] Learn Recommendation shows soft green gradient
- [ ] Cost Planner shows soft green gradient
- [ ] My Advisor shows soft green gradient
- [ ] Senior Trivia shows soft violet gradient
- [ ] Clinical Review shows soft violet gradient
- [ ] Additional services show no gradient (default white)
- [ ] Hover states work on all gradient tiles
- [ ] Gradients don't interfere with phase pills
- [ ] Gradients don't interfere with emoji icons
- [ ] Gradients don't interfere with completion badges
- [ ] Mobile responsive (gradients scale correctly)

---

**Created:** October 30, 2025  
**Phase:** 5F Visual Polish  
**Status:** Complete ✅
