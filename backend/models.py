from typing import List, Optional

from pydantic import BaseModel, Field


class Customer(BaseModel):
    id: int
    name: str
    mrr: float = Field(..., description="Monthly Recurring Revenue")
    usage_score: float = Field(..., ge=0, le=1, description="Usage score from 0 to 1")
    support_tickets: int = Field(..., ge=0, description="Number of support tickets")
    last_login_days: int = Field(..., ge=0, description="Days since last login")
    contract_date: str = Field(..., description="Contract start date")
    health_score: Optional[float] = Field(
        None, ge=0, le=1, description="Calculated health score"
    )


class Alert(BaseModel):
    customer_id: int
    customer_name: str
    type: str = Field(..., description="Alert type: churn_risk, engagement_risk, etc.")
    severity: str = Field(..., description="Alert severity: critical, medium, low")
    message: str = Field(..., description="Human-readable alert message")
    actions: List[str] = Field(..., description="Suggested actions to take")
    created_at: Optional[str] = Field(None, description="When alert was generated")


class HealthScore(BaseModel):
    customer_id: int
    customer_name: str
    overall_score: float = Field(..., ge=0, le=1)
    usage_factor: float = Field(..., ge=0, le=1)
    support_factor: float = Field(..., ge=0, le=1)
    engagement_factor: float = Field(..., ge=0, le=1)
    risk_level: str = Field(..., description="critical, medium, or healthy")


class ActionRecommendation(BaseModel):
    customer_id: int
    action_type: str
    description: str
    urgency: str = Field(..., description="immediate, within_24h, within_week")
    effort: str = Field(..., description="low, medium, high")
    expected_impact: str = Field(..., description="low, medium, high")


class DashboardStats(BaseModel):
    total_customers: int
    critical_alerts: int
    medium_risk_customers: int
    healthy_customers: int
    total_alerts: int
