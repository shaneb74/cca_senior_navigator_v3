import streamlit as st
import json
from pathlib import Path
from core.state import get_module_state, get_user_ctx
from core.ui import hub_section, tiles_open, tiles_close, render_module_tile

# Load config
CONFIG_PATH = Path(__file__).parent.parent / "config" / "cost_config.v3.json"
with open(CONFIG_PATH) as f:
    COST_CONFIG = json.load(f)

def get_module_config():
    """Returns modular module configuration with completion logic and status generators."""
    return {
        "quick_estimate": {
            "title": "Quick Estimate",
            "description": "Get a fast cost estimate",
            "required_fields": [],
            "get_status": lambda data: "Completed" if "care_type" in data else "Not started",
            "is_complete": lambda data: "care_type" in data
        },
        "income_assets": {
            "title": "Income & Assets",
            "description": "Capture monthly income and household finances",
            "required_fields": ["social_security", "pension", "wages", "other_income", "liquid_savings", "retirement"],
            "optional_fields": ["partner", "finance_handling", "home_equity"],
            "get_status": lambda data: get_income_status(data),
            "is_complete": lambda data: is_income_complete(data)
        },
        "housing_options": {
            "title": "Housing Options",
            "description": "Define care requirements and modifiers",
            "required_fields": ["care_type", "care_details"],
            "get_status": lambda data: get_care_status(data),
            "is_complete": lambda data: is_care_complete(data)
        },
        "va_benefits": {
            "title": "VA Benefits",
            "description": "Estimate veteran benefits and eligibility",
            "required_fields": ["va_benefits"],
            "conditional": lambda data: data.get("veteran", False),
            "get_status": lambda data: get_va_status(data),
            "is_complete": lambda data: is_va_complete(data)
        },
        "home_mods": {
            "title": "Home Modifications",
            "description": "Plan home modifications for accessibility",
            "required_fields": [],
            "get_status": lambda data: "Not implemented",
            "is_complete": lambda data: False
        },
        "runway_projection": {
            "title": "Runway Projection",
            "description": "Calculate how long your money will last",
            "required_fields": [],
            "get_status": lambda data: "Not implemented",
            "is_complete": lambda data: False
        }
    }

def is_income_complete(data):
    """Check if income module is complete."""
    required = ["social_security", "pension", "wages", "other_income"]
    return all(k in data for k in required)

def get_income_status(data):
    """Generate detailed income status."""
    if not is_income_complete(data):
        return "Not started"
    
    total = sum([data.get(k, 0) for k in ['social_security', 'pension', 'wages', 'other_income']])
    sources = []
    if data.get('social_security', 0) > 0: sources.append("Social Security")
    if data.get('pension', 0) > 0: sources.append("Pension")
    if data.get('wages', 0) > 0: sources.append("Wages")
    if data.get('other_income', 0) > 0: sources.append("Other")
    
    household = ""
    if data.get('partner'):
        handling = data.get('finance_handling', 'Joint household')
        household = f" • {handling}"
    
    return f"${total:,.0f}/mo from {', '.join(sources)}{household}"

def is_care_complete(data):
    """Check if care needs module is complete."""
    return "care_type" in data and "care_details" in data

def get_care_status(data):
    """Generate detailed care needs status."""
    if not is_care_complete(data):
        return "Not started"
    
    care_type = data.get("care_type", "")
    details = data.get("care_details", {})
    
    type_display = {
        "in_home": f"In-Home Care ({details.get('hours', 4)} hr/day)",
        "assisted_living": f"Assisted Living ({details.get('apartment_type', 'studio').replace('_', ' ')})",
        "memory_care": f"Memory Care ({details.get('care_intensity', 'standard')})"
    }.get(care_type, care_type.replace('_', ' ').title())
    
    modifiers = []
    if details.get('help_level') != 'light':
        modifiers.append(f"Help: {details['help_level']}")
    if details.get('mobility') != 'independent':
        modifiers.append(f"Mobility: {details['mobility']}")
    
    modifier_text = f" • {', '.join(modifiers)}" if modifiers else ""
    
    return f"{type_display}{modifier_text}"

def is_va_complete(data):
    """Check if VA benefits module is complete."""
    return "va_benefits" in data

def get_va_status(data):
    """Generate detailed VA benefits status."""
    if not is_va_complete(data):
        return "Not started"
    
    amount = data.get('va_benefits', 0)
    return f"${amount:,.0f}/mo estimated benefits"

