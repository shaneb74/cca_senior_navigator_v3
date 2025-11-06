"""
Mock Data Generator for CRM Dashboard Demo
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any


def get_mock_advisor_metrics() -> Dict[str, Any]:
    """Generate mock advisor performance metrics"""
    return {
        'active_clients': 12,
        'active_delta': 2,
        'new_leads': 3,
        'new_delta': 1,
        'ready_for_tour': 5,
        'ready_delta': 2,
        'monthly_revenue': 45200,
        'revenue_delta': 12500
    }


def get_mock_action_required() -> List[Dict[str, Any]]:
    """Generate mock urgent action items"""
    return [
        {
            'id': 'action_001',
            'priority': 'urgent',
            'customer': 'Sarah Johnson',
            'task': 'Follow-up overdue (7 days)',
            'last_contact': '2025-10-30',
            'days_since': 7,
            'action': 'Check in on community visits and address any concerns',
            'type': 'follow_up'
        },
        {
            'id': 'action_002',
            'priority': 'high',
            'customer': 'Mike Davis',
            'task': 'Schedule community visit',
            'trigger': 'GCP + Cost Plan complete',
            'action': 'Present top 3 community matches and schedule visits',
            'type': 'appointment'
        },
        {
            'id': 'action_003',
            'priority': 'high',
            'customer': 'Lisa Chen',
            'task': 'Assessment ready for review',
            'action': 'Review GCP results and prepare consultation talking points',
            'type': 'review'
        }
    ]


def get_mock_todays_tasks() -> List[Dict[str, Any]]:
    """Generate mock tasks for today"""
    return [
        {
            'id': 'task_001',
            'time': '10:00 AM',
            'type': 'call',
            'customer': 'Margaret Wilson',
            'purpose': 'Discuss assisted living options and answer questions',
            'duration': '30 min'
        },
        {
            'id': 'task_002',
            'time': '2:00 PM',
            'type': 'visit',
            'customer': 'Brown Family',
            'community': 'Sunset Manor',
            'purpose': 'Community tour with family',
            'duration': '90 min'
        },
        {
            'id': 'task_003',
            'time': '3:30 PM',
            'type': 'review',
            'customer': 'Multiple',
            'purpose': 'Review 3 new GCP assessments',
            'duration': '45 min'
        },
        {
            'id': 'task_004',
            'time': '4:30 PM',
            'type': 'call',
            'customer': 'Robert Taylor',
            'purpose': 'Budget discussion and financing options',
            'duration': '30 min'
        },
        {
            'id': 'task_005',
            'time': '5:00 PM',
            'type': 'email',
            'customer': 'Anderson Family',
            'purpose': 'Send community comparison and pricing details',
            'duration': '15 min'
        }
    ]


def get_mock_customer_pipeline() -> Dict[str, List[Dict[str, Any]]]:
    """Generate mock customer pipeline data"""
    return {
        'new_leads': [
            {
                'name': 'Johnson Family',
                'days_since': 1,
                'source': 'Navigator App',
                'phone': '(425) 555-0123'
            },
            {
                'name': 'Martinez Family',
                'days_since': 2,
                'source': 'Referral',
                'phone': '(425) 555-0156'
            },
            {
                'name': 'Taylor Family',
                'days_since': 3,
                'source': 'Website',
                'phone': '(425) 555-0189'
            }
        ],
        'assessing': [
            {
                'name': 'Margaret Wilson',
                'gcp': 'done',
                'cost': 'in_progress',
                'days_since': 5,
                'care_level': 'Assisted Living'
            },
            {
                'name': 'Anderson Family',
                'gcp': 'in_progress',
                'cost': 'not_started',
                'days_since': 3,
                'care_level': 'Memory Care'
            },
            {
                'name': 'Smith Family',
                'gcp': 'done',
                'cost': 'done',
                'days_since': 2,
                'care_level': 'Assisted Living'
            },
            {
                'name': 'Rodriguez Family',
                'gcp': 'in_progress',
                'cost': 'not_started',
                'days_since': 4,
                'care_level': 'Independent'
            },
            {
                'name': 'Thompson Family',
                'gcp': 'done',
                'cost': 'in_progress',
                'days_since': 6,
                'care_level': 'Memory Care'
            }
        ],
        'touring': [
            {
                'name': 'Mike Davis',
                'communities_visited': 2,
                'favorites': ['Sunset Manor', 'Bellevue Terrace'],
                'days_since': 8,
                'next_visit': 'Nov 8 - Sunrise Senior Living'
            },
            {
                'name': 'Brown Family',
                'communities_visited': 1,
                'visit_scheduled': 'Today 2:00 PM',
                'days_since': 5,
                'community': 'Sunset Manor'
            },
            {
                'name': 'Miller Family',
                'communities_visited': 3,
                'favorites': ['Mercer Island Care'],
                'days_since': 12,
                'status': 'Deciding between 2 communities'
            },
            {
                'name': 'Lee Family',
                'communities_visited': 1,
                'visit_scheduled': 'Nov 9 - Bellevue Terrace',
                'days_since': 4
            }
        ],
        'closing': [
            {
                'name': 'Lisa Chen',
                'community': 'Bellevue Terrace',
                'move_in': '2025-12-01',
                'days_since': 15,
                'contract': 'Signed',
                'deposit': 'Paid'
            },
            {
                'name': 'Garcia Family',
                'community': 'Sunset Manor',
                'move_in': '2025-11-20',
                'days_since': 10,
                'contract': 'Sent',
                'deposit': 'Pending'
            }
        ]
    }


def get_mock_upcoming_appointments() -> List[Dict[str, Any]]:
    """Generate mock upcoming appointments"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    friday = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    
    return [
        {
            'id': 'appt_001',
            'customer_name': 'Anderson Family',
            'appointment_type': 'Initial Consultation',
            'scheduled_at': f'{tomorrow} at 10:00 AM',
            'timezone': 'America/Los_Angeles',
            'confirmation_id': 'A1B2C3D4',
            'notes': 'Interested in memory care options for mother with Alzheimer\'s',
            'days_until': 1
        },
        {
            'id': 'appt_002',
            'customer_name': 'Garcia Family',
            'appointment_type': 'Follow-up Meeting',
            'scheduled_at': f'{friday} at 2:00 PM',
            'timezone': 'America/Los_Angeles',
            'confirmation_id': 'E5F6G7H8',
            'notes': 'Review contract and finalize move-in details',
            'days_until': 2
        }
    ]


