"""
CRM Dashboard - Overview and key metrics.

Provides advisors with a high-level view of customer activity,
recent interactions, and important metrics.
"""
import streamlit as st
from shared.data_access.navigator_reader import navigator_data
from shared.data_access.crm_repository import crm_data
from datetime import datetime, timedelta


def render():
    """Render the CRM dashboard page."""
    
    st.title("📊 CRM Dashboard")
    st.markdown("Welcome to the Advisor Dashboard. Here's an overview of current customer activity.")
    
    # Load customer statistics
    try:
        stats = navigator_data.get_customer_statistics()
        customers = navigator_data.get_all_customers()
        recent_notes = crm_data.get_all_notes()
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-number">{}</div>
                <div class="metric-label">Total Customers</div>
            </div>
            """.format(stats['total_customers']), unsafe_allow_html=True)
        
        with col2:
            completion_rate = int(stats['gcp_completion_rate'] * 100)
            st.markdown("""
            <div class="metric-card">
                <div class="metric-number">{}%</div>
                <div class="metric-label">GCP Completion</div>
            </div>
            """.format(completion_rate), unsafe_allow_html=True)
        
        with col3:
            cost_completion_rate = int(stats['cost_planner_completion_rate'] * 100)
            st.markdown("""
            <div class="metric-card">
                <div class="metric-number">{}%</div>
                <div class="metric-label">Cost Planning</div>
            </div>
            """.format(cost_completion_rate), unsafe_allow_html=True)
        
        with col4:
            recent_count = stats['last_30_days']
            st.markdown("""
            <div class="metric-card">
                <div class="metric-number">{}</div>
                <div class="metric-label">Active (30 days)</div>
            </div>
            """.format(recent_count), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Two-column layout for detailed views
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🕒 Recent Customer Activity")
            
            if customers:
                # Sort by last updated
                recent_customers = sorted(
                    [c for c in customers if c.last_updated], 
                    key=lambda x: x.last_updated, 
                    reverse=True
                )[:10]
                
                for customer in recent_customers:
                    # Status indicators
                    status_indicators = []
                    if customer.gcp_completed:
                        status_indicators.append('<span class="status-badge status-completed">GCP Done</span>')
                    if customer.cost_planner_completed:
                        status_indicators.append('<span class="status-badge status-completed">Cost Done</span>')
                    if not customer.gcp_completed and not customer.cost_planner_completed:
                        status_indicators.append('<span class="status-badge status-pending">In Progress</span>')
                    
                    # Customer name or ID
                    display_name = customer.person_name or customer.user_id
                    if customer.relationship_type:
                        display_name += f" ({customer.relationship_type})"
                    
                    # Last activity time
                    time_ago = _format_time_ago(customer.last_updated)
                    
                    st.markdown(f"""
                    <div class="customer-card">
                        <strong>{display_name}</strong><br>
                        <small>Last activity: {time_ago}</small><br>
                        {' '.join(status_indicators)}
                        {f"<br><em>Care rec: {customer.care_recommendation}</em>" if customer.care_recommendation else ""}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No customer data found. Make sure Navigator customers have been created.")
        
        with col2:
            st.subheader("📝 Recent Notes")
            
            if recent_notes:
                # Show last 5 notes
                recent_notes_sorted = sorted(recent_notes, key=lambda x: x.created_at, reverse=True)[:5]
                
                for note in recent_notes_sorted:
                    time_ago = _format_time_ago(note.created_at)
                    
                    st.markdown(f"""
                    <div style="background: #f8fafc; padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.5rem; border-left: 3px solid #3b82f6;">
                        <strong>{note.advisor_name}</strong> • {note.note_type}<br>
                        <small>{time_ago}</small><br>
                        <em>{note.content[:100]}...</em>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No advisor notes yet.")
            
            st.subheader("🎯 Care Recommendations")
            
            if stats['care_recommendations']:
                for care_type, count in stats['care_recommendations'].items():
                    st.metric(care_type.replace('_', ' ').title(), count)
            else:
                st.info("No care recommendations data.")
    
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")
        st.info("This might be because no Navigator customer data exists yet.")
        
        # Show placeholder metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Customers", "0")
        with col2:
            st.metric("GCP Completion", "0%")
        with col3:
            st.metric("Cost Planning", "0%")
        with col4:
            st.metric("Active (30 days)", "0")


def _format_time_ago(dt: datetime) -> str:
    """Format a datetime as a human-readable 'time ago' string."""
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hours ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minutes ago"
    else:
        return "Just now"