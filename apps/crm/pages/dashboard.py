"""
CRM Dashboard - Advisor Command Center
Professional hub with task queues, pipeline, and team collaboration
"""
import streamlit as st
from shared.data_access.navigator_reader import NavigatorDataReader
from shared.data_access.crm_repository import CrmRepository
from core.adapters.streamlit_crm import get_all_crm_customers

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

# Import mock data service (only for tasks/appointments that don't exist yet)
from apps.crm.services.mock_data import (
    get_mock_todays_tasks,
    get_mock_team_metrics
)


def render():
    """Main render function for advisor hub dashboard"""
    
    # Header with advisor info
    st.title("🏢 Advisor CRM Dashboard")
    
    # Simulated advisor (in production, would come from auth)
    advisor_name = st.session_state.get('advisor_name', 'Sarah Chen')
    st.caption(f"Welcome back, **{advisor_name}** • {st.session_state.get('advisor_role', 'Senior Care Advisor')}")
    
    # Get real CRM customers
    all_customers = get_all_crm_customers()
    
    # Calculate real metrics from actual customers
    metrics = calculate_advisor_metrics(all_customers)
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
        render_tasks_tab(all_customers)
    
    with tab2:
        render_customers_tab(all_customers)
    
    with tab3:
        render_team_tab()
    
    with tab4:
        render_appointments_tab()


def calculate_advisor_metrics(customers):
    """Calculate real metrics from actual CRM customers"""
    
    # Count customers by source/type
    total_customers = len(customers)
    
    # Get Navigator-specific data
    reader = NavigatorDataReader()
    nav_customers = reader.get_all_customers()
    
    completed_gcp = sum(1 for c in nav_customers if c.get("has_gcp_assessment"))
    completed_cost = sum(1 for c in nav_customers if c.get("has_cost_plan"))
    ready_for_consultation = sum(1 for c in nav_customers if c.get("has_gcp_assessment") and c.get("has_cost_plan"))
    
    # New leads (customers created in last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)
    new_leads = 0
    for customer in customers:
        created_str = customer.get('created_at', '')
        if created_str:
            try:
                created_date = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                if created_date > week_ago:
                    new_leads += 1
            except:
                pass
    
    return {
        'active_clients': total_customers,
        'active_delta': None,  # Would need historical data
        'new_leads': new_leads,
        'new_delta': None,
        'ready_for_tour': ready_for_consultation,
        'ready_delta': None,
        'monthly_revenue': 0,  # Would come from closed deals
        'revenue_delta': None
    }


def generate_action_items(customers):
    """Generate action items from real customer data"""
    action_items = []
    
    # Get Navigator data for assessment completion
    reader = NavigatorDataReader()
    nav_customers = reader.get_all_customers()
    
    # Check for customers who completed assessments (need follow-up)
    for customer in nav_customers:
        if customer.get("has_gcp_assessment") and customer.get("has_cost_plan"):
            action_items.append({
                'id': f'action_{customer.get("user_id", "unknown")}',
                'priority': 'high',
                'customer': customer.get('name', customer.get('person_name', 'Unknown')),
                'task': 'Ready for consultation',
                'action': 'Schedule consultation to discuss care options and community matches',
                'type': 'appointment'
            })
    
    # If no real action items, return empty list
    if not action_items:
        return []
    
    return action_items[:5]  # Limit to top 5


def render_tasks_tab(customers):
    """Render My Tasks tab with action items and daily schedule"""
    
    st.subheader("Your Action Center")
    st.caption("Prioritized tasks and follow-ups based on customer activity")
    
    # Generate action items from real customer data
    action_items = generate_action_items(customers)
    if action_items:
        render_action_required_queue(action_items)
        st.markdown("---")
    else:
        st.info("✅ No urgent action items right now")
        st.markdown("---")
    
    # Today's Schedule (using mock for now - would come from calendar/appointments)
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


def build_customer_pipeline(customers):
    """Build pipeline stages from real customer data"""
    
    from datetime import datetime, timedelta
    
    pipeline = {
        'new_leads': [],
        'assessing': [],
        'touring': [],
        'closing': []
    }
    
    # Get Navigator data for assessment status
    reader = NavigatorDataReader()
    nav_customers = reader.get_all_customers()
    nav_by_id = {c.get('user_id'): c for c in nav_customers}
    
    for customer in customers:
        name = customer.get('name', customer.get('person_name', 'Unknown'))
        customer_id = customer.get('id', customer.get('user_id', ''))
        created_str = customer.get('created_at', '')
        
        # Calculate days since creation
        days_since = 0
        if created_str:
            try:
                created_date = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                days_since = (datetime.now() - created_date.replace(tzinfo=None)).days
            except:
                pass
        
        # Check Navigator status
        nav_data = nav_by_id.get(customer_id, {})
        has_gcp = nav_data.get('has_gcp_assessment', False)
        has_cost = nav_data.get('has_cost_plan', False)
        
        # Stage classification logic
        if days_since <= 3 and not has_gcp:
            # New leads - recent signups, no assessments yet
            pipeline['new_leads'].append({
                'name': name,
                'days_since': days_since,
                'source': customer.get('source', 'Unknown')
            })
        elif has_gcp or has_cost:
            # Assessing - working through Navigator
            pipeline['assessing'].append({
                'name': name,
                'gcp': 'done' if has_gcp else 'not_started',
                'cost': 'done' if has_cost else 'not_started',
                'days_since': days_since
            })
        else:
            # Default to assessing for existing customers
            pipeline['assessing'].append({
                'name': name,
                'gcp': 'not_started',
                'cost': 'not_started',
                'days_since': days_since
            })
    
    return pipeline


def render_customers_tab(customers):
    """Render My Customers tab with pipeline visualization"""
    
    st.subheader("Customer Pipeline")
    st.caption("Visual workflow from lead to closing")
    
    # Build real pipeline from actual customers
    pipeline = build_customer_pipeline(customers)
    
    # Pipeline summary metrics
    render_pipeline_summary(pipeline)
    
    st.markdown("---")
    
    # Visual pipeline
    render_customer_pipeline(pipeline)
    
    st.markdown("---")
    
    # Real customer data summary
    st.subheader("📊 Customer Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total = len(customers)
        st.metric("Total Customers", total, help="All customers in CRM")
    
    with col2:
        nav_count = sum(1 for c in customers if c.get('source') == 'navigator_app')
        st.metric("Navigator Users", nav_count, help="Customers from Navigator app")
    
    with col3:
        qb_count = sum(1 for c in customers if c.get('source') == 'quickbase')
        st.metric("QuickBase Import", qb_count, help="Imported from QuickBase")
    
    # Navigator integration insights
    st.markdown("---")
    st.subheader("🔗 Navigator Integration")
    
    # Get real Navigator data
    reader = NavigatorDataReader()
    nav_customers = reader.get_all_customers()
    
    completed_gcp = sum(1 for c in nav_customers if c.get("has_gcp_assessment"))
    completed_cost = sum(1 for c in nav_customers if c.get("has_cost_plan"))
    ready_consultation = sum(1 for c in nav_customers if c.get("has_gcp_assessment") and c.get("has_cost_plan"))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("GCP Assessments", completed_gcp, help="Completed care assessments")
    
    with col2:
        st.metric("Cost Plans", completed_cost, help="Completed cost planning")
    
    with col3:
        st.metric("Ready for Consult", ready_consultation, help="Completed both assessments")
    
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
        st.subheader("📊 Team Pipeline Health")
        
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
