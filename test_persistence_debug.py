"""
Debug script to check persistence layer.

This script helps diagnose why tiles, progress, and module state aren't persisting.
"""

import json
from pathlib import Path

# Load the user's saved file
user_file = Path(".session_store/user_anon_6611127117e7.json")

if user_file.exists():
    with open(user_file, 'r') as f:
        data = json.load(f)
    
    print("=== USER FILE CONTENTS ===")
    print(json.dumps(data, indent=2))
    print()
    
    print("=== CHECKING PERSISTENCE KEYS ===")
    expected_keys = ['profile', 'progress', 'mcip_contracts', 'tiles', 'preferences', 'auth', 'flags']
    
    for key in expected_keys:
        if key in data:
            print(f"✅ {key}: {type(data[key]).__name__} with {len(data[key]) if isinstance(data[key], (dict, list)) else 'N/A'} items")
        else:
            print(f"❌ {key}: MISSING")
    
    print()
    print("=== CHECKING MCIP CONTRACTS ===")
    if 'mcip_contracts' in data and data['mcip_contracts']:
        contracts = data['mcip_contracts']
        print(f"Care Recommendation: {'✅ Present' if contracts.get('care_recommendation') else '❌ Missing'}")
        print(f"Financial Profile: {'✅ Present' if contracts.get('financial_profile') else '❌ Missing'}")
        print(f"Advisor Appointment: {'✅ Present' if contracts.get('advisor_appointment') else '❌ Missing'}")
        print(f"Journey: {'✅ Present' if contracts.get('journey') else '❌ Missing'}")
        
        if contracts.get('care_recommendation'):
            rec = contracts['care_recommendation']
            print(f"\nCare Recommendation Details:")
            print(f"  Tier: {rec.get('tier')}")
            print(f"  Status: {rec.get('status')}")
            print(f"  Confidence: {rec.get('confidence')}")
    else:
        print("❌ mcip_contracts is empty or missing")
    
    print()
    print("=== CHECKING TILES ===")
    if 'tiles' in data and data['tiles']:
        tiles = data['tiles']
        for product_key, tile_state in tiles.items():
            print(f"{product_key}:")
            print(f"  Progress: {tile_state.get('progress', 0)}%")
            print(f"  Status: {tile_state.get('status', 'new')}")
            print(f"  Last Step: {tile_state.get('last_step', 'N/A')}")
    else:
        print("❌ tiles is empty or missing")
    
    print()
    print("=== CHECKING PROGRESS ===")
    if 'progress' in data and data['progress']:
        progress = data['progress']
        print(f"Progress entries: {list(progress.keys())}")
    else:
        print("❌ progress is empty or missing")
    
    print()
    print("=== CHECKING SESSION STATE KEYS ===")
    print(f"Total keys in file: {len(data)}")
    print(f"Keys present: {list(data.keys())}")

else:
    print(f"❌ User file not found: {user_file}")
    print()
    print("Checking for any session files...")
    session_dir = Path(".session_store")
    if session_dir.exists():
        files = list(session_dir.glob("*.json"))
        print(f"Found {len(files)} session files:")
        for f in files:
            print(f"  - {f.name}")
    else:
        print("❌ .session_store directory doesn't exist")
