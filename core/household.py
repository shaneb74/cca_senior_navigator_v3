"""
Household State Management Helpers

Provides functions for creating and managing household objects,
persons, care plans, and cost plans in session state.

These helpers abstract away the session state keys and ensure
consistent data structure across the application.
"""

from __future__ import annotations
from typing import Optional
from core.models import Household, Person, CarePlan, CostPlan


def ensure_household_state(st, zip: str | None = None) -> Household:
    """Get or create household in session state.
    
    Args:
        st: Streamlit module
        zip: ZIP code to initialize if creating new household
        
    Returns:
        Household object
    """
    hh_data = st.session_state.get("household.model")
    if not hh_data:
        hh = Household(zip=zip)
        st.session_state["household.model"] = hh.model_dump()
        return hh
    # Handle both dict and Household instances
    if isinstance(hh_data, Household):
        return hh_data
    return Household(**hh_data)


def add_person(st, role: str, zip: str | None = None) -> Person:
    """Add a person to the household.
    
    Args:
        st: Streamlit module
        role: "primary" or "partner"
        zip: ZIP code for household initialization
        
    Returns:
        Person object
    """
    hh = ensure_household_state(st, zip)
    p = Person(household_id=hh.uid, role=role)
    
    # Add to household members
    if p.uid not in hh.members:
        hh.members.append(p.uid)
    
    # Store person and update household
    st.session_state[f"person.{role}_id"] = p.uid
    st.session_state[f"person.{p.uid}.model"] = p.model_dump()
    st.session_state["household.model"] = hh.model_dump()
    
    return p


def set_careplan_for(st, person_id: str, cp: CarePlan) -> None:
    """Store a CarePlan for a person.
    
    Args:
        st: Streamlit module
        person_id: Person identifier
        cp: CarePlan object
    """
    st.session_state[f"careplan.{person_id}"] = cp.model_dump()


def get_careplan_for(st, person_id: str) -> Optional[CarePlan]:
    """Retrieve a CarePlan for a person.
    
    Args:
        st: Streamlit module
        person_id: Person identifier
        
    Returns:
        CarePlan object or None
    """
    d = st.session_state.get(f"careplan.{person_id}")
    if not d:
        return None
    # Handle both dict and CarePlan instances
    if isinstance(d, CarePlan):
        return d
    return CarePlan(**d)


def set_costplan_for(st, person_id: str, cos: CostPlan) -> None:
    """Store a CostPlan for a person.
    
    Args:
        st: Streamlit module
        person_id: Person identifier
        cos: CostPlan object
    """
    st.session_state[f"costplan.{person_id}"] = cos.model_dump()


def get_costplan_for(st, person_id: str) -> Optional[CostPlan]:
    """Retrieve a CostPlan for a person.
    
    Args:
        st: Streamlit module
        person_id: Person identifier
        
    Returns:
        CostPlan object or None
    """
    d = st.session_state.get(f"costplan.{person_id}")
    if not d:
        return None
    # Handle both dict and CostPlan instances
    if isinstance(d, CostPlan):
        return d
    return CostPlan(**d)
