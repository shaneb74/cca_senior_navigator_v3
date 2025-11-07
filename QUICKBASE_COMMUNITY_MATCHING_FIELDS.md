# QuickBase Community Matching Fields - Complete Analysis

## 🎯 **Executive Summary**

The QuickBase WA Communities table contains **132 fields** with **40+ checkbox amenities** that can be used for sophisticated community matching. This analysis shows we have access to far more matching criteria than initially used.

---

## 📊 **Available Matching Categories**

### 🏠 **Amenities & Facilities (13 fields)**
| Field ID | Field Name | Matching Use |
|----------|------------|--------------|
| 47 | Full Kitchen | Independence preference |
| 50 | Pool | Recreation/fitness needs |
| 51 | Patio | Outdoor space preference |
| 52 | Covered Parking | Weather protection |
| 69 | Garage Parking | Security preference |
| 70 | Extra Storage | Space requirements |
| 72 | Washer & Dryer | Convenience/independence |
| 91 | **Hoyer Lift** | **Critical mobility assistance** |
| 93 | Woodworking Shop | Hobby/activity matching |
| 118 | Water View | Environmental preference |
| 121 | Generator | Power reliability |
| 122 | Air Conditioning | Climate comfort |
| 159 | Has Pets In The Home | Animal interaction |

### 🏥 **Medical Care & Services (13 fields)**
| Field ID | Field Name | Medical Condition Match |
|----------|------------|-------------------------|
| 71 | Dedicated Memory Care | Alzheimer's/Dementia |
| 89 | 2 Person Transfers | Mobility/safety needs |
| 90 | Insulin | Diabetes management |
| 147 | Bariatric | Weight management |
| 150 | Insulin Sliding Scale | Advanced diabetes care |
| 151 | Wound Care | Medical wound management |
| 152 | Colostomy | Specialized care needs |
| 153 | Catheter | Urological care |
| 154 | Tube Feeding | Nutritional support |
| 19 | Awake Staff | 24/7 supervision |
| 57 | Awake Night Staff | Nighttime safety |
| 102 | Medicaid | Financial eligibility |
| 146 | Accepts Medicaid | Payment method |

### 🏘️ **Accommodation Types (2 fields)**
| Field ID | Field Name | Housing Preference |
|----------|------------|-------------------|
| 79 | 2 Bedroom Apt | Couple accommodation |
| 123 | Cottages | Independent living style |

### 🎭 **Lifestyle Preferences (5 fields)**
| Field ID | Field Name | Lifestyle Match |
|----------|------------|-----------------|
| 61 | Allows Pets w/placement | Pet ownership |
| 48 | Accepts Smokers | Smoking preference |
| 104 | Languages Spoken | Cultural/language needs |
| 58 | Nationality | Cultural matching |
| 118 | Water View | Environmental preference |

---

## 🔧 **Enhanced QuickBase Integration**

### **Before (Limited Matching)**
```python
# Old implementation - only basic fields
"select": [3, 27, 6, 7, 33, 34, 37, 55, 21, 59, 40]
```

### **After (Comprehensive Matching)**
```python
# New implementation - 40+ matching fields
"select": [
    # Core identification (5 fields)
    3, 27, 6, 55, 21,
    
    # Contact information (6 fields)  
    7, 10, 11, 33, 34, 37,
    
    # Availability & capacity (3 fields)
    59, 40, 42,
    
    # Medical specializations (13 fields)
    71, 89, 91, 147, 102, 146, 90, 150, 151, 152, 153, 154, 19, 57,
    
    # Amenities & facilities (13 fields)
    47, 50, 51, 52, 69, 70, 72, 122, 121, 93, 118, 61, 159,
    
    # Lifestyle preferences (5 fields)
    48, 104, 79, 123, 43, 96, 45
]
```

---

## 🎯 **Smart Matching Examples**

