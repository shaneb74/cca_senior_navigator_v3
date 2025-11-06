"""
CRM Dashboard - Advisor Command Center
Professional hub with task queues, pipeline, and team collaboration
"""
import streamlit as st
from shared.data_access.navigator_reader import NavigatorDataReader
from shared.data_access.crm_repository import CrmRepository

# Import CRM components
from apps.crm.components.metrics_panel import render_advisor_metrics, render_team_metrics
from apps.crm.components.task_queue import (
    render_action_required_queue,
    render_todays_tasks,
    render_task_queue
)
from apps.crm.components.customer_pipeline import (
    render_customer_pipeline,
    render_pipeline_summary
)

# Import mock data service
from apps.crm.services.mock_data import (
    get_mock_advisor_metrics,
    get_mock_action_required,
    get_mock_todays_tasks,
    get_mock_customer_pipeline,
    get_mock_upcoming_appointments,
    get_mock_team_metrics
)


def render():
    """Main render function for advisor hub dashboard"""
    
    # Header with advisor info
    st.title("🏢 Advisor CRM Dashboard")
    
    # Simulated advisor (in production, would come from auth)
    advisor_name = st.session_state.get('advisor_name', 'Sarah Chen')
    st.caption(f"Welcome back, **{advisor_name}** • {st.session_state.get('advisor_role', 'Senior Care Advisor')}")
    
    # Top-level metrics
    metrics = get_mock_advisor_metrics()
    render_advisor_metrics(metrics)
    
    st.markdown("---")
    
    # Main hub tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 My Tasks",
        "👥 My Customers", 
        "📊 Team View",
        "📅 Appointments"
    ])
    
    with tab1:
        render_tasks_tab()
    
    with tab2:
        render_customers_tab()
    
    with tab3:
        render_team_tab()
    
    with tab4:
        render_appointments_tab()


def render_tasks_tab():
    """Render My Tasks tab with action items and daily schedule"""
    
    st.subheader("Your Action Center")
    st.caption("Prioritized tasks and follow-ups based on customer activity")
    
    # Action Required section (urgent items)
    action_items = get_mock_action_required()
    if action_items:
        render_action_required_queue(action_items)
        st.markdown("---")
    
    # Today's Schedule
    todays_tasks = get_mock_todays_tasks()
    render_todays_tasks(todays_tasks)
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add Manual Task", use_container_width=True):
            st.session_state['show_add_task'] = True
    
    with col2:
        if st.button("📋 View All Tasks", use_container_width=True):
            st.info("Navigate to full task management (coming soon)")
    
    with col3:
        if st.button("📊 Task Analytics", use_container_width=True):
            st.info("Task completion analytics (coming soon)")


def render_customers_tab():
    """Render My Customers tab with pipeline visualization"""
    
    st.subheader("Customer Pipeline")
    st.caption("Visual workflow from lead to closing")
    
    # Get pipeline data
    pipeline = get_mock_customer_pipeline()
    
    # Pipeline summary metrics
    render_pipeline_summary(pipeline)
    
    st.markdown("---")
    
    # Visual pipeline
    render_customer_pipeline(pipeline)
    
    st.markdown("---")
    
    # Navigator integration insights
    st.subheader("🔗 Navigator Integration")
    
    # Get real Navigator data
    reader = NavigatorDataReader()
    nav_customers = reader.get_all_customers()
    
    completed_gcp = sum(1 for c in nav_customers if c.get("has_gcp_assessment"))
    completed_cost = sum(1 for c in nav_customers if c.get("has_cost_plan"))
    ready_consultation = sum(1 for c in nav_customers if c.get("has_gcp_assessment") and c.get("has_cost_plan"))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Navigator Users", len(nav_customers), help="Total customers using Navigator app")
    
    with col2:
        st.metric("Assessments Complete", completed_gcp, help="GCP assessments completed")
    
    with col3:
        st.metric("Ready for Consult", ready_consultation, help="Completed GCP + Cost Planner")
    
    if ready_consultation > 0:
        st.success(f"✨ {ready_consultation} customers ready for consultation - check Action Required!")


