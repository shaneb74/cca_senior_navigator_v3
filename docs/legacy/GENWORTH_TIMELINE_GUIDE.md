# Genworth-Style Timeline Visualization

## Overview
The Expert Review module now features a Genworth-inspired 30-year timeline visualization that replaces the percentage-based progress bar. This design emphasizes **years of coverage** over numeric precision, providing emotional reassurance through visual storytelling.

---

## 🎯 Design Philosophy

**Inspired by:** Genworth Cost of Care Calculator  
**Goal:** Transform financial clarity into emotional reassurance  
**Approach:** Fixed-horizon timeline that visually expands as users add funding sources

**Key Principles:**
- **Security over time** (not percentages)
- **Analytical but friendly** (measured, reassuring tone)
- **Visual progress** (users literally see their future stabilize)
- **Consistent comparisons** (30-year fixed horizon for all users)

---

## 📊 Visual Components

### Timeline Bar Structure

```
┌─────────────────────────────────────────────────────────────┐
│  Yellow (Income)  │  Green (Assets)  │  Gray (Gap)          │
│  ◄── 9.8 years ──►│ ◄─ 3.5 years ──► │ ◄─── 16.7 years ───►│
└─────────────────────────────────────────────────────────────┘
 0y   5y   10y   15y   20y   25y   30y
```

