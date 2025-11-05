#!/usr/bin/env python3
"""
QuickBase API Client for CRM Integration
Pulls community and contact data from QuickBase tables
"""

import os
import json
from typing import Dict, List, Optional, Any
import logging

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    
logger = logging.getLogger(__name__)

class QuickBaseClient:
    """Client for QuickBase API integration"""
    
    def __init__(self):
        """Initialize QuickBase client with credentials"""
        self.base_url = "https://api.quickbase.com/v1"
        
        # Use production credentials from quickbase_connect_KEEP.md
        self.realm = os.getenv("QB_REALM", "marclilly.quickbase.com")
        self.user_token = os.getenv("QB_USER_TOKEN", "capxhv_iaf4_0_cww8jfnbjpfkhvd7752udkw3wv8")
        self.app_token = os.getenv("QB_APP_TOKEN", "cnnkxpkdi9f4d9c4rp2wy89dde")
        
        self.headers = {
            "QB-Realm-Hostname": self.realm,
            "Authorization": f"QB-USER-TOKEN {self.user_token}",
            "QB-AppToken": self.app_token,
            "Content-Type": "application/json"
        }
        
        # Table IDs from your production environment
        self.communities_table_id = "bkp5hn255"  # WA Communities
        self.contacts_table_id = "bkqfsmeuq"     # WA Clients (fallback)
        
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make authenticated request to QuickBase API"""
        if not REQUESTS_AVAILABLE:
            logger.warning("requests library not available, using mock data")
            return {}
            
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            else:
                response = requests.get(url, headers=self.headers, params=data)
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"QuickBase API error: {e}")
            # Return empty data on error to allow graceful fallback
            return {}
    
    def get_communities(self) -> List[Dict[str, Any]]:
        """
        Fetch community data from QuickBase WA Communities table
        
        Returns:
            List of community dictionaries with contact information
        """
        if not REQUESTS_AVAILABLE:
            logger.warning("requests library not available, using mock data")
            return self._get_mock_communities()
        
        # Note: Using production tokens by default, can override with env vars
        
        # QuickBase query for communities - start broad, then filter in code
        query_data = {
            "from": self.communities_table_id,
            "select": [
                3,   # Record ID
                27,  # Business Name (Community Name)
                6,   # Name (Contact Person Name)
                7,   # Address 
                33,  # Phone Number
                34,  # Cell Phone
                37,  # Email
                55,  # Licensee
                21,  # Type/Care Level
                59,  # Vacancy (current availability info)
                40,  # Number of beds (total capacity)
            ],
            # Remove WHERE clause to see all data first, then filter in validation
            "options": {
                "skip": 0,
                "top": 100  # Get more records to analyze
            }
        }
        
        try:
            result = self._make_request("POST", "records/query", query_data)
            
            if "data" not in result:
                logger.warning("No community data returned from QuickBase")
                return self._get_mock_communities()
            
            communities = []
            for record in result["data"]:
                community = self._format_community_record(record)
                if community and self._is_valid_community(community):  # Add validation
                    communities.append(community)
            
            # Sort to prioritize Bellevue communities first
            communities.sort(key=lambda c: (
                not c.get('is_bellevue', False),  # Bellevue first
                not bool(c.get('licensee', '').strip()),  # Then those with licensees
                c.get('name', '')  # Then alphabetically
            ))
            
            logger.info(f"Retrieved {len(communities)} valid WA communities from QuickBase")
            bellevue_count = sum(1 for c in communities if c.get('is_bellevue', False))
            logger.info(f"Including {bellevue_count} Bellevue communities")
            return communities
            
        except Exception as e:
            logger.error(f"Error fetching communities: {e}")
            return self._get_mock_communities()
    
    def _is_valid_community(self, community: Dict[str, Any]) -> bool:
        """
        Validate community has required data and is not closed
        
        Requirements:
        - Must have business name
        - Must have licensee (relaxed for now to see data)
        - Business name must not contain 'closed' (case insensitive)
        - Must be in Washington state (relaxed from Bellevue only)
        """
        import re
        
        # Check for required business name
        business_name = community.get('name', '').strip()
        if not business_name or business_name == 'Unknown Community':
            return False
        
        # Temporarily relax licensee requirement to see more data
        licensee = community.get('licensee', '').strip()
        # if not licensee:
        #     return False
        
        # Check business name doesn't contain 'closed' (case insensitive)
        if re.search(r'\bclosed\b', business_name, re.IGNORECASE):
            return False
        
        # Relax location requirement to just Washington state for now
        location = community.get('location', '').lower()
        address = community.get('address', '').lower()
        if 'wa' not in location and 'washington' not in address:
            return False
        
        # Prefer Bellevue but don't require it yet
        is_bellevue = 'bellevue' in location or 'bellevue' in address
        community['is_bellevue'] = is_bellevue  # Mark for prioritization
        
        return True
    
    def _format_community_record(self, record: Dict) -> Optional[Dict[str, Any]]:
        """Format QuickBase community record for CRM use"""
        try:
            # QuickBase returns fields at the top level, not nested under "fields"
            # Structure: {"21": {"value": "Adult Family Home"}, "27": {"value": "Business Name"}}
            
            # Debug: Log available fields
            # logger.info(f"Available fields in record: {available_fields}")
            
            # Extract field values from top-level structure
            name = record.get("27", {}).get("value", "Unknown Community")  # Business Name
            contact_person = record.get("6", {}).get("value", "")  # Name (Contact Person)
            
            address = record.get("7", {}).get("value", "")
            phone = record.get("33", {}).get("value", "")
            cell_phone = record.get("34", {}).get("value", "")
            email = record.get("37", {}).get("value", "")
            licensee = record.get("55", {}).get("value", "")
            care_type = record.get("21", {}).get("value", "")
            vacancy_info = record.get("59", {}).get("value", "")  # Current vacancy status
            num_beds = record.get("40", {}).get("value", 0)  # Total capacity
            
            # Log care type for debugging (can be removed in production)
            # logger.info(f"Community {name}: care_type = '{care_type}'")
            
            # Use contact person name if licensee is empty
            if not licensee and contact_person:
                licensee = contact_person
            
            # Determine primary contact info (prefer cell phone, fallback to phone)
            primary_contact_phone = cell_phone if cell_phone else phone
            contact_name = licensee if licensee else "Contact"
            
            # Format contact string
            contact_info = f"{contact_name}"
            if primary_contact_phone:
                contact_info += f" - {primary_contact_phone}"
            
            # Map care types to our standard format
            care_levels = []
            care_type_lower = care_type.lower() if care_type else ""
            
            # Map QuickBase care types to standard care levels
            if "assisted" in care_type_lower or "assisted living" in care_type_lower:
                care_levels.append("assisted_living")
            if "memory" in care_type_lower or "memory care" in care_type_lower:
                care_levels.append("memory_care")
            if "adult family home" in care_type_lower:
                # Adult Family Homes can provide various levels of care
                care_levels.extend(["assisted_living", "memory_care"])
            if "independent" in care_type_lower or "retirement" in care_type_lower:
                care_levels.append("independent")
            
            # Default if no specific type found
            if not care_levels:
                care_levels = ["assisted_living"]
            
            # logger.info(f"Community {name}: mapped care_levels = {care_levels}")
            
            # Parse location from address - specifically for Bellevue
            location = "Washington, WA"  # Default for WA state
            if address:
                # Extract city, state from address if more specific
                address_parts = address.split(",")
                if len(address_parts) >= 2:
                    city = address_parts[-2].strip()
                    if 'bellevue' in city.lower():
                        location = f"{city}, WA"
            
            # Parse vacancy information more intelligently
            vacancy_status = "Contact for availability"  # Default
            available_beds = 0
            if vacancy_info:
                vacancy_lower = vacancy_info.lower()
                if "no vacancy" in vacancy_lower or "no openings" in vacancy_lower or "full" in vacancy_lower:
                    vacancy_status = "No current openings"
                    availability = "waitlist"
                elif "private" in vacancy_lower or "shared" in vacancy_lower or "room" in vacancy_lower:
                    vacancy_status = "Current openings available"
                    availability = "immediate"
                    # Try to extract actual bed count (avoid parsing dates)
                    import re
                    # Look for patterns like "2 private", "1 shared", etc.
                    bed_matches = re.findall(r'(\d+)\s*(private|shared|room|bed)', vacancy_lower)
                    if bed_matches:
                        available_beds = sum(int(match[0]) for match in bed_matches)
                elif vacancy_info.strip():
                    vacancy_status = "Current openings available"
                    availability = "immediate"
                else:
                    availability = "contact"
            else:
                availability = "contact"
            
            # Don't override availability if we already set it from vacancy parsing
            if 'availability' not in locals():
                # Determine availability based on vacancy data
                if available_beds > 0:
                    availability = "immediate"
                elif "available" in vacancy_status.lower() or "openings" in vacancy_status.lower():
                    availability = "immediate"
                elif "no" in vacancy_status.lower():
                    availability = "waitlist"
                else:
                    availability = "contact"
            
            community = {
                "id": f"qb_{record.get('recordId', 'unknown')}",
                "name": name,
                "location": location,
                "care_levels": care_levels,
                "monthly_cost": {"min": 4000, "max": 8000},  # Default range - could be enhanced
                "amenities": ["dining", "activities", "transportation"],  # Default amenities
                "specializations": care_levels,
                "rating": 4.5,  # Default rating - could be enhanced with QB field
                "availability": availability,  # Real-time availability from QuickBase
                "vacancy_info": vacancy_info,  # Raw vacancy text from QuickBase
                "vacancy_status": vacancy_status,  # Parsed status
                "available_beds": available_beds,  # Parsed bed count
                "total_beds": num_beds if num_beds else "Not specified",  # Total capacity
                "contact": contact_info,
                "licensee": licensee,
                "phone": phone,
                "cell_phone": cell_phone,
                "email": email,
                "address": address,
                "care_type": care_type,
                "record_id": record.get('recordId', 'unknown')  # Add record ID for unique keys
            }
            
            return community
            
        except Exception as e:
            logger.error(f"Error formatting community record: {e}")
            return None
    
    def _get_mock_communities(self) -> List[Dict[str, Any]]:
        """Fallback mock data for Bellevue communities when QuickBase is unavailable"""
        return [
            {
                "id": "mock_bellevue_001",
                "name": "Sunrise Senior Living Bellevue",
                "location": "Bellevue, WA",
                "care_levels": ["independent", "assisted_living", "memory_care"],
                "monthly_cost": {"min": 4500, "max": 7200},
                "amenities": ["fitness_center", "dining", "transportation", "activities"],
                "specializations": ["alzheimers", "physical_therapy"],
                "rating": 4.8,
                "availability": "immediate",
                "contact": "Sarah Chen - (425) 555-0123",
                "licensee": "Sarah Chen",
                "phone": "(425) 555-0123",
                "cell_phone": "(425) 555-0123",
                "email": "sarah.chen@sunriseseniorliving.com",
                "address": "123 Main St, Bellevue, WA 98004",
                "care_type": "Assisted Living",
                "record_id": "mock_001"
            },
            {
                "id": "mock_bellevue_002",
                "name": "Bellevue Terrace Assisted Living",
                "location": "Bellevue, WA", 
                "care_levels": ["assisted_living", "memory_care"],
                "monthly_cost": {"min": 5200, "max": 7800},
                "amenities": ["gardens", "library", "dining", "wellness"],
                "specializations": ["memory_care", "wellness"],
                "rating": 4.7,
                "availability": "2_weeks",
                "contact": "Michael Torres - (425) 555-0156",
                "licensee": "Michael Torres",
                "phone": "(425) 555-0156", 
                "cell_phone": "(425) 555-0156",
                "email": "michael.torres@bellevueterrace.com",
                "address": "456 Bellevue Way, Bellevue, WA 98004",
                "care_type": "Assisted Living",
                "record_id": "mock_002"
            }
        ]

# Global instance for easy access
quickbase_client = QuickBaseClient()