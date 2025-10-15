# Implementation Guide - Navi & Cost Planner Enhancements

**Quick Start Guide for Developers**

---

## 🎯 Three Main Tasks

### Task 1: Navi Panel Continue Button Logic
**File:** `hubs/concierge.py` (or Navi component)

**Current Behavior:** Continue button may not follow logical progression

**New Behavior:**
```python
def get_next_action():
    gcp_complete = check_gcp_progress() == 100
    cost_planner_complete = check_cost_planner_progress() == 100
    
    if not gcp_complete:
        return "gcp_v4", "Complete your Guided Care Plan"
    elif not cost_planner_complete:
        return "cost_v2", "Review your Cost Planner"
    else:
        return "scheduling", "Schedule your appointment"

# Continue button
next_route, next_text = get_next_action()
if st.button("Continue"):
    route_to(next_route)
```

---

### Task 2: Additional Services Personalization
**Files:** 
- `core/additional_services.py` (tile rendering)
- `assets/css/theme.css` (styles)

**Add to CSS:**
```css
/* Personalized tile gradient */
.service-tile-personalized {
    background: linear-gradient(135deg, 
        rgba(59, 130, 246, 0.1) 0%, 
        rgba(147, 197, 253, 0.05) 100%);
    border: 2px solid rgba(59, 130, 246, 0.3);
}

.service-tile-navi-recommended {
    background: linear-gradient(135deg, 
        rgba(34, 197, 94, 0.1) 0%, 
        rgba(134, 239, 172, 0.05) 100%);
    border: 2px solid rgba(34, 197, 94, 0.3);
}

.personalized-label {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 8px;
}

.label-personalized {
    background: rgba(59, 130, 246, 0.2);
    color: #1e40af;
}

.label-navi {
    background: rgba(34, 197, 94, 0.2);
    color: #15803d;
}
```

**Update tile rendering:**
```python
def render_service_tile(service, is_personalized=False, is_navi_recommended=False):
    css_class = "service-tile"
    label = None
    
    if is_navi_recommended:
        css_class += " service-tile-navi-recommended"
        label = "Navi Recommended"
    elif is_personalized:
        css_class += " service-tile-personalized"
        label = "Personalized for You"
    
    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
    
    if label:
        st.markdown(
            f'<span class="personalized-label label-{"navi" if is_navi_recommended else "personalized"}">'
            f'{label}</span>',
            unsafe_allow_html=True
        )
    
    # ... rest of tile content
```

---

### Task 3: Cost of Care Adjustments Table
**Files:**
- `products/cost_planner_v2/expert_review.py` (or cost breakdown view)
- `products/cost_planner_v2/utils/cost_calculator.py`

**Define flag mappings:**
```python
# In cost_calculator.py or config
COST_ADJUSTMENTS = {
    "mobility_limited": {
        "percentage": 0.15,
        "label": "Mobility / Transfer Issues",
        "rationale": "Need lift equipment and additional staff"
    },
    "falls_risk": {
        "percentage": 0.15,
        "label": "Mobility / Transfer Issues",
        "rationale": "Need lift equipment and additional staff"
    },
    "memory_support": {
        "percentage": 0.20,
        "label": "Severe Cognitive Decline",
        "rationale": "Specialized memory care and behavior management"
    },
    "behavioral_concerns": {
        "percentage": 0.20,
        "label": "Severe Cognitive Decline",
        "rationale": "Specialized memory care and behavior management"
    },
    "adl_support_high": {
        "percentage": 0.10,
        "label": "High ADL Support",
        "rationale": "Extensive help with daily activities"
    },
    "medication_management": {
        "percentage": 0.08,
        "label": "Complex Medication",
        "rationale": "Professional medication oversight required"
    },
    "chronic_conditions": {
        "percentage": 0.12,
        "label": "Chronic Conditions",
        "rationale": "Ongoing medical coordination and monitoring"
    },
    "safety_concerns": {
        "percentage": 0.10,
        "label": "Safety Concerns",
        "rationale": "Enhanced supervision and environmental modifications"
    },
    "memory_care_high_acuity": {
        "percentage": 0.25,
        "label": "High-Acuity Memory Care",
        "rationale": "Always applied for this tier"
    }
}
```

