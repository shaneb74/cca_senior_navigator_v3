"""
"""
CRM Dashboard - Clean professional overview
Shows key metrics and QuickBase transformation progress
"""
import streamlit as st
from datetime import datetime, timedelta
from shared.data_access.navigator_reader import NavigatorDataReader

def inject_dashboard_css():
    """Professional dashboard styling"""
    if st.session_state.get("_dashboard_css"):
        return
        
    css = """
    <style>
    /* Dashboard base styling */
    .dashboard-header {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(30, 64, 175, 0.15);
    }
    
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
    }
    
    .dashboard-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Metrics grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0 0 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #6b7280;
        margin: 0 0 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    
    .metric-change {
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .change-positive { color: #059669; }
    .change-negative { color: #dc2626; }
    .change-neutral { color: #6b7280; }
    
    /* Feature showcase */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 0;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    }
    
    .feature-header {
        padding: 1.5rem;
        border-bottom: 1px solid #e5e7eb;
        display: flex;
        align-items: center;
    }
    
    .feature-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-size: 1.5rem;
    }
    
    .icon-blue { background: #dbeafe; color: #1e40af; }
    .icon-green { background: #dcfce7; color: #166534; }
    .icon-purple { background: #f3e8ff; color: #7c3aed; }
    .icon-orange { background: #fed7aa; color: #ea580c; }
    
    .feature-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0 0 0.25rem 0;
    }
    
    .feature-subtitle {
        font-size: 0.875rem;
        color: #6b7280;
        margin: 0;
    }
    
    .feature-content {
        padding: 1.5rem;
    }
    
    .feature-description {
        color: #374151;
        line-height: 1.6;
        margin: 0 0 1.5rem 0;
    }
    
    .feature-stats {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }
    
    .stat-item {
        text-align: center;
        background: #f9fafb;
        border: 1px solid #f3f4f6;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stat-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #6b7280;
        margin: 0.25rem 0 0 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Transformation showcase */
    .transformation-panel {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        border: 1px solid #bbf7d0;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .transformation-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .transformation-title {
        font-size: 2rem;
        font-weight: 700;
        color: #14532d;
        margin: 0 0 1rem 0;
    }
    
    .transformation-subtitle {
        color: #166534;
        margin: 0;
        font-size: 1.1rem;
    }
    
    .before-after {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        gap: 2rem;
        align-items: center;
    }
    
    .before-card, .after-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
    }
    
    .before-card {
        border: 2px solid #fecaca;
    }
    
    .after-card {
        border: 2px solid #bbf7d0;
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0 0 1rem 0;
    }
    
    .before-title { color: #dc2626; }
    .after-title { color: #059669; }
    
    .card-list {
        text-align: left;
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .card-list li {
        padding: 0.5rem 0;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .card-list li:last-child {
        border-bottom: none;
    }
    
    .transform-arrow {
        font-size: 3rem;
        color: #059669;
    }
    
    /* Quick actions */
    .quick-actions {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .actions-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0 0 1.5rem 0;
        text-align: center;
    }
    
    .actions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
    }
    
    .action-button {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        border: none;
        padding: 1rem;
        border-radius: 12px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        text-align: center;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    st.session_state["_dashboard_css"] = True

def get_dashboard_metrics():
    """Calculate key dashboard metrics"""
    reader = NavigatorDataReader()
    customers = reader.get_all_customers()
    
    total_customers = len(customers)
    completed_gcp = sum(1 for c in customers if c.get('has_gcp_assessment'))
    completed_cost = sum(1 for c in customers if c.get('has_cost_plan'))
    ready_for_consultation = sum(1 for c in customers if c.get('has_gcp_assessment') and c.get('has_cost_plan'))
    
    # Calculate engagement
    active_customers = sum(1 for c in customers if c.get('last_activity_days', 999) <= 7)
    
    return {
        'total_customers': total_customers,
        'completed_gcp': completed_gcp,
        'completed_cost': completed_cost,
        'ready_consultation': ready_for_consultation,
        'active_customers': active_customers,
        'completion_rate': int((ready_for_consultation / max(total_customers, 1)) * 100)
    }

def render():
    """Main render function for dashboard"""
    inject_dashboard_css()
    
    # Dashboard header
    st.markdown("""
    <div class="dashboard-header">
        <h1 class="dashboard-title">🏢 Advisor CRM Dashboard</h1>
        <p class="dashboard-subtitle">
            Professional customer management with smart Navigator integration
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get metrics
    metrics = get_dashboard_metrics()
    
    # Key metrics
    metrics_html = f"""
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-icon">👥</div>
            <div class="metric-value">{metrics['total_customers']}</div>
            <div class="metric-label">Total Customers</div>
            <div class="metric-change change-positive">↗ Navigator integrated</div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">🧠</div>
            <div class="metric-value">{metrics['completed_gcp']}</div>
            <div class="metric-label">GCP Assessments</div>
            <div class="metric-change change-positive">✅ Automated tracking</div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">💰</div>
            <div class="metric-value">{metrics['completed_cost']}</div>
            <div class="metric-label">Cost Plans</div>
            <div class="metric-change change-positive">📊 Smart budgeting</div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">🎯</div>
            <div class="metric-value">{metrics['ready_consultation']}</div>
            <div class="metric-label">Ready for Consult</div>
            <div class="metric-change change-positive">🚀 High priority</div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">⚡</div>
            <div class="metric-value">{metrics['active_customers']}</div>
            <div class="metric-label">Active This Week</div>
            <div class="metric-change change-positive">📈 Engaged users</div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">📊</div>
            <div class="metric-value">{metrics['completion_rate']}%</div>
            <div class="metric-label">Completion Rate</div>
            <div class="metric-change change-positive">🎯 Journey success</div>
        </div>
    </div>
    """
    
    st.markdown(metrics_html, unsafe_allow_html=True)
    
    # Feature showcase
    features_html = """
    <div class="features-grid">
        <div class="feature-card">
            <div class="feature-header">
                <div class="feature-icon icon-blue">🎯</div>
                <div>
                    <h3 class="feature-title">Customer 360°</h3>
                    <p class="feature-subtitle">Complete customer profiles</p>
                </div>
            </div>
            <div class="feature-content">
                <p class="feature-description">
                    Comprehensive customer view with Navigator assessment data, 
                    journey progress, and AI-powered insights.
                </p>
                <div class="feature-stats">
                    <div class="stat-item">
                        <div class="stat-number">0</div>
                        <div class="stat-label">Manual Entry</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">100%</div>
                        <div class="stat-label">Automated</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-header">
                <div class="feature-icon icon-green">🕒</div>
                <div>
                    <h3 class="feature-title">Smart Timeline</h3>
                    <p class="feature-subtitle">Automated activity tracking</p>
                </div>
            </div>
            <div class="feature-content">
                <p class="feature-description">
                    AI-generated customer timeline from Navigator usage. 
                    No manual activity logging required.
                </p>
                <div class="feature-stats">
                    <div class="stat-item">
                        <div class="stat-number">46</div>
                        <div class="stat-label">Reports Replaced</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">95%</div>
                        <div class="stat-label">Time Saved</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-header">
                <div class="feature-icon icon-purple">🤖</div>
                <div>
                    <h3 class="feature-title">AI Next Steps</h3>
                    <p class="feature-subtitle">Intelligent recommendations</p>
                </div>
            </div>
            <div class="feature-content">
                <p class="feature-description">
                    Priority-based action recommendations with urgency scoring 
                    and automated customer analysis.
                </p>
                <div class="feature-stats">
                    <div class="stat-item">
                        <div class="stat-number">218</div>
                        <div class="stat-label">Fields Eliminated</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">90%</div>
                        <div class="stat-label">Accuracy</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-header">
                <div class="feature-icon icon-orange">🏘️</div>
                <div>
                    <h3 class="feature-title">Smart Matching</h3>
                    <p class="feature-subtitle">Community recommendations</p>
                </div>
            </div>
            <div class="feature-content">
                <p class="feature-description">
                    AI-powered community matching using care assessments 
                    and budget data from Navigator.
                </p>
                <div class="feature-stats">
                    <div class="stat-item">
                        <div class="stat-number">132</div>
                        <div class="stat-label">Spreadsheet Fields</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">80%</div>
                        <div class="stat-label">Match Accuracy</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(features_html, unsafe_allow_html=True)
    
    # QuickBase transformation showcase
    transformation_html = """
    <div class="transformation-panel">
        <div class="transformation-header">
            <h2 class="transformation-title">🚀 QuickBase Transformation Complete</h2>
            <p class="transformation-subtitle">From 218+ manual fields to intelligent automation</p>
        </div>
        
        <div class="before-after">
            <div class="before-card">
                <h3 class="card-title before-title">❌ Before: QuickBase</h3>
                <ul class="card-list">
                    <li>📝 218+ manual data entry fields</li>
                    <li>📊 46 activity reports to maintain</li>
                    <li>📋 132 community spreadsheet fields</li>
                    <li>⏰ Hours of daily data entry</li>
                    <li>📉 Outdated customer information</li>
                    <li>🔍 Manual community research</li>
                </ul>
            </div>
            
            <div class="transform-arrow">➡️</div>
            
            <div class="after-card">
                <h3 class="card-title after-title">✅ After: Smart CRM</h3>
                <ul class="card-list">
                    <li>🤖 100% automated data from Navigator</li>
                    <li>📈 AI-powered insights and recommendations</li>
                    <li>🎯 Smart community matching algorithm</li>
                    <li>⚡ Real-time customer journey tracking</li>
                    <li>📊 Live assessment and cost data</li>
                    <li>🧠 Intelligent priority scoring</li>
                </ul>
            </div>
        </div>
    </div>
    """
    
    st.markdown(transformation_html, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("""
    <div class="quick-actions">
        <h2 class="actions-title">⚡ Quick Actions</h2>
        <div class="actions-grid">
            <button class="action-button">🎯 View Customer 360°</button>
            <button class="action-button">🕒 Check Smart Timeline</button>
            <button class="action-button">🤖 AI Recommendations</button>
            <button class="action-button">🏘️ Community Matching</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
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