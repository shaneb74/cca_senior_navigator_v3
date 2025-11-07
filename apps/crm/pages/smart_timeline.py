"""
Smart Timeline - AI-powered customer journey tracking
Replaces manual activity logging with automated Navigator event detection
"""
import streamlit as st
from datetime import datetime, timedelta
from shared.data_access.navigator_reader import NavigatorDataReader

def inject_timeline_css():
    """Professional timeline styling"""
    if st.session_state.get("_timeline_css"):
        return
        
    css = """
    <style>
    /* Timeline base styling */
    .timeline-header {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(5, 150, 105, 0.15);
    }
    
    .timeline-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
    }
    
    .timeline-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Timeline container */
    .timeline-container {
        position: relative;
        max-width: 1000px;
        margin: 2rem auto;
    }
    
    .timeline-line {
        position: absolute;
        left: 30px;
        top: 0;
        bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, #3b82f6, #059669);
        border-radius: 999px;
    }
    
    /* Timeline events */
    .timeline-event {
        position: relative;
        margin-bottom: 2rem;
        padding-left: 80px;
    }
    
    .timeline-dot {
        position: absolute;
        left: 15px;
        top: 20px;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        border: 3px solid white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        z-index: 2;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .dot-navigator {
        background: #3b82f6;
        color: white;
    }
    
    .dot-gcp {
        background: #059669;
        color: white;
    }
    
    .dot-cost {
        background: #dc2626;
        color: white;
    }
    
    .dot-contact {
        background: #7c3aed;
        color: white;
    }
    
    .dot-milestone {
        background: #f59e0b;
        color: white;
    }
    
    /* Event cards */
    .event-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        transition: all 0.2s ease;
    }
    
    .event-card:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    .event-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    
    .event-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
    }
    
    .event-time {
        font-size: 0.875rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    .event-description {
        color: #374151;
        line-height: 1.6;
        margin: 0 0 1rem 0;
    }
    
    .event-tags {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .event-tag {
        display: inline-block;
        background: #f3f4f6;
        color: #374151;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .tag-automated {
        background: #dbeafe;
        color: #1e40af;
    }
    
    .tag-high-priority {
        background: #fef2f2;
        color: #dc2626;
    }
    
    .tag-completed {
        background: #f0fdf4;
        color: #166534;
    }
    
    /* AI insights panel */
    .insights-panel {
        background: linear-gradient(135deg, #fef7ff, #f3e8ff);
        border: 1px solid #e9d5ff;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .insights-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .insights-icon {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #8b5cf6, #7c3aed);
        color: white;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-size: 1.2rem;
    }
    
    .insights-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #581c87;
        margin: 0;
    }
    
    .insight-item {
        background: white;
        border: 1px solid #e9d5ff;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .insight-item:last-child {
        margin-bottom: 0;
    }
    
    .insight-metric {
        font-size: 0.875rem;
        color: #7c3aed;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    
    .insight-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1f2937;
    }
    
    /* Filter controls */
    .filter-bar {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        display: flex;
        gap: 1rem;
        align-items: center;
        flex-wrap: wrap;
    }
    
    .filter-label {
        font-weight: 600;
        color: #374151;
        margin-right: 0.5rem;
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    st.session_state["_timeline_css"] = True

def generate_smart_timeline(customer_data):
    """Generate AI-powered timeline from Navigator data"""
    events = []
    
    # Navigator registration event
    events.append({
        'date': customer_data.get('registration_date', '2024-01-01'),
        'type': 'navigator',
        'title': 'Navigator Registration',
        'description': f"{customer_data.get('person_name', 'Customer')} created Navigator account and began their care planning journey.",
        'icon': '🚀',
        'tags': ['automated', 'milestone'],
        'priority': 'normal'
    })
    
    # GCP Assessment completion
    if customer_data.get('has_gcp_assessment'):
        events.append({
            'date': customer_data.get('gcp_completion_date', '2024-01-15'),
            'type': 'gcp',
            'title': 'Care Assessment Completed',
            'description': f"Guided Care Plan assessment completed. Recommendation: {customer_data.get('care_recommendation', 'Assessment complete')}.",
            'icon': '🧠',
            'tags': ['automated', 'completed'],
            'priority': 'high'
        })
    
    # Cost Planning completion
    if customer_data.get('has_cost_plan'):
        events.append({
            'date': customer_data.get('cost_completion_date', '2024-01-20'),
            'type': 'cost',
            'title': 'Financial Planning Completed',
            'description': "Cost planning assessment finished. Budget range established and ready for community recommendations.",
            'icon': '💰',
            'tags': ['automated', 'completed'],
            'priority': 'high'
        })
    
    # AI-generated follow-up needs
    days_since = customer_data.get('last_activity_days', 0)
    if days_since > 7:
        events.append({
            'date': (datetime.now() - timedelta(days=days_since)).strftime('%Y-%m-%d'),
            'type': 'contact',
            'title': f'Last Activity: {days_since} days ago',
            'description': f"Customer has not used Navigator in {days_since} days. Recommended follow-up to provide assistance.",
            'icon': '📞',
            'tags': ['ai-generated', 'high-priority'],
            'priority': 'urgent'
        })
    
    # Smart next steps based on completion status
    if customer_data.get('has_gcp_assessment') and customer_data.get('has_cost_plan'):
        events.append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'type': 'milestone',
            'title': 'Ready for Community Matching',
            'description': "All assessments complete. Customer is ready for personalized community recommendations and consultation.",
            'icon': '🎯',
            'tags': ['ai-generated', 'ready'],
            'priority': 'high'
        })
    
    # Sort events by date
    events.sort(key=lambda x: x['date'], reverse=True)
    return events

def render_ai_insights(customer_data):
    """Render AI-powered customer insights using Streamlit components"""
    completion_rate = calculate_completion_percentage(customer_data)
    engagement_score = 85 if customer_data.get('last_activity_days', 999) <= 7 else 65
    readiness_score = 90 if (customer_data.get('has_gcp_assessment') and customer_data.get('has_cost_plan')) else 50
    
    # Header with AI icon
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
        <div style="font-size: 1.5rem; margin-right: 0.75rem;">🤖</div>
        <h3 style="margin: 0; color: #1f2937;">AI Customer Insights</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create insights in a clean card layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: #ffffff;
            border: 1px solid #e6edf5;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        ">
            <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 0.25rem;">Journey Completion</div>
            <div style="color: #1f2937; font-size: 1.25rem; font-weight: 600;">{completion_rate}% Complete</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="
            background: #ffffff;
            border: 1px solid #e6edf5;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        ">
            <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 0.25rem;">Engagement Level</div>
            <div style="color: #1f2937; font-size: 1.25rem; font-weight: 600;">{engagement_score}% Active</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="
            background: #ffffff;
            border: 1px solid #e6edf5;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        ">
            <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 0.25rem;">Readiness for Consultation</div>
            <div style="color: #1f2937; font-size: 1.25rem; font-weight: 600;">{readiness_score}% Ready</div>
        </div>
        """, unsafe_allow_html=True)
        
        recommended_action = 'Schedule consultation' if readiness_score >= 80 else 'Follow up on assessments'
        st.markdown(f"""
        <div style="
            background: #ffffff;
            border: 1px solid #e6edf5;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        ">
            <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 0.25rem;">Recommended Action</div>
            <div style="color: #1f2937; font-size: 1.25rem; font-weight: 600;">{recommended_action}</div>
        </div>
        """, unsafe_allow_html=True)

