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
        "income": {
            "title": "Income",
            "description": "Monthly income sources and household finances",
            "required_fields": ["social_security", "pension", "wages", "other_income"],
            "optional_fields": ["partner", "finance_handling"],
            "get_status": lambda data: get_income_status(data),
            "is_complete": lambda data: is_income_complete(data)
        },
        "expenses": {
            "title": "Expenses",
            "description": "Monthly expenses including housing",
            "required_fields": ["housing", "utilities", "groceries", "medications", "transportation", "other_expenses"],
            "get_status": lambda data: get_expenses_status(data),
            "is_complete": lambda data: is_expenses_complete(data)
        },
        "assets": {
            "title": "Assets",
            "description": "Liquid savings and retirement accounts",
            "required_fields": ["liquid_savings"],
            "optional_fields": ["retirement", "home_equity"],
            "get_status": lambda data: get_assets_status(data),
            "is_complete": lambda data: is_assets_complete(data)
        },
        "care_needs": {
            "title": "Care Needs",
            "description": "Care requirements and modifiers",
            "required_fields": ["care_type", "care_details"],
            "get_status": lambda data: get_care_status(data),
            "is_complete": lambda data: is_care_complete(data)
        },
        "va_benefits": {
            "title": "VA Benefits",
            "description": "Veteran benefits and eligibility",
            "required_fields": ["va_benefits"],
            "conditional": lambda data: data.get("veteran", False),
            "get_status": lambda data: get_va_status(data),
            "is_complete": lambda data: is_va_complete(data)
        },
        "health_life_benefits": {
            "title": "Health, Life & Benefits",
            "description": "Health insurance and life insurance benefits",
            "required_fields": [],
            "get_status": lambda data: get_health_life_status(data),
            "is_complete": lambda data: is_health_life_complete(data)
        },
        "medicaid_navigation": {
            "title": "Medicaid Navigation",
            "description": "Medicaid eligibility and spend-down planning",
            "required_fields": [],
            "conditional": lambda data: is_medicaid_unlocked(data),
            "get_status": lambda data: get_medicaid_status(data),
            "is_complete": lambda data: is_medicaid_complete(data)
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

def is_expenses_complete(data):
    """Check if expenses module is complete."""
    required = ["housing", "utilities", "groceries", "medications", "transportation", "other_expenses"]
    return all(k in data for k in required)

def get_expenses_status(data):
    """Generate detailed expenses status."""
    if not is_expenses_complete(data):
        return "Not started"
    
    total = sum([data.get(k, 0) for k in ['housing', 'utilities', 'groceries', 'medications', 'transportation', 'other_expenses']])
    return f"${total:,.0f}/mo total expenses"

def is_assets_complete(data):
    """Check if assets module is complete."""
    return "liquid_savings" in data

def get_assets_status(data):
    """Generate detailed assets status."""
    if not is_assets_complete(data):
        return "Not started"
    
    total = data.get('liquid_savings', 0) + data.get('retirement', 0) + data.get('home_equity', 0)
    return f"${total:,.0f} total assets"

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

def is_health_life_complete(data):
    """Check if health/life benefits module is complete."""
    # This module is optional, so it's always "complete"
    return True

def get_health_life_status(data):
    """Generate detailed health/life benefits status."""
    benefits = []
    if data.get('long_term_care', False):
        benefits.append(f"LTC: ${data.get('ltc_payout', 0):,.0f}/mo")
    if data.get('whole_life', False):
        benefits.append(f"Whole Life: ${data.get('cash_value', 0):,.0f}")
    
    if benefits:
        return f"Benefits: {', '.join(benefits)}"
    return "No benefits configured"

def is_medicaid_unlocked(data):
    """Check if Medicaid Navigation should be unlocked."""
    return (is_income_complete(data) and is_expenses_complete(data) and 
            is_assets_complete(data) and is_care_complete(data))

def is_medicaid_complete(data):
    """Check if Medicaid Navigation module is complete."""
    # This is optional, so it's always "complete" once unlocked
    return True

def get_medicaid_status(data):
    """Generate detailed Medicaid status."""
    if not is_medicaid_unlocked(data):
        return "Locked - Complete Income, Expenses, Assets, Care Needs first"
    
    if data.get('medicaid', False):
        return "Already on Medicaid"
    elif data.get('spend_down_confirmed', False):
        return "Spend-down planning completed"
    else:
        return "Available - Review eligibility and spend-down options"

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
        st.write("Plan care costs (e.g., ~$5,500/mo for Assisted Living).")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start My Plan", key="start_plan"):
            # Force authentication via login modal
            st.session_state["cost_planner_step"] = "auth_required"
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

def render_auth_required():
    st.title("Authentication Required")
    st.write("To create and save your personalized care cost plan, please log in or sign up.")
    
    # Development bypass
    if st.button("Skip Authentication (Development)", key="dev_skip"):
        st.session_state["cost_planner_authenticated"] = True
        st.session_state["cost_planner_step"] = "income"
        st.rerun()
    
    st.markdown("---")
    
    # Simple login form (in production, use proper auth)
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")
        
        if submitted:
            # Mock authentication - in production, validate credentials
            if email and password:
                st.session_state["cost_planner_authenticated"] = True
                st.session_state["cost_planner_step"] = "income"
                st.rerun()
            else:
                st.error("Please enter email and password")
    
    st.write("Don't have an account?")
    if st.button("Sign Up", key="signup"):
        st.info("Sign up functionality would be implemented here")
    
    if st.button("Back to Landing", key="back_landing_auth"):
        st.session_state["cost_planner_step"] = "landing"
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
    # Import the theme CSS
    st.markdown(
        "<link rel='stylesheet' href='/assets/css/theme.css'>",
        unsafe_allow_html=True
    )
    
    # Apply canvas background like welcome pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    # Main content container
    st.markdown('<section class="container section">', unsafe_allow_html=True)
    
    # Hero section with title
    st.markdown(
        f"""
        <div class="text-center" style="margin-bottom: var(--space-10);">
            <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
                Income Module
            </h1>
            <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
                Let's understand your monthly income sources to build an accurate care cost plan.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
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
    
    # Close section
    st.markdown('</section>', unsafe_allow_html=True)

def render_housing_options():
    # Import the theme CSS
    st.markdown(
        "<link rel='stylesheet' href='/assets/css/theme.css'>",
        unsafe_allow_html=True
    )
    
    # Apply canvas background like welcome pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    # Main content container
    st.markdown('<section class="container section">', unsafe_allow_html=True)
    
    # Hero section with title
    st.markdown(
        f"""
        <div class="text-center" style="margin-bottom: var(--space-10);">
            <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
                Care Needs Module
            </h1>
            <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
                Choose your care path and tell us about your specific care requirements.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
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
    
    # Close section
    st.markdown('</section>', unsafe_allow_html=True)

def render_va_benefits():
    # Import the theme CSS
    st.markdown(
        "<link rel='stylesheet' href='/assets/css/theme.css'>",
        unsafe_allow_html=True
    )
    
    # Apply canvas background like welcome pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    # Main content container
    st.markdown('<section class="container section">', unsafe_allow_html=True)
    
    # Hero section with title
    st.markdown(
        f"""
        <div class="text-center" style="margin-bottom: var(--space-10);">
            <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
                VA Benefits Module
            </h1>
            <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
                Let's explore VA benefits that may help cover your care costs.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    data = st.session_state.get("cost_data", {})
    
    # Only show if veteran
    if not data.get("veteran"):
        st.info("This module is only available for veterans.")
        if st.button("Back to Hub", key="back_hub_va"):
            st.session_state["cost_planner_step"] = "hub"
            st.rerun()
        # Close section
        st.markdown('</section>', unsafe_allow_html=True)
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
    
    # Close section
    st.markdown('</section>', unsafe_allow_html=True)

def render_expenses():
    # Import the theme CSS
    st.markdown(
        "<link rel='stylesheet' href='/assets/css/theme.css'>",
        unsafe_allow_html=True
    )
    
    # Apply canvas background like welcome pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    # Main content container
    st.markdown('<section class="container section">', unsafe_allow_html=True)
    
    # Hero section with title
    st.markdown(
        f"""
        <div class="text-center" style="margin-bottom: var(--space-10);">
            <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
                Expenses Module
            </h1>
            <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
                Tell us about your monthly expenses so we can calculate your care affordability.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    data = st.session_state.get("cost_data", {})
    
    homeowner = data.get("homeowner", False)
    
    if homeowner:
        housing = st.number_input("Housing (Mortgage/Property Taxes/Insurance)", value=data.get("housing", 0), step=100)
    else:
        housing = st.number_input("Rent", value=data.get("housing", 0), step=100)
    
    utilities = st.number_input("Utilities (Electric, Water, etc.)", value=data.get("utilities", 0), step=50)
    groceries = st.number_input("Groceries", value=data.get("groceries", 0), step=50)
    medications = st.number_input("Medications/Healthcare", value=data.get("medications", 0), step=50)
    transportation = st.number_input("Transportation (Car, Gas, Transit)", value=data.get("transportation", 0), step=50)
    other_expenses = st.number_input("Other Expenses", value=data.get("other_expenses", 0), step=50,
                                   help="e.g., phone, subscriptions, personal care")
    
    if st.button("Save & Continue", key="save_expenses"):
        data.update({
            "housing": housing,
            "utilities": utilities,
            "groceries": groceries,
            "medications": medications,
            "transportation": transportation,
            "other_expenses": other_expenses
        })
        st.session_state["cost_data"] = data
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()
    
    # Close section
    st.markdown('</section>', unsafe_allow_html=True)

def render_assets():
    # Import the theme CSS
    st.markdown(
        "<link rel='stylesheet' href='/assets/css/theme.css'>",
        unsafe_allow_html=True
    )
    
    # Apply canvas background like welcome pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    # Main content container
    st.markdown('<section class="container section">', unsafe_allow_html=True)
    
    # Hero section with title
    st.markdown(
        f"""
        <div class="text-center" style="margin-bottom: var(--space-10);">
            <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
                Assets Module
            </h1>
            <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
                Let's review your savings and assets to understand your financial runway for care.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    data = st.session_state.get("cost_data", {})
    
    liquid_savings = st.number_input("Liquid Savings (Checking/Savings)", value=data.get("liquid_savings", 0), step=1000)
    retirement = st.number_input("Retirement Accounts (401k, IRA)", value=data.get("retirement", 0), step=1000)
    
    homeowner = data.get("homeowner", False)
    home_equity = 0
    if homeowner:
        home_equity = st.number_input("Home Equity (if owned)", value=data.get("home_equity", 0), step=10000)
    
    if st.button("Save & Continue", key="save_assets"):
        data.update({
            "liquid_savings": liquid_savings,
            "retirement": retirement,
            "home_equity": home_equity
        })
        st.session_state["cost_data"] = data
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()
    
    # Close section
    st.markdown('</section>', unsafe_allow_html=True)

def render_health_life_benefits():
    # Import the theme CSS
    st.markdown(
        "<link rel='stylesheet' href='/assets/css/theme.css'>",
        unsafe_allow_html=True
    )
    
    # Apply canvas background like welcome pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    # Main content container
    st.markdown('<section class="container section">', unsafe_allow_html=True)
    
    # Hero section with title
    st.markdown(
        f"""
        <div class="text-center" style="margin-bottom: var(--space-10);">
            <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
                Health, Life & Benefits Module
            </h1>
            <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
                Tell us about your insurance and benefits that may help with care costs.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    data = st.session_state.get("cost_data", {})
    
    st.markdown("Long-term care insurance?")
    ltc = st.radio(" ", ["Yes", "No"], index=0 if data.get("long_term_care") else 1, key="ltc_radio", label_visibility="collapsed")
    ltc_payout = 0
    if ltc == "Yes":
        ltc_payout = st.number_input("Monthly payout", value=data.get("ltc_payout", 0), step=100)
    
    st.markdown("Medicare?")
    medicare = st.radio(" ", ["Yes", "No"], index=0 if data.get("medicare") else 1, key="medicare_radio", label_visibility="collapsed")
    st.write("*Note: Covers hospital/drugs, not daily care. Gaps may apply.*")
    
    st.markdown("Whole life insurance policy?")
    whole_life = st.radio(" ", ["Yes", "No"], index=0 if data.get("whole_life") else 1, key="whole_life_radio", label_visibility="collapsed")
    cash_value = 0
    expected_payout = 0
    plan_to_sell = False
    if whole_life == "Yes":
        cash_value = st.number_input("Cash value", value=data.get("cash_value", 0), step=1000)
        st.markdown("Plan to sell/liquidate?")
        plan_to_sell = st.radio(" ", ["Yes", "No"], index=0 if data.get("plan_to_sell") else 1, key="sell_radio", label_visibility="collapsed")
        if plan_to_sell == "Yes":
            expected_payout = st.number_input("Expected one-time payout", value=data.get("expected_payout", cash_value), step=1000)
    
    if st.button("Save & Continue", key="save_health_life"):
        data.update({
            "long_term_care": ltc == "Yes",
            "ltc_payout": ltc_payout,
            "medicare": medicare == "Yes",
            "whole_life": whole_life == "Yes",
            "cash_value": cash_value,
            "plan_to_sell": plan_to_sell == "Yes",
            "expected_payout": expected_payout
        })
        st.session_state["cost_data"] = data
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()
    
    # Close section
    st.markdown('</section>', unsafe_allow_html=True)

def render_medicaid_navigation():
    # Import the theme CSS
    st.markdown(
        "<link rel='stylesheet' href='/assets/css/theme.css'>",
        unsafe_allow_html=True
    )
    
    # Apply canvas background like welcome pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    # Main content container
    st.markdown('<section class="container section">', unsafe_allow_html=True)
    
    # Hero section with title
    st.markdown(
        f"""
        <div class="text-center" style="margin-bottom: var(--space-10);">
            <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
                Navigating Medicaid
            </h1>
            <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
                What's safe to keep when planning for Medicaid eligibility.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    data = st.session_state.get("cost_data", {})
    
    # Check if unlocked
    if not is_medicaid_unlocked(data):
        st.error("Locked: Complete Income, Expenses, Assets, Care Needs first")
        st.image("https://via.placeholder.com/50x50?text=🔒", width=50)  # Placeholder for padlock icon
        if st.button("Back to Hub", key="back_hub_medicaid_locked"):
            st.session_state["cost_planner_step"] = "hub"
            st.rerun()
        # Close section
        st.markdown('</section>', unsafe_allow_html=True)
        return
    
    # Main content
    already_on_medicaid = data.get("medicaid", False)
    has_spouse = data.get("partner", False)
    finance_handling = data.get("finance_handling", "Joint household")
    homeowner = data.get("homeowner", False)
    
    if already_on_medicaid:
        st.info("Already on Medicaid? We'll factor it in.")
    else:
        st.markdown("**One spouse needs care? Medicaid won't take everything:**")
        st.markdown("- Community spouse keeps up to $154,140 (2025), plus home, car, personal items.")
        st.markdown("- Care recipient spends down to ~$2,000 in assets.")
        
        if has_spouse:
            st.markdown("**Does this plan include your spouse?**")
            spouse_included = st.radio(" ", ["Yes", "No"], 
                                     index=0 if data.get("spouse_included", True) else 1, 
                                     key="spouse_included_radio", label_visibility="collapsed")
            
            if spouse_included == "No":
                st.markdown("**Is your spouse paying for this care plan?**")
                spouse_paying = st.radio(" ", ["Yes (their money stays separate)", "No (estimate spend-down for care recipient)"], 
                                       index=0 if data.get("spouse_paying") else 1, 
                                       key="spouse_paying_radio", label_visibility="collapsed")
            else:
                spouse_paying = True
        else:
            spouse_included = False
            spouse_paying = False
        
        if homeowner:
            st.markdown("**Own a home?** Keep it—no forced sale, cover upkeep.")
        else:
            st.markdown("**Renting?** Medicaid won't affect your lease.")
        
        # Spend-down preview
        if "spend_down_open" not in st.session_state:
            st.session_state["spend_down_open"] = False
        
        if st.button("Show Spend-Down Preview →", key="open_spend_down"):
            st.session_state["spend_down_open"] = True
            st.rerun()
        
        if st.session_state["spend_down_open"]:
            st.markdown("---")
            st.subheader("Spend-Down Preview")
            
            # Calculate spend-down
            care_cost = calculate_monthly_cost(data.get("care_type", "in_home"), data.get("care_details", {}))
            income = sum([data.get(k, 0) for k in ['social_security', 'pension', 'wages', 'other_income']])
            expenses = sum([data.get(k, 0) for k in ['housing', 'utilities', 'groceries', 'medications', 'transportation', 'other_expenses']])
            assets = data.get('liquid_savings', 0) + data.get('retirement', 0) + data.get('home_equity', 0)
            
            gap = care_cost + expenses - income
            if gap > 0:
                months = assets / gap if gap > 0 else 999
                st.write(f"With ${care_cost:,.0f}/mo care, ${income:,.0f}/mo income, ${gap:,.0f}/mo gap, ${assets:,.0f} assets, Medicaid covers in ~{months:.0f} months.")
            else:
                st.write("No spend-down needed - income covers care costs.")
            
            spend_down_amount = st.slider("Spend before Medicaid?", 0, min(assets, 154140), data.get("spend_down_amount", 0))
            
            if st.button("Confirm Spend-Down Plan", key="confirm_spend_down"):
                data["spend_down_confirmed"] = True
                data["spend_down_amount"] = spend_down_amount
                st.session_state["cost_data"] = data
                st.success("Spend-down plan confirmed!")
        
        if st.button("Close Spend-Down Preview", key="close_spend_down"):
            st.session_state["spend_down_open"] = False
            st.rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Plan PDF", key="generate_pdf"):
            st.info("PDF generation would be implemented here")
    with col2:
        if st.button("Find a Planner", key="find_planner"):
            st.info("State-specific planner links would be shown here")
    
    if st.button("Back to Hub", key="back_hub_medicaid"):
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()
    
    # Close section
    st.markdown('</section>', unsafe_allow_html=True)

def render_expert_review():
    # Import the theme CSS
    st.markdown(
        "<link rel='stylesheet' href='/assets/css/theme.css'>",
        unsafe_allow_html=True
    )
    
    # Apply canvas background like welcome pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    # Main content container
    st.markdown('<section class="container section">', unsafe_allow_html=True)
    
    # Hero section with title
    st.markdown(
        f"""
        <div class="text-center" style="margin-bottom: var(--space-10);">
            <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
                Expert Review Snapshot
            </h1>
            <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
                Your personalized care cost plan summary and recommendations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
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
    
    # Close section
    st.markdown('</section>', unsafe_allow_html=True)

def render():
    """Main render function that routes to the appropriate step."""
    step = st.session_state.get("cost_planner_step", "landing")
    
    if step == "landing":
        render_landing()
    elif step == "auth_required":
        render_auth_required()
    elif step == "explore":
        render_explore()
    elif step == "hub":
        render_hub()
    elif step == "income":
        render_income()
    elif step == "expenses":
        render_expenses()
    elif step == "assets":
        render_assets()
    elif step == "care_needs":
        render_housing_options()  # Reusing existing function
    elif step == "va_benefits":
        render_va_benefits()
    elif step == "health_life_benefits":
        render_health_life_benefits()
    elif step == "medicaid_navigation":
        render_medicaid_navigation()
    elif step == "expert_review":
        render_expert_review()
    else:
        # Default to landing if unknown step
        render_landing()
