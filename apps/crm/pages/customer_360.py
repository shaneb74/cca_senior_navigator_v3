"""
CRM Customer 360° View - Complete customer profile and interaction history
Displays all available information about a customer from Navigator and CRM data
"""
import streamlit as st
from datetime import datetime
from shared.data_access.navigator_reader import NavigatorDataReader
from shared.data_access.crm_repository import CrmRepository
from core.adapters.streamlit_crm import get_crm_customer_by_id, delete_crm_customer

# Set page config first - constrain layout
st.set_page_config(layout="centered", initial_sidebar_state="expanded")

def inject_customer_360_css():
    """Inject Customer 360 specific styling"""
    css = """
    <style>
    /* Enable proper scrolling */
    .stApp {
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }
    
    .main {
        overflow-y: auto !important;
        overflow-x: hidden !important;
        height: 100vh !important;
    }
    
    /* Nuclear option - constrain EVERYTHING */
    .stMainBlockContainer {
        max-width: 800px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }
    
    .st-emotion-cache-1v0mbdj, 
    .st-emotion-cache-z5fcl4,
    .st-emotion-cache-18kf3ut,
    .st-emotion-cache-1f0nklw,
    [class*="st-emotion-cache"] {
        max-width: 100% !important;
        overflow: visible !important;
    }
    
    /* Let Streamlit handle the centering, we just add styling */
    .customer-360-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
    }
    
    .customer-name {
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        word-wrap: break-word;
    }
    
    .customer-id {
        font-size: 0.9rem;
        opacity: 0.9;
        margin: 0;
    }
    
    .info-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #667eea;
    }
    
    .info-card h3 {
        margin-top: 0;
        color: #1f2937;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    
    .info-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f1f5f9;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .info-row:last-child {
        border-bottom: none;
    }
    
    .info-label {
        font-weight: 600;
        color: #64748b;
        word-wrap: break-word;
    }
    
    .info-value {
        color: #1f2937;
        text-align: right;
        word-wrap: break-word;
        overflow-wrap: break-word;
        max-width: 60%;
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
        max-width: 100%;
        overflow: hidden;
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
        word-wrap: break-word;
    }
    
    .timeline-content {
        color: #1f2937;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    /* Ensure Streamlit columns don't overflow */
    [data-testid="column"] {
        overflow: hidden;
    }
    
    /* Fix button overflow */
    .stButton button {
        white-space: normal;
        word-wrap: break-word;
        height: auto;
        min-height: 2.5rem;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_customer_header(customer_data):
    """Render the customer header with name and key info"""
    name = customer_data.get('name') or customer_data.get('person_name', 'Unknown Customer')
    customer_id = customer_data.get('id') or customer_data.get('user_id', 'N/A')
    
    # Use a container to ensure proper boundary constraints
    header_html = f"""
    <div class="customer-360-header">
        <h1 class="customer-name">{name}</h1>
        <p class="customer-id">Customer ID: {customer_id}</p>
    </div>
    """
    
    # Render within Streamlit's container
    st.markdown(header_html, unsafe_allow_html=True)


def render_contact_info(customer_data):
    """Render contact information card"""
    email = customer_data.get('email') or customer_data.get('contact_email', 'Not provided')
    phone = customer_data.get('phone') or customer_data.get('contact_phone', 'Not provided')
    source = customer_data.get('source', 'Unknown')
    created = customer_data.get('created_at', 'Unknown')
    
    # Handle different created_at formats (string, float timestamp, datetime)
    if created != 'Unknown':
        try:
            if isinstance(created, (int, float)):
                # Unix timestamp
                from datetime import datetime
                joined = datetime.fromtimestamp(created).strftime('%Y-%m-%d')
            elif isinstance(created, str) and len(created) >= 10:
                # ISO date string
                joined = created[:10]
            else:
                joined = str(created)
        except:
            joined = 'Unknown'
    else:
        joined = 'Unknown'
    
    # Pure HTML - no Streamlit components that create extra containers
    html = f"""
    <div class="info-card">
        <h3>📞 Contact Information</h3>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Phone:</strong> {phone}</p>
        <p><strong>Source:</strong> {source}</p>
        <p><strong>Joined:</strong> {joined}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_navigator_status(navigator_data):
    """Render Navigator assessment status"""
    
    if not navigator_data:
        st.markdown("""
        <div class="info-card">
            <h3>🧭 Senior Navigator Status</h3>
            <p style="color: #64748b;">No Navigator assessment data available</p>
        </div>
        """, unsafe_allow_html=True)
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
    
    # Build additional details HTML
    additional_html = ""
    
    # Care Recommendation if available
    if has_gcp:
        care_rec = navigator_data.get('care_recommendation', 'Assessment complete')
        additional_html += f"""
        <hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 1rem 0;">
        <p><strong>Care Recommendation:</strong> {care_rec}</p>
        """
        
        # Assessment summary if available
        assessment_summary = navigator_data.get('assessment_summary')
        if assessment_summary:
            additional_html += f"""
            <details style="margin-top: 0.5rem;">
                <summary style="cursor: pointer; color: #3b82f6; font-weight: 500;">📋 Assessment Details</summary>
                <div style="margin-top: 0.5rem; padding: 0.5rem; background: #f8fafc; border-radius: 4px;">
                    {assessment_summary}
                </div>
            </details>
            """
    
    # Cost Summary if available
    if has_cost:
        cost_summary = navigator_data.get('cost_summary')
        if cost_summary:
            additional_html += f"""
            <details style="margin-top: 0.5rem;">
                <summary style="cursor: pointer; color: #3b82f6; font-weight: 500;">💰 Cost Planning Details</summary>
                <div style="margin-top: 0.5rem; padding: 0.5rem; background: #f8fafc; border-radius: 4px;">
                    {cost_summary}
                </div>
            </details>
            """
    
    # Pure HTML - single markdown call
    html = f"""
    <div class="info-card">
        <h3>🧭 Senior Navigator Status</h3>
        <div style="margin-bottom: 1rem;">
            <p style="margin: 0; color: #64748b; font-size: 0.875rem;">GCP Assessment</p>
            <span class="status-badge {gcp_badge_class}">{gcp_status}</span>
        </div>
        <div style="margin-bottom: 1rem;">
            <p style="margin: 0; color: #64748b; font-size: 0.875rem;">Cost Planning</p>
            <span class="status-badge {cost_badge_class}">{cost_status}</span>
        </div>
        <div>
            <p style="margin: 0; color: #64748b; font-size: 0.875rem;">Journey Stage</p>
            <p style="margin: 0.5rem 0 0 0; font-weight: 600; color: #1f2937;">{journey_stage}</p>
        </div>
        {additional_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_medical_profile(customer_data):
    """Render medical profile with conditions, medications, and assessments"""
    
    # Check if customer has enriched medical data
    if 'medical_conditions' not in customer_data and 'medication_count' not in customer_data:
        return
    
    # Medical conditions
    conditions = customer_data.get('medical_conditions', [])
    conditions_html = ""
    if conditions:
        conditions_list = "</li><li>".join(conditions[:5])  # Limit to top 5
        conditions_html = f"<ul style='margin: 0.5rem 0;'><li>{conditions_list}</li></ul>"
        if len(conditions) > 5:
            conditions_html += f"<p style='color: #64748b; font-size: 0.9rem;'>+ {len(conditions) - 5} more conditions</p>"
    else:
        conditions_html = "<p style='color: #64748b;'>No conditions recorded</p>"
    
    # Medications
    med_count = customer_data.get('medication_count', 0)
    allergies = customer_data.get('allergies') or 'None known'
    diet = customer_data.get('diet_restrictions') or 'None'
    
    # Assessment scores
    scores = customer_data.get('assessment_scores', {})
    scores_html = ""
    if scores:
        mmse = scores.get('mmse_score', 'N/A')
        functional = scores.get('functional_score', 'N/A')
        pain = scores.get('pain_level', 'N/A')
        depression = scores.get('depression_screen', 'N/A')
        
        scores_html = f"""<hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 1rem 0;">