### **Mobility Assistance Matching**
```python
# GCP Assessment: "Requires assistance with transfers"
# QuickBase Match: 
community["qb_data"]["hoyer_lift"] == True        # Field 91
community["qb_data"]["two_person_transfers"] == True  # Field 89
```

### **Medical Care Matching**
```python
# GCP Assessment: "Diabetes with insulin"
# QuickBase Match:
community["qb_data"]["medical_services"]["insulin"] == True  # Field 90
community["qb_data"]["medical_services"]["insulin_sliding_scale"] == True  # Field 150
```

### **Lifestyle Preference Matching**
```python
# PFMA Preferences: "Wants to keep pet"
# QuickBase Match:
community["qb_data"]["pet_friendly"] == True  # Field 61 or 159

# PFMA Preferences: "Spanish speaking family"
# QuickBase Match:
"Spanish" in community["languages_spoken"]  # Field 104
```

### **Amenity Preference Matching**
```python
# Cost Planner: "Values independence - cooking"
# QuickBase Match:
community["qb_data"]["full_kitchen"] == True  # Field 47

# PFMA Preferences: "Enjoys swimming"
# QuickBase Match:
community["qb_data"]["pool"] == True  # Field 50
```

---

## 🚀 **Implementation Benefits**

### **Precision Matching**
- **Before**: 11 basic fields → generic matches
- **After**: 40+ specialized fields → precise care matching

### **Medical Compatibility**
- **Hoyer Lift**: Critical for mobility-impaired residents
- **Specialized Care**: Diabetes, wound care, memory care
- **Staffing Levels**: 24/7 supervision capabilities

### **Lifestyle Alignment**
- **Pet Policies**: Exact pet accommodation matching
- **Language Services**: Cultural and communication needs
- **Accommodation Types**: Couple vs. individual preferences

### **Real-Time Availability**
- **Vacancy Status**: Current openings with bed counts
- **Medicaid Acceptance**: Financial eligibility matching
- **Contract Status**: CCA partnership verification

---

## 📈 **Matching Algorithm Enhancement**

### **Weighted Scoring System**
```python
def calculate_community_match_score(gcp_data, pfma_preferences, community):
    score = 0
    
    # Critical medical needs (high weight)
    if gcp_data.get("mobility_assistance") and community["qb_data"]["hoyer_lift"]:
        score += 50  # Critical match
    
    # Care level compatibility (high weight)  
    if gcp_data.get("care_level") in community["care_levels"]:
        score += 40
    
    # Lifestyle preferences (medium weight)
    if pfma_preferences.get("pets") and community["qb_data"]["pet_friendly"]:
        score += 20
    
    # Amenity preferences (low weight)
    if pfma_preferences.get("pool") and community["qb_data"]["pool"]:
        score += 10
    
    return score
```

---

## 🎯 **Next Steps**

1. **Update PFMA Preferences Form** 
   - Add checkboxes for: Pool, Full Kitchen, Pet Policies, Languages
   - Medical needs: Hoyer Lift, Specialized Care Requirements

2. **Enhance GCP Assessment**
   - Include mobility assistance questions
   - Medical care complexity indicators

3. **Smart Matching Algorithm**
   - Implement weighted scoring system
   - Priority ranking based on critical vs. preference matches

4. **Real-Time Integration**
   - Live vacancy status updates
   - Immediate availability notifications

---

## ✅ **Verification Complete**

**CONFIRMED**: QuickBase WA Communities table contains extensive matching data including:
- ✅ **Hoyer Lift** (Field 91) - Critical mobility equipment
- ✅ **Pool** (Field 50) - Recreation amenity  
- ✅ **Full Kitchen** (Field 47) - Independence feature
- ✅ **Languages Spoken** (Field 104) - Cultural matching
- ✅ **Pet Policies** (Fields 61, 159) - Lifestyle preferences
- ✅ **Medical Services** (13+ specialized care fields)
- ✅ **Real-time Vacancy** (Field 59) - Current availability

**Result**: We now have 40+ matching criteria vs. the original 11 fields, enabling precise care matching that rivals industry-leading platforms.