# 6-Hour Prototype PRD - Customer Success Copilot

## 🎯 **PROTOTYPE GOAL**
Build a working demo that shows:
1. **Customer health scoring**
2. **Risk alerts dashboard** 
3. **Basic action recommendations**

**NOT building**: Real integrations, complex ML, production deployment

---

## ⏰ **6-HOUR BREAKDOWN**

### **Hour 1: Foundation Setup (60 min)**
- ✅ Basic FastAPI backend with 3 endpoints
- ✅ Simple React frontend with routing
- ✅ Mock data (no real database initially)
- ✅ Basic project structure

### **Hour 2: Customer Health Engine (60 min)**
- ✅ Simple health scoring algorithm (no ML)
- ✅ Customer data models
- ✅ Health calculation API endpoint
- ✅ Mock customer data (10-15 fake customers)

### **Hour 3: Risk Detection & Alerts (60 min)**
- ✅ Basic risk scoring logic
- ✅ Alert generation (simple rules)
- ✅ Alert severity levels
- ✅ Alerts API endpoint

### **Hour 4: Frontend Dashboard (60 min)**
- ✅ Customer list with health scores
- ✅ Alerts dashboard
- ✅ Basic styling (simple, clean)
- ✅ Connect frontend to backend APIs

### **Hour 5: Action Recommendations (60 min)**
- ✅ Simple action suggestion engine
- ✅ Predefined action templates
- ✅ Action recommendation API
- ✅ Display actions in frontend

### **Hour 6: Polish & Demo Prep (60 min)**
- ✅ Add more realistic mock data
- ✅ Basic error handling
- ✅ Demo script preparation
- ✅ Final testing

---

## 🚀 **MINIMAL VIABLE FEATURES**

### **Core Data Model (Simple)**
```python
Customer:
- id, name, mrr, contract_date
- usage_score (0-1)
- support_tickets_count
- last_login_days_ago

Alert:
- customer_id, type, severity, message
- suggested_actions[]

Action:
- type, description, urgency
```

### **Health Scoring (Rule-Based)**
```python
def calculate_health_score(customer):
    score = 1.0
    
    # Usage penalty
    if customer.usage_score < 0.3:
        score -= 0.4
    elif customer.usage_score < 0.6:
        score -= 0.2
    
    # Support tickets penalty
    if customer.support_tickets > 5:
        score -= 0.3
    elif customer.support_tickets > 2:
        score -= 0.1
    
    # Login recency penalty
    if customer.last_login_days > 30:
        score -= 0.4
    elif customer.last_login_days > 7:
        score -= 0.2
    
    return max(0, score)
```

### **Alert Generation (Simple Rules)**
```python
def generate_alerts(customer):
    alerts = []
    
    if customer.health_score < 0.3:
        alerts.append({
            "type": "churn_risk",
            "severity": "critical",
            "message": f"{customer.name} has very low health score",
            "actions": ["Schedule urgent call", "Send retention offer"]
        })
    
    if customer.last_login_days > 14:
        alerts.append({
            "type": "engagement_risk", 
            "severity": "medium",
            "message": f"{customer.name} hasn't logged in for {customer.last_login_days} days",
            "actions": ["Send check-in email", "Share new feature update"]
        })
    
    return alerts
```

---

## 📱 **FRONTEND PAGES (3 Simple Pages)**

### **1. Dashboard Overview**
```
┌─────────────────────────────────────────┐
│ Customer Success Copilot                │
├─────────────────────────────────────────┤
│ 🔴 3 Critical Alerts                   │
│ 🟡 5 Medium Risk Customers             │
│ 🟢 12 Healthy Customers                │
│                                         │
│ [View All Alerts] [Customer List]      │
└─────────────────────────────────────────┘
```

