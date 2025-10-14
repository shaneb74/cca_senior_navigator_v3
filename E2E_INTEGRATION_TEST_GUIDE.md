# End-to-End Integration Test Guide

> **Testing GCP v4 → MCIP → Cost Planner v2 Handoff**

This guide walks through testing the complete integration to verify the universal product interface works correctly.

---

## Test Objectives

✅ **GCP v4 publishes to MCIP** - CareRecommendation contract stored  
✅ **MCIP fires events** - Event system notifies subscribers  
✅ **Cost Planner v2 gate works** - Blocks without GCP, passes with GCP  
✅ **Tier propagates correctly** - Care tier flows from GCP to Cost Planner  
✅ **Cost Planner publishes to MCIP** - FinancialProfile contract stored  
✅ **Clean boundaries maintained** - No direct state reads between products  

---

## Prerequisites

1. **Start Streamlit**: `streamlit run app.py`
2. **Fresh session**: Clear browser cache or use incognito mode
3. **Debug mode**: Enable to see MCIP state

```python
# In browser console or add to app.py:
st.session_state["debug_mode"] = True
```

---

## Test Flow

### Step 1: Verify Cost Planner Gate (No GCP)

**Goal**: Confirm Cost Planner v2 correctly blocks access without GCP recommendation

**Actions**:
1. Navigate to `http://localhost:8501?page=cost_v2`
2. Observe the gate screen

**Expected Results**:
- ✅ Gate screen displays with message: "Complete Your Guided Care Plan First"
- ✅ Friendly explanation of why GCP is needed
- ✅ Button: "Start Guided Care Plan"
- ✅ Button: "Return to Hub"
- ✅ NO error messages
- ✅ NO access to Cost Planner modules

**Verification**:
```python
# In Streamlit sidebar or debug panel:
import streamlit as st
from core.mcip import MCIP

# Should return None (no recommendation yet)
rec = MCIP.get_care_recommendation()
st.write("Recommendation:", rec)  # Should be None
```

**Screenshot**: Save screenshot as `test_1_cost_gate.png`

---

### Step 2: Complete GCP v4 Assessment

**Goal**: Complete GCP v4 and verify it publishes to MCIP

**Actions**:
1. Click "Start Guided Care Plan" button (or navigate to `?page=gcp_v4`)
2. Complete the care assessment module:
   - **About You**: Age 75-84, Living alone
   - **Medication & Mobility**: Moderate meds, Uses walker, One fall
   - **Cognition**: Moderate memory issues
   - **Daily Living**: Regular help needed, Multiple ADLs/IADLs
3. Reach results page
4. Observe publishing confirmation

**Expected Results**:
- ✅ Module renders with question screens
- ✅ Progress indicator updates
- ✅ Results screen shows care recommendation
- ✅ Success message: "Your care recommendation has been saved!"
- ✅ Buttons: "Calculate Costs" and "Return to Hub"
- ✅ NO errors during publishing

**Verification**:
```python
# Check MCIP state after completion
from core.mcip import MCIP

rec = MCIP.get_care_recommendation()
st.write("Recommendation:", rec)

# Expected fields:
# - tier: "assisted_living" (or other tier based on answers)
# - tier_score: float value
# - confidence: float 0.0-1.0
# - flags: list of flag dicts
# - rationale: list of strings
# - next_step: dict with product/route/label

# Check journey state
st.write("GCP Complete:", MCIP.is_product_complete("gcp"))  # Should be True
```

**Screenshot**: Save screenshot as `test_2_gcp_complete.png`

---

### Step 3: Verify Cost Planner Gate Passes

**Goal**: Confirm Cost Planner v2 now allows access after GCP completion

**Actions**:
1. Click "Calculate Costs" button (or navigate to `?page=cost_v2`)
2. Observe that gate no longer appears

**Expected Results**:
- ✅ Gate does NOT appear
- ✅ Care context box displays at top:
  - "Based on your Guided Care Plan:"
  - Recommended Care Level: {tier}
  - Confidence: {percentage}
- ✅ Module hub interface loads
- ✅ Financial preview shows sample costs

**Verification**:
```python
# Verify gate check logic
from core.mcip import MCIP

rec = MCIP.get_care_recommendation()
st.write("Gate should pass:", rec is not None)  # Should be True
st.write("Care tier:", rec.tier)  # Should match GCP result
```

