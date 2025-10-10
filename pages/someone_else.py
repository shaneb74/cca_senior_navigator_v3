import streamlit as st
from core.nav import route_to
from core.ui import img_src

def render():
    # Set page config
    st.set_page_config(page_title="Concierge Care Senior Navigator", layout="wide")

    # Header
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("https://via.placeholder.com/150x50.png?text=Concierge+Care+Senior+Navigator", width=150)
    with col2:
        st.write('<div style="text-align: right; padding: 10px;"><a href="#" style="padding: 10px; text-decoration: none; color: #3B82F6;">Log in or sign up</a></div>', unsafe_allow_html=True)

    # Background and main content
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #e6f0fa;
        }
        .card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            max-width: 400px;
            margin: 20px auto;
        }
        .image-container {
            position: absolute;
            top: 100px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            justify-content: space-around;
            width: 80%;
            z-index: 1;
        }
        .image {
            width: 200px;
            height: 200px;
            background-color: #d3e0ea;
            margin: 10px;
            border: 10px solid white;
            border-radius: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Card content
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("For someone", key="for_someone"):
                pass  # Already on this page
            if st.button("For me", key="for_me"):
                route_to("for_me_contextual")
        with col2:
            st.write("Supporting Others")
            st.write("Helping you make confident care decisions for someone you love.")
            name_input = st.text_input("What's their name?")
            if st.button("Continue"):
                st.session_state["person_name"] = name_input
                route_to("hub_concierge")
            st.write("If you want to assess several people, you can move on to the next step later.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Placeholder for images
    st.markdown('<div class="image-container">', unsafe_allow_html=True)
    photo_back = img_src("static/images/contextual_someone_else.png")
    photo_front = img_src("static/images/tell_us_about_them.png")
    st.markdown(f'<div class="image"><img src="{photo_back}" style="width: 100%; height: 100%; object-fit: cover;"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="image"><img src="{photo_front}" style="width: 100%; height: 100%; object-fit: cover;"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="image"><img src="{photo_back}" style="width: 100%; height: 100%; object-fit: cover;"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="image"><img src="{photo_front}" style="width: 100%; height: 100%; object-fit: cover;"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)