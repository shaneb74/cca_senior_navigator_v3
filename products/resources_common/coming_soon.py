# products/resources_common/coming_soon.py
"""
Coming Soon Module - Generic placeholder for resources under development

This module provides a consistent "Coming Soon" experience for all resource
modules that haven't been fully implemented yet. It follows the same header,
layout, and navigation structure as other modules.
"""

import streamlit as st

from ui.product_shell import product_shell_end, product_shell_start


def render_coming_soon(product_key: str, product_title: str, product_desc: str):
    """Render the Coming Soon module.

    Args:
        product_key: The product identifier (e.g., 'fall_risk')
        product_title: Display title (e.g., 'Fall Risk')
        product_desc: Brief description of what this resource will offer
    """
    product_shell_start()

    st.markdown(f"# {product_title}")
    st.markdown("---")

    # Coming Soon banner
    st.info(f"""
    ### 🚧 Coming Soon
    
    **{product_title}** is currently under development and will be available soon.
    
    {product_desc}
    
    We're working hard to bring you this valuable resource. Check back soon for updates!
    """)

    st.markdown("---")

    # Placeholder content section
    st.markdown("### What to Expect")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **When this module is ready, you'll be able to:**
        - Access comprehensive information and guidance
        - Use interactive tools and assessments
        - Get personalized recommendations
        - Save your progress and return anytime
        """)

    with col2:
        st.markdown("""
        **Features in development:**
        - Step-by-step questionnaires
        - Expert-curated content
        - Downloadable resources
        - Integration with your care plan
        """)

    st.markdown("---")

    # Navigation options
    st.markdown("### What You Can Do Now")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("← Back to Resources Hub", use_container_width=True):
            from core.nav import route_to

            route_to("hub_resources")

    with col2:
        if st.button("🏠 Go to Concierge Hub", use_container_width=True):
            from core.nav import route_to

            route_to("hub_concierge")

    with col3:
        if st.button("❓ FAQs & Support", use_container_width=True):
            from core.nav import route_to

            route_to("faq")

    # Feedback section
    st.markdown("---")

    with st.expander("💬 Interested in this resource? Let us know!"):
        st.markdown("""
        We'd love to hear from you! Your feedback helps us prioritize which resources to develop first.
        
        **What would be most helpful to you?**
        """)

        feedback = st.text_area(
            "Share your thoughts (optional)",
            placeholder="What information or tools would you find most valuable?",
            key=f"feedback_{product_key}",
        )

        if st.button("Submit Feedback", key=f"submit_{product_key}"):
            if feedback:
                # Store feedback in session state (in production, this would go to a database)
                if "resource_feedback" not in st.session_state:
                    st.session_state.resource_feedback = []

                st.session_state.resource_feedback.append(
                    {"product": product_key, "feedback": feedback}
                )

                st.success("Thank you for your feedback! We'll use this to improve our resources.")
            else:
                st.info("Please share your thoughts before submitting.")

    product_shell_end()
