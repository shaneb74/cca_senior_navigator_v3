# 🎯 Advisor CRM Hub - Professional Dashboard Design

## Executive Summary

Transform the CRM dashboard from a static metrics page into a **true advisor command center** with task queues, customer workflows, and QuickBase integration for advisor assignment and workload distribution.

---

## Current State Analysis

### What We Have:
- ✅ Basic metrics (3 customers, 1 GCP, 1 cost plan)
- ✅ QuickBase transformation messaging
- ✅ Customer data from Navigator app
- ✅ Appointments system (just built)
- ✅ QuickBase client with full API access

### What's Missing:
- ❌ No task queues or workflows
- ❌ No advisor assignment system
- ❌ No customer pipeline visualization
- ❌ No action items or follow-ups
- ❌ No QuickBase advisor data integration

---

## QuickBase Integration Opportunities

### Available QuickBase Data:

#### **WA Clients Table (bkqfsmeuq)**
Can pull for advisor assignment:
- **Field 47**: Advisor Name/ID
- **Field 142**: Stage (prospect, active, closed)
- **Field 6**: Date of Intake
- **Field 171**: Closing Date
- **Field 143**: Move-In Amount (revenue tracking)

#### **Activities Table (bkpvi3btn)**
Can pull for task tracking:
- Activity types
- Activity dates
- Assigned advisors
- Follow-up dates

#### **Value for CRM Hub:**
1. **Advisor Workload Distribution**: Pull current advisor assignments from QB
2. **Stage Pipeline**: Show prospects → active → closed by advisor
3. **Revenue Tracking**: Monthly move-in amounts by advisor
4. **Activity History**: Automatically import QB activities as tasks

---

## Proposed Dashboard Architecture

### **Layout Structure:**

```
┌─────────────────────────────────────────────────────────────┐
│  🏢 Advisor CRM Dashboard - [Advisor Name]                  │
├─────────────────────────────────────────────────────────────┤
│  📊 My Metrics                                              │
│  ┌─────┬─────┬─────┬─────┐                                 │
│  │ Active │ New │ Ready │ Revenue │                         │
│  │  12   │  3  │   5   │ $45.2K  │                         │
│  └─────┴─────┴─────┴─────┘                                 │
├─────────────────────────────────────────────────────────────┤
│  [My Tasks] [My Customers] [Team View] [Appointments]      │
├─────────────────────────────────────────────────────────────┤
│  🎯 ACTION REQUIRED (3)                                     │
│  ┌─────────────────────────────────────────┐              │
│  │ 🔴 Sarah Johnson - Follow-up overdue     │ [Contact]   │
│  │ 🟡 Mike Davis - Schedule community visit │ [Schedule]  │
│  │ 🟢 Lisa Chen - Assessment ready          │ [Review]    │
│  └─────────────────────────────────────────┘              │
├─────────────────────────────────────────────────────────────┤
│  📋 TODAY'S TASKS (5)                                       │
│  ┌─────────────────────────────────────────┐              │
│  │ ☐ Call: Margaret Wilson (2:00 PM)       │              │
│  │ ☐ Visit: Sunset Manor with Brown family │              │
│  │ ☐ Review: 3 new GCP assessments         │              │
│  └─────────────────────────────────────────┘              │
├─────────────────────────────────────────────────────────────┤
│  📅 UPCOMING APPOINTMENTS (2)                               │
│  ┌─────────────────────────────────────────┐              │
│  │ Tomorrow 10AM - Anderson family consult  │ [Details]   │
│  │ Friday 2PM - Garcia community tour       │ [Details]   │
│  └─────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

---

## Task Queue System Design

### **Task Types & Sources:**

#### **1. Navigator-Triggered Tasks (Auto-generated)**
```python
{
    "source": "navigator",
    "trigger": "gcp_complete",
    "task": "Review care assessment",
    "customer": "Margaret Wilson",
    "priority": "high",
    "due": "2025-11-07",
    "action": "Call to discuss AL recommendations"
}
```

**Auto-triggers:**
- ✅ GCP assessment completed → "Review assessment & schedule call"
- ✅ Cost plan completed → "Review budget & discuss communities"
- ✅ Appointment booked → "Prepare consultation materials"
- ✅ Care prep submitted → "Review preferences & create matches"

#### **2. Follow-up Tasks (CRM-generated)**
```python
{
    "source": "crm",
    "type": "follow_up",
    "customer": "Sarah Johnson",
    "last_contact": "2025-10-30",
    "days_since": 7,
    "priority": "urgent",
    "suggested_action": "Check in on community visits"
}
```

**Auto-generated follow-ups:**
- 3 days after appointment → "Follow-up: Did appointment happen?"
- 7 days after last contact → "Check in: Any updates?"
- 14 days no activity → "Re-engagement needed"

#### **3. QuickBase Synced Tasks**
```python
{
    "source": "quickbase",
    "qb_record_id": "12345",
    "advisor": "Sarah Chen",
    "activity_type": "Community Visit",
    "scheduled_date": "2025-11-08",
    "client_name": "Martinez Family"
}
```

#### **4. Manual Tasks (Advisor-created)**
```python
{
    "source": "manual",
    "created_by": "advisor_id_123",
    "task": "Send pricing comparison to Smith family",
    "due": "2025-11-08",
    "priority": "medium"
}
```

---

## Customer Pipeline Visualization

### **Stage-Based View:**

```
┌──────────────────────────────────────────────────────────────┐
│  📊 My Customer Pipeline                                     │
├──────────────────────────────────────────────────────────────┤
│  New Leads (3)    │ Assessing (5)  │ Touring (4)  │ Closing (2) │
│  ┌───────────┐   │ ┌───────────┐  │ ┌─────────┐  │ ┌─────────┐ │
│  │ Johnson   │   │ │ Wilson    │  │ │ Davis   │  │ │ Chen    │ │
│  │ Martinez  │   │ │ Anderson  │  │ │ Brown   │  │ │ Garcia  │ │
│  │ Taylor    │   │ │ Smith     │  │ │ Miller  │  │ └─────────┘ │
│  └───────────┘   │ │ Rodriguez │  │ │ Lee     │  │             │
│                  │ │ Thompson  │  │ └─────────┘  │             │
│  [+Add Lead]     │ └───────────┘  │              │             │
└──────────────────────────────────────────────────────────────┘
```

**Stage Definitions:**
1. **New Leads** - Just registered, no assessments
2. **Assessing** - In Navigator (GCP/Cost Planner in progress)
3. **Touring** - Communities selected, visits scheduled
4. **Closing** - Contract negotiation, move-in planning

---

## QuickBase Integration Strategy

### **Phase 1: Read-Only Integration (Week 1)**

**Pull advisor data to populate dashboard:**

```python
def sync_quickbase_advisors():
    """Pull advisor assignments and workload from QuickBase"""
    
    # Query WA Clients for advisor workload
    query = {
        "from": "bkqfsmeuq",  # WA Clients
        "select": [47, 142, 6, 171, 143],  # Advisor, Stage, Dates, Amount
        "where": "{142.EX.'Active'}OR{142.EX.'Prospect'}"
    }
    
    # Build advisor workload summary
    advisor_workload = {
        "Sarah Chen": {
            "active_clients": 12,
            "new_leads": 3,
            "ready_for_tour": 5,
            "monthly_revenue": 45200
        }
    }
    
    return advisor_workload
