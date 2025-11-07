#!/usr/bin/env python3
"""
Test script to verify QuickBase advisor fetching
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.data_access.quickbase_client import quickbase_client

def main():
    print("=" * 80)
    print("Testing QuickBase Active Advisors API")
    print("=" * 80)
    print()
    
    print("Fetching active advisors from QuickBase WA Clients table...")
    advisors = quickbase_client.get_active_advisors()
    
    print(f"\n✅ Successfully retrieved {len(advisors)} active advisors\n")
    print("=" * 80)
    print(f"{'#':<4} {'Name':<42} {'Email':<35}")
    print("=" * 80)
    
    for i, advisor in enumerate(advisors, 1):
        print(f"{i:<4} {advisor['name']:<42} {advisor['email']:<35}")
    
    print("=" * 80)
    print()
    
    # Show sample advisor details
    if advisors:
        print("Sample Advisor Record:")
        print("-" * 80)
        sample = advisors[0]
        for key, value in sample.items():
            print(f"  {key:15}: {value}")
        print()

if __name__ == "__main__":
    main()
