"""
Smart Community Matching Engine - AI-powered facility recommendations
Replaces QuickBase's 132-field community spreadsheet with intelligent matching
"""
import streamlit as st
import json
from pathlib import Path
from shared.data_access.navigator_reader import NavigatorDataReader
from shared.data_access.quickbase_client import quickbase_client

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
    """Load community data from QuickBase WA Communities table"""
    return quickbase_client.get_communities()

def calculate_match_score(customer_data, community):
<<<<<<< Updated upstream
    """AI-powered matching algorithm - respects care level gating based on diagnosis"""
    score = 0
    reasons = []
    
    # Care level matching (40% weight) - Use actual recommendation which respects gating
    care_recommendation = customer_data.get('care_recommendation', '').lower()
    
    if care_recommendation in community['care_levels']:
        score += 40
        reasons.append(f"Perfect care level match: {care_recommendation}")
    elif any(level in care_recommendation for level in community['care_levels']):
        score += 25
        reasons.append(f"Compatible care levels available")
=======
    """Enhanced AI-powered matching algorithm with QuickBase integration and customer preferences"""
    score = 0
    reasons = []
    
    # Get customer preferences if available
    preferences = PreferencesManager.get_preferences()
    pref_data = PreferencesManager.get_crm_matching_data() if preferences else {}
    
    # Get QuickBase-specific data for advanced matching
    qb_data = community.get('qb_data', {})
    
    # CRITICAL SAFETY & MEDICAL MATCHING (40% weight)
    # These are placement blockers if needed but not available
    
    # Care level matching (25% weight) - Use actual recommendation which respects gating
    care_recommendation = customer_data.get('care_recommendation', '').lower()
    
    if care_recommendation in community['care_levels']:
        score += 25
        reasons.append(f"✅ Perfect care level match: {care_recommendation}")
    elif any(level in care_recommendation for level in community['care_levels']):
        score += 18
        reasons.append(f"✅ Compatible care levels available")
>>>>>>> Stashed changes
    else:
        reasons.append(f"⚠️ Care level mismatch: needs {care_recommendation}, available {community['care_levels']}")
    
<<<<<<< Updated upstream
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
    
    # Availability (20% weight) - Enhanced with real vacancy data
    if community['availability'] == 'immediate':
        score += 20
        reasons.append("✅ Immediate availability")
    elif community['availability'] == '2_weeks':
        score += 15
