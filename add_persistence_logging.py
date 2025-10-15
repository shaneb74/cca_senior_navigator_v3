#!/usr/bin/env python3
"""
Add debug logging to see when persistence saves happen.

This patches session_store.py to add console logging for debugging.
Run this once, then use the app normally to see logs.

To restore original (remove logging):
  git checkout core/session_store.py
"""

import re
from pathlib import Path

session_store_path = Path("core/session_store.py")

if not session_store_path.exists():
    print("❌ core/session_store.py not found!")
    exit(1)

content = session_store_path.read_text()

# Check if already patched
if "DEBUG LOGGING" in content:
    print("⚠️  Already patched! Run `git checkout core/session_store.py` to restore.")
    exit(0)

# Add logging to safe_rerun
patch = """def safe_rerun():
    \"\"\"
    Save session state before rerunning to prevent data loss.
    
    ALWAYS use this instead of st.rerun() to ensure persistence works correctly.
    
    Streamlit's st.rerun() clears session_state changes made during the render,
    so we must save to disk before rerunning.
    \"\"\"
    import streamlit as st
    
    # DEBUG LOGGING
    print("\\n" + "="*60)
    print("🔄 safe_rerun() called - saving state before rerun")
    print("="*60)
    
    # Save user data (persistent across sessions)
    uid = get_or_create_user_id(st.session_state)
    user_data = extract_user_state(st.session_state)
    
    # DEBUG: Show what we're saving
    print(f"👤 User ID: {uid}")
    print(f"💾 Saving user data keys: {list(user_data.keys())}")
    for key, value in user_data.items():
        if isinstance(value, dict):
            print(f"   - {key}: {len(value)} items")
            if value:  # Show first level keys if not empty
                print(f"     Keys: {list(value.keys())}")
        elif isinstance(value, list):
            print(f"   - {key}: {len(value)} items")
        else:
            print(f"   - {key}: {type(value).__name__}")
    
    if user_data:
        save_user(uid, user_data)
        print(f"✅ User data saved to data/users/{uid}.json")
    else:
        print("⚠️  No user data to save (all keys empty)")
    
    # Save session data (browser-specific, temporary)
    if 'session_id' in st.session_state:
        session_data = extract_session_state(st.session_state)
        print(f"📱 Session data keys: {list(session_data.keys())}")
        if session_data:
            save_session(st.session_state['session_id'], session_data)
            print(f"✅ Session data saved")
    
    print("="*60 + "\\n")
    
    # Now safe to rerun
    st.rerun()"""

# Replace the function
content = re.sub(
    r'def safe_rerun\(\):.*?st\.rerun\(\)',
    patch,
    content,
    flags=re.DOTALL
)

session_store_path.write_text(content)

print("✅ Debug logging added to core/session_store.py")
print("\nNow run your app and watch the console for:")
print("  🔄 safe_rerun() called - saving state before rerun")
print("  👤 User ID: anon_...")
print("  💾 Saving user data keys: ['tiles', 'progress', ...]")
print("\nTo remove logging: git checkout core/session_store.py")