def render_team_tab():
    """Render Team View tab with team metrics and collaboration"""
    
    st.subheader("Team Performance Dashboard")
    st.caption("Compare metrics and workload across advisors")
    
    # Team metrics table
    team_metrics = get_mock_team_metrics()
    render_team_metrics(team_metrics)
    
    st.markdown("---")
    
    # Team insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top Performers This Month")
        
        # Sort by revenue
        sorted_advisors = sorted(
            team_metrics.items(),
            key=lambda x: x[1]['monthly_revenue'],
            reverse=True
        )
        
        for idx, (advisor, metrics) in enumerate(sorted_advisors[:3], 1):
            medal = ["🥇", "🥈", "🥉"][idx-1]
            revenue = metrics['monthly_revenue']
            st.markdown(f"{medal} **{advisor}** - ${revenue/1000:.1f}K")
    
    with col2:
        st.subheader("� Team Pipeline Health")
        
        total_active = sum(m['active_clients'] for m in team_metrics.values())
        total_closing = sum(m['closing'] for m in team_metrics.values())
        total_revenue = sum(m['monthly_revenue'] for m in team_metrics.values())
        
        st.metric("Team Active Clients", total_active)
        st.metric("Team Closing This Month", total_closing)
        st.metric("Team Revenue", f"${total_revenue/1000:.1f}K")
    
    st.markdown("---")
    
    # QuickBase integration status
    st.subheader("🔗 QuickBase Integration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("QB Sync Status", "✅ Active", help="Last synced: 5 minutes ago")
    
    with col2:
        st.metric("QB Records", "248", help="Total records in WA Clients table")
    
    with col3:
        st.metric("Sync Frequency", "Real-time", help="Auto-sync enabled")
    
    with st.expander("📋 View QuickBase Sync Details"):
        st.info("QuickBase integration allows:")
        st.markdown("""
        - ✅ Pull advisor assignments from QB WA Clients table
        - ✅ Display QB activities as tasks
        - ✅ Sync Navigator customers back to QB
        - ✅ Real-time workload distribution
        
        **Next Steps:**
        - Configure bi-directional sync settings
        - Map custom QB fields to CRM
        - Set up automated QB report generation
        """)


def render_appointments_tab():
    """Render Appointments tab with upcoming consultations"""
    
    st.subheader("Upcoming Appointments")
    st.caption("Scheduled consultations and follow-ups")
    
    # Get appointments from CRM
    crm_repo = CrmRepository()
    crm_appointments = crm_repo.list_records("appointments")
    
    # Filter for upcoming scheduled appointments
    upcoming = [a for a in crm_appointments if a.get('status', '').lower() == 'scheduled']
    
    if upcoming:
        st.success(f"📅 You have {len(upcoming)} upcoming appointments")
        
        for appt in upcoming[:5]:  # Show first 5
            customer = appt.get('customer_name', 'Unknown')
            appt_type = appt.get('appointment_type', 'Consultation')
            scheduled = appt.get('scheduled_at', 'Not scheduled')
            confirmation = appt.get('confirmation_id', 'N/A')
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{customer}** - {appt_type}")
                    st.caption(f"📅 {scheduled} • Confirmation: {confirmation}")
                
                with col2:
                    if st.button("View Details", key=f"appt_{confirmation}"):
                        st.session_state['selected_appointment'] = appt
                
                st.markdown("---")
        
        if len(upcoming) > 5:
            st.info(f"+ {len(upcoming) - 5} more appointments. View all in Appointments page.")
    else:
        st.info("📅 No upcoming appointments scheduled")
    
    # Quick actions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ Schedule New Appointment", use_container_width=True, type="primary"):
            st.switch_page("apps/crm/pages/appointments.py")
    
    with col2:
        if st.button("📅 View Full Calendar", use_container_width=True):
            st.switch_page("apps/crm/pages/appointments.py")

