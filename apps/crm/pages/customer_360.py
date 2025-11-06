"""
CRM Customer 360° View - Complete customer profile and interaction history
Displays all available information about a customer from Navigator and CRM data
"""
import streamlit as st
from datetime import datetime
from shared.data_access.navigator_reader import NavigatorDataReader
from shared.data_access.crm_repository import CrmRepository
from core.adapters.streamlit_crm import get_crm_customer_by_id

def inject_customer_360_css():
    """Inject Customer 360 specific styling"""
    css = """
    <style>
    .stApp {
        background-color: #f8fafc;
    }
    
    .customer-360-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
    }
    
    .customer-name {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
    }
    
    .customer-id {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    .info-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #667eea;
    }
    
    .info-card h3 {
        margin-top: 0;
        color: #1f2937;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .info-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .info-row:last-child {
        border-bottom: none;
    }
    
    .info-label {
        font-weight: 600;
        color: #64748b;
    }
    
    .info-value {
        color: #1f2937;
        text-align: right;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .status-complete {
        background: #dcfce7;
        color: #16a34a;
    }
    
    .status-in-progress {
        background: #fef3c7;
        color: #d97706;
    }
    
    .status-not-started {
        background: #f1f5f9;
        color: #64748b;
    }
    
    .timeline-item {
        padding: 1rem;
        border-left: 3px solid #e5e7eb;
        margin-left: 1rem;
        margin-bottom: 1rem;
        position: relative;
    }
    
    .timeline-item::before {
        content: '';
        width: 12px;
        height: 12px;
        background: #667eea;
        border-radius: 50%;
        position: absolute;
        left: -7.5px;
        top: 1.2rem;
    }
    
    .timeline-date {
        font-size: 0.875rem;
        color: #64748b;
        margin-bottom: 0.25rem;
    }
    
    .timeline-content {
        color: #1f2937;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_customer_header(customer_data):
    """Render the customer header with name and key info"""
    name = customer_data.get('name') or customer_data.get('person_name', 'Unknown Customer')
    customer_id = customer_data.get('id') or customer_data.get('user_id', 'N/A')
    
    st.markdown(f"""
    <div class="customer-360-header">
        <h1 class="customer-name">{name}</h1>
        <p class="customer-id">Customer ID: {customer_id}</p>
    </div>
    """, unsafe_allow_html=True)


def render_contact_info(customer_data):
    """Render contact information card"""
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("### 📞 Contact Information")
    
    email = customer_data.get('email') or customer_data.get('contact_email', 'Not provided')
    phone = customer_data.get('phone') or customer_data.get('contact_phone', 'Not provided')
    source = customer_data.get('source', 'Unknown')
    created = customer_data.get('created_at', 'Unknown')
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Email:** {email}")
        st.markdown(f"**Phone:** {phone}")
    with col2:
        st.markdown(f"**Source:** {source}")
        st.markdown(f"**Joined:** {created[:10] if created != 'Unknown' else 'Unknown'}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_navigator_status(navigator_data):
    """Render Navigator assessment status"""
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("### 🧭 Senior Navigator Status")
    
    if not navigator_data:
        st.info("No Navigator assessment data available")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # GCP Assessment Status
    has_gcp = navigator_data.get('has_gcp_assessment', False)
    gcp_status = "Complete ✓" if has_gcp else "Not Started"
    gcp_badge_class = "status-complete" if has_gcp else "status-not-started"
    
    # Cost Plan Status
    has_cost = navigator_data.get('has_cost_plan', False)
    cost_status = "Complete ✓" if has_cost else "Not Started"
    cost_badge_class = "status-complete" if has_cost else "status-not-started"
    
    # Journey Stage
    journey_stage = navigator_data.get('journey_stage', 'Initial Contact')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="margin: 0; color: #64748b; font-size: 0.875rem;">GCP Assessment</p>
            <span class="status-badge {gcp_badge_class}">{gcp_status}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="margin: 0; color: #64748b; font-size: 0.875rem;">Cost Planning</p>
            <span class="status-badge {cost_badge_class}">{cost_status}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="margin: 0; color: #64748b; font-size: 0.875rem;">Journey Stage</p>
            <p style="margin: 0.5rem 0 0 0; font-weight: 600; color: #1f2937;">{journey_stage}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Care Recommendation if available
    if has_gcp:
        st.markdown("---")
        care_rec = navigator_data.get('care_recommendation', 'Assessment complete')
        st.markdown(f"**Care Recommendation:** {care_rec}")
        
        # Assessment summary if available
        assessment_summary = navigator_data.get('assessment_summary')
        if assessment_summary:
            with st.expander("📋 Assessment Details"):
                st.write(assessment_summary)
    
    # Cost Summary if available
    if has_cost:
        cost_summary = navigator_data.get('cost_summary')
        if cost_summary:
            with st.expander("💰 Cost Planning Details"):
                st.write(cost_summary)
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_relationship_info(navigator_data):
    """Render relationship and care recipient information"""
    if not navigator_data:
        return
    
    relationship = navigator_data.get('relationship_type')
    if relationship:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 👥 Relationship Information")
        
        st.markdown(f"**Relationship:** {relationship}")
        
        # Additional info if available
        person_name = navigator_data.get('person_name')
        if person_name:
            st.markdown(f"**Care Recipient:** {person_name}")
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_appointments(customer_id):
    """Render customer appointments"""
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("### 📅 Appointments")
    
    crm_repo = CrmRepository()
    appointments = crm_repo.list_records("appointments")
    
    # Filter appointments for this customer
    customer_appointments = [
        a for a in appointments 
        if customer_id in [a.get('customer_id'), a.get('user_id')]
    ]
    
    if customer_appointments:
        for appt in customer_appointments:
            status = appt.get('status', 'Unknown')
            appt_type = appt.get('appointment_type', 'Consultation')
            scheduled = appt.get('scheduled_at', 'Not scheduled')
            confirmation = appt.get('confirmation_id', 'N/A')
            
            status_class = "status-complete" if status.lower() == "scheduled" else "status-in-progress"
            
            st.markdown(f"""
            <div style="padding: 0.75rem; background: #f8fafc; border-radius: 8px; margin-bottom: 0.5rem;">
                <p style="margin: 0; font-weight: 600; color: #1f2937;">{appt_type}</p>
                <p style="margin: 0.25rem 0 0 0; font-size: 0.875rem; color: #64748b;">
                    {scheduled} • <span class="status-badge {status_class}">{status}</span>
                </p>
                <p style="margin: 0.25rem 0 0 0; font-size: 0.875rem; color: #64748b;">
                    Confirmation: {confirmation}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No appointments scheduled")
    
    # Quick action to schedule
    if st.button("➕ Schedule New Appointment", type="primary"):
        st.session_state['schedule_for_customer'] = customer_id
        st.info("📞 Please navigate to **Appointments** page using the sidebar to schedule")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_notes(customer_id):
    """Render customer notes and interactions"""
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("### 📝 Notes & Interactions")
    
    crm_repo = CrmRepository()
    notes = crm_repo.list_records("notes")
    
    # Filter notes for this customer
    customer_notes = [
        n for n in notes 
        if customer_id in [n.get('customer_id'), n.get('user_id')]
    ]
    
    if customer_notes:
        for note in customer_notes[-5:]:  # Show last 5 notes
            created = note.get('created_at', 'Unknown')
            content = note.get('note', 'No content')
            note_type = note.get('note_type', 'General')
            
            st.markdown(f"""
            <div class="timeline-item">
                <p class="timeline-date">{created[:10] if created != 'Unknown' else 'Unknown'} • {note_type}</p>
                <div class="timeline-content">{content}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if len(customer_notes) > 5:
            st.caption(f"+ {len(customer_notes) - 5} more notes")
    else:
        st.info("No notes recorded")
    
    # Quick action to add note
    if st.button("➕ Add Note", type="primary"):
        st.session_state['add_note_customer'] = customer_id
        st.info("📝 Please navigate to **Notes & Interactions** page using the sidebar to add a note")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_activity_timeline(navigator_data):
    """Render customer activity timeline"""
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("### 🕒 Activity Timeline")
    
    if not navigator_data:
        st.info("No activity data available")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Last activity
    last_activity = navigator_data.get('last_activity', 'Never')
    last_activity_days = navigator_data.get('last_activity_days', 999)
    
    if last_activity != 'Never':
        if last_activity_days <= 7:
            activity_status = "🟢 Active (within last week)"
        elif last_activity_days <= 30:
            activity_status = "🟡 Recent (within last month)"
        else:
            activity_status = "🔴 Inactive (over 30 days)"
        
        st.markdown(f"**Status:** {activity_status}")
        st.markdown(f"**Last Seen:** {last_activity}")
    else:
        st.info("No activity recorded")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_quick_actions(customer_id, customer_data):
    """Render quick action buttons"""
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📞 Schedule Call", use_container_width=True):
            st.session_state['schedule_for_customer'] = customer_id
            st.toast("📞 Customer marked for scheduling - use Appointments page")
    
    with col2:
        if st.button("📝 Add Note", use_container_width=True):
            st.session_state['add_note_customer'] = customer_id
            st.toast("📝 Customer marked for note - use Notes page")
    
    with col3:
        if st.button("📧 Send Email", use_container_width=True):
            email = customer_data.get('email') or customer_data.get('contact_email')
            if email:
                st.info(f"📧 Email: {email}")
            else:
                st.warning("No email on file")
    
    with col4:
        if st.button("🏘️ Match Communities", use_container_width=True):
            st.session_state['match_for_customer'] = customer_id
            st.toast("🏘️ Customer marked for matching - use Smart Matching page")


def render():
    """Main render function for Customer 360 view"""
    
    try:
        inject_customer_360_css()
    except Exception as e:
        st.error(f"Error loading CSS: {e}")
    
    # Check if we have a selected customer
    customer_id = st.session_state.get('selected_customer')
    
    # Debug info (can be removed later)
    with st.expander("🔍 Debug Info", expanded=False):
        st.write("Session State Keys:", list(st.session_state.keys()))
        st.write("Selected Customer ID:", customer_id)
    
    if not customer_id:
        st.warning("⚠️ No customer selected")
        st.info("👉 Please select a customer from the Customers page to view their 360° profile.")
        st.markdown("---")
        st.markdown("**How to view a customer:**")
        st.markdown("1. Go to **👥 Customers** page (use sidebar)")
        st.markdown("2. Click **View Details** on any customer card")
        return
    
    # Load customer data from CRM
    try:
        customer_data = get_crm_customer_by_id(customer_id)
    except Exception as e:
        st.error(f"Error loading customer data: {e}")
        import traceback
        with st.expander("Error Details"):
            st.code(traceback.format_exc())
        return
    
    if not customer_data:
        st.error(f"❌ Customer not found: {customer_id}")
        st.info("The customer may have been deleted or the ID is invalid.")
        if st.button("Clear Selection"):
            del st.session_state['selected_customer']
            st.rerun()
        return
    
    # Load Navigator-specific data
    try:
        reader = NavigatorDataReader()
        navigator_data = reader.get_customer_by_id(customer_id)
    except Exception as e:
        st.warning(f"Could not load Navigator data: {e}")
        navigator_data = None
    
    # Back button
    if st.button("← Back to Customers"):
        # Clear the selected customer and return to customers page
        if 'selected_customer' in st.session_state:
            del st.session_state['selected_customer']
        st.info("👈 Use sidebar to navigate back to Customers page")
        st.rerun()
    
    # Render customer profile
    try:
        render_customer_header(customer_data)
    except Exception as e:
        st.error(f"Error rendering header: {e}")
    
    # Main content in columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Primary information
        try:
            render_contact_info(customer_data)
        except Exception as e:
            st.error(f"Error rendering contact info: {e}")
        
        try:
            render_navigator_status(navigator_data)
        except Exception as e:
            st.error(f"Error rendering Navigator status: {e}")
        
        try:
            render_relationship_info(navigator_data)
        except Exception as e:
            st.error(f"Error rendering relationship info: {e}")
        
        try:
            render_activity_timeline(navigator_data)
        except Exception as e:
            st.error(f"Error rendering activity timeline: {e}")
    
    with col2:
        # Secondary information
        try:
            render_appointments(customer_id)
        except Exception as e:
            st.error(f"Error rendering appointments: {e}")
        
        try:
            render_notes(customer_id)
        except Exception as e:
            st.error(f"Error rendering notes: {e}")
    
    # Quick actions at bottom
    st.markdown("---")
    try:
        render_quick_actions(customer_id, customer_data)
    except Exception as e:
        st.error(f"Error rendering quick actions: {e}")