<p style="margin-bottom: 0.5rem;"><strong>Assessment Scores:</strong></p>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
    <div style="background: #f8fafc; padding: 0.5rem; border-radius: 4px;">
        <div style="font-size: 0.8rem; color: #64748b;">MMSE Score</div>
        <div style="font-weight: 600; color: #1f2937;">{mmse}/30</div>
    </div>
    <div style="background: #f8fafc; padding: 0.5rem; border-radius: 4px;">
        <div style="font-size: 0.8rem; color: #64748b;">Functional</div>
        <div style="font-weight: 600; color: #1f2937;">{functional}/100</div>
    </div>
    <div style="background: #f8fafc; padding: 0.5rem; border-radius: 4px;">
        <div style="font-size: 0.8rem; color: #64748b;">Pain Level</div>
        <div style="font-weight: 600; color: #1f2937;">{pain}/10</div>
    </div>
    <div style="background: #f8fafc; padding: 0.5rem; border-radius: 4px;">
        <div style="font-size: 0.8rem; color: #64748b;">Depression</div>
        <div style="font-weight: 600; color: #1f2937;">{depression}</div>
    </div>
</div>"""
    
    html = f"""<div class="info-card">
<h3>🏥 Medical Profile</h3>
<p><strong>Medical Conditions:</strong></p>
{conditions_html}
<p style="margin-top: 0.5rem;"><strong>Medications:</strong> {med_count} current medications</p>
<p><strong>Allergies:</strong> {allergies}</p>
<p><strong>Diet Restrictions:</strong> {diet}</p>
{scores_html}
</div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_adl_assessment(customer_data):
    """Render ADL (Activities of Daily Living) assessment"""
    
    adl = customer_data.get('adl_assessment')
    if not adl:
        return
    
    # ADL categories with icons
    adl_icons = {
        'bathing': '🚿',
        'dressing': '👔',
        'toileting': '🚽',
        'transferring': '🚶',
        'eating': '🍽️',
        'medication': '💊'
    }
    
    # Status colors
    status_colors = {
        'Independent': '#10b981',
        'Needs Reminders': '#3b82f6',
        'Needs Assistance': '#f59e0b',
        'Fully Dependent': '#ef4444',
        'Needs Setup': '#3b82f6',
        'Needs Feeding Assistance': '#f59e0b',
        'Injectable Meds': '#f59e0b',
        'Needs Administration': '#f59e0b',
        'Requires Equipment': '#f59e0b',
        'Two Person Transfer': '#ef4444'
    }
    
    # Build ADL items
    adl_html = ""
    for category, status in adl.items():
        icon = adl_icons.get(category, '📋')
        color = status_colors.get(status, '#64748b')
        category_display = category.replace('_', ' ').title()
        
        adl_html += f"""<div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: #f8fafc; border-radius: 4px; margin-bottom: 0.5rem;">
    <div>
        <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
        <strong>{category_display}</strong>
    </div>
    <span style="color: {color}; font-weight: 600; font-size: 0.9rem;">{status}</span>
</div>
"""
    
    # Mobility info
    mobility = customer_data.get('mobility', {})
    mobility_html = ""
    if mobility:
        equipment = mobility.get('equipment', 'None')
        fall_risk = mobility.get('fall_risk', 'Unknown')
        
        risk_color = {
            'Low': '#10b981',
            'Moderate': '#f59e0b',
            'High': '#ef4444'
        }.get(fall_risk, '#64748b')
        
        mobility_html = f"""<hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 1rem 0;">
<p style="margin-bottom: 0.5rem;"><strong>Mobility Assessment:</strong></p>
<p>🦽 <strong>Equipment:</strong> {equipment}</p>
<p>⚠️ <strong>Fall Risk:</strong> <span style="color: {risk_color}; font-weight: 600;">{fall_risk}</span></p>"""
    
    html = f"""<div class="info-card">
<h3>📊 ADL Assessment</h3>
<p style="color: #64748b; font-size: 0.9rem; margin-bottom: 0.75rem;">Activities of Daily Living independence levels</p>
{adl_html}
{mobility_html}
</div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_family_involvement(customer_data):
    """Render family context and involvement"""
    
    family = customer_data.get('family_context')
    if not family:
        return
    
    relationship = family.get('primary_contact_relationship', 'Unknown')
    involvement = family.get('involvement_level', 'Unknown')
    decision_maker = family.get('decision_maker', False)
    lives_nearby = family.get('lives_nearby', False)
    financial_poa = family.get('financial_poa', False)
    
    # Build badges
    badges = []
    if decision_maker:
        badges.append('<span style="background: #dbeafe; color: #1e40af; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">Decision Maker</span>')
    if lives_nearby:
        badges.append('<span style="background: #dcfce7; color: #15803d; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">Lives Nearby</span>')
    if financial_poa:
        badges.append('<span style="background: #fef3c7; color: #92400e; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">Financial POA</span>')
    
    badges_html = " ".join(badges) if badges else ""
    
    html = f"""<div class="info-card">
