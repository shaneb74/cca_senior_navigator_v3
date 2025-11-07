"""
CRM Integration for Senior Navigator App

Clean interface between the app and CRM SDK. This module handles the 
app-specific CRM integration while keeping the core logic in the SDK.

When the SDK is extracted, this file will import from the external SDK
instead of the local core/sdk/ directory.

Usage:
    from core.crm_ids import create_lead, convert_to_customer, get_crm_status
    
    # Generate lead on form interaction
    lead_id = create_lead(name="John Doe", email="john@example.com", source="pfma")
    
    # Convert to customer on appointment booking
    customer_id = convert_to_customer(source="appointment_booking")
    
    # Check current status
    status = get_crm_status()  # Returns {"user_type": "customer", "lead_id": "...", "customer_id": "..."}
"""

from typing import Optional, Dict, Any
import streamlit as st

from core.sdk.crm_interface import CRMClient, ContactInfo
from core.adapters.streamlit_crm import get_crm_storage, get_crm_logger


def _get_session_id() -> str:
    """Get session ID for CRM tracking."""
    return st.session_state.get("anonymous_uid") or st.session_state.get("uid") or "unknown"


def _get_crm_client() -> CRMClient:
    """Get configured CRM client."""
    storage = get_crm_storage()
    logger = get_crm_logger()
    return CRMClient(storage, logger)


def create_lead(name: Optional[str] = None, email: Optional[str] = None, 
                phone: Optional[str] = None, source: str = "unknown") -> str:
    """Create lead record on first meaningful engagement.
    
    Args:
        name: Contact name (optional)
        email: Contact email (optional)
        phone: Contact phone (optional)
        source: Engagement source ("pfma", "gcp", "cost_planner")
        
    Returns:
        lead_id: Generated lead identifier
    """
    contact_info = ContactInfo(
        name=name,
        email=email,
        phone=phone,
        source=source,
        session_id=_get_session_id()
    )
    
    client = _get_crm_client()
    return client.create_lead(contact_info, source, _get_session_id())


def convert_to_customer(name: Optional[str] = None, email: Optional[str] = None,
                       phone: Optional[str] = None, source: str = "appointment_booking") -> str:
    """Convert lead to customer on appointment booking.
    
    Args:
        name: Updated contact name (optional)
        email: Updated contact email (optional)  
        phone: Updated contact phone (optional)
        source: Conversion source ("appointment_booking")
        
    Returns:
        customer_id: Generated customer identifier
    """
    contact_info = ContactInfo(
        name=name,
        email=email,
        phone=phone,
        source=source,
        session_id=_get_session_id()
    )
    
    client = _get_crm_client()
    return client.convert_to_customer(contact_info, source, _get_session_id())


def get_crm_status() -> Dict[str, Any]:
    """Get current CRM status for user.
    
    Returns:
        Dict with user_type, lead_id, customer_id, timestamps
    """
    client = _get_crm_client()
    status = client.get_status(_get_session_id())
    
    return {
        "user_type": status.user_type,
        "lead_id": status.lead_id,
        "customer_id": status.customer_id,
        "created_at": status.created_at,
        "converted_at": status.converted_at,
    }


def is_lead() -> bool:
    """Check if user has lead status."""
    status = get_crm_status()
    return status["user_type"] == "lead"


def is_customer() -> bool:
    """Check if user has customer status."""
    status = get_crm_status()
    return status["user_type"] == "customer"


# Legacy compatibility functions for existing code
def get_or_create_lead_id() -> str:
    """Legacy: Create lead with minimal info."""
    return create_lead(source="legacy_call")


def convert_lead_to_customer() -> str:
    """Legacy: Convert lead to customer with minimal info."""
    return convert_to_customer(source="legacy_conversion")


def get_crm_ids() -> Dict[str, Optional[str]]:
    """Legacy: Get CRM IDs in old format."""
    status = get_crm_status()
    return {
        "lead_id": status["lead_id"],
        "customer_id": status["customer_id"],
        "status": status["user_type"],
    }