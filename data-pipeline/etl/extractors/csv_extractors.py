"""
CSV Data Extractors for Customer Success ETL Pipeline.
"""

from datetime import datetime
from typing import Dict

import pandas as pd

from .base_extractor import BaseExtractor


class CustomerExtractor(BaseExtractor):
    """Extractor for customer data."""

    REQUIRED_COLUMNS = [
        "customer_id",
        "name",
        "customer_type",
        "industry",
        "company_size",
        "contract_date",
        "contract_length_months",
        "payment_status",
        "nps_score",
        "onboarding_completed",
    ]

    def extract(self) -> Dict:
        """Extract customer data with validation and processing."""
        df = self.extract_csv("customers.csv", self.REQUIRED_COLUMNS)

        # Convert date columns
        df["contract_date"] = pd.to_datetime(df["contract_date"])

        # Add derived fields - calculate contract end date from start + length
        df["contract_end_date"] = df["contract_date"] + pd.to_timedelta(
            df["contract_length_months"] * 30, unit="D"
        )
        df["customer_age_days"] = (datetime.now() - df["contract_date"]).dt.days
        df["contract_duration_days"] = (
            df["contract_length_months"] * 30
        )  # Convert months to days

        # Add calculated fields to match expected schema
        df["company_name"] = df["name"]  # Alias for backward compatibility
        df["signup_date"] = df["contract_date"]  # Use contract date as signup
        df["contract_start"] = df["contract_date"]
        df["contract_end"] = df["contract_end_date"]

        # Set default values for missing health metrics
        df["health_score"] = 0.5  # Will be calculated by health engine
        df["csat_score"] = df["nps_score"] / 10  # Convert NPS to CSAT scale
        df["mrr"] = 0  # Will be calculated from sales data
        df["account_manager"] = "Unassigned"
        df["country"] = "Unknown"

        # Validate data quality
        quality_metrics = self.validate_data_quality(df, "Customer")

        return {
            "data": df,
            "record_count": len(df),
            "quality_metrics": quality_metrics,
            "extracted_at": datetime.now().isoformat(),
        }


class SalesExtractor(BaseExtractor):
    """Extractor for sales data."""

    REQUIRED_COLUMNS = [
        "transaction_id",
        "customer_id",
        "deal_date",
        "deal_amount",
        "deal_type",
        "deal_stage",
        "mrr",
        "account_manager",
        "product_type",
    ]

    def extract(self) -> Dict:
        """Extract sales data with validation and processing."""
        df = self.extract_csv("sales.csv", self.REQUIRED_COLUMNS)

        # Convert date columns
        df["deal_date"] = pd.to_datetime(df["deal_date"])

        # Add derived fields
        df["deal_age_days"] = (datetime.now() - df["deal_date"]).dt.days
        df["is_closed_won"] = df["deal_stage"] == "closed_won"
        df["is_expansion"] = df["deal_type"].isin(["expansion", "upsell"])

        # Calculate MRR impact for new deals
        df["mrr_impact"] = df.apply(
            lambda row: row["mrr"] if row["is_closed_won"] else 0, axis=1
        )

        # Validate data quality
        quality_metrics = self.validate_data_quality(df, "Sales")

        return {
            "data": df,
            "record_count": len(df),
            "quality_metrics": quality_metrics,
            "extracted_at": datetime.now().isoformat(),
        }


class SupportExtractor(BaseExtractor):
    """Extractor for support data."""

    REQUIRED_COLUMNS = [
        "ticket_id",
        "customer_id",
        "created_date",
        "resolved_date",
        "priority",
        "category",
        "status",
        "satisfaction_score",
        "agent_name",
        "resolution_hours",
    ]

    def extract(self) -> Dict:
        """Extract support data with validation and processing."""
        df = self.extract_csv("support.csv", self.REQUIRED_COLUMNS)

        # Convert date columns
        df["created_date"] = pd.to_datetime(df["created_date"])
        df["resolved_date"] = pd.to_datetime(df["resolved_date"])

        # Add derived fields
        df["is_resolved"] = df["status"] == "resolved"
        df["is_high_priority"] = df["priority"].isin(["high", "urgent"])
        df["response_time_hours"] = df["resolution_hours"]  # Alias for clarity

        # Calculate satisfaction categories
        df["satisfaction_category"] = pd.cut(
            df["satisfaction_score"],
            bins=[0, 6, 8, 10],
            labels=["poor", "good", "excellent"],
        )

        # Validate data quality
        quality_metrics = self.validate_data_quality(df, "Support")

        return {
            "data": df,
            "record_count": len(df),
            "quality_metrics": quality_metrics,
            "extracted_at": datetime.now().isoformat(),
        }


class ActivityExtractor(BaseExtractor):
    """Extractor for user activity data."""

    REQUIRED_COLUMNS = [
        "activity_id",
        "customer_id",
        "activity_date",
        "activity_type",
        "feature_category",
        "session_duration",
        "login_count",
        "participation_score",
    ]

    def extract(self) -> Dict:
        """Extract activity data with validation and processing."""
        df = self.extract_csv("activity.csv", self.REQUIRED_COLUMNS)

        # Convert date columns
        df["activity_date"] = pd.to_datetime(df["activity_date"])

        # Add derived fields
        df["activity_age_days"] = (datetime.now() - df["activity_date"]).dt.days
        df["is_login"] = df["activity_type"] == "login"
        df["is_core_feature"] = df["feature_category"] == "core"
        df["is_advanced_feature"] = df["feature_category"] == "advanced"

        # Categorize session duration
        df["session_length_category"] = pd.cut(
            df["session_duration"],
            bins=[0, 30, 60, 120, float("inf")],
            labels=["short", "medium", "long", "extended"],
        )

        # Categorize participation scores
        df["engagement_level"] = pd.cut(
            df["participation_score"],
            bins=[0, 5, 7, 9, 10],
            labels=["low", "medium", "high", "excellent"],
        )

        # Validate data quality
        quality_metrics = self.validate_data_quality(df, "Activity")

        return {
            "data": df,
            "record_count": len(df),
            "quality_metrics": quality_metrics,
            "extracted_at": datetime.now().isoformat(),
        }


class CombinedExtractor(BaseExtractor):
    """Meta-extractor that combines all data sources."""

    def __init__(self, data_path: str):
        super().__init__(data_path)
        self.customer_extractor = CustomerExtractor(data_path)
        self.sales_extractor = SalesExtractor(data_path)
        self.support_extractor = SupportExtractor(data_path)
        self.activity_extractor = ActivityExtractor(data_path)

    def extract(self) -> Dict:
        """Extract all data sources with comprehensive validation."""
        start_time = datetime.now()

        # Extract all data sources
        customer_data = self.customer_extractor.extract()
        sales_data = self.sales_extractor.extract()
        support_data = self.support_extractor.extract()
        activity_data = self.activity_extractor.extract()

        end_time = datetime.now()

        # Combine metrics
        total_records = (
            customer_data["record_count"]
            + sales_data["record_count"]
            + support_data["record_count"]
            + activity_data["record_count"]
        )

        return {
            "customers": customer_data,
            "sales": sales_data,
            "support": support_data,
            "activity": activity_data,
            "extraction_summary": {
                "total_records": total_records,
                "extraction_time_seconds": (end_time - start_time).total_seconds(),
                "extracted_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
            },
        }
