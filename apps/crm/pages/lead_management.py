"""
Lead Management and Quality Control

Tools for analyzing lead quality and purging low-value leads.
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime, timedelta
import os


def analyze_lead_quality(lead_data):
    """Analyze lead quality based on various criteria"""
    quality_score = 0
    issues = []
    engagement_activities = []
    
    # Check for basic profile information
    profile = lead_data.get('profile', {})
    if profile.get('name'):
        quality_score += 20
    else:
        issues.append("Missing name")
    
    if profile.get('age_range') or profile.get('age'):
        quality_score += 15
    else:
        issues.append("Missing age information")
    
    if profile.get('location') or profile.get('zip_code'):
        quality_score += 15
    else:
        issues.append("Missing location")
    
    # Check for product engagement and completion
    mcip = lead_data.get('mcip_contracts', {})
    progress = lead_data.get('progress', {})
    journey = mcip.get('journey', {})
    completed_products = journey.get('completed_products', [])
    
    # Track specific product engagements
    product_engagement = {
        'gcp_completed': 'gcp' in completed_products or mcip.get('care_recommendation'),
        'cost_planner_completed': 'cost_planner' in completed_products or lead_data.get('cost_planner_v2_va_benefits') or lead_data.get('cost'),
        'discovery_learning_completed': 'discovery_learning' in completed_products,
        'pfma_completed': 'pfma' in completed_products,
        'senior_trivia_played': bool(lead_data.get('senior_trivia')),
        'additional_services_viewed': bool(lead_data.get('additional_services')),
        'learn_recommendation_completed': 'learn_recommendation' in completed_products,
        'advisor_prep_completed': 'advisor_prep' in completed_products
    }
    
    # Score based on engagement
    if product_engagement['gcp_completed']:
        quality_score += 25
        engagement_activities.append("✅ Completed GCP Assessment")
    else:
        issues.append("No care recommendation")
    
    if product_engagement['cost_planner_completed']:
        quality_score += 20
        engagement_activities.append("✅ Completed Cost Planning")
    
    if product_engagement['discovery_learning_completed']:
        quality_score += 15
        engagement_activities.append("✅ Watched Discovery Video")
    
    if product_engagement['pfma_completed']:
        quality_score += 15
        engagement_activities.append("✅ Completed Financial Assessment")
    
    if product_engagement['senior_trivia_played']:
        quality_score += 10
        engagement_activities.append("✅ Played Senior Trivia")
    
    if product_engagement['additional_services_viewed']:
        quality_score += 10
        engagement_activities.append("✅ Viewed Additional Services")
    
    if product_engagement['learn_recommendation_completed']:
        quality_score += 10
        engagement_activities.append("✅ Learned About Recommendations")
    
    if product_engagement['advisor_prep_completed']:
        quality_score += 15
        engagement_activities.append("✅ Completed Advisor Prep")
    
    # Check for contact information
    auth = lead_data.get('auth', {})
    if auth.get('email') or profile.get('email'):
        quality_score += 10
    else:
        issues.append("Missing email")
    
    # Age of lead (older leads may be stale)
    created_at = lead_data.get('created_at')
    if created_at:
        age_days = (datetime.now().timestamp() - created_at) / (24 * 3600)
        if age_days > 180:  # 6 months
            issues.append(f"Very old lead ({age_days:.0f} days)")
            quality_score -= 10
        elif age_days > 90:  # 3 months
            issues.append(f"Old lead ({age_days:.0f} days)")
            quality_score -= 5
    
    return {
        'score': max(0, quality_score),
        'issues': issues,
        'grade': get_quality_grade(quality_score),
        'engagement_activities': engagement_activities,
        'product_engagement': product_engagement
    }


def get_quality_grade(score):
    """Convert quality score to letter grade"""
    if score >= 80:
        return "A"
    elif score >= 65:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 35:
        return "D"
    else:
        return "F"


def get_all_leads():
    """Get all lead files with quality analysis"""
    leads_dir = Path("/Users/shane/Desktop/cca_senior_navigator_v3/data/users/leads")
    leads = []
    
    if leads_dir.exists():
        for file_path in leads_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                stat = file_path.stat()
                modified_time = datetime.fromtimestamp(stat.st_mtime)
                file_size = stat.st_size
                
                quality = analyze_lead_quality(data)
                
                leads.append({
                    'file': file_path.name,
                    'path': str(file_path),
                    'uid': data.get('uid', file_path.stem),
                    'size_kb': round(file_size / 1024, 1),
                    'modified': modified_time,
                    'quality': quality,
                    'data': data
                })
                
            except Exception as e:
                st.error(f"Error reading {file_path.name}: {e}")
    
    return leads


def get_converted_lead_session_ids():
    """Get set of session IDs that have been converted to customers"""
    converted_ids = set()
    customers_file = Path("/Users/shane/Desktop/cca_senior_navigator_v3/data/crm/customers.jsonl")
    
    if customers_file.exists():
        try:
            with open(customers_file, 'r') as f:
                for line in f:
                    if line.strip():
                        customer = json.loads(line)
                        session_id = customer.get('session_id')
                        if session_id and session_id != 'unknown':
                            converted_ids.add(session_id)
        except Exception as e:
            st.warning(f"Could not load customer data: {e}")
    
    return converted_ids


def show_lead_management():
    """Main lead management interface"""
    st.title("🧹 Lead Management & Quality Control")
    
    leads = get_all_leads()
    
    # Load customer data to identify converted leads
    converted_session_ids = get_converted_lead_session_ids()
    
    # Add conversion status to each lead
    for lead in leads:
        # Extract session ID from filename (e.g., "anon_909375ded6d6.json" -> "anon_909375ded6d6")
        session_id = lead['file'].replace('.json', '')
        lead['is_converted'] = session_id in converted_session_ids
    
    # Summary stats
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_leads = len(leads)
    converted_leads = len([l for l in leads if l.get('is_converted', False)])
    low_quality = len([l for l in leads if l['quality']['score'] < 35])
    very_old = len([l for l in leads if any('Very old' in issue for issue in l['quality']['issues'])])
    missing_contact = len([l for l in leads if 'Missing email' in l['quality']['issues']])
    high_engagement = len([l for l in leads if len(l['quality']['engagement_activities']) >= 4])
    
    col1.metric("Total Leads", total_leads)
    col2.metric("Converted to Customers", converted_leads, delta_color="off")
    col3.metric("Low Quality (F grade)", low_quality)
    col4.metric("Very Old (6+ months)", very_old)
    col5.metric("High Engagement (4+ activities)", high_engagement)
    
    # Filters
    st.subheader("🔍 Filter & Sort")
    
    # Add checkbox to hide converted leads
    hide_converted = st.checkbox("Hide Converted Leads (now customers)", value=True, 
                                  help="Hide leads that have been converted to customers via appointment booking")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        min_quality = st.selectbox(
            "Minimum Quality Grade",
            ["All", "A", "B", "C", "D", "F"],
            index=0
        )
    
    with col2:
        max_age_days = st.selectbox(
            "Maximum Age (days)",
            ["All", "30", "90", "180", "365"],
            index=0
        )
    
    with col3:
        min_engagement = st.selectbox(
            "Minimum Engagement",
            ["All", "High (4+)", "Medium (2+)", "Low (1+)", "None (0)"],
            index=0
        )
    
    with col4:
        sort_by = st.selectbox(
            "Sort By",
            ["Quality Score", "Engagement", "Age", "File Size", "Name"],
            index=0
        )
    
    # Apply filters
    filtered_leads = leads.copy()
    
    # Filter out converted leads if checkbox is checked
    if hide_converted:
        filtered_leads = [l for l in filtered_leads if not l.get('is_converted', False)]
    
    if min_quality != "All":
        grade_scores = {"A": 80, "B": 65, "C": 50, "D": 35, "F": 0}
        min_score = grade_scores[min_quality]
        filtered_leads = [l for l in filtered_leads if l['quality']['score'] >= min_score]
    
    if max_age_days != "All":
        max_age = int(max_age_days)
        cutoff_time = datetime.now() - timedelta(days=max_age)
        filtered_leads = [l for l in filtered_leads if l['modified'] >= cutoff_time]
    
    if min_engagement != "All":
        if min_engagement == "High (4+)":
            filtered_leads = [l for l in filtered_leads if len(l['quality']['engagement_activities']) >= 4]
        elif min_engagement == "Medium (2+)":
            filtered_leads = [l for l in filtered_leads if len(l['quality']['engagement_activities']) >= 2]
        elif min_engagement == "Low (1+)":
            filtered_leads = [l for l in filtered_leads if len(l['quality']['engagement_activities']) >= 1]
        elif min_engagement == "None (0)":
            filtered_leads = [l for l in filtered_leads if len(l['quality']['engagement_activities']) == 0]
    
    # Sort
    if sort_by == "Quality Score":
        filtered_leads.sort(key=lambda x: x['quality']['score'], reverse=True)
    elif sort_by == "Engagement":
        filtered_leads.sort(key=lambda x: len(x['quality']['engagement_activities']), reverse=True)
    elif sort_by == "Age":
        filtered_leads.sort(key=lambda x: x['modified'], reverse=True)
    elif sort_by == "File Size":
        filtered_leads.sort(key=lambda x: x['size_kb'], reverse=True)
    else:  # Name
        filtered_leads.sort(key=lambda x: x['uid'])
    
    st.write(f"Showing {len(filtered_leads)} of {total_leads} leads")
    
    # Bulk actions (always work on ALL leads, not filtered subset)
    st.subheader("🗑️ Bulk Actions")
    st.caption("⚠️ Bulk actions apply to ALL leads, not just filtered results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Count F-grade leads from ALL leads
        f_grade_leads = [l for l in leads if l['quality']['grade'] == 'F']
        if st.button(f"🗑️ Purge All F-Grade Leads ({len(f_grade_leads)})", type="secondary", disabled=len(f_grade_leads)==0):
            deleted = purge_leads_by_quality("F", leads)
            if deleted > 0:
                st.success(f"✅ Deleted {deleted} F-grade leads")
                st.rerun()
    
    with col2:
        # Count very old leads from ALL leads
        cutoff_time = datetime.now() - timedelta(days=180)
        old_leads = [l for l in leads if l['modified'] < cutoff_time]
        if st.button(f"🗑️ Purge Very Old Leads ({len(old_leads)})", type="secondary", disabled=len(old_leads)==0):
            deleted = purge_old_leads(180, leads)
            if deleted > 0:
                st.success(f"✅ Deleted {deleted} old leads")
                st.rerun()
    
    with col3:
        # Count minimal leads from ALL leads
        minimal_leads = []
        for lead in leads:
            profile = lead['data'].get('profile', {})
            mcip = lead['data'].get('mcip_contracts', {})
            progress = lead['data'].get('progress', {})
            has_name = bool(profile.get('name'))
            has_engagement = bool(mcip or progress or lead['data'].get('cost'))
            if not has_name and not has_engagement:
                minimal_leads.append(lead)
        
        if st.button(f"🗑️ Purge Empty/Minimal Leads ({len(minimal_leads)})", type="secondary", disabled=len(minimal_leads)==0):
            deleted = purge_minimal_leads(leads)
            if deleted > 0:
                st.success(f"✅ Deleted {deleted} minimal leads")
                st.rerun()
    
    with col4:
        # Count no-engagement leads from ALL leads
        no_engagement_leads = [l for l in leads if len(l['quality']['engagement_activities']) == 0]
        if st.button(f"🗑️ Purge No-Engagement Leads ({len(no_engagement_leads)})", type="secondary", disabled=len(no_engagement_leads)==0):
            deleted = purge_no_engagement_leads(leads)
            if deleted > 0:
                st.success(f"✅ Deleted {deleted} no-engagement leads")
                st.rerun()
    
    # Lead list with individual actions
    st.subheader("📋 Lead Details & Engagement Analytics")
    
    if filtered_leads:
        for lead in filtered_leads:
            engagement_count = len(lead['quality']['engagement_activities'])
            engagement_indicator = "🔥" if engagement_count >= 4 else "⚡" if engagement_count >= 2 else "💤"
            
            # Add customer conversion indicator
            is_converted = lead.get('is_converted', False)
            conversion_badge = " 👤 CUSTOMER" if is_converted else ""
            
            with st.expander(f"{engagement_indicator} {lead['uid']} - Grade {lead['quality']['grade']} ({lead['quality']['score']}pts) - {engagement_count} activities{conversion_badge}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Show conversion status
                    if is_converted:
                        st.success("✅ **Converted to Customer** - This lead has booked an appointment")
                    
                    st.write(f"**File:** {lead['file']}")
                    st.write(f"**Size:** {lead['size_kb']} KB")
                    st.write(f"**Modified:** {lead['modified'].strftime('%Y-%m-%d %H:%M')}")
                    
                    # Show engagement activities
                    if lead['quality']['engagement_activities']:
                        st.write("**🎯 Engagement Activities:**")
                        for activity in lead['quality']['engagement_activities']:
                            st.write(f"  {activity}")
                    else:
                        st.write("**❌ No engagement activities detected**")
                    
                    # Show product engagement matrix
                    with st.expander("📊 Product Engagement Matrix"):
                        engagement = lead['quality']['product_engagement']
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Core Journey:**")
                            st.write(f"{'✅' if engagement['gcp_completed'] else '❌'} GCP Assessment")
                            st.write(f"{'✅' if engagement['cost_planner_completed'] else '❌'} Cost Planning")
                            st.write(f"{'✅' if engagement['pfma_completed'] else '❌'} Financial Assessment")
                            st.write(f"{'✅' if engagement['advisor_prep_completed'] else '❌'} Advisor Prep")
                        
                        with col2:
                            st.write("**Learning & Engagement:**")
                            st.write(f"{'✅' if engagement['discovery_learning_completed'] else '❌'} Discovery Video")
                            st.write(f"{'✅' if engagement['learn_recommendation_completed'] else '❌'} Learn Recommendations")
                            st.write(f"{'✅' if engagement['senior_trivia_played'] else '❌'} Senior Trivia")
                            st.write(f"{'✅' if engagement['additional_services_viewed'] else '❌'} Additional Services")
                    
                    if lead['quality']['issues']:
                        st.write("**⚠️ Issues:**")
                        for issue in lead['quality']['issues']:
                            st.write(f"  • {issue}")
                    
                    # Show key data
                    profile = lead['data'].get('profile', {})
                    if profile.get('name'):
                        st.write(f"**Name:** {profile['name']}")
                    if profile.get('location'):
                        st.write(f"**Location:** {profile['location']}")
                    
                    mcip = lead['data'].get('mcip_contracts', {})
                    if mcip.get('care_recommendation'):
                        rec = mcip['care_recommendation']
                        st.write(f"**Care Rec:** {rec.get('tier', 'N/A')}")
                
                with col2:
                    # Engagement score
                    st.metric("Engagement", f"{engagement_count}/8", 
                             help="Number of completed activities out of 8 possible")
                    
                    if st.button(f"🗑️ Delete", key=f"delete_{lead['uid']}", type="secondary"):
                        delete_single_lead(lead['path'])
                        st.rerun()
    else:
        st.info("No leads match the current filters.")


def purge_leads_by_quality(min_grade, leads):
    """Purge leads with a specific quality grade"""
    # Delete leads that match the specified grade
    to_delete = [l for l in leads if l['quality']['grade'] == min_grade]
    
    deleted_count = 0
    for lead in to_delete:
        try:
            os.remove(lead['path'])
            deleted_count += 1
        except Exception as e:
            st.error(f"Failed to delete {lead['file']}: {e}")
    
    return deleted_count


def purge_old_leads(max_age_days, leads):
    """Purge leads older than specified days"""
    cutoff_time = datetime.now() - timedelta(days=max_age_days)
    to_delete = [l for l in leads if l['modified'] < cutoff_time]
    
    deleted_count = 0
    for lead in to_delete:
        try:
            os.remove(lead['path'])
            deleted_count += 1
        except Exception as e:
            st.error(f"Failed to delete {lead['file']}: {e}")
    
    return deleted_count


def purge_minimal_leads(leads):
    """Purge leads with minimal data (no name, no engagement)"""
    to_delete = []
    for lead in leads:
        profile = lead['data'].get('profile', {})
        mcip = lead['data'].get('mcip_contracts', {})
        progress = lead['data'].get('progress', {})
        
        has_name = bool(profile.get('name'))
        has_engagement = bool(mcip or progress or lead['data'].get('cost'))
        
        if not has_name and not has_engagement:
            to_delete.append(lead)
    
    deleted_count = 0
    for lead in to_delete:
        try:
            os.remove(lead['path'])
            deleted_count += 1
        except Exception as e:
            st.error(f"Failed to delete {lead['file']}: {e}")
    
    return deleted_count


def purge_no_engagement_leads(leads):
    """Purge leads with no engagement activities"""
    to_delete = [l for l in leads if len(l['quality']['engagement_activities']) == 0]
    
    deleted_count = 0
    for lead in to_delete:
        try:
            os.remove(lead['path'])
            deleted_count += 1
        except Exception as e:
            st.error(f"Failed to delete {lead['file']}: {e}")
    
    return deleted_count


def delete_single_lead(file_path):
    """Delete a single lead file"""
    try:
        os.remove(file_path)
        st.success(f"Deleted {Path(file_path).name}")
    except Exception as e:
        st.error(f"Failed to delete file: {e}")


if __name__ == "__main__":
    show_lead_management()