"""
Navigator Data Reader - Safe read-only access to Senior Navigator customer data
Provides CRM with access to customer submissions, assessments, and plans
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

class NavigatorDataReader:
    """Read-only access to Navigator customer data for CRM use"""
    
    def __init__(self, data_root: str = "data"):
        self.data_root = Path(data_root)
        self.users_dir = self.data_root / "users"
        self.demo_dir = self.users_dir / "demo"
    
    def get_all_customers(self) -> List[Dict[str, Any]]:
        """Get summary of all Navigator customers"""
        customers = []
        
        # Process regular user files
        if self.users_dir.exists():
            for user_file in self.users_dir.glob("anon_*.json"):
                try:
                    customer_data = self._load_user_file(user_file)
                    if customer_data:
                        customers.append(customer_data)
                except Exception as e:
                    print(f"Error loading {user_file}: {e}")
        
        # Process demo users
        if self.demo_dir.exists():
            for demo_dir in self.demo_dir.iterdir():
                if demo_dir.is_dir():
                    try:
                        customer_data = self._load_demo_user(demo_dir)
                        if customer_data:
                            customers.append(customer_data)
                    except Exception as e:
                        print(f"Error loading demo {demo_dir}: {e}")
        
        return customers
    
    def get_customer_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed customer information by user ID"""
        try:
            # Load basic customer data
            user_data = self.load_user_data(user_id)
            if not user_data:
                return None
            
            # Enhance with assessment data
            customer_data = {
                'user_id': user_id,
                'person_name': user_data.get('person_name', 'Unknown'),
                'relationship_type': user_data.get('relationship_type', 'Unknown'),
                'last_activity': user_data.get('last_activity', 'Never'),
                'last_activity_days': self._calculate_days_since_activity(user_data.get('last_activity')),
                'has_gcp_assessment': False,
                'has_cost_plan': False,
                'care_recommendation': None,
                'assessment_summary': None,
                'cost_summary': None,
                'journey_stage': 'Initial Contact'
            }
            
            # Check for GCP assessment
            gcp_data = self._load_gcp_data(user_id)
            if gcp_data:
                customer_data['has_gcp_assessment'] = True
                customer_data['care_recommendation'] = gcp_data.get('recommendation', 'Assessment Complete')
                customer_data['assessment_summary'] = self._generate_assessment_summary(gcp_data)
                customer_data['journey_stage'] = 'Care Assessment Complete'
            
            # Check for cost planning
            cost_data = self._load_cost_data(user_id)
            if cost_data:
                customer_data['has_cost_plan'] = True
                customer_data['cost_summary'] = self._generate_cost_summary(cost_data)
                if customer_data['has_gcp_assessment']:
                    customer_data['journey_stage'] = 'Ready for Recommendations'
                else:
                    customer_data['journey_stage'] = 'Cost Planning Complete'
            
            return customer_data
            
        except Exception as e:
            self.logger.error(f"Error loading customer {user_id}: {e}")
            return None
    
    def _calculate_days_since_activity(self, last_activity):
        """Calculate days since last activity"""
        if not last_activity or last_activity == 'Never':
            return 999
        
        try:
            from datetime import datetime
            # Try to parse the date
            activity_date = datetime.strptime(last_activity, '%Y-%m-%d')
            days_diff = (datetime.now() - activity_date).days
            return max(0, days_diff)
        except:
            return 999
    
    def _load_gcp_data(self, user_id):
        """Load GCP assessment data for user"""
        try:
            gcp_file = self.data_dir / 'users' / user_id / 'gcp_assessment.json'
            if gcp_file.exists():
                return self._load_json_file(gcp_file)
            return None
        except Exception as e:
            self.logger.debug(f"No GCP data for {user_id}: {e}")
            return None
    
    def _load_cost_data(self, user_id):
        """Load cost planning data for user"""
        try:
            cost_file = self.data_dir / 'users' / user_id / 'cost_plan.json'
            if cost_file.exists():
                return self._load_json_file(cost_file)
            return None
        except Exception as e:
            self.logger.debug(f"No cost data for {user_id}: {e}")
            return None
    
    def _generate_assessment_summary(self, gcp_data):
        """Generate human-readable assessment summary"""
        recommendation = gcp_data.get('recommendation', 'Unknown')
        mobility_score = gcp_data.get('mobility_score', 0)
        care_level = gcp_data.get('care_level', 'Unknown')
        
        summary = f"Care recommendation: {recommendation}. "
        
        if mobility_score:
            summary += f"Mobility assessment score: {mobility_score}/100. "
        
        if care_level and care_level != 'Unknown':
            summary += f"Care level: {care_level}."
        
        return summary.strip()
    
    def _generate_cost_summary(self, cost_data):
        """Generate human-readable cost summary"""
        budget_range = cost_data.get('budget_range', 'Not specified')
        monthly_income = cost_data.get('monthly_income', 0)
        
        summary = f"Budget range: {budget_range}. "
        
        if monthly_income:
            summary += f"Monthly income: ${monthly_income:,}. "
        
        summary += "Financial capacity assessment completed."
        
        return summary.strip()
    
    def _load_user_file(self, user_file: Path) -> Optional[Dict[str, Any]]:
        """Load and summarize a regular user file"""
        try:
            with open(user_file, 'r') as f:
                data = json.load(f)
            
            # Extract key information for CRM summary
            user_id = user_file.stem
            person_name = data.get('person_name', 'Unknown')
            
            # Calculate last activity from file modification time
            last_modified = datetime.fromtimestamp(user_file.stat().st_mtime)
            days_since_activity = (datetime.now() - last_modified).days
            
            # Check what assessments/plans exist
            has_gcp_assessment = bool(data.get('gcp_assessment_complete') or 
                                    data.get('care_recommendation'))
            has_cost_plan = bool(data.get('cost_planner_complete') or 
                               data.get('estimated_monthly_cost'))
            
            return {
                'user_id': user_id,
                'person_name': person_name,
                'last_activity': last_modified.strftime('%Y-%m-%d'),
                'last_activity_days': days_since_activity,
                'has_gcp_assessment': has_gcp_assessment,
                'has_cost_plan': has_cost_plan,
                'relationship_type': data.get('relationship_type', 'Unknown'),
                'source': 'navigator'
            }
            
        except Exception as e:
            print(f"Error processing {user_file}: {e}")
            return None
    
    def _load_demo_user(self, demo_dir: Path) -> Optional[Dict[str, Any]]:
        """Load and summarize a demo user directory"""
        try:
            # Try to load session.json for basic info
            session_file = demo_dir / "session.json"
            if session_file.exists():
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                user_id = demo_dir.name
                person_name = session_data.get('person_name', 
                                             session_data.get('planning_for_name', 
                                                             demo_dir.name.replace('demo_', '').replace('_', ' ').title()))
                
                # Check for assessment files
                has_gcp_assessment = (demo_dir / "careplan.json").exists()
                has_cost_plan = (demo_dir / "costplan.json").exists()
                
                return {
                    'user_id': user_id,
                    'person_name': person_name,
                    'last_activity': '2024-11-05',  # Demo data
                    'last_activity_days': 1,
                    'has_gcp_assessment': has_gcp_assessment,
                    'has_cost_plan': has_cost_plan,
                    'relationship_type': session_data.get('relationship_type', 'Demo'),
                    'source': 'demo'
                }
            
        except Exception as e:
            print(f"Error processing demo {demo_dir}: {e}")
            return None
    
    def _load_detailed_user_data(self, user_file: Path) -> Dict[str, Any]:
        """Load complete user data for detailed view"""
        try:
            with open(user_file, 'r') as f:
                data = json.load(f)
            
            # Add metadata
            data['_metadata'] = {
                'user_id': user_file.stem,
                'source': 'navigator',
                'last_modified': datetime.fromtimestamp(user_file.stat().st_mtime).isoformat()
            }
            
            return data
            
        except Exception as e:
            print(f"Error loading detailed data from {user_file}: {e}")
            return {}
    
    def _load_detailed_demo_data(self, demo_dir: Path) -> Dict[str, Any]:
        """Load complete demo user data from directory"""
        try:
            combined_data = {
                '_metadata': {
                    'user_id': demo_dir.name,
                    'source': 'demo',
                    'last_modified': datetime.now().isoformat()
                }
            }
            
            # Load all JSON files in the demo directory
            for json_file in demo_dir.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        file_data = json.load(f)
                    combined_data[json_file.stem] = file_data
                except Exception as e:
                    print(f"Error loading {json_file}: {e}")
            
            return combined_data
            
        except Exception as e:
            print(f"Error loading detailed demo data from {demo_dir}: {e}")
            return {}
    
    def get_customer_assessment_summary(self, user_id: str) -> Dict[str, Any]:
        """Get assessment summary for a customer"""
        customer_data = self.get_customer_by_id(user_id)
        if not customer_data:
            return {}
        
        summary = {
            'user_id': user_id,
            'person_name': customer_data.get('person_name', 'Unknown'),
            'assessments': {},
            'recommendations': {},
            'cost_analysis': {}
        }
        
        # Extract GCP assessment if available
        if customer_data.get('care_recommendation'):
            summary['assessments']['gcp'] = {
                'completed': True,
                'recommendation': customer_data['care_recommendation'],
                'reasoning': customer_data.get('care_reasoning', '')
            }
        
        # Extract cost planner data if available
        if customer_data.get('estimated_monthly_cost'):
            summary['cost_analysis'] = {
                'monthly_cost': customer_data['estimated_monthly_cost'],
                'care_level': customer_data.get('care_level', 'Unknown')
            }
        
        # Handle demo data structure
        if customer_data.get('careplan'):
            summary['assessments']['gcp'] = customer_data['careplan']
        
        if customer_data.get('costplan'):
            summary['cost_analysis'] = customer_data['costplan']
        
        return summary


