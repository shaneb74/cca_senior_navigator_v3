"""
Task Queue Component - Reusable task list display
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Any


def render_task_item(task: Dict[str, Any], show_customer: bool = True):
    """Render a single task item with actions"""
    
    priority = task.get('priority', 'medium')
    customer = task.get('customer', 'Unknown')
    task_text = task.get('task', 'No description')
    task_type = task.get('type', 'general')
    due_date = task.get('due')
    
    # Priority styling
    priority_colors = {
        'urgent': '🔴',
        'high': '🟡',
        'medium': '🟢',
        'low': '⚪'
    }
    priority_icon = priority_colors.get(priority, '⚪')
    
    # Task type icons
    type_icons = {
        'call': '📞',
        'visit': '🏢',
        'email': '✉️',
        'review': '📋',
        'follow_up': '🔄',
        'appointment': '📅'
    }
    type_icon = type_icons.get(task_type, '📋')
    
    # Build task display
    col1, col2 = st.columns([5, 1])
    
    with col1:
        if show_customer:
            st.markdown(f"{priority_icon} {type_icon} **{customer}** - {task_text}")
        else:
            st.markdown(f"{priority_icon} {type_icon} {task_text}")
        
        # Show additional context
        if task.get('last_contact'):
            days_ago = task.get('days_since', 0)
            st.caption(f"Last contact: {days_ago} days ago")
        
        if due_date:
            st.caption(f"Due: {due_date}")
    
    with col2:
        action = task.get('action_button', 'View')
        if st.button(action, key=f"task_{task.get('id', hash(task_text))}"):
            # Store selected task in session state
            st.session_state['selected_task'] = task
            return True
    
    return False


def render_task_queue(tasks: List[Dict[str, Any]], title: str, show_customer: bool = True):
    """Render a complete task queue section"""
    
    if not tasks:
        st.info(f"✅ No {title.lower()}")
        return
    
    st.subheader(f"{title} ({len(tasks)})")
    
    for task in tasks:
        with st.container():
            if render_task_item(task, show_customer):
                st.rerun()
        st.markdown("---")


def render_action_required_queue(tasks: List[Dict[str, Any]]):
    """Render urgent action items with prominent styling"""
    
    if not tasks:
        return
    
    st.markdown("""
    <div style='background-color: #fff3cd; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #ffc107;'>
        <h3 style='margin: 0; color: #856404;'>🎯 ACTION REQUIRED</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")  # Spacing
    
    for task in tasks:
        priority = task.get('priority', 'medium')
        customer = task.get('customer', 'Unknown')
        task_text = task.get('task', 'No description')
        action_text = task.get('action', 'Review')
        
        # Priority colors
        bg_colors = {
            'urgent': '#f8d7da',
            'high': '#fff3cd',
            'medium': '#d1ecf1'
        }
        border_colors = {
            'urgent': '#dc3545',
            'high': '#ffc107',
            'medium': '#17a2b8'
        }
        
        bg = bg_colors.get(priority, '#e2e3e5')
        border = border_colors.get(priority, '#6c757d')
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"""
            <div style='background-color: {bg}; padding: 0.75rem; border-radius: 0.25rem; 
                        border-left: 3px solid {border}; margin-bottom: 0.5rem;'>
                <strong>{customer}</strong><br/>
                <span style='color: #666;'>{task_text}</span><br/>
                <small style='color: #888;'>{action_text}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("Act", key=f"action_{hash(customer + task_text)}", type="primary"):
                st.session_state['selected_customer'] = customer
                st.session_state['selected_action'] = action_text
                st.rerun()


def render_todays_tasks(tasks: List[Dict[str, Any]]):
    """Render today's scheduled tasks with time display"""
    
    st.subheader(f"📋 TODAY'S TASKS ({len(tasks)})")
    
    if not tasks:
        st.success("✅ All caught up for today!")
        return
    
    for task in tasks:
        time = task.get('time', '')
        task_type = task.get('type', 'call')
        customer = task.get('customer', 'Unknown')
        purpose = task.get('purpose', '')
        
        # Type-specific icons and colors
        type_config = {
            'call': {'icon': '📞', 'color': '#17a2b8'},
            'visit': {'icon': '🏢', 'color': '#28a745'},
            'email': {'icon': '✉️', 'color': '#6f42c1'},
            'review': {'icon': '📋', 'color': '#fd7e14'}
        }
        
        config = type_config.get(task_type, {'icon': '📋', 'color': '#6c757d'})
        
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            st.markdown(f"**{time}**")
        
        with col2:
            st.markdown(f"{config['icon']} **{customer}**")
            if purpose:
                st.caption(purpose)
        
        with col3:
            if st.button("✓", key=f"complete_{hash(customer + time)}", help="Mark complete"):
                st.toast(f"✅ Completed: {customer}", icon="✅")
                # Here you would mark the task complete in the backend
        
        st.markdown("---")
