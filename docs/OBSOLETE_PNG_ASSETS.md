# Obsolete PNG Assets - Phase 5E Cleanup

## Product Tile Images (OBSOLETE - Replaced with CSS Emoji Icons)

The following PNG files in `static/images/` are **no longer used** and can be safely deleted:

### Product Tiles (Replaced in Phase 5E)
- ✅ `cp.png` - Cost Planner (now 💰 emoji)
- ✅ `done.png` - Completion badge (now CSS checkmark ✓)
- ✅ `faq.png` - FAQ tile (tile removed in Phase 4A)
- ✅ `gcp.png` - Guided Care Plan (now 🧭 emoji)
- ✅ `pfma.png` - My Advisor (now 👥 emoji)

### Additional Service Product Tiles (Replaced in Phase 5E)
- ✅ `d_management.png` - Disease Management (now 💊 emoji)
- ✅ `dme.png` - Durable Medical Equipment (now 🦽 emoji)
- ✅ `fall.png` - Fall Risk Assessment (now 🛡️ emoji)
- ✅ `home_health.png` - Home Health (now 🏥 emoji)
- ✅ `home_safety.png` - Home Safety (icon varies by context)
- ✅ `med_manage.png` - Medication Management (icon varies by context)
- ✅ `predictive_health.png` - Predictive Health (icon varies by context)

### Planning Graphics (Context-Dependent)
- ⚠️ `planning.png` - May be used in documentation or presentations (audit before removal)

## Files to KEEP (In Active Use)

### Brand Assets
- ✅ `better-business-bureau-logo.png` - BBB accreditation badge
- ✅ `static/images/logos/cca_logo.png` - Primary brand logo

### Hero & Contextual Images
- ✅ `hero.png` - Welcome page hero image
- ✅ `contextual_someone_else.png` - Caregiver journey illustration
- ✅ `self.png` - Self-care journey illustration
- ✅ `tell_us_about_them.png` - Audience selection image
- ✅ `tell_us_about_you.png` - Audience selection image
- ✅ `welcome_self.png` - Welcome self-care variant
- ✅ `welcome_someone_else.png` - Welcome caregiver variant

### Authentication Pages
- ✅ `login.png` - Login/signup page illustration

## Removal Instructions

To safely remove obsolete PNG files:

```bash
# Navigate to static/images directory
cd static/images/

# Remove obsolete product tile images
rm -f cp.png done.png faq.png gcp.png pfma.png
rm -f d_management.png dme.png fall.png home_health.png
rm -f home_safety.png med_manage.png predictive_health.png

# Verify no active references remain
grep -r "cp\.png\|done\.png\|faq\.png\|gcp\.png\|pfma\.png" ../../ --exclude-dir=_deprecated
```

## Phase 5E Visual System

Product tiles now use:
1. **CSS emoji icons** (via `::before` pseudo-elements)
2. **Responsive scaling** (2.5rem font-size)
3. **Consistent opacity** (0.8 for visual balance)
4. **Smart fallbacks** (default 📋 emoji if no match)
5. **Conditional hiding** (no emoji if image_square exists)

See `core/styles/dashboard.css` for complete emoji icon mapping.

## Verification Steps

After removing obsolete PNGs:

1. ✅ Run app and verify all lobby tiles render with emoji icons
2. ✅ Check completed journey section shows checkmarks (not broken images)
3. ✅ Verify no 404 errors in browser console for PNG files
4. ✅ Confirm brand assets (logos, hero images) still load correctly
5. ✅ Test all product modules (GCP, Cost Planner, My Advisor, etc.)

---

**Last Updated:** 2025-10-30  
**Phase:** 5E Dynamic Personalization  
**Status:** Complete - PNG product tiles fully replaced with CSS/emoji icons
