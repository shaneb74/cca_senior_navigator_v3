"""
Concierge Care Advisors - CRM Application

This is the advisor-facing CRM application for managing customer interactions,
appointments, and workflow. It provides read access to Senior Navigator customer
data and CRM-specific functionality for internal team use.

Run with: streamlit run crm_app.py --server.port=8502
"""
import streamlit as st
import sys
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configure the CRM application
st.set_page_config(
    page_title="Advisor CRM Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CRM-specific styling
st.markdown("""
<style>
    /* CRM-specific styling */
    .crm-header {
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
    }
    
    .crm-nav {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    
    .customer-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .status-active { background: #dcfce7; color: #166534; }
    .status-pending { background: #fef3c7; color: #92400e; }
    .status-completed { background: #dbeafe; color: #1e40af; }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    
    .metric-number {
        font-size: 2rem;
        font-weight: 700;
        color: #1e40af;
    }
    
    .metric-label {
        color: #64748b;
        font-size: 0.875rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# CRM Header
st.markdown("""
<div class="crm-header">
    <h1 style="margin: 0; font-size: 1.5rem;">🏢 Advisor CRM Dashboard</h1>
    <p style="margin: 0; opacity: 0.9;">Concierge Care Advisors Internal Platform</p>
</div>
""", unsafe_allow_html=True)

# Navigation Sidebar
st.sidebar.markdown("""
<div class="crm-nav">
    <h3 style="margin: 0 0 1rem 0; color: #1e40af;">CRM Navigation</h3>
</div>
""", unsafe_allow_html=True)

# Main navigation
page = st.sidebar.radio(
    "Go to:",
    [
        "📊 Dashboard", 
        "👥 Customers", 
        "🎯 Customer 360°",
        "🕒 Smart Timeline",
        "🤖 AI Next Steps",
        "🏘️ Smart Matching",
        "📞 Appointments", 
        "📝 Notes & Interactions",
        "📈 Analytics"
    ],
    index=0
)

# Environment indicator
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.75rem;">
    <strong>Environment:</strong> Development<br>
    <strong>Data Source:</strong> File-based Demo
</div>
""", unsafe_allow_html=True)

# Route to appropriate page
try:
    if page == "📊 Dashboard":
        from apps.crm.pages.dashboard import render
        render()
    elif page == "👥 Customers":
        from apps.crm.pages.customers import render
        render()
    elif page == "🎯 Customer 360°":
        from apps.crm.pages.customer_360 import render
        render()
    elif page == "🕒 Smart Timeline":
        from apps.crm.pages.smart_timeline import render
        render()
    elif page == "🤖 AI Next Steps":
        from apps.crm.pages.ai_next_steps import render
        render()
    elif page == "🏘️ Smart Matching":
        from apps.crm.pages.smart_matching import render
        render()
    elif page == "📞 Appointments":
        from apps.crm.pages.appointments import render
        render()
    elif page == "📝 Notes & Interactions":
        from apps.crm.pages.notes import render
        render()
    elif page == "📈 Analytics":
        from apps.crm.pages.analytics import render
        render()

except ImportError as e:
    st.error(f"""
    **CRM Module Not Found**
    
    The CRM page module could not be imported: `{e}`
    
    This likely means the CRM pages haven't been created yet or there's a path issue.
    
    **Expected Structure:**
    ```
    apps/
    └── crm/
        └── pages/
            ├── dashboard.py
            ├── customers.py
            ├── appointments.py
            ├── notes.py
            └── analytics.py
    ```
    """)
    
    # Show basic placeholder content
    st.subheader(f"🚧 {page} - Coming Soon")
    st.info("This CRM page is under development. Please check back soon!")

except Exception as e:
    st.error(f"""
    **Error Loading CRM Page**
    
    An error occurred while loading the page: `{str(e)}`
    
    Please check the application logs for more details.
    """)
    
    # Debug information in development
    with st.expander("Debug Information"):
        st.code(str(e))
        import traceback
        st.code(traceback.format_exc())