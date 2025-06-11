"""
JSON Data Loaders for Customer Success ETL Pipeline.
"""

from datetime import datetime
from typing import Dict, List

from .base_loader import BaseLoader


class HealthScoreLoader(BaseLoader):
    """Loader for health score calculation results."""

    def load(self, data: Dict, filename: str = "health_scores.json") -> bool:
        """
        Load health score data to JSON file.

        Args:
            data: Health score calculation results
            filename: Output filename

        Returns:
            True if successful, False otherwise
        """
        # Process health score data for output
        processed_data = self._process_health_score_data(data)

        return self.save_json(processed_data, filename)

    def _process_health_score_data(self, data: Dict) -> Dict:
        """Process health score data for JSON output."""
        integrated_df = data.get("integrated_data")

        if integrated_df is None or integrated_df.empty:
            return {"error": "No health score data to process"}

        # Convert to customer records
        customers = []
        for _, row in integrated_df.iterrows():
            customer_record = {
                "customer_id": row["customer_id"],
                "company_name": row["company_name"],
                "customer_type": row["customer_type"],
                "industry": row.get("industry", ""),
                "health_score": {
                    "overall_score": row.get("calculated_health_score", 0),
                    "score_percentage": round(
                        row.get("calculated_health_score", 0) * 100, 1
                    ),
                    "category": row.get("health_category", "unknown"),
                    "risk_level": row.get("risk_level", "unknown"),
                    "calculated_at": row.get(
                        "health_score_calculated_at", datetime.now().isoformat()
                    ),
                },
                "factor_scores": {
                    "usage": round(row.get("usage_factor", 0), 3),
                    "engagement": round(row.get("engagement_factor", 0), 3),
                    "support": round(row.get("support_factor", 0), 3),
                    "payment": round(row.get("payment_factor", 0), 3),
                    "adoption": round(row.get("adoption_factor", 0), 3),
                    "satisfaction": round(row.get("satisfaction_factor", 0), 3),
                    "lifecycle": round(row.get("lifecycle_factor", 0), 3),
                    "value": round(row.get("value_factor", 0), 3),
                },
                "metrics": {
                    "mrr": row.get("mrr", 0),
                    "nps_score": row.get("nps_score", 0),
                    "csat_score": row.get("csat_score", 0),
                    "total_activities": row.get("total_activities", 0),
                    "total_tickets": row.get("total_tickets", 0),
                    "customer_age_days": row.get("customer_age_days", 0),
                },
            }
            customers.append(customer_record)

        # Add summary statistics
        summary = {
            "total_customers": len(customers),
            "avg_health_score": integrated_df["calculated_health_score"].mean(),
            "health_distribution": integrated_df["health_category"]
            .value_counts()
            .to_dict(),
            "risk_distribution": integrated_df["risk_level"].value_counts().to_dict(),
        }

        return {
            "customers": customers,
            "summary": summary,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "data_version": "1.0",
                "source": "etl_pipeline",
            },
        }


