"""
Metrics Panel Component - Advisor performance metrics
"""
import streamlit as st
from typing import Dict, Any


def render_advisor_metrics(metrics: Dict[str, Any]):
    """Render advisor performance metrics"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        active = metrics.get('active_clients', 0)
        st.metric(
            "Active Clients",
            active,
            delta=metrics.get('active_delta', None),
            help="Total customers currently in your pipeline"
        )
    
    with col2:
        new = metrics.get('new_leads', 0)
        st.metric(
            "New This Week",
            new,
            delta=metrics.get('new_delta', None),
            help="New leads assigned in the last 7 days"
        )
    
    with col3:
        ready = metrics.get('ready_for_tour', 0)
        st.metric(
            "Ready for Tours",
            ready,
            delta=metrics.get('ready_delta', None),
            help="Customers who completed assessments and are ready for community visits"
        )
    
    with col4:
        revenue = metrics.get('monthly_revenue', 0)
        revenue_formatted = f"${revenue/1000:.1f}K" if revenue >= 1000 else f"${revenue}"
        st.metric(
            "This Month",
            revenue_formatted,
            delta=metrics.get('revenue_delta', None),
            help="Commission from closings this month"
        )


def render_team_metrics(team_metrics: Dict[str, Dict[str, Any]]):
    """Render team-wide metrics comparison"""
    
    st.subheader("👥 Team Performance")
    
    # Create comparison table
    advisors = list(team_metrics.keys())
    
    if not advisors:
        st.info("No team data available")
        return
    
    # Build metrics table
    data = []
    for advisor_name, metrics in team_metrics.items():
        data.append({
            "Advisor": advisor_name,
            "Active": metrics.get('active_clients', 0),
            "New": metrics.get('new_leads', 0),
            "Closing": metrics.get('closing', 0),
            "Revenue": f"${metrics.get('monthly_revenue', 0)/1000:.1f}K"
        })
    
    st.dataframe(data, hide_index=True, use_container_width=True)


def render_performance_chart(metrics: Dict[str, Any]):
    """Render performance trend chart"""
    
    # Mock weekly performance data
    import pandas as pd
    
    weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
    new_leads = [2, 3, 4, 3]
    tours_scheduled = [1, 2, 3, 2]
    closings = [0, 1, 0, 1]
    
    chart_data = pd.DataFrame({
        "New Leads": new_leads,
        "Tours": tours_scheduled,
        "Closings": closings
    }, index=weeks)
    
    st.subheader("📈 Monthly Trend")
    st.line_chart(chart_data)
