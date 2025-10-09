import streamlit as st
import json
from pathlib import Path
from core.ui import hub_section, tile_close, tile_open, tiles_close, tiles_open

# Load config
CONFIG_PATH = Path(__file__).parent.parent / "config" / "cost_config.v3.json"
with open(CONFIG_PATH) as f:
    COST_CONFIG = json.load(f)

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
        st.markdown('<button class="btn btn--primary" onclick="javascript:void(0)" id="start_plan">Start My Plan</button>', unsafe_allow_html=True)
        if st.button("Start My Plan", key="start_plan"):
            # Assume auth handled, or add modal
            st.session_state["cost_planner_step"] = "entry_flow"
            st.rerun()
    with col2:
        st.markdown('<button class="btn btn--secondary" onclick="javascript:void(0)" id="explore_costs">Explore Costs</button>', unsafe_allow_html=True)
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
    
    st.markdown('<div class="card-actions"><button class="btn btn--primary" onclick="javascript:void(0)" id="continue_entry">Continue</button></div>', unsafe_allow_html=True)
    if st.button("Continue", key="continue_entry"):
        st.session_state["cost_data"] = {
            "veteran": veteran == "Yes",
            "homeowner": homeowner == "Yes"
        }
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()

def render_hub():
    data = st.session_state.get("cost_data", {})
    
    # Cost summary
    care_type = data.get("care_type", "in_home")
    details = data.get("care_details", {})
    cost = calculate_monthly_cost(care_type, details, data.get("zip"))
    summary = f"Current Plan: {care_type.replace('_', ' ').title()} | Estimated Monthly Cost: ${cost:,.0f}/mo"
    
    hub_section("Modules Hub", right_meta=summary)
    tiles_open()
    
    modules = [
        ("income", "Income Sources", "Capture monthly income and household finances"),
        ("expenses", "Monthly Expenses", "Track housing, utilities, and other costs"),
        ("va_benefits", "VA Benefits", "Estimate veteran benefits and eligibility"),
        ("care_needs", "Care Needs", "Define care requirements and modifiers"),
        ("assets", "Assets", "Assess savings and retirement accounts")
    ]
    
    for mod_key, title, default_meta in modules:
        tile_open("md")
        status = "Completed" if mod_key in data else "Not Started"
        badge_class = "success" if status == "Completed" else "info"
        
        # Dynamic meta based on data
        if mod_key == "income" and status == "Completed":
            total_income = sum([data.get(k, 0) for k in ['social_security', 'pension', 'wages', 'other_income']])
            meta = f"Total Monthly Income: ${total_income:,.0f}"
        elif mod_key == "expenses" and status == "Completed":
            total_expenses = sum([data.get(k, 0) for k in ['housing', 'rent', 'utilities', 'groceries', 'medications', 'transportation', 'other_expenses']])
            meta = f"Total Monthly Expenses: ${total_expenses:,.0f}"
        elif mod_key == "va_benefits" and status == "Completed":
            va_amt = data.get('va_benefits', 0)
            meta = f"Estimated VA Benefits: ${va_amt:,.0f}/mo"
        elif mod_key == "care_needs" and status == "Completed":
            care_desc = f"{care_type.replace('_', ' ').title()}"
            if care_type == "in_home":
                hours = details.get("hours", 4)
                care_desc += f" ({hours} hr/day)"
            meta = f"Care Plan: {care_desc}"
        elif mod_key == "assets" and status == "Completed":
            total_assets = data.get('liquid_savings', 0) + data.get('retirement', 0) + data.get('home_equity', 0)
            meta = f"Total Assets: ${total_assets:,.0f}"
        else:
            meta = default_meta
        
        st.markdown(
            f"""<div class="tile-head">
  <div class="tile-title">{title}</div>
  <span class="badge {badge_class}">{status}</span>
</div>
<p class="tile-meta">{meta}</p>
<div class="kit-row">
  <button class="btn btn--primary" onclick="javascript:void(0)" id="edit_{mod_key}">Edit</button>
</div>""",
            unsafe_allow_html=True,
        )
        # Use a hidden button to trigger
        if st.button("Edit", key=f"edit_{mod_key}", help="Edit this module"):
            st.session_state["cost_planner_step"] = f"module_{mod_key}"
            st.rerun()
        tile_close()
    
    tiles_close()
    
    st.markdown('<div class="card-actions"><button class="btn btn--primary" onclick="javascript:void(0)" id="continue_review">Continue to Expert Review</button></div>', unsafe_allow_html=True)
    if st.button("Continue to Expert Review", key="continue_review"):
        st.session_state["cost_planner_step"] = "expert_review"
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
    
    st.markdown('<div class="card-actions"><button class="btn btn--primary" onclick="javascript:void(0)" id="save_income">Save & Continue</button></div>', unsafe_allow_html=True)
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

