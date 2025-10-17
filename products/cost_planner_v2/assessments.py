"""
Financial Assessment Hub for Cost Planner v2

JSON-driven assessment hub that loads and displays financial assessments
as a card grid, similar to Senior Trivia module hub pattern.

Pattern: Follows products/senior_trivia/product.py architecture
Configuration: Loads assessments from JSON files
State Management: Tracks completion status and progress
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

from core.assessment_engine import run_assessment
from core.events import log_event


def render_assessment_hub(product_key: str = "cost_planner_v2") -> None:
    """
    Render the assessment selection hub.
    
    Displays available financial assessments as a card grid with:
    - Assessment title and description
    - Estimated completion time
    - Progress indicator
    - Conditional visibility based on flags
    
    Args:
        product_key: Product key for state management
    """
    
    # Check if a specific assessment is selected
    current_assessment = st.session_state.get(f"{product_key}_current_assessment")
    
    if current_assessment:
        # Run the selected assessment
        _render_assessment(current_assessment, product_key)
    else:
        # Show assessment hub
        _render_hub_view(product_key)


def _render_hub_view(product_key: str) -> None:
    """Render the hub view with assessment cards."""
    
    # Load all assessment configs
    assessments = _load_all_assessments(product_key)
    
    if not assessments:
        st.error("⚠️ No assessments found. Please check configuration.")
        return
    
    # Hub header
    st.markdown("## Financial Assessments")
    st.markdown("Complete these assessments to build your financial profile for care planning.")
    st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
    
    # Calculate overall progress
    total_assessments = len(assessments)
    completed_assessments = sum(1 for a in assessments if _is_assessment_complete(a["key"], product_key))
    overall_progress = int((completed_assessments / total_assessments) * 100) if total_assessments > 0 else 0
    
    # Progress bar
    st.markdown(f"**Progress:** {completed_assessments} of {total_assessments} assessments completed")
    st.progress(overall_progress / 100.0)
    st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
    
    # 🚀 BIG EXPERT REVIEW BUTTON (ALWAYS VISIBLE)
    st.markdown("### 🚀 Ready to See Your Financial Analysis?")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("**GO TO EXPERT REVIEW NOW →**", type="primary", use_container_width=True, key="goto_expert_review_top"):
            st.session_state.cost_v2_step = "expert_review"
            st.rerun()
    
    st.markdown("<div style='margin: 32px 0;'></div>", unsafe_allow_html=True)
    
    # Render assessment cards in grid
    _render_assessment_grid(assessments, product_key)


def _render_assessment_grid(assessments: List[Dict[str, Any]], product_key: str) -> None:
    """Render assessment cards in a responsive grid."""
    
    # Get user flags for conditional visibility
    flags = st.session_state.get("flags", {})
    
    # Filter assessments based on visibility rules
    visible_assessments = []
    for assessment in assessments:
        if _is_assessment_visible(assessment, flags):
            visible_assessments.append(assessment)
    
    if not visible_assessments:
        st.info("No assessments available based on your profile.")
        return
    
    # Render in 2-column grid
    num_cols = 2
    cols = st.columns(num_cols)
    
    for idx, assessment in enumerate(visible_assessments):
        col_index = idx % num_cols
        
        with cols[col_index]:
            _render_assessment_card(assessment, product_key)
    
    # 🚀 BOTTOM EXPERT REVIEW BUTTON (ALWAYS VISIBLE)
    st.markdown("<div style='margin: 32px 0;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🔬 Skip to Expert Review")
    st.markdown("*View your financial analysis even if assessments aren't complete*")
    if st.button("🚀 GO TO EXPERT REVIEW (BYPASS) →", type="secondary", use_container_width=True, key="goto_expert_review_bottom"):
        st.session_state.cost_v2_step = "expert_review"
        st.rerun()


def _render_assessment_card(assessment: Dict[str, Any], product_key: str) -> None:
    """Render a single assessment card."""
    
    key = assessment.get("key", "unknown")
    title = assessment.get("title", "Assessment")
    icon = assessment.get("icon", "📊")
    description = assessment.get("description", "")
    estimated_time = assessment.get("estimated_time", "")
    required = assessment.get("required", False)
    
    # Get completion status
    is_complete = _is_assessment_complete(key, product_key)
    progress_pct = _get_assessment_progress(key, product_key)
    
    # Status badge
    if is_complete:
        status_badge = "✅ Complete"
        status_color = "#22c55e"
    elif progress_pct > 0:
        status_badge = f"🔄 {progress_pct}% Done"
        status_color = "#f59e0b"
    else:
        status_badge = "⚪ Not Started"
        status_color = "#94a3b8"
    
    # Required badge
    required_badge = "🔴 Required" if required else ""
    
    # Card HTML
    st.markdown(f"""
    <div style="
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        cursor: pointer;
        transition: all 0.2s;
    ">
        <div style="display: flex; align-items: center; margin-bottom: 12px;">
            <div style="font-size: 32px; margin-right: 12px;">{icon}</div>
            <div style="flex: 1;">
                <div style="font-size: 18px; font-weight: 600; color: #1e293b; margin-bottom: 4px;">
                    {title}
                </div>
                <div style="font-size: 12px; color: {status_color}; font-weight: 600;">
                    {status_badge} {required_badge}
                </div>
            </div>
        </div>
        <div style="font-size: 14px; color: #64748b; margin-bottom: 12px; line-height: 1.5;">
            {description}
        </div>
        <div style="font-size: 12px; color: #94a3b8;">
            ⏱️ {estimated_time}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Button to start/resume assessment
    button_label = "Resume" if progress_pct > 0 and not is_complete else ("Review" if is_complete else "Start")
    
    if st.button(
        f"{button_label} →",
        key=f"start_{key}",
        use_container_width=True,
        type="primary" if required and not is_complete else "secondary"
    ):
        # Set current assessment
        st.session_state[f"{product_key}_current_assessment"] = key
        
        # Log event
        log_event("assessment.started", {
            "product": product_key,
            "assessment": key,
            "is_resume": progress_pct > 0
        })
        
        st.rerun()


