"""
Debug script for Additional Services flag detection

Run this in a Streamlit session to see what flags are present and
why services aren't being triggered.

Usage:
1. Complete GCP with some answers that should trigger flags
2. Go to Concierge Hub
3. Open Streamlit terminal and run:
   streamlit run debug_additional_services.py
"""

import streamlit as st
from core.mcip import MCIP
from core.additional_services import _ctx, _visible, _passes, REGISTRY

st.title("🔍 Additional Services Debug")

# Initialize MCIP
MCIP.initialize()

# Get context
ctx = _ctx()

st.header("1. Context Flags")
st.write("These are all the flags currently in the system:")
st.json(ctx.get("flags", {}))

st.header("2. MCIP Care Recommendation")
care_rec = MCIP.get_care_recommendation()
if care_rec:
    st.write(f"**Tier:** {care_rec.tier}")
    st.write(f"**Confidence:** {care_rec.confidence}")
    st.write("**Flags from CareRecommendation:**")
    if care_rec.flags:
        for flag in care_rec.flags:
            st.write(f"  - {flag}")
    else:
        st.warning("No flags in CareRecommendation!")
else:
    st.error("No CareRecommendation found!")

st.header("3. Legacy Handoff Data")
handoff = st.session_state.get("handoff", {})
st.write("Handoff data in session state:")
st.json(handoff)

st.header("4. Service Visibility Check")

# Check OMCARE
st.subheader("OMCARE (Medication Management)")
omcare = next((s for s in REGISTRY if s["key"] == "omcare"), None)
if omcare:
    st.write("**Visible When Rules:**")
    for rule in omcare.get("visible_when", []):
        st.write(f"  - {rule}")
        passes = _passes(rule, ctx)
        st.write(f"    → **Passes:** {passes}")
    
    is_visible = _visible(omcare, ctx)
    if is_visible:
        st.success("✅ OMCARE should be VISIBLE")
    else:
        st.error("❌ OMCARE is HIDDEN (no rules passed)")
else:
    st.error("OMCARE not found in REGISTRY!")

st.markdown("---")

# Check SeniorLife AI
st.subheader("SeniorLife AI")
seniorlife = next((s for s in REGISTRY if s["key"] == "seniorlife_ai"), None)
if seniorlife:
    st.write("**Visible When Rules:**")
    for rule in seniorlife.get("visible_when", []):
        st.write(f"  - {rule}")
        passes = _passes(rule, ctx)
        st.write(f"    → **Passes:** {passes}")
    
    is_visible = _visible(seniorlife, ctx)
    if is_visible:
        st.success("✅ SeniorLife AI should be VISIBLE")
    else:
        st.error("❌ SeniorLife AI is HIDDEN (no rules passed)")
else:
    st.error("SeniorLife AI not found in REGISTRY!")

st.markdown("---")

st.header("5. Expected Flags for Triggering")
st.markdown("""
**OMCARE should appear when:**
- `meds_management_needed` = True (5-10 meds OR 10+ meds)
- `medication_risk` = True
- `medication_adherence_risk` = True

**SeniorLife AI should appear when:**
- `cognitive_risk` = True (Moderate OR Severe memory changes)
- `fall_risk` = True (Multiple falls per month)
- `cognition_risk_mild/moderate/severe` = True
- `cognitive_safety_risk` = True
""")

st.header("6. Flag Matching Test")
st.write("Checking if ANY expected flags are present:")

expected_omcare_flags = ["meds_management_needed", "medication_risk", "medication_adherence_risk"]
expected_seniorlife_flags = ["cognitive_risk", "fall_risk", "cognition_risk_mild", "cognition_risk_moderate", "cognition_risk_severe", "cognitive_safety_risk"]

current_flags = ctx.get("flags", {})

st.write("**OMCARE Flags:**")
for flag in expected_omcare_flags:
    if flag in current_flags and current_flags[flag]:
        st.success(f"  ✅ {flag} = True")
    else:
        st.error(f"  ❌ {flag} = False or missing")

st.write("**SeniorLife AI Flags:**")
for flag in expected_seniorlife_flags:
    if flag in current_flags and current_flags[flag]:
        st.success(f"  ✅ {flag} = True")
    else:
        st.error(f"  ❌ {flag} = False or missing")

st.header("7. Diagnosis")
if not current_flags:
    st.error("""
    **PROBLEM: No flags found!**
    
    Possible causes:
    1. GCP hasn't been completed yet
    2. GCP completion didn't save flags to MCIP
    3. Flag generation logic in GCP isn't working
    
    **Solution:** Check if GCP is setting flags in MCIP after completion.
    """)
elif not any(f in current_flags for f in expected_omcare_flags + expected_seniorlife_flags):
    st.warning("""
    **FLAGS PRESENT BUT WRONG NAMES**
    
    The system has flags, but they don't match what the services expect.
    
    Check:
    1. What flag names is GCP actually setting?
    2. Do the flag names in additional_services.py match GCP's flag names?
    """)
else:
    st.info("""
    **Flags look correct!**
    
    If services still aren't showing, check:
    1. Are you on the concierge hub? (services need hub="concierge")
    2. Is there a rendering issue in the UI?
    3. Check browser console for errors
    """)