```

**Use Cases:**
- Show advisor's current QB customers in CRM
- Display QB activities as tasks
- Compare Navigator vs QB customer lists
- Identify customers in both systems

### **Phase 2: Bi-Directional Sync (Week 2-3)**

**Write Navigator data back to QuickBase:**

```python
def push_navigator_customer_to_qb(customer):
    """Create/update QuickBase record from Navigator customer"""
    
    qb_record = {
        "Name": customer['name'],
        "Email": customer['email'],
        "Phone": customer['phone'],
        "Stage": "Assessing",  # Based on Navigator progress
        "Care_Recommendation": customer['gcp_tier'],
        "Budget_Range": f"${customer['min']}-${customer['max']}",
        "Advisor": assign_advisor_by_workload(),
        "Source": "Navigator App",
        "Date_Created": customer['created_at']
    }
    
    quickbase_client.create_record("bkqfsmeuq", qb_record)
```

**Benefits:**
- Automatic QB record creation for Navigator users
- Keep QB up-to-date with Navigator progress
- Enable existing QB workflows to continue
- Gradual migration path

### **Phase 3: Smart Advisor Assignment (Week 4)**

**Use QB data to intelligently assign new customers:**

```python
def assign_advisor_smart(customer, navigator_assessment):
    """Assign advisor based on workload, expertise, and geography"""
    
    # Pull current advisor workload from QB
    advisors = get_quickbase_advisor_workload()
    
    # Scoring factors:
    # - Current workload (prefer less loaded advisors)
    # - Care specialization (memory care, assisted living)
    # - Geographic territory (Bellevue, Seattle, etc.)
    # - Success rate with similar customers
    
    best_advisor = max(advisors, key=lambda a: calculate_fit_score(
        customer, navigator_assessment, a
    ))
    
    return best_advisor
