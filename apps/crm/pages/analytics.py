"""
CRM Analytics page - business insights and performance metrics
Clean, professional styling following the lobby design pattern
"""
import streamlit as st
from shared.data_access.crm_repository import CrmRepository
from shared.data_access.navigator_reader import NavigatorDataReader
from datetime import datetime, timedelta
import json

def inject_crm_css():
    """Inject clean CRM styling"""
    if st.session_state.get("_crm_css_injected"):
        return
        
    css = """
    <style>
    .stApp { background-color: #ffffff; }
    .crm-header {
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 0.75rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    .crm-title { 
        font-size: 2rem; 
        font-weight: 700; 
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .crm-subtitle {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e40af;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        font-size: 0.875rem;
        letter-spacing: 0.05em;
    }
    .insight-card {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 4px solid #3b82f6;
        margin-bottom: 1rem;
    }
    .insight-title {
        color: #1e293b;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .insight-text {
        color: #475569;
        line-height: 1.6;
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    st.session_state["_crm_css_injected"] = True

def get_analytics_data():
    """Gather analytics data from Navigator and CRM sources"""
    nav_reader = NavigatorDataReader()
    crm_repo = CrmRepository()
    
    # Get Navigator customer data
    customers = nav_reader.get_all_customers()
    
    # Get CRM activity data
    notes = crm_repo.get_all_notes()
    appointments = crm_repo.list_records("appointments")
    
    # Calculate metrics
    total_customers = len(customers)
    active_customers = len([c for c in customers if c.get('last_activity_days', 0) <= 30])
    
    # Assessment completion rates  
    gcp_completed = len([c for c in customers if c.get('has_gcp_assessment', False)])
    cost_completed = len([c for c in customers if c.get('has_cost_plan', False)])
    
    # Care recommendations breakdown
    care_recommendations = {}
    for customer in customers:
        rec = customer.get('care_recommendation', 'Unknown')
        care_recommendations[rec] = care_recommendations.get(rec, 0) + 1
    
    # Recent activity
    recent_notes = [n for n in notes if (datetime.now() - n.created_at).days <= 7]
    upcoming_appointments = [a for a in appointments if a.get('status') == 'scheduled']
    
    return {
        'total_customers': total_customers,
        'active_customers': active_customers,
        'gcp_completion_rate': (gcp_completed / total_customers * 100) if total_customers > 0 else 0,
        'cost_completion_rate': (cost_completed / total_customers * 100) if total_customers > 0 else 0,
        'care_recommendations': care_recommendations,
        'recent_notes_count': len(recent_notes),
        'upcoming_appointments_count': len(upcoming_appointments),
        'total_notes': len(notes),
        'total_appointments': len(appointments)
    }

def render():
    """Render the analytics dashboard"""
    inject_crm_css()
    
    # Header
    st.markdown("""
    <div class="crm-header">
        <h1 class="crm-title">Analytics & Insights</h1>
        <p class="crm-subtitle">Business performance and customer journey metrics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get analytics data
    try:
        analytics = get_analytics_data()
    except Exception as e:
        st.error(f"Error loading analytics data: {e}")
        return
    
    # Key Metrics Row
    st.subheader("📊 Key Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analytics['total_customers']}</div>
            <div class="metric-label">Total Customers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analytics['active_customers']}</div>
            <div class="metric-label">Active (30 days)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analytics['gcp_completion_rate']:.1f}%</div>
            <div class="metric-label">GCP Complete</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analytics['cost_completion_rate']:.1f}%</div>
            <div class="metric-label">Cost Planning</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Activity Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analytics['recent_notes_count']}</div>
            <div class="metric-label">Notes (7 days)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analytics['upcoming_appointments_count']}</div>
            <div class="metric-label">Upcoming Appts</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analytics['total_notes']}</div>
            <div class="metric-label">Total Notes</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Care Recommendations Breakdown
    st.subheader("🏥 Care Recommendations Analysis")
    
    if analytics['care_recommendations']:
        # Create columns for care recommendation display
        total_recs = sum(analytics['care_recommendations'].values())
        
        for rec_type, count in analytics['care_recommendations'].items():
            percentage = (count / total_recs * 100) if total_recs > 0 else 0
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{rec_type.replace('_', ' ').title()}**")
                st.progress(percentage / 100)
            with col2:
                st.metric("", f"{count} ({percentage:.1f}%)")
    else:
        st.info("No care recommendation data available")
    
    # Insights Section
    st.subheader("💡 Business Insights")
    
    # Generate insights based on data
    insights = []
    
    if analytics['gcp_completion_rate'] < 70:
        insights.append({
            "title": "GCP Completion Opportunity",
            "text": f"Only {analytics['gcp_completion_rate']:.1f}% of customers have completed their Geriatric Care Plan. Consider follow-up campaigns to increase completion rates."
        })
    
    if analytics['recent_notes_count'] < analytics['active_customers'] * 0.3:
        insights.append({
            "title": "Customer Engagement",
            "text": f"Recent note activity ({analytics['recent_notes_count']} notes) is low relative to active customers ({analytics['active_customers']}). Consider scheduling more regular check-ins."
        })
    
    if analytics['upcoming_appointments_count'] == 0:
        insights.append({
            "title": "Appointment Pipeline",
            "text": "No upcoming appointments scheduled. This may indicate a need to proactively reach out to customers for follow-up consultations."
        })
    
    if not insights:
        insights.append({
            "title": "Performance Strong",
            "text": "Key metrics are looking healthy! Continue current customer engagement strategies."
        })
    
    for insight in insights:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">{insight['title']}</div>
            <div class="insight-text">{insight['text']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Raw Data Section (collapsible)
    with st.expander("🔍 View Raw Analytics Data"):
        st.json(analytics)

if __name__ == "__main__":
    render()