import streamlit as st
import json
from pathlib import Path

from core.state import get_module_state, get_user_ctx
from core.ui import hub_section, render_module_tile, tiles_close, tiles_open
from core.gcp_data import load_schema, load_blurbs, evaluate


def get_person_name():
    """Get the person's name from session state, with fallback."""
    if "person_name" in st.session_state:
        name = st.session_state["person_name"].strip()
        return name if name else "this person"
    else:
        return "this person"  # Fallback if key doesn't exist


def replace_name_placeholder(text):
    """Replace {name} placeholder with the person's name."""
    name = get_person_name()
    return text.replace("{name}", name)


def generate_conversational_blurb(result, answers):
    """Generate a conversational blurb based on GCP results and cost config."""
    try:
        # Load cost config
        cost_config_path = Path(__file__).parent.parent / "config" / "cost_config.v3.json"
        with open(cost_config_path, "r", encoding="utf-8") as f:
            cost_config = json.load(f)
        
        tier_name = result["tier"]
        behaviors = answers.get("behaviors", [])
        
        # Base messages by care type
        base_messages = {
            "In-Home Care": "Based on your needs, we recommend In-Home Care for personalized support in your own home.",
            "Assisted Living": "Based on your moderate assistance needs, we recommend Assisted Living for a supportive community environment.",
            "Memory Care": "Based on your cognitive and behavioral needs, we recommend Memory Care for specialized dementia support.",
            "Memory Care High Acuity": "Based on your complex cognitive and behavioral needs, we recommend Memory Care with high-acuity support."
        }
        
        blurb_parts = [base_messages.get(tier_name, f"Based on your assessment, we recommend {tier_name}.")]
        
        # Add behavior-specific messaging
        behavior_messages = []
        if "Wandering" in behaviors:
            behavior_messages.append("we've factored in extra support for wandering behaviors")
        if "Aggression" in behaviors:
            behavior_messages.append("we've included provisions for behavioral support")
        if "Elopement / Exit-seeking" in behaviors:
            behavior_messages.append("we've accounted for exit-seeking behaviors with secure environment features")
        
        if behavior_messages:
            blurb_parts.append(f"Since you've mentioned certain behaviors, {', and '.join(behavior_messages)}.")
        
        # Add mobility considerations
        mobility = answers.get("mobility")
        if mobility in ["Uses wheelchair or scooter", "Bed-bound or limited mobility"]:
            blurb_parts.append("Your mobility needs also suggest assistance with daily activities, which this option covers well.")
        
        # Combine into 2-4 sentences
        full_blurb = " ".join(blurb_parts[:3])  # Limit to 3 parts max
        
        return full_blurb
        
    except Exception as e:
        # Fallback template
        tier_name = result["tier"]
        return f"Based on your needs, we recommend {tier_name} for the level of support that best fits your situation. This option provides the right balance of care and independence while considering your specific requirements."


