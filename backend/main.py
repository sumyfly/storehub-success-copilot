from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from health_engine import calculate_health_score, generate_alerts
from mock_data import MOCK_CUSTOMERS
from models import Alert, Customer

app = FastAPI(title="Customer Success Copilot", version="0.1.0")

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Customer Success Copilot API", "version": "0.1.0"}


@app.get("/customers", response_model=List[Customer])
async def get_customers():
    """Get all customers with their health scores"""
    customers_with_health = []
    for customer_data in MOCK_CUSTOMERS:
        # Calculate health score for each customer
        health_score = calculate_health_score(customer_data)
        customer = Customer(**customer_data, health_score=health_score)
        customers_with_health.append(customer)
    return customers_with_health


@app.get("/alerts", response_model=List[Alert])
async def get_alerts():
    """Get all active alerts for at-risk customers"""
    all_alerts = []
    for customer_data in MOCK_CUSTOMERS:
        # Calculate health score first
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}

        # Generate alerts for this customer
        alerts = generate_alerts(customer_with_health)
        all_alerts.extend(alerts)

    return all_alerts


@app.get("/health/{customer_id}")
async def get_customer_health(customer_id: int):
    """Get detailed health information for a specific customer"""
    # Find customer by ID
    customer_data = next((c for c in MOCK_CUSTOMERS if c["id"] == customer_id), None)
    if not customer_data:
        return {"error": "Customer not found"}

    # Calculate health score
    health_score = calculate_health_score(customer_data)

    # Generate health breakdown
    health_breakdown = {
        "customer_id": customer_id,
        "customer_name": customer_data["name"],
        "overall_health_score": health_score,
        "factors": {
            "usage_score": customer_data["usage_score"],
            "support_tickets": customer_data["support_tickets"],
            "last_login_days": customer_data["last_login_days"],
            "mrr": customer_data["mrr"],
        },
        "risk_level": "critical"
        if health_score < 0.3
        else "medium"
        if health_score < 0.6
        else "healthy",
        "alerts": generate_alerts({**customer_data, "health_score": health_score}),
    }

    return health_breakdown


@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get summary statistics for the dashboard"""
    customers_with_health = []
    all_alerts = []

    # Process all customers
    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        customers_with_health.append(customer_with_health)

        # Generate alerts
        alerts = generate_alerts(customer_with_health)
        all_alerts.extend(alerts)

    # Calculate stats
    critical_alerts = len([a for a in all_alerts if a["severity"] == "critical"])
    medium_risk = len(
        [c for c in customers_with_health if 0.3 <= c["health_score"] < 0.6]
    )
    healthy_customers = len(
        [c for c in customers_with_health if c["health_score"] >= 0.6]
    )

    return {
        "total_customers": len(customers_with_health),
        "critical_alerts": critical_alerts,
        "medium_risk_customers": medium_risk,
        "healthy_customers": healthy_customers,
        "total_alerts": len(all_alerts),
    }
