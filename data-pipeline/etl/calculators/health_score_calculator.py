"""
Health Score Calculator for ETL Pipeline.
Adapts existing health score algorithm to work with ETL data structure.
"""

import logging
from datetime import datetime
from typing import Any, Dict

import pandas as pd


class HealthScoreCalculator:
    """
    Calculates health scores using the existing 8-dimension algorithm
    adapted for ETL pipeline data structure.
    """

    def __init__(self):
        """Initialize the health score calculator."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def calculate_health_scores(self, integrated_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate health scores for all customers in the integrated dataset.

        Args:
            integrated_data: DataFrame with integrated customer data

        Returns:
            DataFrame with calculated health scores and factors
        """
        df = integrated_data.copy()

        # Calculate individual health factors
        df["usage_factor"] = df.apply(self._calculate_usage_factor, axis=1)
        df["engagement_factor"] = df.apply(self._calculate_engagement_factor, axis=1)
        df["support_factor"] = df.apply(self._calculate_support_factor, axis=1)
        df["payment_factor"] = df.apply(self._calculate_payment_factor, axis=1)
        df["adoption_factor"] = df.apply(self._calculate_adoption_factor, axis=1)
        df["satisfaction_factor"] = df.apply(
            self._calculate_satisfaction_factor, axis=1
        )
        df["lifecycle_factor"] = df.apply(self._calculate_lifecycle_factor, axis=1)
        df["value_factor"] = df.apply(self._calculate_value_factor, axis=1)

        # Calculate weighted health score
        df["calculated_health_score"] = df.apply(self._calculate_weighted_score, axis=1)

        # Add health categories and risk levels
        df["health_category"] = pd.cut(
            df["calculated_health_score"] * 100,
            bins=[0, 30, 50, 70, 85, 100],
            labels=["critical", "at_risk", "stable", "healthy", "excellent"],
        )

        df["risk_level"] = df["calculated_health_score"].apply(self._categorize_risk)

        # Add calculation metadata
        df["health_score_calculated_at"] = datetime.now().isoformat()

        self.logger.info(f"Calculated health scores for {len(df)} customers")

        return df

    def _get_customer_weights(self, customer_type: str) -> Dict[str, float]:
        """Get scoring weights based on customer type."""
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
            "mid-market": {  # Note: adapted for our data format
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
        return weights.get(customer_type.lower(), weights["mid-market"])

    def _calculate_usage_factor(self, row: pd.Series) -> float:
        """Calculate usage-based score from activity data."""
        # Use activity metrics to calculate usage
        total_activities = row.get("total_activities", 0)
        avg_session_duration = row.get("avg_session_duration", 0)
        login_sessions = row.get("login_sessions", 0)

        # Normalize activity metrics
        activity_score = min(
            1.0, total_activities / 100
        )  # Assume 100+ activities = max score
        session_score = min(1.0, avg_session_duration / 120)  # 2+ hours avg = max score
        login_score = min(1.0, login_sessions / 30)  # 30+ logins = max score

        # Calculate days since last activity (simulated from activity date range)
        last_activity_max = row.get("activity_date_max", datetime.now())
        if pd.isna(last_activity_max):
            last_login_penalty = 1.0
        else:
            if isinstance(last_activity_max, str):
                last_activity_max = pd.to_datetime(last_activity_max)
            days_since_last = (datetime.now() - last_activity_max).days
            last_login_penalty = min(days_since_last / 30, 1.0)

        usage_score = activity_score * 0.4 + session_score * 0.3 + login_score * 0.3
        return max(0, usage_score - (last_login_penalty * 0.3))

    def _calculate_engagement_factor(self, row: pd.Series) -> float:
        """Calculate engagement score from participation and training data."""
        avg_participation = row.get("avg_participation", 0)

        # Convert participation score (0-10) to 0-1 scale
        engagement_score = avg_participation / 10.0

        # Simulated onboarding completion based on customer age
        customer_age_days = row.get("customer_age_days", 0)
        onboarding_bonus = 0.1 if customer_age_days > 30 else -0.2

        return min(1.0, max(0, engagement_score + onboarding_bonus))

    def _calculate_support_factor(self, row: pd.Series) -> float:
        """Calculate support health factor from support tickets."""
        total_tickets = row.get("total_tickets", 0)
        avg_satisfaction = row.get(
            "avg_satisfaction", 10
        )  # Default to high satisfaction

        # Base score from ticket volume
        if total_tickets == 0:
            volume_score = 1.0
        elif total_tickets <= 2:
            volume_score = 0.8
        elif total_tickets <= 5:
            volume_score = 0.5
        else:
            volume_score = max(0, 0.3 - (total_tickets - 5) * 0.05)

        # Adjust based on satisfaction
        satisfaction_multiplier = avg_satisfaction / 10.0

        return volume_score * satisfaction_multiplier

    def _calculate_payment_factor(self, row: pd.Series) -> float:
        """Calculate payment health factor."""
        payment_status = row.get("payment_status", "current")
        status_scores = {"current": 1.0, "late": 0.6, "overdue": 0.2, "failed": 0.0}
        return status_scores.get(payment_status, 0.5)

    def _calculate_adoption_factor(self, row: pd.Series) -> float:
        """Calculate feature adoption score from activity patterns."""
        core_feature_usage = row.get("core_feature_usage", 0)
        advanced_feature_usage = row.get("advanced_feature_usage", 0)
        total_activities = row.get("total_activities", 1)

        if total_activities == 0:
            return 0.3

        # Calculate adoption ratios
        core_ratio = core_feature_usage / total_activities
        advanced_ratio = advanced_feature_usage / total_activities
        integration_ratio = 0.1  # Simulated - could be extracted from activity types

        # Weighted adoption score
        score = core_ratio * 0.5 + advanced_ratio * 0.3 + integration_ratio * 0.2

        return min(1.0, score)

    def _calculate_satisfaction_factor(self, row: pd.Series) -> float:
        """Calculate satisfaction score from NPS and CSAT."""
        nps_score = row.get("nps_score", 5)
        csat_score = row.get("csat_score", 7)

        # Combine NPS and CSAT (both on 0-10 scale)
        combined_score = nps_score * 0.6 + csat_score * 0.4

        # Convert to 0-1 scale
        return min(1.0, max(0, combined_score / 10))

    def _calculate_lifecycle_factor(self, row: pd.Series) -> float:
        """Calculate lifecycle stage factor."""
        contract_start = row.get("contract_start")

        if pd.isna(contract_start):
            return 0.8  # Default score

        if isinstance(contract_start, str):
            contract_start = pd.to_datetime(contract_start)

        days_since_start = (datetime.now() - contract_start).days

        # New customers (< 90 days) get lifecycle bonus
        if days_since_start < 90:
            return 1.0
        # Established customers (> 365 days) get stability bonus
        elif days_since_start > 365:
            return 0.9
        else:
            return 0.8

    def _calculate_value_factor(self, row: pd.Series) -> float:
        """Calculate value-based factor from MRR."""
        mrr = row.get("mrr", 0)

        # Logarithmic scaling for MRR influence
        if mrr < 1000:
            return 0.5
        elif mrr < 5000:
            return 0.7
        elif mrr < 10000:
            return 0.9
        else:
            return 1.0

    def _calculate_weighted_score(self, row: pd.Series) -> float:
        """Calculate final weighted health score."""
        customer_type = row.get("customer_type", "mid-market")
        weights = self._get_customer_weights(customer_type)

        factors = {
            "usage": row.get("usage_factor", 0),
            "engagement": row.get("engagement_factor", 0),
            "support": row.get("support_factor", 0),
            "payment": row.get("payment_factor", 0),
            "adoption": row.get("adoption_factor", 0),
            "satisfaction": row.get("satisfaction_factor", 0),
            "lifecycle": row.get("lifecycle_factor", 0),
            "value": row.get("value_factor", 0),
        }

        # Calculate weighted score
        weighted_score = 0
        for factor, score in factors.items():
            weighted_score += score * weights.get(factor, 0.1)

        # Normalize to 0-1 range
        final_score = min(1.0, max(0.0, weighted_score))

        return round(final_score, 3)

    def _categorize_risk(self, health_score: float) -> str:
        """Categorize risk level based on health score."""
        if health_score < 0.3:
            return "critical"
        elif health_score < 0.7:
            return "medium"
        else:
            return "healthy"

    def get_health_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for calculated health scores."""
        return {
            "total_customers": len(df),
            "avg_health_score": df["calculated_health_score"].mean(),
            "health_distribution": df["health_category"].value_counts().to_dict(),
            "risk_distribution": df["risk_level"].value_counts().to_dict(),
            "factor_averages": {
                "usage": df["usage_factor"].mean(),
                "engagement": df["engagement_factor"].mean(),
                "support": df["support_factor"].mean(),
                "payment": df["payment_factor"].mean(),
                "adoption": df["adoption_factor"].mean(),
                "satisfaction": df["satisfaction_factor"].mean(),
                "lifecycle": df["lifecycle_factor"].mean(),
                "value": df["value_factor"].mean(),
            },
        }
