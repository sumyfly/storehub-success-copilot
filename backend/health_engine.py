from datetime import datetime

from mock_data import ACTION_TEMPLATES, CUSTOMER_LABELS


def calculate_health_score(customer):
    """
    Enhanced health score calculation with multiple weighted factors
    Score ranges from 0.0 (critical) to 1.0 (excellent)
    """

    # Get customer type weights
    weights = get_customer_weights(customer.get("customer_type", "mid_market"))

    # Calculate individual factor scores
    factors = {
        "usage": calculate_usage_factor(customer),
        "engagement": calculate_engagement_factor(customer),
        "support": calculate_support_factor(customer),
        "payment": calculate_payment_factor(customer),
        "adoption": calculate_adoption_factor(customer),
        "satisfaction": calculate_satisfaction_factor(customer),
        "lifecycle": calculate_lifecycle_factor(customer),
        "value": calculate_value_factor(customer),
    }

    # Calculate weighted health score
    weighted_score = 0
    for factor, score in factors.items():
        weighted_score += score * weights.get(factor, 0.1)

    # Normalize to 0-1 range
    final_score = min(1.0, max(0.0, weighted_score))

    return round(final_score, 2)


def get_customer_weights(customer_type):
    """Get scoring weights based on customer type"""
    weights = {
        "enterprise": {
            "usage": 0.15,
            "engagement": 0.10,
            "support": 0.15,
            "payment": 0.20,
            "adoption": 0.15,
            "satisfaction": 0.15,
            "lifecycle": 0.05,
            "value": 0.05,
        },
        "mid_market": {
            "usage": 0.20,
            "engagement": 0.15,
            "support": 0.15,
            "payment": 0.15,
            "adoption": 0.15,
            "satisfaction": 0.10,
            "lifecycle": 0.05,
            "value": 0.05,
        },
        "startup": {
            "usage": 0.25,
            "engagement": 0.20,
            "support": 0.10,
            "payment": 0.10,
            "adoption": 0.20,
            "satisfaction": 0.10,
            "lifecycle": 0.03,
            "value": 0.02,
        },
    }
    return weights.get(customer_type, weights["mid_market"])


def calculate_usage_factor(customer):
    """Calculate usage-based score"""
    usage_score = customer.get("usage_score", 0)
    last_login_penalty = min(customer.get("last_login_days", 0) / 30, 1.0)
    return max(0, usage_score - (last_login_penalty * 0.3))


def calculate_engagement_factor(customer):
    """Calculate engagement score"""
    engagement = customer.get("engagement_score", 0)
    onboarding_bonus = 0.1 if customer.get("onboarding_completed", False) else -0.2
    return min(1.0, max(0, engagement + onboarding_bonus))


def calculate_support_factor(customer):
    """Calculate support health factor"""
    tickets = customer.get("support_tickets", 0)
    if tickets == 0:
        return 1.0
    elif tickets <= 2:
        return 0.8
    elif tickets <= 5:
        return 0.5
    else:
        return max(0, 0.3 - (tickets - 5) * 0.05)


def calculate_payment_factor(customer):
    """Calculate payment health factor"""
    payment_status = customer.get("payment_status", "current")
    status_scores = {"current": 1.0, "late": 0.6, "overdue": 0.2, "failed": 0.0}
    return status_scores.get(payment_status, 0.5)


def calculate_adoption_factor(customer):
    """Calculate feature adoption score"""
    adoption = customer.get("feature_adoption", {})
    if not adoption:
        return 0.3

    # Weighted adoption score
    core_weight = 0.5
    advanced_weight = 0.3
    integrations_weight = 0.2

    score = (
        adoption.get("core", 0) * core_weight
        + adoption.get("advanced", 0) * advanced_weight
        + adoption.get("integrations", 0) * integrations_weight
    )
    return min(1.0, score)


def calculate_satisfaction_factor(customer):
    """Calculate satisfaction score from NPS"""
    nps = customer.get("nps_score", 5)
    # Convert NPS (0-10) to 0-1 scale
    return min(1.0, max(0, nps / 10))