**Screenshot**: Save screenshot as `test_3_cost_unlocked.png`

---

### Step 4: Review Tier-Based Cost Calculation

**Goal**: Verify care tier from GCP correctly influences cost estimates

**Actions**:
1. Review the care context display
2. Check the cost preview metrics
3. Verify costs match the tier

**Expected Results**:
- ✅ Care tier label matches GCP recommendation
- ✅ Base care cost appropriate for tier:
  - Independent: $0
  - In-Home: ~$3,500/mo
  - Assisted Living: ~$4,500/mo
  - Memory Care: ~$6,500/mo
- ✅ Additional services vary by tier
- ✅ Tier-specific modules shown (e.g., care_hours only for in-home)

**Verification**:
```python
# Compare GCP tier to Cost Planner context
from core.mcip import MCIP

rec = MCIP.get_care_recommendation()
st.write("GCP Tier:", rec.tier)

# Check if hub received correct tier
# (Look at care context display on page)
```

**Screenshot**: Save screenshot as `test_4_tier_costs.png`

---

### Step 5: Publish Financial Profile to MCIP

**Goal**: Complete Cost Planner and verify it publishes to MCIP

**Actions**:
1. Click "Publish Financial Profile to MCIP" button
2. Observe publishing confirmation
3. Check completion screen

**Expected Results**:
- ✅ Success message: "Financial profile published!"
- ✅ Page updates to show completion screen
- ✅ Financial summary displays:
  - Base Care Cost
  - Additional Services
  - Total Monthly Cost
  - Funding sources breakdown
  - Funding gap/surplus
- ✅ Long-term projections (1yr, 3yr, 5yr)
- ✅ Next steps buttons: "Schedule Advisor Call" and "Return to Hub"

**Verification**:
```python
# Check MCIP state after Cost Planner completion
from core.mcip import MCIP

financial = MCIP.get_financial_profile()
st.write("Financial Profile:", financial)

# Expected fields:
# - base_care_cost: float
# - additional_services: float
# - total_monthly_cost: float
# - annual_cost: float
# - funding_sources: dict
# - funding_gap: float
# - care_tier: string (should match GCP tier)

# Check journey state
st.write("Cost Planner Complete:", MCIP.is_product_complete("cost_planner"))  # Should be True

# Verify care tier matches
rec = MCIP.get_care_recommendation()
st.write("Tiers match:", financial.care_tier == rec.tier)  # Should be True
```

**Screenshot**: Save screenshot as `test_5_financial_published.png`

---

### Step 6: Verify MCIP State Consistency

**Goal**: Confirm both products published correctly and data is consistent

**Actions**:
1. Check MCIP state in debug panel or sidebar

**Expected Results**:
- ✅ Both CareRecommendation and FinancialProfile exist in MCIP
- ✅ Care tiers match between products
- ✅ Journey state shows both products complete
- ✅ Timestamps indicate publication order (GCP before Cost Planner)

**Verification**:
```python
# Complete MCIP state check
from core.mcip import MCIP
import streamlit as st

st.markdown("### 🔍 MCIP State Verification")

# Care Recommendation
rec = MCIP.get_care_recommendation()
if rec:
    st.success("✅ Care Recommendation exists")
    st.json({
        "tier": rec.tier,
        "confidence": rec.confidence,
        "generated_at": rec.generated_at,
        "version": rec.version
    })
else:
    st.error("❌ Care Recommendation missing")

# Financial Profile
financial = MCIP.get_financial_profile()
if financial:
    st.success("✅ Financial Profile exists")
    st.json({
        "care_tier": financial.care_tier,
        "total_monthly_cost": financial.total_monthly_cost,
        "generated_at": financial.generated_at,
        "version": financial.version
    })
else:
    st.error("❌ Financial Profile missing")

# Consistency checks
if rec and financial:
    st.markdown("### ✅ Consistency Checks")
    st.write("Tiers match:", rec.tier == financial.care_tier)
    st.write("GCP complete:", MCIP.is_product_complete("gcp"))
    st.write("Cost Planner complete:", MCIP.is_product_complete("cost_planner"))

# Journey state
journey = st.session_state.get("mcip", {}).get("journey", {})
st.markdown("### 📊 Journey State")
st.json(journey)
```

**Screenshot**: Save screenshot as `test_6_mcip_state.png`

---

## Success Criteria

