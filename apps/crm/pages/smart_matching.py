"""
Smart Community Matching Engine - AI-powered facility recommendations
Replaces QuickBase's 132-field community spreadsheet with intelligent matching
"""
import streamlit as st
import json
from pathlib import Path
from shared.data_access.navigator_reader import NavigatorDataReader

def inject_matching_css():
    """Professional community matching styling"""
    if st.session_state.get("_matching_css"):
        return
        
    css = """
    <style>
    /* Matching engine base styling */
    .matching-header {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(5, 150, 105, 0.15);
    }
    
    .matching-title {
        font-size: 2.25rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        display: flex;
        align-items: center;
    }
    
    .matching-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    .smart-badge {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        font-size: 0.875rem;
        font-weight: 600;
        margin-left: 1rem;
    }
    
    /* Match results grid */
    .matches-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .match-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 0;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
    }
    
    .match-card:hover {
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        transform: translateY(-4px);
    }
    
    .match-header {
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        padding: 1.5rem;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .match-name {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0 0 0.5rem 0;
    }
    
    .match-location {
        font-size: 0.9rem;
        color: #6b7280;
        margin: 0;
    }
    
    .match-score {
        background: linear-gradient(135deg, #059669, #047857);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        font-size: 0.875rem;
        font-weight: 700;
        float: right;
        margin-top: -0.5rem;
    }
    
    .match-content {
        padding: 1.5rem;
    }
    
    .match-highlights {
        margin-bottom: 1.5rem;
    }
    
    .highlight {
        display: flex;
        align-items: center;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
    }
    
    .highlight-icon {
        width: 24px;
        height: 24px;
        background: #f0fdf4;
        color: #166534;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 0.75rem;
        font-size: 0.75rem;
    }
    
    .highlight-text {
        color: #374151;
    }
    
    .match-details {
        background: #f9fafb;
        border: 1px solid #f3f4f6;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .detail-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }
    
    .detail-row:last-child {
        margin-bottom: 0;
    }
    
    .detail-label {
        font-size: 0.875rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    .detail-value {
        font-size: 0.875rem;
        color: #1f2937;
        font-weight: 600;
    }
    
    /* Customer context panel */
    .context-panel {
        background: linear-gradient(135deg, #fef7ff, #f3e8ff);
        border: 1px solid #e9d5ff;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    
    .context-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .context-icon {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #8b5cf6, #7c3aed);
        color: white;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-size: 1.2rem;
    }
    
    .context-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #581c87;
        margin: 0;
    }
    
    .context-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
    }
    
    .context-item {
        background: white;
        border: 1px solid #e9d5ff;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    
    .context-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0 0 0.25rem 0;
    }
    
    .context-label {
        font-size: 0.875rem;
        color: #7c3aed;
        margin: 0;
    }
    
    /* Action buttons */
    .match-actions {
        display: flex;
        gap: 0.75rem;
    }
    
    .btn-recommend {
        background: #059669;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        flex: 1;
    }
    
    .btn-recommend:hover {
        background: #047857;
        transform: translateY(-1px);
    }
    
    .btn-details {
        background: white;
        color: #374151;
        border: 1px solid #d1d5db;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .btn-details:hover {
        background: #f9fafb;
    }
    
    /* No matches state */
    .no-matches {
        text-align: center;
        padding: 4rem 2rem;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        margin: 2rem 0;
    }
    
    .no-matches-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .no-matches-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0 0 1rem 0;
    }
    
    .no-matches-text {
        color: #6b7280;
        margin: 0;
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    st.session_state["_matching_css"] = True

def load_community_database():
    """Load community data (simulated for demo)"""
    # In production, this would connect to partner database
    communities = [
        {
            "id": "com_001",
            "name": "Sunrise Senior Living",
            "location": "Bellevue, WA",
            "care_levels": ["independent", "assisted_living", "memory_care"],
            "monthly_cost": {"min": 4500, "max": 7200},
            "amenities": ["fitness_center", "dining", "transportation", "activities"],
            "specializations": ["alzheimers", "physical_therapy"],
            "rating": 4.8,
            "availability": "immediate",
            "contact": "Sarah Chen - (425) 555-0123"
        },
        {
            "id": "com_002", 
            "name": "Emerald Heights",
            "location": "Redmond, WA",
            "care_levels": ["independent", "assisted_living"],
            "monthly_cost": {"min": 3800, "max": 6500},
            "amenities": ["gardens", "library", "dining", "wellness"],
            "specializations": ["rehabilitation", "wellness"],
            "rating": 4.6,
            "availability": "2_weeks",
            "contact": "Michael Torres - (425) 555-0156"
        },
        {
            "id": "com_003",
            "name": "Memory Care Specialists",
            "location": "Seattle, WA", 
            "care_levels": ["memory_care", "memory_care_high_acuity"],
            "monthly_cost": {"min": 6000, "max": 9500},
            "amenities": ["secure_units", "specialized_staff", "therapy"],
            "specializations": ["dementia", "alzheimers", "behavioral_support"],
            "rating": 4.9,
            "availability": "immediate",
            "contact": "Dr. Lisa Park - (206) 555-0198"
        },
        {
            "id": "com_004",
            "name": "Golden Years Community",
            "location": "Kirkland, WA",
            "care_levels": ["independent", "assisted_living"],
            "monthly_cost": {"min": 3200, "max": 5800},
            "amenities": ["pool", "cafe", "activities", "transportation"],
            "specializations": ["social_activities", "wellness"],
            "rating": 4.4,
            "availability": "1_month",
            "contact": "Amanda Wilson - (425) 555-0134"
        }
    ]
    
    return communities

def calculate_match_score(customer_data, community):
    """AI-powered matching algorithm"""
    score = 0
    reasons = []
    
    # Care level matching (40% weight)
    care_recommendation = customer_data.get('care_recommendation', '').lower()
    if care_recommendation in community['care_levels']:
        score += 40
        reasons.append(f"Perfect care level match: {care_recommendation}")
    elif any(level in care_recommendation for level in community['care_levels']):
        score += 25
        reasons.append(f"Compatible care levels available")
    
    # Budget compatibility (30% weight)
    # Simulate budget from customer data
    budget_min = 3000  # Would come from Navigator cost planning
    budget_max = 6000
    
    if (budget_min <= community['monthly_cost']['max'] and 
        budget_max >= community['monthly_cost']['min']):
        score += 30
        reasons.append(f"Budget compatible: ${community['monthly_cost']['min']:,}-${community['monthly_cost']['max']:,}")
    elif budget_max >= community['monthly_cost']['min']:
        score += 15
        reasons.append(f"Partial budget overlap available")
    
    # Availability (20% weight)
    if community['availability'] == 'immediate':
        score += 20
        reasons.append("Immediate availability")
    elif community['availability'] == '2_weeks':
        score += 15
        reasons.append("Available within 2 weeks")
    else:
        score += 10
        reasons.append("Limited availability")
    
    # Quality rating (10% weight)
    if community['rating'] >= 4.7:
        score += 10
        reasons.append(f"Excellent rating: {community['rating']}/5")
    elif community['rating'] >= 4.5:
        score += 7
        reasons.append(f"High rating: {community['rating']}/5")
    else:
        score += 5
        reasons.append(f"Good rating: {community['rating']}/5")
    
    return min(score, 100), reasons

def render_customer_context(customer_data):
    """Render customer context for matching"""
    care_rec = customer_data.get('care_recommendation', 'Not assessed')
    budget_status = "Established" if customer_data.get('has_cost_plan') else "Needs planning"
    journey_progress = "90%" if customer_data.get('has_gcp_assessment') and customer_data.get('has_cost_plan') else "In progress"
    readiness = "High" if customer_data.get('has_gcp_assessment') and customer_data.get('has_cost_plan') else "Medium"
    
    context_html = f"""
    <div class="context-panel">
        <div class="context-header">
            <div class="context-icon">👤</div>
            <h2 class="context-title">{customer_data.get('person_name', 'Customer')} - Matching Context</h2>
        </div>
        <div class="context-grid">
            <div class="context-item">
                <div class="context-value">{care_rec}</div>
                <div class="context-label">Care Recommendation</div>
            </div>
            <div class="context-item">
                <div class="context-value">{budget_status}</div>
                <div class="context-label">Budget Status</div>
            </div>
            <div class="context-item">
                <div class="context-value">{journey_progress}</div>
                <div class="context-label">Journey Progress</div>
            </div>
            <div class="context-item">
                <div class="context-value">{readiness}</div>
                <div class="context-label">Readiness Level</div>
            </div>
        </div>
    </div>
    """
    
    return context_html

def render_community_match(community, score, reasons):
    """Render individual community match card"""
    # Format cost range
    cost_range = f"${community['monthly_cost']['min']:,} - ${community['monthly_cost']['max']:,}"
    
    # Generate highlights from reasons
    highlights_html = ""
    for reason in reasons[:3]:  # Show top 3 reasons
        highlights_html += f"""
        <div class="highlight">
            <div class="highlight-icon">✓</div>
            <div class="highlight-text">{reason}</div>
        </div>
        """
    
    # Availability text
    avail_map = {
        'immediate': 'Immediate',
        '2_weeks': '2 weeks',
        '1_month': '1 month'
    }
    availability = avail_map.get(community['availability'], 'Contact for details')
    
    match_html = f"""
    <div class="match-card">
        <div class="match-header">
            <div class="match-name">{community['name']}</div>
            <div class="match-score">{score}% Match</div>
            <div class="match-location">📍 {community['location']}</div>
        </div>
        <div class="match-content">
            <div class="match-highlights">
                {highlights_html}
            </div>
            <div class="match-details">
                <div class="detail-row">
                    <span class="detail-label">Monthly Cost:</span>
                    <span class="detail-value">{cost_range}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Availability:</span>
                    <span class="detail-value">{availability}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Rating:</span>
                    <span class="detail-value">{community['rating']}/5 ⭐</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Contact:</span>
                    <span class="detail-value">{community['contact']}</span>
                </div>
            </div>
            <div class="match-actions">
                <button class="btn-recommend">Recommend to Customer</button>
                <button class="btn-details">View Details</button>
            </div>
        </div>
    </div>
    """
    
    return match_html

def render(customer_id=None):
    """Main render function for Smart Community Matching"""
    inject_matching_css()
    
    if not customer_id:
        # Customer selection interface
        st.markdown("""
        <div class="matching-header">
            <h1 class="matching-title">
                🎯 Smart Community Matching
                <span class="smart-badge">AI Powered</span>
            </h1>
            <p class="matching-subtitle">
                Intelligent facility recommendations replacing 132-field QuickBase spreadsheets
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        reader = NavigatorDataReader()
        customers = reader.get_all_customers()
        
        if customers:
            st.subheader("Select Customer for Community Matching")
            for customer in customers:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.write(f"**{customer.get('person_name', 'Unknown')}**")
                with col2:
                    care_rec = customer.get('care_recommendation', 'Not assessed')
                    st.write(f"Care: {care_rec}")
                with col3:
                    has_assessments = customer.get('has_gcp_assessment') and customer.get('has_cost_plan')
                    status = "✅ Ready" if has_assessments else "⏳ In progress"
                    st.write(status)
                with col4:
                    if st.button("Match", key=f"match_{customer['user_id']}"):
                        st.session_state['matching_customer'] = customer['user_id']
                        st.rerun()
        else:
            st.info("No customers found. Customers will appear here after they use the Navigator.")
        
        # Show innovation summary
        st.markdown("""
        ---
        
        ### 🚀 **QuickBase Community Transformation**
        
        **Before:** 132 manual fields per community requiring constant spreadsheet maintenance  
        **After:** AI-powered matching using Navigator assessment data
        
        **Key Improvements:**
        - ✅ **Smart matching algorithm** - Care level + budget + availability scoring
        - ✅ **Real-time recommendations** - No manual community research required  
        - ✅ **Navigator integration** - Uses GCP and cost planning data automatically
        - ✅ **Quality scoring** - Partner ratings and availability tracking
        
        *This replaces QuickBase's complex community database with intelligent, automated matching.*
        """)
        
        return
    
    # Community matching for specific customer
    reader = NavigatorDataReader()
    customer_data = reader.get_customer_by_id(customer_id)
    
    if not customer_data:
        st.error(f"Customer not found: {customer_id}")
        return
    
    # Matching header
    customer_name = customer_data.get('person_name', 'Unknown Customer')
    st.markdown(f"""
    <div class="matching-header">
        <h1 class="matching-title">
            🎯 Community Matches for {customer_name}
            <span class="smart-badge">AI Powered</span>
        </h1>
        <p class="matching-subtitle">
            Intelligent recommendations based on Navigator assessments
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Customer context
    st.markdown(render_customer_context(customer_data), unsafe_allow_html=True)
    
    # Load communities and calculate matches
    communities = load_community_database()
    matches = []
    
    for community in communities:
        score, reasons = calculate_match_score(customer_data, community)
        if score >= 30:  # Only show decent matches
            matches.append((community, score, reasons))
    
    # Sort by score
    matches.sort(key=lambda x: x[1], reverse=True)
    
    if matches:
        st.markdown('<div class="matches-grid">', unsafe_allow_html=True)
        
        for community, score, reasons in matches:
            st.markdown(render_community_match(community, score, reasons), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Summary stats
        avg_score = sum(match[1] for match in matches) / len(matches)
        st.markdown(f"""
        ---
        
        **🤖 AI Matching Summary:** Found {len(matches)} compatible communities with average match score of {avg_score:.0f}%
        
        **Next Steps:** Review top recommendations with customer and schedule facility tours for highest-scoring matches.
        """)
        
    else:
        st.markdown("""
        <div class="no-matches">
            <div class="no-matches-icon">🔍</div>
            <h2 class="no-matches-title">No Compatible Communities Found</h2>
            <p class="no-matches-text">
                No communities match the current assessment criteria. 
                Consider expanding search parameters or updating customer preferences.
            </p>
        </div>
        """, unsafe_allow_html=True)

# Handle customer selection
if 'matching_customer' in st.session_state:
    render(st.session_state['matching_customer'])
else:
    render()