"""
Leads Page - Manage anonymous user sessions and leads
"""
import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from core.adapters.streamlit_crm import StreamlitCRMStorage

def render():
    """Render the Leads management page"""
    st.title("🔥 Leads Management")
    st.write("Manage anonymous user sessions and lead nurturing")
    
    # Initialize CRM storage adapter
    crm_adapter = StreamlitCRMStorage()
    
    # Add cleanup section at the top
    with st.expander("🗑️ Data Cleanup", expanded=False):
        render_cleanup_section()
    
    # Create tabs for different lead views
    tab1, tab2, tab3 = st.tabs(["Active Sessions", "Recent Activity", "Lead Conversion"])
    
    with tab1:
        render_active_sessions()
    
    with tab2:
        render_recent_activity()
    
    with tab3:
        render_conversion_opportunities()

def render_cleanup_section():
    """Render data cleanup controls"""
    st.subheader("Delete Anonymous Leads")
    st.write("Remove anonymous leads that have no contact information.")
    
    # Get all leads and analyze them
    all_leads = get_all_leads()
    
    anonymous_count = 0
    synthetic_count = 0
    named_count = 0
    
    for lead in all_leads:
        if is_anonymous_lead(lead):
            anonymous_count += 1
        elif is_synthetic_lead(lead):
            synthetic_count += 1
        elif has_contact_name(lead):
            named_count += 1
    
    # Display counts
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Anonymous Leads", anonymous_count, help="Leads with no name or contact info")
    with col2:
        st.metric("Synthetic Leads", synthetic_count, help="Test/demo leads (will be preserved)")
    with col3:
        st.metric("Named Leads", named_count, help="Leads with contact information (will be preserved)")
    
    # Delete button with confirmation
    if anonymous_count > 0:
        st.warning(f"⚠️ This will permanently delete {anonymous_count} anonymous lead(s)")
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("🗑️ Delete Anonymous Leads", type="primary", use_container_width=True):
                deleted_count = delete_anonymous_leads()
                st.success(f"✅ Deleted {deleted_count} anonymous leads")
                st.rerun()
        with col_btn2:
            st.info("Synthetic leads and leads with names will be preserved")
    else:
        st.success("✅ No anonymous leads to delete")

def render_active_sessions():
    """Render active user sessions"""
    st.header("Active User Sessions")
    
    # Get all session files
    session_files = get_session_files()
    
    if not session_files:
        st.info("No active sessions found")
        return
    
    # Display session count
    st.metric("Active Sessions", len(session_files))
    
    # Create columns for session display
    for i, session_file in enumerate(session_files[:20]):  # Limit to 20 for performance
        with st.expander(f"Session {i+1}: {session_file['name']}", expanded=False):
            display_session_details(session_file)

def render_recent_activity():
    """Render recent user activity"""
    st.header("Recent Activity")
    
    # Get session files sorted by modification time
    session_files = get_session_files(sort_by_time=True)
    
    if not session_files:
        st.info("No recent activity found")
        return
    
    # Show activity from last 24 hours
    recent_sessions = [
        s for s in session_files 
        if s['modified_time'] > datetime.now() - timedelta(hours=24)
    ]
    
    st.metric("Active in Last 24h", len(recent_sessions))
    
    for session in recent_sessions[:10]:  # Show last 10
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**{session['name']}**")
            if session.get('data', {}).get('user_name'):
                st.write(f"User: {session['data']['user_name']}")
        
        with col2:
            st.write(f"Modified: {session['modified_time'].strftime('%H:%M')}")
        
        with col3:
            progress = calculate_session_progress(session.get('data', {}))
            st.progress(progress, text=f"{int(progress*100)}%")

def render_conversion_opportunities():
    """Render potential conversion opportunities"""
    st.header("Conversion Opportunities")
    
    session_files = get_session_files()
    
    # Analyze sessions for conversion potential
    high_intent = []
    medium_intent = []
    low_intent = []
    
    for session in session_files:
        data = session.get('data', {})
        intent_score = calculate_intent_score(data)
        
        if intent_score >= 0.7:
            high_intent.append((session, intent_score))
        elif intent_score >= 0.4:
            medium_intent.append((session, intent_score))
        else:
            low_intent.append((session, intent_score))
    
    # Display by intent level
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("High Intent", len(high_intent), delta_color="normal")
        for session, score in high_intent[:5]:
            with st.container():
                st.write(f"**{session['name']}**")
                st.write(f"Intent Score: {score:.2f}")
                if st.button(f"Convert to Customer", key=f"convert_{session['name']}"):
                    convert_lead_to_customer(session)
    
    with col2:
        st.metric("Medium Intent", len(medium_intent))
        for session, score in medium_intent[:3]:
            st.write(f"{session['name']} ({score:.2f})")
    
    with col3:
        st.metric("Low Intent", len(low_intent))
        st.write(f"Total sessions with low engagement")

