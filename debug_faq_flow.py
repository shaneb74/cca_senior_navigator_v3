"""
Debug script to trace MCIP state through FAQ navigation flow.
Add this to pages to see what's happening.
"""

import streamlit as st
import json

def debug_mcip_state(location: str):
    """Print MCIP state at a specific location in the flow."""
    st.write(f"### DEBUG: {location}")
    
    # Check if mcip exists
    if "mcip" in st.session_state:
        mcip = st.session_state["mcip"]
        st.write("**MCIP State:**")
        st.json({
            "care_recommendation_status": mcip.get("care_recommendation", {}).get("status"),
            "care_recommendation_exists": bool(mcip.get("care_recommendation")),
            "journey_completed": mcip.get("journey", {}).get("completed_products", []),
            "journey_unlocked": mcip.get("journey", {}).get("unlocked_products", [])
        })
    else:
        st.warning("NO MCIP STATE")
    
    # Check if mcip_contracts exists
    if "mcip_contracts" in st.session_state:
        contracts = st.session_state["mcip_contracts"]
        st.write("**MCIP Contracts (Persistence):**")
        st.json({
            "care_recommendation_status": contracts.get("care_recommendation", {}).get("status"),
            "care_recommendation_exists": bool(contracts.get("care_recommendation")),
            "journey_completed": contracts.get("journey", {}).get("completed_products", []),
            "journey_unlocked": contracts.get("journey", {}).get("unlocked_products", [])
        })
    else:
        st.warning("NO MCIP CONTRACTS")
    
    st.write("---")


# Add these calls to your pages:
# 
# In hubs/concierge.py at the START of render():
#   from debug_faq_flow import debug_mcip_state
#   debug_mcip_state("Hub START - before MCIP.initialize()")
#
# In hubs/concierge.py AFTER MCIP.initialize():
#   debug_mcip_state("Hub AFTER - after MCIP.initialize()")
#
# In pages/faq.py at the START of render():
#   from debug_faq_flow import debug_mcip_state
#   debug_mcip_state("FAQ START - before reading MCIP")
#
# In pages/faq.py AFTER reading MCIP:
#   debug_mcip_state("FAQ AFTER - after reading MCIP")
