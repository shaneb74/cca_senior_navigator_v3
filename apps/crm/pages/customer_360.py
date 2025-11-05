"""
Customer 360° View - Professional advisor dashboard for Navigator customers
Clean, lobby-style design with comprehensive customer insights
"""
import streamlit as st
from datetime import datetime, timedelta
from shared.data_access.navigator_reader import NavigatorDataReader

def inject_clean_crm_css():
    """Professional CRM styling - zero Streamlit clutter"""
    if st.session_state.get("_customer_360_css"):
        return
        
    css = """
    <style>
    /* Base clean styling */
    .stApp { background: #ffffff; }
    .block-container { padding: 2rem; max-width: 1400px; }
    .stDeployButton, .stDecoration, .stToolbar { display: none !important; }
    
    /* Customer 360 Header */
    .customer-header {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(37, 99, 235, 0.15);
    }
    
    .customer-name {
        font-size: 2.25rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
    }
    
    .customer-context {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0 0 1.5rem 0;
    }
    
    .progress-bar-container {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 999px;
        height: 8px;
        overflow: hidden;
        margin-bottom: 1rem;
    }
    
    .progress-bar {
        background: #ffffff;
        height: 100%;
        border-radius: 999px;
        transition: width 0.3s ease;
    }
    
    .progress-text {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Metrics Grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #6b7280;
        margin: 0.5rem 0 0 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-change {
        font-size: 0.8rem;
        margin: 0.25rem 0 0 0;
    }
    
    .metric-positive { color: #059669; }
    .metric-neutral { color: #6b7280; }
    
    /* Assessment Cards */
    .assessment-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .assessment-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    }
    
    .assessment-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .assessment-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-size: 1.5rem;
    }
    
    .icon-gcp {
        background: #dbeafe;
        color: #2563eb;
    }
    
    .icon-cost {
        background: #ecfdf5;
        color: #059669;
    }
    
    .icon-family {
        background: #fef3c7;
        color: #d97706;
    }
    
    .assessment-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
    }
    
    .assessment-subtitle {
        font-size: 0.9rem;
        color: #6b7280;
        margin: 0.25rem 0 0 0;
    }
    
    .assessment-content {
        color: #374151;
        line-height: 1.6;
    }
    
    .recommendation-badge {
        display: inline-block;
        background: #f3f4f6;
        color: #1f2937;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 1rem 0;
    }
    
    .badge-memory-care {
        background: #fef2f2;
        color: #dc2626;
    }
    
    .badge-assisted-living {
        background: #fffbeb;
        color: #d97706;
    }
    
    .badge-independent {
        background: #f0fdf4;
        color: #16a34a;
    }
    
    /* Next Steps Section */
    .next-steps {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .next-steps-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0 0 1rem 0;
        display: flex;
        align-items: center;
    }
    
    .ai-badge {
        background: linear-gradient(135deg, #8b5cf6, #a855f7);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 1rem;
    }
    
    .step-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .step-item {
        display: flex;
        align-items: flex-start;
        padding: 1rem 0;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .step-item:last-child {
        border-bottom: none;
    }
    
    .step-number {
        background: #2563eb;
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.875rem;
        font-weight: 700;
        margin-right: 1rem;
        flex-shrink: 0;
    }
    
    .step-content {
        flex: 1;
    }
    
    .step-title {
        font-weight: 600;
        color: #1f2937;
        margin: 0 0 0.25rem 0;
    }
    
    .step-description {
        font-size: 0.9rem;
        color: #6b7280;
        margin: 0;
    }
    
    /* Action Buttons */
    .action-bar {
        display: flex;
        gap: 1rem;
        margin: 2rem 0;
        padding: 1.5rem;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
    }
    
    .btn-action {
        background: #2563eb;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .btn-action:hover {
        background: #1d4ed8;
        transform: translateY(-1px);
    }
    
    .btn-secondary {
        background: #ffffff;
        color: #374151;
        border: 1px solid #d1d5db;
    }
    
    .btn-secondary:hover {
        background: #f9fafb;
        border-color: #9ca3af;
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    st.session_state["_customer_360_css"] = True

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

def render_customer_header(customer_data):
    """Render clean customer header with progress"""
    name = customer_data.get('person_name', 'Customer')
    relationship = customer_data.get('relationship_type', 'Unknown')
    last_activity = customer_data.get('last_activity', 'Never')
    completion = calculate_completion_percentage(customer_data)
    
    context_text = f"Planning for {relationship} • Last activity: {last_activity}"
    
    header_html = f"""
    <div class="customer-header">
        <h1 class="customer-name">{name}</h1>
        <p class="customer-context">{context_text}</p>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {completion}%"></div>
        </div>
        <p class="progress-text">Navigator Journey: {completion}% Complete</p>
    </div>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)

