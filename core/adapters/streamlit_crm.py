"""
Streamlit-Specific CRM Implementation

Implements the CRM SDK interfaces using proper CRM repository and session state.
This adapter separates anonymous session data from customer records.

Key Changes:
- Lead data tied to anonymous sessions (session files)
- Customer data stored in CRM repository (separate from sessions)
- Proper attribution between leads and customers
"""

from typing import Optional, Dict, Any
import streamlit as st

from core.sdk.crm_interface import (
    CRMStorageProvider, 
    CRMEventLogger, 
    LeadData, 
    CustomerData, 
    CRMStatus,
    ContactInfo
)
from core.session_store import save_user
from core.events import log_event
from shared.data_access.crm_repository import CrmRepository


class StreamlitCRMStorage(CRMStorageProvider):
    """Streamlit CRM storage with proper lead/customer separation."""
    
    def __init__(self):
        self.crm_repo = CrmRepository()
    
    def save_lead(self, lead_data: LeadData) -> None:
        """Save lead to session state (tied to anonymous session)."""
        # Store in session state for quick access
        st.session_state["_crm_lead_data"] = {
            "lead_id": lead_data.lead_id,
            "contact_info": lead_data.contact_info.__dict__,
            "engagement_source": lead_data.engagement_source,
            "created_at": lead_data.created_at,
            "status": lead_data.status,
            "metadata": lead_data.metadata or {}
        }
        
        # Persist lead data to session file (for anonymous users)
        self._persist_session_data()
    
    def save_customer(self, customer_data: CustomerData) -> None:
        """Save customer to CRM repository (separate from session)."""
        # Save to CRM repository using customer name as identifier
        customer_record = {
            "customer_id": customer_data.customer_id,
            "lead_id": customer_data.lead_id,
            "name": customer_data.contact_info.name,
            "email": customer_data.contact_info.email,
            "phone": customer_data.contact_info.phone,
            "source": customer_data.contact_info.source,
            "conversion_source": customer_data.conversion_source,
            "converted_at": customer_data.converted_at,
            "status": customer_data.status,
            "session_id": customer_data.metadata.get("session_id") if customer_data.metadata else None,
            "metadata": customer_data.metadata or {}
        }
        
        # Save to CRM repository file
        self.crm_repo._append_to_jsonl("customers.jsonl", customer_record)
        
        # Also store customer reference in session state
        st.session_state["_crm_customer_data"] = {
            "customer_id": customer_data.customer_id,
            "lead_id": customer_data.lead_id,
            "converted_at": customer_data.converted_at,
            "status": customer_data.status
        }
        
        # Persist session data (now includes customer reference)
        self._persist_session_data()
    
    def get_crm_status(self, session_id: str) -> Optional[CRMStatus]:
        """Get CRM status from session state."""
        lead_data = st.session_state.get("_crm_lead_data")
        customer_data = st.session_state.get("_crm_customer_data")
        
        if customer_data:
            return CRMStatus(
                user_type="customer",
                lead_id=customer_data["lead_id"],
                customer_id=customer_data["customer_id"],
                created_at=lead_data.get("created_at") if lead_data else None,
                converted_at=customer_data["converted_at"]
            )
        elif lead_data:
            return CRMStatus(
                user_type="lead",
                lead_id=lead_data["lead_id"],
                created_at=lead_data["created_at"]
            )
        else:
            return None
    
    def update_crm_status(self, session_id: str, status: CRMStatus) -> None:
        """Update CRM status in session state."""
        st.session_state["_crm_status"] = {
            "user_type": status.user_type,
            "lead_id": status.lead_id,
            "customer_id": status.customer_id,
            "created_at": status.created_at,
            "converted_at": status.converted_at
        }
        
        # Persist to session file
        self._persist_session_data()
    
    def get_all_customers(self):
        """Get all customers from Navigator app, QuickBase, and demo sources."""
        all_customers = []
        
        # Get Navigator app customers (appointment bookings)
        try:
            nav_customers = self.crm_repo._load_from_jsonl("customers.jsonl")
            for customer in nav_customers:
                customer['source'] = 'navigator_app'
                customer['customer_type'] = 'appointment_booking'
                all_customers.append(customer)
        except Exception:
            pass  # No Navigator app customers yet
        
        # Get QuickBase customers (imported from QuickBase)
        try:
            import json
            import os
            qb_file = os.path.join(
                self.crm_repo.data_root,
                "crm",
                "synthetic_august2025_summary.json"
            )
            if os.path.exists(qb_file):
                with open(qb_file, 'r') as f:
                    qb_data = json.load(f)
                    qb_customers = qb_data.get('customers', [])
                    for customer in qb_customers:
                        customer['source'] = 'quickbase'
                        customer['customer_type'] = 'quickbase_import'
                        # Standardize field names
                        if 'person_name' in customer and 'name' not in customer:
                            customer['name'] = customer['person_name']
                        if 'user_id' in customer and 'id' not in customer:
                            customer['id'] = customer['user_id']
                        all_customers.append(customer)
        except Exception as e:
            pass  # QuickBase file not found or invalid
        
        # Get demo users (stored separately)
        try:
            import json
            import os
            demo_file = os.path.join(
                self.crm_repo.data_root,
                "crm",
                "demo_users.jsonl"
            )
            if os.path.exists(demo_file):
                with open(demo_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            demo_user = json.loads(line)
                            demo_user['source'] = 'demo'
                            demo_user['customer_type'] = 'demo_user'
                            # Standardize field names
                            if 'person_name' in demo_user and 'name' not in demo_user:
                                demo_user['name'] = demo_user['person_name']
                            if 'user_id' in demo_user and 'id' not in demo_user:
                                demo_user['id'] = demo_user['user_id']
                            all_customers.append(demo_user)
        except Exception as e:
            pass  # Demo users file not found or invalid
        
        return all_customers
    
    def get_customer_by_id(self, customer_id: str):
        """Get specific customer by ID."""
        customers = self.get_all_customers()
        for customer in customers:
            # Check multiple possible ID fields
            if (customer.get("customer_id") == customer_id or 
                customer.get("user_id") == customer_id or
                customer.get("id") == customer_id):
                return customer
        return None
    
    def _persist_session_data(self) -> None:
        """Persist session data to user file."""
        uid = st.session_state.get("anonymous_uid") or st.session_state.get("uid")
        if uid:
            user_data = {**st.session_state}
            save_user(uid, user_data)


class StreamlitCRMLogger(CRMEventLogger):
    """Streamlit-specific CRM event logging."""
    
    def log_lead_created(self, lead_data: LeadData) -> None:
        """Log lead creation using Streamlit logging system."""
        log_event(
            "crm.lead.created",
            {
                "lead_id": lead_data.lead_id,
                "engagement_source": lead_data.engagement_source,
                "created_at": lead_data.created_at,
                "has_name": bool(lead_data.contact_info.name),
                "has_email": bool(lead_data.contact_info.email),
                "has_phone": bool(lead_data.contact_info.phone),
                "source": lead_data.contact_info.source,
            }
        )
    
    def log_lead_converted(self, customer_data: CustomerData) -> None:
        """Log lead conversion using Streamlit logging system."""
        log_event(
            "crm.lead.converted",
            {
                "lead_id": customer_data.lead_id,
                "customer_id": customer_data.customer_id,
                "conversion_source": customer_data.conversion_source,
                "converted_at": customer_data.converted_at,
                "has_name": bool(customer_data.contact_info.name),
                "has_email": bool(customer_data.contact_info.email),
                "has_phone": bool(customer_data.contact_info.phone),
            }
        )


# Singleton instance for the app
_storage_provider = StreamlitCRMStorage()
_logger_provider = StreamlitCRMLogger()


def get_crm_storage() -> StreamlitCRMStorage:
    """Get the app's CRM storage provider."""
    return _storage_provider


def get_crm_logger() -> CRMEventLogger:
    """Get the app's CRM event logger."""
    return _logger_provider


def get_all_crm_customers():
    """Helper function to get all customers for CRM app."""
    return _storage_provider.get_all_customers()


def get_crm_customer_by_id(customer_id: str):
    """Helper function to get specific customer for CRM app."""
    return _storage_provider.get_customer_by_id(customer_id)


def delete_crm_customer(customer_id: str) -> bool:
    """Delete a customer from all CRM sources. Returns True if deleted from any source."""
    import json
    import os
    from pathlib import Path
    
    deleted = False
    
    # Get data root path
    try:
        data_root = Path(_storage_provider.crm_repo.data_root)
    except Exception:
        # Try relative to current working directory
        data_root = Path("data")
        # If that doesn't exist, try relative to this file
        if not data_root.exists():
            script_dir = Path(__file__).parent.parent.parent
            data_root = script_dir / "data"
    
    # Try to delete from Navigator app customers (JSONL)
    try:
        customers_file = data_root / "crm" / "customers.jsonl"
        
        if customers_file.exists():
            customers = []
            original_count = 0
            with open(customers_file, 'r') as f:
                for line in f:
                    original_count += 1
                    customer = json.loads(line)
                    # Check multiple ID fields
                    if not any([
                        customer.get('id') == customer_id,
                        customer.get('customer_id') == customer_id,
                        customer.get('user_id') == customer_id
                    ]):
                        customers.append(customer)
            
            if len(customers) < original_count:
                with open(customers_file, 'w') as f:
                    for customer in customers:
                        f.write(json.dumps(customer) + '\n')
                deleted = True
    except Exception:
        pass
    
    # Try to delete from QuickBase synthetic data (JSON)
    try:
        qb_file = data_root / "crm" / "synthetic_august2025_summary.json"
        if qb_file.exists():
            with open(qb_file, 'r') as f:
                qb_data = json.load(f)
            
            customers = qb_data.get('customers', [])
            original_count = len(customers)
            # Check multiple ID fields
            customers = [c for c in customers if not any([
                c.get('user_id') == customer_id,
                c.get('id') == customer_id,
                c.get('customer_id') == customer_id
            ])]
            
            if len(customers) < original_count:
                qb_data['customers'] = customers
                qb_data['record_count'] = len(customers)
                with open(qb_file, 'w') as f:
                    json.dump(qb_data, f, indent=2)
                deleted = True
    except Exception:
        pass
    
    # Try to delete from demo users (JSONL)
    try:
        demo_file = data_root / "crm" / "demo_users.jsonl"
        if demo_file.exists():
            demo_users = []
            original_demo_count = 0
            with open(demo_file, 'r') as f:
                for line in f:
                    original_demo_count += 1
                    user = json.loads(line)
                    # Check multiple ID fields
                    if not any([
                        user.get('user_id') == customer_id,
                        user.get('id') == customer_id,
                        user.get('customer_id') == customer_id
                    ]):
                        demo_users.append(user)
            
            if len(demo_users) < original_demo_count:
                with open(demo_file, 'w') as f:
                    for user in demo_users:
                        f.write(json.dumps(user) + '\n')
                deleted = True
    except Exception:
        pass
    
    return deleted