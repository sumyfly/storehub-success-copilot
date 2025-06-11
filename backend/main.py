from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from health_engine import (
    calculate_health_score,
    generate_alerts,
    get_customer_label,
    get_health_trend,
    recommend_actions,
)
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
    """Get all customers with their enhanced health scores and labels"""
    customers_with_health = []
    for customer_data in MOCK_CUSTOMERS:
        # Calculate health score for each customer
        health_score = calculate_health_score(customer_data)
        customer_label = get_customer_label(
            {**customer_data, "health_score": health_score}
        )

        # Create enhanced customer object
        enhanced_customer = {
            **customer_data,
            "health_score": health_score,
            "customer_label": customer_label,
        }
        customer = Customer(**enhanced_customer)
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

    # Calculate health score and get additional insights
    health_score = calculate_health_score(customer_data)
    customer_with_health = {**customer_data, "health_score": health_score}

    # Get comprehensive health breakdown
    health_breakdown = {
        "customer_id": customer_id,
        "customer_name": customer_data["name"],
        "overall_health_score": health_score,
        "customer_label": get_customer_label(customer_with_health),
        "factors": {
            "usage_score": customer_data["usage_score"],
            "engagement_score": customer_data.get("engagement_score", 0),
            "support_tickets": customer_data["support_tickets"],
            "last_login_days": customer_data["last_login_days"],
            "payment_status": customer_data.get("payment_status", "current"),
            "feature_adoption": customer_data.get("feature_adoption", {}),
            "nps_score": customer_data.get("nps_score", 5),
            "mrr": customer_data["mrr"],
        },
        "risk_level": "critical"
        if health_score < 0.3
        else "medium"
        if health_score < 0.6
        else "healthy",
        "health_trend": get_health_trend(customer_with_health),
        "alerts": generate_alerts(customer_with_health),
        "recommended_actions": recommend_actions(customer_with_health),
    }

    return health_breakdown


@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get enhanced summary statistics for the dashboard"""
    customers_with_health = []
    all_alerts = []
    customer_labels = {}

    # Process all customers
    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        customers_with_health.append(customer_with_health)

        # Generate alerts
        alerts = generate_alerts(customer_with_health)
        all_alerts.extend(alerts)

        # Get customer labels
        label = get_customer_label(customer_with_health)
        customer_labels[customer_data["id"]] = label

    # Calculate enhanced stats
    critical_alerts = len([a for a in all_alerts if a["severity"] == "critical"])
    medium_risk = len(
        [c for c in customers_with_health if 0.3 <= c["health_score"] < 0.6]
    )
    healthy_customers = len(
        [c for c in customers_with_health if c["health_score"] >= 0.6]
    )

    # Count customers by label
    label_counts = {}
    for label in customer_labels.values():
        label_counts[label] = label_counts.get(label, 0) + 1

    # Calculate average health score
    avg_health = sum(c["health_score"] for c in customers_with_health) / len(
        customers_with_health
    )

    return {
        "total_customers": len(customers_with_health),
        "critical_alerts": critical_alerts,
        "medium_risk_customers": medium_risk,
        "healthy_customers": healthy_customers,
        "total_alerts": len(all_alerts),
        "average_health_score": round(avg_health, 2),
        "customer_segments": label_counts,
        "expansion_opportunities": len(
            [
                c
                for c in customers_with_health
                if c["health_score"] > 0.8 and c.get("nps_score", 0) >= 8
            ]
        ),
        "payment_issues": len(
            [
                c
                for c in customers_with_health
                if c.get("payment_status") in ["late", "overdue"]
            ]
        ),
    }


@app.get("/insights/trends")
async def get_health_trends():
    """Get health trend insights for all customers"""
    trends = []
    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        trend = get_health_trend(customer_with_health)

        trends.append(
            {
                "customer_id": customer_data["id"],
                "customer_name": customer_data["name"],
                "current_health": health_score,
                "trend": trend,
            }
        )

    return sorted(trends, key=lambda x: x["current_health"])


@app.get("/recommendations/{customer_id}")
async def get_customer_recommendations(customer_id: int):
    """Get action recommendations for a specific customer"""
    customer_data = next((c for c in MOCK_CUSTOMERS if c["id"] == customer_id), None)
    if not customer_data:
        return {"error": "Customer not found"}

    health_score = calculate_health_score(customer_data)
    customer_with_health = {**customer_data, "health_score": health_score}

    return {
        "customer_id": customer_id,
        "customer_name": customer_data["name"],
        "current_health": health_score,
        "recommendations": recommend_actions(customer_with_health),
    }
