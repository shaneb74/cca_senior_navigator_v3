import streamlit as st

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


def render():
    ctx = get_user_ctx()
    user_id = ctx["auth"].get("user_id", "guest")
    product_key = "gcp"
    
    hub_section("Guided Care Plan")
    
    # Initialize session state for GCP wizard
    if "gcp_section" not in st.session_state:
        st.session_state["gcp_section"] = 0
    if "gcp_answers" not in st.session_state:
        st.session_state["gcp_answers"] = {}
    
    sections = [
        {"id": "about", "title": "About", "icon": "👤"},
        {"id": "care_needs", "title": "Care Needs", "icon": "�"},
        {"id": "daily_living", "title": "Daily Living", "icon": "🏠"},
        {"id": "cognition_mental_health", "title": "Cognition & Mental Health", "icon": "🧠"},
        {"id": "results", "title": "Results", "icon": "📊"}
    ]
    
    current_section_idx = st.session_state["gcp_section"]
    current_section = sections[current_section_idx]
    
    # Progress indicator at the top
    progress = (current_section_idx + 1) / len(sections)
    st.progress(progress)
    
    # Section header with improved styling
    header_title = f"About {get_person_name()}" if current_section["id"] == "about" else current_section["title"]
    
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


def render_section_questions(section_id):
    """Render questions for a specific section."""
    schema = load_schema()
    section_data = next((s for s in schema["sections"] if s["id"] == section_id), None)
    
    if not section_data:
        st.error(f"Section {section_id} not found in schema")
        return
    
    answers = st.session_state["gcp_answers"]
    
    for question in section_data["questions"]:
        qid = question["id"]
        label = replace_name_placeholder(question["label"])  # Replace [name] with actual name
        qtype = question["type"]
        options = question["options"]
        
        # Check showIf conditions
        should_show = True
        if "showIf" in question:
            should_show = evaluate_show_conditions(question["showIf"], answers)
        
        if not should_show:
            continue
            
        st.markdown(f"""
        <div style="margin: 5px 0; padding: 1rem; background: #F5F5F5; border: 1px solid #E0E0E0; border-radius: 8px;">
            <h4 style="color: #2c3e50; margin-bottom: 0.5rem; font-weight: 600; font-size: 14px; text-align: left;">{label}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if qtype == "single":
            # Use segmented control for single choice
            current_value = answers.get(qid)
            selected_idx = None
            if current_value:
                try:
                    selected_idx = options.index(current_value)
                except ValueError:
                    selected_idx = None
            
            selected_option = st.segmented_control(
                label=f"Select answer for {label}",
                options=options,
                default=current_value,
                key=f"gcp_{qid}",
                label_visibility="collapsed"
            )
            
            if selected_option:
                answers[qid] = selected_option
                
        elif qtype == "multi_select":
            # Use multiselect for multi-select questions with custom styling
            current_selections = answers.get(qid, [])
            
            selected = st.multiselect(
                f"Select all that apply for {label}",
                options=options,
                default=current_selections,
                key=f"gcp_{qid}",
                label_visibility="collapsed"
            )
            
            answers[qid] = selected
                
        elif qtype == "matrix":
            # Use multiselect for matrix questions
            items = question.get("items", [])
            matrix_options = question.get("options", ["Not present", "Present"])
            
            st.markdown("<div style='margin-top: 0.5rem;'>", unsafe_allow_html=True)
            
            # Initialize answers[qid] as a list if it doesn't exist
            if qid not in answers:
                answers[qid] = []
            
            for item in items:
                item_id = item["id"]
                item_label = item["label"]
                
                # Create unique key for this matrix item
                matrix_key = f"{qid}_{item_id}"
                current_selections = answers.get(matrix_key, [])
                
                selected = st.multiselect(
                    f"{item_label}",
                    options=matrix_options,
                    default=current_selections,
                    key=f"gcp_{matrix_key}",
                    label_visibility="visible"
                )
                
                answers[matrix_key] = selected
                
                # Convert matrix selections to the expected format for scoring
                # Remove old entries for this item
                answers[qid] = [entry for entry in answers[qid] if not entry.startswith(f"{item_label} — ")]
                
                # Add new selections
                for option in selected:
                    answer_key = f"{item_label} — {option}"
                    if answer_key not in answers[qid]:
                        answers[qid].append(answer_key)
            
            st.markdown("</div>", unsafe_allow_html=True)


def evaluate_show_conditions(conditions, answers):
    """Evaluate showIf conditions for questions."""
    for condition in conditions:
        if "anyOf" in condition:
            any_match = False
            for sub_condition in condition["anyOf"]:
                if "count" in sub_condition:
                    # Handle count conditions (e.g., chronic conditions >= 2)
                    count_spec = sub_condition["count"]
                    question_id = count_spec["of"]
                    threshold = count_spec["gte"]
                    question_answers = answers.get(question_id, [])
                    if isinstance(question_answers, list) and len(question_answers) >= threshold:
                        any_match = True
                        break
                elif "not" in sub_condition:
                    # Handle "not" conditions
                    key = list(sub_condition.keys())[0]
                    value = sub_condition[key]
                    if answers.get(key) != value:
                        any_match = True
                        break
                else:
                    # Handle direct equality conditions
                    key = list(sub_condition.keys())[0]
                    value = sub_condition[key]
                    if answers.get(key) == value:
                        any_match = True
                        break
            if not any_match:
                return False
    return True


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
        
        # Add conversational blurb from blurbs.json
        blurbs = load_blurbs()
        blurb_key = f"recommendation_{tier_name.lower().replace(' ', '_')}"
        if blurb_key in blurbs:
            blurb_text = blurbs[blurb_key]
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
            if st.button("🏠 Return to Hub", use_container_width=True):
                st.query_params["page"] = "welcome"
                st.rerun()
                
    except Exception as e:
        st.error(f"Error evaluating assessment: {str(e)}")
        st.json(answers)  # Debug info

