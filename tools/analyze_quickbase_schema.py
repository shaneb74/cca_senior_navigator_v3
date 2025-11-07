"""
QuickBase Schema Analyzer - Extract key insights from current CRM structure
"""
import xml.etree.ElementTree as ET
from pathlib import Path
import json

def analyze_schema_file(file_path):
    """Analyze a QuickBase schema XML file"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Extract table info
        table = root.find('table')
        if table is None:
            return None
            
        table_name_elem = table.find('name')
        table_name = table_name_elem.text if table_name_elem is not None else "Unknown"
        
        table_desc_elem = table.find('desc')
        table_desc = table_desc_elem.text if table_desc_elem is not None else ""
        
        # Extract fields
        fields = []
        for field in table.findall('.//field'):
            field_id = field.get('id')
            field_type = field.get('field_type')
            base_type = field.get('base_type')
            
            label_elem = field.find('label')
            label = label_elem.text if label_elem is not None else f"Field {field_id}"
            
            required_elem = field.find('required')
            required = required_elem.text == '1' if required_elem is not None else False
            
            appears_default_elem = field.find('appears_by_default')
            appears_default = appears_default_elem.text == '1' if appears_default_elem is not None else False
            
            fields.append({
                'id': field_id,
                'label': label,
                'type': field_type,
                'base_type': base_type,
                'required': required,
                'appears_by_default': appears_default
            })
        
        # Extract queries (reports/views)
        queries = []
        for query in table.findall('.//query'):
            query_id = query.get('id')
            name_elem = query.find('qyname')
            name = name_elem.text if name_elem is not None else f"Query {query_id}"
            
            type_elem = query.find('qytype')
            query_type = type_elem.text if type_elem is not None else "table"
            
            queries.append({
                'id': query_id,
                'name': name,
                'type': query_type
            })
        
        return {
            'table_name': table_name,
            'description': table_desc,
            'fields': fields,
            'queries': queries,
            'total_fields': len(fields)
        }
        
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return None

def main():
    """Analyze all QuickBase schema files"""
    schema_files = [
        'quickbase_contacts_schema.xml',
        'quickbase_communities_schema.xml', 
        'quickbase_activities_schema.xml'
    ]
    
    analysis = {}
    
    for file_name in schema_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"\n=== Analyzing {file_name} ===")
            result = analyze_schema_file(file_path)
            if result:
                analysis[file_name] = result
                
                print(f"Table: {result['table_name']}")
                print(f"Description: {result['description'][:100]}...")
                print(f"Total Fields: {result['total_fields']}")
                print(f"Total Queries: {len(result['queries'])}")
                
                print("\nKey Fields (appears by default):")
                for field in result['fields']:
                    if field['appears_by_default']:
                        req_str = " (Required)" if field['required'] else ""
                        print(f"  - {field['label']} ({field['type']}){req_str}")
                
                print("\nAvailable Reports/Views:")
                for query in result['queries'][:5]:  # Show first 5
                    print(f"  - {query['name']} ({query['type']})")
        else:
            print(f"File not found: {file_name}")
    
    # Save analysis to JSON for further review
    with open('quickbase_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n=== Analysis Complete ===")
    print("Detailed analysis saved to quickbase_analysis.json")
    
    # Print innovation opportunities
    print("\n=== INNOVATION OPPORTUNITIES ===")
    print("Based on QuickBase structure, here are modernization opportunities:")
    
    if 'quickbase_contacts_schema.xml' in analysis:
        contacts = analysis['quickbase_contacts_schema.xml']
        print(f"\n1. CONTACTS TABLE ({contacts['total_fields']} fields)")
        print("   Current: Basic contact info (name, phone, email, title)")
        print("   Innovation: → Smart contact profiles with interaction history")
        print("   Innovation: → AI-powered relationship scoring")
        print("   Innovation: → Integrated communication (click-to-call, email)")
    
    if 'quickbase_communities_schema.xml' in analysis:
        communities = analysis['quickbase_communities_schema.xml']
        print(f"\n2. COMMUNITIES TABLE ({communities['total_fields']} fields)")
        print("   Current: Static facility information")
        print("   Innovation: → Interactive community profiles with photos")
        print("   Innovation: → Smart matching based on Navigator care plans")
        print("   Innovation: → Real-time availability and pricing")
    
    if 'quickbase_activities_schema.xml' in analysis:
        activities = analysis['quickbase_activities_schema.xml']
        print(f"\n3. ACTIVITIES TABLE ({activities['total_fields']} fields)")
        print("   Current: Manual activity logging")
        print("   Innovation: → Automated activity tracking from Navigator")
        print("   Innovation: → AI-suggested next steps")
        print("   Innovation: → Visual timeline of customer journey")

if __name__ == "__main__":
    main()