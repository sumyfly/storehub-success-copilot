"""
Data Transformers for Customer Success ETL Pipeline.
"""

from datetime import datetime, timedelta
from typing import Dict

import numpy as np
import pandas as pd

from .base_transformer import BaseTransformer


class CustomerDataTransformer(BaseTransformer):
    """Transformer for customer data preparation."""

    def transform(self, data: Dict) -> Dict:
        """Transform customer data for health score calculation."""
        df = data["data"].copy()

        # Clean and validate
        df = self.clean_dataframe(df, "Customer")
        self.validate_required_fields(df, ["customer_id", "company_name"], "Customer")

        # Standardize customer types
        df["customer_type"] = df["customer_type"].str.lower()

        # Calculate customer maturity score
        df["customer_maturity_score"] = self._calculate_maturity_score(df)

        # Categorize by health score ranges for analysis
        df["health_category"] = pd.cut(
            df["health_score"],
            bins=[0, 30, 50, 70, 85, 100],
            labels=["critical", "at_risk", "stable", "healthy", "excellent"],
        )

        # Add customer value tier based on MRR
        df["value_tier"] = pd.cut(
            df["mrr"],
            bins=[0, 5000, 15000, float("inf")],
            labels=["low", "medium", "high"],
        )

        transformed_data = {
            "data": df,
            "record_count": len(df),
            "customer_distribution": df["customer_type"].value_counts().to_dict(),
            "health_distribution": df["health_category"].value_counts().to_dict(),
            "value_distribution": df["value_tier"].value_counts().to_dict(),
        }

        return self.add_transformation_metadata(
            transformed_data, "customer_preparation"
        )

    def _calculate_maturity_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate customer maturity score based on tenure and contract data."""
        now = datetime.now()

        # Customer age in months
        customer_age_months = df["customer_age_days"] / 30

        # Contract duration in months
        contract_duration_months = df["contract_duration_days"] / 30

        # Maturity score (0-100)
        maturity_score = np.minimum(
            (customer_age_months * 2) + (contract_duration_months * 1.5), 100
        )

        return maturity_score.fillna(0)


class SalesDataTransformer(BaseTransformer):
    """Transformer for sales data aggregation."""

    def transform(self, data: Dict) -> Dict:
        """Transform sales data for revenue analysis."""
        df = data["data"].copy()

        # Clean and validate
        df = self.clean_dataframe(df, "Sales")
        self.validate_required_fields(df, ["customer_id", "deal_date"], "Sales")

        # Calculate time windows for revenue trends
        windowed_data = self.calculate_time_windows(df, "deal_date", [30, 90, 180])

        # Aggregate by customer
        customer_sales = self._aggregate_customer_sales(df)

        # Calculate sales velocity metrics
        sales_velocity = self._calculate_sales_velocity(df)

        transformed_data = {
            "data": df,
            "customer_aggregates": customer_sales,
            "sales_velocity": sales_velocity,
            "windowed_data": windowed_data,
            "record_count": len(df),
            "total_revenue": df[df["is_closed_won"]]["deal_amount"].sum(),
            "conversion_rate": df["is_closed_won"].mean(),
        }

        return self.add_transformation_metadata(transformed_data, "sales_aggregation")

    def _aggregate_customer_sales(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate sales metrics by customer."""
        customer_groups = df.groupby("customer_id")

        aggregates = customer_groups.agg(
            {
                "deal_amount": ["sum", "mean", "count"],
                "mrr_impact": "sum",
                "is_closed_won": "mean",
                "is_expansion": "sum",
                "deal_date": ["min", "max"],
            }
        ).round(2)

        # Flatten column names
        aggregates.columns = [
            "_".join(col).strip() for col in aggregates.columns.values
        ]

        return aggregates.reset_index()

    def _calculate_sales_velocity(self, df: pd.DataFrame) -> Dict:
        """Calculate sales velocity metrics."""
        recent_df = df[df["deal_age_days"] <= 90]  # Last 90 days

        velocity_metrics = {
            "deals_per_month": len(recent_df) / 3,  # 90 days = ~3 months
            "avg_deal_size": recent_df["deal_amount"].mean(),
            "win_rate": recent_df["is_closed_won"].mean(),
            "expansion_rate": recent_df["is_expansion"].mean(),
            "velocity_score": 0,  # Will be calculated
        }

        # Calculate composite velocity score (0-100)
        velocity_metrics["velocity_score"] = min(
            (velocity_metrics["deals_per_month"] * 10)
            + (velocity_metrics["win_rate"] * 50)
            + (velocity_metrics["expansion_rate"] * 30),
            100,
        )

        return velocity_metrics