=======
    # Critical equipment/capability matching (15% weight total)
    critical_matches = 0
    critical_total = 0
    
    # Check for mobility assistance needs (HIGH PRIORITY)
    if customer_data.get('mobility_assistance') or pref_data.get('needs_mobility_assistance'):
        critical_total += 1
        if qb_data.get('hoyer_lift'):
            score += 8
            critical_matches += 1
            reasons.append("🦽 Critical: Hoyer Lift available for mobility assistance")
        else:
            reasons.append("⚠️ Critical: Mobility assistance needed but no Hoyer Lift")
    
    # Check for memory care needs (HIGH PRIORITY)
    if 'memory' in care_recommendation or pref_data.get('needs_memory_care'):
        critical_total += 1
        if qb_data.get('memory_care_dedicated'):
            score += 8
            critical_matches += 1
            reasons.append("🧠 Critical: Dedicated Memory Care unit available")
        else:
            reasons.append("⚠️ Critical: Memory care needed but not specialized facility")
    
    # Check for heavy care needs (MEDIUM PRIORITY)
    if customer_data.get('complex_care') or pref_data.get('needs_heavy_care'):
        critical_total += 1
        if qb_data.get('two_person_transfers'):
            score += 4
            critical_matches += 1
            reasons.append("👥 Two-person transfer capability available")
        elif qb_data.get('awake_staff'):
            score += 3
            critical_matches += 1
            reasons.append("🌙 24/7 awake staff for complex care needs")
    
    # Check for bariatric needs (MEDIUM PRIORITY)
    if customer_data.get('bariatric_care') or pref_data.get('needs_bariatric'):
        critical_total += 1
        if qb_data.get('bariatric'):
            score += 6
            critical_matches += 1
            reasons.append("💪 Bariatric care capabilities available")
        else:
            reasons.append("⚠️ Bariatric care needed but not available")
    
    # COMMON MEDICAL SERVICES MATCHING (15% weight)
    medical_score = 0
    
    # Diabetes/insulin management (VERY COMMON)
    if customer_data.get('diabetes') or pref_data.get('needs_insulin'):
        if qb_data.get('insulin_management'):
            medical_score += 6
            reasons.append("💉 Insulin management services available")
        else:
            reasons.append("ℹ️ Diabetes care - verify insulin management capability")
    
    # Wound care services (COMMON)
    if customer_data.get('wound_care') or pref_data.get('needs_wound_care'):
        if qb_data.get('wound_care'):
            medical_score += 4
            reasons.append("🩹 Professional wound care services available")
        else:
            reasons.append("ℹ️ Wound care needed - verify clinical capabilities")
    
    # 24/7 supervision (HIGH-RISK RESIDENTS)
    if customer_data.get('high_risk') or pref_data.get('needs_supervision'):
        if qb_data.get('awake_staff'):
            medical_score += 5
            reasons.append("👨‍⚕️ 24/7 awake staff supervision available")
        else:
            reasons.append("⚠️ 24/7 supervision needed - verify staffing levels")
    
    score += medical_score
    
    # HIGH-IMPACT LIFESTYLE PREFERENCES (20% weight)
    lifestyle_score = 0
    
    # Pet policies (MAJOR QUALITY OF LIFE FACTOR)
    if pref_data.get('has_pets') or customer_data.get('emotional_support_animal'):
        if qb_data.get('pet_friendly'):
            lifestyle_score += 10
            reasons.append("🐕 Pet-friendly policies - emotional support available")
        else:
            lifestyle_score -= 5
            reasons.append("❌ Pets not allowed - may impact placement")
    
    # Language/cultural compatibility (COMMUNICATION CRITICAL)
    family_language = pref_data.get('primary_language', 'English')
    if family_language != 'English':
        community_languages = qb_data.get('languages_spoken', '')
        if family_language.lower() in community_languages.lower():
            lifestyle_score += 8
            reasons.append(f"🗣️ {family_language} language services available")
        else:
            lifestyle_score -= 3
            reasons.append(f"⚠️ {family_language} language services not confirmed")
    
    # Independence preferences (COOKING AUTONOMY)
    if pref_data.get('values_independence') or customer_data.get('independent_living'):
        if qb_data.get('full_kitchen'):
            lifestyle_score += 6
            reasons.append("🍳 Full kitchen available for independent cooking")
        else:
            reasons.append("ℹ️ Dining services provided - limited cooking independence")
    
    score += lifestyle_score
    
    # GEOGRAPHIC PREFERENCE MATCHING (15% weight)
    location_score = 0
    if pref_data.get('preferred_regions'):
        community_location = community.get('location', '').lower()
        
        for region in pref_data['preferred_regions']:
            if region == 'bellevue_area' and 'bellevue' in community_location:
                location_score += 15
                reasons.append("🎯 Perfect: Preferred Bellevue area location")
                break
            elif region == 'eastside' and any(city in community_location for city in ['bellevue', 'redmond', 'kirkland']):
                location_score += 12
                reasons.append("🎯 Excellent: Preferred Eastside location")
                break
            elif region == 'seattle' and 'seattle' in community_location:
                location_score += 12
                reasons.append("🎯 Excellent: Preferred Seattle area location")
                break
            elif region == 'washington_state':
                location_score += 8
                reasons.append("✓ Within preferred Washington state")
                break
        
        if location_score == 0:
            reasons.append("⚠️ Outside preferred geographic areas")
    else:
        # Default geographic bonus for Bellevue (if no preferences)
        if 'bellevue' in community.get('location', '').lower():
            location_score += 10
            reasons.append("🏠 Bellevue location advantage")
    
    score += location_score
    
    # BUDGET COMPATIBILITY (10% weight)
    budget_min = 3000  # Default
    budget_max = 6000  # Default
    
    # Adjust budget based on preferences
    if pref_data.get('budget_level') == 'tight':
        budget_max = 5000
        budget_min = 2500
    elif pref_data.get('budget_level') == 'comfortable':
        budget_min = 4000
        budget_max = 8000
    elif pref_data.get('budget_level') == 'luxury':
        budget_min = 6000
        budget_max = 12000
    
    if (budget_min <= community['monthly_cost']['max'] and 
        budget_max >= community['monthly_cost']['min']):
        score += 10
        reasons.append(f"💰 Budget compatible: ${community['monthly_cost']['min']:,}-${community['monthly_cost']['max']:,}")
    elif budget_max >= community['monthly_cost']['min']:
        score += 5
        reasons.append(f"💰 Partial budget overlap available")
    else:
        score -= 5
        reasons.append(f"⚠️ Budget concern: ${community['monthly_cost']['min']:,}-${community['monthly_cost']['max']:,}")
    
    # AVAILABILITY & TIMING (10% weight)
    timeline = pref_data.get('timeline', 'exploring')
    if timeline == 'immediate' and community['availability'] == 'immediate':
        score += 10
        reasons.append("🚨 Perfect: Immediate availability matches urgent timeline")
    elif timeline == '2_4_weeks' and community['availability'] in ['immediate', '2_weeks']:
        score += 8
        reasons.append("⏰ Excellent: Availability matches 2-4 week timeline")
    elif timeline == 'exploring' and community['availability'] == 'contact':
        score += 6
        reasons.append("🔍 Good: Contact for availability - ideal for exploration")
    else:
        score += 4
        reasons.append("✓ Standard availability consideration")
    
    # Bonus for specific vacancy information from QuickBase
    if community.get('available_beds', 0) > 0:
        score += 2
        reasons.append(f"🛏️ {community['available_beds']} beds currently available")
    
    # QUALITY RATING BONUS (5% weight)
    if community['rating'] >= 4.7:
        score += 5
        reasons.append(f"⭐ Excellent rating: {community['rating']}/5")
    elif community['rating'] >= 4.5:
        score += 3
        reasons.append(f"⭐ High rating: {community['rating']}/5")
    else:
        score += 2
        reasons.append(f"⭐ Good rating: {community['rating']}/5")
    
    # Calculate critical match percentage for priority sorting
    critical_match_rate = (critical_matches / critical_total * 100) if critical_total > 0 else 100
    
    # Add critical match indicator to reasons
    if critical_total > 0:
        if critical_match_rate == 100:
            reasons.insert(0, f"✅ ALL critical needs met ({critical_matches}/{critical_total})")
        elif critical_match_rate >= 50:
            reasons.insert(0, f"⚠️ Most critical needs met ({critical_matches}/{critical_total})")
        else:
            reasons.insert(0, f"❌ Critical needs gaps ({critical_matches}/{critical_total})")
    
    return min(score, 100), reasons
        score += 8
