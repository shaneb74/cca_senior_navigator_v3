#!/usr/bin/env python3
"""Test customer deletion independently"""

import json
from pathlib import Path

def test_delete_customer(customer_id: str) -> bool:
    """Test deleting a customer"""
    print(f"\n{'='*60}")
    print(f"Testing deletion of: {customer_id}")
    print(f"{'='*60}\n")
    
    deleted = False
    data_root = Path("data")
    
    # Try to delete from Navigator app customers (JSONL)
    customers_file = data_root / "crm" / "customers.jsonl"
    print(f"Checking: {customers_file}")
    print(f"File exists: {customers_file.exists()}")
    
    if customers_file.exists():
        customers = []
        original_count = 0
        found_customer = None
        
        with open(customers_file, 'r') as f:
            for line in f:
                original_count += 1
                customer = json.loads(line)
                
                # Check if this is the customer to delete
                is_match = any([
                    customer.get('id') == customer_id,
                    customer.get('customer_id') == customer_id,
                    customer.get('user_id') == customer_id
                ])
                
                if is_match:
                    found_customer = customer
                    print(f"\n✅ FOUND CUSTOMER TO DELETE:")
                    print(f"   Name: {customer.get('name')}")
                    print(f"   ID field: customer_id = {customer.get('customer_id')}")
                    print(f"   Skipping this record...")
                else:
                    customers.append(customer)
        
        print(f"\nOriginal count: {original_count}")
        print(f"After filter: {len(customers)}")
        print(f"Found customer to delete: {found_customer is not None}")
        
        if len(customers) < original_count:
            print(f"\n✅ Writing {len(customers)} customers back to file...")
            with open(customers_file, 'w') as f:
                for customer in customers:
                    f.write(json.dumps(customer) + '\n')
            deleted = True
            print("✅ File written successfully")
        else:
            print("\n❌ No change in customer count - customer not found")
    
    print(f"\n{'='*60}")
    print(f"Result: {'✅ DELETED' if deleted else '❌ NOT FOUND'}")
    print(f"{'='*60}\n")
    
    return deleted

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_delete.py <customer_id>")
        print("\nAvailable customers:")
        with open("data/crm/customers.jsonl", 'r') as f:
            for line in f:
                customer = json.loads(line)
                print(f"  - {customer.get('customer_id')}: {customer.get('name')}")
        sys.exit(1)
    
    customer_id = sys.argv[1]
    result = test_delete_customer(customer_id)
    sys.exit(0 if result else 1)