**Color Scheme:**
- **Yellow Gradient** (#fbbf24 → #f59e0b): Income coverage
- **Green Gradient** (#34d399 → #10b981): Asset coverage  
- **Gray** (#e5e7eb): Funding gap

**Year Markers:**
- Subtle ticks every 5 years (0, 5, 10, 15, 20, 25, 30)
- Light gray color (#6b7280) for non-intrusive guidance

---

## 💬 Dynamic Headlines

### Example Variations

**No Assets Selected (Income Only, 43% coverage):**
```
"Your current income provides partial coverage"
Coverage from Income
```

**Liquid Assets Added (9.8 years total):**
```
"Your income and liquid assets fund care for 9 years, 9 months"
Coverage from Income and Liquid Assets
```

**Liquid + Retirement (13.3 years):**
```
"Your income, liquid assets, and retirement accounts fund care for 13 years, 3 months"
Coverage from Income, Liquid Assets, and Retirement Accounts
```

**Fully Funded (30+ years):**
```
"Your resources fully fund care for 30+ years"
Coverage from Income, Liquid Assets, and Retirement Accounts
```

---

## 🗣️ Navi Messaging (Genworth Tone)

### Tier-Based Guidance

**Tier 1: Fully Funded (30+ years)**
- **Title:** "Excellent Financial Position"
- **Message:** *"Excellent. Your income and resources cover your care for 30 years or more."*
- **Tone:** Confident, celebrating achievement

**Tier 2: Very Strong (15-29 years)**
- **Title:** "Strong Financial Security"
- **Message:** *"You're in good shape. Your resources fund care for nearly two decades."*
- **Tone:** Reassuring, positive

**Tier 3: Moderate (5-14 years)**
- **Title:** "Solid Financial Foundation"
- **Message (with assets):** *"Good progress. Adding resources extends your coverage meaningfully."*
- **Message (without assets):** *"Your income provides a strong foundation. Adding available resources can extend your plan."*
- **Tone:** Encouraging, actionable

**Tier 4: Limited (< 5 years)**
- **Title:** "Planning Opportunity"
- **Message (with assets):** *"You're making progress. Consider additional resources to strengthen your long-term plan."*
- **Message (without assets):** *"Your income provides a foundation. Adding available resources can extend your coverage."*
- **Tone:** Measured, supportive (never anxious)

---

## ⚙️ Technical Implementation

### Function: `_calculate_timeline_segments(analysis, selected_assets)`

**Purpose:** Calculate timeline segments for visualization

**Returns:**
```python
{
    "income_years": 9.8,        # Years covered by income alone
    "asset_years": 3.5,         # Additional years from assets
    "total_years": 13.3,        # Total coverage duration
    "timeline_max": 30,         # Fixed horizon
    "exceeds_timeline": False   # Whether total >= 30 years
}
```

**Logic:**
1. Calculate total coverage with selected assets (`extended_runway`)
2. Calculate coverage with no assets (income only baseline)
3. Subtract to get asset contribution
4. Cap at 30-year maximum
5. Flag if exceeds timeline for "30+" display

**Edge Cases:**
- **No gap (indefinite coverage):** Returns timeline_max for all segments
- **No assets selected:** income_years = extended_runway, asset_years = 0
- **Exceeds 30 years:** Caps at 30, sets exceeds_timeline = True

---

## 🎨 HTML/CSS Structure

```html
<div style="padding: 24px; ...">
  <!-- Headline -->
  <div>
    <div style="font-size: 16px; ...">{headline}</div>
    <div style="font-size: 13px; ...">{coverage_label}</div>
  </div>
  
  <!-- Timeline Bar -->
  <div style="position: relative; height: 50px; ...">
    <!-- Income segment (yellow) -->
    <div style="width: {income_pct}%; background: linear-gradient(90deg, #fbbf24, #f59e0b); ..."></div>
    
    <!-- Asset segment (green) -->
    <div style="left: {income_pct}%; width: {asset_pct}%; background: linear-gradient(90deg, #34d399, #10b981); ..."></div>
    
    <!-- Gap segment (gray) -->
    <div style="left: {total_pct}%; width: {gap_pct}%; background: #e5e7eb; ..."></div>
    
    <!-- Year markers -->
    <div style="position: absolute; ...">
      <span>0y</span>
      <span>5y</span>
      ...
      <span>30y</span>
    </div>
  </div>
  
  <!-- Legend -->
  <div style="display: flex; gap: 20px; ...">
    <div>
      <div style="background: linear-gradient(90deg, #fbbf24, #f59e0b); ..."></div>
      <span>Income Coverage (9.8 years)</span>
    </div>
    <div>
      <div style="background: linear-gradient(90deg, #34d399, #10b981); ..."></div>
      <span>Assets Coverage (3.5 years)</span>
    </div>
    <div *ngIf="gap_pct > 0">
      <div style="background: #e5e7eb; ..."></div>
      <span>Funding Gap</span>
    </div>
  </div>
</div>
```

**Key CSS Properties:**
- `transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1)` - Smooth animations
- `position: absolute` - Layered segments
- `border-radius: 8px` - Soft, friendly corners
- `box-shadow: inset 0 2px 4px rgba(0,0,0,0.08)` - Subtle depth

---

## 🔄 Interactive Behavior

### Checkbox Toggle Flow

1. **User checks "Retirement Accounts"**
   - Session state updated: `expert_review_selected_assets["retirement_accounts"] = True`
   - `st.rerun()` triggered

2. **Page Reloads**
   - `_calculate_timeline_segments()` called with new selections
   - New segments: income = 9.8y, assets = 3.5y → **total = 13.3y**
   - Timeline bar animates from 9.8y to 13.3y (smooth 0.6s transition)

3. **Dynamic Updates**
   - Headline: *"...fund care for 13 years, 3 months"*
   - Label: *"Coverage from Income, Liquid Assets, and Retirement Accounts"*
   - Navi: *"Good progress. Adding resources extends your coverage meaningfully."*
   - Legend: Updates asset years (0y → 3.5y)

4. **Visual Feedback**
   - Green segment expands (width: 0% → 11.7%)
   - Gray segment shrinks (gap reduces)
   - No flicker or delay
   - All elements update simultaneously

---

## 📐 Example Scenarios

### Scenario 1: Mary (43% income coverage, $1.27M assets)

**Initial State (Liquid + Retirement checked):**
```
Timeline: ████████████████░░░░░░░░░░░░░░  (13.3 / 30 years)
          ◄─ Yellow ─►◄─ Green ─►◄─ Gray ─►
Headline: "Your income, liquid assets, and retirement accounts fund care for 13 years, 3 months"
Navi: "Good progress. Adding resources extends your coverage meaningfully."
```

**Uncheck Retirement:**
```
Timeline: ████████████░░░░░░░░░░░░░░░░░░  (9.8 / 30 years)
          ◄─ Yellow ─►◄─ Gray ──────────►
Headline: "Your income and liquid assets fund care for 9 years, 9 months"
Navi: "Your income provides a strong foundation. Adding available resources can extend your plan."
```

**Uncheck All:**
```
Timeline: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  (0 / 30 years)
          ◄────────── Gray ──────────────►
Headline: "Your current income provides partial coverage"
Navi: "Your income provides a foundation. Adding available resources can extend your coverage."
```

### Scenario 2: High-Income User (90% coverage, $500K assets)

**Initial State:**
```
Timeline: ████████████████████████████░░  (28 / 30 years)
          ◄───────── Yellow ─────────►◄ Gray
Headline: "Your income funds care for 28 years"
Navi: "You're in good shape. Your resources fund care for nearly two decades."
```

**Add Liquid Assets:**
```
Timeline: ██████████████████████████████  (30+ / 30 years)
          ◄── Yellow ──►◄─── Green ────►
Headline: "Your resources fully fund care for 30+ years"
Navi: "Excellent. Your income and resources cover your care for 30 years or more."
```

---

## 🎯 Benefits

### For Users
- **Intuitive:** Years more relatable than percentages
- **Reassuring:** Visual expansion shows progress
- **Clear:** Color-coded sources easy to understand
- **Actionable:** See immediate impact of adding assets
- **Emotional:** "Future stabilizes" creates positive feeling

### For Developers
- **Maintainable:** Clean calculation function
- **Scalable:** Works for any number of asset types
- **Testable:** Pure function with predictable outputs
- **Flexible:** Easy to adjust horizon or add features

### For Product
- **Differentiated:** Unique vs. competitors
- **Professional:** Genworth-quality visualization
- **Engaging:** Interactive timeline invites exploration
- **Educational:** Users learn about funding sequencing

---

## 🧪 Testing Checklist

- [ ] **Indefinite coverage (no gap):** Shows full 30-year bar, yellow only
- [ ] **Income only (43%):** Shows yellow segment, large gray gap
- [ ] **With liquid assets:** Green segment appears, gray shrinks
- [ ] **With all assets (30+):** Full bar, "30+" headline
- [ ] **Toggle checkbox:** Smooth 0.6s animation, no flicker
- [ ] **Legend updates:** Years display correctly for each segment
- [ ] **Navi messages:** Change appropriately by tier
- [ ] **Headline grammar:** Correct singular/plural (year vs years)
- [ ] **Year markers:** Aligned correctly at 5-year intervals
- [ ] **Mobile responsive:** Timeline readable on small screens

---

## 🔮 Future Enhancements

### Potential Additions
1. **Hover tooltips:** Show exact values on segment hover
2. **Interactive markers:** Click year markers to see cost at that point
3. **Comparison view:** Toggle between current plan and "what-if" scenarios
4. **Animation options:** Let users enable/disable transitions
5. **Custom horizon:** Allow users to set 20, 30, or 40-year view
6. **Milestone indicators:** Show life expectancy, planned moves, etc.
7. **Funding sequence:** Visual representation of which assets to use when

### Accessibility Improvements
- Add ARIA labels for screen readers
- Keyboard navigation for timeline segments
- High-contrast mode support
- Text-only alternative view

---

## 📊 Analytics Opportunities

Track user engagement:
- Time spent viewing timeline
- Number of asset toggles per session
- Which combinations users explore most
- Correlation between timeline view and application completion

---

## 🤝 Alignment with Genworth

This implementation borrows Genworth's:
- **Fixed timeline horizon** (consistent framing)
- **Years of coverage focus** (vs. dollar amounts)
- **Measured tone** (confident, never anxious)
- **Visual storytelling** (see your future stabilize)
- **Professional polish** (soft gradients, smooth animations)

While maintaining Senior Navigator's:
- **Conversational Navi** (friendly guide)
- **Card-based layout** (clean white backgrounds)
- **Dynamic asset selection** (interactive planning)
- **Comprehensive context** (all metrics visible)

---

## 📝 Commit Reference

**Commit:** f408bd7  
**Branch:** genworth  
**Files Modified:** products/cost_planner_v2/expert_review.py  
**Lines Changed:** +146 / -34

**Functions Added:**
- `_calculate_timeline_segments(analysis, selected_assets)` - Timeline calculation logic

**Functions Modified:**
- `_render_navi_guidance()` - Genworth-style measured messaging
- `_render_financial_summary_banner()` - Timeline HTML/CSS rendering

---

**Created:** October 20, 2025  
**Author:** Shane (with GitHub Copilot)  
**Status:** ✅ Complete and ready for testing
