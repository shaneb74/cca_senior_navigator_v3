"""
GCP Assessment Review Page

Displays a read-only view of the user's completed GCP assessment responses
and shows how the care recommendation was calculated.

Features:
- Shows all assessment responses organized by section
- Displays score breakdown by category
- Collapsible confidence score explanation
- Read-only (no editing capability)
- Link back to Concierge Hub

Route: ?page=gcp_review
"""

import streamlit as st

from core.mcip import MCIP


def render():
    """Render the GCP Assessment Review page."""

    # Get care recommendation from MCIP
    recommendation = MCIP.get_care_recommendation()

    if not recommendation or not recommendation.tier:
        # No completed assessment found
        st.warning("⚠️ No completed assessment found. You haven't completed the Guided Care Plan yet.")
        if st.button("← Back to Concierge", key="gcp_review_back_incomplete"):
            st.query_params["page"] = "hub_concierge"
            st.rerun()
        return

    # Check if we have the assessment data
    assessment_data = st.session_state.get("gcp_care_recommendation", {})

    # Render with header
    from ui.product_shell import product_shell_end, product_shell_start

    product_shell_start()

    # Render succinct Navi-style guidance at top
    _render_navi_guidance(recommendation)

    # Render main content
    _render_review_content(recommendation, assessment_data)

    product_shell_end()


def _render_navi_guidance(recommendation):
    """Render Navi-style guidance banner."""
    tier_display = {
        "no_care_needed": "No Care Needed",
        "in_home": "In-Home Care",
        "in_home_care": "In-Home Care",
        "assisted_living": "Assisted Living",
        "memory_care": "Memory Care",
        "memory_care_high_acuity": "Memory Care (High Acuity)"
    }

    tier_name = tier_display.get(recommendation.tier, recommendation.tier.replace("_", " ").title())
    confidence_pct = int(recommendation.confidence * 100)

    # Simple Navi-style banner (using string concatenation to avoid f-string issues)
    banner_html = (
        '<div style="background: #f0f9ff; border-left: 4px solid #3b82f6; border-radius: 8px; padding: 16px 20px; margin-bottom: 24px;">'
        '    <div style="display: flex; align-items: start; gap: 12px;">'
        '        <span style="font-size: 24px;">📋</span>'
        '        <div style="flex: 1;">'
        '            <div style="font-weight: 700; color: #1e40af; font-size: 16px; margin-bottom: 4px;">Your Assessment Results</div>'
        '            <div style="color: #1e3a8a; font-size: 14px; line-height: 1.5;">'
        '                Based on your responses, we recommend <strong>' + tier_name + '</strong> with ' + str(confidence_pct) + '% confidence. '
        '                This page shows how we arrived at your care recommendation.'
        '            </div>'
        '        </div>'
        '    </div>'
        '</div>'
    )
    st.markdown(banner_html, unsafe_allow_html=True)


def _render_review_content(recommendation, assessment_data):
    """Render the main review content."""

    # Title
    st.markdown("## Your Care Assessment Review")
    st.markdown("Here's your responses and how we arrived at your Care Recommendation.")

    st.markdown("---")

    # SECTION 1: Care Recommendation Summary
    _render_recommendation_summary(recommendation)

    st.markdown("---")

    # SECTION 2: Assessment Responses
    _render_assessment_responses(assessment_data)

    st.markdown("---")

    # SECTION 3: Score Breakdown (detailed)
    _render_score_breakdown(recommendation, assessment_data)

    st.markdown("---")

    # SECTION 4: Confidence Score (collapsible)
    _render_confidence_section(recommendation)

    st.markdown("---")

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back to Concierge", use_container_width=True):
            st.query_params["page"] = "hub_concierge"
            st.rerun()

    with col2:
        if st.button("💰 View Costs", type="primary", use_container_width=True):
            st.query_params["page"] = "cost_v2"
            st.rerun()

    with col3:
        if st.button("🔁 Retake Assessment", use_container_width=True):
            st.query_params["page"] = "gcp_v4"
            st.rerun()