def render_timeline_event_streamlit(event, index):
    """Render individual timeline event using Streamlit components"""
    
    # Event icon color based on type
    icon_colors = {
        'milestone': '#2563eb',
        'interaction': '#16a34a', 
        'system': '#64748b',
        'automated': '#8b5cf6'
    }
    icon_color = icon_colors.get(event['type'], '#64748b')
    
    st.markdown(f"""
    <div style="
        display: flex;
        margin-bottom: 1.5rem;
        position: relative;
    ">
        <div style="
            background: {icon_color};
            color: #ffffff;
            width: 2.5rem;
            height: 2.5rem;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            margin-right: 1rem;
            flex-shrink: 0;
        ">{event['icon']}</div>
        <div style="
            background: #ffffff;
            border: 1px solid #e6edf5;
            border-radius: 12px;
            padding: 1.25rem;
            flex: 1;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        ">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                <h4 style="margin: 0; color: #1f2937; font-size: 1.125rem;">{event['title']}</h4>
                <span style="color: #64748b; font-size: 0.875rem; margin-left: 1rem;">{event['date']}</span>
            </div>
            <p style="margin: 0 0 1rem 0; color: #64748b; line-height: 1.5;">{event['description']}</p>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
    """, unsafe_allow_html=True)
    
    # Render tags
    for tag in event['tags']:
        tag_colors = {
            'automated': {'bg': '#f3e8ff', 'text': '#7c3aed'},
            'high-priority': {'bg': '#fef3c7', 'text': '#d97706'},
            'completed': {'bg': '#dcfce7', 'text': '#16a34a'}
        }
        colors = tag_colors.get(tag, {'bg': '#f1f5f9', 'text': '#64748b'})
        
        st.markdown(f"""
        <span style="
            background: {colors['bg']};
            color: {colors['text']};
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 500;
        ">{tag}</span>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div></div>", unsafe_allow_html=True)

def calculate_completion_percentage(customer_data):
    """Calculate customer journey completion percentage"""
    total_steps = 4
    completed = 0
    
    if customer_data.get('person_name'):
        completed += 1
    if customer_data.get('has_gcp_assessment'):
        completed += 1
    if customer_data.get('has_cost_plan'):
        completed += 1
    if customer_data.get('relationship_type'):
        completed += 1
    
    return int((completed / total_steps) * 100)

def render(customer_id=None):
    """Main render function for Smart Timeline"""
    inject_timeline_css()
    
    # Check for selected customer in session state if no customer_id provided
    if not customer_id and 'timeline_customer' in st.session_state:
        customer_id = st.session_state['timeline_customer']
    
    if not customer_id:
        # Customer selection interface
        st.markdown("""
        <div class="timeline-header">
            <h1 class="timeline-title">🕒 Smart Timeline</h1>
            <p class="timeline-subtitle">AI-powered customer journey tracking - no manual logging required</p>
        </div>
        """, unsafe_allow_html=True)
        
        reader = NavigatorDataReader()
        customers = reader.get_all_customers()
        
        if customers:
            st.subheader("Select Customer")
            for customer in customers:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{customer.get('person_name', 'Unknown')}**")
                with col2:
                    completion = calculate_completion_percentage(customer)
                    st.write(f"Journey: {completion}% complete")
                with col3:
                    if st.button("View Timeline", key=f"timeline_{customer['user_id']}"):
                        st.session_state['timeline_customer'] = customer['user_id']
                        st.rerun()
        else:
            st.info("No customers found. Customers will appear here after they use the Navigator.")
        
        return
    
    # Timeline view for specific customer
    reader = NavigatorDataReader()
    customer_data = reader.get_customer_by_id(customer_id)
    
    if not customer_data:
        st.error(f"Customer not found: {customer_id}")
        return
    
    # Timeline header
    customer_name = customer_data.get('person_name', 'Unknown Customer')
    st.markdown(f"""
    <div class="timeline-header">
        <h1 class="timeline-title">🕒 {customer_name}'s Journey</h1>
        <p class="timeline-subtitle">Automated timeline from Navigator activities</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter controls
    st.markdown("""
    <div class="filter-bar">
        <span class="filter-label">Timeline View:</span>
        <span style="color: #059669;">✨ Automatically generated from Navigator data</span>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Insights using Streamlit components
    render_ai_insights(customer_data)
    
    # Generate and render timeline using Streamlit components
    events = generate_smart_timeline(customer_data)
    
    if events:
        st.subheader("Timeline Events")
        
        for i, event in enumerate(events):
            render_timeline_event_streamlit(event, i)
    else:
        st.info("No timeline events found for this customer.")

