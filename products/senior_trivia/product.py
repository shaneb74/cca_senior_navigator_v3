"""
Senior Trivia & Brain Games Product Router

A gamified learning and engagement product for seniors in the Waiting Room.
Offers multiple trivia modules covering care knowledge, entertainment, Medicare, 
healthy habits, and family-friendly challenges.

Features:
- Points and badges for completing modules
- Instant feedback on each question
- Progress tracking across modules
- Fun, accessible, educational content
"""

import streamlit as st
from core.modules.engine import run_module
from core.modules.schema import ModuleConfig, StepDef, FieldDef
from core.navi import render_navi_panel
from ui.product_shell import product_shell_start, product_shell_end


def render():
    """Render Senior Trivia & Brain Games product.
    
    Flow:
    1. Show module selection hub
    2. User selects a trivia game
    3. Run selected module via module engine
    4. Award points and badges on completion
    5. Return to module hub or continue to next game
    """
    
    product_shell_start()
    
    try:
        # Check if a specific module is selected
        module_key = st.session_state.get("senior_trivia_current_module")
        
        if module_key:
            # Load and run the selected module
            config = _load_module_config(module_key)
            
            # Render Navi panel with module guidance
            render_navi_panel(
                location="product",
                product_key="senior_trivia",
                module_config=config
            )
            
            # Run module engine
            module_state = run_module(config)
            
            # Check if module is complete
            outcome_key = f"{config.state_key}._outcomes"
            outcome = st.session_state.get(outcome_key)
            
            if outcome:
                # Award points/badges
                _award_completion_points(module_key, outcome)
                
                # Show completion options
                _show_completion_actions()
        else:
            # Show module selection hub
            _render_module_hub()
    
    finally:
        product_shell_end()


def _render_module_hub():
    """Render the trivia module selection hub."""
    st.markdown("## 🎯 Senior Trivia & Brain Games")
    st.markdown("Choose a trivia game to play. Each game takes 3-5 minutes and earns you points and badges!")
    
    # Module cards
    modules = [
        {
            "key": "truths_myths",
            "title": "🏡 Truths & Myths about Senior Living",
            "desc": "Test your knowledge about assisted living, memory care, and financial planning",
            "time": "4 min",
            "questions": 8,
            "badge": "Myth Buster"
        },
        {
            "key": "music_trivia",
            "title": "🎵 Music & Entertainment (1950s-1980s)",
            "desc": "Classic songs, artists, TV shows, and cultural touchstones",
            "time": "5 min",
            "questions": 10,
            "badge": "Music Master"
        },
        {
            "key": "medicare_quiz",
            "title": "🏥 Medicare Enrollment Know-How",
            "desc": "Learn about enrollment periods, coverage, and common mistakes",
            "time": "4 min",
            "questions": 8,
            "badge": "Medicare Pro"
        },
        {
            "key": "healthy_habits",
            "title": "💪 Healthy Habits & Longevity",
            "desc": "Evidence-based tips for mobility, nutrition, and mental well-being",
            "time": "5 min",
            "questions": 10,
            "badge": "Wellness Champion"
        },
        {
            "key": "community_challenge",
            "title": "👨‍👩‍👧‍👦 Community Challenge / Family Trivia",
            "desc": "Play together with family! Fun questions for all generations",
            "time": "4 min",
            "questions": 8,
            "badge": "Family Fun"
        }
    ]
    
    for module in modules:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {module['title']}")
                st.markdown(module['desc'])
                st.markdown(f"⏱️ {module['time']} • {module['questions']} questions • Badge: **{module['badge']}**")
            with col2:
                if st.button("Play", key=f"play_{module['key']}", use_container_width=True):
                    st.session_state["senior_trivia_current_module"] = module['key']
                    st.rerun()
            st.markdown("---")


def _load_module_config(module_key: str) -> ModuleConfig:
    """Load module configuration for the specified trivia game.
    
    Converts trivia JSON format to ModuleConfig for module engine.
    
    Args:
        module_key: Key of the trivia module (e.g., "truths_myths")
    
    Returns:
        ModuleConfig object for module engine
    """
    from pathlib import Path
    import json
    
    module_path = Path(__file__).parent / "modules" / f"{module_key}.json"
    
    with open(module_path, "r") as f:
        data = json.load(f)
    
    module_meta = data.get("module", {})
    sections = data.get("sections", [])
    
    # Convert sections to steps
    steps = []
    for section in sections:
        step = _convert_section_to_step(section)
        if step:
            steps.append(step)
    
    return ModuleConfig(
        product="senior_trivia",
        version=module_meta.get("version", "v2025.10"),
        steps=steps,
        state_key=f"trivia_{module_meta.get('id', module_key)}",
        outcomes_compute=None,  # Trivia scores computed inline
        results_step_id=module_meta.get("results_step_id", "results"),
    )


