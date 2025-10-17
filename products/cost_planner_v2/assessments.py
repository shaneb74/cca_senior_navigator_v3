"""
Financial Assessment Hub for Cost Planner v2

JSON-driven assessment hub that loads and displays financial assessments
as a card grid, similar to Senior Trivia module hub pattern.

Pattern: Follows products/senior_trivia/product.py architecture
Configuration: Loads assessments from JSON files
State Management: Tracks completion status and progress
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

from core.assessment_engine import run_assessment
from core.events import log_event
from core.session_store import safe_rerun
from core.ui import render_navi_panel_v2
from products.cost_planner_v2.utils.financial_helpers import (
    normalize_income_data,
    normalize_asset_data,
    calculate_total_monthly_income,
    calculate_total_asset_value,
    calculate_total_asset_debt,
)


_SINGLE_PAGE_ASSESSMENTS: Dict[str, Dict[str, Any]] = {
    "income": {
        "save_label": "Save Income Information",
        "success_message": "Income assessment saved.",
        "navi": {
            "title": "I'm here to help",
            "reason": "We'll review monthly income so your care plan stays realistic.",
            "encouragement": {
                "icon": "💡",
                "text": "Take your time—I'll keep track of everything you enter.",
                "status": "getting_started"
            }
        },
        "expert_requires": ["income", "assets"],
        "expert_disabled_text": "Complete the Assets assessment to unlock Expert Review."
    },
    "assets": {
        "save_label": "Save Asset Information",
        "success_message": "Assets assessment saved.",
        "navi": {
            "title": "You're doing great",
            "reason": "Capture assets and obligations so we can map out funding options.",
            "encouragement": {
                "icon": "🧭",
                "text": "List only what matters—clarity beats perfection here.",
                "status": "getting_started"
            }
        },
        "expert_requires": ["income", "assets"],
        "expert_disabled_text": "Complete the Income assessment to unlock Expert Review."
    }
}


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
        # Set current assessment to trigger the assessment engine
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
    
    # Use single-page layout for designated assessments (e.g., income, assets)
    if assessment_key in _SINGLE_PAGE_ASSESSMENTS:
        _render_single_page_assessment(
            assessment_key=assessment_key,
            assessment_config=assessment_config,
            product_key=product_key,
            settings=_SINGLE_PAGE_ASSESSMENTS[assessment_key]
        )
        return
    
    # Run assessment engine (original multi-step flow)
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
    
    # Compact header with container
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        color: white;
    ">
        <h1 style="margin: 0; font-size: 28px;">{icon} {title}</h1>
        <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 14px;">{description}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get sections
    sections = assessment_config.get("sections", [])
    
    # Separate sections by type
    intro_sections = [s for s in sections if s.get("type") == "intro"]
    results_sections = [s for s in sections if s.get("type") == "results"]
    # Field sections are those that have fields but aren't intro/results
    field_sections = [s for s in sections if s.get("fields") and s.get("type") not in ["intro", "results"]]
    
    # Compact intro (help text only, no big info boxes at top)
    if intro_sections:
        intro = intro_sections[0]
        if intro.get("help_text"):
            st.info(f"💡 {intro['help_text']}")
    
    # Render all field sections in an expander for cleaner look
    for idx, section in enumerate(field_sections):
        section_title = section.get("title", f"Section {idx + 1}")
        section_icon = section.get("icon", "📝")
        
        # Use expander for each section (collapsed by default except first)
        with st.expander(f"{section_icon} {section_title}", expanded=(idx == 0)):
            # Render fields for this section
            new_values = _render_fields_for_page(section, state)
            if new_values:
                state.update(new_values)
                
                # Save to tiles for persistence
                tiles = st.session_state.setdefault("tiles", {})
                product_tiles = tiles.setdefault(product_key, {})
                assessments_state = product_tiles.setdefault("assessments", {})
                assessments_state[assessment_key] = state.copy()
            
            # Render section info boxes (compact, at bottom of expander)
            for info_box in section.get("info_boxes", []):
                _render_single_info_box(info_box)
    
    
    # Calculate and show results if formula exists (compact summary at top)
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
                
                # Display result in a nice card at the top
                result_label = calculation.get("label", "Total")
                st.markdown(f"""
                <div style="
                    background: #f0fdf4;
                    border-left: 4px solid #22c55e;
                    padding: 16px 20px;
                    border-radius: 8px;
                    margin: 24px 0;
                ">
                    <div style="font-size: 14px; color: #166534; font-weight: 600; margin-bottom: 4px;">
                        {result_label}
                    </div>
                    <div style="font-size: 28px; color: #15803d; font-weight: 700;">
                        {formatted}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Mark as complete
    state["status"] = "done"
    
    # Compact navigation at bottom
    st.markdown("<div style='margin: 32px 0;'></div>", unsafe_allow_html=True)
    _render_page_navigation(assessment_key, product_key, assessment_config)