def render_key_metrics(customer_data):
    """Render key customer metrics"""
    days_since_activity = customer_data.get('last_activity_days', 0)
    has_gcp = customer_data.get('has_gcp_assessment', False)
    has_cost = customer_data.get('has_cost_plan', False)
    
    engagement_score = 85 if days_since_activity <= 7 else 65 if days_since_activity <= 30 else 35
    readiness_score = 90 if (has_gcp and has_cost) else 60 if (has_gcp or has_cost) else 30
    
    metrics_html = f"""
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value">{days_since_activity}</div>
            <div class="metric-label">Days Since Activity</div>
            <div class="metric-change metric-neutral">Last Navigator use</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{engagement_score}%</div>
            <div class="metric-label">Engagement Score</div>
            <div class="metric-change metric-positive">Active user</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{readiness_score}%</div>
            <div class="metric-label">Readiness Score</div>
            <div class="metric-change metric-positive">Ready for outreach</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">A</div>
            <div class="metric-label">Priority Level</div>
            <div class="metric-change metric-positive">High-value prospect</div>
        </div>
    </div>
    """
    
    st.markdown(metrics_html, unsafe_allow_html=True)

def render_assessments(customer_data):
    """Render assessment cards with clean styling using Streamlit components"""
    
    st.subheader("Assessment Overview")
    
    # Create 3-column layout for assessment cards
    col1, col2, col3 = st.columns(3)
    
    # GCP Assessment Card
    with col1:
        if customer_data.get('has_gcp_assessment'):
            gcp_recommendation = customer_data.get('care_recommendation', 'Assessment completed')
            
            st.markdown(f"""
            <div style="
                background: #ffffff;
                border: 1px solid #e6edf5;
                border-radius: 12px;
                padding: 1.25rem;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
                margin-bottom: 1rem;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="font-size: 1.5rem; margin-right: 0.75rem;">🧠</div>
                    <div>
                        <h4 style="margin: 0; color: #1f2937;">Guided Care Plan</h4>
                        <p style="margin: 0; color: #16a34a; font-size: 0.875rem;">Completed assessment</p>
                    </div>
                </div>
                <div style="
                    background: #dcfce7;
                    color: #16a34a;
                    padding: 0.5rem 1rem;
                    border-radius: 999px;
                    font-size: 0.875rem;
                    font-weight: 600;
                    text-align: center;
                    margin-bottom: 0.75rem;
                ">{gcp_recommendation}</div>
                <p style="margin: 0; color: #64748b; font-size: 0.875rem;">
                    Care recommendation based on comprehensive assessment of needs, mobility, and preferences.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="
                background: #ffffff;
                border: 1px solid #e6edf5;
                border-radius: 12px;
                padding: 1.25rem;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
                margin-bottom: 1rem;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="font-size: 1.5rem; margin-right: 0.75rem;">🧠</div>
                    <div>
                        <h4 style="margin: 0; color: #1f2937;">Guided Care Plan</h4>
                        <p style="margin: 0; color: #f59e0b; font-size: 0.875rem;">Not started</p>
                    </div>
                </div>
                <p style="margin: 0; color: #64748b; font-size: 0.875rem;">
                    Customer has not completed the care assessment. This is a key next step for understanding their needs.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Cost Planner Card
    with col2:
        if customer_data.get('has_cost_plan'):
            st.markdown(f"""
            <div style="
                background: #ffffff;
                border: 1px solid #e6edf5;
                border-radius: 12px;
                padding: 1.25rem;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
                margin-bottom: 1rem;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="font-size: 1.5rem; margin-right: 0.75rem;">💰</div>
                    <div>
                        <h4 style="margin: 0; color: #1f2937;">Cost Planner</h4>
                        <p style="margin: 0; color: #16a34a; font-size: 0.875rem;">Completed analysis</p>
                    </div>
                </div>
                <div style="
                    background: #dbeafe;
                    color: #2563eb;
                    padding: 0.5rem 1rem;
                    border-radius: 999px;
                    font-size: 0.875rem;
                    font-weight: 600;
                    text-align: center;
                    margin-bottom: 0.75rem;
                ">Budget established</div>
                <p style="margin: 0; color: #64748b; font-size: 0.875rem;">
                    Financial capacity and budget range determined. Ready for community recommendations.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="
                background: #ffffff;
                border: 1px solid #e6edf5;
                border-radius: 12px;
                padding: 1.25rem;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
                margin-bottom: 1rem;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="font-size: 1.5rem; margin-right: 0.75rem;">💰</div>
                    <div>
                        <h4 style="margin: 0; color: #1f2937;">Cost Planner</h4>
                        <p style="margin: 0; color: #f59e0b; font-size: 0.875rem;">Not started</p>
                    </div>
                </div>
                <p style="margin: 0; color: #64748b; font-size: 0.875rem;">
                    Customer has not completed cost planning. Understanding budget is crucial for community matching.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Family Context Card
    with col3:
        relationship = customer_data.get('relationship_type', 'Unknown')
        st.markdown(f"""
        <div style="
            background: #ffffff;
            border: 1px solid #e6edf5;
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
            margin-bottom: 1rem;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div style="font-size: 1.5rem; margin-right: 0.75rem;">👨‍👩‍👧‍👦</div>
                <div>
                    <h4 style="margin: 0; color: #1f2937;">Family Context</h4>
                    <p style="margin: 0; color: #16a34a; font-size: 0.875rem;">Relationship established</p>
                </div>
            </div>
            <div style="
                background: #f3f4f6;
                color: #374151;
                padding: 0.5rem 1rem;
                border-radius: 999px;
                font-size: 0.875rem;
                font-weight: 600;
                text-align: center;
                margin-bottom: 0.75rem;
            ">{relationship}</div>
            <p style="margin: 0; color: #64748b; font-size: 0.875rem;">
                Understanding family dynamics and decision-making structure for effective communication.
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_ai_next_steps(customer_data):
    """Render AI-powered next steps using Streamlit components"""
    has_gcp = customer_data.get('has_gcp_assessment', False)
    has_cost = customer_data.get('has_cost_plan', False)
    days_since = customer_data.get('last_activity_days', 0)
    
    # AI logic for next steps
    if has_gcp and has_cost:
        steps = [
            ("Schedule consultation call", "Customer is ready for personalized guidance"),
            ("Prepare community recommendations", "Match facilities to their care plan and budget"),
            ("Send welcome packet", "Introduce CCA services and next steps")
        ]
    elif has_gcp and not has_cost:
        steps = [
            ("Follow up on cost planning", "Help complete their financial assessment"),
            ("Provide budget guidance", "Share cost planning resources"),
            ("Schedule cost consultation", "Walk through their financial options")
        ]
    elif not has_gcp and has_cost:
        steps = [
            ("Follow up on care assessment", "Complete their care planning process"),
            ("Explain GCP benefits", "Show how assessment improves recommendations"),
            ("Offer assessment assistance", "Provide guidance through the process")
        ]
    else:
        steps = [
            ("Welcome outreach call", "Introduce CCA services and support"),
            ("Guide through Navigator", "Help complete assessments"),
            ("Send getting started resources", "Provide helpful materials")
        ]

    # Header with AI badge
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
        <h3 style="margin: 0; color: #1f2937;">Recommended Next Steps</h3>
        <span style="
            background: #8b5cf6;
            color: #ffffff;
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 1rem;
        ">AI Powered</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Render steps using Streamlit components
    for i, (title, description) in enumerate(steps, 1):
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: flex-start;
            background: #ffffff;
            border: 1px solid #e6edf5;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        ">
            <div style="
                background: #2563eb;
                color: #ffffff;
                width: 2rem;
                height: 2rem;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 0.875rem;
                margin-right: 1rem;
                flex-shrink: 0;
            ">{i}</div>
            <div>
                <h4 style="margin: 0 0 0.25rem 0; color: #1f2937; font-size: 1rem;">{title}</h4>
                <p style="margin: 0; color: #64748b; font-size: 0.875rem;">{description}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_action_bar():
    """Render clean action buttons"""
    action_html = """
    <div class="action-bar">
        <button class="btn-action">📞 Call Customer</button>
        <button class="btn-action btn-secondary">✉️ Send Email</button>
        <button class="btn-action btn-secondary">📅 Schedule Meeting</button>
        <button class="btn-action btn-secondary">📝 Add Note</button>
    </div>
    """
    
    st.markdown(action_html, unsafe_allow_html=True)

def render(customer_id=None):
    """Main render function for Customer 360° view"""
    inject_clean_crm_css()
    
    # Check for selected customer in session state if no customer_id provided
    if not customer_id and 'selected_customer' in st.session_state:
        customer_id = st.session_state['selected_customer']
    
    if not customer_id:
        # Customer selection interface
        st.markdown("""
        <div class="customer-header">
            <h1 class="customer-name">Customer 360° View</h1>
            <p class="customer-context">Select a customer to view their comprehensive profile</p>
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
                    st.write(f"Last activity: {customer.get('last_activity', 'Never')}")
                with col3:
                    if st.button("View", key=f"view_{customer['user_id']}"):
                        st.session_state['selected_customer'] = customer['user_id']
                        st.rerun()
        else:
            st.info("No customers found. Customers will appear here after they use the Navigator.")
        
        return
    
    # Customer details view
    reader = NavigatorDataReader()
    customer_data = reader.get_customer_by_id(customer_id)
    
    if not customer_data:
        st.error(f"Customer not found: {customer_id}")
        return
    
    # Render customer 360° view
    render_customer_header(customer_data)
    render_key_metrics(customer_data)
    render_assessments(customer_data)
    render_ai_next_steps(customer_data)
    render_action_bar()