def get_base_cost(care_type, details):
    if care_type == "in_home":
        hours = details.get("hours", 4)
        return COST_CONFIG["base_rates"]["in_home_hourly"] * hours * 30  # monthly
    elif care_type == "assisted_living":
        apt_type = details.get("apartment_type", "studio")
        return COST_CONFIG["base_rates"]["assisted_living"][apt_type]
    elif care_type == "memory_care":
        intensity = details.get("care_intensity", "standard")
        return COST_CONFIG["base_rates"]["memory_care"][intensity]
    return 0

def get_modifiers(care_type, details):
    total = 0
    mods = COST_CONFIG["modifiers"]
    for key, value in details.items():
        if key in mods and value in mods[key]:
            total += mods[key][value]
    if care_type == "assisted_living" and details.get("second_person"):
        apt_type = details.get("apartment_type", "studio")
        total += mods["second_person"][apt_type]
    return total

def calculate_monthly_cost(care_type, details, zip_code=None):
    base = get_base_cost(care_type, details)
    mods = get_modifiers(care_type, details)
    multiplier = COST_CONFIG["zip_multipliers"].get(str(zip_code), COST_CONFIG["zip_multipliers"]["default"])
    return (base + mods) * multiplier

def get_gcp_recommendation():
    gcp_data = st.session_state.get("gcp_data", {})
    # Assume gcp_data has 'care_type' and 'details'
    care_type = gcp_data.get("care_type", "in_home")
    details = gcp_data.get("details", {"hours": 4})
    cost = calculate_monthly_cost(care_type, details)
    return care_type, details, cost

def render_landing():
    st.title("Cost Planner: See How Long Your Money Lasts")
    
    gcp_exists = "gcp_data" in st.session_state
    if gcp_exists:
        care_type, details, cost = get_gcp_recommendation()
        care_label = {
            "in_home": f"In-Home Care, {details.get('hours', 4)} hr/day",
            "assisted_living": "Assisted Living (studio)",
            "memory_care": "Memory Care (standard)"
        }.get(care_type, "In-Home Care")
        st.write(f"Based on your Guided Care Plan, we recommend: {care_label}")
        st.write(f"Estimated Monthly Cost: ${cost:,.0f}/mo (national average)")
    else:
        st.write("Plan your care costs (e.g., ~$5,500/mo for Assisted Living).")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start My Plan", key="start_plan"):
            # Assume auth handled, or add modal
            st.session_state["cost_planner_step"] = "entry_flow"
            st.rerun()
    with col2:
        if st.button("Explore Costs", key="explore_costs"):
            st.session_state["cost_planner_step"] = "explore"
            st.rerun()

def render_explore():
    st.title("Explore Care Costs")
    care_type = st.selectbox("Care Type", ["in_home", "assisted_living", "memory_care"])
    if care_type == "in_home":
        hours = st.slider("Daily Hours", 1, 24, 4)
        details = {"hours": hours}
    elif care_type == "assisted_living":
        apt = st.selectbox("Apartment Type", ["studio", "1_bedroom", "2_bedroom"])
        details = {"apartment_type": apt}
    else:
        intensity = st.selectbox("Care Intensity", ["standard", "high_acuity"])
        details = {"care_intensity": intensity}
    
    cost = calculate_monthly_cost(care_type, details)
    st.write(f"Estimated Monthly Cost: ${cost:,.0f}/mo")
    
    if st.button("Back to Landing"):
        st.session_state["cost_planner_step"] = "landing"
        st.rerun()

def render_entry_flow():
    st.title("Planning Context")
    data = st.session_state.get("cost_data", {})
    
    st.markdown("Are you a veteran?")
    veteran = st.radio(" ", ["Yes", "No"], index=0 if data.get("veteran") else 1, key="veteran", label_visibility="collapsed")
    
    st.markdown("Do you own a home?")
    homeowner = st.radio(" ", ["Yes", "No"], index=0 if data.get("homeowner") else 1, key="homeowner", label_visibility="collapsed")
    
    if st.button("Continue", key="continue_entry"):
        st.session_state["cost_data"] = {
            "veteran": veteran == "Yes",
            "homeowner": homeowner == "Yes"
        }
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()

