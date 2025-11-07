#!/usr/bin/env python3
"""
Test Synthetic Data Integration

Quick test to verify NavigatorDataReader picks up synthetic customers
"""

from shared.data_access.navigator_reader import NavigatorDataReader

def main():
    """Test synthetic data integration"""
    print("🔄 Testing synthetic data integration...")
    
    reader = NavigatorDataReader()
    customers = reader.get_all_customers()
    
    print(f"\n📊 Total customers found: {len(customers)}")
    
    # Filter synthetic customers  
    synthetic_customers = []
    for customer in customers:
        # Check multiple ways to identify synthetic data
        if ('synthetic_aug2025' in customer.get('user_id', '') or 
            customer.get('data_source') == 'synthetic_generator_aug2025' or
            any('synthetic' in str(v) for v in customer.values() if isinstance(v, str))):
            synthetic_customers.append(customer)
    
    print(f"🎭 Synthetic customers: {len(synthetic_customers)}")
    
    if synthetic_customers:
        print("\n📋 SYNTHETIC CUSTOMER SAMPLE:")
        for i, customer in enumerate(synthetic_customers[:3]):  # Show first 3
            print(f"\n   {i+1}. {customer.get('person_name', 'Unknown')}")
            print(f"      ID: {customer.get('user_id')}")
            print(f"      Journey: {customer.get('journey_stage', 'Unknown')}")
            print(f"      Care Level: {customer.get('care_recommendation', 'Unknown')}")
            print(f"      GCP: {'✅' if customer.get('has_gcp_assessment') else '❌'}")
            print(f"      Cost Plan: {'✅' if customer.get('has_cost_plan') else '❌'}")
            print(f"      Monthly Cost: ${customer.get('monthly_cost_estimate', 0):,}")
    
    print(f"\n✅ Synthetic data integration test complete!")
    
    return len(synthetic_customers)

if __name__ == "__main__":
    main()