class ETLReportLoader(BaseLoader):
    """Loader for comprehensive ETL execution reports."""

    def load(self, data: Dict, filename: str = "etl_report.json") -> bool:
        """
        Load ETL execution report to JSON file.

        Args:
            data: ETL execution results
            filename: Output filename

        Returns:
            True if successful, False otherwise
        """
        # Process ETL report data
        processed_data = self._process_etl_report(data)

        return self.save_json(processed_data, filename)

    def _process_etl_report(self, data: Dict) -> Dict:
        """Process ETL execution data for comprehensive report."""
        extraction_data = data.get("extraction", {})
        transformation_data = data.get("transformation", {})
        calculation_data = data.get("calculation", {})

        report = {
            "execution_summary": {
                "pipeline_executed_at": datetime.now().isoformat(),
                "status": "completed",
                "total_processing_time": data.get("total_time", 0),
                "records_processed": data.get("total_records", 0),
            },
            "extraction_phase": {
                "status": "completed",
                "sources_processed": 4,  # Number of CSV sources (customers, sales, support, activity)
                "total_records_extracted": extraction_data.get(
                    "extraction_summary", {}
                ).get("total_records", 0),
                "extraction_time": extraction_data.get("extraction_summary", {}).get(
                    "extraction_time_seconds", 0
                ),
                "data_quality": {
                    "customers": extraction_data.get("customers", {}).get(
                        "quality_metrics", {}
                    ),
                    "sales": extraction_data.get("sales", {}).get(
                        "quality_metrics", {}
                    ),
                    "support": extraction_data.get("support", {}).get(
                        "quality_metrics", {}
                    ),
                    "activity": extraction_data.get("activity", {}).get(
                        "quality_metrics", {}
                    ),
                },
            },
            "transformation_phase": {
                "status": "completed",
                "transformers_executed": len(transformation_data),
                "integration_quality": transformation_data.get("integration", {}).get(
                    "integration_quality", {}
                ),
                "data_completeness": transformation_data.get("integration", {}).get(
                    "data_completeness", {}
                ),
            },
            "calculation_phase": {
                "status": "completed",
                "health_scores_calculated": calculation_data.get("total_customers", 0),
                "avg_health_score": calculation_data.get("avg_health_score", 0),
                "score_distribution": calculation_data.get("health_distribution", {}),
                "factor_performance": calculation_data.get("factor_averages", {}),
            },
            "output_files": self.get_output_summary(),
        }

        return report


class CustomerDataLoader(BaseLoader):
    """Loader for customer-centric data exports."""

    def load(self, data: Dict, filename: str = "customer_data.json") -> bool:
        """
        Load customer data in API-compatible format.

        Args:
            data: Customer data from ETL pipeline
            filename: Output filename

        Returns:
            True if successful, False otherwise
        """
        # Process customer data for API consumption
        processed_data = self._process_customer_data(data)

        return self.save_json(processed_data, filename)

    def _process_customer_data(self, data: Dict) -> Dict:
        """Process customer data for API-compatible format."""
        integrated_df = data.get("integrated_data")

        if integrated_df is None or integrated_df.empty:
            return {"customers": [], "total": 0}

        customers = []
        for _, row in integrated_df.iterrows():
            customer = {
                "id": row["customer_id"],
                "name": row["company_name"],
                "customer_type": row["customer_type"],
                "industry": row.get("industry", ""),
                "country": row.get("country", ""),
                "signup_date": row.get("signup_date", ""),
                "contract_start": row.get("contract_start", ""),
                "contract_end": row.get("contract_end", ""),
                "mrr": row.get("mrr", 0),
                "health_score": row.get("calculated_health_score", 0),
                "nps_score": row.get("nps_score", 0),
                "csat_score": row.get("csat_score", 0),
                "payment_status": row.get("payment_status", "current"),
                "account_manager": row.get("account_manager", ""),
                "usage_metrics": {
                    "total_activities": row.get("total_activities", 0),
                    "avg_session_duration": row.get("avg_session_duration", 0),
                    "login_sessions": row.get("login_sessions", 0),
                    "core_feature_usage": row.get("core_feature_usage", 0),
                    "advanced_feature_usage": row.get("advanced_feature_usage", 0),
                },
                "support_metrics": {
                    "total_tickets": row.get("total_tickets", 0),
                    "avg_satisfaction": row.get("avg_satisfaction", 0),
                    "avg_resolution_hours": row.get("avg_resolution_hours", 0),
                    "high_priority_tickets": row.get("high_priority_tickets", 0),
                },
                "sales_metrics": {
                    "total_deals": row.get("deal_amount_count", 0),
                    "total_revenue": row.get("deal_amount_sum", 0),
                    "avg_deal_size": row.get("deal_amount_mean", 0),
                    "mrr_impact": row.get("mrr_impact_sum", 0),
                },
            }
            customers.append(customer)

        return {
            "customers": customers,
            "total": len(customers),
            "last_updated": datetime.now().isoformat(),
        }