def render_hub():
    ctx = get_user_ctx()
    user_id = ctx["auth"].get("user_id", "guest")
    product_key = "cost_planner"
    
    data = st.session_state.get("cost_data", {})
    
    # Cost summary
    care_type = data.get("care_type", "in_home")
    details = data.get("care_details", {})
    cost = calculate_monthly_cost(care_type, details, data.get("zip"))
    summary = f"Current Plan: {care_type.replace('_', ' ').title()} | Estimated Monthly Cost: ${cost:,.0f}/mo"
    
    hub_section("Cost Planner", right_meta=summary)
    tiles_open()
    
    # Get module configurations
    module_configs = get_module_config()
    
    # Render tiles for each module
    for module_key, config in module_configs.items():
        # Skip conditional modules that don't apply
        if "conditional" in config and not config["conditional"](data):
            continue
            
        # Mock state for now
        state = get_module_state(user_id, product_key, module_key)
        st.markdown('<article class="tile tile--md">', unsafe_allow_html=True)
        render_module_tile(product_key, module_key, state)
        st.markdown('</article>', unsafe_allow_html=True)
    
    tiles_close()
    
    if st.button("Continue to Expert Review", key="continue_review"):
        st.session_state["cost_planner_step"] = "expert_review"
        st.rerun()

def render_quick_estimate():
    st.title("Quick Estimate")
    data = st.session_state.get("cost_data", {})
    
    care_type = st.selectbox("Care Type", ["in_home", "assisted_living", "memory_care"])
    if care_type == "in_home":
        hours = st.slider("Daily Hours", 1, 24, 4)
        details = {"hours": hours}
    elif care_type == "assisted_living":
        apt = st.selectbox("Apartment Type", ["studio", "1_bedroom", "2_bedroom"])
        details = {"apartment_type": apt}
    else:
        intensity = st.selectbox("Care Intensity", ["standard", "high_acuity"])
        details = {"care_intensity": intensity}
    
    cost = calculate_monthly_cost(care_type, details)
    st.write(f"Estimated Monthly Cost: ${cost:,.0f}/mo")
    
    if st.button("Save & Continue", key="save_quick"):
        data["care_type"] = care_type
        data["care_details"] = details
        st.session_state["cost_data"] = data
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()

def render_income():
    st.title("Income Module")
    data = st.session_state.get("cost_data", {})
    
    ss = st.number_input("Social Security", value=data.get("social_security", 0), step=100)
    pension = st.number_input("Pension", value=data.get("pension", 0), step=100)
    wages = st.number_input("Wages", value=data.get("wages", 0), step=100)
    other = st.number_input("Other Monthly Income", value=data.get("other_income", 0), step=100)
    
    st.markdown("Is there a partner or spouse in this household?")
    partner = st.radio(" ", ["Yes", "No"], index=0 if data.get("partner") else 1, key="partner_radio", label_visibility="collapsed")
    finance_handling = None
    if partner == "Yes":
        st.markdown("How would you like to handle finances?")
        options = ["Joint household", "Split household", "Planning only for me"]
        default_index = 0
        if data.get("finance_handling"):
            try:
                default_index = options.index(data["finance_handling"])
            except ValueError:
                default_index = 0
        finance_handling = st.radio(" ", options, index=default_index, key="finance_radio", label_visibility="collapsed")
    
    if st.button("Save & Continue", key="save_income"):
        data.update({
            "social_security": ss,
            "pension": pension,
            "wages": wages,
            "other_income": other,
            "partner": partner == "Yes",
            "finance_handling": finance_handling
        })
        st.session_state["cost_data"] = data
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()

