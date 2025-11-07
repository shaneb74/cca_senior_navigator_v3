"""
CRM-specific data repository using JSON-Lines persistence.

This module handles CRM data that is separate from Navigator customer data:
- Advisor notes and interactions
- Appointments and scheduling
- CRM-specific customer metadata
- Internal workflow data
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid


@dataclass
class AdvisorNote:
    """Advisor note about a customer interaction."""
    id: str
    customer_id: str
    advisor_name: str
    note_type: str  # "call", "email", "meeting", "follow_up", "assessment"
    content: str
    created_at: datetime
    follow_up_date: Optional[datetime] = None
    priority: str = "normal"  # "low", "normal", "high", "urgent"


@dataclass
class Appointment:
    """Scheduled appointment with a customer."""
    id: str
    customer_id: str
    advisor_name: str
    appointment_type: str  # "consultation", "follow_up", "assessment", "planning"
    scheduled_at: datetime
    duration_minutes: int
    status: str  # "scheduled", "completed", "cancelled", "no_show"
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class CustomerCrmMetadata:
    """CRM-specific metadata about a customer."""
    customer_id: str
    advisor_assigned: Optional[str] = None
    priority_level: str = "normal"  # "low", "normal", "high", "urgent"
    tags: List[str] = None  # ["new_customer", "follow_up_needed", "completed"]
    lead_source: Optional[str] = None  # "website", "referral", "marketing"
    first_contact_date: Optional[datetime] = None
    last_contact_date: Optional[datetime] = None
    status: str = "active"  # "active", "inactive", "converted", "archived"
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class CrmRepository:
    """Repository for CRM-specific data operations."""
    
    def __init__(self, data_root: str = "data"):
        self.data_root = Path(data_root)
        self.crm_dir = self.data_root / "crm"
        self.crm_dir.mkdir(parents=True, exist_ok=True)
    
    # --- Advisor Notes ---
    
    def add_advisor_note(self, customer_id: str, advisor_name: str, 
                        note_type: str, content: str, 
                        follow_up_date: Optional[datetime] = None,
                        priority: str = "normal") -> AdvisorNote:
        """Add a new advisor note."""
        note = AdvisorNote(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            advisor_name=advisor_name,
            note_type=note_type,
            content=content,
            created_at=datetime.now(),
            follow_up_date=follow_up_date,
            priority=priority
        )
        
        self._append_to_jsonl("advisor_notes.jsonl", asdict(note))
        return note
    
    def get_customer_notes(self, customer_id: str) -> List[AdvisorNote]:
        """Get all advisor notes for a customer."""
        notes = self._load_from_jsonl("advisor_notes.jsonl")
        customer_notes = [n for n in notes if n.get("customer_id") == customer_id]
        
        return [AdvisorNote(
            id=n["id"],
            customer_id=n["customer_id"],
            advisor_name=n["advisor_name"],
            note_type=n["note_type"],
            content=n["content"],
            created_at=datetime.fromisoformat(n["created_at"]),
            follow_up_date=datetime.fromisoformat(n["follow_up_date"]) if n.get("follow_up_date") else None,
            priority=n.get("priority", "normal")
        ) for n in customer_notes]
    
    def get_all_notes(self) -> List[AdvisorNote]:
        """Get all advisor notes."""
        notes = self._load_from_jsonl("advisor_notes.jsonl")
        
        return [AdvisorNote(
            id=n["id"],
            customer_id=n["customer_id"],
            advisor_name=n["advisor_name"],
            note_type=n["note_type"],
            content=n["content"],
            created_at=datetime.fromisoformat(n["created_at"]),
            follow_up_date=datetime.fromisoformat(n["follow_up_date"]) if n.get("follow_up_date") else None,
            priority=n.get("priority", "normal")
        ) for n in notes]
    
    # --- Appointments ---
    
    def schedule_appointment(self, customer_id: str, advisor_name: str,
                           appointment_type: str, scheduled_at: datetime,
                           duration_minutes: int = 60) -> Appointment:
        """Schedule a new appointment."""
        appointment = Appointment(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            advisor_name=advisor_name,
            appointment_type=appointment_type,
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes,
            status="scheduled",
            created_at=datetime.now()
        )
        
        self._append_to_jsonl("appointments.jsonl", asdict(appointment))
        return appointment
    
    def get_customer_appointments(self, customer_id: str) -> List[Appointment]:
        """Get all appointments for a customer."""
        appointments = self._load_from_jsonl("appointments.jsonl")
        customer_appointments = [a for a in appointments if a.get("customer_id") == customer_id]
        
        return [Appointment(
            id=a["id"],
            customer_id=a["customer_id"],
            advisor_name=a["advisor_name"],
            appointment_type=a["appointment_type"],
            scheduled_at=datetime.fromisoformat(a["scheduled_at"]),
            duration_minutes=a["duration_minutes"],
            status=a["status"],
            notes=a.get("notes"),
            created_at=datetime.fromisoformat(a["created_at"]) if a.get("created_at") else None
        ) for a in customer_appointments]
    
    def update_appointment_status(self, appointment_id: str, status: str, notes: Optional[str] = None):
        """Update appointment status and notes."""
        appointments = self._load_from_jsonl("appointments.jsonl")
        
        for appointment in appointments:
            if appointment["id"] == appointment_id:
                appointment["status"] = status
                if notes:
                    appointment["notes"] = notes
                break
        
        self._save_to_jsonl("appointments.jsonl", appointments)
    
    # --- Customer CRM Metadata ---
    
    def set_customer_metadata(self, customer_id: str, **kwargs) -> CustomerCrmMetadata:
        """Set or update CRM metadata for a customer."""
        metadata_list = self._load_from_jsonl("customer_metadata.jsonl")
        
        # Find existing metadata
        existing = None
        for i, meta in enumerate(metadata_list):
            if meta.get("customer_id") == customer_id:
                existing = i
                break
        
        # Create or update metadata
        if existing is not None:
            metadata_list[existing].update(kwargs)
            metadata_dict = metadata_list[existing]
        else:
            metadata_dict = {"customer_id": customer_id, **kwargs}
            metadata_list.append(metadata_dict)
        
        # Save back to file
        self._save_to_jsonl("customer_metadata.jsonl", metadata_list)
        
        return CustomerCrmMetadata(
            customer_id=metadata_dict["customer_id"],
            advisor_assigned=metadata_dict.get("advisor_assigned"),
            priority_level=metadata_dict.get("priority_level", "normal"),
            tags=metadata_dict.get("tags", []),
            lead_source=metadata_dict.get("lead_source"),
            first_contact_date=datetime.fromisoformat(metadata_dict["first_contact_date"]) if metadata_dict.get("first_contact_date") else None,
            last_contact_date=datetime.fromisoformat(metadata_dict["last_contact_date"]) if metadata_dict.get("last_contact_date") else None,
            status=metadata_dict.get("status", "active")
        )
    
    def get_customer_metadata(self, customer_id: str) -> Optional[CustomerCrmMetadata]:
        """Get CRM metadata for a customer."""
        metadata_list = self._load_from_jsonl("customer_metadata.jsonl")
        
        for meta in metadata_list:
            if meta.get("customer_id") == customer_id:
                return CustomerCrmMetadata(
                    customer_id=meta["customer_id"],
                    advisor_assigned=meta.get("advisor_assigned"),
                    priority_level=meta.get("priority_level", "normal"),
                    tags=meta.get("tags", []),
                    lead_source=meta.get("lead_source"),
                    first_contact_date=datetime.fromisoformat(meta["first_contact_date"]) if meta.get("first_contact_date") else None,
                    last_contact_date=datetime.fromisoformat(meta["last_contact_date"]) if meta.get("last_contact_date") else None,
                    status=meta.get("status", "active")
                )
        
        return None
    
    # --- Generic Record Management ---
    
    def add_record(self, record_type: str, record_data: Dict[str, Any]) -> str:
        """Add a generic record and return its ID."""
        record_id = str(uuid.uuid4())
        record_data["id"] = record_id
        record_data["created_at"] = datetime.now()
        
        filename = f"{record_type}.jsonl"
        self._append_to_jsonl(filename, record_data)
        return record_id
    
    def list_records(self, record_type: str) -> List[Dict[str, Any]]:
        """List all records of a given type."""
        filename = f"{record_type}.jsonl"
        return self._load_from_jsonl(filename)
    
    def get_record(self, record_type: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific record by ID."""
        records = self.list_records(record_type)
        for record in records:
            if record.get("id") == record_id:
                return record
        return None
    
    def update_record(self, record_type: str, record_id: str, updates: Dict[str, Any]) -> bool:
        """Update a record with new data."""
        records = self.list_records(record_type)
        for record in records:
            if record.get("id") == record_id:
                record.update(updates)
                record["updated_at"] = datetime.now()
                filename = f"{record_type}.jsonl"
                self._save_to_jsonl(filename, records)
                return True
        return False
    
    def delete_record(self, record_type: str, record_id: str) -> bool:
        """Delete a record by ID. Handles multiple ID field names."""
        records = self.list_records(record_type)
        original_count = len(records)
        
        # Check multiple possible ID fields
        records = [r for r in records if not any([
            r.get("id") == record_id,
            r.get("customer_id") == record_id,
            r.get("user_id") == record_id,
            r.get("lead_id") == record_id
        ])]
        
        if len(records) < original_count:
            filename = f"{record_type}.jsonl"
            self._save_to_jsonl(filename, records)
            return True
        return False
    
    # --- Utility Methods ---
    
    def _load_from_jsonl(self, filename: str) -> List[Dict[str, Any]]:
        """Load data from a JSON-Lines file."""
        file_path = self.crm_dir / filename
        
        if not file_path.exists():
            return []
        
        data = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data.append(json.loads(line))
        except (json.JSONDecodeError, FileNotFoundError):
            return []
        
        return data
    
    def _append_to_jsonl(self, filename: str, record: Dict[str, Any]):
        """Append a record to a JSON-Lines file."""
        file_path = self.crm_dir / filename
        
        # Convert datetime objects to ISO format
        record_copy = self._serialize_datetime(record)
        
        with open(file_path, 'a') as f:
            f.write(json.dumps(record_copy, ensure_ascii=False) + '\n')
    
    def _save_to_jsonl(self, filename: str, records: List[Dict[str, Any]]):
        """Save all records to a JSON-Lines file (overwrites existing)."""
        file_path = self.crm_dir / filename
        
        with open(file_path, 'w') as f:
            for record in records:
                record_copy = self._serialize_datetime(record)
                f.write(json.dumps(record_copy, ensure_ascii=False) + '\n')
    
    def _serialize_datetime(self, obj: Any) -> Any:
        """Convert datetime objects to ISO format for JSON serialization."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._serialize_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetime(item) for item in obj]
        else:
            return obj


# Singleton instance for easy access
crm_data = CrmRepository()