def render_expenses():
    st.title("Expenses Module")
    data = st.session_state.get("cost_data", {})
    homeowner = data.get("homeowner", False)
    
    if homeowner:
        housing = st.number_input("Housing (Mortgage/Property Taxes/Insurance)", value=data.get("housing", 0), step=100)
    else:
        rent = st.number_input("Rent", value=data.get("rent", 0), step=100)
    
    utilities = st.number_input("Utilities", value=data.get("utilities", 0), step=100)
    groceries = st.number_input("Groceries", value=data.get("groceries", 0), step=100)
    meds = st.number_input("Medications/Healthcare", value=data.get("medications", 0), step=100)
    transport = st.number_input("Transportation", value=data.get("transportation", 0), step=100)
    other_exp = st.number_input("Other Expenses", value=data.get("other_expenses", 0), step=100)
    
    st.markdown('<div class="card-actions"><button class="btn btn--primary" onclick="javascript:void(0)" id="save_expenses">Save & Continue</button></div>', unsafe_allow_html=True)
    if st.button("Save & Continue", key="save_expenses"):
        updates = {
            "utilities": utilities,
            "groceries": groceries,
            "medications": meds,
            "transportation": transport,
            "other_expenses": other_exp
        }
        if homeowner:
            updates["housing"] = housing
        else:
            updates["rent"] = rent
        data.update(updates)
        st.session_state["cost_data"] = data
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()

def render_va_benefits():
    st.title("VA Benefits Module")
    data = st.session_state.get("cost_data", {})
    if not data.get("veteran"):
        st.write("Not applicable")
        return
    
    estimated = COST_CONFIG["va_benefits"]["aid_attendance_veteran_spouse"]
    st.write(f"Based on your answers, we estimate: ${estimated}/month (Aid & Attendance)")
    va_benefit = st.number_input("Adjust if different", value=estimated, step=100)
    
    # Simple quiz placeholder
    if st.button("Quick VA Quiz"):
        st.write("Quiz not implemented yet")
    
    st.markdown('<div class="card-actions"><button class="btn btn--primary" onclick="javascript:void(0)" id="save_va">Save & Continue</button></div>', unsafe_allow_html=True)
    if st.button("Save & Continue", key="save_va"):
        data["va_benefits"] = va_benefit
        st.session_state["cost_data"] = data
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()

def render_care_needs():
    st.title("Care Needs Module")
    data = st.session_state.get("cost_data", {})
    
    gcp_exists = "gcp_data" in st.session_state
    if gcp_exists:
        care_type, details, _ = get_gcp_recommendation()
        st.write(f"Based on GCP, recommended: {care_type}")
        st.markdown('<div class="card-actions"><button class="btn btn--secondary" onclick="javascript:void(0)" id="change_care">Change</button></div>', unsafe_allow_html=True)
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
    
    # Add more as needed
    
    st.markdown('<div class="card-actions"><button class="btn btn--primary" onclick="javascript:void(0)" id="save_care">Save & Continue</button></div>', unsafe_allow_html=True)
    if st.button("Save & Continue", key="save_care"):
        data["care_type"] = care_type
        data["care_details"] = details
        st.session_state["cost_data"] = data
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()

def render_assets():
    st.title("Assets Module")
    data = st.session_state.get("cost_data", {})
    
    liquid = st.number_input("Liquid Savings", value=data.get("liquid_savings", 0), step=1000)
    retirement = st.number_input("Retirement Accounts", value=data.get("retirement", 0), step=1000)
    home_equity = 0
    if data.get("homeowner"):
        home_equity = st.number_input("Home Equity", value=data.get("home_equity", 0), step=1000)
    
    st.markdown('<div class="card-actions"><button class="btn btn--primary" onclick="javascript:void(0)" id="save_assets">Save & Continue</button></div>', unsafe_allow_html=True)
    if st.button("Save & Continue", key="save_assets"):
        data.update({
            "liquid_savings": liquid,
            "retirement": retirement,
            "home_equity": home_equity
        })
        st.session_state["cost_data"] = data
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
    st.write(f"Expenses: ${sum([data.get(k, 0) for k in ['housing', 'rent', 'utilities', 'groceries', 'medications', 'transportation', 'other_expenses']])}")
    st.write(f"VA Benefits: ${data.get('va_benefits', 0)}")
    st.write(f"Assets: ${data.get('liquid_savings', 0) + data.get('retirement', 0) + data.get('home_equity', 0)}")
    
    # Runway placeholder
    st.write("Runway: Calculation not implemented yet")
    
    st.markdown('<div class="card-actions"><button class="btn btn--secondary" onclick="javascript:void(0)" id="back_hub">Back to Hub</button></div>', unsafe_allow_html=True)
    if st.button("Back to Hub", key="back_hub"):
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()

def render():
    if "cost_planner_step" not in st.session_state:
        st.session_state["cost_planner_step"] = "landing"
    
    step = st.session_state["cost_planner_step"]
    
    if step == "landing":
        render_landing()
    elif step == "explore":
        render_explore()
    elif step == "entry_flow":
        render_entry_flow()
    elif step == "hub":
        render_hub()
    elif step == "module_income":
        render_income()
    elif step == "module_expenses":
        render_expenses()
    elif step == "module_va_benefits":
        render_va_benefits()
    elif step == "module_care_needs":
        render_care_needs()
    elif step == "module_assets":
        render_assets()
    elif step == "expert_review":
        render_expert_review()
    else:
        st.write("Unknown step")
