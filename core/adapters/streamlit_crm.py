"""
Streamlit-Specific CRM Implementation

Implements the CRM SDK interfaces using Streamlit session state and logging.
This is the app-specific adapter that can be easily swapped out.

When extracting to SDK, this file stays with the app, not the SDK.
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


class StreamlitCRMStorage(CRMStorageProvider):
    """Streamlit session-based CRM storage implementation."""
    
    def save_lead(self, lead_data: LeadData) -> None:
        """Save lead to Streamlit session state and user persistence."""
        # Store in session state
        st.session_state["_crm_lead_data"] = {
            "lead_id": lead_data.lead_id,
            "contact_info": lead_data.contact_info.__dict__,
            "engagement_source": lead_data.engagement_source,
            "created_at": lead_data.created_at,
            "status": lead_data.status,
            "metadata": lead_data.metadata or {}
        }
        
        # Persist to user file
        self._persist_session_data()
    
    def save_customer(self, customer_data: CustomerData) -> None:
        """Save customer to Streamlit session state and user persistence."""
        # Store in session state
        st.session_state["_crm_customer_data"] = {
            "customer_id": customer_data.customer_id,
            "lead_id": customer_data.lead_id,
            "contact_info": customer_data.contact_info.__dict__,
            "conversion_source": customer_data.conversion_source,
            "converted_at": customer_data.converted_at,
            "status": customer_data.status,
            "metadata": customer_data.metadata or {}
        }
        
        # Persist to user file
        self._persist_session_data()
    
    def get_crm_status(self, session_id: str) -> Optional[CRMStatus]:
        """Get CRM status from Streamlit session state."""
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
        
        # Persist to user file
        self._persist_session_data()
    
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


def get_crm_storage() -> CRMStorageProvider:
    """Get the app's CRM storage provider."""
    return _storage_provider


def get_crm_logger() -> CRMEventLogger:
    """Get the app's CRM event logger."""
    return _logger_provider