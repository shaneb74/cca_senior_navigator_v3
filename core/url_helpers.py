"""
URL Helpers for Session Preservation

Provides utilities to add UID to hrefs to preserve session across navigation.
Critical for maintaining user state when using href links (which reload the page).
"""

import streamlit as st


def add_uid_to_href(href: str) -> str:
    """Add current UID to href to preserve session across navigation.
    
    Args:
        href: Original href string (e.g., "?page=faqs" or "?page=hub&foo=bar")
        
    Returns:
        href with uid appended (e.g., "?page=faqs&uid=anon_xxxxx")
    """
    if not href or href == "#" or href.startswith("http"):
        return href
    
    # Get current UID from session_state
    uid = None
    if 'anonymous_uid' in st.session_state:
        uid = st.session_state['anonymous_uid']
    elif 'auth' in st.session_state and st.session_state['auth'].get('user_id'):
        uid = st.session_state['auth']['user_id']
    
    if not uid:
        return href
    
    # Add uid to query string
    separator = '&' if '?' in href else '?'
    return f"{href}{separator}uid={uid}"
