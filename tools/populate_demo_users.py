#!/usr/bin/env python3
"""
Populate demo_users.jsonl from existing demo user data in data/users/demo/

This script scans the demo user directories and creates CRM-compatible
demo user records in the demo_users.jsonl file.
"""

import json
import os
from pathlib import Path
from datetime import datetime

def load_demo_user(demo_dir: Path) -> dict:
    """Load demo user data from directory"""
    user_data = {
        'user_id': demo_dir.name,
        'source': 'demo',
        'customer_type': 'demo_user',
        'created_at': datetime.now().isoformat()
    }
    
    # Try to load session.json
    session_file = demo_dir / "session.json"
    if session_file.exists():
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            user_data['person_name'] = session_data.get('person_name', 
                                      session_data.get('planning_for_name',
                                                     demo_dir.name.replace('demo_', '').replace('_', ' ').title()))
            user_data['relationship_type'] = session_data.get('relationship_type', 'Demo')
            user_data['journey_stage'] = 'Demo User'
            
            # Add any other relevant session data
            if 'email' in session_data:
                user_data['email'] = session_data['email']
            if 'phone' in session_data:
                user_data['phone'] = session_data['phone']
        except Exception as e:
            print(f"Error loading session for {demo_dir.name}: {e}")
    
    # Check for assessment files
    if (demo_dir / "careplan.json").exists():
        user_data['has_gcp_assessment'] = True
        try:
            with open(demo_dir / "careplan.json", 'r') as f:
                careplan = json.load(f)
                user_data['care_recommendation'] = careplan.get('recommendation', 'Unknown')
        except:
            pass
    
    if (demo_dir / "costplan.json").exists():
        user_data['has_cost_plan'] = True
        try:
            with open(demo_dir / "costplan.json", 'r') as f:
                costplan = json.load(f)
                user_data['monthly_cost_estimate'] = costplan.get('estimated_cost', 0)
        except:
            pass
    
    user_data['last_activity'] = datetime.now().strftime('%Y-%m-%d')
    user_data['last_activity_days'] = 0
    
    return user_data

def main():
    """Main function to populate demo_users.jsonl"""
    # Find the data root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "data"
    demo_users_dir = data_dir / "users" / "demo"
    crm_dir = data_dir / "crm"
    
    if not demo_users_dir.exists():
        print(f"Demo users directory not found: {demo_users_dir}")
        return
    
    # Create CRM directory if it doesn't exist
    crm_dir.mkdir(parents=True, exist_ok=True)
    
    # Load all demo users
    demo_users = []
    for demo_dir in demo_users_dir.iterdir():
        if demo_dir.is_dir():
            try:
                user_data = load_demo_user(demo_dir)
                demo_users.append(user_data)
                print(f"Loaded demo user: {user_data.get('person_name', demo_dir.name)}")
            except Exception as e:
                print(f"Error processing {demo_dir}: {e}")
    
    if not demo_users:
        print("No demo users found")
        return
    
    # Write to demo_users.jsonl
    output_file = crm_dir / "demo_users.jsonl"
    with open(output_file, 'w') as f:
        for user in demo_users:
            f.write(json.dumps(user, ensure_ascii=False) + '\n')
    
    print(f"\n✅ Successfully wrote {len(demo_users)} demo users to {output_file}")
    
    # Show summary
    print("\nDemo Users Summary:")
    for user in demo_users:
        name = user.get('person_name', user.get('user_id'))
        gcp = '✓' if user.get('has_gcp_assessment') else '✗'
        cost = '✓' if user.get('has_cost_plan') else '✗'
        print(f"  • {name} | GCP: {gcp} | Cost: {cost}")

if __name__ == "__main__":
    main()
