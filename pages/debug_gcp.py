"""
Diagnostic page to check GCP and Cost Planner session state.

Add to nav.json temporarily:
{
  "key": "debug_gcp",
  "label": "Debug GCP",
  "module": "pages.debug_gcp:render"
}
"""

import streamlit as st
from pprint import pformat


def render():
    """Render debug page showing GCP and Cost Planner session state."""
    st.title("🔍 GCP & Cost Planner Debug")
    
    st.markdown("---")
    
    # GCP State
    st.markdown("## 1. GCP Module State")
    gcp_state = st.session_state.get("gcp", {})
    
    if gcp_state:
        st.success("✅ GCP state exists")
        
        # Key values
        progress = gcp_state.get("progress", 0)
        status = gcp_state.get("status", "unknown")
        care_tier = gcp_state.get("care_tier", "NOT SET")
        step = gcp_state.get("_step", "NOT SET")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Progress", f"{progress}%")
            st.metric("Status", status)
        with col2:
            st.metric("Care Tier", care_tier)
            st.metric("Current Step", step)
        
        # Check for outcomes
        outcomes = gcp_state.get("_outcomes")
        if outcomes:
            st.success("✅ Outcomes exist")
            rec = outcomes.get("recommendation", "NOT SET")
            score = outcomes.get("summary", {}).get("total_score", "NOT SET")
            tier = outcomes.get("summary", {}).get("tier", "NOT SET")
            
            st.write("**Outcomes:**")
            st.write(f"- Recommendation: `{rec}`")
            st.write(f"- Score: `{score}`")
            st.write(f"- Tier: `{tier}`")
        else:
            st.error("❌ No outcomes data found in `gcp._outcomes`")
        
        # Gate check
        st.markdown("### Cost Planner Gate Check")
        if progress >= 100:
            st.success(f"✅ GATE CHECK PASSES (progress={progress} >= 100)")
        else:
            st.error(f"❌ GATE CHECK FAILS (progress={progress} < 100)")
    else:
        st.error("❌ No GCP state found in session_state")
    
    st.markdown("---")
    
    # Handoff Data
    st.markdown("## 2. Handoff Data (for Cost Planner)")
    handoff = st.session_state.get("handoff", {})
    gcp_handoff = handoff.get("gcp", {})
    
    if gcp_handoff:
        st.success("✅ Handoff data exists")
        
        recommendation = gcp_handoff.get("recommendation", "NOT SET")
        flags = gcp_handoff.get("flags", {})
        tags = gcp_handoff.get("tags", [])
        domain_scores = gcp_handoff.get("domain_scores", {})
        
        st.write("**Handoff Data:**")
        st.write(f"- Recommendation: `{recommendation}`")
        st.write(f"- Flags: {len(flags)} flags")
        st.write(f"- Tags: {len(tags)} tags")
        st.write(f"- Domain Scores: {len(domain_scores)} domains")
        
        if recommendation and recommendation != "NOT SET":
            st.success(f"✅ Recommendation ready for Cost Planner: '{recommendation}'")
        else:
            st.error("❌ Recommendation not set in handoff")
    else:
        st.error("❌ No handoff['gcp'] data found")
    
    st.markdown("---")
    
    # Tiles State
    st.markdown("## 3. Tiles State")
    tiles = st.session_state.get("tiles", {})
    gcp_tile = tiles.get("gcp", {})
    
    if gcp_tile:
        st.success("✅ GCP tile state exists")
        
        tile_progress = gcp_tile.get("progress", 0)
        tile_status = gcp_tile.get("status", "unknown")
        last_step = gcp_tile.get("last_step", "NOT SET")
        
        st.write("**Tile Data:**")
        st.write(f"- Progress: `{tile_progress}%`")
        st.write(f"- Status: `{tile_status}`")
        st.write(f"- Last Step: `{last_step}`")
    else:
        st.warning("⚠️ No GCP tile state found (may not have started GCP yet)")
    
    st.markdown("---")
    
    # Full session state (expandable)
    st.markdown("## 4. Full Session State")
    
    with st.expander("Show Full session_state['gcp']"):
        if gcp_state:
            # Create a sanitized version without _outcomes (too large)
            display_state = {k: v for k, v in gcp_state.items() if k != "_outcomes"}
            display_state["_outcomes"] = "{ ... truncated for display ... }" if "_outcomes" in gcp_state else "NOT SET"
            st.code(pformat(display_state), language="python")
        else:
            st.code("{}", language="python")
    
    with st.expander("Show Full session_state['handoff']['gcp']"):
        if gcp_handoff:
            st.code(pformat(gcp_handoff), language="python")
        else:
            st.code("{}", language="python")
    
    st.markdown("---")
    
    # Actions
    st.markdown("## 5. Test Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Page"):
            st.rerun()
    
    with col2:
        if st.button("🏠 Go to Hub"):
            st.query_params.clear()
            st.query_params["page"] = "concierge"
            st.rerun()
    
    with col3:
        if st.button("🧮 Go to Cost Planner"):
            st.query_params.clear()
            st.query_params["page"] = "cost"
            st.rerun()
    
    st.markdown("---")
    
    # Diagnostics
    st.markdown("## 6. Diagnostics")
    
    # Check what would happen if user tries to access Cost Planner
    gcp_progress_check = float(st.session_state.get("gcp", {}).get("progress", 0))
    
    st.write("**Cost Planner Access Check:**")
    st.code(f"""
# This is what Cost Planner does:
gcp_progress = float(st.session_state.get("gcp", {{}}).get("progress", 0))
# Result: {gcp_progress_check}

if gcp_progress < 100:
    # Show "GCP Required" message
    # Result: {'BLOCKED' if gcp_progress_check < 100 else 'ALLOWED'}
""", language="python")
    
    if gcp_progress_check >= 100:
        st.success("✅ Cost Planner should be ACCESSIBLE")
    else:
        st.error(f"❌ Cost Planner is BLOCKED (progress={gcp_progress_check} < 100)")
        st.info("**To fix:** Complete the GCP assessment to the results page")
    
    st.markdown("---")
    
    # Quick fix button
    if gcp_progress_check < 100:
        st.markdown("### 🔧 Quick Fix (Dev Only)")
        st.caption("This will manually set progress to 100 to unblock Cost Planner")
        
        if st.button("⚡ Force GCP to 100% Complete", type="primary"):
            st.session_state.setdefault("gcp", {})["progress"] = 100.0
            st.session_state["gcp"]["status"] = "done"
            
            # Also set a dummy handoff
            st.session_state.setdefault("handoff", {})["gcp"] = {
                "recommendation": "Assisted Living",
                "flags": {},
                "tags": [],
                "domain_scores": {}
            }
            
            st.success("✅ Forced GCP to 100% complete!")
            st.info("Refresh the page to see changes")
            st.rerun()
