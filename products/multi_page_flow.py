import streamlit as st

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

# Track the current page in session state
if "current_page" not in st.session_state:
    st.session_state.current_page = 1

def go_to_page(page_number):
    st.session_state.current_page = page_number
    st.rerun()

def progress_indicator():
    total_pages = 5
    current = st.session_state.current_page
    st.markdown(
        f"<div style='text-align: center;'>Page {current} of {total_pages}</div>",
        unsafe_allow_html=True,
    )

def page_1():
    st.title("Find the right senior care")
    st.markdown(
        "<div style='text-align: center; margin-top: 20px;'>"
        "<button style='font-size: 20px; padding: 10px 20px;' onclick='window.location.reload()'>Start</button>"
        "</div>",
        unsafe_allow_html=True,
    )

def page_2():
    st.warning("We are unable to help with Medicaid-only situations.")
    st.subheader("Qualifier Questions")
    st.radio("Are you seeking care for yourself or a loved one?", ["Myself", "A loved one"], key="q1")
    st.slider("What is your estimated monthly budget?", 0, 10000, 5000, key="q2")
    st.radio("Is location a major factor in your decision?", ["Yes", "No"], key="q3")
    st.radio("Do you require memory care or specialized medical support?", ["Yes", "No"], key="q4")
    st.radio("Will you be paying privately or using insurance?", ["Privately", "Insurance"], key="q5")

def page_3():
    st.subheader("Daily Life & Support")
    st.radio("What level of help is needed with daily activities?", ["Minimal", "Moderate", "Extensive"], key="q6")
    st.radio("Social engagement preferences?", ["Group activities", "Quiet environment"], key="q7")
    st.radio("Transportation needs?", ["None", "Occasional", "Frequent"], key="q8")
    st.text_input("Dietary restrictions or preferences?", key="q9")

def page_4():
    st.subheader("Health & Safety")
    st.text_input("Any chronic health conditions?", key="q10")
    st.radio("Safety concerns?", ["None", "Fall risk", "Wandering"], key="q11")
    st.radio("Medication management needs?", ["None", "Some", "Full support"], key="q12")
    st.radio("Emergency response preferences?", ["None", "Basic", "Advanced"], key="q13")

def page_5():
    st.title("Summary & Recommendation")
    st.markdown(
        "<h2 style='text-align: center;'>Based on everything, we recommend</h2>"
        "<h1 style='text-align: center; color: green;'>ASSISTED LIVING</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<ul>"
        "<li>Location: Close to family in [City/Area]</li>"
        "<li>Budget: Within your stated range</li>"
        "<li>Care Level: Provides daily support and safety</li>"
        "<li>Social: Strong activity program</li>"
        "<li>Health: Medication and emergency management included</li>"
        "</ul>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center;'>This keeps Mom safe, close to you, and under budget.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='text-align: center;'>"
        "<button style='margin-right: 10px;'>View recommended communities</button>"
        "<button>Restart</button>"
        "</div>",
        unsafe_allow_html=True,
    )

# Render the current page
progress_indicator()
if st.session_state.current_page == 1:
    page_1()
    if st.button("Next"):
        go_to_page(2)
elif st.session_state.current_page == 2:
    page_2()
    if st.button("Next"):
        go_to_page(3)
elif st.session_state.current_page == 3:
    page_3()
    if st.button("Next"):
        go_to_page(4)
elif st.session_state.current_page == 4:
    page_4()
    if st.button("Next"):
        go_to_page(5)
elif st.session_state.current_page == 5:
    page_5()
    if st.button("Restart"):
        go_to_page(1)

# Close section
st.markdown('</section>', unsafe_allow_html=True)