```

---

## Mock Data Strategy

### **For Demo/Development:**

Create realistic task queues and customer pipelines:

```python
MOCK_TASKS = {
    "action_required": [
        {
            "priority": "urgent",
            "customer": "Sarah Johnson",
            "task": "Follow-up overdue (7 days)",
            "last_contact": "2025-10-30",
            "action": "Check in on community visits"
        },
        {
            "priority": "high",
            "customer": "Mike Davis",
            "task": "Schedule community visit",
            "trigger": "GCP + Cost Plan complete",
            "action": "Present top 3 community matches"
        }
    ],
    "today": [
        {
            "time": "2:00 PM",
            "type": "call",
            "customer": "Margaret Wilson",
            "purpose": "Discuss AL options"
        },
        {
            "time": "3:30 PM",
            "type": "visit",
            "community": "Sunset Manor",
            "customer": "Brown Family"
        }
    ]
}

MOCK_PIPELINE = {
    "new_leads": [
        {"name": "Johnson Family", "days_since": 1},
        {"name": "Martinez Family", "days_since": 2}
    ],
    "assessing": [
        {"name": "Wilson", "gcp": "done", "cost": "in_progress"},
        {"name": "Anderson", "gcp": "in_progress", "cost": "not_started"}
    ],
    "touring": [
        {"name": "Davis", "communities_visited": 2, "favorites": ["Sunset Manor"]},
        {"name": "Brown", "visit_scheduled": "2025-11-08"}
    ],
    "closing": [
        {"name": "Chen", "community": "Bellevue Terrace", "move_in": "2025-12-01"},
        {"name": "Garcia", "contract_sent": true}
    ]
}
```

---

## Implementation Priority

### **Week 1: Foundation (This Week)**
1. ✅ Redesign dashboard layout with tabs
2. ✅ Create task queue UI component
3. ✅ Build customer pipeline visualization
4. ✅ Add mock data for realistic demo

### **Week 2: Navigator Integration**
1. Auto-generate tasks from Navigator events
2. Link customers to their Navigator progress
3. Show GCP/Cost Plan summaries in customer cards
4. Trigger advisor notifications

### **Week 3: QuickBase Integration**
1. Pull advisor data from QB WA Clients table
2. Display QB activities as tasks
3. Show QB customer assignments
4. Build sync dashboard to monitor data flow

### **Week 4: Smart Features**
1. Smart advisor assignment algorithm
2. Bi-directional sync (Navigator → QB)
3. Predictive follow-up suggestions
4. Revenue forecasting by advisor

---

## Technical Architecture

### **New CRM Structure:**

```
apps/crm/
├── pages/
│   ├── dashboard.py          # Main hub (redesign)
│   ├── tasks.py              # Task queue management
│   ├── pipeline.py           # Customer pipeline view
│   ├── customers.py          # Existing customer list
│   ├── appointments.py       # Existing appointments
│   └── quickbase_sync.py     # QB integration dashboard
├── components/
│   ├── task_queue.py         # Reusable task list
│   ├── customer_card.py      # Pipeline customer cards
│   ├── metrics_panel.py      # Advisor metrics
│   └── action_item.py        # Action required items
└── services/
    ├── task_generator.py     # Auto-task creation
    ├── advisor_assignment.py # Smart assignment logic
    └── quickbase_sync.py     # QB integration service
```

---

## Success Metrics

### **Advisor Efficiency:**
- ⏱️ Time to first contact: <24 hours
- 📞 Follow-up completion rate: >90%
- 🎯 Tasks completed per day: Track trend
- 📊 Conversion rate: Lead → Tour → Close

### **System Integration:**
- 🔄 QB sync success rate: >95%
- ⚡ Navigator task generation: Real-time
- 📈 Data consistency: Navigator ↔ QB
- 🤖 Auto-assignment accuracy: Advisor satisfaction survey

---

## Next Steps

**Immediate (Today):**
1. Review and approve this design
2. Choose starting point: Dashboard redesign OR QB integration?
3. Define mock data needs for realistic demo

**This Week:**
1. Implement tab-based dashboard
2. Build task queue component
3. Create customer pipeline visualization
4. Add mock task data

**Next Week:**
1. Connect Navigator events to task generation
2. Build QB advisor data pull
3. Create sync monitoring dashboard

---

## Questions for Discussion

1. **Priority**: Dashboard redesign first, or QB integration first?
2. **Advisor Assignment**: Manual override? Fully automated?
3. **QuickBase Sync**: Real-time or scheduled (hourly/daily)?
4. **Task Auto-Generation**: Which Navigator events should create tasks?
5. **Mock vs Real**: How much mock data for Phase 1 demo?

---

*This design transforms the CRM from a static page into an **advisor command center** with intelligent workflows, automated task generation, and QuickBase integration for team coordination.*