def get_mock_team_metrics() -> Dict[str, Dict[str, Any]]:
    """Generate mock team-wide metrics"""
    return {
        'Sarah Chen': {
            'active_clients': 12,
            'new_leads': 3,
            'closing': 2,
            'monthly_revenue': 45200
        },
        'Michael Torres': {
            'active_clients': 15,
            'new_leads': 2,
            'closing': 3,
            'monthly_revenue': 62500
        },
        'Jennifer Kim': {
            'active_clients': 10,
            'new_leads': 4,
            'closing': 1,
            'monthly_revenue': 31000
        },
        'David Martinez': {
            'active_clients': 13,
            'new_leads': 3,
            'closing': 2,
            'monthly_revenue': 48700
        }
    }


def get_mock_all_tasks() -> List[Dict[str, Any]]:
    """Generate complete task list for task management page"""
    return [
        {
            'id': 'task_101',
            'customer': 'Margaret Wilson',
            'task': 'Initial consultation call',
            'type': 'call',
            'priority': 'high',
            'due': '2025-11-07',
            'status': 'pending',
            'created_at': '2025-11-05'
        },
        {
            'id': 'task_102',
            'customer': 'Brown Family',
            'task': 'Community tour at Sunset Manor',
            'type': 'visit',
            'priority': 'high',
            'due': '2025-11-07',
            'status': 'scheduled',
            'created_at': '2025-11-03'
        },
        {
            'id': 'task_103',
            'customer': 'Sarah Johnson',
            'task': 'Follow-up on community visits',
            'type': 'follow_up',
            'priority': 'urgent',
            'due': '2025-11-06',
            'status': 'overdue',
            'created_at': '2025-10-30'
        },
        {
            'id': 'task_104',
            'customer': 'Mike Davis',
            'task': 'Schedule community visits',
            'type': 'appointment',
            'priority': 'high',
            'due': '2025-11-08',
            'status': 'pending',
            'created_at': '2025-11-05'
        },
        {
            'id': 'task_105',
            'customer': 'Lisa Chen',
            'task': 'Review GCP assessment results',
            'type': 'review',
            'priority': 'medium',
            'due': '2025-11-07',
            'status': 'pending',
            'created_at': '2025-11-06'
        }
    ]