>>>>>>> Stashed changes
        reasons.append("⏰ Available within 2 weeks")
    elif community['availability'] == 'waitlist':
        score += 5
        reasons.append("⏳ Waitlist available")
    elif community['availability'] == 'contact':
        score += 10
        reasons.append("📞 Contact for availability details")
    else:
        score += 10
        reasons.append("Limited availability")
    
    # Bonus for specific vacancy information from QuickBase
    if community.get('available_beds', 0) > 0:
        score += 5
        reasons.append(f"🛏️ {community['available_beds']} beds currently available")
    
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
    
    # Generate highlights from reasons (using clean text only)
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
    
    # Check for selected customer in session state if no customer_id provided
    if not customer_id and 'matching_customer' in st.session_state:
        customer_id = st.session_state['matching_customer']
    
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
        
        ### 🚀 **Enhanced QuickBase Community Matching**
        
        **Before:** 132 manual fields per community requiring constant spreadsheet maintenance  
        **After:** Focused AI-driven matching using 11 high-impact criteria for precise care compatibility
        
        **Critical Safety Matching:**
        - 🦽 Hoyer Lift availability for mobility assistance
        - 🧠 Dedicated Memory Care for specialized needs  
        - 👥 Two-person transfer capabilities for complex care
        - 💪 Bariatric care equipment and training
        
        **Medical Service Compatibility:**
        - 💉 Insulin management for diabetes care
        - 🩹 Professional wound care services
        - 👨‍⚕️ 24/7 awake staff supervision
        
        **Quality of Life Factors:**
        - 🐕 Pet-friendly policies for emotional support
        - 🗣️ Language services for cultural compatibility
        - 🍳 Full kitchen access for independence
        
        *This transforms QuickBase's 132-field complexity into intelligent, safety-first community matching.*
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
        
        for idx, (community, score, reasons) in enumerate(matches):
            # Render match card with clean Streamlit components instead of complex HTML
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{community['name']}** - {score}% Match")
                    st.markdown(f"📍 {community['location']}")
                with col2:
                    st.markdown(f"**{score}%** Match", help="AI-powered compatibility score")
                
                # Show highlights as clean bullet points
                st.markdown("**Match Highlights:**")
                for reason in reasons[:3]:
                    st.markdown(f"• ✅ {reason}")
                
                # Show details
                cost_range = f"${community['monthly_cost']['min']:,} - ${community['monthly_cost']['max']:,}"
                avail_map = {
                    'immediate': '✅ Immediate',
                    '2_weeks': '⏰ 2 weeks', 
                    '1_month': '📅 1 month',
                    'waitlist': '⏳ Waitlist',
                    'contact': '📞 Contact for details'
                }
                availability = avail_map.get(community['availability'], 'Contact for details')
                
                # Create columns for metrics including vacancy info
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Monthly Cost", cost_range)
                with col2:
                    st.metric("Availability", availability)
                with col3:
                    st.metric("Rating", f"{community['rating']}/5 ⭐")
                with col4:
                    # Show real-time vacancy data from QuickBase
                    if community.get('available_beds', 0) > 0:
                        st.metric("Open Beds", f"{community['available_beds']} available")
                    elif community.get('vacancy_status'):
                        st.metric("Vacancy Status", community['vacancy_status'])
                    else:
                        st.metric("Capacity", f"{community.get('total_beds', 'N/A')} beds")
                
                # Action buttons with guaranteed unique keys using index
                col1, col2 = st.columns(2)
                with col1:
                    # Use index to guarantee unique keys
                    button_key = f"contact_{idx}_{hash(str(community)) % 10000}"
                    if st.button(f"📞 Contact {community['name']}", key=button_key):
                        # Display detailed contact information from QuickBase
                        contact_info = f"**Contact Information:**\n\n"
                        
                        if community.get('licensee'):
                            contact_info += f"**Licensee:** {community['licensee']}\n\n"
                        
                        if community.get('cell_phone'):
                            contact_info += f"**Cell Phone:** {community['cell_phone']}\n\n"
                        
                        if community.get('phone') and community.get('phone') != community.get('cell_phone'):
                            contact_info += f"**Phone:** {community['phone']}\n\n"
                        
                        if community.get('email'):
                            contact_info += f"**Email:** {community['email']}\n\n"
                        
                        if community.get('address'):
                            contact_info += f"**Address:** {community['address']}"
                        
                        st.success(contact_info)
                with col2:
                    # Use index to guarantee unique keys
                    details_key = f"details_{idx}_{hash(str(community)) % 10000}"
                    if st.button(f"📋 View Details", key=details_key):
                        # Show detailed community information including vacancy data
                        details = f"**{community['name']} Details:**\n\n"
                        details += f"**Care Type:** {community.get('care_type', 'Not specified')}\n\n"
                        details += f"**Care Levels:** {', '.join(community.get('care_levels', []))}\n\n"
                        details += f"**Monthly Cost:** ${community['monthly_cost']['min']:,} - ${community['monthly_cost']['max']:,}\n\n"
                        details += f"**Rating:** {community['rating']}/5 ⭐\n\n"
                        details += f"**Availability:** {availability}\n\n"
                        
                        # Add real-time vacancy information from QuickBase
                        if community.get('vacancy_info'):
                            details += f"**Current Vacancy Info:** {community['vacancy_info']}\n\n"
                        if community.get('available_beds', 0) > 0:
                            details += f"**Available Beds:** {community['available_beds']} currently open\n\n"
                        if community.get('total_beds'):
                            details += f"**Total Capacity:** {community['total_beds']} beds\n\n"
                        
                        details += f"**Address:** {community.get('address', 'Not specified')}"
                        st.info(details)
                
                st.markdown("---")
        
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

