"""
CRM Appointments page - manage customer appointments and scheduling
Clean, professional styling following the lobby design pattern
"""
import streamlit as st
import uuid
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
            for idx, appointment in enumerate(upcoming_appointments):
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
                created_at = appointment.get('created_at', '')
                
                # Format care prep preferences if available
                care_prep = appointment.get('care_prep_preferences', {})
                care_type = care_prep.get('care_type', 'Not specified')
                location = care_prep.get('location', 'Not specified')
                budget_range = ''
                if care_prep.get('budget_min') and care_prep.get('budget_max'):
                    budget_range = f"${care_prep['budget_min']:,} - ${care_prep['budget_max']:,}/month"
                
                # Create unique key for this appointment using created_at timestamp
                appt_key = f"appt_{created_at}_{idx}"
                
                with st.container():
                    # Display appointment details
                    st.markdown(f"""
                    <div class="appointment-card">
                        <div class="appointment-time">📅 {scheduled_at}</div>
                        <div class="appointment-customer">
                            <strong>Care Recipient:</strong> {customer_name}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Show attendee if different
                    if attendee_name != customer_name:
                        st.markdown(f"""
                        <div class="appointment-customer">
                            <strong>Attendee:</strong> {attendee_name} ({relation})
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <span class="appointment-type status-scheduled">{appt_type}</span>
                    """, unsafe_allow_html=True)
                    
                    # Contact info and details
                    details_html = '<p style="margin-top: 1rem; color: #64748b;">'
                    details_html += f'<strong>Confirmation:</strong> {confirmation}<br>'
                    details_html += f'<strong>Timezone:</strong> {timezone.split("/")[-1]}<br>'
                    if email:
                        details_html += f'<strong>Email:</strong> {email}<br>'
                    if phone:
                        details_html += f'<strong>Phone:</strong> {phone}<br>'
                    details_html += '</p></div>'
                    
                    st.markdown(details_html, unsafe_allow_html=True)
                    
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
                    
                    # Action buttons (Edit and Delete)
                    col1, col2, col3 = st.columns([1, 1, 3])
                    with col1:
                        if st.button("✏️ Edit", key=f"edit_{appt_key}", use_container_width=True):
                            st.session_state[f'editing_{appt_key}'] = True
                            st.rerun()
                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_{appt_key}", type="secondary", use_container_width=True):
                            st.session_state[f'confirm_delete_{appt_key}'] = True
                            st.rerun()
                    
                    # Confirm delete dialog
                    if st.session_state.get(f'confirm_delete_{appt_key}'):
                        st.warning(f"⚠️ Delete appointment for {customer_name} on {scheduled_at}?")
                        col_yes, col_no, col_spacer = st.columns([1, 1, 3])
                        with col_yes:
                            if st.button("Yes, Delete", key=f"confirm_yes_{appt_key}", type="primary"):
                                # Delete the appointment using created_at as unique identifier
                                all_appointments = crm_repo.list_records("appointments")
                                filtered = [a for a in all_appointments if a.get('created_at') != created_at]
                                crm_repo.data["appointments"] = filtered
                                crm_repo.save()
                                st.success(f"✅ Appointment deleted")
                                del st.session_state[f'confirm_delete_{appt_key}']
                                st.rerun()
                        with col_no:
                            if st.button("Cancel", key=f"confirm_no_{appt_key}"):
                                del st.session_state[f'confirm_delete_{appt_key}']
                                st.rerun()
                    
                    # Edit dialog
                    if st.session_state.get(f'editing_{appt_key}'):
                        st.markdown("---")
                        st.subheader("Edit Appointment")
                        
                        with st.form(f"edit_form_{appt_key}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                edit_customer = st.text_input("Customer Name *", value=customer_name, key=f"e_cust_{appt_key}")
                                edit_type = st.selectbox("Appointment Type *", [
                                    "Video", "Phone", "Initial Consultation", "Follow-up Meeting", 
                                    "Assessment Review", "Care Planning Session", "Family Meeting"
                                ], index=["Video", "Phone", "Initial Consultation", "Follow-up Meeting", 
                                         "Assessment Review", "Care Planning Session", "Family Meeting"].index(appt_type) if appt_type in [
                                    "Video", "Phone", "Initial Consultation", "Follow-up Meeting", 
                                    "Assessment Review", "Care Planning Session", "Family Meeting"
                                ] else 0, key=f"e_type_{appt_key}")
                                edit_email = st.text_input("Email", value=email, key=f"e_email_{appt_key}")
                            
                            with col2:
                                # Parse date/time from scheduled_at
                                try:
                                    if " at " in scheduled_at:
                                        date_str, time_str = scheduled_at.split(" at ")
                                        edit_date = st.date_input("Date *", value=datetime.strptime(date_str.strip(), "%Y-%m-%d").date(), key=f"e_date_{appt_key}")
                                        time_obj = datetime.strptime(time_str.strip(), "%I:%M %p").time()
                                        edit_time = st.time_input("Time *", value=time_obj, key=f"e_time_{appt_key}")
                                    else:
                                        edit_date = st.date_input("Date *", key=f"e_date_{appt_key}")
                                        edit_time = st.time_input("Time *", key=f"e_time_{appt_key}")
                                except:
                                    edit_date = st.date_input("Date *", key=f"e_date_{appt_key}")
                                    edit_time = st.time_input("Time *", key=f"e_time_{appt_key}")
                                
                                edit_phone = st.text_input("Phone", value=phone, key=f"e_phone_{appt_key}")
                            
                            edit_tz = st.selectbox("Timezone *", [
                                "America/New_York", "America/Chicago", "America/Denver", 
                                "America/Los_Angeles", "America/Phoenix"
                            ], index=[
                                "America/New_York", "America/Chicago", "America/Denver", 
                                "America/Los_Angeles", "America/Phoenix"
                            ].index(timezone) if timezone in [
                                "America/New_York", "America/Chicago", "America/Denver", 
                                "America/Los_Angeles", "America/Phoenix"
                            ] else 0, key=f"e_tz_{appt_key}")
                            
                            edit_notes = st.text_area("Notes", value=notes, key=f"e_notes_{appt_key}")
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("💾 Save Changes", type="primary"):
                                    # Update the appointment
                                    all_appointments = crm_repo.list_records("appointments")
                                    for a in all_appointments:
                                        if a.get('created_at') == created_at:
                                            a['customer_name'] = edit_customer
                                            a['appointment_type'] = edit_type
                                            a['scheduled_at'] = f"{edit_date} at {edit_time.strftime('%I:%M %p')}"
                                            a['timezone'] = edit_tz
                                            a['contact_email'] = edit_email
                                            a['contact_phone'] = edit_phone
                                            a['notes'] = edit_notes
                                            a['preferred_time'] = edit_time.strftime('%I:%M %p')
                                            break
                                    crm_repo.save()
                                    st.success("✅ Appointment updated")
                                    del st.session_state[f'editing_{appt_key}']
                                    st.rerun()
                            with col_cancel:
                                if st.form_submit_button("Cancel"):
                                    del st.session_state[f'editing_{appt_key}']
                                    st.rerun()
                        
                        st.markdown("---")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("📅 No upcoming appointments scheduled")
    
    with tab2:
        st.subheader("Schedule New Appointment")
        
        with st.form("schedule_appointment"):
            col1, col2 = st.columns(2)
            
            with col1:
                customer_name = st.text_input("Customer Name *", placeholder="Care recipient's full name")
                appointment_type = st.selectbox("Appointment Type *", [
                    "Video",
                    "Phone",
                    "Initial Consultation",
                    "Follow-up Meeting", 
                    "Assessment Review",
                    "Care Planning Session",
                    "Family Meeting"
                ])
                email = st.text_input("Email", placeholder="customer@example.com")
            
            with col2:
                appointment_date = st.date_input("Date *", min_value=datetime.now().date())
                appointment_time = st.time_input("Time *", value=datetime.now().time())
                phone = st.text_input("Phone", placeholder="555-123-4567")
            
            col3, col4 = st.columns(2)
            with col3:
                timezone = st.selectbox("Timezone *", [
                    "America/New_York",
                    "America/Chicago",
                    "America/Denver",
                    "America/Los_Angeles",
                    "America/Phoenix"
                ], index=0)
            
            with col4:
                advisor = st.text_input("Advisor", value="CRM Scheduling")
            
            notes = st.text_area("Notes", placeholder="Any specific topics or preparation notes...")
            
            if st.form_submit_button("Schedule Appointment", type="primary"):
                if not customer_name:
                    st.error("Customer name is required")
                else:
                    # Generate confirmation ID for consistency with app appointments
                    import uuid
                    confirmation_id = str(uuid.uuid4())[:8].upper()
                    
                    # Create appointment record matching app format
                    appointment_data = {
                        "customer_id": None,  # CRM appointments may not have customer_id yet
                        "customer_name": customer_name,
                        "attendee_name": customer_name,  # Same as customer for CRM-created
                        "relation_to_recipient": "Self",  # Default for CRM-created
                        "appointment_type": appointment_type,
                        "scheduled_at": f"{appointment_date} at {appointment_time.strftime('%I:%M %p')}",
                        "timezone": timezone,
                        "status": "scheduled",
                        "confirmation_id": confirmation_id,
                        "contact_email": email or "",
                        "contact_phone": phone or "",
                        "notes": notes,
                        "preferred_time": appointment_time.strftime('%I:%M %p'),
                        "care_prep_preferences": {},
                        "created_at": datetime.now().isoformat(),
                        "source": "crm_manual"  # Track that this was manually created
                    }
                    
                    crm_repo.add_record("appointments", appointment_data)
                    st.success(f"✅ Appointment scheduled for {customer_name} on {appointment_date}")
                    st.info(f"Confirmation ID: **{confirmation_id}**")
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