def _render_single_page_assessment(
    assessment_key: str,
    assessment_config: Dict[str, Any],
    product_key: str,
    settings: Dict[str, Any]
) -> None:
    """Render designated assessments on a single page with streamlined styling."""
    
    state_key = f"{product_key}_{assessment_key}"
    state = st.session_state.setdefault(state_key, {})
    
    success_flash_key = f"{state_key}._flash_success"
    error_flash_key = f"{state_key}._flash_error"
    
    success_flash = st.session_state.pop(success_flash_key, None)
    error_flash = st.session_state.pop(error_flash_key, None)
    
    # Ensure derived fields are populated even on initial load
    _persist_assessment_state(product_key, assessment_key, state)
    
    st.markdown('<div class="sn-app module-container">', unsafe_allow_html=True)
    
    navi = settings.get("navi")
    if navi:
        nav_cols = st.columns([1, 2, 1])
        with nav_cols[1]:
            encouragement = navi.get("encouragement", {})
            render_navi_panel_v2(
                title=navi.get("title", ""),
                reason=navi.get("reason", ""),
                encouragement={
                    "icon": encouragement.get("icon", "💡"),
                    "text": encouragement.get("text", ""),
                    "status": encouragement.get("status", "getting_started")
                },
                context_chips=navi.get("context_chips", []),
                primary_action={"label": "", "action": None},
                variant="module"
            )
        st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
    
    title = assessment_config.get("title", "Assessment")
    icon = assessment_config.get("icon", "📋")
    description = assessment_config.get("description", "")
    
    st.markdown(
        f"""
        <div style="display:flex; flex-direction:column; gap:10px; text-align:left;">
            <div style="font-size:30px; font-weight:700; color:#0f172a;">{icon} {title}</div>
            <div style="font-size:15px; color:#475569; line-height:1.6;">{description}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if success_flash:
        st.success(success_flash)
    if error_flash:
        st.warning(error_flash)
    
    sections = assessment_config.get("sections", [])
    field_sections = [
        s for s in sections if s.get("fields") and s.get("type") not in ["intro", "results"]
    ]
    
    intro_section = next((s for s in sections if s.get("type") == "intro"), None)
    if intro_section and intro_section.get("help_text"):
        st.markdown(
            f"<div style='font-size:14px; color:#475569; margin: 12px 0 24px 0;'>{intro_section.get('help_text')}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown("<div style='margin: 12px 0 24px 0;'></div>", unsafe_allow_html=True)
    
    if field_sections:
        for row_index in range(0, len(field_sections), 2):
            row_sections = field_sections[row_index:row_index + 2]
            row_cols = st.columns(2, gap="large")
            for col_index in range(2):
                if col_index < len(row_sections):
                    section = row_sections[col_index]
                    with row_cols[col_index]:
                        _render_section_content(section, state, product_key, assessment_key)
                else:
                    with row_cols[col_index]:
                        st.write("")
            if row_index + 2 < len(field_sections):
                st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
    else:
        st.write("No sections configured.")
    
    summary_config = assessment_config.get("summary", {})
    summary_value = _calculate_summary_total(summary_config, state)
    
    if summary_config and summary_value is not None:
        label = summary_config.get("label", "Summary")
        display_format = summary_config.get("display_format", "${:,.0f}")
        try:
            formatted_total = display_format.format(summary_value)
        except Exception:
            formatted_total = f"${summary_value:,.0f}"
        
        st.markdown(
            f"""
            <div style="
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 18px 20px;
                margin: 28px 0 8px 0;
                background: #ffffff;
            ">
                <div style="font-size:12px; font-weight:600; color:#475569; letter-spacing:0.04em; text-transform:uppercase;">
                    {label}
                </div>
                <div style="font-size:28px; font-weight:700; color:#0f172a; margin-top:6px;">
                    {formatted_total}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown("<div style='margin:28px 0 8px 0;'></div>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 32px 0 16px 0;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    back_label = settings.get("back_label", "← Back to Assessments")
    save_label = settings.get("save_label", "Save")
    success_message = settings.get("success_message", "Details saved.")
    expert_requires = settings.get("expert_requires", [])
    expert_disabled_text = settings.get("expert_disabled_text")
    expert_button_label = settings.get("expert_button_label", "🚀 Expert Review →")
    
    with col1:
        if st.button(back_label, type="secondary", use_container_width=True, key=f"{assessment_key}_back"):
            st.session_state.pop(f"{product_key}_current_assessment", None)
            st.session_state.cost_v2_step = "assessments"
            safe_rerun()
    
    with col2:
        if st.button(save_label, type="primary", use_container_width=True, key=f"{assessment_key}_save"):
            missing_fields = _get_missing_required_fields(field_sections, state)
            if missing_fields:
                st.session_state[error_flash_key] = "Please complete required fields: " + ", ".join(missing_fields)
            else:
                previously_done = state.get("status") == "done"
                state["status"] = "done"
                state["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                _persist_assessment_state(product_key, assessment_key, state)
                st.session_state[success_flash_key] = success_message
                
                event_payload = {
                    "product": product_key,
                    "assessment": assessment_key,
                    "mode": "single_page"
                }
                summary_value_for_event = _calculate_summary_total(summary_config, state)
                if summary_config and summary_value_for_event is not None:
                    event_payload["calculated_summary"] = summary_value_for_event
                
                if previously_done:
                    log_event("assessment.updated", event_payload)
                else:
                    log_event("assessment.completed", event_payload)
            safe_rerun()
    
    with col3:
        def _is_complete(target_key: str) -> bool:
            if target_key == assessment_key:
                return state.get("status") == "done"
            return _is_assessment_complete(target_key, product_key)
        
        expert_ready = all(_is_complete(target) for target in expert_requires) if expert_requires else True
        
        if expert_ready:
            if st.button(expert_button_label, type="secondary", use_container_width=True, key=f"{assessment_key}_expert"):
                st.session_state.cost_v2_step = "expert_review"
                st.session_state.pop(f"{product_key}_current_assessment", None)
                safe_rerun()
        else:
            if expert_disabled_text:
                st.markdown(
                    f"""
                    <div style="
                        background:#f8fafc;
                        border:1px dashed #cbd5f5;
                        border-radius:8px;
                        padding:12px;
                        font-size:13px;
                        color:#64748b;
                        text-align:center;
                    ">
                        {expert_disabled_text}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    st.markdown('</div>', unsafe_allow_html=True)


def _render_section_content(
    section: Dict[str, Any],
    state: Dict[str, Any],
    product_key: str,
    assessment_key: str
) -> None:
    """Render a section's heading and fields inside a single column."""
    
    section_icon = section.get("icon", "📝")
    section_title = section.get("title", "Section")
    help_text = section.get("help_text")
    
    st.markdown(
        f"""
        <div style="display:flex; flex-direction:column; gap:6px; margin-bottom:12px;">
            <div style="font-size:20px; font-weight:600; color:#0f172a;">{section_icon} {section_title}</div>
            {f"<div style='font-size:14px; color:#475569;'>{help_text}</div>" if help_text else ""}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    new_values = _render_fields_for_page(section, state)
    if new_values:
        state.update(new_values)
        _persist_assessment_state(product_key, assessment_key, state)
    
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)


def _persist_assessment_state(product_key: str, assessment_key: str, state: Dict[str, Any]) -> None:
    """Persist assessment state into session tiles and module registry."""
    augmented_state = _augment_assessment_state(assessment_key, state)
    
    # Persist to tiles (used by financial profile builder)
    tiles = st.session_state.setdefault("tiles", {})
    product_tiles = tiles.setdefault(product_key, {})
    assessments_state = product_tiles.setdefault("assessments", {})
    assessments_state[assessment_key] = augmented_state.copy()
    
    # Update module registry for backward compatibility with hub metrics
    modules = st.session_state.setdefault("cost_v2_modules", {})
    module_entry = modules.setdefault(assessment_key, {
        "status": "in_progress",
        "progress": 0,
        "data": {}
    })
    module_entry["data"] = augmented_state.copy()
    
    if augmented_state.get("status") == "done":
        module_entry["status"] = "completed"
        module_entry["progress"] = 100
    else:
        if module_entry.get("status") != "completed":
            module_entry["status"] = module_entry.get("status", "in_progress") or "in_progress"
            module_entry.setdefault("progress", 0)


def _augment_assessment_state(assessment_key: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Augment raw assessment state with normalized values and summaries."""
    base_state = dict(state or {})
    
    if assessment_key == "income":
        normalized = normalize_income_data(base_state)
        # Ensure total is up to date (normalize already calculates but recalc for certainty)
        normalized["total_monthly_income"] = calculate_total_monthly_income(normalized)
        return normalized
    
    if assessment_key == "assets":
        normalized = normalize_asset_data(base_state)
        normalized["total_asset_value"] = calculate_total_asset_value(normalized)
        normalized["total_asset_debt"] = calculate_total_asset_debt(normalized)
        normalized["net_asset_value"] = max(
            normalized["total_asset_value"] - normalized["total_asset_debt"],
            0.0
        )
        return normalized
    
    return base_state


def _calculate_summary_total(summary_config: Dict[str, Any], state: Dict[str, Any]) -> Optional[float]:
    """Calculate summary total using the formula defined in config."""
    if not summary_config:
        return None
    
    formula = summary_config.get("formula")
    if not formula:
        return None
    
    try:
        if formula.startswith("sum(") and formula.endswith(")"):
            field_names = [f.strip() for f in formula[4:-1].split(",") if f.strip()]
            total = 0.0
            for field_name in field_names:
                value = state.get(field_name)
                if isinstance(value, (int, float)):
                    total += float(value)
                elif isinstance(value, str) and value.strip():
                    try:
                        total += float(value)
                    except ValueError:
                        continue
            return total
        
        return float(eval(formula, {"__builtins__": {}}, state))
    except Exception:
        return None


def _get_missing_required_fields(sections: List[Dict[str, Any]], state: Dict[str, Any]) -> List[str]:
    """Return labels for required fields that have not been completed."""
    from core.assessment_engine import _is_field_visible  # Local import to avoid circularity
    
    missing: List[str] = []
    for section in sections:
        for field in section.get("fields", []):
            if not field.get("required"):
                continue
            if not _is_field_visible(field, state):
                continue
            
            key = field.get("key")
            value = state.get(key)
            if value in (None, "", []):
                missing.append(field.get("label", key))
    
    return missing


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
    from core.assessment_engine import _render_fields
    
    # Just use the existing _render_fields function from assessment_engine
    return _render_fields(section, state)


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
    
    # Check if required assessments complete (income and assets)
    income_complete = _is_assessment_complete("income", product_key)
    assets_complete = _is_assessment_complete("assets", product_key)
    required_complete = income_complete and assets_complete
    
    # Compact navigation
    col1, col2 = st.columns(2)
    
    # Back to Hub button
    with col1:
        if st.button("← Back to Assessments", use_container_width=True, type="secondary"):
            st.session_state.cost_v2_step = "assessments"
            st.rerun()
    
    # Expert Review button
    with col2:
        if required_complete:
            if st.button("🚀 Expert Review →", use_container_width=True, type="primary"):
                st.session_state.cost_v2_step = "expert_review"
                st.rerun()
        else:
            # Disabled state with tooltip
            st.markdown("""
            <div style="
                background: #fef3c7;
                border: 1px solid #fbbf24;
                border-radius: 6px;
                padding: 12px;
                text-align: center;
                font-size: 14px;
                color: #92400e;
            ">
                ⚠️ Complete Income & Assets first
            </div>
            """, unsafe_allow_html=True)


__all__ = ["render_assessment_hub", "render_assessment_page"]
