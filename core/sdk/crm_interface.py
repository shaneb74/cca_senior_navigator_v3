"""
CRM Interface SDK - App-Agnostic Core

This module defines the contract between applications and CRM systems.
Designed to be extracted as a standalone SDK in the future.

Key Principles:
- No Streamlit dependencies
- No app-specific logic
- Pure data transformation and ID management
- Clear interface contracts
- Easily testable and portable

Usage:
    from core.sdk.crm_interface import CRMClient
    
    crm = CRMClient()
    lead_id = crm.create_lead(contact_info)
    customer_id = crm.convert_to_customer(lead_id, booking_info)
"""

from __future__ import annotations

import uuid
import time
from typing import Dict, Any, Optional, Protocol
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class ContactInfo:
    """Standard contact information structure."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None  # "pfma", "gcp", "cost_planner"
    session_id: Optional[str] = None


@dataclass
class LeadData:
    """Lead record structure for CRM."""
    lead_id: str
    contact_info: ContactInfo
    engagement_source: str
    created_at: int
    status: str = "active"
    metadata: Dict[str, Any] = None


@dataclass
class CustomerData:
    """Customer record structure for CRM."""
    customer_id: str
    lead_id: str  # Attribution
    contact_info: ContactInfo
    conversion_source: str
    converted_at: int
    status: str = "active"
    metadata: Dict[str, Any] = None


@dataclass
class CRMStatus:
    """Current CRM status for a user."""
    user_type: str  # "visitor", "lead", "customer"
    lead_id: Optional[str] = None
    customer_id: Optional[str] = None
    created_at: Optional[int] = None
    converted_at: Optional[int] = None


class CRMStorageProvider(Protocol):
    """Interface for CRM data persistence."""
    
    def save_lead(self, lead_data: LeadData) -> None:
        """Save lead record to storage."""
        ...
    
    def save_customer(self, customer_data: CustomerData) -> None:
        """Save customer record to storage."""
        ...
    
    def get_crm_status(self, session_id: str) -> Optional[CRMStatus]:
        """Get CRM status for session."""
        ...
    
    def update_crm_status(self, session_id: str, status: CRMStatus) -> None:
        """Update CRM status for session."""
        ...


class CRMEventLogger(Protocol):
    """Interface for CRM event logging."""
    
    def log_lead_created(self, lead_data: LeadData) -> None:
        """Log lead creation event."""
        ...
    
    def log_lead_converted(self, customer_data: CustomerData) -> None:
        """Log lead conversion event."""
        ...


class CRMClient:
    """Core CRM client - app-agnostic business logic."""
    
    def __init__(self, storage: CRMStorageProvider, logger: CRMEventLogger):
        self.storage = storage
        self.logger = logger
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID with timestamp and random component."""
        timestamp = int(time.time())
        random_part = uuid.uuid4().hex[:8]
        return f"{prefix}_{timestamp}_{random_part}"
    
    def create_lead(self, contact_info: ContactInfo, engagement_source: str, session_id: str) -> str:
        """Create new lead record.
        
        Args:
            contact_info: User contact information
            engagement_source: Where engagement started ("pfma", "gcp", etc.)
            session_id: Session identifier for tracking
            
        Returns:
            lead_id: Generated lead identifier
        """
        # Check if lead already exists for this session
        current_status = self.storage.get_crm_status(session_id)
        if current_status and current_status.lead_id:
            return current_status.lead_id
        
        # Generate new lead
        lead_id = self._generate_id("lead")
        lead_data = LeadData(
            lead_id=lead_id,
            contact_info=contact_info,
            engagement_source=engagement_source,
            created_at=int(time.time()),
            metadata={"session_id": session_id}
        )
        
        # Save to storage
        self.storage.save_lead(lead_data)
        
        # Update status
        status = CRMStatus(
            user_type="lead",
            lead_id=lead_id,
            created_at=lead_data.created_at
        )
        self.storage.update_crm_status(session_id, status)
        
        # Log event
        self.logger.log_lead_created(lead_data)
        
        return lead_id
    
    def convert_to_customer(self, contact_info: ContactInfo, conversion_source: str, session_id: str) -> str:
        """Convert lead to customer.
        
        Args:
            contact_info: Updated contact information
            conversion_source: What triggered conversion ("appointment_booking")
            session_id: Session identifier
            
        Returns:
            customer_id: Generated customer identifier
        """
        # Get current status
        current_status = self.storage.get_crm_status(session_id)
        if not current_status or not current_status.lead_id:
            # Create lead first if it doesn't exist
            lead_id = self.create_lead(contact_info, "unknown", session_id)
            current_status = self.storage.get_crm_status(session_id)
        
        # Check if already converted
        if current_status.customer_id:
            return current_status.customer_id
        
        # Generate customer
        customer_id = self._generate_id("customer")
        customer_data = CustomerData(
            customer_id=customer_id,
            lead_id=current_status.lead_id,
            contact_info=contact_info,
            conversion_source=conversion_source,
            converted_at=int(time.time()),
            metadata={"session_id": session_id}
        )
        
        # Save to storage
        self.storage.save_customer(customer_data)
        
        # Update status
        status = CRMStatus(
            user_type="customer",
            lead_id=current_status.lead_id,
            customer_id=customer_id,
            created_at=current_status.created_at,
            converted_at=customer_data.converted_at
        )
        self.storage.update_crm_status(session_id, status)
        
        # Log event
        self.logger.log_lead_converted(customer_data)
        
        return customer_id
    
    def get_status(self, session_id: str) -> CRMStatus:
        """Get current CRM status for session.
        
        Returns:
            CRMStatus with current user type and IDs
        """
        status = self.storage.get_crm_status(session_id)
        if not status:
            return CRMStatus(user_type="visitor")
        return status