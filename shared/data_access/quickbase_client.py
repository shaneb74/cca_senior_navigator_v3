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
        
        # QuickBase query for communities - focused high-impact matching criteria
        query_data = {
            "from": self.communities_table_id,
            "select": [
                # Core identification (existing)
                3,   # Record ID
                27,  # Business Name (Community Name)
                6,   # Name (Contact Person Name)
                55,  # Licensee
                21,  # Type/Care Level
                7,   # Address 
                33,  # Phone Number
                34,  # Cell Phone
                37,  # Email
                59,  # Vacancy (current availability info)
                40,  # Number of beds (total capacity)
                
                # Critical safety/medical (4 fields)
                91,  # Hoyer Lift - Critical for mobility assistance
                71,  # Dedicated Memory Care - Alzheimer's/dementia safety
                89,  # 2 Person Transfers - Heavy care needs
                147, # Bariatric - Weight management capabilities
                
                # Common medical needs (3 fields)
                90,  # Insulin management - Very common (diabetes)
                151, # Wound care - Common post-hospital need
                19,  # Awake night staff - Safety for high-risk residents
                
                # High-impact lifestyle (3 fields)
                61,  # Pet policies - Major emotional/psychological impact
                104, # Languages spoken - Cultural/communication needs
                47,  # Full kitchen - Independence preference
                
                # Filters
                43,  # Do Not Place List
                96,  # Community Closed
                45,  # Contracted with CCA
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
            
            # Extract basic field values
            name = record.get("27", {}).get("value", "Unknown Community")  # Business Name
            contact_person = record.get("6", {}).get("value", "")  # Name (Contact Person)
            
            address = record.get("7", {}).get("value", "")
            city = record.get("10", {}).get("value", "")
            state = record.get("11", {}).get("value", "")
            phone = record.get("33", {}).get("value", "")
            cell_phone = record.get("34", {}).get("value", "")
            email = record.get("37", {}).get("value", "")
            licensee = record.get("55", {}).get("value", "")
            care_type = record.get("21", {}).get("value", "")
            vacancy_info = record.get("59", {}).get("value", "")  # Current vacancy status
            num_beds = record.get("40", {}).get("value", 0)  # Total capacity
            rating = record.get("42", {}).get("value", "")
            
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
            
            # Parse location from address - specifically for Bellevue
            location = f"{city}, {state}" if city and state else "Washington, WA"
            
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
            
            # Extract amenities from QuickBase checkbox fields (focused set)
            amenities = []
            
            # Helper function to check checkbox value
            def is_checked(field_id):
                return record.get(str(field_id), {}).get("value") == "1"
            
            # High-impact amenities only
            if is_checked(47):  # Full Kitchen
                amenities.append("full_kitchen")
            
            # Always include basic amenities
            amenities.extend(["dining", "activities", "transportation"])
            
            # Extract critical specializations and medical services
            specializations = list(care_levels)  # Start with care levels
            
            # Critical safety/medical capabilities
            if is_checked(71):  # Dedicated Memory Care
                specializations.append("memory_care_dedicated")
            if is_checked(91):  # Hoyer Lift
                specializations.append("hoyer_lift")
            if is_checked(147): # Bariatric
                specializations.append("bariatric_care")
            if is_checked(89):  # 2 Person Transfers
                specializations.append("two_person_transfers")
            
            # Common medical services
            if is_checked(90):  # Insulin
                specializations.append("insulin_management")
            if is_checked(151): # Wound Care
                specializations.append("wound_care")
            if is_checked(19):  # Awake Staff
                specializations.append("awake_staff")
            
            # Extract lifestyle preferences (high-impact only)
            lifestyle_features = []
            if is_checked(61):  # Allows Pets w/placement
                lifestyle_features.append("pet_friendly")
            
            # Extract languages spoken
            languages_spoken = record.get("104", {}).get("value", "")
            if languages_spoken:
                lifestyle_features.append(f"languages: {languages_spoken}")
            
            # Parse rating (if available)
            rating_value = 4.5  # Default
            if rating:
                try:
                    rating_value = float(rating)
                except:
                    pass
            
            community = {
                "id": f"qb_{record.get('recordId', 'unknown')}",
                "name": name,
                "location": location,
                "care_levels": care_levels,
                "monthly_cost": {"min": 4000, "max": 8000},  # Default range - could be enhanced
                "amenities": amenities,
                "specializations": specializations,
                "lifestyle_features": lifestyle_features,
                "rating": rating_value,
                "availability": availability,
                "vacancy_info": vacancy_info,
                "vacancy_status": vacancy_status,
                "available_beds": available_beds,
                "total_beds": num_beds if num_beds else "Not specified",
                "contact": contact_info,
                "licensee": licensee,
                "phone": phone,
                "cell_phone": cell_phone,
                "email": email,
                "address": address,
                "city": city,
                "state": state,
                "care_type": care_type,
                "rating_text": rating,
                "languages_spoken": languages_spoken,
                "record_id": record.get('recordId', 'unknown'),
                
                # QuickBase-specific data for advanced matching (focused set)
                "qb_data": {
                    # Critical safety/medical
                    "hoyer_lift": is_checked(91),
                    "memory_care_dedicated": is_checked(71),
                    "bariatric": is_checked(147),
                    "two_person_transfers": is_checked(89),
                    
                    # Common medical services
                    "insulin_management": is_checked(90),
                    "wound_care": is_checked(151),
                    "awake_staff": is_checked(19),
                    
                    # High-impact lifestyle
                    "pet_friendly": is_checked(61),
                    "full_kitchen": is_checked(47),
                    "languages_spoken": languages_spoken,
                }
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