def calculate_lifecycle_factor(customer):
    """Calculate lifecycle stage factor"""
    from datetime import datetime

    contract_date = datetime.strptime(
        customer.get("contract_date", "2023-01-01"), "%Y-%m-%d"
    )
    days_since_start = (datetime.now() - contract_date).days

    # New customers (< 90 days) get lifecycle bonus
    if days_since_start < 90:
        return 1.0
    # Established customers (> 365 days) get stability bonus
    elif days_since_start > 365:
        return 0.9
    else:
        return 0.8


def calculate_value_factor(customer):
    """Calculate value-based factor"""
    mrr = customer.get("mrr", 0)
    # Logarithmic scaling for MRR influence
    if mrr < 1000:
        return 0.5
    elif mrr < 5000:
        return 0.7
    elif mrr < 10000:
        return 0.9
    else:
        return 1.0


def generate_alerts(customer):
    """
    Enhanced alert generation with multiple alert types
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
                "message": f"{customer['name']} has critical health score ({health_score}) - immediate action required",
                "actions": ACTION_TEMPLATES["churn_risk"][:2],
                "created_at": current_time,
            }
        )

    # Payment risk alerts
    payment_status = customer.get("payment_status", "current")
    if payment_status in ["late", "overdue"]:
        severity = "critical" if payment_status == "overdue" else "medium"
        alerts.append(
            {
                "customer_id": customer["id"],
                "customer_name": customer["name"],
                "type": "payment_risk",
                "severity": severity,
                "message": f"{customer['name']} has {payment_status} payment status",
                "actions": ACTION_TEMPLATES["payment_risk"][:2],
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

    # Feature adoption alert
    adoption = customer.get("feature_adoption", {})
    avg_adoption = sum(adoption.values()) / len(adoption) if adoption else 0
    if avg_adoption < 0.4:
        alerts.append(
            {
                "customer_id": customer["id"],
                "customer_name": customer["name"],
                "type": "usage_decline",
                "severity": "medium" if avg_adoption < 0.2 else "low",
                "message": f"{customer['name']} has low feature adoption ({avg_adoption:.1%})",
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

    # Onboarding incomplete alert
    if not customer.get("onboarding_completed", True):
        alerts.append(
            {
                "customer_id": customer["id"],
                "customer_name": customer["name"],
                "type": "onboarding_incomplete",
                "severity": "medium",
                "message": f"{customer['name']} has not completed onboarding",
                "actions": ACTION_TEMPLATES["onboarding_incomplete"][:2],
                "created_at": current_time,
            }
        )

    # Expansion opportunity (positive alert)
    if health_score > 0.8 and customer.get("nps_score", 0) >= 8:
        alerts.append(
            {
                "customer_id": customer["id"],
                "customer_name": customer["name"],
                "type": "expansion_opportunity",
                "severity": "low",
                "message": f"{customer['name']} is a high-health customer ready for expansion",
                "actions": ACTION_TEMPLATES["expansion_opportunity"][:2],
                "created_at": current_time,
            }
        )

    return alerts


def get_customer_label(customer):
    """
    Assign intelligent customer labels based on multiple factors
    """
    health_score = customer.get("health_score", calculate_health_score(customer))
    nps = customer.get("nps_score", 5)
    engagement = customer.get("engagement_score", 0)
    usage = customer.get("usage_score", 0)

    # Check contract age
    contract_date = datetime.strptime(
        customer.get("contract_date", "2023-01-01"), "%Y-%m-%d"
    )
    days_since_start = (datetime.now() - contract_date).days
    is_new = days_since_start < 90

    # Label assignment logic
    if health_score >= 0.8 and nps >= 8:
        return CUSTOMER_LABELS["champions"]
    elif health_score >= 0.8 and engagement >= 0.7:
        return CUSTOMER_LABELS["expansion_ready"]
    elif health_score < 0.3:
        return CUSTOMER_LABELS["churn_risk"]
    elif health_score < 0.6:
        return CUSTOMER_LABELS["at_risk"]
    elif usage >= 0.8 and engagement >= 0.8:
        return CUSTOMER_LABELS["power_user"]
    elif is_new:
        return CUSTOMER_LABELS["new_customer"]
    elif customer.get("last_login_days", 0) > 21:
        return CUSTOMER_LABELS["dormant"]
    else:
        return CUSTOMER_LABELS["needs_attention"]


def get_health_trend(customer):
    """
    Simulate health trend analysis with predictive insights
    """
    health_score = calculate_health_score(customer)

    # Simulate trend based on multiple indicators
    trend_factors = []

    # Usage trend factor
    usage = customer.get("usage_score", 0)
    if usage > 0.7:
        trend_factors.append(0.1)
    elif usage < 0.3:
        trend_factors.append(-0.15)

    # Engagement trend factor
    engagement = customer.get("engagement_score", 0)
    if engagement > 0.7:
        trend_factors.append(0.05)
    elif engagement < 0.3:
        trend_factors.append(-0.1)

    # Support trend factor
    if customer.get("support_tickets", 0) > 5:
        trend_factors.append(-0.1)
    elif customer.get("support_tickets", 0) == 0:
        trend_factors.append(0.05)

    # Payment trend factor
    payment_status = customer.get("payment_status", "current")
    if payment_status == "overdue":
        trend_factors.append(-0.2)
    elif payment_status == "current":
        trend_factors.append(0.02)

    # Calculate trend
    trend_change = sum(trend_factors)

    if trend_change > 0.1:
        trend = "improving"
    elif trend_change < -0.1:
        trend = "declining"
    else:
        trend = "stable"

    # Forecast 30-day health score
    forecast_score = min(1.0, max(0.0, health_score + trend_change))

    return {
        "trend": trend,
        "change_30d": round(trend_change, 2),
        "forecast_30d": round(forecast_score, 2),
        "confidence": 0.75,  # Simulated confidence level
    }


def recommend_actions(customer):
    """
    Generate comprehensive action recommendations
    """
    recommendations = []
    health_score = calculate_health_score(customer)
    customer_type = customer.get("customer_type", "mid_market")

    # Critical health actions
    if health_score < 0.3:
        recommendations.extend(
            [
                {
                    "action_type": "urgent_intervention",
                    "description": "Schedule emergency success review within 24 hours",
                    "urgency": "immediate",
                    "effort": "high",
                    "expected_impact": "high",
                    "priority": 1,
                },
                {
                    "action_type": "executive_escalation",
                    "description": "Escalate to C-level stakeholders",
                    "urgency": "immediate",
                    "effort": "medium",
                    "expected_impact": "high",
                    "priority": 2,
                },
            ]
        )

    # Payment-specific actions
    payment_status = customer.get("payment_status", "current")
    if payment_status in ["late", "overdue"]:
        recommendations.append(
            {
                "action_type": "payment_resolution",
                "description": "Coordinate with billing team to resolve payment issues",
                "urgency": "within_24h",
                "effort": "medium",
                "expected_impact": "high",
                "priority": 3,
            }
        )

    # Engagement actions
    if customer.get("last_login_days", 0) > 14:
        recommendations.append(
            {
                "action_type": "re_engagement",
                "description": "Launch targeted re-engagement campaign",
                "urgency": "within_week",
                "effort": "low",
                "expected_impact": "medium",
                "priority": 4,
            }
        )

    # Feature adoption actions
    adoption = customer.get("feature_adoption", {})
    if adoption and sum(adoption.values()) / len(adoption) < 0.5:
        recommendations.append(
            {
                "action_type": "training_program",
                "description": "Enroll in advanced feature training program",
                "urgency": "within_week",
                "effort": "medium",
                "expected_impact": "medium",
                "priority": 5,
            }
        )

    # Expansion opportunities
    if health_score > 0.8 and customer.get("nps_score", 0) >= 8:
        recommendations.append(
            {
                "action_type": "expansion_discussion",
                "description": "Present upgrade and expansion opportunities",
                "urgency": "within_week",
                "effort": "low",
                "expected_impact": "high",
                "priority": 6,
            }
        )

    return sorted(recommendations, key=lambda x: x["priority"])
