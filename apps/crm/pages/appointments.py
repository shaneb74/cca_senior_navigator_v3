"""
CRM Appointments page - manage customer appointments and scheduling
Clean, professional styling following the lobby design pattern
"""
import streamlit as st
from shared.data_access.crm_repository import CrmRepository
from datetime import datetime, timedelta

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
    .appointment-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .appointment-time {
        color: #3b82f6;
        font-weight: 600;
        font-size: 1.1rem;
    }
    .appointment-customer {
        color: #1e293b;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    .appointment-type {
        background: #dbeafe;
        color: #1e40af;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-block;
        margin-top: 0.5rem;
    }
    .status-scheduled { 
        background: #dbeafe; 
        color: #1e40af; 
    }
    .status-completed { 
        background: #dcfce7; 
        color: #15803d; 
    }
    .status-cancelled { 
        background: #fee2e2; 
        color: #dc2626; 
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    st.session_state["_crm_css_injected"] = True

def render():
    """Render the appointments management page"""
    inject_crm_css()
    
    # Header
    st.markdown("""
    <div class="crm-header">
        <h1 class="crm-title">Appointments & Scheduling</h1>
        <p class="crm-subtitle">Manage customer consultations and follow-up meetings</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize CRM repository
    crm_repo = CrmRepository()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📅 Upcoming", "➕ Schedule New", "📊 History"])
    
    with tab1:
        st.subheader("Upcoming Appointments")
        
        # Get all appointments
        appointments = crm_repo.list_records("appointments")
        
        # Filter upcoming appointments (status = scheduled)
        upcoming_appointments = [a for a in appointments if a.get('status', '').lower() == 'scheduled']
        
        # Sort by scheduled_at (most recent first)
        upcoming_appointments.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        if upcoming_appointments:
            for appointment in upcoming_appointments:
                customer_name = appointment.get('customer_name', 'Unknown Customer')
                attendee_name = appointment.get('attendee_name', customer_name)
                relation = appointment.get('relation_to_recipient', 'Self')
                appt_type = appointment.get('appointment_type', 'Consultation')
                scheduled_at = appointment.get('scheduled_at', 'No time set')
                timezone = appointment.get('timezone', 'America/New_York')
                confirmation = appointment.get('confirmation_id', 'N/A')
                email = appointment.get('contact_email', '')
                phone = appointment.get('contact_phone', '')
                notes = appointment.get('notes', '')
                
                # Format care prep preferences if available
                care_prep = appointment.get('care_prep_preferences', {})
                care_type = care_prep.get('care_type', 'Not specified')
                location = care_prep.get('location', 'Not specified')
                budget_range = ''
                if care_prep.get('budget_min') and care_prep.get('budget_max'):
                    budget_range = f"${care_prep['budget_min']:,} - ${care_prep['budget_max']:,}/month"
                
                with st.container():
                    st.markdown(f"""
                    <div class="appointment-card">
                        <div class="appointment-time">📅 {scheduled_at}</div>
                        <div class="appointment-customer">
                            <strong>Care Recipient:</strong> {customer_name}
                            {f'<br><strong>Attendee:</strong> {attendee_name} ({relation})' if attendee_name != customer_name else ''}
                        </div>
                        <span class="appointment-type status-scheduled">{appt_type}</span>
                        <p style="margin-top: 1rem; color: #64748b;">
                            <strong>Confirmation:</strong> {confirmation}<br>
                            <strong>Timezone:</strong> {timezone.split('/')[-1]}<br>
                            {f'<strong>Email:</strong> {email}<br>' if email else ''}
                            {f'<strong>Phone:</strong> {phone}<br>' if phone else ''}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show care prep details in expander
                    if care_prep or notes:
                        with st.expander("View Preparation Details"):
                            if care_prep:
                                st.markdown("**Care Preparation:**")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Care Type:** {care_type.title()}")
                                    st.write(f"**Location:** {location}")
                                    if budget_range:
                                        st.write(f"**Budget:** {budget_range}")
                                with col2:
                                    if care_prep.get('priorities'):
                                        st.write(f"**Priorities:** {', '.join(care_prep['priorities'])}")
                                    if care_prep.get('amenities'):
                                        st.write(f"**Amenities:** {', '.join(care_prep['amenities'][:5])}")
                                        if len(care_prep['amenities']) > 5:
                                            st.caption(f"+ {len(care_prep['amenities']) - 5} more")
                            if notes:
                                st.markdown("**Additional Notes:**")
                                st.info(notes)
        else:
            st.info("📅 No upcoming appointments scheduled")
    
    with tab2:
        st.subheader("Schedule New Appointment")
        
        with st.form("schedule_appointment"):
            col1, col2 = st.columns(2)
            
            with col1:
                customer_name = st.text_input("Customer Name")
                appointment_type = st.selectbox("Appointment Type", [
                    "Initial Consultation",
                    "Follow-up Meeting", 
                    "Assessment Review",
                    "Care Planning Session",
                    "Family Meeting"
                ])
                duration = st.selectbox("Duration", ["30 minutes", "60 minutes", "90 minutes"])
            
            with col2:
                appointment_date = st.date_input("Date", min_value=datetime.now().date())
                appointment_time = st.time_input("Time", value=datetime.now().time())
                advisor = st.text_input("Advisor", value="Current Advisor")
            
            notes = st.text_area("Notes", placeholder="Any specific topics or preparation notes...")
            
            if st.form_submit_button("Schedule Appointment", type="primary"):
                # Create appointment record
                appointment_data = {
                    "customer_name": customer_name,
                    "appointment_type": appointment_type,
                    "scheduled_at": f"{appointment_date} {appointment_time}",
                    "duration": duration,
                    "advisor": advisor,
                    "notes": notes,
                    "status": "scheduled"
                }
                
                crm_repo.add_record("appointments", appointment_data)
                st.success(f"✅ Appointment scheduled for {customer_name} on {appointment_date}")
                st.rerun()
    
    with tab3:
        st.subheader("Appointment History")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Completed", "Cancelled", "No Show"])
        with col2:
            date_range = st.selectbox("Date Range", ["Last 30 days", "Last 90 days", "All time"])
        
        # Show filtered appointments
        all_appointments = crm_repo.list_records("appointments")
        
        if all_appointments:
            st.write(f"Found {len(all_appointments)} appointment records")
            
            for appointment in all_appointments:
                status = appointment.get('status', 'scheduled')
                if status_filter == "All" or status.lower() == status_filter.lower():
                    with st.expander(f"{appointment.get('customer_name', 'Unknown')} - {appointment.get('scheduled_at', 'No date')}"):
                        st.write(f"**Type:** {appointment.get('appointment_type', 'Unknown')}")
                        st.write(f"**Status:** {status.title()}")
                        st.write(f"**Advisor:** {appointment.get('advisor', 'Unknown')}")
                        if appointment.get('notes'):
                            st.write(f"**Notes:** {appointment.get('notes')}")
        else:
            st.info("📊 No appointment history available")

if __name__ == "__main__":
    render()