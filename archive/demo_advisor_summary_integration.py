"""
Integration Demo: Advisor Summary + Navi LLM System

This file demonstrates how the new Advisor Summary LLM templates 
integrate with your existing Navi LLM enhancement system.

Shows the complete flow from session data → LLM generation → UI display.
"""

from typing import Dict, Any, Optional

# Mock imports for demonstration (replace with actual imports in production)
try:
    from ai.advisor_summary_engine import AdvisorSummaryEngine
    from ai.navi_llm_engine import NaviLLMEngine, build_navi_context_from_session
    from core.flags import get_flag_value
    PRODUCTION_READY = True
except ImportError:
    PRODUCTION_READY = False
    print("[DEMO] Using mock imports - replace with actual imports in production")


def render_advisor_summary_panel():
    """
    Example function showing how to integrate advisor summary 
    generation into your existing UI flow.
    
    This would replace the deprecated PFMA/Advisor Prep modules.
    """
    print("=== Advisor Summary Panel Integration ===\n")
    
    # Check if LLM features are enabled (using existing flag system)
    if PRODUCTION_READY:
        advisor_llm_mode = get_flag_value("FEATURE_ADVISOR_SUMMARY_LLM", "off")
        navi_llm_mode = get_flag_value("FEATURE_LLM_NAVI", "off") 
    else:
        advisor_llm_mode = "adjust"  # Demo mode
        navi_llm_mode = "adjust"
    
    print(f"🎛️  Advisor LLM Mode: {advisor_llm_mode}")
    print(f"🎛️  Navi LLM Mode: {navi_llm_mode}")
    
    # Generate advisor summary drawers
    if advisor_llm_mode in ["assist", "adjust"]:
        if PRODUCTION_READY:
            # Production path
            drawers = AdvisorSummaryEngine.generate_all_drawers()
        else:
            # Demo path
            drawers = {
                "about_person": "This plan is for Margaret, who is in her late seventies and currently lives alone in the Baton Rouge area. She has limited access to nearby family and occasionally relies on neighbors for support.",
                "housing_preferences": "Margaret has expressed interest in Assisted Living communities that provide both independence and support with daily activities. Her move timeline is flexible.",
                "medical_care": "Margaret experiences moderate memory changes and mild mobility challenges. Her care plan emphasizes consistent routines and medication management.",
                "financial_overview": "Margaret's projected monthly budget for care is approximately $4,200. She is estimated to be funded for roughly four to five years of Assisted Living."
            }
        
        print("\n📋 Generated Advisor Summary Drawers:")
        for drawer_name, narrative in drawers.items():
            word_count = len(narrative.split())
            print(f"\n### {drawer_name.replace('_', ' ').title()} ({word_count} words)")
            print(f"{narrative}")
    else:
        print("\n📋 Advisor Summary: Using static fallback content")
    
    # Generate contextual Navi encouragement  
    if navi_llm_mode in ["assist", "adjust"]:
        if PRODUCTION_READY:
            # Production path
            navi_context = build_navi_context_from_session()
            navi_context.current_location = "advisor_summary"
            navi_context.product_context = {"step_type": "summary_generation"}
            
            navi_advice = NaviLLMEngine.generate_advice(navi_context)
            if navi_advice:
                navi_message = navi_advice.message
            else:
                navi_message = "Your advisor summary is ready for review."
        else:
            # Demo path
            navi_message = "Perfect! I've generated a comprehensive summary for your advisor. This covers everything we've learned about your situation, preferences, and care planning progress."
        
        print(f"\n🌟 Navi Context: {navi_message}")
    else:
        print("\n🌟 Navi: Static guidance active")
    
    print("\n" + "="*60)


def demonstrate_data_flow():
    """
    Show how data flows from different parts of the system 
    into the advisor summary generation.
    """
    print("=== Data Flow Demonstration ===\n")
    
    print("📊 Data Sources for Advisor Summary:")
    print("├── Profile Context")
    print("│   ├── person_a_name (from user input)")
    print("│   ├── person_a_age_range (from demographics)")
    print("│   ├── geo_zip (from location data)")
    print("│   └── relationship_type (from signup flow)")
    print("│")
    print("├── Guided Care Plan (GCP)")
    print("│   ├── recommended_tier (from GCP assessment)")
    print("│   ├── care_flags[] (from module responses)")
    print("│   ├── move_timeline (from preferences)")
    print("│   └── room_type (from housing preferences)")
    print("│")
    print("├── Cost Planner (CP)")
    print("│   ├── monthly_cost (from cost calculations)")
    print("│   ├── years_funded (from financial analysis)")
    print("│   ├── household_income (from income assessment)")
    print("│   └── va_benefits_eligible (from benefits check)")
    print("│")
    print("└── Session State & Flags")
    print("    ├── support_network_low (from family assessment)")
    print("    ├── home_carry (from move preferences)")
    print("    └── flag_manager_flags (from system flags)")
    
    print("\n🔄 Processing Flow:")
    print("1. AdvisorSummaryEngine.build_advisor_context_from_session()")
    print("   → Extracts all relevant data from st.session_state")
    print("   → Creates AdvisorSummaryContext dataclass")
    print("   → Handles missing data gracefully")
    print("")
    print("2. AdvisorSummaryEngine.generate_all_drawers(context)")
    print("   → Generates 4 narrative paragraphs using LLM")
    print("   → Uses structured prompts with context injection")
    print("   → Returns dict with drawer_name → narrative mapping")
    print("")
    print("3. UI Rendering")
    print("   → Display each drawer in advisor dashboard")
    print("   → Show word counts and generation timestamps")
    print("   → Provide fallback content if generation fails")


