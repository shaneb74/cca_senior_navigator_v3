"""
Customer Pipeline Component - Visual pipeline display
"""
import streamlit as st
from typing import List, Dict, Any


def render_pipeline_stage(stage_name: str, customers: List[Dict[str, Any]], stage_color: str):
    """Render a single pipeline stage column"""
    
    st.markdown(f"""
    <div style='background-color: {stage_color}; padding: 0.5rem; border-radius: 0.25rem; text-align: center; margin-bottom: 0.5rem;'>
        <strong style='color: white;'>{stage_name} ({len(customers)})</strong>
    </div>
    """, unsafe_allow_html=True)
    
    if not customers:
        st.caption("_No customers_")
        return
    
    for idx, customer in enumerate(customers):
        name = customer.get('name', 'Unknown')
        customer_id = customer.get('customer_id') or customer.get('id') or customer.get('user_id', idx)
        days_in_stage = customer.get('days_since', 0)
        
        # Build card content based on stage
        card_content = f"**{name}**<br/>"
        
        if 'gcp' in customer:
            gcp_status = "✅" if customer['gcp'] == 'done' else "⏳"
            card_content += f"{gcp_status} GCP "
        
        if 'cost' in customer:
            cost_status = "✅" if customer['cost'] == 'done' else "⏳"
            card_content += f"{cost_status} Cost "
        
        if 'communities_visited' in customer:
            card_content += f"<br/>🏢 {customer['communities_visited']} visits"
        
        if 'visit_scheduled' in customer:
            card_content += f"<br/>📅 {customer['visit_scheduled']}"
        
        if 'move_in' in customer:
            card_content += f"<br/>🎉 Move-in: {customer['move_in']}"
        
        if days_in_stage > 0:
            card_content += f"<br/><small>{days_in_stage} days in stage</small>"
        
        # Render card
        st.markdown(f"""
        <div style='background-color: white; padding: 0.75rem; border-radius: 0.25rem; 
                    border: 1px solid #dee2e6; margin-bottom: 0.5rem; cursor: pointer;'>
            {card_content}
        </div>
        """, unsafe_allow_html=True)
        
        # Use customer_id + stage to ensure uniqueness
        if st.button("View", key=f"pipeline_{stage_name}_{customer_id}", use_container_width=True):
            # Set customer ID (not name) for Customer 360 page
            st.session_state['selected_customer'] = customer_id
            # Set flag to trigger auto-navigation
            st.session_state['auto_navigate_to_360'] = True
            st.rerun()


def render_customer_pipeline(pipeline: Dict[str, List[Dict[str, Any]]]):
    """Render complete customer pipeline visualization"""
    
    st.subheader("📊 My Customer Pipeline")
    
    # Stage definitions
    stages = [
        {
            'key': 'new_leads',
            'name': 'New Leads',
            'color': '#6c757d'
        },
        {
            'key': 'assessing',
            'name': 'Assessing',
            'color': '#17a2b8'
        },
        {
            'key': 'touring',
            'name': 'Touring',
            'color': '#ffc107'
        },
        {
            'key': 'closing',
            'name': 'Closing',
            'color': '#28a745'
        }
    ]
    
    # Create columns for each stage
    cols = st.columns(len(stages))
    
    for idx, stage in enumerate(stages):
        with cols[idx]:
            customers = pipeline.get(stage['key'], [])
            render_pipeline_stage(stage['name'], customers, stage['color'])


def render_pipeline_summary(pipeline: Dict[str, List[Dict[str, Any]]]):
    """Render summary metrics for the pipeline"""
    
    total_customers = sum(len(customers) for customers in pipeline.values())
    new_leads = len(pipeline.get('new_leads', []))
    closing = len(pipeline.get('closing', []))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Active", total_customers)
    
    with col2:
        st.metric("New This Week", new_leads)
    
    with col3:
        st.metric("Ready to Close", closing)
    
    with col4:
        # Calculate conversion rate
        if total_customers > 0:
            conversion_rate = (closing / total_customers) * 100
            st.metric("Pipeline Health", f"{conversion_rate:.0f}%")
        else:
            st.metric("Pipeline Health", "0%")