**Calculate cumulative adjustments:**
```python
def calculate_cost_with_adjustments(base_cost, flags):
    """
    Calculate final cost with cumulative flag adjustments.
    
    Args:
        base_cost: Base monthly cost (e.g., 5200)
        flags: List of flag keys (e.g., ['mobility_limited', 'adl_support_high'])
    
    Returns:
        dict with final_cost, adjustments list, total_percentage
    """
    running_cost = base_cost
    adjustments = []
    
    # Deduplicate flags (same adjustment may come from multiple flags)
    seen_labels = set()
    
    for flag in flags:
        if flag in COST_ADJUSTMENTS:
            adjustment = COST_ADJUSTMENTS[flag]
            label = adjustment["label"]
            
            # Skip if we've already applied this adjustment
            if label in seen_labels:
                continue
            
            seen_labels.add(label)
            
            previous_cost = running_cost
            running_cost *= (1 + adjustment["percentage"])
            increase = running_cost - previous_cost
            
            adjustments.append({
                "label": label,
                "percentage": adjustment["percentage"],
                "rationale": adjustment["rationale"],
                "increase": increase,
                "running_total": running_cost
            })
    
    return {
        "base_cost": base_cost,
        "final_cost": running_cost,
        "adjustments": adjustments,
        "total_percentage": (running_cost - base_cost) / base_cost
    }
```

**Render adjustments table:**
```python
def render_cost_adjustments_table(cost_breakdown):
    """Render the Cost of Care Adjustments table."""
    
    if not cost_breakdown["adjustments"]:
        return
    
    st.markdown("### 💰 Cost of Care Adjustments")
    st.caption("These adjustments reflect your specific care needs. All add-ons are cumulative.")
    
    # Build table data
    table_data = []
    for adj in cost_breakdown["adjustments"]:
        table_data.append({
            "Condition": adj["label"],
            "Add-On %": f"+{adj['percentage']*100:.0f}%",
            "Monthly Increase": f"${adj['increase']:,.0f}",
            "Rationale": adj["rationale"]
        })
    
    # Display as dataframe
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Base Cost", f"${cost_breakdown['base_cost']:,.0f}/mo")
    with col2:
        st.metric(
            "Total Adjustments", 
            f"+{cost_breakdown['total_percentage']*100:.1f}%",
            delta=f"${cost_breakdown['final_cost'] - cost_breakdown['base_cost']:,.0f}"
        )
    with col3:
        st.metric("Final Cost", f"${cost_breakdown['final_cost']:,.0f}/mo")
```

---

## 🗺️ Integration Points

### Where to Get Data

**GCP Flags:**
```python
# From handoff data
handoff = st.session_state.get("handoff", {})
gcp_data = handoff.get("gcp", {})
flags = gcp_data.get("flags", {})

# Example flags:
# {
#   "mobility_limited": True,
#   "falls_risk": True,
#   "adl_support_high": True,
#   ...
# }
```

**GCP Progress:**
```python
gcp_state = st.session_state.get("gcp_v4", {})
progress = gcp_state.get("progress", 0)
is_complete = progress >= 100
```

**Cost Planner Progress:**
```python
cost_state = st.session_state.get("cost_v2_modules", {})
all_complete = all(
    module.get("status") == "completed"
    for module in cost_state.values()
)
```

---

## 🧪 Testing Checklist

### Navi Panel
- [ ] New user → Continue opens GCP
- [ ] GCP complete → Continue opens Cost Planner
- [ ] Both complete → Continue opens scheduling
- [ ] Navi text updates dynamically
- [ ] Alert shows when additional services flagged

### Additional Services
- [ ] Tiles with flags show gradient overlay
- [ ] Correct label displays ("Personalized" or "Navi Recommended")
- [ ] Standard tiles remain unchanged
- [ ] Gradient is subtle and professional

### Cost Adjustments
- [ ] Table appears in Cost Breakdown
- [ ] All active flags listed
- [ ] Percentages calculate correctly (cumulative)
- [ ] Rationale text displays
- [ ] Summary metrics show base → final
- [ ] No duplicate adjustments

---

## 📁 Quick File Reference

```
Key Files to Edit:
├── hubs/concierge.py                          # Navi panel
├── core/additional_services.py                # Tile personalization
├── assets/css/theme.css                       # Styles
├── products/cost_planner_v2/expert_review.py  # Cost breakdown
└── products/cost_planner_v2/utils/cost_calculator.py  # Calculations
```

---

**Ready to implement!** Start with Task 1 (Navi logic), then Task 2 (tiles), then Task 3 (cost table).
