"""
CRM Customers page - view and manage Navigator customer data
Clean, professional styling following the lobby design pattern
"""
import streamlit as st
from shared.data_access.navigator_reader import NavigatorDataReader
from shared.data_access.crm_repository import CrmRepository

def inject_crm_css():
    """Inject clean CRM styling consistent with Navigator lobby"""
    if st.session_state.get("_crm_css_injected"):
        return
        
    css = """
    <style>
    /* Clean professional CRM styling */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Main content area */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* CRM header styling */
    .crm-header {
        background: #ffffff;
        border-bottom: 1px solid #e6edf5;
        padding: 1.5rem 0;
        margin-bottom: 2rem;
    }
    
    .crm-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
    }
    
    .crm-subtitle {
        font-size: 1.1rem;
        color: #64748b;
        margin: 0.5rem 0 0 0;
    }
    
    /* Customer cards grid */
    .customer-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .customer-card {
        background: #ffffff;
        border: 1px solid #e6edf5;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
        transition: all 0.2s ease;
    }
    
    .customer-card:hover {
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
        transform: translateY(-2px);
    }
    
    .customer-name {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0 0 0.5rem 0;
    }
    
    .customer-meta {
        font-size: 0.95rem;
        color: #64748b;
        margin: 0 0 1rem 0;
    }
    
    .customer-status {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .status-active {
        background: #dcfce7;
        color: #16a34a;
    }
    
    .status-pending {
        background: #fef3c7;
        color: #d97706;
    }
    
    /* Action buttons */
    .customer-actions {
        display: flex;
        gap: 0.75rem;
        margin-top: 1rem;
    }
    
    .btn-clean {
        background: #ffffff;
        border: 1px solid #d1d5db;
        color: #374151;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 500;
        text-decoration: none;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .btn-clean:hover {
        background: #f9fafb;
        border-color: #9ca3af;
    }
    
    .btn-primary {
        background: #2563eb;
        border: 1px solid #2563eb;
        color: #ffffff;
    }
    
    .btn-primary:hover {
        background: #1d4ed8;
        border-color: #1d4ed8;
    }
    
    /* Stats section */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: #ffffff;
        border: 1px solid #e6edf5;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #2563eb;
        margin: 0;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: #64748b;
        margin: 0.25rem 0 0 0;
    }
    
    /* Search and filters */
    .search-bar {
        background: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 0.75rem;
        font-size: 1rem;
        width: 100%;
        margin-bottom: 1rem;
    }
    
    .search-bar:focus {
        outline: none;
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    /* Hide Streamlit clutter */
    .stDeployButton {
        display: none !important;
    }
    
    .stDecoration {
        display: none !important;
    }
    
    /* Clean sidebar */
    .css-1d391kg {
        background-color: #f8fafc;
    }
    
    .css-1lcbmhc {
        background-color: #ffffff;
        border: 1px solid #e6edf5;
        border-radius: 8px;
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    st.session_state["_crm_css_injected"] = True

def render_customer_stats(customers):
    """Render customer statistics overview"""
    total_customers = len(customers)
    active_customers = len([c for c in customers if c.get('last_activity_days', 0) <= 30])
    completed_assessments = len([c for c in customers if c.get('has_gcp_assessment')])
    
    st.markdown("""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">{}</div>
            <div class="stat-label">Total Customers</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{}</div>
            <div class="stat-label">Active (30 days)</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{}</div>
            <div class="stat-label">Completed GCP</div>
        </div>
    </div>
    """.format(total_customers, active_customers, completed_assessments), unsafe_allow_html=True)

def render_customer_cards_streamlit(customers):
    """Render customer cards using Streamlit native components"""
    
    # Create a grid using Streamlit columns
    for i in range(0, len(customers), 2):  # 2 cards per row
        cols = st.columns(2)
        
        for j, col in enumerate(cols):
            if i + j < len(customers):
                customer = customers[i + j]
                
                with col:
                    # Customer card container
                    with st.container():
                        name = customer.get('person_name', 'Unknown Customer')
                        user_id = customer.get('user_id', 'N/A')
                        last_activity = customer.get('last_activity', 'Never')
                        days_since = customer.get('last_activity_days', 999)
                        status = 'Active' if days_since <= 30 else 'Inactive'
                        
                        # Determine progress
                        has_gcp = customer.get('has_gcp_assessment', False)
                        has_cost_plan = customer.get('has_cost_plan', False)
                        
                        progress_items = []
                        if has_gcp:
                            progress_items.append("GCP Assessment")
                        if has_cost_plan:
                            progress_items.append("Cost Plan")
                        progress_text = ", ".join(progress_items) if progress_items else "Getting started"
                        
                        # Card styling with container
                        st.markdown(f"""
                        <div style="
                            background: #ffffff;
                            border: 1px solid #e6edf5;
                            border-radius: 16px;
                            padding: 1.5rem;
                            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
                            margin-bottom: 1rem;
                        ">
                            <h3 style="margin: 0 0 0.5rem 0; color: #1f2937;">{name}</h3>
                            <p style="margin: 0 0 1rem 0; color: #64748b; font-size: 0.95rem;">
                                ID: {user_id} • Last seen: {last_activity}
                            </p>
                            <span style="
                                display: inline-block;
                                padding: 0.25rem 0.75rem;
                                border-radius: 999px;
                                font-size: 0.875rem;
                                font-weight: 600;
                                margin-bottom: 1rem;
                                background: {'#dcfce7' if status == 'Active' else '#fef3c7'};
                                color: {'#16a34a' if status == 'Active' else '#d97706'};
                            ">{status}</span>
                            <p style="margin: 0; color: #64748b; font-size: 0.95rem;">
                                Progress: {progress_text}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Action buttons using Streamlit buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("View Details", key=f"view_{user_id}"):
                                st.session_state['selected_customer'] = user_id
                                # Could redirect to customer 360 page here
                        with col2:
                            if st.button("Add Note", key=f"note_{user_id}"):
                                st.session_state['add_note_customer'] = user_id
                                # Could open note dialog here

