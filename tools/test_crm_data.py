#!/usr/bin/env python3
"""
Quick test to verify CRM data loading is working correctly
"""

import json
from pathlib import Path

def load_all_crm_data():
    """Load CRM data directly without Streamlit dependency"""
    project_root = Path(__file__).parent.parent
    crm_dir = project_root / "data" / "crm"
    
    customers = []
    
    # Load Navigator app customers
    customers_file = crm_dir / "customers.jsonl"
    if customers_file.exists():
        with open(customers_file, 'r') as f:
            for line in f:
                if line.strip():
                    customer = json.loads(line)
                    customer['source'] = 'navigator_app'
                    customers.append(customer)
    
    # Load QuickBase customers
    qb_file = crm_dir / "synthetic_august2025_summary.json"
    if qb_file.exists():
        with open(qb_file, 'r') as f:
            qb_data = json.load(f)
            for customer in qb_data.get('customers', []):
                customer['source'] = 'quickbase'
                customers.append(customer)
    
    # Load demo users
    demo_file = crm_dir / "demo_users.jsonl"
    if demo_file.exists():
        with open(demo_file, 'r') as f:
            for line in f:
                if line.strip():
                    customer = json.loads(line)
                    customer['source'] = 'demo'
                    customers.append(customer)
    
    return customers

def main():
    print("=" * 60)
    print("CRM Data Loading Test")
    print("=" * 60)
    
    customers = load_all_crm_data()
    
    print(f"\n✅ Total Customers Loaded: {len(customers)}")
    
    # Group by source
    by_source = {}
    for customer in customers:
        source = customer.get('source', 'unknown')
        by_source[source] = by_source.get(source, 0) + 1
    
    print("\n📊 Customers by Source:")
    for source, count in sorted(by_source.items()):
        print(f"   • {source}: {count}")
    
    print("\n👥 Customer Details:")
    print("-" * 60)
    
    for i, customer in enumerate(customers[:15], 1):  # Show first 15
        source = customer.get('source', 'unknown')
        name = customer.get('name', customer.get('person_name', 'Unknown'))
        user_id = customer.get('id', customer.get('user_id', customer.get('customer_id', 'N/A')))
        
        # Source emoji
        emoji = {
            'quickbase': '🔵',
            'navigator_app': '🟢',
            'demo': '🟣'
        }.get(source, '⚪')
        
        print(f"{i:2}. {emoji} {name:<30} [{source:<15}] ID: {user_id}")
    
    if len(customers) > 15:
        print(f"    ... and {len(customers) - 15} more")
    
    print("\n" + "=" * 60)
    
    # Verify expected counts
    expected = {
        'quickbase': 10,
        'navigator_app': 1,
        'demo': 1
    }
    
    all_good = True
    print("\n🔍 Verification:")
    for source, expected_count in expected.items():
        actual_count = by_source.get(source, 0)
        status = "✅" if actual_count == expected_count else "❌"
        print(f"   {status} {source}: expected {expected_count}, got {actual_count}")
        if actual_count != expected_count:
            all_good = False
    
    if all_good:
        print("\n🎉 All data sources loaded correctly!")
    else:
        print("\n⚠️  Some data sources have unexpected counts")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
