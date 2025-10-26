"""AI Advisor product - RAG-powered Q&A using corporate content corpus."""

import streamlit as st
from products.global.ai.advisor_service import get_answer


def describe():
    """Product metadata."""
    return {
        "name": "AI Advisor",
        "capabilities": ["rag", "chat_ui", "corporate_content", "faq_fallback"],
        "version": "2.0.0",
        "hub": "concierge"
    }


def render():
    """Render AI Advisor chat interface with RAG-first answers."""
    
    st.markdown("### 💬 Ask Navi")
    st.markdown(
        "Ask about assisted living, memory care, cost planning, or any senior care topic. "
        "I'll search our comprehensive knowledge base to help you."
    )
    
    # Initialize chat history
    if "advisor_history" not in st.session_state:
        st.session_state.advisor_history = []
    
    # Display chat history
    for msg in st.session_state.advisor_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        mode = msg.get("mode")
        sources = msg.get("sources", [])
        
        if role == "user":
            st.chat_message("user").markdown(content)
        else:
            with st.chat_message("assistant"):
                st.markdown(content)
                
                # Show mode badge for transparency
                if mode:
                    mode_label = {
                        "rag": "📚 Knowledge Base",
                        "faq": "❓ FAQ",
                        "suggest": "💡 Suggestion",
                        "error": "⚠️ Error"
                    }.get(mode, mode)
                    st.caption(f"*Source: {mode_label}*")
                
                # Show sources if available
                if sources:
                    with st.expander("📖 Sources", expanded=False):
                        for src in sources:
                            title = src.get("title", "Source")
                            url = src.get("url", "")
                            if url:
                                st.markdown(f"- [{title}]({url})")
                            else:
                                st.markdown(f"- {title}")
    
    # Chat input
    question = st.chat_input("Ask your question here...")
    
    if question:
        # Add user message to history
        st.session_state.advisor_history.append({
            "role": "user",
            "content": question
        })
        
        # Get answer from advisor service
        with st.spinner("Searching knowledge base..."):
            response = get_answer(
                question=question,
                name=st.session_state.get("person_name"),
                source="auto"  # Try corp first, then FAQ
            )
        
        # Extract response data
        answer = response.get("answer", "I couldn't generate an answer.")
        mode = response.get("mode", "unknown")
        sources = response.get("sources", [])
        cta = response.get("cta")
        meta = response.get("meta", {})
        
        # Add assistant response to history
        st.session_state.advisor_history.append({
            "role": "assistant",
            "content": answer,
            "mode": mode,
            "sources": sources,
            "cta": cta,
            "meta": meta
        })
        
        # Rerun to show new messages
        st.rerun()