def show_integration_examples():
    """
    Show specific code examples for integrating advisor summaries
    into existing product flows.
    """
    print("=== Integration Code Examples ===\n")
    
    print("🔧 Example 1: Add to existing advisor dashboard")
    print("""
def render_advisor_dashboard():
    st.title("Advisor Dashboard")
    
    # Generate advisor summary
    from ai.advisor_summary_engine import AdvisorSummaryEngine
    drawers = AdvisorSummaryEngine.generate_all_drawers()
    
    # Display summary drawers
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### About the Person")
        st.write(drawers['about_person'])
        
        st.markdown("### Medical & Care Information") 
        st.write(drawers['medical_care'])
    
    with col2:
        st.markdown("### Housing Preferences")
        st.write(drawers['housing_preferences'])
        
        st.markdown("### Financial Overview")
        st.write(drawers['financial_overview'])
""")
    
    print("\n🔧 Example 2: Integrate with existing Navi system")
    print("""
def render_navi_with_advisor_summary():
    from core.navi import render_navi_panel_v2
    from ai.advisor_summary_engine import AdvisorSummaryEngine
    
    # Check if user has completed assessments
    gcp_complete = st.session_state.get("gcp_complete", False)
    cost_complete = st.session_state.get("financial_assessment_complete", {})
    
    if gcp_complete and cost_complete:
        # Generate summary and show Navi encouragement
        drawers = AdvisorSummaryEngine.generate_all_drawers()
        
        render_navi_panel_v2(
            title="Your advisor summary is ready!",
            reason="I've compiled everything we know about your situation.",
            encouragement={
                "icon": "📋", 
                "text": "This summary helps advisors understand your needs quickly.",
                "status": "completed"
            },
            context_chips=[f"{len(drawers)} sections generated"],
            primary_action={"label": "View Summary", "route": "advisor_summary"},
            variant="hub"
        )
    else:
        # Show progress toward summary
        render_navi_panel_v2(
            title="Building your advisor summary",
            reason="Complete your assessments to generate a comprehensive summary.",
            encouragement={
                "icon": "⏳",
                "text": "We're gathering the information advisors need to help you.",
                "status": "in_progress"
            },
            context_chips=[],
            primary_action={"label": "Continue", "route": "gcp_v4"},
            variant="hub"
        )
""")
    
    print("\n🔧 Example 3: Feature flag integration")
    print("""
def advisor_summary_with_flags():
    from core.flags import get_flag_value
    
    # Check feature flags
    advisor_mode = get_flag_value("FEATURE_ADVISOR_SUMMARY_LLM", "off")
    
    if advisor_mode == "off":
        st.write("Advisor summaries are currently disabled.")
        
    elif advisor_mode == "shadow":
        # Generate but don't show (for testing)
        drawers = AdvisorSummaryEngine.generate_all_drawers()
        st.write("Using static advisor content (LLM running in shadow mode)")
        
    elif advisor_mode in ["assist", "adjust"]:
        # Full LLM generation
        drawers = AdvisorSummaryEngine.generate_all_drawers()
        for drawer_name, narrative in drawers.items():
            st.markdown(f"### {drawer_name.replace('_', ' ').title()}")
            st.write(narrative)
""")


def main():
    """Run the complete integration demonstration."""
    print("🚀 ADVISOR SUMMARY LLM INTEGRATION DEMO")
    print("="*60)
    print()
    
    render_advisor_summary_panel()
    print()
    
    demonstrate_data_flow() 
    print()
    
    show_integration_examples()
    print()
    
    print("✅ INTEGRATION COMPLETE")
    print("\nThe Advisor Summary LLM system is ready to replace")
    print("the deprecated PFMA and Advisor Prep modules with")
    print("dynamic, contextual narratives for advisor stakeholders.")
    print("\n📚 See ADVISOR_SUMMARY_LLM_GUIDE.md for complete documentation")


if __name__ == "__main__":
    main()