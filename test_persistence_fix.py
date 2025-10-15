#!/usr/bin/env python3
"""
Test script to verify persistence fix works correctly.

Run this AFTER starting the app and completing at least one GCP question:
1. streamlit run app.py
2. Navigate to GCP, answer ONE question
3. Navigate away (to welcome or another page)
4. Run this script: python test_persistence_fix.py
5. Should show tiles with progress data

Expected output:
- tiles dict should NOT be empty
- Should show gcp_v4 key with progress/status
- progress dict should show module progress
"""

import json
from pathlib import Path

# Find user files
data_dir = Path("data/users")
if not data_dir.exists():
    print("❌ data/users/ directory not found!")
    exit(1)

user_files = list(data_dir.glob("anon_*.json"))
if not user_files:
    print("❌ No user files found in data/users/")
    exit(1)

print(f"Found {len(user_files)} user file(s)\n")

# Check most recent file
latest_file = max(user_files, key=lambda f: f.stat().st_mtime)
print(f"📁 Most recent file: {latest_file.name}")
print(f"⏰ Last modified: {latest_file.stat().st_mtime}\n")

with open(latest_file) as f:
    data = json.load(f)

print("=" * 60)
print("PERSISTENCE DATA CHECK")
print("=" * 60)

# Check tiles
tiles = data.get("tiles", {})
print(f"\n🎯 tiles: {len(tiles)} product(s)")
if tiles:
    for product_key, tile_state in tiles.items():
        print(f"  ✅ {product_key}:")
        print(f"     - progress: {tile_state.get('progress', 'N/A')}")
        print(f"     - status: {tile_state.get('status', 'N/A')}")
        print(f"     - last_step: {tile_state.get('last_step', 'N/A')}")
else:
    print("  ❌ EMPTY - No tile data saved!")

# Check progress
progress = data.get("progress", {})
print(f"\n📊 progress: {len(progress)} module(s)")
if progress:
    for module_key, module_progress in progress.items():
        print(f"  ✅ {module_key}: {module_progress}")
else:
    print("  ❌ EMPTY - No progress data saved!")

# Check mcip_contracts
mcip_contracts = data.get("mcip_contracts", {})
print(f"\n📋 mcip_contracts: {len(mcip_contracts)} contract(s)")
if mcip_contracts:
    for contract_key, contract_data in mcip_contracts.items():
        print(f"  ✅ {contract_key}:")
        if isinstance(contract_data, dict):
            print(f"     - keys: {list(contract_data.keys())}")
        else:
            print(f"     - value: {contract_data}")
else:
    print("  ⚠️  EMPTY - No MCIP contracts saved (OK if GCP not completed)")

# Check profile
profile = data.get("profile", {})
print(f"\n👤 profile: {len(profile)} field(s)")
if profile:
    print(f"  ✅ {list(profile.keys())}")
else:
    print("  ⚠️  EMPTY (OK if user hasn't entered profile data)")

# Check preferences
preferences = data.get("preferences", {})
print(f"\n⚙️  preferences: {len(preferences)} setting(s)")
if preferences:
    print(f"  ✅ {list(preferences.keys())}")
else:
    print("  ⚠️  EMPTY (OK if user hasn't set preferences)")

print("\n" + "=" * 60)
print("VERDICT")
print("=" * 60)

if tiles or progress:
    print("✅ SUCCESS - Persistence is working!")
    print("   Tiles or progress data was saved successfully.")
else:
    print("❌ FAILED - Persistence still broken!")
    print("   No tiles or progress data found.")
    print("\n   Troubleshooting:")
    print("   1. Did you complete at least ONE GCP question?")
    print("   2. Did you navigate AWAY from GCP (to trigger save)?")
    print("   3. Check console logs in Streamlit for errors")

print("\n📝 Full file contents:")
print(json.dumps(data, indent=2))
