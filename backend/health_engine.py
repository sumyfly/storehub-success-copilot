from datetime import datetime

from mock_data import ACTION_TEMPLATES


def calculate_health_score(customer):
    """
    Calculate customer health score based on multiple factors
    Score ranges from 0.0 (critical) to 1.0 (excellent)
    """
    score = 1.0

    # Usage penalty
    if customer["usage_score"] < 0.3:
        score -= 0.4
    elif customer["usage_score"] < 0.6:
        score -= 0.2

    # Support tickets penalty
    if customer["support_tickets"] > 5:
        score -= 0.3
    elif customer["support_tickets"] > 2:
        score -= 0.1

    # Login recency penalty
    if customer["last_login_days"] > 30:
        score -= 0.4
    elif customer["last_login_days"] > 7:
        score -= 0.2

    return max(0, round(score, 2))


def generate_alerts(customer):
    """
    Generate alerts based on customer health indicators
    Returns list of alerts with suggested actions
    """
    alerts = []
    current_time = datetime.now().isoformat()

    health_score = customer.get("health_score", calculate_health_score(customer))

    # Critical churn risk alert
    if health_score < 0.3:
        alerts.append(
            {
                "customer_id": customer["id"],
                "customer_name": customer["name"],
                "type": "churn_risk",
                "severity": "critical",
                "message": f"{customer['name']} has very low health score ({health_score})",
                "actions": ACTION_TEMPLATES["churn_risk"][:2],  # Top 2 actions
                "created_at": current_time,
            }
        )

    # Engagement risk alert
    if customer["last_login_days"] > 14:
        severity = "critical" if customer["last_login_days"] > 30 else "medium"
        alerts.append(
            {
                "customer_id": customer["id"],
                "customer_name": customer["name"],
                "type": "engagement_risk",
                "severity": severity,
                "message": f"{customer['name']} hasn't logged in for {customer['last_login_days']} days",
                "actions": ACTION_TEMPLATES["engagement_risk"][:2],
                "created_at": current_time,
            }
        )

    # Usage decline alert
    if customer["usage_score"] < 0.4:
        severity = "critical" if customer["usage_score"] < 0.2 else "medium"
        alerts.append(
            {
                "customer_id": customer["id"],
                "customer_name": customer["name"],
                "type": "usage_decline",
                "severity": severity,
                "message": f"{customer['name']} has low product usage ({customer['usage_score']})",
                "actions": ACTION_TEMPLATES["usage_decline"][:2],
                "created_at": current_time,
            }
        )

    # Support overload alert
    if customer["support_tickets"] > 5:
        alerts.append(
            {
                "customer_id": customer["id"],
                "customer_name": customer["name"],
                "type": "support_overload",
                "severity": "medium",
                "message": f"{customer['name']} has {customer['support_tickets']} open support tickets",
                "actions": ACTION_TEMPLATES["support_overload"][:2],
                "created_at": current_time,
            }
        )

    return alerts


def get_health_trend(customer):
    """
    Simulate health trend analysis (in real app, this would use historical data)
    """
    health_score = calculate_health_score(customer)

    # Simulate trend based on current indicators
    if health_score < 0.3:
        trend = "declining"
    elif health_score > 0.7:
        trend = "improving"
    else:
        trend = "stable"

    return {
        "trend": trend,
        "change_30d": round((health_score - 0.5) * 0.1, 2),  # Simulated change
        "forecast_30d": min(
            1.0,
            max(
                0.0,
                health_score
                + (
                    0.1 if trend == "improving" else -0.1 if trend == "declining" else 0
                ),
            ),
        ),
    }


def recommend_actions(customer):
    """
    Generate personalized action recommendations based on customer profile
    """
    recommendations = []
    health_score = calculate_health_score(customer)

    # Urgent actions for critical health
    if health_score < 0.3:
        recommendations.extend(
            [
                {
                    "action_type": "urgent_call",
                    "description": "Schedule immediate call with executive sponsor",
                    "urgency": "immediate",
                    "effort": "medium",
                    "expected_impact": "high",
                },
                {
                    "action_type": "retention_offer",
                    "description": "Prepare customized retention package",
                    "urgency": "within_24h",
                    "effort": "high",
                    "expected_impact": "high",
                },
            ]
        )

    # Engagement actions
    if customer["last_login_days"] > 7:
        recommendations.append(
            {
                "action_type": "engagement_outreach",
                "description": "Send personalized check-in email with value reminder",
                "urgency": "within_24h"
                if customer["last_login_days"] > 14
                else "within_week",
                "effort": "low",
                "expected_impact": "medium",
            }
        )

    # Usage improvement actions
    if customer["usage_score"] < 0.5:
        recommendations.append(
            {
                "action_type": "training_session",
                "description": "Schedule product training and best practices review",
                "urgency": "within_week",
                "effort": "medium",
                "expected_impact": "high",
            }
        )

    return recommendations
