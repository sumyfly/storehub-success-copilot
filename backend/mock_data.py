# Enhanced mock customer data with multiple dimensions for prototype
MOCK_CUSTOMERS = [
    {
        "id": 1,
        "name": "Acme Corp",
        "mrr": 5000,
        "usage_score": 0.1,
        "support_tickets": 8,
        "last_login_days": 45,
        "contract_date": "2023-01-15",
        "customer_type": "enterprise",
        "payment_status": "overdue",
        "feature_adoption": {"core": 0.2, "advanced": 0.0, "integrations": 0.1},
        "engagement_score": 0.2,
        "onboarding_completed": True,
        "contract_length_months": 12,
        "industry": "manufacturing",
        "company_size": "large",
        "nps_score": 3,
        # Hour 6: Customer Journey Analytics
        "lifecycle_stage": "at_risk",
        "days_in_stage": 45,
        "previous_stage": "mature",
        "time_to_value_days": 180,
        "journey_velocity": -0.4,
        # Hour 6: Predictive Risk Modeling
        "churn_probability_30d": 0.85,
        "churn_probability_60d": 0.92,
        "churn_probability_90d": 0.96,
        "risk_factors": ["payment_overdue", "low_usage", "high_support_load"],
        "risk_trend": "increasing",
        # Hour 6: Revenue Intelligence
        "expansion_score": 0.15,
        "upsell_readiness": 0.1,
        "cross_sell_potential": [],
        "revenue_growth_trend": -0.25,
        "contract_renewal_probability": 0.20,
        "ltv_prediction": 8500,
    },
    {
        "id": 2,
        "name": "Tech Solutions Ltd",
        "mrr": 3000,
        "usage_score": 0.4,
        "support_tickets": 2,
        "last_login_days": 16,
        "contract_date": "2023-03-01",
        "customer_type": "mid_market",
        "payment_status": "current",
        "feature_adoption": {"core": 0.6, "advanced": 0.2, "integrations": 0.3},
        "engagement_score": 0.5,
        "onboarding_completed": True,
        "contract_length_months": 6,
        "industry": "technology",
        "company_size": "medium",
        "nps_score": 6,
        # Hour 6: Customer Journey Analytics
        "lifecycle_stage": "adoption",
        "days_in_stage": 90,
        "previous_stage": "onboarding",
        "time_to_value_days": 75,
        "journey_velocity": 0.1,
        # Hour 6: Predictive Risk Modeling
        "churn_probability_30d": 0.35,
        "churn_probability_60d": 0.45,
        "churn_probability_90d": 0.55,
        "risk_factors": ["declining_engagement", "moderate_usage"],
        "risk_trend": "stable",
        # Hour 6: Revenue Intelligence
        "expansion_score": 0.45,
        "upsell_readiness": 0.3,
        "cross_sell_potential": ["training", "integrations"],
        "revenue_growth_trend": 0.05,
        "contract_renewal_probability": 0.65,
        "ltv_prediction": 18000,
    },
    {
        "id": 3,
        "name": "Innovation Inc",
        "mrr": 8000,
        "usage_score": 0.8,
        "support_tickets": 1,
        "last_login_days": 2,
        "contract_date": "2022-12-01",
        "customer_type": "enterprise",
        "payment_status": "current",
        "feature_adoption": {"core": 0.9, "advanced": 0.7, "integrations": 0.8},
        "engagement_score": 0.9,
        "onboarding_completed": True,
        "contract_length_months": 24,
        "industry": "technology",
        "company_size": "large",
        "nps_score": 9,
        # Hour 6: Customer Journey Analytics
        "lifecycle_stage": "growth",
        "days_in_stage": 120,
        "previous_stage": "adoption",
        "time_to_value_days": 45,
        "journey_velocity": 0.3,
        # Hour 6: Predictive Risk Modeling
        "churn_probability_30d": 0.05,
        "churn_probability_60d": 0.08,
        "churn_probability_90d": 0.12,
        "risk_factors": [],
        "risk_trend": "stable",
        # Hour 6: Revenue Intelligence
        "expansion_score": 0.85,
        "upsell_readiness": 0.9,
        "cross_sell_potential": ["analytics", "api", "premium_support"],
        "revenue_growth_trend": 0.15,
        "contract_renewal_probability": 0.95,
        "ltv_prediction": 45000,
    },
    {
        "id": 4,
        "name": "StartupCo",
        "mrr": 2000,
        "usage_score": 0.9,
        "support_tickets": 0,
        "last_login_days": 1,
        "contract_date": "2023-06-15",
        "customer_type": "startup",
        "payment_status": "current",
        "feature_adoption": {"core": 0.8, "advanced": 0.5, "integrations": 0.4},
        "engagement_score": 0.8,
        "onboarding_completed": True,
        "contract_length_months": 3,
        "industry": "fintech",
        "company_size": "small",
        "nps_score": 8,
    },
    {
        "id": 5,
        "name": "Global Enterprises",
        "mrr": 15000,
        "usage_score": 0.2,
        "support_tickets": 12,
        "last_login_days": 30,
        "contract_date": "2022-08-01",
        "customer_type": "enterprise",
        "payment_status": "current",
        "feature_adoption": {"core": 0.3, "advanced": 0.1, "integrations": 0.0},
        "engagement_score": 0.1,
        "onboarding_completed": False,
        "contract_length_months": 36,
        "industry": "retail",
        "company_size": "large",
        "nps_score": 4,
    },
    {
        "id": 6,
        "name": "Digital Dynamics",
        "mrr": 4500,
        "usage_score": 0.7,
        "support_tickets": 1,
        "last_login_days": 3,
        "contract_date": "2023-02-20",
        "customer_type": "mid_market",
        "payment_status": "current",
        "feature_adoption": {"core": 0.8, "advanced": 0.4, "integrations": 0.6},
        "engagement_score": 0.7,
        "onboarding_completed": True,
        "contract_length_months": 12,
        "industry": "marketing",
        "company_size": "medium",
        "nps_score": 7,
    },
    {
        "id": 7,
        "name": "Future Systems",
        "mrr": 6500,
        "usage_score": 0.6,
        "support_tickets": 3,
        "last_login_days": 5,
        "contract_date": "2023-04-10",
        "customer_type": "enterprise",
        "payment_status": "current",
        "feature_adoption": {"core": 0.7, "advanced": 0.3, "integrations": 0.5},
        "engagement_score": 0.6,
        "onboarding_completed": True,
        "contract_length_months": 12,
        "industry": "healthcare",
        "company_size": "large",
        "nps_score": 6,
    },
    {
        "id": 8,
        "name": "CloudFirst LLC",
        "mrr": 3500,
        "usage_score": 0.3,
        "support_tickets": 6,
        "last_login_days": 20,
        "contract_date": "2023-01-30",
        "customer_type": "mid_market",
        "payment_status": "current",
        "feature_adoption": {"core": 0.4, "advanced": 0.1, "integrations": 0.2},
        "engagement_score": 0.3,
        "onboarding_completed": True,
        "contract_length_months": 6,
        "industry": "saas",
        "company_size": "medium",
        "nps_score": 5,
    },
    {
        "id": 9,
        "name": "DataDriven Co",
        "mrr": 7200,
        "usage_score": 0.85,
        "support_tickets": 0,
        "last_login_days": 1,
        "contract_date": "2022-11-15",
        "customer_type": "enterprise",
        "payment_status": "current",
        "feature_adoption": {"core": 0.9, "advanced": 0.8, "integrations": 0.9},
        "engagement_score": 0.9,
        "onboarding_completed": True,
        "contract_length_months": 24,
        "industry": "analytics",
        "company_size": "large",
        "nps_score": 9,
    },
    {
        "id": 10,
        "name": "ScaleUp Technologies",
        "mrr": 2800,
        "usage_score": 0.5,
        "support_tickets": 4,
        "last_login_days": 8,
        "contract_date": "2023-05-01",
        "customer_type": "startup",
        "payment_status": "current",
        "feature_adoption": {"core": 0.6, "advanced": 0.2, "integrations": 0.3},
        "engagement_score": 0.5,
        "onboarding_completed": True,
        "contract_length_months": 6,
        "industry": "edtech",
        "company_size": "small",
        "nps_score": 6,
    },
    {
        "id": 11,
        "name": "Enterprise Solutions",
        "mrr": 12000,
        "usage_score": 0.75,
        "support_tickets": 2,
        "last_login_days": 4,
        "contract_date": "2022-09-01",
        "customer_type": "enterprise",
        "payment_status": "current",
        "feature_adoption": {"core": 0.8, "advanced": 0.6, "integrations": 0.7},
        "engagement_score": 0.8,
        "onboarding_completed": True,
        "contract_length_months": 36,
        "industry": "consulting",
        "company_size": "large",
        "nps_score": 8,
    },
    {
        "id": 12,
        "name": "NextGen Industries",
        "mrr": 4000,
        "usage_score": 0.4,
        "support_tickets": 5,
        "last_login_days": 12,
        "contract_date": "2023-02-01",
        "customer_type": "mid_market",
        "payment_status": "current",
        "feature_adoption": {"core": 0.5, "advanced": 0.2, "integrations": 0.1},
        "engagement_score": 0.4,
        "onboarding_completed": False,
        "contract_length_months": 12,
        "industry": "manufacturing",
        "company_size": "medium",
        "nps_score": 5,
    },
    {
        "id": 13,
        "name": "Rapid Growth Inc",
        "mrr": 5500,
        "usage_score": 0.9,
        "support_tickets": 1,
        "last_login_days": 2,
        "contract_date": "2023-07-01",
        "customer_type": "startup",
        "payment_status": "current",
        "feature_adoption": {"core": 0.9, "advanced": 0.6, "integrations": 0.8},
        "engagement_score": 0.9,
        "onboarding_completed": True,
        "contract_length_months": 12,
        "industry": "fintech",
        "company_size": "medium",
        "nps_score": 9,
    },
    {
        "id": 14,
        "name": "Legacy Corp",
        "mrr": 9000,
        "usage_score": 0.25,
        "support_tickets": 9,
        "last_login_days": 35,
        "contract_date": "2022-06-01",
        "customer_type": "enterprise",
        "payment_status": "late",
        "feature_adoption": {"core": 0.3, "advanced": 0.0, "integrations": 0.1},
        "engagement_score": 0.2,
        "onboarding_completed": False,
        "contract_length_months": 36,
        "industry": "banking",
        "company_size": "large",
        "nps_score": 3,
    },
    {
        "id": 15,
        "name": "Modern Workflows",
        "mrr": 3200,
        "usage_score": 0.65,
        "support_tickets": 2,
        "last_login_days": 6,
        "contract_date": "2023-03-15",
        "customer_type": "mid_market",
        "payment_status": "current",
        "feature_adoption": {"core": 0.7, "advanced": 0.4, "integrations": 0.5},
        "engagement_score": 0.6,
        "onboarding_completed": True,
        "contract_length_months": 12,
        "industry": "productivity",
        "company_size": "medium",
        "nps_score": 7,
    },
]

