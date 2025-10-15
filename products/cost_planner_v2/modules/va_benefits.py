"""
Cost Planner v2 - VA Benefits Module

Collects information about:
- Veteran status and service era
- VA Disability Compensation
- VA Aid & Attendance benefits
- Eligibility for benefits

Returns standard contract for aggregation.
"""

import streamlit as st
from typing import Dict, Any


# VA Aid & Attendance Maximum Monthly Benefits (2025)
VA_BENEFIT_AMOUNTS = {
    "veteran_alone": 2379,
    "veteran_with_spouse": 2829,
    "spouse_of_veteran": 1537,
    "surviving_spouse": 1537
}


def render():
    """Render VA benefits assessment module."""
    
    st.title("🎖️ VA Benefits")
    st.markdown("### VA Disability and Aid & Attendance benefits")
    
    st.info("""
    This helps us determine:
    - Current VA benefits you're receiving
    - Potential eligibility for additional VA benefits
    - Aid & Attendance benefits for care costs
    """)
    
    st.markdown("---")
    
    # Initialize module state
    if "cost_v2_va_benefits" not in st.session_state:
        st.session_state.cost_v2_va_benefits = {
            "is_veteran": False,
            "veteran_relationship": "veteran_alone",
            "service_era": "not_sure",
            "has_va_disability": False,
            "va_disability_rating": "10",
            "va_disability_monthly": 0,
            "receives_aid_attendance": False,
            "aid_attendance_monthly": 0,
            "eligible_aid_attendance": False
        }
    
    # Veteran Status Section
    st.markdown("## 🎖️ Veteran Status")
    st.caption("Determine eligibility for VA benefits")
    
    is_veteran = st.checkbox(
        "Are you (or your spouse) a wartime veteran?",
        value=st.session_state.cost_v2_va_benefits["is_veteran"],
        help="Veterans and surviving spouses may qualify for benefits",
        key="is_veteran"
    )
    
    if is_veteran:
        veteran_relationship = st.selectbox(
            "Your Relationship",
            options=["veteran_alone", "veteran_with_spouse", "spouse_of_veteran", "surviving_spouse"],
            format_func=lambda x: {
                "veteran_alone": "I am the veteran",
                "veteran_with_spouse": "I am the veteran (married)",
                "spouse_of_veteran": "I am the spouse of a veteran",
                "surviving_spouse": "I am the surviving spouse"
            }[x],
            index=["veteran_alone", "veteran_with_spouse", "spouse_of_veteran", "surviving_spouse"].index(
                st.session_state.cost_v2_va_benefits["veteran_relationship"]
            ),
            key="veteran_relationship"
        )
        
        service_era = st.selectbox(
            "Service Era",
            options=["wwii", "korea", "vietnam", "gulf_war", "afghanistan_iraq", "peacetime", "not_sure"],
            format_func=lambda x: {
                "wwii": "World War II (1941-1945)",
                "korea": "Korean War (1950-1953)",
                "vietnam": "Vietnam War (1964-1975)",
                "gulf_war": "Gulf War (1990-1991)",
                "afghanistan_iraq": "Afghanistan/Iraq (2001-present)",
                "peacetime": "Peacetime service",
                "not_sure": "Not sure"
            }[x],
            index=["wwii", "korea", "vietnam", "gulf_war", "afghanistan_iraq", "peacetime", "not_sure"].index(
                st.session_state.cost_v2_va_benefits["service_era"]
            ),
            key="service_era"
        )
    else:
        veteran_relationship = "veteran_alone"
        service_era = "not_sure"
    
    st.markdown("---")
    
    # VA Disability Section
    if is_veteran:
        st.markdown("## 🏥 VA Disability Compensation")
        st.caption("Monthly disability compensation from VA")
        
        has_va_disability = st.checkbox(
            "Do you receive VA Disability Compensation?",
            value=st.session_state.cost_v2_va_benefits["has_va_disability"],
            key="has_va_disability"
        )
        
        va_disability_rating = "10"
        va_disability_monthly = 0
        
        if has_va_disability:
            va_disability_rating = st.selectbox(
                "Disability Rating Percentage",
                options=["10", "20", "30", "40", "50", "60", "70", "80", "90", "100"],
                format_func=lambda x: f"{x}%",
                index=["10", "20", "30", "40", "50", "60", "70", "80", "90", "100"].index(
                    st.session_state.cost_v2_va_benefits["va_disability_rating"]
                ),
                key="va_disability_rating"
            )
            
            va_disability_monthly = st.number_input(
                "Monthly VA Disability Payment",
                min_value=0,
                max_value=5000,
                step=10,
                value=st.session_state.cost_v2_va_benefits["va_disability_monthly"],
                help="Enter your monthly VA disability compensation",
                key="va_disability_monthly"
            )
        
        st.markdown("---")
        
        # Aid & Attendance Section
        st.markdown("## 🏛️ VA Aid & Attendance")
        st.caption("Enhanced pension for veterans needing care assistance")
        
        receives_aid_attendance = st.checkbox(
            "Do you currently receive Aid & Attendance benefits?",
            value=st.session_state.cost_v2_va_benefits["receives_aid_attendance"],
            key="receives_aid_attendance"
        )
        
        aid_attendance_monthly = 0
        eligible_aid_attendance = False
        estimated_aid_attendance = 0
        
        if receives_aid_attendance:
            aid_attendance_monthly = st.number_input(
                "Monthly Aid & Attendance Benefit",
                min_value=0,
                max_value=3000,
                step=10,
                value=st.session_state.cost_v2_va_benefits["aid_attendance_monthly"],
                help="Enter your current monthly A&A benefit",
                key="aid_attendance_monthly"
            )
        else:
            eligible_aid_attendance = st.checkbox(
                "Interested in applying for Aid & Attendance?",
                value=st.session_state.cost_v2_va_benefits["eligible_aid_attendance"],
                key="eligible_aid_attendance"
            )
            
            if eligible_aid_attendance:
                estimated_aid_attendance = VA_BENEFIT_AMOUNTS.get(veteran_relationship, 0)
                
                st.success(f"""
                ### ✅ You may be eligible for VA Aid & Attendance!
                
                **Estimated Maximum Monthly Benefit:** ${estimated_aid_attendance:,.0f}
                
                **2025 Maximum Monthly Benefits:**
                - Veteran alone: ${VA_BENEFIT_AMOUNTS['veteran_alone']:,.0f}
                - Veteran with spouse: ${VA_BENEFIT_AMOUNTS['veteran_with_spouse']:,.0f}
                - Surviving spouse: ${VA_BENEFIT_AMOUNTS['surviving_spouse']:,.0f}
                
                **Requirements:**
                - Served during wartime period
                - Need help with activities of daily living
                - Meet income and asset limits
                
                💡 **Tip:** We can connect you with VA benefit specialists to help with the application process.
                """)
    else:
        has_va_disability = False
        va_disability_rating = "10"
        va_disability_monthly = 0
        receives_aid_attendance = False
        aid_attendance_monthly = 0
        eligible_aid_attendance = False
        estimated_aid_attendance = 0
    
    st.markdown("---")
    
    # Calculate total
    total_va_benefits = va_disability_monthly + aid_attendance_monthly
    
    # Summary
    if is_veteran:
        st.markdown("## 📊 Total VA Benefits")
        st.metric("**Current Monthly Benefits**", f"${total_va_benefits:,.0f}/month")
        
        if total_va_benefits > 0:
            st.info(f"""
            💡 **VA Benefits Breakdown:**
            - Disability: ${va_disability_monthly:,.0f}
            - Aid & Attendance: ${aid_attendance_monthly:,.0f}
            """)
        elif eligible_aid_attendance:
            st.info(f"""
            💡 **Potential Monthly Benefit:**
            You may be eligible for up to ${estimated_aid_attendance:,.0f}/month in Aid & Attendance benefits!
            """)
    
    st.markdown("---")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🏠 Back to Hub", key="va_hub"):
            from core.nav import route_to
            route_to("hub_concierge")
    
    with col2:
        if st.button("← Back to Modules", key="va_back"):
            st.session_state.cost_v2_step = "modules"
            st.rerun()
    
    with col3:
        if st.button("Save & Continue →", type="primary", use_container_width=True, key="va_save"):
            # Save data to module state
            data = {
                "is_veteran": is_veteran,
                "veteran_relationship": veteran_relationship,
                "service_era": service_era,
                "has_va_disability": has_va_disability,
                "va_disability_rating": va_disability_rating,
                "va_disability_monthly": va_disability_monthly,
                "receives_aid_attendance": receives_aid_attendance,
                "aid_attendance_monthly": aid_attendance_monthly,
                "eligible_aid_attendance": eligible_aid_attendance,
                "estimated_aid_attendance": estimated_aid_attendance,
                "total_va_benefits": total_va_benefits
            }
            
            # Update session state
            st.session_state.cost_v2_va_benefits = data
            
            # Mark module complete
            if "cost_v2_modules" not in st.session_state:
                st.session_state.cost_v2_modules = {}
            
            st.session_state.cost_v2_modules["va_benefits"] = {
                "status": "completed",
                "progress": 100,
                "data": data
            }
            
            # Return to hub
            st.session_state.cost_v2_step = "modules"
            st.success("✅ VA Benefits saved!")
            st.rerun()
    
    st.caption("💾 Your progress is automatically saved")
