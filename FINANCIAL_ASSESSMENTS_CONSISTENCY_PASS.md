# 🎛️ Financial Assessments – Visual Consistency Pass

**Status:** Ready for Implementation  
**Branch:** assessment-updates  
**Prerequisites:** Income/Assets Basic/Advanced toggle completed ✅

---

## Goal

Refactor remaining Financial Assessment modules to match Income/Assets visual style, grouping, and clarity.

**Key Constraint:** Do NOT add Basic/Advanced mode to other modules. This is visual/structural consistency only.

---

## Scope – Remaining Assessments

Current assessments requiring consistency pass:

1. **Health Insurance** (`health_insurance.json`)
2. **Life Insurance** (`life_insurance.json`)
3. **VA Benefits** (`va_benefits.json`)
4. **Medicaid Navigation** (`medicaid_navigation.json`)
5. Any additional financial assessments in `products/cost_planner_v2/modules/assessments/`

---

## 1) UX & Layout Requirements (Match Income/Assets)

### Visual Elements
- ✅ **Card-based structure** with clean white backgrounds
- ✅ **Section headers** (H2) and subgroup headers (H3) with consistent spacing
- ✅ **Navi at top** with single-line guide tailored to assessment
- ✅ **Inline help** beneath fields (no large explanatory banners)
- ✅ **Compact summary card** showing key metrics
- ✅ **Consistent spacing** matching Income/Assets rhythm
- ✅ **Visible labels** for all fields (accessible)
- ❌ **NO Basic/Advanced toggle** for these modules

### Layout Pattern
```
┌─────────────────────────────────────┐
│ Navi Panel (single-line guide)     │
├─────────────────────────────────────┤
│ Assessment Title + Icon             │
│ Description                         │
├─────────────────────────────────────┤
│ Section 1: Coverage Details         │
│  ├─ Field 1 (with inline help)     │
│  ├─ Field 2 (with inline help)     │
│  └─ Info box (if needed)           │
├─────────────────────────────────────┤
│ Section 2: Benefit Details          │
│  ├─ Field 3                         │
│  └─ Field 4                         │
├─────────────────────────────────────┤
│ Summary Card (compact, pinned)      │
├─────────────────────────────────────┤
│ Actions: Back | Save | Expert →    │
└─────────────────────────────────────┘
```

---

## 2) JSON-Driven Grouping

All assessments should support same metadata structure:

```json
{
  "key": "health_insurance",
  "title": "Health Insurance",
  "icon": "🏥",
  "description": "Medicare, Medicaid, and supplemental coverage",
  "estimated_time": "3-5 min",
  "required": true,
  "sort_order": 3,
  "sections": [
    {
      "id": "coverage_type",
      "title": "Coverage Type",
      "icon": "📋",
      "help_text": "Tell me about your current health insurance.",
      "layout": "single_column",
      "fields": [
        {
          "key": "coverage_primary",
          "label": "Primary Health Coverage",
          "type": "select",
          "required": false,
          "options": [...],
          "help": "Your main health insurance"
        }
      ],
      "info_boxes": [
        {
          "type": "info",
          "message": "💡 Medicare becomes available at age 65."
        }
      ]
    }
  ],
  "summary": {
    "type": "text",
    "label": "Coverage Summary",
    "fields": ["coverage_primary", "medicare_parts"]
  }
}
```

### Renderer Expectations
- Group by `sections`, order by `sort_order`
- Render `help_text` beneath section title
- Use field `help` for inline guidance
- Render `info_boxes` at section bottom
- NO code-side whitelists: visibility comes from JSON

---

## 3) Assessment-Specific Guidelines

### Health Insurance Assessment
**Navi Copy:**  
"Review your coverage and benefits so your advisor can tailor options quickly."

**Key Sections:**
- Coverage Type (Medicare, Medicaid, Private, etc.)
- Medicare Parts (if applicable)
- Supplemental Coverage
- Out-of-Pocket Costs

**Summary Card:**
- Coverage type
- Monthly premium estimate
- Gaps identified

---

### Life Insurance Assessment
**Navi Copy:**  
"Life insurance policies can provide liquidity for care costs through cash value or loans."

**Key Sections:**
- Policy Overview
- Cash Value (if applicable)
- Death Benefit
- Loans Against Policy

**Summary Card:**
- Total cash value available
- Outstanding loans
- Net available equity

---

### VA Benefits Assessment
**Navi Copy:**  
"If you may qualify for VA programs, add any known details here."

**Key Sections:**
- Veteran Status
- Service-Connected Disability
- Aid & Attendance Eligibility
- Pension Status

**Summary Card:**
- Current benefits amount
- Potential Aid & Attendance
- Application status

---

### Medicaid Navigation Assessment
**Navi Copy:**  
"Understanding Medicaid options helps identify paths to coverage if assets are limited."

**Key Sections:**
- Current Medicaid Status
- Asset Limits & Planning
- Spousal Protections
- Look-Back Period Concerns

**Summary Card:**
- Medicaid eligibility timeline
- Asset spend-down needed
- Planning recommendations

---

## 4) Implementation Checklist

### Phase 1: Audit Existing Assessments
- [ ] Review all assessment JSON files in `modules/assessments/`
- [ ] Document current structure vs. target structure
- [ ] Identify fields that need reorganization
- [ ] Note any custom rendering logic to preserve

### Phase 2: Update JSON Configurations
- [ ] Health Insurance: Restructure sections, add help text
- [ ] Life Insurance: Restructure sections, add help text
- [ ] VA Benefits: Restructure sections, add help text
- [ ] Medicaid Navigation: Restructure sections, add help text
- [ ] Validate all JSON syntax