def _render_recommendation_summary(recommendation):
    """Render the care recommendation summary at the top."""
    st.markdown("### 🎯 Your Care Recommendation")

    # Tier display names
    tier_display = {
        "no_care_needed": "No Care Needed",
        "in_home": "In-Home Care",
        "in_home_care": "In-Home Care",
        "assisted_living": "Assisted Living",
        "memory_care": "Memory Care",
        "memory_care_high_acuity": "Memory Care (High Acuity)"
    }

    tier_name = tier_display.get(recommendation.tier, recommendation.tier.replace("_", " ").title())
    score = recommendation.tier_score
    confidence_pct = int(recommendation.confidence * 100)

    # Show recommendation with visual indicator
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Care Level", tier_name)
    with col2:
        st.metric("Assessment Score", f"{score} points")
    with col3:
        st.metric("Confidence", f"{confidence_pct}%")

    # Score range context
    _render_score_range_visual(score, recommendation.tier)

    # Rationale
    if recommendation.rationale:
        st.markdown("#### Why This Recommendation?")
        for reason in recommendation.rationale:
            st.markdown(f"- {reason}")


def _render_score_range_visual(score, tier):
    """Render a visual showing where the score falls in the tier ranges."""
    st.markdown("#### Score Range Context")

    # Tier thresholds (from logic.py)
    thresholds = {
        "no_care_needed": (0, 8),
        "in_home": (9, 16),
        "assisted_living": (17, 24),
        "memory_care": (25, 39),
        "memory_care_high_acuity": (40, float('inf'))
    }

    # Get current tier range
    tier_key = tier if tier != "in_home_care" else "in_home"
    min_score, max_score = thresholds.get(tier_key, (0, 0))

    if max_score == float('inf'):
        range_text = f"{min_score}+ points"
    else:
        range_text = f"{min_score}-{max_score} points"

    st.markdown(f"""
**Your score of {score} points** falls within the **{tier.replace('_', ' ').title()}** range ({range_text}).

**All Care Level Ranges:**
- No Care Needed: 0-8 points
- In-Home Care: 9-16 points
- Assisted Living: 17-24 points
- Memory Care: 25-39 points
- Memory Care (High Acuity): 40+ points
    """)


def _render_assessment_responses(assessment_data):
    """Render the user's assessment responses organized by section."""
    st.markdown("### 📝 Your Assessment Responses")

    if not assessment_data:
        st.markdown("_Assessment response details are not available in this session._")
        return

    # Display key assessment fields in a structured way
    sections = [
        {
            "title": "👤 About You",
            "fields": {
                "Age Range": _format_value(assessment_data.get("age_range")),
                "Living Situation": _format_value(assessment_data.get("living_situation")),
            }
        },
        {
            "title": "💊 Health & Medications",
            "fields": {
                "Medical Conditions": _format_list(assessment_data.get("conditions", [])),
                "Medication Management": _format_value(assessment_data.get("medications")),
                "Falls History": _format_value(assessment_data.get("falls")),
            }
        },
        {
            "title": "🚶 Mobility & Daily Activities (ADLs)",
            "fields": {
                "Activities Needing Help": f"{assessment_data.get('adl_count', 0)} ADLs",
                "ADL Details": _format_list(assessment_data.get("adls", [])),
                "Mobility Support": _format_value(assessment_data.get("mobility")),
            }
        },
        {
            "title": "🏠 Independent Living (IADLs)",
            "fields": {
                "Tasks Needing Help": f"{assessment_data.get('iadl_count', 0)} IADLs",
                "IADL Details": _format_list(assessment_data.get("iadls", [])),
            }
        },
        {
            "title": "🧠 Memory & Cognition",
            "fields": {
                "Cognitive Decline": _format_value(assessment_data.get("cognitive_decline")),
                "Memory Concerns": _format_value(assessment_data.get("memory")),
                "Behavioral Issues": _format_bool(assessment_data.get("behavioral_issues")),
                "Wandering Risk": _format_bool(assessment_data.get("wandering_risk")),
            }
        },
        {
            "title": "👥 Support System",
            "fields": {
                "Primary Caregiver": _format_value(assessment_data.get("primary_caregiver")),
                "Caregiver Hours/Day": assessment_data.get("caregiver_hours", 0),
                "Professional Help": _format_bool(assessment_data.get("professional_help")),
                "Safety Concerns": _format_bool(assessment_data.get("safety_concerns")),
            }
        },
    ]

    # Render each section
    for section in sections:
        with st.expander(f"**{section['title']}**", expanded=True):
            for label, value in section['fields'].items():
                if value and value != "Not specified":
                    st.markdown(f"**{label}:** {value}")


