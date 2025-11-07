"""
CRM Notes page - manage advisor notes and customer interactions
Clean, professional styling following the lobby design pattern
"""
import streamlit as st
from shared.data_access.crm_repository import CrmRepository
from datetime import datetime

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
    .note-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .note-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #f1f5f9;
    }
    .note-customer {
        color: #1e293b;
        font-weight: 600;
        font-size: 1.1rem;
    }
    .note-date {
        color: #64748b;
        font-size: 0.875rem;
    }
    .note-type {
        background: #dbeafe;
        color: #1e40af;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    .note-priority-high {
        background: #fee2e2;
        color: #dc2626;
    }
    .note-priority-urgent {
        background: #fef2f2;
        color: #b91c1c;
        animation: pulse 2s infinite;
    }
    .note-content {
        color: #374151;
        line-height: 1.6;
        margin-top: 1rem;
    }
    .note-advisor {
        color: #6b7280;
        font-style: italic;
        margin-top: 1rem;
        padding-top: 0.5rem;
        border-top: 1px solid #f3f4f6;
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    st.session_state["_crm_css_injected"] = True

def render():
    """Render the notes management page"""
    inject_crm_css()
    
    # Header
    st.markdown("""
    <div class="crm-header">
        <h1 class="crm-title">Advisor Notes & Interactions</h1>
        <p class="crm-subtitle">Track customer communications and follow-up items</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize CRM repository
    crm_repo = CrmRepository()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📝 Recent Notes", "➕ Add Note", "🔍 Search"])
    
    with tab1:
        st.subheader("Recent Customer Notes")
        
        # Get all notes (using the proper method)
        notes = crm_repo.get_all_notes()
        
        if notes:
            # Sort by creation date (most recent first)
            notes.sort(key=lambda x: x.created_at, reverse=True)
            
            for note in notes:
                priority_class = f"note-priority-{note.priority}" if note.priority in ["high", "urgent"] else ""
                
                st.markdown(f"""
                <div class="note-card">
                    <div class="note-header">
                        <div class="note-customer">Customer ID: {note.customer_id}</div>
                        <div class="note-date">{note.created_at.strftime("%m/%d/%Y %I:%M %p")}</div>
                    </div>
                    <span class="note-type {priority_class}">{note.note_type.replace('_', ' ').title()}</span>
                    <div class="note-content">{note.content}</div>
                    <div class="note-advisor">— {note.advisor_name}</div>
                    {f'<div style="margin-top: 0.5rem; color: #f59e0b; font-weight: 500;">Follow-up: {note.follow_up_date.strftime("%m/%d/%Y")}</div>' if note.follow_up_date else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📝 No customer notes found")
    
    with tab2:
        st.subheader("Add New Note")
        
        with st.form("add_note"):
            col1, col2 = st.columns(2)
            
            with col1:
                customer_id = st.text_input("Customer ID", placeholder="Enter customer ID")
                note_type = st.selectbox("Note Type", [
                    "call",
                    "email", 
                    "meeting",
                    "follow_up",
                    "assessment"
                ])
                priority = st.selectbox("Priority", ["normal", "high", "urgent"])
            
            with col2:
                advisor_name = st.text_input("Advisor Name", value="Current Advisor")
                follow_up_needed = st.checkbox("Follow-up Required")
                if follow_up_needed:
                    follow_up_date = st.date_input("Follow-up Date")
                else:
                    follow_up_date = None
            
            content = st.text_area("Note Content", 
                                 placeholder="Enter detailed notes about the interaction...",
                                 height=150)
            
            if st.form_submit_button("Add Note", type="primary"):
                if customer_id and content and advisor_name:
                    # Add note using the repository method
                    follow_up_datetime = datetime.combine(follow_up_date, datetime.min.time()) if follow_up_date else None
                    
                    note = crm_repo.add_advisor_note(
                        customer_id=customer_id,
                        advisor_name=advisor_name,
                        note_type=note_type,
                        content=content,
                        follow_up_date=follow_up_datetime,
                        priority=priority
                    )
                    
                    st.success(f"✅ Note added for customer {customer_id}")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields")
    
    with tab3:
        st.subheader("Search Notes")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_customer = st.text_input("Search by Customer ID")
        with col2:
            search_type = st.selectbox("Filter by Type", ["All", "call", "email", "meeting", "follow_up", "assessment"])
        with col3:
            search_priority = st.selectbox("Filter by Priority", ["All", "normal", "high", "urgent"])
        
        if st.button("Search Notes"):
            all_notes = crm_repo.get_all_notes()
            filtered_notes = []
            
            for note in all_notes:
                # Apply filters
                if search_customer and search_customer.lower() not in note.customer_id.lower():
                    continue
                if search_type != "All" and note.note_type != search_type:
                    continue
                if search_priority != "All" and note.priority != search_priority:
                    continue
                
                filtered_notes.append(note)
            
            if filtered_notes:
                st.write(f"Found {len(filtered_notes)} matching notes")
                
                for note in filtered_notes:
                    with st.expander(f"{note.customer_id} - {note.note_type} ({note.created_at.strftime('%m/%d/%Y')})"):
                        st.write(f"**Advisor:** {note.advisor_name}")
                        st.write(f"**Priority:** {note.priority}")
                        st.write(f"**Content:** {note.content}")
                        if note.follow_up_date:
                            st.write(f"**Follow-up:** {note.follow_up_date.strftime('%m/%d/%Y')}")
            else:
                st.info("🔍 No notes match your search criteria")

if __name__ == "__main__":
    render()