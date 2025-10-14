# Header & Footer Rebuild — Cleanup + Visual Alignment

## 🎯 Objective
- Remove all old header/footer code and rebuild clean, single version
- Minimize white space above/below content globally
- Prevent new session requests from header (no re-renders, no reruns)
- Keep header lightweight, clean, consistent with rest of app

## 1️⃣ Visual + Layout Goals

### ✅ Header Appearance
```
[ CCA logo + "Senior Navigator" ]   Welcome | Concierge | Waiting Room | Learning | Trusted Partners | Professional | Log In
```

### ✅ Layout & Hierarchy
- One single-line header — no stacked logo/title rows
- No white padding above or below header
- Page content sits directly under header, no extra vertical spacing

### ✅ Footer Appearance
- Minimalist footer with copyright + version only
- No redundant padding at top or bottom
- Font: same family/weight as global content
- Color: soft gray (#94a3b8) on white background

## 2️⃣ Navigation Logic

### Menu Items
- Welcome
- Concierge
- Waiting Room
- Learning
- Trusted Partners
- Professional
- Log In / Log Out

### Navigation Behavior
- Use plain `<a href="?page=welcome">` style links
- No `st.rerun()`, no state mutations, no data writes
- All routes resolve through central routing function
- Highlight current route (active state)

## 3️⃣ Global Spacing Cleanup

### CSS Targets
```css
/* Remove layout.py spacing issues */
.sn-app main,
.sn-app .dashboard-shell,
.sn-app .block-container {
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  margin-top: 0 !important;
  margin-bottom: 0 !important;
}

/* Remove excess header gap */
header, .sn-header {
  margin-bottom: 0 !important;
  padding-bottom: 8px !important;
}

/* Reduce blank space under titles */
h1.page-title, .dashboard-title {
  margin-bottom: 8px !important;
}
```

## 4️⃣ Functional Requirements
- Header never writes to `session_state` or `st.query_params` during render
- No `st.button()` in header (use links)
- Header must not trigger rerun when navigating
- Use caching for logo/nav JSON (`@st.cache_data`)

## 5️⃣ Implementation Plan

### Phase 1: Create New Components
1. Create `ui/header_v2.py` - Clean header implementation
2. Create `ui/footer_v2.py` - Minimal footer
3. Add new CSS file `assets/css/layout_v2.css` - Clean spacing rules

### Phase 2: Remove Old Code
1. Identify all old header/footer references in `layout.py`
2. Remove or comment out legacy code
3. Clean up CSS conflicts

### Phase 3: Integration
1. Update `layout.py` to use new header/footer
2. Test all pages (welcome, hubs, products, modules)
3. Verify no spacing regressions

## 6️⃣ Files to Modify

### Create New:
- `ui/header_v2.py`
- `ui/footer_v2.py`
- `assets/css/layout_v2.css`

### Modify:
- `layout.py` - Replace header/footer calls
- `assets/css/global.css` - Add spacing overrides
- All hub files (if needed) - Update imports

### Review/Clean:
- `assets/css/hubs.css` - Remove conflicting spacing
- `assets/css/products.css` - Check for issues
- `core/ui.py` - Update any header-related functions

## 7️⃣ QA Checklist
- [ ] No duplicate headers or footers
- [ ] Header links navigate instantly (no reruns)
- [ ] Page content begins immediately below header
- [ ] Footer has no extra padding
- [ ] Mobile layout works cleanly
- [ ] Header text/icons/logo vertically aligned
- [ ] Welcome page looks correct
- [ ] All hub pages look correct
- [ ] No white gaps anywhere

## 8️⃣ Success Criteria
- Header is single line, minimal padding
- Footer is minimal, no wasted space
- Content flows naturally top to bottom
- No layout.py spacing issues
- Welcome page looks exactly as before
- Navigation works without reruns