@dataclass
class CustomerProfile:
    """Customer profile data from Navigator."""
    user_id: str
    person_name: Optional[str] = None
    relationship_type: Optional[str] = None
    planning_for_relationship: Optional[str] = None
    last_updated: Optional[datetime] = None
    
    # Navigator completion status
    gcp_completed: bool = False
    cost_planner_completed: bool = False
    pfma_completed: bool = False
    
    # Assessment data
    care_recommendation: Optional[str] = None
    mobility_score: Optional[int] = None
    cognitive_score: Optional[int] = None
    
    # Cost planning data
    estimated_monthly_cost: Optional[float] = None
    care_hours_needed: Optional[int] = None


# Singleton instance for easy access
navigator_data = NavigatorDataReader()


class NavigatorDataReader:
    """Read-only access to Navigator customer data."""
    
    def __init__(self, data_root: str = "data"):
        self.data_root = Path(data_root)
        self.users_dir = self.data_root / "users"
    
    def get_all_customers(self) -> List[CustomerProfile]:
        """Get all customer profiles from Navigator data."""
        customers = []
        
        if not self.users_dir.exists():
            return customers
        
        # Read regular user files
        for user_file in self.users_dir.glob("*.json"):
            if user_file.name.startswith("anon_"):
                customer = self._load_customer_from_file(user_file)
                if customer:
                    customers.append(customer)
        
        # Read demo user files
        demo_dir = self.users_dir / "demo"
        if demo_dir.exists():
            for demo_file in demo_dir.glob("*.json"):
                customer = self._load_customer_from_file(demo_file)
                if customer:
                    customers.append(customer)
        
        return customers
    
    def get_customer(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific customer by user ID."""
        # Try regular user file
        user_file = self.users_dir / f"{user_id}.json"
        if user_file.exists():
            return self._load_customer_from_file(user_file)
        
        # Try demo user file
        demo_file = self.users_dir / "demo" / f"{user_id}.json"
        if demo_file.exists():
            return self._load_customer_from_file(demo_file)
        
        return None
    
    def get_customer_raw_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get raw Navigator data for a customer (for detailed analysis)."""
        customer = self.get_customer(user_id)
        if not customer:
            return None
        
        # Load the full data file
        user_file = self.users_dir / f"{user_id}.json"
        if not user_file.exists():
            user_file = self.users_dir / "demo" / f"{user_id}.json"
        
        if user_file.exists():
            try:
                return json.loads(user_file.read_text())
            except (json.JSONDecodeError, Exception):
                return None
        
        return None
    
    def _load_customer_from_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load customer profile from a Navigator data file."""
        try:
            data = json.loads(file_path.read_text())
            
            # Extract user ID from filename
            user_id = file_path.stem
            
            # Extract basic profile info
            person_name = data.get("person_name")
            relationship_type = data.get("relationship_type") 
            planning_for_relationship = data.get("planning_for_relationship")
            
            # Check completion status (look for product completion markers)
            has_gcp_assessment = self._check_completion(data, ["gcp", "gcp_v4"])
            has_cost_plan = self._check_completion(data, ["cost_planner", "cost_v2"])
            has_financial_assessment = self._check_completion(data, ["pfma", "pfma_v3"])
            
            # Extract assessment data
            care_recommendation = data.get("gcp_care_recommendation")
            mobility_score = data.get("gcp_mobility_score")
            cognitive_score = data.get("gcp_cognitive_score")
            
            # Extract cost data
            estimated_monthly_cost = data.get("estimated_monthly_cost")
            care_hours_needed = data.get("recommended_care_hours")
            
            # File modification time as last updated
            last_updated = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            # Calculate activity metrics
            days_since_update = (datetime.now() - last_updated).days
            
            return {
                "user_id": user_id,
                "person_name": person_name,
                "relationship_type": relationship_type,
                "planning_for_relationship": planning_for_relationship,
                "last_updated": last_updated,
                "last_activity_days": days_since_update,
                "has_gcp_assessment": has_gcp_assessment,
                "has_cost_plan": has_cost_plan,
                "has_financial_assessment": has_financial_assessment,
                "care_recommendation": care_recommendation,
                "mobility_score": mobility_score,
                "cognitive_score": cognitive_score,
                "estimated_monthly_cost": estimated_monthly_cost,
                "care_hours_needed": care_hours_needed,
            }
            
        except (json.JSONDecodeError, FileNotFoundError, Exception):
            return None
    
    def _check_completion(self, data: Dict[str, Any], product_keys: List[str]) -> bool:
        """Check if a product is completed based on various possible keys."""
        for key in product_keys:
            if data.get(f"{key}_completed"):
                return True
            if data.get(f"{key}_completion_date"):
                return True
        return False
    
    def get_customer_statistics(self) -> Dict[str, Any]:
        """Get overall statistics about Navigator customers."""
        customers = self.get_all_customers()
        
        total_customers = len(customers)
        gcp_completed = sum(1 for c in customers if c.gcp_completed)
        cost_planner_completed = sum(1 for c in customers if c.cost_planner_completed)
        pfma_completed = sum(1 for c in customers if c.pfma_completed)
        
        # Count by care recommendation
        care_recommendations = {}
        for customer in customers:
            if customer.care_recommendation:
                care_recommendations[customer.care_recommendation] = \
                    care_recommendations.get(customer.care_recommendation, 0) + 1
        
        return {
            "total_customers": total_customers,
            "gcp_completion_rate": gcp_completed / total_customers if total_customers > 0 else 0,
            "cost_planner_completion_rate": cost_planner_completed / total_customers if total_customers > 0 else 0,
            "pfma_completion_rate": pfma_completed / total_customers if total_customers > 0 else 0,
            "care_recommendations": care_recommendations,
            "last_30_days": self._get_recent_customers(customers, 30),
        }
    
    def _get_recent_customers(self, customers: List[CustomerProfile], days: int) -> int:
        """Count customers active in the last N days."""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        return sum(1 for c in customers if c.last_updated and c.last_updated > cutoff)


# Singleton instance for easy access
navigator_data = NavigatorDataReader()