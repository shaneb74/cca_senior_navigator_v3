# Concierge Hub / Navi Panel and Cost Planner Requirements

**Date:** October 14, 2025  
**Status:** Requirements Documented - Ready for Implementation

---

## 1. 🧭 Navi Panel Behavior

### Continue Button Logic
The **Continue button** beneath the Navi panel should follow Navi's recommendation for the next step:

**Priority Order:**
1. **If GCP incomplete** → Continue opens **Guided Care Plan**
2. **If GCP complete but Cost Planner incomplete** → Continue opens **Cost Planner**
3. **If both complete** → Continue opens **Appointment Scheduling**

### Navi Panel Text
- ❌ **Remove:** Generic placeholder text like "what I know so far" or "appointment not scheduled"
- ✅ **Replace with:** Context-aware next-step guidance

**Examples:**
```
"Here's what you should do next:"
→ Complete your Guided Care Plan to get personalized recommendations

"Here's what you should do next:"
→ Review your Cost Planner to understand care costs

"Here's what you should do next:"
→ Schedule an appointment with a Care Advisor
```

### Additional Services Alert
When additional services are triggered by care or cost flags, Navi should display:

```
💡 "Hey, check out the additional services below for tailored recommendations."
```

---

## 2. 🎨 Additional Services Personalization

### Visual Treatment for Personalized Tiles

**Apply to tiles when:**
- Services are triggered by user-specific flags
- Navi has made a recommendation based on GCP/Cost data

**Visual Changes:**
1. **Light gradient overlay** on the tile
2. **Visible tag/label** with appropriate text

### Label Types

| Label | When to Use | Visual Style |
|-------|-------------|--------------|
| **"Personalized for You"** | User-specific recommendations based on profile/flags | Blue gradient, subtle glow |
| **"Navi Recommended"** | Services specifically flagged by Navi AI advisor | Green gradient, AI icon |

**Purpose:**
Visually distinguish Navi's personalized recommendations from standard options.

---

## 3. 💰 Cost Planner - Cost of Care Adjustments Table

### Location
Include the **Cost of Care Adjustments** table in the **Cost Breakdown** section of the **Cost Recommendation** view.

### Table Content
Display each flag with:
- ✅ Flag name / condition
- ✅ Percentage increase
- ✅ Rationale / description
- ✅ **All add-ons are cumulative** (they stack)

### Reference Table

| Flag / Condition | Add-On % | Rationale / Description |
|------------------|----------|-------------------------|
| **Mobility / Transfer Issues** | +15% | `mobility_limited`, `falls_risk` — Need lift equipment and additional staff |
| **Severe Cognitive Decline** | +20% | `memory_support`, `behavioral_concerns` — Specialized memory care and behavior management |
| **High ADL Support** | +10% | `adl_support_high` — Extensive help with daily activities |
| **Complex Medication** | +8% | `medication_management` — Professional medication oversight required |
| **Chronic Conditions** | +12% | `chronic_conditions` — Ongoing medical coordination and monitoring |
| **Safety Concerns** | +10% | `safety_concerns` — Enhanced supervision and environmental modifications |
| **High-Acuity Memory Care** | +25% | `memory_care_high_acuity` tier — Always applied for this tier |

### Calculation Method
```
Base Cost: $5,200/month (example)

Flag 1: Mobility Issues (+15%)  → $5,200 × 1.15 = $5,980
Flag 2: High ADL Support (+10%) → $5,980 × 1.10 = $6,578
Flag 3: Chronic Conditions (+12%) → $6,578 × 1.12 = $7,367

Final Monthly Cost: $7,367
Total Adjustment: +41.7% from base
```

**Important:** Each add-on multiplies the running total (cumulative stacking).

---

## 📋 Implementation Checklist

### Navi Panel (Priority 1)
- [ ] Update Continue button logic (GCP → Cost Planner → Scheduling)
- [ ] Replace placeholder text with dynamic next-step guidance
- [ ] Add "check out additional services" alert when flags present
- [ ] Update `hubs/concierge.py` or Navi rendering logic

### Additional Services Tiles (Priority 2)
- [ ] Add gradient overlay CSS for personalized tiles
- [ ] Create "Personalized for You" label component
- [ ] Create "Navi Recommended" label component
- [ ] Update tile rendering in `core/additional_services.py`
- [ ] Add flag detection logic to trigger personalization

### Cost Planner Adjustments Table (Priority 3)
- [ ] Create Cost of Care Adjustments table component
- [ ] Add table to Cost Breakdown view in Cost Planner V2
- [ ] Implement cumulative calculation logic
- [ ] Map GCP flags to adjustment percentages
- [ ] Display rationale for each adjustment
- [ ] Update `products/cost_planner_v2/` with new view

---

## 🗂️ Files Likely to Edit

### Navi Panel Updates
```
hubs/concierge.py                      # Navi panel rendering
core/state.py                          # Progress tracking
[Navi rendering component]             # Text and button logic
```

### Additional Services
```
core/additional_services.py            # Tile rendering
assets/css/theme.css                   # Gradient styles
core/ui.py                             # Label components
```

### Cost Planner
```
products/cost_planner_v2/expert_review.py    # Cost breakdown view
products/cost_planner_v2/utils/cost_calculator.py  # Adjustment logic
config/cost_planner_v2_modules.json          # Flag mappings (if needed)
```

---

## 🎯 Expected Behavior After Implementation

### User Journey
1. **User lands on Concierge Hub**
   - Navi says: "Complete your Guided Care Plan first"
   - Continue button → Opens GCP

2. **User completes GCP**
   - Navi says: "Now review your Cost Planner"
   - Continue button → Opens Cost Planner
   - Additional services show "Navi Recommended" labels

3. **User opens Cost Planner**
   - Sees Cost Breakdown with Adjustments Table
   - Understands why costs are higher (mobility +15%, ADL +10%, etc.)
   - Base $5,200 → Adjusted $6,578 (+26.5%)

4. **User completes Cost Planner**
   - Navi says: "Schedule your appointment"
   - Continue button → Opens scheduling

---

## 💡 Design Notes

### Navi Tone
- Friendly, conversational
- Clear about next steps
- Proactive (alerts about additional services)

### Visual Hierarchy
- Personalized tiles stand out but don't overwhelm
- Gradient is subtle (not garish)
- Labels are clear and readable

### Cost Transparency
- Table makes adjustments explicit
- Users understand "why" costs increased
- Cumulative stacking is explained

---

## 🧪 Testing Scenarios

1. **New user (nothing complete)**
   - Continue → GCP
   - Navi text: "Complete GCP"

2. **GCP complete, Cost Planner not started**
   - Continue → Cost Planner
   - Navi text: "Review costs"
   - Additional services show flags

3. **GCP has mobility + ADL flags**
   - Cost Planner shows +15% and +10%
   - Base $5,200 → $6,578

4. **Both complete**
   - Continue → Scheduling
   - Navi text: "Book appointment"

---

**Ready for implementation!** 🚀

See individual sections above for detailed requirements.