<h3>👨‍👩‍👧‍👦 Family Involvement</h3>
<p><strong>Primary Contact:</strong> {relationship}</p>
<p><strong>Involvement Level:</strong> {involvement}</p>
{f'<div style="margin-top: 0.5rem;">{badges_html}</div>' if badges_html else ''}
</div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_relationship_info(navigator_data):
    """Render relationship and care recipient information"""
    if not navigator_data:
        return
    
    relationship = navigator_data.get('relationship_type')
    if relationship:
        person_name = navigator_data.get('person_name', '')
        person_html = f"<p><strong>Care Recipient:</strong> {person_name}</p>" if person_name else ""
        
        html = f"""
        <div class="info-card">
            <h3>👥 Relationship Information</h3>
            <p><strong>Relationship:</strong> {relationship}</p>
            {person_html}
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)


def render_appointments(customer_id):
    """Render customer appointments"""
    crm_repo = CrmRepository()
    appointments = crm_repo.list_records("appointments")
    
    # Filter appointments for this customer
    customer_appointments = [
        a for a in appointments 
        if customer_id in [a.get('customer_id'), a.get('user_id')]
    ]
    
    # Build appointments HTML
    if customer_appointments:
        appointments_html = ""
        for appt in customer_appointments:
            status = appt.get('status', 'Unknown')
            appt_type = appt.get('appointment_type', 'Consultation')
            scheduled = appt.get('scheduled_at', 'Not scheduled')
            confirmation = appt.get('confirmation_id', 'N/A')
            
            status_class = "status-complete" if status.lower() == "scheduled" else "status-in-progress"
            
            appointments_html += f"""
            <div style="padding: 0.75rem; background: #f8fafc; border-radius: 8px; margin-bottom: 0.5rem;">
                <p style="margin: 0; font-weight: 600; color: #1f2937;">{appt_type}</p>
                <p style="margin: 0.25rem 0 0 0; font-size: 0.875rem; color: #64748b;">
                    {scheduled} • <span class="status-badge {status_class}">{status}</span>
                </p>
                <p style="margin: 0.25rem 0 0 0; font-size: 0.875rem; color: #64748b;">
                    Confirmation: {confirmation}
                </p>
            </div>
            """
    else:
        appointments_html = '<p style="color: #64748b;">No appointments scheduled</p>'
    
    html = f"""
    <div class="info-card">
        <h3>📅 Appointments</h3>
        {appointments_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
    # Keep button as Streamlit component (outside the HTML card)
    if st.button("➕ Schedule New Appointment", type="primary", key=f"sched_appt_{customer_id}"):
        st.session_state['schedule_for_customer'] = customer_id
        st.info("📞 Please navigate to **Appointments** page using the sidebar to schedule")


def render_notes(customer_id):
    """Render customer notes and interactions"""
    crm_repo = CrmRepository()
    notes = crm_repo.list_records("notes")
    
    # Filter notes for this customer
    customer_notes = [
        n for n in notes 
        if customer_id in [n.get('customer_id'), n.get('user_id')]
    ]
    
    # Build notes HTML
    if customer_notes:
        notes_html = ""
        for note in customer_notes[-5:]:  # Show last 5 notes
            created = note.get('created_at', 'Unknown')
            content = note.get('note', 'No content')
            note_type = note.get('note_type', 'General')
            created_date = created[:10] if created != 'Unknown' else 'Unknown'
            
            notes_html += f"""
            <div class="timeline-item">
                <p class="timeline-date">{created_date} • {note_type}</p>
                <div class="timeline-content">{content}</div>
            </div>
            """
        
        if len(customer_notes) > 5:
            notes_html += f'<p style="color: #64748b; font-size: 0.875rem;">+ {len(customer_notes) - 5} more notes</p>'
    else:
        notes_html = '<p style="color: #64748b;">No notes recorded</p>'
    
    html = f"""
    <div class="info-card">
        <h3>📝 Notes & Interactions</h3>
        {notes_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
    # Quick action button (outside HTML card)
    if st.button("➕ Add Note", type="primary", key=f"add_note_{customer_id}"):
        st.session_state['add_note_customer'] = customer_id
        st.info("📝 Please navigate to **Notes & Interactions** page using the sidebar to add a note")


def render_activity_timeline(navigator_data):
    """Render customer activity timeline"""
    
    if not navigator_data:
        content_html = '<p style="color: #64748b;">No activity data available</p>'
    else:
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
            
            content_html = f"""
            <p><strong>Status:</strong> {activity_status}</p>
            <p><strong>Last Seen:</strong> {last_activity}</p>
            """
        else:
            content_html = '<p style="color: #64748b;">No activity recorded</p>'
    
    html = f"""
    <div class="info-card">
        <h3>🕒 Activity Timeline</h3>
        {content_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_quick_actions(customer_id, customer_data):
    """Render quick action buttons"""
    # Title as HTML for consistency
    html = '<div class="info-card"><h3>⚡ Quick Actions</h3></div>'
    st.markdown(html, unsafe_allow_html=True)
    
    # Stack buttons vertically instead of using columns
    if st.button("📞 Schedule Call", use_container_width=True, key=f"schedule_call_{customer_id}"):
        st.session_state['schedule_for_customer'] = customer_id
        st.toast("📞 Customer marked for scheduling - use Appointments page")
    
    if st.button("📝 Add Note", use_container_width=True, key=f"quick_note_{customer_id}"):
        st.session_state['add_note_customer'] = customer_id
        st.toast("📝 Customer marked for note - use Notes page")
    
    if st.button("📧 Send Email", use_container_width=True, key=f"send_email_{customer_id}"):
        email = customer_data.get('email') or customer_data.get('contact_email')
        if email:
            st.info(f"📧 Email: {email}")
        else:
            st.warning("No email on file")
    
    if st.button("🏘️ Match Communities", use_container_width=True, key=f"match_comm_{customer_id}"):
        st.session_state['match_for_customer'] = customer_id
        st.toast("🏘️ Customer marked for matching - use Smart Matching page")
    
    # Danger zone - delete button
    st.markdown("---")
    st.markdown("**⚠️ Danger Zone**")
    
    # Use a confirmation pattern
    if 'confirm_delete' not in st.session_state:
        st.session_state['confirm_delete'] = None
    
    if st.session_state['confirm_delete'] == customer_id:
        # Show confirmation buttons
        st.warning(f"⚠️ Are you sure you want to delete **{customer_data.get('name', customer_id)}**?")
        st.write(f"**Customer ID:** `{customer_id}`")
        st.write("This action cannot be undone.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Delete", use_container_width=True, type="primary", key=f"confirm_delete_{customer_id}"):
                # Show debug info FIRST before anything else
                st.write("🔵 DELETE BUTTON CLICKED!")
                st.write(f"🔵 Customer ID to delete: `{customer_id}`")
                st.write(f"🔵 Customer name: {customer_data.get('name', 'Unknown')}")
                
                # Perform the deletion
                try:
                    st.write(f"� About to call delete_crm_customer...")
                    
                    # Call the delete function
                    result = delete_crm_customer(customer_id)
                    
                    st.write(f"� Delete function returned: **{result}**")
                    
                    if result:
                        st.success(f"✅ Customer deleted successfully!")
                        st.write("🔵 Clearing session state...")
                        # Clear selected customer and confirmation state
                        if 'selected_customer' in st.session_state:
                            del st.session_state['selected_customer']
                        st.session_state['confirm_delete'] = None
                        st.balloons()
                        st.write("🔵 About to refresh page in 2 seconds...")
                        # Force a full rerun to refresh customer list
                        import time
                        time.sleep(2)
                        st.write("🔵 Calling st.rerun()...")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to delete customer - not found in database")
                        st.write("🔵 Customer was not found in any data source")
                        st.session_state['confirm_delete'] = None
                except Exception as e:
                    st.error(f"❌ Error during deletion: {str(e)}")
                    st.write(f"🔵 Exception type: {type(e).__name__}")
                    st.exception(e)
                    st.session_state['confirm_delete'] = None
        with col2:
            if st.button("❌ Cancel", use_container_width=True, key=f"cancel_delete_{customer_id}"):
                st.session_state['confirm_delete'] = None
                st.rerun()
    else:
        # Show initial delete button
        if st.button("🗑️ Delete Customer", use_container_width=True, type="secondary", key=f"delete_customer_{customer_id}"):
            st.session_state['confirm_delete'] = customer_id
            st.rerun()


def render():
    """Main render function for Customer 360 view"""
    
    try:
        inject_customer_360_css()
    except Exception as e:
        st.error(f"Error loading CSS: {e}")
    
    # Check if we have a selected customer
    customer_id = st.session_state.get('selected_customer')
    
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
    
    # Use single column layout to avoid width issues
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
    
    # Enriched data sections (medical, ADL, family)
    if 'medical_conditions' in customer_data or 'medication_count' in customer_data:
        try:
            render_medical_profile(customer_data)
        except Exception as e:
            st.error(f"❌ Medical profile error: {type(e).__name__}")
    
    if 'adl_assessment' in customer_data:
        try:
            render_adl_assessment(customer_data)
        except Exception as e:
            st.error(f"❌ ADL assessment error: {type(e).__name__}")
    
    if 'family_context' in customer_data:
        try:
            render_family_involvement(customer_data)
        except Exception as e:
            st.error(f"❌ Family involvement error: {type(e).__name__}")
    
    # Secondary information
    try:
        render_appointments(customer_id)
    except Exception as e:
        st.error(f"Error rendering appointments: {e}")
    
    try:
        render_notes(customer_id)
    except Exception as e:
        st.error(f"Error rendering notes: {e}")
    
    try:
        render_activity_timeline(navigator_data)
    except Exception as e:
        st.error(f"Error rendering activity timeline: {e}")    # Quick actions at bottom
    st.markdown("---")
    try:
        render_quick_actions(customer_id, customer_data)
    except Exception as e:
        st.error(f"Error rendering quick actions: {e}")
