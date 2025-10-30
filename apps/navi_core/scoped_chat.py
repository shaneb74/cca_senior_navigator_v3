"""
Scoped NAVI Chat - Topic-constrained chat interface

Phase 5B: NAVI chat that only answers questions within a specific topic scope.
Used by learning_template.py to provide focused guidance without straying off-topic.

Features:
- Topic-specific context window
- Gentle redirection for out-of-scope questions
- Session-based chat history per topic
- Integration with NAVI LLM engine
"""

import streamlit as st
from typing import Optional

from ai.navi_llm_engine import NaviLLMEngine, NaviContext
from ai.llm_client import get_client
from core.flags import get_flag_value


class ScopedNaviChat:
    """A NAVI chat interface restricted to a single learning topic.
    
    Phase 5B: Provides focused, on-topic guidance for learning tiles.
    
    Args:
        topic_scope: Topic identifier (e.g., "senior_navigator_overview")
        max_history: Maximum chat history entries to retain (default: 10)
        
    Examples:
        >>> chat = ScopedNaviChat(topic_scope="care_recommendation_explainer")
        >>> chat.render()
        # Displays chat interface with topic-scoped responses
    """
    
    def __init__(self, topic_scope: str, max_history: int = 10):
        self.topic_scope = topic_scope
        self.max_history = max_history
        self.history_key = f"navi_chat_history_{topic_scope}"
        
        # Initialize chat history for this topic
        if self.history_key not in st.session_state:
            st.session_state[self.history_key] = []
    
    def render(self) -> None:
        """Render the scoped chat interface.
        
        Displays chat history and input field. Processes user messages and
        generates topic-scoped NAVI responses.
        """
        # Display chat history
        history = st.session_state[self.history_key]
        
        if history:
            for message in history:
                role = message.get("role", "user")
                content = message.get("content", "")
                
                if role == "user":
                    with st.chat_message("user"):
                        st.markdown(content)
                elif role == "assistant":
                    with st.chat_message("assistant", avatar="🧭"):
                        st.markdown(content)
        else:
            # Show welcome message if no history
            with st.chat_message("assistant", avatar="🧭"):
                st.markdown(
                    f"👋 Hi! I'm NAVI. Ask me anything about "
                    f"**{self.topic_scope.replace('_', ' ').title()}**. "
                    f"I'm here to help you understand this topic better!"
                )
        
        # Chat input
        prompt = st.chat_input(
            f"Ask NAVI about {self.topic_scope.replace('_', ' ')}...",
            key=f"chat_input_{self.topic_scope}"
        )
        
        if prompt:
            # Add user message to history
            self._add_to_history("user", prompt)
            
            # Display user message immediately
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate and display response
            with st.chat_message("assistant", avatar="🧭"):
                with st.spinner("NAVI is thinking..."):
                    response = self._query_llm(prompt)
                    st.markdown(response)
            
            # Add assistant response to history
            self._add_to_history("assistant", response)
            
            # Rerun to update UI
            st.rerun()
    
    def _query_llm(self, user_prompt: str) -> str:
        """Query the NAVI LLM with topic-scoped context.
        
        Args:
            user_prompt: User's question or message
            
        Returns:
            str: NAVI's response constrained to topic scope
        """
        # Check if LLM features are enabled
        llm_mode = get_flag_value("FEATURE_LLM_NAVI", "off")
        if llm_mode == "off":
            return self._get_fallback_response(user_prompt)
        
        try:
            client = get_client()
            if not client:
                return self._get_fallback_response(user_prompt)
            
            # Build topic-scoped system prompt
            system_prompt = self._build_system_prompt()
            
            # Build user prompt with context
            full_prompt = self._build_user_prompt(user_prompt)
            
            # Generate response
            response_text = client.generate_completion(
                system_prompt=system_prompt,
                user_prompt=full_prompt,
                max_tokens=300,
            )
            
            return response_text or self._get_fallback_response(user_prompt)
            
        except Exception as e:
            print(f"[SCOPED_NAVI] LLM query failed: {e}")
            return self._get_fallback_response(user_prompt)
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with topic scope constraints.
        
        Returns:
            str: System prompt for LLM
        """
        topic_display = self.topic_scope.replace("_", " ").title()
        
        return f"""You are NAVI, the Senior Navigator assistant. You are helping a user learn about a specific topic.

**TOPIC SCOPE:** {topic_display}

**YOUR ROLE:**
- Answer questions ONLY about {topic_display}
- Be warm, encouraging, and supportive
- Keep responses clear and actionable
- If the user asks about something outside this topic, gently redirect them:
  "That's a great question, but it's outside our current topic of {topic_display}. 
  Let me help you with that in the main Senior Navigator experience!"

**RESPONSE GUIDELINES:**
- Keep responses under 200 words
- Use bullet points for clarity when appropriate
- Be empathetic and understanding
- Avoid medical advice or guarantees
- Use "you" and "your" to be personal

Stay focused on {topic_display} and provide helpful, actionable guidance."""
    
    def _build_user_prompt(self, user_message: str) -> str:
        """Build user prompt with chat history context.
        
        Args:
            user_message: Current user message
            
        Returns:
            str: Formatted user prompt with context
        """
        # Get recent history (last 3 exchanges)
        history = st.session_state[self.history_key]
        recent_history = history[-6:] if len(history) > 6 else history
        
        # Format history
        history_text = ""
        if recent_history:
            history_text = "\n\nPrevious conversation:\n"
            for msg in recent_history:
                role = "User" if msg["role"] == "user" else "NAVI"
                history_text += f"{role}: {msg['content']}\n"
        
        return f"{history_text}\n\nUser's current question: {user_message}"
    
    def _get_fallback_response(self, user_prompt: str) -> str:
        """Generate a fallback response when LLM is unavailable.
        
        Args:
            user_prompt: User's message
            
        Returns:
            str: Fallback response message
        """
        topic_display = self.topic_scope.replace("_", " ").title()
        
        return (
            f"Thank you for your question about {topic_display}! "
            f"I'm currently in learning mode and can provide general guidance. "
            f"\n\nFor detailed, personalized answers, please visit the main NAVI chat "
            f"in the Lobby or reach out to your Care Advisor."
        )
    
    def _add_to_history(self, role: str, content: str) -> None:
        """Add a message to chat history.
        
        Args:
            role: Message role ("user" or "assistant")
            content: Message content
        """
        history = st.session_state[self.history_key]
        history.append({"role": role, "content": content})
        
        # Trim history if too long
        if len(history) > self.max_history * 2:  # *2 because each exchange is 2 messages
            st.session_state[self.history_key] = history[-self.max_history * 2:]
    
    def clear_history(self) -> None:
        """Clear the chat history for this topic."""
        st.session_state[self.history_key] = []


def render_scoped_chat(topic_scope: str) -> None:
    """Convenience function to render a scoped chat.
    
    Args:
        topic_scope: Topic identifier for scoping
        
    Example:
        >>> render_scoped_chat("senior_navigator_overview")
    """
    chat = ScopedNaviChat(topic_scope=topic_scope)
    chat.render()