def _convert_section_to_step(section: dict) -> StepDef:
    """Convert a trivia JSON section to a StepDef.
    
    Args:
        section: Section dict from trivia JSON
    
    Returns:
        StepDef object for module engine
    """
    section_type = section.get("type", "questions")
    section_id = section["id"]
    title = section.get("title", "")
    description = section.get("description", "")
    
    # Handle info sections (intro pages)
    if section_type == "info":
        return StepDef(
            id=section_id,
            title=title,
            subtitle=description,
            icon=None,
            fields=[],
            content=section.get("content"),
            next_label="Start Quiz" if section_id == "intro" else "Continue",
            skip_label=None,
            show_progress=False,
            show_bottom_bar=True,
            summary_keys=None,
        )
    
    # Handle results section
    if section_type == "results":
        return StepDef(
            id=section_id,
            title=title,
            subtitle=description,
            icon="🎯",
            fields=[],
            next_label="Continue",
            skip_label=None,
            show_progress=True,
            show_bottom_bar=True,
            summary_keys=None,
        )
    
    # Handle question sections
    questions = section.get("questions", [])
    fields = [_convert_question_to_field(q) for q in questions]
    
    return StepDef(
        id=section_id,
        title=title,
        subtitle=description,
        icon=None,
        fields=fields,
        next_label="Continue",
        skip_label=None,
        show_progress=True,
        show_bottom_bar=True,
        summary_keys=None,
    )


def _convert_question_to_field(question: dict) -> FieldDef:
    """Convert a trivia question to a FieldDef.
    
    Args:
        question: Question dict from trivia JSON
    
    Returns:
        FieldDef object for module engine
    """
    question_id = question["id"]
    question_type = question.get("type", "string")
    select_type = question.get("select", "single")
    ui_config = question.get("ui", {})
    
    return FieldDef(
        key=question_id,
        label=question.get("label", ""),
        type=_convert_type(question_type, select_type, ui_config),
        help=question.get("help"),
        required=question.get("required", False),
        options=question.get("options", []),
        min=question.get("min"),
        max=question.get("max"),
        step=question.get("step"),
        placeholder=question.get("placeholder"),
        default=question.get("default"),
        visible_if=None,
        write_key=None,
        a11y_hint=None,
        prefill_from=None,
        ask_if_missing=False,
        ui=ui_config,
        effects=[],
    )


def _convert_type(question_type: str, select_type: str, ui: dict = None) -> str:
    """Convert trivia type to FieldDef type.
    
    Args:
        question_type: Type from JSON ("string", "number", etc.)
        select_type: Select type ("single", "multi")
        ui: UI configuration dict with widget preference
    
    Returns:
        FieldDef type string matching component renderer names
    """
    widget = (ui or {}).get("widget", "")
    
    # Single-select types - use chip widget for trivia
    if question_type == "string" and select_type == "single":
        if widget == "chip":
            return "pill"  # Chip widget uses pill renderer
        elif widget == "dropdown":
            return "dropdown"
        else:
            return "radio"
    
    # Multi-select types
    elif question_type == "string" and select_type == "multi":
        if widget == "multi_chip":
            return "chip_multi"
        return "multiselect"
    
    # Number types
    elif question_type == "number":
        return "number"
    
    # Boolean types
    elif question_type == "boolean":
        return "yesno"
    
    # Default to text
    else:
        return "text"


def _award_completion_points(module_key: str, outcome: dict):
    """Award points and badges for completing a trivia module."""
    # Initialize trivia progress tracker
    if "senior_trivia_progress" not in st.session_state:
        st.session_state["senior_trivia_progress"] = {
            "total_points": 0,
            "modules_completed": [],
            "badges_earned": []
        }
    
    progress = st.session_state["senior_trivia_progress"]
    
    # Check if already completed
    if module_key not in progress["modules_completed"]:
        progress["modules_completed"].append(module_key)
        
        # Award points (10 points per correct answer)
        correct_count = outcome.get("correct_count", 0)
        points = correct_count * 10
        progress["total_points"] += points
        
        # Award badge
        badge_names = {
            "truths_myths": "Myth Buster",
            "music_trivia": "Music Master",
            "medicare_quiz": "Medicare Pro",
            "healthy_habits": "Wellness Champion",
            "community_challenge": "Family Fun"
        }
        badge = badge_names.get(module_key, "Trivia Star")
        progress["badges_earned"].append(badge)
        
        st.success(f"🎉 You earned {points} points and the **{badge}** badge!")


def _show_completion_actions():
    """Show actions after completing a trivia module."""
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔙 Back to Trivia Hub", use_container_width=True):
            st.session_state["senior_trivia_current_module"] = None
            st.rerun()
    
    with col2:
        if st.button("🏠 Back to Waiting Room", use_container_width=True):
            st.session_state["senior_trivia_current_module"] = None
            # Route back to waiting room hub
            st.rerun()