### ✅ Gate Functionality
- [ ] Cost Planner blocks access without GCP recommendation
- [ ] Cost Planner allows access after GCP completion
- [ ] Friendly gate messaging (not just "locked")
- [ ] Clear path forward (Start GCP button works)

### ✅ Data Flow
- [ ] GCP publishes CareRecommendation to MCIP
- [ ] Cost Planner reads recommendation from MCIP
- [ ] Care tier propagates correctly
- [ ] Cost Planner publishes FinancialProfile to MCIP
- [ ] Both contracts stored in `st.session_state["mcip"]`

### ✅ Clean Boundaries
- [ ] Cost Planner never reads `st.session_state["gcp"]` directly
- [ ] Cost Planner never reads `st.session_state["gcp_v4"]` directly
- [ ] All cross-product data flows through MCIP
- [ ] No direct state coupling between products

### ✅ Journey Orchestration
- [ ] MCIP.mark_product_complete() called by both products
- [ ] MCIP.is_product_complete() returns correct state
- [ ] Journey state tracks completion
- [ ] Timestamps indicate proper sequence

### ✅ User Experience
- [ ] No errors or warnings during flow
- [ ] Smooth transitions between products
- [ ] Clear visual connection (care context display)
- [ ] Next steps buttons work correctly

---

## Test Results Template

```markdown
## Test Results - GCP v4 → MCIP → Cost Planner v2

**Date**: YYYY-MM-DD  
**Tester**: [Name]  
**Branch**: feature/cost_planner_v2  
**Commit**: [hash]

### Step 1: Cost Planner Gate (No GCP)
- Status: ✅ PASS / ❌ FAIL
- Notes: [Observations]

### Step 2: Complete GCP v4
- Status: ✅ PASS / ❌ FAIL
- Recommended Tier: [tier]
- Confidence: [percentage]
- Notes: [Observations]

### Step 3: Cost Planner Gate Passes
- Status: ✅ PASS / ❌ FAIL
- Notes: [Observations]

### Step 4: Tier-Based Costs
- Status: ✅ PASS / ❌ FAIL
- Tier Match: ✅ YES / ❌ NO
- Notes: [Observations]

### Step 5: Financial Profile Published
- Status: ✅ PASS / ❌ FAIL
- Total Monthly Cost: $[amount]
- Notes: [Observations]

### Step 6: MCIP State Consistency
- Status: ✅ PASS / ❌ FAIL
- Tier Consistency: ✅ YES / ❌ NO
- Both Products Complete: ✅ YES / ❌ NO
- Notes: [Observations]

### Overall Result
- ✅ ALL TESTS PASSED
- ❌ TESTS FAILED: [list failed tests]

### Issues Found
1. [Issue description]
2. [Issue description]

### Screenshots
- test_1_cost_gate.png
- test_2_gcp_complete.png
- test_3_cost_unlocked.png
- test_4_tier_costs.png
- test_5_financial_published.png
- test_6_mcip_state.png
```

---

## Troubleshooting

### Issue: Cost Planner gate doesn't pass after GCP completion

**Possible Causes**:
1. GCP didn't publish to MCIP (check for error messages)
2. Publishing flag not set correctly
3. Navigation happened too fast (before state updated)

**Solution**:
- Check `MCIP.get_care_recommendation()` returns data
- Look for success message after GCP completion
- Try navigating manually to `?page=cost_v2` instead of button

### Issue: Care tier mismatch between GCP and Cost Planner

**Possible Causes**:
1. Cost Planner reading wrong state
2. GCP published incorrect tier
3. Tier name mapping issue

**Solution**:
- Verify `rec.tier` matches expected value
- Check `financial.care_tier` matches `rec.tier`
- Look for tier mapping in logic.py

### Issue: Financial profile not publishing

**Possible Causes**:
1. Required fields missing
2. Dataclass validation error
3. MCIP publish method error

**Solution**:
- Check error messages in UI
- Verify all FinancialProfile fields present
- Check browser console for JavaScript errors

---

## Next Steps After Testing

If all tests pass:
1. ✅ Document test results
2. ✅ Commit test documentation
3. ✅ Move to Phase 4: Update Concierge Hub for polymorphic display

If tests fail:
1. ❌ Document failures
2. ❌ Create bug fix tasks
3. ❌ Fix issues and re-test

---

**Ready to test!** 🚀