def get_session_files(sort_by_time=False):
    """Get all session files from Navigator data"""
    session_files = []
    
    # Check for leads in CRM JSONL file first
    from pathlib import Path
    leads_file = Path("/Users/shane/Desktop/cca_senior_navigator_v3/data/crm/leads.jsonl")
    if leads_file.exists():
        import json
        try:
            with open(leads_file, 'r') as f:
                for line in f:
                    if line.strip():
                        lead = json.loads(line)
                        session_files.append({
                            'name': lead.get('lead_id', 'Unknown'),
                            'path': str(leads_file),
                            'modified_time': datetime.fromisoformat(lead.get('created_at', datetime.now().isoformat())),
                            'size': len(json.dumps(lead)),
                            'data': lead,
                            'source': 'crm_leads'
                        })
        except (json.JSONDecodeError, Exception) as e:
            st.warning(f"Error loading CRM leads: {e}")
    
    # Look for anonymous session files in Navigator users directory
    users_dir = Path("/Users/shane/Desktop/cca_senior_navigator_v3/data/users")
    
    if users_dir.exists():
        for file_path in users_dir.glob("anon_*.json"):
            try:
                stat = file_path.stat()
                modified_time = datetime.fromtimestamp(stat.st_mtime)
                
                # Try to load session data
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                session_files.append({
                    'name': file_path.stem,
                    'path': str(file_path),
                    'modified_time': modified_time,
                    'size': stat.st_size,
                    'data': data,
                    'source': 'navigator_session'
                })
            except (json.JSONDecodeError, PermissionError):
                # Skip invalid or inaccessible files
                continue
    
    if sort_by_time:
        session_files.sort(key=lambda x: x['modified_time'], reverse=True)
    
    return session_files

def display_session_details(session_file):
    """Display detailed information about a session"""
    data = session_file.get('data', {})
    source = session_file.get('source', 'unknown')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Session Info:**")
        st.write(f"• Source: {source}")
        st.write(f"• File: {session_file['name']}")
        st.write(f"• Modified: {session_file['modified_time'].strftime('%Y-%m-%d %H:%M')}")
        st.write(f"• Size: {session_file['size']} bytes")
        
        # Extract user ID based on source
        if source == 'crm_leads':
            uid = data.get('lead_id', 'Unknown')
            st.write(f"• Lead ID: {uid}")
            st.write(f"• Contact: {data.get('contact_info', {}).get('name', 'N/A')}")
            st.write(f"• Email: {data.get('contact_info', {}).get('email', 'N/A')}")
        else:
            uid = data.get('uid', data.get('anonymous_uid', 'Unknown'))
            st.write(f"• User ID: {uid}")
        
        # Check for profile data
        profile = data.get('profile', {})
        if profile:
            st.write("**Profile Data:**")
            for key, value in profile.items():
                if value:
                    st.write(f"• {key}: {value}")
    
    with col2:
        st.write("**Progress:**")
        progress = calculate_session_progress(data)
        st.progress(progress, text=f"Completion: {int(progress*100)}%")
        
        # Show journey progress
        journey = data.get('mcip_contracts', {}).get('journey', {})
        if journey:
            st.write("**Journey Progress:**")
            completed = journey.get('completed_products', [])
            unlocked = journey.get('unlocked_products', [])
            current_hub = journey.get('current_hub', 'Not set')
            
            st.write(f"• Current Hub: {current_hub}")
            st.write(f"• Completed: {len(completed)} products")
            st.write(f"• Unlocked: {len(unlocked)} products")
            
            if journey.get('recommended_next'):
                st.write(f"• Next: {journey['recommended_next']}")
        
        # Show care recommendation status
        care_rec = data.get('mcip_contracts', {}).get('care_recommendation', {})
        if care_rec:
            status = care_rec.get('status', 'unknown')
            tier = care_rec.get('tier')
            st.write(f"**Care Status:** {status}")
            if tier:
                st.write(f"**Care Tier:** {tier}")