# Enhanced action templates with more scenarios
ACTION_TEMPLATES = {
    "churn_risk": [
        "Schedule urgent call with decision maker",
        "Send personalized retention offer",
        "Escalate to account manager",
        "Provide executive business review",
    ],
    "engagement_risk": [
        "Send check-in email",
        "Share new feature updates",
        "Schedule product training session",
        "Invite to user community",
    ],
    "usage_decline": [
        "Analyze feature adoption gaps",
        "Provide usage optimization consultation",
        "Send best practices guide",
        "Schedule success review call",
    ],
    "support_overload": [
        "Schedule technical review session",
        "Escalate to technical team",
        "Provide additional training resources",
        "Review implementation approach",
    ],
    "payment_risk": [
        "Contact billing department",
        "Review contract terms",
        "Offer payment plan options",
        "Schedule finance team meeting",
    ],
    "onboarding_incomplete": [
        "Schedule onboarding completion session",
        "Assign dedicated success manager",
        "Provide implementation checklist",
        "Offer professional services",
    ],
    "expansion_opportunity": [
        "Present upgrade options",
        "Schedule feature demo",
        "Share ROI case studies",
        "Connect with sales team",
    ],
}

# Customer segmentation labels
CUSTOMER_LABELS = {
    "champions": "🚀 Growth Champion",
    "at_risk": "⚠️ At Risk",
    "expansion_ready": "🔥 Expansion Ready",
    "dormant": "😴 Dormant User",
    "churn_risk": "🆘 Churn Risk",
    "new_customer": "🆕 New Customer",
    "power_user": "💪 Power User",
    "needs_attention": "👀 Needs Attention",
}