def _render_score_breakdown(recommendation, assessment_data):
    """Render detailed score breakdown by category."""
    st.markdown("### 📊 Score Breakdown by Category")

    st.markdown(f"""
    Your total score of **{recommendation.tier_score} points** comes from the following categories:
    """)

    # Calculate approximate contribution by category
    # Note: This is a simplified breakdown since we don't have the exact
    # per-question scoring stored in the assessment data

    categories = []

    # ADLs contribution
    adl_count = assessment_data.get("adl_count", 0)
    if adl_count > 0:
        adl_points = min(adl_count * 2, 6)  # Approximate: 2 points per ADL, max 6
        categories.append(("Activities of Daily Living (ADLs)", adl_points, adl_count))

    # IADLs contribution
    iadl_count = assessment_data.get("iadl_count", 0)
    if iadl_count > 0:
        iadl_points = min(iadl_count * 1.5, 8)  # Approximate: 1.5 points per IADL, max 8
        categories.append(("Instrumental Activities (IADLs)", iadl_points, iadl_count))

    # Cognitive decline
    cognitive = assessment_data.get("cognitive_decline")
    if cognitive and cognitive != "none" and cognitive != False:
        if cognitive == "severe":
            cog_points = 5
        elif cognitive == "moderate":
            cog_points = 3
        elif cognitive == "occasional":
            cog_points = 1
        else:
            cog_points = 2
        categories.append(("Cognitive/Memory Concerns", cog_points, cognitive))

    # Safety and behavioral
    safety_points = 0
    if assessment_data.get("safety_concerns"):
        safety_points += 2
    if assessment_data.get("behavioral_issues"):
        safety_points += 3
    if assessment_data.get("wandering_risk"):
        safety_points += 3
    if safety_points > 0:
        categories.append(("Safety & Behavioral Concerns", safety_points, None))

    # Support system
    support_points = 0
    if assessment_data.get("primary_caregiver") == "none":
        support_points += 2
    if assessment_data.get("living_situation") == "alone":
        support_points += 1
    if support_points > 0:
        categories.append(("Support System", support_points, None))

    # Display categories
    if categories:
        for category, points, detail in categories:
            col1, col2 = st.columns([3, 1])
            with col1:
                detail_text = f" ({detail})" if detail else ""
                st.markdown(f"**{category}**{detail_text}")
            with col2:
                st.markdown(f"**+{points:.0f}** pts")
    else:
        st.markdown("_Detailed scoring breakdown is not available for this assessment._")

    st.markdown("")
    st.caption("Note: Score breakdown is approximate based on typical scoring patterns. Individual question responses may vary.")


def _render_confidence_section(recommendation):
    """Render collapsible confidence score section."""
    with st.expander("ℹ️ **Understanding Your Confidence Score**", expanded=False):
        confidence_pct = int(recommendation.confidence * 100)

        st.markdown(f"""
### Confidence Score: {confidence_pct}%

The confidence score reflects how complete and clear your assessment was.

**What affects confidence:**
- ✅ **Completeness:** How many questions were answered
- ✅ **Consistency:** How well responses align with each other
- ✅ **Clarity:** How definitive your score is within the tier range

**Confidence Levels:**
- **90-100%:** Very high confidence - clear and complete assessment
- **75-89%:** Good confidence - most key questions answered
- **60-74%:** Moderate confidence - some gaps in information
- **Below 60%:** Lower confidence - consider retaking with more detail

**Your {confidence_pct}% confidence means:**
        """)

        if confidence_pct >= 90:
            st.markdown("✅ Your assessment was very thorough and provides a clear picture of care needs.")
        elif confidence_pct >= 75:
            st.markdown("✅ Your assessment provides a good basis for care planning.")
        elif confidence_pct >= 60:
            st.markdown("⚠️ Your assessment is reasonably complete, but adding more details could improve accuracy.")
        else:
            st.markdown("⚠️ Consider retaking the assessment with more detailed responses for better accuracy.")


# Helper functions for formatting
def _format_value(value):
    """Format a single value for display."""
    if value is None or value == "":
        return "Not specified"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, str):
        return value.replace("_", " ").title()
    return str(value)


def _format_bool(value):
    """Format a boolean value."""
    if value is None:
        return "Not specified"
    return "Yes" if value else "No"


def _format_list(items):
    """Format a list of items."""
    if not items:
        return "None reported"
    if isinstance(items, list):
        formatted = [item.replace("_", " ").title() for item in items]
        return ", ".join(formatted)
    return str(items)


__all__ = ["render"]
