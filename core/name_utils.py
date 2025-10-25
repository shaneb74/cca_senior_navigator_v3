"""
Name utilities for personalizing the Senior Navigator experience.

Provides consistent name handling across the application for titles, questions,
and LLM responses. Gracefully falls back to second person when no name is available.
"""

import re
import streamlit as st
from typing import Optional


def first_name(full_name: Optional[str]) -> str:
    """
    Extract the first name from a full name string.
    
    Args:
        full_name: The person's full name
        
    Returns:
        The first token of the name, trimmed to 20 characters max.
        Returns empty string if full_name is None or empty.
    """
    if not full_name or not full_name.strip():
        return ""
    
    # Split on whitespace and take first token
    try:
        tokens = full_name.strip().split()
        if tokens:
            # Trim to 20 characters for very long names
            return tokens[0][:20]
    except Exception:
        # Non-Latin safe fallback - return original if tokenization fails
        return full_name.strip()[:20]
    
    return ""


def possessive(name: str) -> str:
    """
    Create possessive form of a name.
    
    Args:
        name: The person's name
        
    Returns:
        Possessive form: "James's" for most names, "James'" for names ending in 's'
        if using AP style (currently using standard style).
    """
    if not name or not name.strip():
        return ""
    
    name = name.strip()
    
    # Standard possessive rules (not AP style)
    # Add 's to all names, even those ending in s
    return f"{name}'s"


def pname(default: str = "you") -> str:
    """
    Get the person's first name from session state, with fallback.
    
    Args:
        default: Default value if no name is available
        
    Returns:
        First name if available, otherwise the default value
    """
    if hasattr(st, 'session_state') and 'person_a_name' in st.session_state:
        name = first_name(st.session_state.get('person_a_name'))
        if name:
            return name
    
    return default


def pname_possessive(default: str = "your") -> str:
    """
    Get the person's possessive name from session state, with fallback.
    
    Args:
        default: Default value if no name is available (e.g., "your")
        
    Returns:
        Possessive name if available, otherwise the default value
    """
    name = pname("")
    if name:
        return possessive(name)
    return default


def titlecase(text: str) -> str:
    """
    Convert text to title case for headers.
    
    Args:
        text: Text to convert
        
    Returns:
        Title-cased text
    """
    if not text:
        return ""
    return text.title()


def personalize(template: str, person_name: Optional[str] = None) -> str:
    """
    Replace name tokens in a template string with personalized values.
    
    Token replacements:
    - {NAME} → first name or "you"
    - {NAME_POS} → possessive form or "your"
    - {NAME_UPPER} → uppercase first name or "YOU"
    - {NAME_TITLE} → title-cased first name or "You"
    
    Args:
        template: Template string with tokens to replace
        person_name: Optional override for person's name (uses session state if not provided)
        
    Returns:
        Template with tokens replaced
    """
    if not template:
        return ""
    
    # Get name from parameter or session state
    if person_name is not None:
        name = first_name(person_name)
    else:
        name = pname("")
    
    # Set up replacements
    if name:
        replacements = {
            '{NAME}': name,
            '{NAME_POS}': possessive(name),
            '{NAME_UPPER}': name.upper(),
            '{NAME_TITLE}': titlecase(name)
        }
    else:
        # Fallback to second person
        replacements = {
            '{NAME}': 'you',
            '{NAME_POS}': 'your',
            '{NAME_UPPER}': 'YOU',
            '{NAME_TITLE}': 'You'
        }
    
    # Apply replacements
    result = template
    for token, replacement in replacements.items():
        result = result.replace(token, replacement)
    
    return result


def get_person_context() -> dict:
    """
    Get person context for LLM prompts and templates.
    
    Returns:
        Dictionary with person context including:
        - person_first_name: First name or "you"
        - person_possessive: Possessive form or "your"
        - relationship_type: From session state
        - planning_for_self: Boolean indicating if planning for self
    """
    name = pname("")
    relationship = st.session_state.get('relationship_type', 'Myself') if hasattr(st, 'session_state') else 'Myself'
    
    return {
        'person_first_name': name if name else "you",
        'person_possessive': possessive(name) if name else "your",
        'person_full_name': st.session_state.get('person_a_name', '') if hasattr(st, 'session_state') else '',
        'relationship_type': relationship,
        'planning_for_self': relationship == 'Myself'
    }


# Convenience functions for common patterns
def page_title(base_title: str) -> str:
    """Create personalized page title: 'About You' → 'About {NAME}'"""
    return personalize(base_title.replace('You', '{NAME_TITLE}').replace('Your', '{NAME_POS}'))


def section_header(base_header: str) -> str:
    """Create personalized section header with possessive: 'Medical & Care' → '{NAME_POS} Medical & Care'"""
    # Common patterns to personalize
    if 'Medical' in base_header and not '{NAME_POS}' in base_header:
        return personalize(f"{{NAME_POS}} {base_header}")
    elif 'Housing' in base_header and not '{NAME_POS}' in base_header:
        return personalize(f"{{NAME_POS}} {base_header}")
    elif 'Financial' in base_header and not '{NAME_POS}' in base_header:
        return personalize(f"{{NAME_POS}} {base_header}")
    else:
        return personalize(base_header)


def question_stem(base_question: str) -> str:
    """Create personalized question: 'Tell us about mood changes' → 'Tell us about {NAME_POS} moods'"""
    return personalize(base_question)


def help_text(base_text: str) -> str:
    """Create personalized help text: 'This will help us...' → 'This will help us tailor {NAME_POS} care plan.'"""
    return personalize(base_text)