### **2. Alerts Dashboard**
```
┌─────────────────────────────────────────┐
│ Risk Alerts                             │
├─────────────────────────────────────────┤
│ 🔴 CRITICAL - Acme Corp                │
│    Churn risk: Very low health score   │
│    → Schedule urgent call              │
│    → Send retention offer              │
│                                         │
│ 🟡 MEDIUM - Tech Solutions Ltd         │
│    Engagement risk: No login 16 days   │
│    → Send check-in email               │
└─────────────────────────────────────────┘
```

### **3. Customer List**
```
┌─────────────────────────────────────────┐
│ Customer Health Overview                │
├─────────────────────────────────────────┤
│ Acme Corp        🔴 0.2  $5,000        │
│ Tech Solutions   🟡 0.5  $3,000        │
│ Innovation Inc   🟢 0.8  $8,000        │
│ StartupCo        🟢 0.9  $2,000        │
└─────────────────────────────────────────┘
```

---

## 🛠 **TECHNICAL STACK (Simplified)**

### **Backend (FastAPI - 4 files)**
```
backend/
├── main.py              # FastAPI app + all endpoints
├── models.py            # Pydantic models
├── mock_data.py         # Fake customer data
└── health_engine.py     # Health scoring logic
```

### **Frontend (React - 6 files)**
```
frontend/src/
├── App.js               # Main app + routing
├── Dashboard.js         # Overview dashboard
├── AlertsList.js        # Alerts page
├── CustomerList.js      # Customers page
├── api.js              # API calls
└── styles.css          # Basic styling
```

---

## 📊 **MOCK DATA (15 Customers)**

```python
MOCK_CUSTOMERS = [
    {
        "id": 1,
        "name": "Acme Corp",
        "mrr": 5000,
        "usage_score": 0.1,
        "support_tickets": 8,
        "last_login_days": 45,
        "contract_date": "2023-01-15"
    },
    {
        "id": 2, 
        "name": "Tech Solutions Ltd",
        "mrr": 3000,
        "usage_score": 0.4,
        "support_tickets": 2,
        "last_login_days": 16,
        "contract_date": "2023-03-01"
    },
    # ... 13 more varied customers
]
```

---

## 🎬 **DEMO SCRIPT (5 minutes)**

### **Opening (30 seconds)**
"This is our Customer Success Copilot prototype. It automatically identifies at-risk customers and suggests actions to prevent churn."

### **Dashboard Tour (2 minutes)**
1. **Overview**: "We have 3 critical alerts today"
2. **Alerts Page**: "Acme Corp shows churn risk - health score 0.2"
3. **Actions**: "System suggests urgent call and retention offer"

### **Customer Drill-down (2 minutes)**
1. **Customer List**: "Health scores from 0-1, color coded"
2. **Risk Factors**: "Low usage + support tickets + no logins"
3. **Proactive Approach**: "Catch issues before customers leave"

### **Value Proposition (30 seconds)**
"Instead of reactive support, CSMs get proactive alerts with specific actions. Early prototype shows core concept working."

---

## ✅ **SUCCESS CRITERIA**

At the end of 6 hours, you should have:

1. **Working backend** with 4 API endpoints
2. **Functional frontend** with 3 pages
3. **Realistic mock data** for 15 customers
4. **Health scoring** that makes sense
5. **Alert generation** with action suggestions
6. **Demo-ready** application

## 🚫 **EXPLICITLY NOT INCLUDED**

- Real database setup
- Authentication/login
- External API integrations  
- Machine learning models
- Complex UI/UX design
- Error handling (basic only)
- Testing
- Deployment configuration
- Real customer data

---

## 🏃‍♂️ **NEXT STEPS (Start Now!)**

1. **Clone the project structure** we created
2. **Start with Hour 1** - basic FastAPI + React setup
3. **Use mock data** throughout - no database complexity
4. **Keep it simple** - resist feature creep
5. **Focus on the demo** - what story does it tell?

**Remember**: This is a prototype to prove the concept, not a production system. Simple and working beats complex and broken!

Ready to build? Let's start with Hour 1! 🚀 