def render():
    # Import the theme CSS and apply new styling
    st.markdown(
        """
        <link rel='stylesheet' href='/assets/css/theme.css'>
        <style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        /* New styling overrides */
        .stButton > button {
            background: #3B82F6 !important;
            color: white !important;
            border-radius: 5px !important;
            border: none !important;
        }
        .stButton > button:hover {
            background: #2563EB !important;
        }
        .stRadio label[data-baseweb="radio"] input:checked + div {
            color: black !important;
        }
        .stRadio label[data-baseweb="radio"] input:not(:checked) + div {
            color: gray !important;
        }
        .stTextInput > div > div, .stNumberInput > div > div, .stSelectbox > div > div, .stTextArea > div > div {
            border-radius: 5px !important;
            padding: 10px !important;
        }
        .container {
            padding: 10px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Main content container
    st.markdown('<section class="container section" style="padding: 10px;">', unsafe_allow_html=True)
    
    ctx = get_user_ctx()
    user_id = ctx["auth"].get("user_id", "guest")
    product_key = "gcp"
    
    hub_section("Guided Care Plan")
    
    # Initialize session state for GCP wizard
    if "gcp_section" not in st.session_state:
        st.session_state["gcp_section"] = 0
    if "gcp_answers" not in st.session_state:
        st.session_state["gcp_answers"] = {}
    
    # Load sections from schema
    schema = load_schema()
    section_icons = {
        "about": "👤",
        "care_needs": "💊",
        "daily_living": "🏠",
        "cognition_mental_health": "🧠",
        "results": "📊"
    }
    sections = [
        {
            "id": s["id"],
            "title": s["title"],
            "icon": section_icons.get(s["id"], "�")
        }
        for s in schema["sections"]
    ]
    
    current_section_idx = st.session_state["gcp_section"]
    current_section = sections[current_section_idx]
    
    # Progress indicator at the top
    progress = (current_section_idx + 1) / len(sections)
    st.progress(progress)
    
    # Section header with improved styling
    header_title = current_section["title"]
    
    st.markdown(f"""
    <div style="text-align: center; margin: 1rem 0; padding: 1rem; background: #F5F5F5; border: 1px solid #E0E0E0; border-radius: 8px;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{current_section['icon']}</div>
        <h1 style="color: #2c3e50; margin-bottom: 0.5rem; font-size: 1.5rem; font-weight: bold;">{header_title}</h1>
        <p style="color: #7f8c8d; font-size: 0.9rem; margin: 0;">Section {current_section_idx + 1} of {len(sections)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if current_section["id"] == "results":
        render_results()
    else:
        render_section_questions(current_section["id"])
    
    # Navigation buttons with improved styling
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_section_idx > 0:
            if st.button("← Back", use_container_width=True, key="back_btn"):
                st.session_state["gcp_section"] = current_section_idx - 1
                st.rerun()
    
    with col3:
        if current_section_idx < len(sections) - 1:
            if st.button("Next →", use_container_width=True, key="next_btn"):
                st.session_state["gcp_section"] = current_section_idx + 1
                st.rerun()
        else:
            # On results page, show different navigation
            pass
    
    # Close section
    st.markdown('</section>', unsafe_allow_html=True)


def render_section_questions(section_id):
    """Render questions for a specific section."""
    schema = load_schema()
    section_data = next((s for s in schema["sections"] if s["id"] == section_id), None)
    
    if not section_data:
        st.error(f"Section {section_id} not found in schema")
        return
    
    answers = st.session_state["gcp_answers"]
    
    for question in section_data["questions"]:
        qkey = question["key"]
        label = replace_name_placeholder(question["label"])
        qtype = question["type"]
        options = question.get("options", [])
        required = question.get("required", False)
        
        # Check conditional display
        should_show = True
        if "when" in question:
            when = question["when"]
            if "in" in when:
                dep_key = when["in"][0]  # assuming single dependency
                dep_values = when["in"][1:]
                dep_answer = answers.get(dep_key)
                if isinstance(dep_answer, list):
                    should_show = any(val in dep_answer for val in dep_values)
                else:
                    should_show = dep_answer in dep_values
        
        if not should_show:
            continue
            
        st.markdown(f"""
        <div style="margin: 5px 0; padding: 1rem; background: #F5F5F5; border: 1px solid #E0E0E0; border-radius: 8px;">
            <h4 style="color: #2c3e50; margin-bottom: 0.5rem; font-weight: 600; font-size: 14px; text-align: left;">{label}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if qtype == "pills":
            # Use radio buttons for single choice pills
            current_value = answers.get(qkey)
            selected_option = st.radio(
                f"Select answer for {label}",
                options=options,
                index=options.index(current_value) if current_value in options else None,
                key=f"gcp_{qkey}",
                label_visibility="collapsed"
            )
            if selected_option:
                answers[qkey] = selected_option
                
        elif qtype == "multiselect":
            # Use multiselect for multi-select questions
            current_selections = answers.get(qkey, [])
            selected = st.multiselect(
                f"Select all that apply for {label}",
                options=options,
                default=current_selections,
                key=f"gcp_{qkey}",
                label_visibility="collapsed"
            )
            answers[qkey] = selected
            
        elif qtype == "pill_list":
            # Implement pill list similar to product_tile.py
            current_pills = answers.get(qkey, [])
            new_pill = st.text_input(f"Add item for {label}", key=f"gcp_{qkey}_input")
            col1, col2 = st.columns([3, 1])
            with col1:
                pass  # text input is above
            with col2:
                if st.button("Add", key=f"gcp_{qkey}_add") and new_pill.strip():
                    new_pill = new_pill.strip()
                    if new_pill not in current_pills:
                        current_pills.append(new_pill)
                        answers[qkey] = current_pills
                        st.rerun()
            
            # Display current pills
            if current_pills:
                st.markdown('<div style="margin-top: 10px;">', unsafe_allow_html=True)
                for i, pill in enumerate(current_pills):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"<span style='background: #007BFF; color: white; padding: 2px 8px; border-radius: 12px; margin-right: 5px;'>{pill}</span>", unsafe_allow_html=True)
                    with col2:
                        if st.button("×", key=f"gcp_{qkey}_remove_{i}"):
                            current_pills.remove(pill)
                            answers[qkey] = current_pills
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)





def render_results():
    """Render the results page with evaluation and recommendations."""
    answers = st.session_state["gcp_answers"]
    
    if not answers:
        st.warning("No answers provided yet. Please complete the assessment.")
        return
    
    # Evaluate using GCP engine
    try:
        result = evaluate(answers)
        
        # Display recommendation
        tier_name = result["tier"]
        st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px;">
            <h3 style="margin-bottom: 1rem; font-size: 2rem;">Recommended Care Setting</h3>
            <div style="font-size: 3rem; margin: 1rem 0;">{tier_name}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add conversational blurb from cost_config.json
        blurb_text = generate_conversational_blurb(result, answers)
        if blurb_text:
            st.markdown(f"""
            <div style="margin: 1rem 0; padding: 1rem; background: #F5F5F5; border: 1px solid #E0E0E0; border-radius: 8px; font-style: italic;">
                {blurb_text}
            </div>
            """, unsafe_allow_html=True)
        
        # Show key drivers
        if result.get("drivers"):
            st.markdown("### Key Factors in This Recommendation")
            for qid, answer, points in result["drivers"]:
                st.markdown(f"- **{answer}** ({points:+.1f} points)")
        
        # Show advisories
        if result.get("advisories"):
            st.markdown("### Important Considerations")
            for advisory in result["advisories"]:
                st.info(advisory)
        
        # Navigation options
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Start Over", use_container_width=True):
                st.session_state["gcp_answers"] = {}
                st.session_state["gcp_section"] = 0
                st.rerun()
        
        with col2:
            if st.button("💰 Try Cost Planner", use_container_width=True):
                from core.nav import route_to
                route_to("cost_planner")
        
        # Return to Hub button (centered below)
        st.markdown("<div style='text-align: center; margin-top: 1rem;'>", unsafe_allow_html=True)
        if st.button("🏠 Return to Hub", use_container_width=False):
            from core.nav import route_to
            route_to("hub_concierge")
        st.markdown("</div>", unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"Error evaluating assessment: {str(e)}")
        st.json(answers)  # Debug info