def calculate_session_progress(data):
    """Calculate how far through the Navigator a session has progressed"""
    if not data:
        return 0.0
    
    # Check journey progress
    journey = data.get('mcip_contracts', {}).get('journey', {})
    if journey:
        completed = journey.get('completed_products', [])
        unlocked = journey.get('unlocked_products', [])
        
        # Base score on completed products
        total_possible = max(len(completed) + len(unlocked), 1)
        completion_score = len(completed) / total_possible
        
        # Bonus for having profile data
        profile_score = 0.2 if data.get('profile') else 0.0
        
        # Bonus for care recommendation progress
        care_rec = data.get('mcip_contracts', {}).get('care_recommendation', {})
        care_score = 0.1 if care_rec.get('tier') else 0.0
        
        return min(1.0, completion_score * 0.7 + profile_score + care_score)
    
    return 0.1  # Minimal progress for having a session

def calculate_intent_score(data):
    """Calculate lead intent score based on session data"""
    if not data:
        return 0.0
    
    score = 0.0
    
    # Journey completion indicates engagement
    journey = data.get('mcip_contracts', {}).get('journey', {})
    if journey:
        completed = journey.get('completed_products', [])
        unlocked = journey.get('unlocked_products', [])
        
        # Score based on product completion
        if completed:
            score += 0.4 * (len(completed) / max(len(completed) + len(unlocked), 1))
        
        # Current hub indicates engagement level
        current_hub = journey.get('current_hub', '')
        if current_hub in ['concierge', 'care_planning']:
            score += 0.2
        elif current_hub in ['financial', 'outcomes']:
            score += 0.3
    
    # Profile data indicates personalization
    if data.get('profile'):
        score += 0.2
    
    # Care recommendation progress
    care_rec = data.get('mcip_contracts', {}).get('care_recommendation', {})
    if care_rec:
        if care_rec.get('tier'):
            score += 0.3
        elif care_rec.get('status') != 'new':
            score += 0.1
    
    # Recent activity (last updated)
    last_updated = data.get('last_updated', 0)
    if last_updated:
        # Recent activity within last week gets bonus
        import time
        if time.time() - last_updated < 7 * 24 * 3600:
            score += 0.1
    
    return min(1.0, score)

def convert_lead_to_customer(session):
    """Convert a lead session to a customer record"""
    try:
        data = session.get('data', {})
        uid = data.get('uid', 'unknown')
        profile = data.get('profile', {})
        
        # Create customer record
        customer_data = {
            'id': f"customer_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'name': profile.get('name', f"Lead {uid}"),
            'source': 'Navigator Lead Conversion',
            'conversion_date': datetime.now().isoformat(),
            'original_session': session['name'],
            'navigator_uid': uid,
            'navigator_data': data,
            'lead_score': calculate_intent_score(data),
            'progress_score': calculate_session_progress(data)
        }
        
        # Add any additional profile data
        if profile:
            customer_data.update({
                'email': profile.get('email', ''),
                'phone': profile.get('phone', ''),
                'location': profile.get('location', ''),
            })
        
        # Save to CRM
        crm_adapter = StreamlitCRMStorage()
        crm_adapter.save_customer(customer_data)
        
        st.success(f"Successfully converted {customer_data['name']} to customer!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error converting lead: {str(e)}")

def get_all_leads():
    """Get all leads from both CRM JSONL and Navigator session files"""
    all_leads = []
    
    # Load from CRM leads.jsonl
    from pathlib import Path
    leads_file = Path("/Users/shane/Desktop/cca_senior_navigator_v3/data/crm/leads.jsonl")
    if leads_file.exists():
        try:
            with open(leads_file, 'r') as f:
                for line in f:
                    if line.strip():
                        lead = json.loads(line)
                        lead['_source'] = 'crm_jsonl'
                        lead['_file_path'] = str(leads_file)
                        all_leads.append(lead)
        except (json.JSONDecodeError, Exception) as e:
            st.warning(f"Error loading CRM leads: {e}")
    
    # Load from Navigator session files
    users_dir = Path("/Users/shane/Desktop/cca_senior_navigator_v3/data/users")
    if users_dir.exists():
        for file_path in users_dir.glob("anon_*.json"):
            try:
                with open(file_path, 'r') as f:
                    session_data = json.load(f)
                    lead = {
                        'lead_id': file_path.stem,
                        '_source': 'navigator_session',
                        '_file_path': str(file_path),
                        'session_data': session_data,
                        'contact_info': session_data.get('profile', {}),
                        'metadata': {
                            'session_id': file_path.stem,
                            'uid': session_data.get('uid', session_data.get('anonymous_uid', ''))
                        }
                    }
                    all_leads.append(lead)
            except (json.JSONDecodeError, PermissionError):
                continue
    
    return all_leads

