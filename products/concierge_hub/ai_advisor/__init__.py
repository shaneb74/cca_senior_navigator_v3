"""AI Advisor product wrapper - delegates to pages.faq for FAQ/chat interface."""
from pages.faq import render as render

def describe():
    return {
        "name": "AI Advisor",
        "capabilities": ["chat_ui", "faq", "canonical_questions"],
        "version": "1.0.0",
        "hub": "concierge"
    }
