"""
CRM Contacts page - manage advisor contacts and referral sources
Clean, professional styling following the lobby design pattern
"""
import streamlit as st
from shared.data_access.crm_repository import CrmRepository

def inject_crm_css():
    """Reuse the same clean CSS from customers page"""
    if st.session_state.get("_crm_css_injected"):
        return
        
    # Same CSS as customers page - keeping it DRY
    css = """
    <style>
    .stApp { background-color: #ffffff; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
    .crm-header { background: #ffffff; border-bottom: 1px solid #e6edf5; padding: 1.5rem 0; margin-bottom: 2rem; }
    .crm-title { font-size: 2rem; font-weight: 700; color: #1f2937; margin: 0; }
    .crm-subtitle { font-size: 1.1rem; color: #64748b; margin: 0.5rem 0 0 0; }
    .stDeployButton { display: none !important; }
    .stDecoration { display: none !important; }
    
    .contact-form {
        background: #ffffff;
        border: 1px solid #e6edf5;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
    }
    
    .contact-list {
        background: #ffffff;
        border: 1px solid #e6edf5;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 2rem 0;
    }
    
    .contact-item {
        padding: 1rem;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .contact-item:last-child {
        border-bottom: none;
    }
    
    .contact-name {
        font-weight: 600;
        color: #1f2937;
    }
    
    .contact-details {
        font-size: 0.9rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    st.session_state["_crm_css_injected"] = True

def render():
    """Main render function for contacts page"""
    inject_crm_css()
    
    # Header
    st.markdown("""
    <div class="crm-header">
        <h1 class="crm-title">Contacts & Referrals</h1>
        <p class="crm-subtitle">Manage healthcare providers, facilities, and referral sources</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load existing contacts
    crm_repo = CrmRepository()
    contacts = crm_repo.list_records("contacts")
    
    # Add new contact form
    st.markdown('<div class="contact-form">', unsafe_allow_html=True)
    st.subheader("Add New Contact")
    
    with st.form("add_contact", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name")
            organization = st.text_input("Organization")
            phone = st.text_input("Phone")
        with col2:
            last_name = st.text_input("Last Name")
            title = st.text_input("Title/Role")
            email = st.text_input("Email")
        
        contact_type = st.selectbox("Contact Type", [
            "Healthcare Provider", 
            "Senior Living Facility", 
            "Home Care Agency",
            "Insurance Representative",
            "Legal/Financial Advisor",
            "Other Professional"
        ])
        
        notes = st.text_area("Notes", height=80)
        
        submitted = st.form_submit_button("Add Contact", type="primary")
        
        if submitted and first_name and last_name:
            new_contact = {
                "id": f"contact_{len(contacts)+1:04d}",
                "first_name": first_name,
                "last_name": last_name,
                "organization": organization,
                "title": title,
                "phone": phone,
                "email": email,
                "contact_type": contact_type,
                "notes": notes,
                "created_date": st.session_state.get("today", "2024-11-05")
            }
            
            crm_repo.save_record("contacts", new_contact)
            st.success(f"Added {first_name} {last_name} to contacts")
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display existing contacts
    if contacts:
        st.markdown('<div class="contact-list">', unsafe_allow_html=True)
        st.subheader(f"Contacts ({len(contacts)})")
        
        # Search/filter
        search_term = st.text_input("Search contacts...", placeholder="Name, organization, or type")
        
        # Filter contacts
        filtered_contacts = contacts
        if search_term:
            search_lower = search_term.lower()
            filtered_contacts = [c for c in contacts if 
                               search_lower in c.get('first_name', '').lower() or
                               search_lower in c.get('last_name', '').lower() or
                               search_lower in c.get('organization', '').lower() or
                               search_lower in c.get('contact_type', '').lower()]
        
        for contact in filtered_contacts:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div class="contact-item">
                        <div>
                            <div class="contact-name">{contact.get('first_name', '')} {contact.get('last_name', '')}</div>
                            <div class="contact-details">
                                {contact.get('title', '')} at {contact.get('organization', '')}<br>
                                {contact.get('contact_type', '')} • {contact.get('phone', '')} • {contact.get('email', '')}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("Edit", key=f"edit_{contact['id']}", help="Edit contact"):
                        st.info("Edit functionality coming soon")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No contacts yet. Add your first contact above.")