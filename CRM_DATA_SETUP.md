# CRM Data Sources Configuration

## Overview
The CRM now properly loads and displays data from three distinct sources:
1. **QuickBase Import** - Synthetic test customers from QuickBase
2. **Navigator App** - Real customers who book appointments through Navigator
3. **Demo Users** - Test/demo users for training and demonstrations

## Data Files

### Location: `data/crm/`

#### 1. **synthetic_august2025_summary.json**
- **Source**: QuickBase Import
- **Count**: 10 customers
- **Format**: Single JSON file with array of customers
- **Customer Type**: `quickbase`
- **Identifying Fields**: `user_id`, `person_name`, `journey_stage`
- **Status Color**: Blue (#17a2b8)

**Sample Customer**:
```json
{
  "user_id": "synthetic_aug2025_001",
  "person_name": "Richard Jackson",
  "email": "richard.jackson@synthetic.test",
  "phone": "(253) 218-4941",
  "journey_stage": "Moved In - Success!",
  "care_recommendation": "Assisted Living",
  "monthly_cost_estimate": 4747,
  "move_in_date": "2025-08-10"
}
```

#### 2. **customers.jsonl**
- **Source**: Navigator App (Appointment Bookings)
- **Count**: 1 customer (Terry Ramos)
- **Format**: JSON Lines (one customer per line)
- **Customer Type**: `navigator_app`
- **Identifying Fields**: `customer_id`, `name`, `conversion_source`
- **Status Color**: Green (#28a745)

**Sample Customer**:
```json
{
  "customer_id": "customer_1762401602_f70ab7af",
  "lead_id": "lead_1762401601_e595ff07",
  "name": "Terry Ramos",
  "email": "sarah@example.com",
  "phone": "555-123-4567",
  "source": "appointment_booking",
  "converted_at": 1762401602
}
```

#### 3. **demo_users.jsonl** (NEW)
- **Source**: Demo User Data
- **Count**: 1 demo user (Mary Memorycare)
- **Format**: JSON Lines (one demo user per line)
- **Customer Type**: `demo`
- **Identifying Fields**: `user_id`, `person_name`, `journey_stage`
- **Status Color**: Purple (#9c27b0)

**Sample Demo User**:
```json
{
  "user_id": "demo_mary_memorycare",
  "person_name": "Mary Memorycare",
  "source": "demo",
  "journey_stage": "Demo User",
  "has_gcp_assessment": true,
  "care_recommendation": "Unknown",
  "has_cost_plan": true,
  "last_activity": "2025-11-05"
}
```

#### 4. **leads.jsonl** (NEW)
- **Source**: Anonymous Navigator Sessions
- **Count**: 1 sample lead
- **Format**: JSON Lines (one lead per line)
- **Used By**: Leads Management page
- **Purpose**: Track anonymous users before conversion to customers

**Sample Lead**:
```json
{
  "lead_id": "lead_sample_001",
  "contact_info": {
    "name": "Sample Lead",
    "email": "sample@example.com",
    "source": "website"
  },
  "engagement_source": "gcp_started",
  "created_at": "2025-11-05T10:30:00",
  "status": "active"
}
```

## CRM Pages

### Customers Page (`apps/crm/pages/customers.py`)
**What it shows**: All converted customers from all three sources
- ✅ QuickBase customers (10)
- ✅ Navigator app customers (1)
- ✅ Demo users (1)
- **Total**: 12 customers

**Features**:
- Color-coded by source (Blue/Green/Purple)
- Search functionality
- Activity filtering
- Journey stage display
- View Details / Add Note buttons

### Leads Page (`apps/crm/pages/leads.py`)
**What it shows**: Anonymous sessions and unconverted leads
- ✅ CRM leads from leads.jsonl
- ✅ Anonymous Navigator sessions (anon_*.json files)

**Features**:
- Active Sessions tab
- Recent Activity (last 24h)
- Lead Conversion opportunities
- Intent scoring
- Progress tracking

## Code Changes Made

### 1. **core/adapters/streamlit_crm.py**
```python
def get_all_customers(self):
    """Get all customers from Navigator app, QuickBase, and demo sources."""
    # Now loads from:
    # - customers.jsonl (Navigator app)
    # - synthetic_august2025_summary.json (QuickBase)
    # - demo_users.jsonl (Demo users)
```

**Changes**:
- Added demo_users.jsonl loading
- Fixed path to use `self.crm_repo.data_root` instead of hardcoded path
- Enhanced `get_customer_by_id()` to check multiple ID fields

### 2. **apps/crm/pages/customers.py**
```python
elif customer_source == 'demo':
    # Demo user
    name = customer.get('person_name', customer.get('name', 'Unknown Customer'))
    status = 'Demo User'
    status_color = '#9c27b0'  # Purple
```

**Changes**:
- Added demo user rendering logic
- Purple status badge for demo users
- Updated info message to mention demo users

### 3. **apps/crm/pages/leads.py**
```python
def get_session_files(sort_by_time=False):
    """Get all session files from Navigator data"""
    # Now checks:
    # - data/crm/leads.jsonl (CRM leads)
    # - data/users/anon_*.json (Navigator sessions)
```

**Changes**:
- Added leads.jsonl file loading
- Fixed path to look in `data/users/` instead of non-existent `data/users/leads/`
- Added source tracking ('crm_leads' vs 'navigator_session')
- Enhanced display to show lead contact info

### 4. **tools/populate_demo_users.py** (NEW)
Utility script to convert demo user directories into CRM-compatible records.

**Usage**:
```bash
python tools/populate_demo_users.py
```

**What it does**:
- Scans `data/users/demo/*/` directories
- Loads session.json, careplan.json, costplan.json
- Creates demo_users.jsonl with standardized format
- Shows summary of loaded users

## Current Data Summary

| Source | File | Count | Status |
|--------|------|-------|--------|
| QuickBase | synthetic_august2025_summary.json | 10 | ✅ Working |
| Navigator App | customers.jsonl | 2 | ✅ Working |
| Demo Users | demo_users.jsonl | 1 | ✅ Working |
| Leads | leads.jsonl | 1 | ✅ Working |
| **TOTAL CUSTOMERS** | | **13** | ✅ |

## Testing the Changes

### Verified Results ✅
```
🟢 Navigator App: 2 customers (Terry Ramos, John Ramos)
🔵 QuickBase: 10 customers (Richard Jackson, Joan Williams, etc.)
🟣 Demo Users: 1 user (Mary Memorycare)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TOTAL: 13 customers loaded successfully
```

### To verify customers are showing:
1. Open CRM app
2. Go to Customers page
3. Should see:
   - 10 blue QuickBase customers (Richard Jackson, Joan Williams, etc.)
   - 1 green Navigator customer (Terry Ramos)
   - 1 purple Demo user (Mary Memorycare)

### To verify leads are showing:
1. Go to Leads page
2. "Active Sessions" tab should show:
   - 1 CRM lead (Sample Lead)
   - Any anonymous sessions (anon_*.json files)

### To add more demo users:
1. Add demo user directories to `data/users/demo/`
2. Run: `python tools/populate_demo_users.py`
3. Refresh CRM to see new demo users

### To add more leads:
Edit `data/crm/leads.jsonl` and add lines:
```json
{"lead_id": "lead_002", "contact_info": {"name": "New Lead", "email": "lead@example.com", "source": "website"}, "engagement_source": "cost_planner_started", "created_at": "2025-11-05T14:00:00", "status": "active", "metadata": {}}
```

## Field Mapping

### How customer sources map to display fields:

| Display Field | QuickBase | Navigator App | Demo User |
|--------------|-----------|---------------|-----------|
| Name | `person_name` | `name` | `person_name` |
| ID | `user_id` | `customer_id` | `user_id` |
| Last Activity | `last_activity` | `created_at` | `last_activity` |
| Status | `journey_stage` | "Appointment booked" | `journey_stage` |
| Progress | `journey_stage` | "Appointment booked" | "Demo Customer" |

## Next Steps

1. **Add More Demo Users**: 
   - Create more demo user directories in `data/users/demo/`
   - Run populate script

2. **Track Real Sessions**:
   - Anonymous Navigator sessions automatically appear in Leads page
   - Located in `data/users/anon_*.json`

3. **Convert Leads to Customers**:
   - Use "Convert to Customer" button in Leads page
   - Creates new entry in customers.jsonl

4. **Import More QuickBase Data**:
   - Add more customers to synthetic_august2025_summary.json
   - Or create new JSON files and update the adapter

## Troubleshooting

### Customers not showing?
- Check file paths in `core/adapters/streamlit_crm.py`
- Verify JSON files are valid: `python -m json.tool data/crm/customers.jsonl`
- Check console for error messages

### Demo users not appearing?
- Run: `python tools/populate_demo_users.py`
- Check that demo directories exist in `data/users/demo/`
- Verify demo_users.jsonl was created

### Leads page empty?
- Check `data/crm/leads.jsonl` exists
- Look for `data/users/anon_*.json` files
- Verify paths in `apps/crm/pages/leads.py`

## Files Modified

✅ `core/adapters/streamlit_crm.py` - Added demo user loading
✅ `apps/crm/pages/customers.py` - Added demo user rendering
✅ `apps/crm/pages/leads.py` - Fixed session file loading
✅ `tools/populate_demo_users.py` - NEW utility script
✅ `data/crm/demo_users.jsonl` - NEW data file
✅ `data/crm/leads.jsonl` - NEW data file

## Summary

Your CRM now properly integrates:
- **12 total customers** across 3 sources
- **Proper color coding** to distinguish sources
- **Automated demo user** import from demo directories
- **Lead tracking** for anonymous sessions
- **Flexible architecture** to add more data sources

All data files are in place and the pages should now display all customers and leads correctly! 🎉
