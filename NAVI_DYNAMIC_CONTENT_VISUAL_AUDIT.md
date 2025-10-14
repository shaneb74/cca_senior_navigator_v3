# Navi Dynamic Content - Visual Design Audit

**Date:** October 14, 2025  
**Purpose:** Comprehensive review of all Navi dynamic content elements for design optimization  
**Branch:** feature/cost_planner_v2

---

## Executive Summary

Navi currently displays **8 major types of dynamic content** across two primary contexts (Hub and Product pages). This audit documents each element's current placement, visual treatment, data sources, and recommendations for improved hierarchy and user experience.

---

## Content Hierarchy Map

```
┌─────────────────────────────────────────────────────────────┐
│                        HUB VIEW                              │
├─────────────────────────────────────────────────────────────┤
│ 1. Save Progress Alert (conditional)                        │
│ 2. Navi Guide Block (primary intelligence)                  │
│    ├── Eyebrow label (status)                              │
│    ├── Summary title (personalized greeting)               │
│    ├── Encouragement banner (gamified)                     │
│    ├── Reason text (why this matters)                      │
│    ├── Context boost bullets (what we know)                │
│    └── Action buttons (next step + FAQ)                    │
│ 3. Product Tiles (3 core journey products)                  │
│    ├── Completion badges (done.png overlay)                │
│    ├── Progress indicators                                  │
│    └── Recommended step chips                              │
│ 4. Additional Services (conditional, flag-based)            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      PRODUCT VIEW                            │
├─────────────────────────────────────────────────────────────┤
│ 1. Navi Guide Bar (top, persistent)                         │
│    ├── Icon + main message                                  │
│    ├── Subtext (why/context)                               │
│    └── Progress badge (X/Y)                                 │
│ 2. Info/Warning Callouts (conditional)                      │
│    ├── Encouragement messages                               │
│    ├── Support messages (sensitive topics)                  │
│    └── Red flags (clinical considerations)                  │
│ 3. Question Content (module-driven)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Hub: Save Progress Alert

### Current Implementation
**Location:** Top of hub, before Navi Guide Block  
**File:** `hubs/concierge.py` → `_build_saved_progress_alert()`  
**Trigger:** Returning from product with save message in session state

### Visual Treatment
```html
<div style="
  margin-bottom: 20px;
  padding: 16px 20px;
  border-radius: 14px;
  background: [#ecfdf5 (complete) | #eff6ff (in-progress)];
  border: 1px solid [#bbf7d0 | #bfdbfe];
  color: [#047857 | #1d4ed8];
">
  [Icon] [Message]
</div>
```

### Dynamic Content
- **Icon**: ✅ (complete) or 💾 (in-progress)
- **Message**: Product name, progress %, step X of Y
- **Colors**: Green (complete) or Blue (in-progress)

### Data Sources
- `st.session_state["_show_save_message"]` (popped on render)
- Product: `gcp`, `gcp_v4`, `cost_v2`, `pfma_v2`
- Progress: 0-100%, step counts

### Design Issues
1. **Placement:** Appears above Navi Guide Block, creating hierarchy confusion
2. **Persistence:** Disappears on rerun (session pop), no way to dismiss
3. **Visual weight:** Same prominence as Navi's primary guidance
4. **Redundancy:** Progress info duplicated in product tiles

### Recommendations
- [ ] **Move below Navi Guide Block** - Let Navi's guidance be first thing user sees
- [ ] **Add dismiss button** - User control over persistence
- [ ] **Reduce visual weight** - Use info banner instead of alert styling
- [ ] **Consider toast notification** - Non-blocking, auto-dismissing alternative

---

## 2. Hub: Navi Guide Block (Primary Intelligence)

### Current Implementation
**Location:** Top of hub content area  
**File:** `hubs/concierge.py` → `_build_navi_guide_block()`  
**Render:** Always visible, adapts to journey state

### Structure Breakdown

#### A. Eyebrow Label
```html
<div class="hub-guide__eyebrow">
  🤖 Navi Insight · [Status]
</div>
```
**Dynamic Values:**
- Getting started
- In progress  
- Nearly there
- Journey complete

**Data Source:** `MCIP.get_recommended_next_action()["status"]`

#### B. Summary Title
```html
<h2 class="hub-guide__title">
  [Personalized greeting + context]
</h2>
```
**Dynamic Logic:**
- 0 complete: "Hey [name]! Let's get started..."
- 1 complete: "Great progress! You've chosen [tier]..."
- 2 complete: "Almost done! 2/3 complete..."
- 3 complete: "🎉 Journey complete!..."

**Data Sources:**
- `ctx.is_authenticated`, `ctx.user_name`
- `ctx.care_recommendation.tier`
- `ctx.progress["completed_count"]`

#### C. Encouragement Banner (NEW - Gamified)
```html
<div style="
  margin: 12px 0;
  padding: 14px 18px;
  background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
  border: 1px solid #bfdbfe;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
">
  <span style="font-size: 1.75rem;">[Emoji]</span>
  <span>[Message]</span>
</div>
```

**Dynamic Content:**
| Status | Emoji | Message |
|--------|-------|---------|
| getting_started | 🚀 | "Let's get started! Every journey begins with a single step." |
| in_progress | 💪 | "You're making great progress! Keep up the momentum." |
| nearly_there | 🎯 | "Almost there! Just one more step to complete your journey." |
| complete | 🎉 | "Amazing work! You've completed all the essentials..." |

**Data Source:** `next_action["status"]`

#### D. Reason Text
```html
<p class="hub-guide__text">
  [Why this next step matters]
</p>
```
**Data Source:** `next_action["reason"]`

#### E. Context Boost Bullets
```html
<ul style="...">
  <li>✅ Care Plan: [tier] ([confidence]% confidence)</li>
  <li>✅ Cost Estimate: $[monthly]/month ([runway] month runway)</li>
  <li>✅ Appointment Scheduled: [advisor_type]</li>
</ul>
```

**Data Sources:**
- `ctx.care_recommendation` (tier, confidence)
- `ctx.financial_profile` (monthly cost, runway)
- `ctx.advisor_appointment` (advisor type)

**Conditional:** Only shown if data exists

#### F. Action Buttons
```html
<div class="hub-guide__actions">
  <a class="btn btn--primary" href="[next_route]">[action_label]</a>
  <a class="btn btn--secondary" href="?page=faqs">Ask Navi →</a>
</div>
```

**Dynamic Content:**
- **Primary button:**
  - Label: From `next_action["action"]`
  - Route: From `next_action["route"]`
- **Secondary button:** Always "Ask Navi →" to FAQs

### Design Issues
1. **Information density:** Too many elements competing for attention
2. **Vertical hierarchy:** Unclear which element is most important
3. **Encouragement placement:** Banner between title and reason breaks flow
4. **Redundant status:** Eyebrow and encouragement both show status
5. **Button balance:** Two equal-weight buttons (should primary be more prominent?)

### Recommendations
- [ ] **Simplify eyebrow:** Just "🤖 Navi" (move status to encouragement)
- [ ] **Restructure flow:** Title → Reason → Encouragement → Boost → Actions
- [ ] **Make encouragement subtle:** Smaller, less prominent (or integrate into title)
- [ ] **Emphasize primary action:** Make primary button larger/more prominent
- [ ] **Add visual separator:** Divide "what we know" from "what to do next"

---

## 3. Hub: Product Tiles

### Current Implementation
**Location:** Below Navi Guide Block  
**File:** `core/product_tile.py` → `ProductTileHub`  
**Render:** 3 core tiles + FAQ tile

### Dynamic Elements per Tile

#### A. Completion Badge (NEW - Gamified)
```html
<div class="tile-completion-badge">
  <img src="[done.png]" alt="Complete" />
</div>
```

**Visual Treatment:**
- Position: Absolute, top-right (-8px overflow)
- Size: 64x64px
- Animation: Bouncy entrance (scale + rotation)
- Shadow: Green-tinted drop-shadow

**Conditional:** Only shown when `progress >= 100` AND `key != "faqs"`

**CSS:**
```css
.tile-completion-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 64px;
  height: 64px;
  z-index: 10;
  animation: completion-badge-entrance 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  filter: drop-shadow(0 4px 12px rgba(34, 197, 94, 0.3));
}
```

#### B. Recommended Step Chip
```html
<div class="badge badge--step">
  Step [order] of [total]
</div>
```

**Dynamic Content:**
- Order: 1, 2, or 3 (from MCIP)
- Total: Always 3

**Conditional:** Only shown when `recommended_order` is set

**Data Source:** `MCIP.get_recommended_next_action()`

#### C. Progress Status Text
```html
<div class="dashboard-status">
  [Status]
</div>
```

**Dynamic Values:**
- "New" (0%)
- "In progress" (1-99%)
- "Complete" (100%)
- "Locked" (prerequisites not met)

**Data Source:** `tile.progress` (float 0-100)

#### D. Tile State Classes
```css
.tile--new
.tile--doing
.tile--done
.tile--locked
.tile--recommended  /* NEW - MCIP gradient */
```

**Visual Impact:**
- `.tile--done`: Green border + gradient background
- `.tile--recommended`: Blue gradient border
- `.tile--locked`: Greyed out, lock icon overlay

#### E. Dynamic Description
**Examples:**
- GCP Complete: "✅ Care recommendation: [tier]"
- Cost Planner In Progress: "Resume cost analysis ([progress]% complete)"
- PFMA Locked: "Complete Cost Planner first"

**Data Source:** `MCIP.get_product_summary(product_key)`

### Design Issues
1. **Badge size:** 64px badge may be too large, dominates tile
2. **Completion glow:** Green gradient subtle, may be too subtle
3. **Step chip placement:** Competes with status badge in title row
4. **Recommended gradient:** Blue border conflicts with done green
5. **Visual hierarchy:** Status text, badges, and description all same weight

### Recommendations
- [ ] **Reduce badge size:** Try 48px or 56px
- [ ] **Enhance glow:** Make green gradient more visible (3-5% instead of 2%)
- [ ] **Reposition step chip:** Move to top-left (eyebrow position)
- [ ] **Separate states:** Don't show recommended gradient on done tiles
- [ ] **Emphasize description:** Make summary text larger/bolder

---

## 4. Hub: Additional Services Section

### Current Implementation
**Location:** Below product tiles  
**File:** `core/additional_services.py`  
**Render:** Conditional based on GCP completion

### Dynamic Content
- **Service cards:** 3-5 cards based on flags
- **Flag mapping:** GCP module flags → service recommendations
- **Card content:** Logo, title, description, CTA

**Data Sources:**
- `get_all_flags()` → flag-based filtering
- `config/partners.json` → service metadata

### Design Issues
1. **Visibility:** Easily missed below the fold
2. **Relevance:** May not be clear why services are recommended
3. **Timing:** Shows immediately after GCP (before Cost Planner/PFMA)

### Recommendations
- [ ] **Add context:** "Based on your care plan, these services may help"
- [ ] **Defer appearance:** Only show after all 3 products complete?
- [ ] **Improve connection:** Show flags that triggered each service

---

## 5. Product: Navi Guide Bar (Top Panel)

### Current Implementation
**Location:** Top of every product page/module  
**File:** `core/ui.py` → `render_navi_guide_bar()`  
**Render:** Always visible, provides contextual guidance

### Structure
```html
<div style="
  background: linear-gradient(135deg, [color] 0%, [color]dd 100%);
  padding: 12px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  color: white;
  display: flex;
  align-items: center;
  gap: 12px;
">
  <div style="font-size: 24px;">[Icon]</div>
  <div style="flex: 1;">
    <div style="font-size: 14px; font-weight: 600;">[Text]</div>
    <div style="font-size: 12px;">[Subtext]</div>
  </div>
  <div style="...">[Progress Badge: X/Y]</div>
</div>
```

### Dynamic Content

#### A. Icon
- Default: 🤖
- Custom: From `module_config.steps[step].navi_guidance.icon`
- Examples: 🚶 (mobility), 🧠 (cognition), 💊 (medications)

#### B. Main Text
**Priority sources:**
1. `navi_guidance.section_purpose` ("what this section does")
2. `navi_guidance.encouragement` ("friendly motivational text")
3. Fallback: `step.title`

**Example:** "🤖 Navi: Let's talk about your daily mobility needs"

#### C. Subtext
**Priority sources:**
1. `navi_guidance.why_this_matters` ("educational context")
2. `navi_guidance.what_happens_next` ("preview")
3. `navi_guidance.time_estimate` ("for intro pages")
4. `navi_guidance.context_note` ("additional details")

**Example:** "💡 This helps me recommend the right level of care support"

#### D. Progress Badge
```html
<div style="
  font-size: 12px;
  font-weight: 500;
  padding: 4px 12px;
  background: rgba(255,255,255,0.2);
  border-radius: 12px;
">
  [step]/[total]
</div>
```

**Conditional:** Only shown when `show_progress=True` and step counts available

#### E. Color
- Default: `#0066cc` (CCA blue)
- Custom: From `navi_guidance.color`
- Used for gradient background

### Design Issues
1. **Text size:** 14px main text may be too small for importance
2. **Color contrast:** Gradient backgrounds may have WCAG issues
3. **Progress badge:** White-on-color may be hard to read
4. **Fixed position:** Always at top, can't scroll with content
5. **Mobile:** Very compact on small screens

### Recommendations
- [ ] **Increase text size:** 16px main, 14px subtext
- [ ] **Test contrast:** Ensure all color combinations meet WCAG AA
- [ ] **Improve progress badge:** Use solid background or border
- [ ] **Make sticky:** Consider position: sticky for long pages
- [ ] **Mobile optimization:** Stack icon/text/progress vertically on small screens

---

## 6. Product: Secondary Info Callouts

### Current Implementation
**Location:** Below Navi Guide Bar, within module content  
**File:** `core/navi.py` → `render_navi_panel()` (product branch)  
**Render:** Conditional based on guidance content

### Types

#### A. Encouragement Messages
```python
if guidance.get('encouragement') and guidance.get('section_purpose'):
    st.info(f"💬 {guidance['encouragement']}")
```

**Visual:** Streamlit info banner (blue background)  
**Purpose:** Additional motivation when section_purpose used as main text  
**Conditional:** Only if both encouragement AND section_purpose exist

#### B. Support Messages
```python
elif guidance.get('support_message'):
    st.info(f"💙 {guidance['support_message']}")
```

**Visual:** Streamlit info banner (blue background)  
**Purpose:** Empathy for sensitive topics (mental health, safety concerns)  
**Example:** "💙 These questions can be difficult. Take your time."

#### C. Red Flags (Clinical Warnings)
```python
if guidance.get('red_flags'):
    with st.expander("⚠️ Important Considerations"):
        st.warning("**Watch for these combinations:**")
        for flag in guidance['red_flags']:
            st.markdown(f"- {flag}")
```

**Visual:** Streamlit expander (collapsed by default) + warning banner (yellow)  
**Purpose:** Alert clinicians/caregivers to concerning flag combinations  
**Conditional:** Only if red_flags array exists in guidance

### Design Issues
1. **Visual consistency:** Using Streamlit native components (different from custom Navi bar)
2. **Hierarchy:** Info banners same visual weight as primary content
3. **Icon inconsistency:** 💬 and 💙 don't match Navi's 🤖 branding
4. **Expander placement:** Red flags hidden by default, may be missed

### Recommendations
- [ ] **Custom styling:** Create custom info cards matching Navi Guide Bar
- [ ] **Consistent iconography:** Use 🤖 prefix for all Navi messages
- [ ] **Visual hierarchy:** Make secondary callouts more subtle (lighter background)
- [ ] **Red flags visibility:** Consider making visible (not collapsed) when present

---

## 7. Context Boost (Hub)

### Current Implementation
**Location:** Within Navi Guide Block, after encouragement  
**File:** `hubs/concierge.py` → `_build_navi_guide_block()`  
**Render:** Conditional, only if data available

### Content Structure
```html
<ul style="
  margin: 0.75rem 0 0;
  padding-left: 1.2rem;
  color: var(--ink-600);
  font-size: 0.95rem;
  line-height: 1.55;
">
  <li>✅ Care Plan: [tier] ([confidence]% confidence)</li>
  <li>✅ Cost Estimate: $[monthly]/month ([runway] month runway)</li>
  <li>✅ Appointment Scheduled: [advisor_type]</li>
</ul>
```

### Dynamic Logic
- **Line 1:** Only if `ctx.care_recommendation` exists
- **Line 2:** Only if `ctx.financial_profile` exists  
- **Line 3:** Only if `ctx.advisor_appointment` exists

**Progressive disclosure:** Grows as user completes products

### Design Issues
1. **Visual treatment:** Plain bullet list, not very engaging
2. **Icon usage:** ✅ repeated, could use varied icons per type
3. **Data density:** Numbers in parentheses hard to scan
4. **Prominence:** Buried in middle of guide block

### Recommendations
- [ ] **Card layout:** Convert to visual "achievement cards" instead of list
- [ ] **Varied icons:** 🧭 (care), 💰 (cost), 📅 (appointment)
- [ ] **Readable numbers:** Format with commas, better spacing
- [ ] **Elevate position:** Move above encouragement banner (show wins first)

---

## 8. FAQ CTA (Hub)

### Current Implementation
**Location:** Bottom of Navi Guide Block (in render_navi_panel, hub branch)  
**File:** `core/navi.py` → `render_navi_panel()` (hub section)

### Content
```python
num_suggested = len(NaviOrchestrator.get_suggested_questions(...))
if num_suggested > 0:
    st.markdown(f"**💬 Have questions?** I have {num_suggested} personalized answers ready for you.")
    if st.button("Ask Navi →", key="navi_faq_cta", type="secondary", use_container_width=True):
        route_to("faq")
```

**Conditional:** Only if suggested questions exist (currently: none until PFMA complete)

### Design Issues
1. **Currently disabled:** Quick questions removed to maintain focus
2. **Placement:** Would be below context boost (bottom of guide block)
3. **Visual treatment:** Streamlit button (inconsistent with HTML action buttons)
4. **Prominence:** Equal weight to primary action

### Recommendations
- [ ] **Re-enable thoughtfully:** Consider showing 1-2 top questions (not 3)
- [ ] **Move to separate section:** Below guide block, not within it
- [ ] **Match button styling:** Use custom HTML buttons like primary actions
- [ ] **Reduce prominence:** Use ghost/outline style

---

## Cross-Cutting Design Issues

### 1. Inconsistent Visual Language
**Problem:** Mixing custom HTML styling with Streamlit native components
- Navi Guide Bar: Custom HTML + inline styles
- Hub Guide Block: Custom HTML + CSS classes
- Info callouts: Streamlit st.info() / st.warning()
- Buttons: Mix of HTML links and st.button()

**Recommendation:** Standardize on either:
- **Option A:** All custom HTML (more control, consistent styling)
- **Option B:** Streamlit components with custom CSS theme (easier maintenance)

### 2. Color Palette Fragmentation
**Current colors used:**
- Blue: `#0066cc`, `#eff6ff`, `#bfdbfe`, `#1d4ed8`
- Green: `rgba(34, 197, 94, ...)`, `#ecfdf5`, `#bbf7d0`, `#047857`
- Purple: `#8b5cf6` (default Navi bar color, rarely used)

**Recommendation:** Define semantic color system:
```css
--navi-primary: #0066cc;      /* CCA blue */
--navi-success: #22c55e;      /* Completions */
--navi-info: #3b82f6;         /* Information */
--navi-warning: #f59e0b;      /* Cautions */
--navi-encouragement: #eff6ff; /* Motivation backgrounds */
```

### 3. Typography Hierarchy Confusion
**Current sizes:**
- Guide block title: 1.5-2rem (h2)
- Guide bar text: 14px
- Subtext: 12px
- Encouragement: 0.95rem
- Context boost: 0.95rem

**Problem:** No clear hierarchy between "primary" and "supporting" content

**Recommendation:** Define semantic scale:
```
Hero (primary action): 18-20px, bold
Title (section headers): 16-18px, semibold
Body (main content): 14-16px, regular
Caption (supporting): 12-14px, regular
Meta (progress, labels): 10-12px, medium
```

### 4. Responsive Behavior Gaps
**Issues:**
- Navi Guide Bar: Barely fits on mobile (24px icon + text + badge)
- Hub Guide Block: Encouragement banner doesn't stack on mobile
- Product tiles: Completion badge may overlap text on small screens
- Context boost: Bullets with numbers may wrap awkwardly

**Recommendation:** Add mobile-first responsive rules:
```css
@media (max-width: 640px) {
  .navi-guide-bar { flex-direction: column; }
  .tile-completion-badge { width: 48px; height: 48px; }
  .encouragement-banner { font-size: 0.85rem; }
}
```

### 5. Animation Timing & Performance
**Current animations:**
- Completion badge: 0.5s entrance (scale + rotate)
- Hover effects: Various transition timings
- No defined animation curve system

**Recommendation:** Standardize motion system:
```css
--motion-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
--motion-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
--motion-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
--motion-bounce: 500ms cubic-bezier(0.34, 1.56, 0.64, 1);
```

---

## Proposed Visual Redesign Priorities

### Phase 1: Critical Fixes (Immediate)
1. **Fix save alert placement** - Move below Navi Guide Block
2. **Improve Navi Guide Bar contrast** - WCAG AA compliance
3. **Standardize button styling** - Consistent HTML/CSS approach
4. **Mobile breakpoints** - Ensure all components work on mobile

### Phase 2: Hierarchy Refinement (Short-term)
1. **Restructure Hub Guide Block** - Clearer visual flow
2. **Reduce encouragement prominence** - Make subtle, not competing
3. **Elevate context boost** - Show achievements first
4. **Separate FAQ section** - Don't mix with primary actions

### Phase 3: System Consolidation (Medium-term)
1. **Create Navi design system** - Semantic colors, typography, spacing
2. **Build component library** - Reusable Navi UI components
3. **Document patterns** - When to use each element type
4. **Performance audit** - Optimize animations, lazy-load images

### Phase 4: Advanced Enhancements (Long-term)
1. **Adaptive layouts** - AI-driven content prioritization
2. **Micro-interactions** - Delightful transitions between states
3. **Accessibility testing** - Full screen reader + keyboard nav audit
4. **A/B testing framework** - Data-driven design decisions

---

## Detailed Element Placement Recommendations

### Hub Layout (Revised)
```
┌─────────────────────────────────────────────────────────────┐
│ 1. NAVI GUIDE BLOCK (HERO)                                  │
│    ┌─────────────────────────────────────────────────────┐ │
│    │ 🤖 Navi Insight                           [Step 2/3]│ │
│    │                                                      │ │
│    │ [TITLE: Personalized greeting]                      │ │
│    │ [REASON: Why this next step matters]                │ │
│    │                                                      │ │
│    │ ┌─────────────────────────────────────────────────┐│ │
│    │ │ 💪 You're making great progress! Keep going.    ││ │
│    │ └─────────────────────────────────────────────────┘│ │
│    │                                                      │ │
│    │ What I know so far:                                 │ │
│    │ ┌──────┐ ┌──────┐ ┌──────┐                         │ │
│    │ │ 🧭   │ │ 💰   │ │ 📅   │  [Achievement cards]    │ │
│    │ │ Care │ │ Cost │ │ Appt │                         │ │
│    │ └──────┘ └──────┘ └──────┘                         │ │
│    │                                                      │ │
│    │ [Primary Action Button] [Secondary: Ask Navi]      │ │
│    └─────────────────────────────────────────────────────┘ │
│                                                              │
│ 2. SAVE PROGRESS ALERT (if needed)                          │
│    💾 Progress saved! You're 60% through Cost Planner    [×]│
│                                                              │
│ 3. PRODUCT TILES (with visual indicators)                   │
│    ┌─────────┐ ┌─────────┐ ┌─────────┐                     │
│    │ GCP  ✓  │ │Cost Plan│ │  PFMA   │                     │
│    │[done.png│ │[step 2/3│ │ Locked  │                     │
│    └─────────┘ └─────────┘ └─────────┘                     │
│                                                              │
│ 4. QUESTIONS & SUPPORT (collapsible)                        │
│    💬 Have questions? [Expand for personalized answers]     │
│                                                              │
│ 5. ADDITIONAL SERVICES (after journey complete)             │
│    Based on your care plan, these services may help:        │
│    [Service cards...]                                        │
└─────────────────────────────────────────────────────────────┘
```

### Product Layout (Revised)
```
┌─────────────────────────────────────────────────────────────┐
│ NAVI GUIDE BAR (sticky)                                      │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🤖 Let's talk about your daily mobility needs  [Step 2/5││ │
│ │ 💡 This helps me recommend the right level of care      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ [Question/Content Area]                                      │
│                                                              │
│ SECONDARY CALLOUT (if needed)                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 💙 These questions can be sensitive. Take your time.    │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ [Form controls / Buttons]                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Accessibility Checklist

### Current State
- ✅ Semantic HTML in guide bar
- ✅ ARIA labels on completion badges
- ⚠️ Color contrast issues (white text on light gradients)
- ⚠️ No focus visible styles defined
- ❌ No skip navigation links
- ❌ Screen reader testing not documented
- ❌ Keyboard navigation incomplete (some buttons not keyboard-accessible)

### Recommendations
- [ ] Add `role="status"` to progress indicators
- [ ] Add `aria-live="polite"` to dynamic content areas
- [ ] Ensure all gradients meet WCAG AA contrast (4.5:1)
- [ ] Add visible focus states (outline or box-shadow)
- [ ] Test with VoiceOver (Mac) and NVDA (Windows)
- [ ] Add skip to main content link
- [ ] Ensure all interactive elements keyboard-accessible

---

## Implementation Roadmap

### Week 1: Foundation
- [ ] Create `NAVI_DESIGN_SYSTEM.md` documentation
- [ ] Define semantic color palette
- [ ] Establish typography scale
- [ ] Document component patterns

### Week 2: Critical Fixes
- [ ] Reorder hub elements (Navi first, alert second)
- [ ] Fix Navi Guide Bar contrast issues
- [ ] Standardize button styling across hub/products
- [ ] Add mobile breakpoints for all components

### Week 3: Hierarchy Refinement
- [ ] Restructure Hub Guide Block (achievement cards)
- [ ] Reduce encouragement banner prominence
- [ ] Create separate FAQ section
- [ ] Improve context boost visual treatment

### Week 4: Testing & Polish
- [ ] Accessibility audit (WCAG AA)
- [ ] Cross-browser testing
- [ ] Mobile device testing
- [ ] Performance profiling

---

## Files Requiring Updates

### Core Files
- `core/navi.py` - Main intelligence layer
- `core/ui.py` - Navi Guide Bar component
- `hubs/concierge.py` - Hub guide block
- `core/product_tile.py` - Tile visual elements

### CSS Files
- `assets/css/products.css` - Tile styling, completion badges
- `assets/css/hubs.css` - Hub guide block styling
- `assets/css/theme.css` - Global Navi design tokens

### Documentation
- `NAVI_DESIGN_SYSTEM.md` (new) - Design system documentation
- `NAVI_COMPONENT_LIBRARY.md` (new) - Reusable component guide

---

## Questions for Design Review

1. **Primary vs Secondary Actions**: Should FAQ button be less prominent than primary action?
2. **Encouragement Timing**: Show encouragement on every hub visit, or only on state changes?
3. **Completion Badge Size**: 64px, 56px, or 48px? What feels celebratory but not overwhelming?
4. **Context Boost Format**: Bullet list, cards, or inline badges?
5. **Save Alert Behavior**: Toast notification or persistent banner?
6. **Mobile Priority**: Which elements should collapse/hide on mobile first?
7. **Animation Philosophy**: Playful/bouncy or smooth/professional?
8. **Color Semantics**: Should different Navi guidance types use different colors?

---

**End of Audit** • Ready for design team review and prioritization