### Phase 3: Verify Renderer Compatibility
- [ ] Confirm `_render_single_page_assessment` handles all field types
- [ ] Test section grouping and ordering
- [ ] Verify info_boxes render correctly
- [ ] Check summary card calculations

### Phase 4: Add Navi Copy
- [ ] Update intro sections with single-line Navi guidance
- [ ] Ensure Navi styling matches Income/Assets
- [ ] Test Navi panel rendering for each assessment

### Phase 5: Visual QA
- [ ] Compare each assessment side-by-side with Income/Assets
- [ ] Verify spacing, headers, label placement match
- [ ] Test on mobile viewport
- [ ] Accessibility audit (screen reader, keyboard nav)

### Phase 6: Functional Testing
- [ ] Fill out each assessment completely
- [ ] Verify data persists correctly
- [ ] Check summary calculations
- [ ] Test validation messages reference correct labels
- [ ] Confirm no regressions in Income/Assets

---

## 5) Accessibility Requirements

### Labels
✅ Every field has a visible label (no placeholders-only)  
✅ Labels are source of truth for validation messages  
✅ Custom HTML labels match Streamlit widget labels  

### Navigation
✅ Section headers are landmarks  
✅ Keyboard navigation is predictable and linear  
✅ Tab order follows visual order  

### Screen Readers
✅ Section context announced: "Section: Long-Term Care Insurance"  
✅ Field labels announced before input  
✅ Help text associated with fields via aria-describedby  
✅ Error messages reference field labels  

---

## 6) QA Scenarios

### Visual Parity Test
1. Open Income assessment
2. Open Health Insurance assessment
3. Compare side-by-side:
   - [ ] Section header styling matches
   - [ ] Field label styling matches
   - [ ] Spacing and padding identical
   - [ ] Info boxes styled consistently
   - [ ] Summary card layout matches

### JSON Change Test
1. Move a field to different section in JSON
2. Adjust sort_order
3. Reload assessment
4. Verify:
   - [ ] Field appears in new section
   - [ ] Order reflects JSON changes
   - [ ] No code edits required

### Navi Presence Test
1. Load each assessment
2. Verify:
   - [ ] One Navi panel at top
   - [ ] Copy matches assessment context
   - [ ] No duplicate Navi panels
   - [ ] Styling matches Income/Assets

### Accessibility Test
1. Use screen reader (VoiceOver/NVDA)
2. Navigate through assessment
3. Verify:
   - [ ] Section headers announced
   - [ ] Field labels announced
   - [ ] Help text accessible
   - [ ] Validation messages clear

### Summary Card Test
1. Complete assessment
2. Verify summary card:
   - [ ] Shows correct metrics
   - [ ] Calculations accurate
   - [ ] Persists after reload
   - [ ] Styling matches Income/Assets

### Toggle Isolation Test
1. Open Income assessment
2. Verify Basic/Advanced toggle present
3. Open Health Insurance assessment
4. Verify:
   - [ ] NO toggle present
   - [ ] All fields visible (no filtering)
   - [ ] Layout still clean and organized

---

## 7) Technical Notes

### Files to Modify
- `products/cost_planner_v2/modules/assessments/health_insurance.json`
- `products/cost_planner_v2/modules/assessments/life_insurance.json`
- `products/cost_planner_v2/modules/assessments/va_benefits.json`
- `products/cost_planner_v2/modules/assessments/medicaid_navigation.json`

### Files NOT to Modify
- ❌ `core/assessment_engine.py` (unless bugs found)
- ❌ `products/cost_planner_v2/assessments.py` (unless bugs found)
- ❌ Persistence keys or calculation formulas
- ❌ Income/Assets toggle logic

### Backward Compatibility
- Existing data must remain valid
- No breaking changes to output_contract
- Calculations preserve existing formulas
- Session state keys unchanged

---

## 8) Success Criteria

✅ All Financial Assessments have consistent visual style  
✅ JSON metadata drives layout (no hardcoded groupings)  
✅ Navi appears correctly on each assessment  
✅ Summary cards render and calculate correctly  
✅ Labels visible and accessible throughout  
✅ NO Basic/Advanced toggles outside Income/Assets  
✅ NO regressions in Income/Assets functionality  
✅ All validation messages reference correct labels  
✅ Screen reader navigation works properly  
✅ Mobile responsive on all assessments  

---

## 9) Deliverable

A consistency pass across all remaining Financial Assessment modules so they:
1. Look and behave like Income/Assets
2. Use same JSON grouping conventions
3. Have consistent Navi placement
4. Maintain accessible labels throughout
5. Do NOT have Basic/Advanced toggles

---

## Implementation Timeline

**Estimated Effort:** 4-6 hours

- **Phase 1 (Audit):** 30 min
- **Phase 2 (JSON Updates):** 2-3 hours
- **Phase 3 (Renderer Check):** 30 min
- **Phase 4 (Navi Copy):** 30 min
- **Phase 5 (Visual QA):** 1 hour
- **Phase 6 (Testing):** 1-2 hours

---

## Next Steps

1. Review this document with team
2. Create backup of all assessment JSON files
3. Start with one assessment (Health Insurance) as pilot
4. Validate pilot against all QA scenarios
5. Apply pattern to remaining assessments
6. Final cross-assessment QA pass
7. Commit with detailed changelog

---

**Document Version:** 1.0  
**Last Updated:** October 18, 2025  
**Author:** AI Assistant (via Copilot)  
**Status:** Ready for Implementation
