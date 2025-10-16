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
from core.modules.schema import ModuleConfig
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
    """Load module configuration for the specified trivia game."""
    from pathlib import Path
    import json
    
    module_path = Path(__file__).parent / "modules" / f"{module_key}.json"
    
    with open(module_path, "r") as f:
        data = json.load(f)
    
    return ModuleConfig.from_dict(data)


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