def is_anonymous_lead(lead):
    """Check if a lead is anonymous (no name or contact info)"""
    # Check for synthetic/test markers first
    if is_synthetic_lead(lead):
        return False
    
    # Check contact info
    contact_info = lead.get('contact_info', {})
    
    # Has a name?
    if contact_info.get('name') and contact_info['name'].strip():
        return False
    
    # Has email?
    if contact_info.get('email') and contact_info['email'].strip():
        return False
    
    # Check session data profile
    session_data = lead.get('session_data', {})
    profile = session_data.get('profile', {})
    
    if profile.get('name') and profile['name'].strip():
        return False
    
    if profile.get('email') and profile['email'].strip():
        return False
    
    # Check lead_id for synthetic patterns
    lead_id = lead.get('lead_id', '')
    if 'sample' in lead_id.lower() or 'test' in lead_id.lower() or 'demo' in lead_id.lower():
        return False
    
    # If no identifying info found, it's anonymous
    return True

def is_synthetic_lead(lead):
    """Check if a lead is synthetic (test/demo data)"""
    # Check lead_id for synthetic markers
    lead_id = lead.get('lead_id', '')
    if any(marker in lead_id.lower() for marker in ['sample', 'synthetic', 'test', 'demo']):
        return True
    
    # Check metadata
    metadata = lead.get('metadata', {})
    if metadata.get('is_synthetic') or metadata.get('is_test'):
        return True
    
    # Check source
    contact_info = lead.get('contact_info', {})
    source = contact_info.get('source', '')
    if source in ['synthetic', 'test', 'demo']:
        return True
    
    return False

def has_contact_name(lead):
    """Check if lead has a contact name"""
    # Check contact_info
    contact_info = lead.get('contact_info', {})
    if contact_info.get('name') and contact_info['name'].strip():
        return True
    
    # Check session profile
    session_data = lead.get('session_data', {})
    profile = session_data.get('profile', {})
    if profile.get('name') and profile['name'].strip():
        return True
    
    return False

def delete_anonymous_leads():
    """Delete all anonymous leads, preserving synthetic and named leads"""
    deleted_count = 0
    all_leads = get_all_leads()
    
    # Separate leads by source
    session_files_to_delete = []
    jsonl_lead_ids_to_delete = set()
    
    # Identify which leads to delete
    for lead in all_leads:
        if is_anonymous_lead(lead):
            source = lead['_source']
            
            if source == 'navigator_session':
                session_files_to_delete.append(Path(lead['_file_path']))
            elif source == 'crm_jsonl':
                jsonl_lead_ids_to_delete.add(lead.get('lead_id'))
    
    # Delete session files
    for file_path in session_files_to_delete:
        try:
            if file_path.exists():
                file_path.unlink()
                deleted_count += 1
        except Exception as e:
            st.error(f"Error deleting session file {file_path.name}: {e}")
    
    # Delete from JSONL file (one bulk operation)
    if jsonl_lead_ids_to_delete:
        leads_file = Path("/Users/shane/Desktop/cca_senior_navigator_v3/data/crm/leads.jsonl")
        if leads_file.exists():
            try:
                # Read all leads and keep only non-anonymous ones
                remaining_leads = []
                with open(leads_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            existing_lead = json.loads(line)
                            if existing_lead.get('lead_id') not in jsonl_lead_ids_to_delete:
                                remaining_leads.append(existing_lead)
                
                # Rewrite file with remaining leads (single operation)
                with open(leads_file, 'w') as f:
                    for remaining_lead in remaining_leads:
                        f.write(json.dumps(remaining_lead) + '\n')
                
                deleted_count += len(jsonl_lead_ids_to_delete)
            except Exception as e:
                st.error(f"Error updating leads JSONL file: {e}")
    
    return deleted_count
