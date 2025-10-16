# Module Redesign Testing Guide

**Branch:** `navi-reconfig`  
**Test URL:** http://localhost:8501

---

## 🧪 What to Test

### **1. Hub Comparison**
**Goal:** Verify modules match Hub aesthetic

**Steps:**
1. Navigate to Concierge Hub
2. Observe layout: centered ~800px, white tiles, clean spacing
3. Click "Guided Care Plan" to start module
4. **Verify:** Module content is centered at same width as Hub
5. **Verify:** Form fields appear as white cards (like Hub tiles)
6. **Verify:** Clean, uncluttered layout

**Expected Result:**
✅ Module page looks like natural extension of Hub  
✅ Same centered width (~800px)  
✅ White cards with subtle shadows  
✅ Consistent spacing and visual rhythm  

---

### **2. Button Hierarchy**
**Goal:** Single prominent Continue, text links for secondary actions

**Steps:**
1. Start any module (GCP or Cost Planner)
2. Navigate to a question page
3. Observe button layout at bottom

**Expected Result:**
✅ **One blue Continue button** - centered, ~400px wide, 48px tall  
✅ **Text links below** - "💾 Save & Continue Later", "← Back to Hub"  
✅ **No gray button boxes** - secondary actions are subtle text  
✅ **Proper spacing** - 16px gaps, centered alignment  

**Hover States:**
- Continue: Darker blue, slight lift
- Text links: Underline, change from gray to black

---

### **3. Form Card Styling**
**Goal:** White cards with shadows for all form fields

**Steps:**
1. Navigate through module questions
2. Observe each question's form field

**Expected Result:**
✅ White background (not flat)  
✅ 1px gray border  
✅ 16px rounded corners  
✅ 32px padding inside card  
✅ Subtle shadow (0 1px 3px)  
✅ 24px margin between cards  

---

### **4. Width & Centering**
**Goal:** Content perfectly centered at 800px

**Steps:**
1. Start module on desktop (full screen)
2. Observe content width
3. Compare to Hub width

**Expected Result:**
✅ Content centered in viewport  
✅ Max 800px width  
✅ Equal margins on left/right  
✅ Matches Hub tile width exactly  

**Test at Different Widths:**
- Desktop (1920px): Content centered, large margins
- Laptop (1440px): Content centered, medium margins
- Tablet (768px): Content uses full width minus padding

---

### **5. Navigation Flow**
**Goal:** All buttons work correctly

**Steps:**
1. Click "Continue" - should advance to next question
2. Click "← Back to Previous Question" - should go back one step
3. Click "💾 Save & Continue Later" - should save and return to Hub
4. Click "← Back to Hub" - should return to Hub immediately

**Expected Result:**
✅ Continue: Advances to next step  
✅ Back: Returns to previous question  
✅ Save & Exit: Saves progress, returns to Hub with tile updated  
✅ Back to Hub: Returns immediately (may prompt to save)  

---

### **6. Results Page**
**Goal:** Verify results page layout

**Steps:**
1. Complete a module to reach results page
2. Observe button layout

**Expected Result:**
✅ "← Review Your Answers" button (left column)  
✅ "← Back to Hub" button (right column)  
✅ Both buttons same style (gray secondary)  
✅ Two-column layout preserved  

---

### **7. Responsive Design**
**Goal:** Layout adapts to mobile/tablet

**Steps:**
1. Resize browser window to mobile width (~375px)
2. Verify layout doesn't break
3. Test button sizes and touch targets

**Expected Result:**
✅ Container adapts to viewport width  
✅ Cards remain padded, readable  
✅ Buttons stack vertically if needed  
✅ Text links remain clickable  
✅ No horizontal scroll  

---

## 🐛 Known Issues to Watch For

### **Potential Issues:**
1. **Container not closing:** If content extends beyond viewport, check for missing `</div>` closing tag
2. **Buttons full-width:** Secondary buttons should be auto-width, not stretched
3. **White cards not showing:** Check for CSS specificity conflicts
4. **Text links look like buttons:** Verify `background: transparent` is applied

### **How to Debug:**
```bash
# Check browser console for errors
# Inspect element to verify CSS classes applied
# Look for .module-container, .mod-field, .mod-actions
```

---

## ✅ Success Criteria

### **Visual**
- [ ] Module width matches Hub width (~800px)
- [ ] Forms appear as white elevated cards
- [ ] Single blue Continue button stands out
- [ ] Secondary actions are subtle text links
- [ ] Clean, uncluttered layout

### **Functional**
- [ ] Continue button advances to next question
- [ ] Back button returns to previous question
- [ ] Save & Exit preserves progress
- [ ] Back to Hub returns to Concierge
- [ ] All click handlers work correctly

### **Consistency**
- [ ] Module pages feel like extension of Hub
- [ ] No jarring transitions between Hub and module
- [ ] Spacing and rhythm match throughout
- [ ] Professional, polished appearance

### **User Experience**
- [ ] Clear which button is primary action
- [ ] Less overwhelming than old design
- [ ] Faster to scan and understand
- [ ] Familiar pattern from Hub

---

## 📸 Screenshot Checklist

**Before Testing, Take Screenshots:**
1. Hub page (for comparison)
2. Module intro page
3. Module question page with form
4. Module actions section (Continue + text links)
5. Module results page
6. Mobile view of module

**Compare to Hub:**
- Side-by-side Hub vs Module width
- Card styling Hub tile vs Module form
- Spacing Hub vs Module

---

## 🔍 Edge Cases

### **Test These Scenarios:**
1. **Long form fields:** Do cards expand properly?
2. **Multiple choice questions:** Do radio pills still work?
3. **Multi-select fields:** Do black chips still appear?
4. **Error messages:** Do validation warnings display correctly?
5. **Long question text:** Does card height adapt?
6. **Results with many recommendations:** Does layout hold?

---

## 💬 Feedback Template

**What's Working:**
- 

**What Needs Improvement:**
- 

**Visual Bugs:**
- 

**Functional Issues:**
- 

**Suggestions:**
- 

---

## 🚀 After Testing

If everything looks good:
```bash
# Merge to main branch
git checkout main
git merge navi-reconfig
git push origin main
```

If issues found:
```bash
# Stay on navi-reconfig
git checkout navi-reconfig

# Make fixes, commit, test again
git add .
git commit -m "fix: [description]"
```

---

**Status:** ✅ Ready for testing  
**Test by:** Opening http://localhost:8501 and navigating to modules
