"""
CRM Dashboard - Clean professional overview
"""
import streamlit as st
from shared.data_access.navigator_reader import NavigatorDataReader

def render():
    """Main render function for dashboard"""
    
    # Header
    st.title("🏢 Advisor CRM Dashboard")
    st.subheader("Professional customer management with Navigator integration")
    
    # Get metrics
    reader = NavigatorDataReader()
    customers = reader.get_all_customers()
    
    total_customers = len(customers)
    completed_gcp = sum(1 for c in customers if c.get("has_gcp_assessment"))
    completed_cost = sum(1 for c in customers if c.get("has_cost_plan"))
    ready_consultation = sum(1 for c in customers if c.get("has_gcp_assessment") and c.get("has_cost_plan"))
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Customers", total_customers)
    with col2:
        st.metric("GCP Assessments", completed_gcp)
    with col3:
        st.metric("Cost Plans", completed_cost)
    with col4:
        st.metric("Ready for Consult", ready_consultation)
    
    # Transformation summary
    st.markdown("---")
    st.markdown("## 🚀 QuickBase Transformation Complete")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### ❌ Before: QuickBase
        - 📝 218+ manual data entry fields
        - 📊 46 activity reports to maintain
        - 📋 132 community spreadsheet fields
        - ⏰ Hours of daily data entry
        """)
    
    with col2:
        st.markdown("""
        ### ✅ After: Smart CRM
        - 🤖 100% automated data from Navigator
        - 📈 AI-powered insights and recommendations
        - 🎯 Smart community matching algorithm
        - ⚡ Real-time customer journey tracking
        """)
    
    st.success("**Mission Accomplished:** Advisors transformed from data entry clerks to strategic customer guides!")