class SupportDataTransformer(BaseTransformer):
    """Transformer for support data analysis."""

    def transform(self, data: Dict) -> Dict:
        """Transform support data for customer health insights."""
        df = data["data"].copy()

        # Clean and validate
        df = self.clean_dataframe(df, "Support")
        self.validate_required_fields(df, ["customer_id", "created_date"], "Support")

        # Calculate time windows for support trends
        windowed_data = self.calculate_time_windows(df, "created_date", [7, 30, 90])

        # Aggregate by customer
        customer_support = self._aggregate_customer_support(df)

        # Calculate support health metrics
        support_health = self._calculate_support_health(df)

        transformed_data = {
            "data": df,
            "customer_aggregates": customer_support,
            "support_health": support_health,
            "windowed_data": windowed_data,
            "record_count": len(df),
            "avg_satisfaction": df["satisfaction_score"].mean(),
            "avg_resolution_time": df["resolution_hours"].mean(),
        }

        return self.add_transformation_metadata(transformed_data, "support_analysis")

    def _aggregate_customer_support(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate support metrics by customer."""
        customer_groups = df.groupby("customer_id")

        aggregates = customer_groups.agg(
            {
                "ticket_id": "count",
                "satisfaction_score": "mean",
                "resolution_hours": "mean",
                "is_high_priority": "sum",
                "is_resolved": "mean",
                "created_date": ["min", "max"],
            }
        ).round(2)

        # Flatten column names
        aggregates.columns = [
            "_".join(col).strip() for col in aggregates.columns.values
        ]

        # Rename for clarity
        aggregates = aggregates.rename(
            columns={
                "ticket_id_count": "total_tickets",
                "satisfaction_score_mean": "avg_satisfaction",
                "resolution_hours_mean": "avg_resolution_hours",
                "is_high_priority_sum": "high_priority_tickets",
                "is_resolved_mean": "resolution_rate",
            }
        )

        return aggregates.reset_index()

    def _calculate_support_health(self, df: pd.DataFrame) -> Dict:
        """Calculate overall support health metrics."""
        recent_df = df[df["created_date"] >= (datetime.now() - timedelta(days=30))]

        return {
            "ticket_volume_trend": len(recent_df)
            / max(len(df), 1),  # Recent vs total ratio
            "satisfaction_trend": recent_df["satisfaction_score"].mean(),
            "resolution_efficiency": recent_df["is_resolved"].mean(),
            "escalation_rate": recent_df["is_high_priority"].mean(),
            "avg_response_time": recent_df["resolution_hours"].mean(),
        }


class ActivityDataTransformer(BaseTransformer):
    """Transformer for user activity analysis."""

    def transform(self, data: Dict) -> Dict:
        """Transform activity data for engagement insights."""
        df = data["data"].copy()

        # Clean and validate
        df = self.clean_dataframe(df, "Activity")
        self.validate_required_fields(df, ["customer_id", "activity_date"], "Activity")

        # Calculate time windows for activity trends
        windowed_data = self.calculate_time_windows(df, "activity_date", [7, 30, 90])

        # Aggregate by customer
        customer_activity = self._aggregate_customer_activity(df)

        # Calculate engagement metrics
        engagement_metrics = self._calculate_engagement_metrics(df)

        transformed_data = {
            "data": df,
            "customer_aggregates": customer_activity,
            "engagement_metrics": engagement_metrics,
            "windowed_data": windowed_data,
            "record_count": len(df),
            "avg_session_duration": df["session_duration"].mean(),
            "avg_participation_score": df["participation_score"].mean(),
        }

        return self.add_transformation_metadata(transformed_data, "activity_analysis")

    def _aggregate_customer_activity(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate activity metrics by customer."""
        customer_groups = df.groupby("customer_id")

        aggregates = customer_groups.agg(
            {
                "activity_id": "count",
                "session_duration": "mean",
                "participation_score": "mean",
                "login_count": "sum",
                "is_login": "sum",
                "is_core_feature": "sum",
                "is_advanced_feature": "sum",
                "activity_date": ["min", "max"],
            }
        ).round(2)

        # Flatten column names
        aggregates.columns = [
            "_".join(col).strip() for col in aggregates.columns.values
        ]

        # Rename for clarity
        aggregates = aggregates.rename(
            columns={
                "activity_id_count": "total_activities",
                "session_duration_mean": "avg_session_duration",
                "participation_score_mean": "avg_participation",
                "login_count_sum": "total_logins",
                "is_login_sum": "login_sessions",
                "is_core_feature_sum": "core_feature_usage",
                "is_advanced_feature_sum": "advanced_feature_usage",
            }
        )

        return aggregates.reset_index()

    def _calculate_engagement_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate engagement health metrics."""
        recent_df = df[df["activity_date"] >= (datetime.now() - timedelta(days=30))]

        return {
            "activity_frequency": len(recent_df) / 30,  # Activities per day
            "feature_adoption_rate": recent_df["is_advanced_feature"].mean(),
            "session_quality": recent_df["participation_score"].mean(),
            "user_stickiness": recent_df["is_login"].sum()
            / max(recent_df["customer_id"].nunique(), 1),
            "engagement_depth": recent_df["session_duration"].mean(),
        }


class DataIntegrationTransformer(BaseTransformer):
    """Transformer for integrating all data sources."""

    def transform(self, data: Dict) -> Dict:
        """Integrate and prepare all data for health score calculation."""
        # Extract transformed data from each source
        customer_data = data["customers"]["data"]
        sales_aggregates = data["sales"]["customer_aggregates"]
        support_aggregates = data["support"]["customer_aggregates"]
        activity_aggregates = data["activity"]["customer_aggregates"]

        # Start with customer data as base
        integrated_df = customer_data.copy()

        # Merge sales data
        integrated_df = integrated_df.merge(
            sales_aggregates, on="customer_id", how="left", suffixes=("", "_sales")
        )

        # Merge support data
        integrated_df = integrated_df.merge(
            support_aggregates, on="customer_id", how="left", suffixes=("", "_support")
        )

        # Merge activity data
        integrated_df = integrated_df.merge(
            activity_aggregates,
            on="customer_id",
            how="left",
            suffixes=("", "_activity"),
        )

        # Fill missing values with defaults
        integrated_df = self._fill_missing_values(integrated_df)

        # Calculate integration quality metrics
        integration_quality = self._assess_integration_quality(integrated_df)

        transformed_data = {
            "integrated_data": integrated_df,
            "integration_quality": integration_quality,
            "record_count": len(integrated_df),
            "data_completeness": integrated_df.count().to_dict(),
        }

        return self.add_transformation_metadata(transformed_data, "data_integration")

    def _fill_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values with appropriate defaults."""
        # Sales metrics defaults
        sales_columns = [
            col
            for col in df.columns
            if "sales" in col or col.startswith("deal_") or col.startswith("mrr_")
        ]
        df[sales_columns] = df[sales_columns].fillna(0)

        # Support metrics defaults
        support_columns = [
            col
            for col in df.columns
            if "support" in col or "ticket" in col or "satisfaction" in col
        ]
        df[support_columns] = df[support_columns].fillna(0)

        # Activity metrics defaults
        activity_columns = [
            col
            for col in df.columns
            if "activity" in col or "session" in col or "participation" in col
        ]
        df[activity_columns] = df[activity_columns].fillna(0)

        return df

    def _assess_integration_quality(self, df: pd.DataFrame) -> Dict:
        """Assess the quality of data integration."""
        total_customers = len(df)

        # Count customers with data in each source
        has_sales = (df["deal_amount_sum"].fillna(0) > 0).sum()
        has_support = (df["total_tickets"].fillna(0) > 0).sum()
        has_activity = (df["total_activities"].fillna(0) > 0).sum()

        return {
            "total_customers": total_customers,
            "customers_with_sales_data": has_sales,
            "customers_with_support_data": has_support,
            "customers_with_activity_data": has_activity,
            "sales_coverage_pct": (has_sales / total_customers * 100)
            if total_customers > 0
            else 0,
            "support_coverage_pct": (has_support / total_customers * 100)
            if total_customers > 0
            else 0,
            "activity_coverage_pct": (has_activity / total_customers * 100)
            if total_customers > 0
            else 0,
        }