def render_housing_options():
    st.title("Housing Options Module")
    data = st.session_state.get("cost_data", {})
    
    gcp_exists = "gcp_data" in st.session_state
    if gcp_exists:
        care_type, details, _ = get_gcp_recommendation()
        st.write(f"Based on GCP, recommended: {care_type}")
        if st.button("Change", key="change_care"):
            gcp_exists = False
    
    if not gcp_exists:
        st.markdown("Choose Your Care Path")
        care_options = ["in_home", "assisted_living", "memory_care"]
        care_labels = ["In-Home Care (hourly, comes to you)", "Assisted Living (meals, help on site)", "Memory Care (secure, dementia-specialized)"]
        default_index = care_options.index(data.get("care_type", "in_home")) if data.get("care_type") in care_options else 0
        selected_label = st.radio(" ", care_labels, index=default_index, key="care_radio", label_visibility="collapsed")
        care_type = care_options[care_labels.index(selected_label)]
        
        details = {}
        if care_type == "in_home":
            hours = st.slider("Daily Hours Needed: 0 ----[4]---- 24", 1, 24, data.get("care_details", {}).get("hours", 4))
            details["hours"] = hours
        elif care_type == "assisted_living":
            apt_options = ["studio", "1_bedroom", "2_bedroom"]
            apt_labels = ["Studio ($5,500/mo)", "1 Bedroom ($5,900/mo)", "2 Bedroom ($6,400/mo)"]
            default_apt = data.get("care_details", {}).get("apartment_type", "studio")
            apt_index = apt_options.index(default_apt) if default_apt in apt_options else 0
            apt_label = st.radio("Apartment Type", apt_labels, index=apt_index, key="apt_radio", label_visibility="collapsed")
            details["apartment_type"] = apt_options[apt_labels.index(apt_label)]
        else:
            intensity_options = ["standard", "high_acuity"]
            intensity_labels = ["Standard ($7,500/mo)", "High Acuity (+$1,500/mo, ~$9,000/mo)"]
            default_intensity = data.get("care_details", {}).get("care_intensity", "standard")
            intensity_index = intensity_options.index(default_intensity) if default_intensity in intensity_options else 0
            intensity_label = st.radio("Care Intensity", intensity_labels, index=intensity_index, key="intensity_radio", label_visibility="collapsed")
            details["care_intensity"] = intensity_options[intensity_labels.index(intensity_label)]
    
    # Modifiers
    st.markdown("Help Level")
    help_options = ["light", "moderate", "high"]
    help_labels = ["Light (+$0)", "Moderate (+$300)", "High (+$700)"]
    default_help = data.get("care_details", {}).get("help_level", "light")
    help_index = help_options.index(default_help) if default_help in help_options else 0
    help_label = st.radio(" ", help_labels, index=help_index, key="help_radio", label_visibility="collapsed")
    details["help_level"] = help_options[help_labels.index(help_label)]
    
    st.markdown("Mobility")
    mobility_options = ["independent", "device", "wheelchair", "bedbound"]
    mobility_labels = ["Independent (+$0)", "Device (+$200)", "Wheelchair (+$400)", "Bedbound (+$900)"]
    default_mobility = data.get("care_details", {}).get("mobility", "independent")
    mobility_index = mobility_options.index(default_mobility) if default_mobility in mobility_options else 0
    mobility_label = st.radio(" ", mobility_labels, index=mobility_index, key="mobility_radio", label_visibility="collapsed")
    details["mobility"] = mobility_options[mobility_labels.index(mobility_label)]
    
    if st.button("Save & Continue", key="save_care"):
        data["care_type"] = care_type
        data["care_details"] = details
        st.session_state["cost_data"] = data
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()

