"""Test GCP state persistence across navigation.

Run this to verify:
1. GCP state is written to st.session_state["gcp"]
2. State is persisted to disk via session_store
3. State is loaded back when navigating to Cost Planner

Usage:
    streamlit run app.py
    Complete GCP → navigate to Cost Planner → check logs
"""

import json
import os


def check_user_data_files():
    """Check if user data files are being created correctly."""
    users_dir = "data/users"

    if not os.path.exists(users_dir):
        print(f"❌ {users_dir} does not exist!")
        return

    # List all files
    files = []
    for item in os.listdir(users_dir):
        path = os.path.join(users_dir, item)
        if os.path.isfile(path) and item.endswith(".json"):
            files.append(item)

    print(f"\n{'='*80}")
    print(f"User Data Files in {users_dir}")
    print(f"{'='*80}")
    print(f"Total JSON files: {len(files)}\n")

    # Show most recent 5
    files.sort(reverse=True)
    for f in files[:5]:
        print(f"  {f}")

    # Check for latest file content
    if files:
        latest = files[0]
        latest_path = os.path.join(users_dir, latest)
        print(f"\nLatest file: {latest}")
        print("Content preview:")
        with open(latest_path) as fp:
            data = json.load(fp)
            # Show GCP-related keys
            if "gcp" in data:
                print("  ✅ Has 'gcp' key")
                gcp = data["gcp"]
                print(f"     published_tier: {gcp.get('published_tier')}")
                print(f"     allowed_tiers: {gcp.get('allowed_tiers')}")
            else:
                print("  ❌ No 'gcp' key found")

            # Show all top-level keys
            print(f"  Top-level keys: {list(data.keys())}")

    print(f"{'='*80}\n")


if __name__ == "__main__":
    check_user_data_files()
