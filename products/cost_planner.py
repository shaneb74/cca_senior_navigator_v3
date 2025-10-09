import streamlit as st
import json
from pathlib import Path

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
    veteran = st.radio("Are you a veteran?", ["Yes", "No"], key="veteran")
    homeowner = st.radio("Do you own a home?", ["Yes", "No"], key="homeowner")
    
    if st.button("Continue"):
        st.session_state["cost_data"] = {
            "veteran": veteran == "Yes",
            "homeowner": homeowner == "Yes"
        }
        st.session_state["cost_planner_step"] = "hub"
        st.rerun()

def render_hub():
    st.title("Modules Hub")
    data = st.session_state.get("cost_data", {})
    
    # Cost summary
    care_type = data.get("care_type", "in_home")
    details = data.get("care_details", {})
    cost = calculate_monthly_cost(care_type, details, data.get("zip"))
    st.write(f"Current Plan: {care_type.replace('_', ' ').title()}")
    st.write(f"Estimated Monthly Cost: ${cost:,.0f}/mo")
    
    modules = ["income", "expenses", "va_benefits", "care_needs", "assets"]
    cols = st.columns(len(modules))
    for i, mod in enumerate(modules):
        with cols[i]:
            status = "Completed" if mod in data else "Not Started"
            if st.button(f"{mod.replace('_', ' ').title()}\n{status}", key=f"mod_{mod}"):
                st.session_state["cost_planner_step"] = f"module_{mod}"
                st.rerun()
    
    if st.button("Continue to Expert Review"):
        st.session_state["cost_planner_step"] = "expert_review"
        st.rerun()

def render_income():
    st.title("Income Module")
    data = st.session_state.get("cost_data", {})
    
    ss = st.number_input("Social Security", value=data.get("social_security", 0), step=100)
    pension = st.number_input("Pension", value=data.get("pension", 0), step=100)
    wages = st.number_input("Wages", value=data.get("wages", 0), step=100)
    other = st.number_input("Other Monthly Income", value=data.get("other_income", 0), step=100)
    
    partner = st.radio("Is there a partner or spouse?", ["Yes", "No"], index=0 if data.get("partner") else 1)
    finance_handling = None
    if partner == "Yes":
        finance_handling = st.selectbox("How to handle finances?", 
                                        ["Joint household", "Split household", "Planning only for me"])
    
    if st.button("Save & Continue"):
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
    
    if st.button("Save & Continue"):
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
    
    if st.button("Save & Continue"):
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
        if st.button("Change"):
            gcp_exists = False
    
    if not gcp_exists:
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
    
    # Modifiers
    help_level = st.selectbox("Help Level", ["light", "moderate", "high"])
    mobility = st.selectbox("Mobility", ["independent", "device", "wheelchair", "bedbound"])
    details.update({"help_level": help_level, "mobility": mobility})
    # Add more as needed
    
    if st.button("Save & Continue"):
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
    
    if st.button("Save & Continue"):
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
    
    if st.button("Back to Hub"):
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
