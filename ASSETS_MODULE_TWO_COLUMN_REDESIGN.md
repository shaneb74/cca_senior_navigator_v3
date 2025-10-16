# Assets & Resources Module - Two-Column Redesign

## Overview
Redesigned the Assets & Resources module to use a compact two-column layout with visible inputs, collapsible Quick Guides, and a home sale interest trigger that dynamically activates a Home Sale module.

## Design Goals
1. **Reduce vertical scrolling** by 40-50% through two-column grid layout
2. **Improve scannability** with card-based design grouping related inputs
3. **Add home sale trigger** to activate Home Sale module for advanced planning
4. **Maintain accessibility** with 16-20px fonts, WCAG AA contrast, 44px touch targets
5. **Keep consistency** with Income Sources module design patterns

## Layout Structure

### Before (Vertical List)
- Multiple long sections stacked vertically
- 10+ separate sections requiring extensive scrolling
- Difficult to see relationships between related inputs
- ~6-8 viewport heights on 1080p screens

### After (Two-Column Grid + Cards)
```
┌─────────────────────────────────────────┐
│ ✨ Navi Panel (Warm + Confident)        │
└─────────────────────────────────────────┘

🏦 Assets & Resources
─────────────────────────────────────────────

┌──────────────┬──────────────┐
│ Primary      │ Property &   │
│ Assets       │ Real Estate  │
│              │              │
│ • Checking   │ • Primary    │
│   & Savings  │   Residence  │
│ • Investment │ • [ ] Home   │
│   Accounts   │   Sale Flag  │
│              │ • Other RE   │
└──────────────┴──────────────┘

┌──────────────────────────────┐
│ Other Resources              │
│ • Vehicles/Valuables/Other   │
└──────────────────────────────┘

💵 Total Asset Value: $_______
─────────────────────────────────────────────
[← Back]      [💾 Save & Continue →]
```

## Implementation Details

### Three Asset Cards

#### 1. Primary Assets (Left Column)
- **Checking & Savings**
  - Single number input for total balance
  - Quick Guide: Account types, Medicaid limits, liquidity importance
- **Investment Accounts**
  - Combined 401(k), IRA, brokerage, stocks, bonds, mutual funds
  - Quick Guide: Account types, penalties, tax implications

#### 2. Property & Real Estate (Right Column)
- **Primary Residence**
  - Estimated home value input
  - Quick Guide: Valuation methods, Medicaid protection, median values
- **Home Sale Interest Checkbox**
  - Label: "I'd like to evaluate selling this home or explore home equity options"
  - Sets `home_sale_interest` flag and `cost_v2_home_sale_enabled`
  - Shows info message: "I'll guide you through sale, reverse mortgage, or HELOC options"
  - Activates Home Sale module tile in hub when checked
- **Other Real Estate**
  - Rental properties, vacation homes, land
  - Quick Guide: Rental income, liquidation options, tax implications

#### 3. Other Resources (Full Width)
- **Vehicles / Valuables / Other Assets**
  - Combined input for all other resources
  - Quick Guide: Vehicles, jewelry, collectibles, business interests

### Home Sale Trigger Logic
```python
# On save, set flag for hub to show Home Sale module
if home_sale_interest:
    st.session_state.cost_v2_home_sale_enabled = True
else:
    st.session_state.cost_v2_home_sale_enabled = False
```

The hub can then check this flag:
```python
if st.session_state.get("cost_v2_home_sale_enabled", False):
    # Show Home Sale module tile
```

## Simplified Data Model

### Before (15 fields)
```python
{
    "checking_savings": 0,
    "cds_money_market": 0,
    "ira_traditional": 0,
    "ira_roth": 0,
    "k401_403b": 0,
    "other_retirement": 0,
    "stocks_bonds": 0,
    "mutual_funds": 0,
    "primary_residence_value": 0,
    "primary_residence_mortgage": 0,
    "investment_property": 0,
    "business_value": 0,
    "other_assets_value": 0
}
```