def render_va_benefits():
    st.title("VA Benefits Module")
    data = st.session_state.get("cost_data", {})
    
    # Only show if veteran
    if not data.get("veteran"):
        st.info("This module is only available for veterans.")
        if st.button("Back to Hub", key="back_hub_va"):
            st.session_state["cost_planner_step"] = "hub"
            st.rerun()
        return
    
    # Get ADL flags from care needs
    care_details = data.get("care_details", {})
    adl_flags = []
    if care_details.get("help_level") in ["moderate", "high"]:
        adl_flags.append("help with daily activities")
    if care_details.get("mobility") in ["wheelchair", "bedbound"]:
        adl_flags.append("mobility assistance")
    
    # Determine household configuration
    has_spouse = data.get("partner", False)
    finance_handling = data.get("finance_handling", "Joint household")
    
    # Estimate VA benefits
    estimated_benefit = 0
    benefit_type = ""
    
    if adl_flags:  # Has ADL needs
        if has_spouse and finance_handling in ["Joint household", "Split household"]:
            estimated_benefit = COST_CONFIG["va_benefits"]["veteran_spouse_aid_attendance"]
            benefit_type = "Aid & Attendance (veteran + spouse)"
        else:
            estimated_benefit = COST_CONFIG["va_benefits"]["veteran_alone_aid_attendance"]
            benefit_type = "Aid & Attendance (veteran-alone)"
    else:  # No ADL needs
        estimated_benefit = COST_CONFIG["va_benefits"]["veteran_alone_base"]
        benefit_type = "Base pension (veteran-alone)"
    
    # Display estimate
    adl_text = ", ".join(adl_flags) if adl_flags else "no specific ADL needs"
    st.markdown(f"Based on your answers (needing help with {adl_text}) and veteran status, we estimate: **${estimated_benefit:,.0f}/month** ({benefit_type}).")
    
    # Manual override
    st.markdown("Does this match what you receive?")
    col1, col2 = st.columns([3, 1])
    with col1:
        va_benefit = st.number_input(
            "Adjust → $", 
            value=data.get("va_benefits", estimated_benefit), 
            step=100,
            min_value=0,
            help="If you're getting a different amount, enter it here. We'll use it for your care cost plan."
        )
    with col2:
        st.markdown("*Adjust if different*")
    
    # Eligibility quiz
    if "va_quiz_open" not in st.session_state:
        st.session_state["va_quiz_open"] = False
    
    if st.button("Don't know if you qualify? Quick VA Quiz →", key="open_quiz"):
        st.session_state["va_quiz_open"] = True
        st.rerun()
    
    if st.session_state["va_quiz_open"]:
        st.markdown("---")
        st.subheader("Quick Eligibility Check")
        
        # Quiz questions
        active_duty = st.checkbox("Active duty for 24+ months?", value=True)
        dishonorable = st.checkbox("Other-than-honorable discharge or worse?", value=False)
        
        # Income check (simplified)
        low_income = st.checkbox("Household income under ~$25,000/year (veteran-alone)?", value=False)
        
        # ADL need
        adl_need = st.checkbox(
            "Need help with daily activities (e.g., bathing, dressing, meds)?", 
            value=bool(adl_flags),
            help=f"You marked needing help with {adl_text} in Care Needs." if adl_flags else None
        )
        
        service_issue = st.checkbox("Chronic issues (e.g., dementia, mobility) from service?", value=False)
        
        # Quiz result
        eligible = active_duty and not dishonorable and low_income and adl_need and service_issue
        
        if eligible:
            quiz_benefit = COST_CONFIG["va_benefits"]["veteran_spouse_aid_attendance"] if (has_spouse and finance_handling in ["Joint household", "Split household"]) else COST_CONFIG["va_benefits"]["veteran_alone_aid_attendance"]
            st.success(f"**Likely qualify for ~${quiz_benefit:,.0f}/month** (Aid & Attendance).")
        else:
            st.warning("**May not qualify.** Call 1-877-VET-CLAIM for Aid & Attendance info.")
        
        if st.button("Close Quiz", key="close_quiz"):
            st.session_state["va_quiz_open"] = False
            st.rerun()
    
    # Save button
    if st.button("Save & Continue", key="save_va"):
        data["va_benefits"] = va_benefit
        st.session_state["cost_data"] = data
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()

def render_home_mods():
    st.title("Home Modifications Module")
    st.info("This module is not yet implemented.")
    if st.button("Back to Hub", key="back_hub_mods"):
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()

def render_runway_projection():
    st.title("Runway Projection Module")
    st.info("This module is not yet implemented.")
    if st.button("Back to Hub", key="back_hub_runway"):
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()

def render_expert_review():
    st.title("Expert Review Snapshot")
    data = st.session_state.get("cost_data", {})
    
    care_type = data.get("care_type", "in_home")
    details = data.get("care_details", {})
    cost = calculate_monthly_cost(care_type, details, data.get("zip"))
    st.write(f"Care Plan: {care_type}")
    st.write(f"Monthly Cost: ${cost:,.0f}")
    st.write(f"Income: ${sum([data.get(k, 0) for k in ['social_security', 'pension', 'wages', 'other_income']])}")
    st.write(f"VA Benefits: ${data.get('va_benefits', 0):,.0f}")
    st.write(f"Assets: ${data.get('liquid_savings', 0) + data.get('retirement', 0) + data.get('home_equity', 0)}")
    
    # Runway placeholder
    st.write("Runway: Calculation not implemented yet")
    
    if st.button("Back to Hub", key="back_hub"):
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()

def render():
    """Main render function that routes to the appropriate step."""
    step = st.session_state.get("cost_planner_step", "landing")
    
    if step == "landing":
        render_landing()
    elif step == "explore":
        render_explore()
    elif step == "entry_flow":
        render_entry_flow()
    elif step == "hub":
        render_hub()
    elif step == "quick_estimate":
        render_quick_estimate()
    elif step == "income_assets":
        render_income()
    elif step == "housing_options":
        render_housing_options()
    elif step == "va_benefits":
        render_va_benefits()
    elif step == "home_mods":
        render_home_mods()
    elif step == "runway_projection":
        render_runway_projection()
    elif step == "expert_review":
        render_expert_review()
    else:
        # Default to landing if unknown step
        render_landing()