def _render_assessment(assessment_key: str, product_key: str) -> None:
    """Render a specific assessment using the assessment engine."""
    
    # Load assessment config
    assessment_config = _load_assessment_config(assessment_key, product_key)
    
    if not assessment_config:
        st.error(f"⚠️ Assessment '{assessment_key}' not found.")
        if st.button("← Back to Hub"):
            st.session_state[f"{product_key}_current_assessment"] = None
            st.rerun()
        return
    
    # Run assessment engine
    run_assessment(
        assessment_key=assessment_key,
        assessment_config=assessment_config,
        product_key=product_key
    )


def render_assessment_page(assessment_key: str, product_key: str = "cost_planner_v2") -> None:
    """
    Render a full assessment page with all sections visible at once.
    
    This replaces the hub-based multi-step pattern with a single scrollable page
    showing intro, all field sections, and calculated results together.
    
    Args:
        assessment_key: Assessment to render (e.g., 'income', 'assets')
        product_key: Product key for state management
    """
    
    # Load assessment config
    assessment_config = _load_assessment_config(assessment_key, product_key)
    
    if not assessment_config:
        st.error(f"⚠️ Assessment '{assessment_key}' not found.")
        return
    
    # Initialize state
    state_key = f"{product_key}_{assessment_key}"
    st.session_state.setdefault(state_key, {})
    state = st.session_state[state_key]
    
    # Get assessment metadata
    title = assessment_config.get("title", "Assessment")
    icon = assessment_config.get("icon", "📊")
    description = assessment_config.get("description", "")
    
    # Header
    st.markdown(f"# {icon} {title}")
    st.markdown(f"*{description}*")
    st.markdown("---")
    
    # Get sections
    sections = assessment_config.get("sections", [])
    field_sections = [s for s in sections if s.get("type") == "fields"]
    
    # Render intro if exists
    intro_sections = [s for s in sections if s.get("type") == "intro"]
    if intro_sections:
        intro = intro_sections[0]
        if intro.get("help_text"):
            st.markdown(intro["help_text"])
        
        # Render intro info boxes
        for info_box in intro.get("info_boxes", []):
            _render_single_info_box(info_box)
        
        st.markdown("---")
    
    # Render all field sections at once
    for idx, section in enumerate(field_sections):
        section_title = section.get("title", f"Section {idx + 1}")
        section_icon = section.get("icon", "📝")
        
        st.markdown(f"### {section_icon} {section_title}")
        
        # Render fields for this section
        new_values = _render_fields_for_page(section, state)
        if new_values:
            state.update(new_values)
            
            # Save to tiles for persistence
            tiles = st.session_state.setdefault("tiles", {})
            product_tiles = tiles.setdefault(product_key, {})
            assessments_state = product_tiles.setdefault("assessments", {})
            assessments_state[assessment_key] = state.copy()
        
        # Render section info boxes
        for info_box in section.get("info_boxes", []):
            _render_single_info_box(info_box)
        
        # Add spacing between sections
        st.markdown("<div style='margin: 32px 0;'></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Calculate and show results if formula exists
    results_sections = [s for s in sections if s.get("type") == "results"]
    if results_sections:
        results = results_sections[0]
        calculation = results.get("calculation")
        
        if calculation:
            calc_type = calculation.get("type")
            
            if calc_type == "sum":
                # Calculate sum
                field_keys = calculation.get("fields", [])
                total = 0
                for field_key in field_keys:
                    value = state.get(field_key, 0)
                    if isinstance(value, (int, float)):
                        total += value
                
                # Format result
                result_format = calculation.get("format", "currency")
                if result_format == "currency":
                    formatted = f"${total:,.0f}"
                elif result_format == "currency_monthly":
                    formatted = f"${total:,.0f}/month"
                else:
                    formatted = str(total)
                
                # Display result
                result_label = calculation.get("label", "Total")
                st.success(f"**{result_label}:** {formatted}")
    
    # Mark as complete
    state["status"] = "done"
    
    # Render navigation at bottom
    _render_page_navigation(assessment_key, product_key, assessment_config)


def _load_all_assessments(product_key: str) -> List[Dict[str, Any]]:
    """Load all assessment configurations."""
    
    # Load from modules/assessments/ directory (colocation with product code)
    assessments_dir = Path(__file__).parent / "modules" / "assessments"
    
    if not assessments_dir.exists():
        return []
    
    assessments = []
    
    # Load each JSON file
    for json_file in sorted(assessments_dir.glob("*.json")):
        try:
            with open(json_file, 'r') as f:
                config = json.load(f)
                assessments.append(config)
        except Exception as e:
            st.error(f"Error loading {json_file.name}: {e}")
    
    # Sort by sort_order if specified
    assessments.sort(key=lambda a: a.get("sort_order", 999))
    
    return assessments


def _load_assessment_config(assessment_key: str, product_key: str) -> Optional[Dict[str, Any]]:
    """Load a specific assessment configuration."""
    
    # Load from modules/assessments/ directory (colocation with product code)
    config_path = Path(__file__).parent / "modules" / "assessments" / f"{assessment_key}.json"
    
    if not config_path.exists():
        return None
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading assessment config: {e}")
        return None


def _is_assessment_visible(assessment: Dict[str, Any], flags: Dict[str, Any]) -> bool:
    """Check if assessment should be visible based on flags."""
    
    visible_if = assessment.get("visible_if")
    if not visible_if:
        return True
    
    # Check flag condition
    flag_key = visible_if.get("flag")
    if not flag_key:
        return True
    
    flag_value = flags.get(flag_key, False)
    expected = visible_if.get("equals", True)
    
    return flag_value == expected


def _is_assessment_complete(assessment_key: str, product_key: str) -> bool:
    """Check if an assessment is complete."""
    
    state_key = f"{product_key}_{assessment_key}"
    state = st.session_state.get(state_key, {})
    
    return state.get("status") == "done"


def _get_assessment_progress(assessment_key: str, product_key: str) -> int:
    """Get assessment progress percentage."""
    
    state_key = f"{product_key}_{assessment_key}"
    state = st.session_state.get(state_key, {})
    
    # Load config to count sections
    config = _load_assessment_config(assessment_key, product_key)
    if not config:
        return 0
    
    sections = config.get("sections", [])
    current_section = st.session_state.get(f"{state_key}._section", 0)
    
    # Calculate progress
    if len(sections) == 0:
        return 0
    
    progress = int((current_section / len(sections)) * 100)
    return min(progress, 100)


def _render_fields_for_page(section: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Render fields for a section in page mode (all fields visible at once).
    Returns dict of updated field values.
    """
    from core.assessment_engine import _render_single_field, _check_field_visibility
    
    fields = section.get("fields", [])
    if not fields:
        st.info("No fields defined for this section.")
        return {}
    
    new_values = {}
    flags = st.session_state.get("flags", {})
    
    # Handle two-column layout if specified
    layout = section.get("layout", "single")
    
    if layout == "two_column":
        col1, col2 = st.columns(2)
        for idx, field in enumerate(fields):
            # Check visibility
            if not _check_field_visibility(field, state, flags):
                continue
            
            # Alternate columns
            with (col1 if idx % 2 == 0 else col2):
                value = _render_single_field(field, state)
                if value is not None:
                    new_values[field["key"]] = value
    else:
        # Single column
        for field in fields:
            # Check visibility
            if not _check_field_visibility(field, state, flags):
                continue
            
            value = _render_single_field(field, state)
            if value is not None:
                new_values[field["key"]] = value
    
    return new_values


def _render_single_info_box(info_box: Dict[str, Any]) -> None:
    """Render a single info box."""
    variant = info_box.get("variant", "info")
    message = info_box.get("message", "")
    
    # Map variants to Streamlit methods
    if variant == "success":
        st.success(message)
    elif variant == "warning":
        st.warning(message)
    elif variant == "error":
        st.error(message)
    else:
        st.info(message)


def _render_page_navigation(assessment_key: str, product_key: str, assessment_config: Dict[str, Any]) -> None:
    """Render navigation buttons at bottom of assessment page."""
    
    # Define assessment order
    assessment_order = ["income", "assets", "health_insurance", "life_insurance", "va_benefits", "medicaid_navigation"]
    
    # Get flags for conditional assessments
    flags = st.session_state.get("flags", {})
    is_veteran = flags.get("is_veteran", False)
    medicaid_interest = flags.get("medicaid_planning_interest", False)
    
    # Filter order based on flags
    visible_order = []
    for key in assessment_order:
        if key == "va_benefits" and not is_veteran:
            continue
        if key == "medicaid_navigation" and not medicaid_interest:
            continue
        visible_order.append(key)
    
    # Find current index
    try:
        current_idx = visible_order.index(assessment_key)
    except ValueError:
        current_idx = 0
    
    # Determine previous and next
    prev_key = visible_order[current_idx - 1] if current_idx > 0 else None
    next_key = visible_order[current_idx + 1] if current_idx < len(visible_order) - 1 else None
    
    # Check if required assessments complete (income and assets)
    income_complete = _is_assessment_complete("income", product_key)
    assets_complete = _is_assessment_complete("assets", product_key)
    required_complete = income_complete and assets_complete
    
    st.markdown("---")
    st.markdown("### Navigation")
    
    # Create button layout
    if next_key:
        col1, col2, col3 = st.columns(3)
    else:
        # Last assessment - show Expert Review button
        col1, col2 = st.columns(2)
    
    # Previous button
    with col1:
        if prev_key:
            prev_config = _load_assessment_config(prev_key, product_key)
            prev_title = prev_config.get("title", "Previous") if prev_config else "Previous"
            if st.button(f"← {prev_title}", use_container_width=True):
                st.session_state.cost_v2_step = f"assessment_{prev_key}"
                st.rerun()
        else:
            # First assessment - back to intro
            if st.button("← Back to Intro", use_container_width=True):
                st.session_state.cost_v2_step = "intro"
                st.rerun()
    
    # Next button or Expert Review
    if next_key:
        with col2:
            next_config = _load_assessment_config(next_key, product_key)
            next_title = next_config.get("title", "Next") if next_config else "Next"
            
            # Disable next if current assessment is required and not complete
            is_required = assessment_config.get("required", False)
            
            if st.button(f"{next_title} →", use_container_width=True, type="primary"):
                st.session_state.cost_v2_step = f"assessment_{next_key}"
                st.rerun()
        
        # Optional: Expert Review bypass on non-last pages
        with col3:
            if required_complete:
                if st.button("🚀 Expert Review", use_container_width=True, type="secondary"):
                    st.session_state.cost_v2_step = "expert_review"
                    st.rerun()
    else:
        # Last assessment - prominent Expert Review button
        with col2:
            if required_complete:
                if st.button("🚀 Go to Expert Review →", use_container_width=True, type="primary"):
                    st.session_state.cost_v2_step = "expert_review"
                    st.rerun()
            else:
                st.warning("⚠️ Please complete Income and Assets assessments before proceeding to Expert Review")


__all__ = ["render_assessment_hub", "render_assessment_page"]
