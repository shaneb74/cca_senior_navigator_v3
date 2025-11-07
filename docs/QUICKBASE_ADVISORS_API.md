# QuickBase Advisors API Integration

## Overview

The QuickBase client now supports fetching active advisor data from the WA Clients table. This provides a real-time list of advisors who are currently assigned to clients.

---

## Active Advisors (from Screenshot)

The following advisors are currently active in the WA Clients table:

| # | Advisor Name | Email | Territory |
|---|--------------|-------|-----------|
| 1 | Ashley - Eastside Angst | ashley@conciergecareadvisors.com | Eastside |
| 2 | Chanda - Thurston Co. Hickman | chanda@conciergecareadvisors.com | Thurston County |
| 3 | Jennifer-North King James | jenniferj@conciergecareadvisors.com | North King County |
| 4 | Jenny- Pierce Co. Austin-Krzemien | jenny@conciergecareadvisors.com | Pierce County |
| 5 | JJ White | jj@conciergecareadvisors.com | - |
| 6 | Karine Stebbins | karine@conciergecareadvisors.com | - |
| 7 | Kelsey - Pierce Co Jochum | kelsey@conciergecareadvisors.com | Pierce County |
| 8 | Marta - S Snoho Street | marta@conciergecareadvisors.com | South Snohomish |

---

## API Usage

### Basic Usage

```python
from shared.data_access.quickbase_client import quickbase_client

# Fetch all active advisors
advisors = quickbase_client.get_active_advisors()

# Display advisors
for advisor in advisors:
    print(f"{advisor['name']} - {advisor['email']}")
```

### Response Format

Each advisor object contains:

```python
{
    "name": "Jenny- Pierce Co. Austin-Krzemien",
    "email": "jenny@conciergecareadvisors.com",
    "qb_user_id": "59668014.abc123"  # QuickBase user ID
}
```

### Advanced Usage

```python
# Get advisor by email
def get_advisor_by_email(email: str):
    advisors = quickbase_client.get_active_advisors()
    return next((a for a in advisors if a['email'] == email), None)

# Get advisor names for dropdown
def get_advisor_names():
    advisors = quickbase_client.get_active_advisors()
    return [a['name'] for a in advisors]

# Create advisor lookup dict
def get_advisor_lookup():
    advisors = quickbase_client.get_active_advisors()
    return {a['qb_user_id']: a for a in advisors}
```

---

## Data Source

**QuickBase Table**: WA Clients (`bkqfsmeuq`)

**Fields Used**:
- **Field 81**: Record - Advisor #1
- **Field 89**: Record - Advisor #2

The method queries all client records and extracts unique advisors from both advisor fields, ensuring we capture all currently active advisors.

---

## Fallback Behavior

If QuickBase API is unavailable or the requests library is not installed, the method returns mock data with the 8 active advisors listed above.

This ensures the CRM continues to function even if QuickBase connectivity is temporarily lost.

---

## Testing

A test script is provided to verify the advisor fetching:

```bash
python3 tools/test_advisors.py
```

**Expected Output**:
```
================================================================================
Testing QuickBase Active Advisors API
================================================================================

Fetching active advisors from QuickBase WA Clients table...

✅ Successfully retrieved 8 active advisors

================================================================================
#    Name                                       Email                              
================================================================================
1    Ashley - Eastside Angst                    ashley@conciergecareadvisors.com
2    Chanda - Thurston Co. Hickman              chanda@conciergecareadvisors.com
3    Jennifer-North King James                  jenniferj@conciergecareadvisors.com
4    Jenny- Pierce Co. Austin-Krzemien          jenny@conciergecareadvisors.com
5    JJ White                                   jj@conciergecareadvisors.com
6    Karine Stebbins                            karine@conciergecareadvisors.com
7    Kelsey - Pierce Co Jochum                  kelsey@conciergecareadvisors.com
8    Marta - S Snoho Street                     marta@conciergecareadvisors.com
================================================================================
```

---

## CRM Integration Use Cases

### 1. Advisor Assignment Dropdown

```python
import streamlit as st
from shared.data_access.quickbase_client import quickbase_client

# In CRM dashboard
advisors = quickbase_client.get_active_advisors()
advisor_names = [a['name'] for a in advisors]

selected_advisor = st.selectbox(
    "Assign to Advisor:",
    options=advisor_names
)
```

### 2. Filter Customers by Advisor

```python
# Get advisor's QB user ID
selected_advisor_obj = next(
    (a for a in advisors if a['name'] == selected_advisor),
    None
)

if selected_advisor_obj:
    # Filter customers assigned to this advisor
    # (would need to query WA Clients with advisor filter)
    pass
```

### 3. Advisor Metrics Dashboard

```python
# Show workload per advisor
for advisor in advisors:
    # Query number of clients assigned to each advisor
    # (would need additional QuickBase query)
    st.metric(
        label=advisor['name'],
        value="12 clients",  # from query
        delta="+2 this week"
    )
```

---

## Additional Advisor Data Available

Beyond the active advisors in WA Clients, there are **35 total advisors** in the Intake Forms table (field 47: "Name of Advisor"). This includes historical advisors who may have done intake but are no longer active.

To fetch all intake advisors (not just active ones), a similar method could be added:

```python
def get_all_intake_advisors(self) -> List[Dict[str, Any]]:
    """Fetch all advisors from Intake Forms table (historical + current)"""
    # Query bkpvi5e32, field 47
    pass
```

---

## Notes

- **Deduplication**: Advisors are deduplicated by QuickBase user ID
- **Sorting**: Results are sorted alphabetically by name
- **Real-time**: Data is fetched fresh on each call (consider caching for production)
- **Territory Naming**: Some advisors have territory in their name (Pierce Co., North King, etc.)
- **Email Domain**: All advisors use `@conciergecareadvisors.com` domain

---

## Future Enhancements

1. **Caching**: Add 24-hour cache to reduce API calls
2. **Advisor Workload**: Query client counts per advisor
3. **Territory Filtering**: Extract and expose territory information
4. **Historical Tracking**: Track advisor assignments over time
5. **Availability Status**: Add active/inactive status field