def render():
    """Main render function for customers page"""
    inject_crm_css()
    
    # Header
    st.markdown("""
    <div class="crm-header">
        <h1 class="crm-title">Customer Management</h1>
        <p class="crm-subtitle">View and manage Senior Navigator customers</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load customer data
    try:
        reader = NavigatorDataReader()
        customers = reader.get_all_customers()
        
        if not customers:
            st.info("No customer data found. Customers will appear here after they use the Senior Navigator.")
            return
            
        # Statistics overview
        render_customer_stats(customers)
        
        # Search and filters
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("Search customers...", placeholder="Enter name or ID", label_visibility="collapsed")
        with col2:
            status_filter = st.selectbox("Filter by status", ["All", "Active", "Inactive"], label_visibility="collapsed")
        
        # Filter customers
        filtered_customers = customers
        if search_term:
            filtered_customers = [c for c in filtered_customers 
                                if search_term.lower() in c.get('person_name', '').lower() 
                                or search_term.lower() in c.get('user_id', '').lower()]
        
        if status_filter != "All":
            if status_filter == "Active":
                filtered_customers = [c for c in filtered_customers if c.get('last_activity_days', 999) <= 30]
            else:
                filtered_customers = [c for c in filtered_customers if c.get('last_activity_days', 999) > 30]
        
        # Customer grid
        if filtered_customers:
            st.subheader(f"Customers ({len(filtered_customers)})")
            render_customer_cards_streamlit(filtered_customers)
        else:
            st.info("No customers match your search criteria.")
            
    except Exception as e:
        st.error(f"Error loading customer data: {str(e)}")
        st.info("Make sure the Navigator data directory exists and contains customer files.")