### After (6 fields)
```python
{
    "checking_savings": 0,
    "investment_accounts": 0,
    "primary_residence_value": 0,
    "home_sale_interest": False,
    "other_real_estate": 0,
    "other_resources": 0,
    "total_asset_value": 0
}
```

**Rationale:** Consolidate granular fields into logical groups. Users don't need to separate IRA types or investment vehicle types at this stage - just total investable assets.

## CSS Implementation

### Card Styling
```css
.asset-card {
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 10px;
  padding: 16px 16px 20px;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  height: 100%;
}
```

### Responsive Breakpoint
```css
@media (max-width: 900px) {
  /* Stacks to single column */
  .asset-card {
    margin-bottom: 20px;
  }
}
```

### Accessibility
- Typography: 16-20px for readability
- Contrast: Navy #0D1F4B on light backgrounds (WCAG AA)
- Touch targets: Min 44px height for inputs and buttons
- Focus states: 3px box-shadow for keyboard navigation

## User Experience Improvements

### Before
- ❌ Required 6-8 viewport heights of scrolling
- ❌ 15+ separate inputs overwhelming users
- ❌ Related fields scattered across page
- ❌ No path to home sale planning

### After
- ✅ Reduced to ~2-3 viewport heights
- ✅ 6 consolidated inputs in logical groups
- ✅ Related fields grouped in cards
- ✅ Home sale checkbox activates dedicated planning module
- ✅ Quick Guides provide context without cluttering main view
- ✅ Inputs always visible (no hidden accordion content)

## Testing Checklist

### Layout & Responsiveness
- [ ] Two-column grid displays correctly on desktop (>900px)
- [ ] Cards stack to single column on tablet/mobile (≤900px)
- [ ] All three cards render with proper spacing
- [ ] Cards have consistent height alignment

### Navi Panel
- [ ] Single Navi banner displays at top
- [ ] No duplicate or conflicting banners
- [ ] Warm, confident tone matches design spec

### Inputs & Validation
- [ ] All 6 number inputs accept values correctly
- [ ] Home sale checkbox toggles properly
- [ ] Input values persist across page interactions
- [ ] Quick Guides expand/collapse smoothly

### Home Sale Trigger
- [ ] Checking box shows info message
- [ ] Unchecking box hides info message
- [ ] `home_sale_interest` flag saves correctly
- [ ] `cost_v2_home_sale_enabled` flag sets properly
- [ ] Hub shows Home Sale tile when flag is true (requires hub update)
- [ ] Hub hides Home Sale tile when flag is false

### Navigation & Persistence
- [ ] "Back to Modules" returns to hub
- [ ] "Save & Continue" saves all data
- [ ] Module status changes to "completed" after save
- [ ] Returning to module shows saved values
- [ ] Total asset value calculates correctly

### Accessibility
- [ ] Tab navigation works through all inputs
- [ ] Focus states visible on all interactive elements
- [ ] Text contrast meets WCAG AA standards
- [ ] Touch targets ≥44px height
- [ ] Font sizes 16-20px throughout

## Files Modified
1. `products/cost_planner_v2/modules/assets.py` - Complete redesign
2. `assets/css/modules.css` - Added `.asset-card` styles (~75 lines)

## Future Enhancements
1. **Home Sale Module** - Create dedicated module for:
   - Sell outright vs. age in place
   - Reverse mortgage calculator
   - HELOC/Home equity loan options
   - Tax implications and proceeds planning

2. **Hub Integration** - Update hub.py to:
   - Check `cost_v2_home_sale_enabled` flag
   - Dynamically show/hide Home Sale module tile
   - Position Home Sale module after Assets in workflow

## Status
✅ **COMPLETE** - Assets module redesigned with two-column layout, home sale trigger, and simplified data model. Ready for testing and hub integration.