class AlertDataLoader(BaseLoader):
    """Loader for alert data based on health scores."""

    def load(self, data: Dict, filename: str = "alerts.json") -> bool:
        """
        Generate and load alert data based on health scores.

        Args:
            data: Health score data
            filename: Output filename

        Returns:
            True if successful, False otherwise
        """
        # Generate alerts from health score data
        alerts = self._generate_alerts(data)

        alert_data = {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a["severity"] == "critical"]),
            "generated_at": datetime.now().isoformat(),
        }

        return self.save_json(alert_data, filename)

    def _generate_alerts(self, data: Dict) -> List[Dict]:
        """Generate alerts based on health score data."""
        integrated_df = data.get("integrated_data")

        if integrated_df is None or integrated_df.empty:
            return []

        alerts = []
        current_time = datetime.now().isoformat()

        for _, row in integrated_df.iterrows():
            health_score = row.get("calculated_health_score", 0)
            customer_id = row["customer_id"]
            customer_name = row["company_name"]

            # Critical churn risk alert
            if health_score < 0.3:
                alerts.append(
                    {
                        "id": f"ALERT_{customer_id}_{int(datetime.now().timestamp())}",
                        "customer_id": customer_id,
                        "customer_name": customer_name,
                        "type": "churn_risk",
                        "severity": "critical",
                        "message": f"{customer_name} has critical health score ({health_score:.1%}) - immediate action required",
                        "health_score": health_score,
                        "actions": [
                            "Schedule immediate customer success call",
                            "Review account health metrics",
                            "Implement retention strategy",
                        ],
                        "created_at": current_time,
                    }
                )

            # Medium risk alert
            elif health_score < 0.7:
                alerts.append(
                    {
                        "id": f"ALERT_{customer_id}_{int(datetime.now().timestamp())}",
                        "customer_id": customer_id,
                        "customer_name": customer_name,
                        "type": "health_decline",
                        "severity": "medium",
                        "message": f"{customer_name} shows declining health score ({health_score:.1%}) - monitor closely",
                        "health_score": health_score,
                        "actions": [
                            "Monitor usage patterns",
                            "Check for support issues",
                            "Consider proactive outreach",
                        ],
                        "created_at": current_time,
                    }
                )

            # Support alerts
            total_tickets = row.get("total_tickets", 0)
            if total_tickets > 10:
                alerts.append(
                    {
                        "id": f"ALERT_{customer_id}_SUPPORT_{int(datetime.now().timestamp())}",
                        "customer_id": customer_id,
                        "customer_name": customer_name,
                        "type": "support_volume",
                        "severity": "medium",
                        "message": f"{customer_name} has high support ticket volume ({total_tickets} tickets)",
                        "ticket_count": total_tickets,
                        "actions": [
                            "Review support ticket patterns",
                            "Identify recurring issues",
                            "Consider additional training",
                        ],
                        "created_at": current_time,
                    }
                )

        return alerts


class DataExportLoader(BaseLoader):
    """Loader for various data export formats."""

    def export_csv_files(self, data: Dict) -> bool:
        """Export all data as CSV files for analysis."""
        success = True

        # Export integrated customer data
        integrated_df = data.get("integrated_data")
        if integrated_df is not None:
            success &= self.save_csv(integrated_df, "integrated_customers.csv")

        # Export health scores only
        if integrated_df is not None:
            health_scores_df = integrated_df[
                [
                    "customer_id",
                    "company_name",
                    "calculated_health_score",
                    "health_category",
                    "risk_level",
                    "usage_factor",
                    "engagement_factor",
                    "support_factor",
                    "payment_factor",
                    "adoption_factor",
                    "satisfaction_factor",
                    "lifecycle_factor",
                    "value_factor",
                ]
            ].copy()
            success &= self.save_csv(health_scores_df, "health_scores.csv")

        return success

    def load(self, data: Dict, filename: str = "data_export.json") -> bool:
        """
        Load comprehensive data export.

        Args:
            data: All ETL data
            filename: Output filename

        Returns:
            True if successful, False otherwise
        """
        export_data = {
            "export_type": "comprehensive",
            "exported_at": datetime.now().isoformat(),
            "data": self._make_serializable(data),
        }

        return self.save_json(export_data, filename)
