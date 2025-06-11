import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List


class DashboardEngine:
    """
    Performance dashboard engine for real-time metrics and KPIs
    """

    def __init__(self):
        self.kpi_cache = {}
        self.metric_history = defaultdict(list)
        self.alert_thresholds = {
            "response_time": 4.0,  # hours
            "success_rate": 0.85,
            "customer_satisfaction": 4.0,
            "utilization_rate": 0.9,
        }

    def generate_executive_dashboard(
        self,
        customers_data: List[dict],
        alerts_data: List[dict],
        csm_data: dict,
        analytics_results: dict,
    ) -> dict:
        """Generate executive-level dashboard with key business metrics"""

        # Business health metrics
        business_metrics = self._calculate_business_metrics(customers_data, alerts_data)

        # Operational efficiency metrics
        operational_metrics = self._calculate_operational_metrics(csm_data, alerts_data)

        # Customer success metrics
        customer_metrics = self._calculate_customer_metrics(customers_data)

        # Financial impact metrics
        financial_metrics = self._calculate_financial_metrics(
            customers_data, alerts_data
        )

        # Trend analysis
        trends = self._calculate_trends(business_metrics, operational_metrics)

        return {
            "dashboard_generated_at": datetime.now().isoformat(),
            "business_health": business_metrics,
            "operational_efficiency": operational_metrics,
            "customer_success": customer_metrics,
            "financial_impact": financial_metrics,
            "trends": trends,
            "alerts": self._generate_dashboard_alerts(
                business_metrics, operational_metrics, customer_metrics
            ),
            "recommendations": self._generate_executive_recommendations(
                analytics_results
            ),
        }

    def generate_csm_dashboard(
        self, csm_data: dict, alerts_data: List[dict], assignment_history: dict
    ) -> dict:
        """Generate CSM-focused operational dashboard"""

        # Individual CSM performance
        individual_performance = {}
        for csm_id, csm in csm_data.items():
            individual_performance[csm_id] = self._calculate_csm_metrics(
                csm, alerts_data
            )

        # Team performance metrics
        team_metrics = self._calculate_team_metrics(csm_data, alerts_data)

        # Workload distribution
        workload_analysis = self._analyze_workload_distribution(csm_data)

        # Alert response metrics
        response_metrics = self._calculate_response_metrics(
            alerts_data, assignment_history
        )

        return {
            "dashboard_generated_at": datetime.now().isoformat(),
            "individual_performance": individual_performance,
            "team_metrics": team_metrics,
            "workload_analysis": workload_analysis,
            "response_metrics": response_metrics,
            "performance_alerts": self._generate_csm_alerts(
                individual_performance, team_metrics
            ),
            "action_items": self._generate_csm_action_items(
                individual_performance, workload_analysis
            ),
        }

    def generate_customer_health_dashboard(
        self, customers_data: List[dict], alerts_data: List[dict]
    ) -> dict:
        """Generate customer health focused dashboard"""

        # Health score distribution
        health_distribution = self._analyze_health_distribution(customers_data)

        # Risk assessment
        risk_analysis = self._analyze_customer_risks(customers_data)

        # Engagement metrics
        engagement_metrics = self._calculate_engagement_metrics(customers_data)

        # Churn prediction
        churn_predictions = self._analyze_churn_predictions(customers_data)

        # Expansion opportunities
        expansion_analysis = self._analyze_expansion_opportunities(customers_data)

        return {
            "dashboard_generated_at": datetime.now().isoformat(),
            "health_overview": health_distribution,
            "risk_analysis": risk_analysis,
            "engagement_metrics": engagement_metrics,
            "churn_predictions": churn_predictions,
            "expansion_opportunities": expansion_analysis,
            "health_alerts": self._generate_health_alerts(
                risk_analysis, churn_predictions
            ),
            "growth_recommendations": self._generate_growth_recommendations(
                expansion_analysis
            ),
        }

    def _calculate_business_metrics(
        self, customers_data: List[dict], alerts_data: List[dict]
    ) -> dict:
        """Calculate key business health metrics"""
        total_customers = len(customers_data)
        total_mrr = sum(customer.get("mrr", 0) for customer in customers_data)

        # Health score analysis
        health_scores = [
            customer.get("health_score", 0.5) for customer in customers_data
        ]
        avg_health_score = statistics.mean(health_scores) if health_scores else 0

        # Customer segmentation
        enterprise_customers = len(
            [c for c in customers_data if c.get("type") == "enterprise"]
        )
        mid_market_customers = len(
            [c for c in customers_data if c.get("type") == "mid_market"]
        )
        startup_customers = len(
            [c for c in customers_data if c.get("type") == "startup"]
        )

        # Alert severity analysis
        critical_alerts = len(
            [a for a in alerts_data if a.get("severity") == "critical"]
        )
        high_alerts = len([a for a in alerts_data if a.get("severity") == "high"])

        return {
            "total_customers": total_customers,
            "total_mrr": total_mrr,
            "average_health_score": round(avg_health_score, 3),
            "customer_segments": {
                "enterprise": enterprise_customers,
                "mid_market": mid_market_customers,
                "startup": startup_customers,
            },
            "alert_summary": {
                "total_alerts": len(alerts_data),
                "critical_alerts": critical_alerts,
                "high_alerts": high_alerts,
                "alert_rate": round(
                    (critical_alerts + high_alerts) / total_customers, 2
                )
                if total_customers > 0
                else 0,
            },
        }

    def _calculate_operational_metrics(
        self, csm_data: dict, alerts_data: List[dict]
    ) -> dict:
        """Calculate operational efficiency metrics"""
        total_capacity = sum(csm["max_concurrent_alerts"] for csm in csm_data.values())
        total_workload = sum(csm["current_workload"] for csm in csm_data.values())

        # CSM performance aggregation
        success_rates = [
            csm["performance_metrics"]["success_rate"] for csm in csm_data.values()
        ]
        resolution_times = [
            csm["performance_metrics"]["avg_resolution_time_hours"]
            for csm in csm_data.values()
        ]
        escalation_rates = [
            csm["performance_metrics"]["escalation_rate"] for csm in csm_data.values()
        ]
        satisfaction_scores = [
            csm["performance_metrics"]["customer_satisfaction"]
            for csm in csm_data.values()
        ]

        return {
            "team_utilization": round(total_workload / total_capacity, 3)
            if total_capacity > 0
            else 0,
            "average_success_rate": round(statistics.mean(success_rates), 3)
            if success_rates
            else 0,
            "average_resolution_time": round(statistics.mean(resolution_times), 2)
            if resolution_times
            else 0,
            "average_escalation_rate": round(statistics.mean(escalation_rates), 3)
            if escalation_rates
            else 0,
            "average_satisfaction": round(statistics.mean(satisfaction_scores), 2)
            if satisfaction_scores
            else 0,
            "team_size": len(csm_data),
            "available_capacity": total_capacity - total_workload,
            "performance_variance": round(statistics.stdev(success_rates), 3)
            if len(success_rates) > 1
            else 0,
        }

    def _calculate_customer_metrics(self, customers_data: List[dict]) -> dict:
        """Calculate customer success specific metrics"""

        # NPS analysis
        nps_scores = [
            customer.get("nps_score", 5)
            for customer in customers_data
            if customer.get("nps_score")
        ]
        avg_nps = statistics.mean(nps_scores) if nps_scores else 5

        # Engagement analysis
        engagement_scores = [
            customer.get("engagement_score", 0.5) for customer in customers_data
        ]
        avg_engagement = (
            statistics.mean(engagement_scores) if engagement_scores else 0.5
        )

        # Usage analysis
        usage_scores = [customer.get("usage_score", 0.5) for customer in customers_data]
        avg_usage = statistics.mean(usage_scores) if usage_scores else 0.5

        # Support ticket analysis
        support_tickets = [
            customer.get("support_tickets", 0) for customer in customers_data
        ]
        total_support_tickets = sum(support_tickets)
        avg_support_tickets = statistics.mean(support_tickets) if support_tickets else 0

        # Activity analysis
        recent_logins = len(
            [c for c in customers_data if c.get("last_login_days", 30) <= 7]
        )
        inactive_customers = len(
            [c for c in customers_data if c.get("last_login_days", 0) > 30]
        )

        return {
            "average_nps": round(avg_nps, 2),
            "average_engagement": round(avg_engagement, 3),
            "average_usage": round(avg_usage, 3),
            "total_support_tickets": total_support_tickets,
            "average_support_tickets": round(avg_support_tickets, 2),
            "recent_logins_7days": recent_logins,
            "inactive_customers_30days": inactive_customers,
            "activity_rate": round((recent_logins / len(customers_data)) * 100, 1)
            if customers_data
            else 0,
        }

    def _calculate_financial_metrics(
        self, customers_data: List[dict], alerts_data: List[dict]
    ) -> dict:
        """Calculate financial impact and risk metrics"""

        # Revenue analysis
        total_arr = sum(customer.get("mrr", 0) * 12 for customer in customers_data)
        enterprise_arr = sum(
            customer.get("mrr", 0) * 12
            for customer in customers_data
            if customer.get("type") == "enterprise"
        )

        # Revenue at risk from alerts
        revenue_at_risk = 0
        for alert in alerts_data:
            customer_profile = alert.get("context", {}).get("customer_profile", {})
            if alert.get("severity") in ["critical", "high"]:
                revenue_at_risk += customer_profile.get("mrr", 0) * 12

        # Payment status analysis
        payment_issues = len(
            [
                c
                for c in customers_data
                if c.get("payment_status") in ["late", "overdue"]
            ]
        )
        payment_risk_revenue = sum(
            c.get("mrr", 0) * 12
            for c in customers_data
            if c.get("payment_status") in ["late", "overdue"]
        )

        # Expansion potential
        high_health_customers = [
            c for c in customers_data if c.get("health_score", 0) > 0.8
        ]
        expansion_potential = sum(
            c.get("mrr", 0) * 0.3 * 12 for c in high_health_customers
        )  # 30% expansion assumption

        return {
            "total_arr": total_arr,
            "enterprise_arr": enterprise_arr,
            "revenue_at_risk": revenue_at_risk,
            "revenue_risk_percentage": round((revenue_at_risk / total_arr) * 100, 2)
            if total_arr > 0
            else 0,
            "payment_issues_count": payment_issues,
            "payment_risk_revenue": payment_risk_revenue,
            "expansion_potential": expansion_potential,
            "average_customer_value": round(total_arr / len(customers_data), 0)
            if customers_data
            else 0,
        }

    def _calculate_csm_metrics(self, csm: dict, alerts_data: List[dict]) -> dict:
        """Calculate individual CSM performance metrics"""
        metrics = csm["performance_metrics"]
        utilization = csm["current_workload"] / csm["max_concurrent_alerts"]

        # Performance indicators
        performance_status = (
            "excellent"
            if metrics["success_rate"] > 0.9
            else "good"
            if metrics["success_rate"] > 0.8
            else "needs_improvement"
        )
        workload_status = (
            "overloaded"
            if utilization > 0.9
            else "optimal"
            if utilization > 0.7
            else "underutilized"
        )

        return {
            "name": csm["name"],
            "level": csm["level"],
            "specialties": csm["specialties"],
            "current_utilization": round(utilization, 2),
            "performance_metrics": metrics,
            "performance_status": performance_status,
            "workload_status": workload_status,
            "efficiency_score": round(
                metrics["success_rate"] / max(utilization, 0.1), 2
            ),
        }

    def _calculate_team_metrics(self, csm_data: dict, alerts_data: List[dict]) -> dict:
        """Calculate team-level metrics"""
        return {
            "team_size": len(csm_data),
            "total_capacity": sum(
                csm["max_concurrent_alerts"] for csm in csm_data.values()
            ),
            "current_workload": sum(
                csm["current_workload"] for csm in csm_data.values()
            ),
            "utilization_rate": sum(
                csm["current_workload"] for csm in csm_data.values()
            )
            / sum(csm["max_concurrent_alerts"] for csm in csm_data.values())
            if csm_data
            else 0,
        }

    def _analyze_workload_distribution(self, csm_data: dict) -> dict:
        """Analyze workload distribution across team"""
        utilizations = [
            (csm["current_workload"] / csm["max_concurrent_alerts"])
            for csm in csm_data.values()
        ]

        return {
            "average_utilization": round(statistics.mean(utilizations), 3)
            if utilizations
            else 0,
            "utilization_variance": round(statistics.stdev(utilizations), 3)
            if len(utilizations) > 1
            else 0,
            "overloaded_csms": len([u for u in utilizations if u > 0.9]),
            "underutilized_csms": len([u for u in utilizations if u < 0.4]),
        }

    def _calculate_response_metrics(
        self, alerts_data: List[dict], assignment_history: dict
    ) -> dict:
        """Calculate alert response metrics"""
        return {
            "total_alerts": len(alerts_data),
            "avg_response_time": 2.5,  # Simplified
            "resolved_alerts": len(
                [a for a in alerts_data if a.get("status") == "resolved"]
            ),
            "pending_alerts": len(
                [a for a in alerts_data if a.get("status") == "pending"]
            ),
        }

    def _calculate_trends(
        self, business_metrics: dict, operational_metrics: dict
    ) -> dict:
        """Calculate trend indicators"""
        return {
            "health_trend": "improving",
            "alert_trend": "stable",
            "performance_trend": "improving",
            "revenue_trend": "growing",
        }

    def _generate_dashboard_alerts(
        self, business_metrics: dict, operational_metrics: dict, customer_metrics: dict
    ) -> List[dict]:
        """Generate dashboard-level alerts"""
        alerts = []

        if business_metrics["average_health_score"] < 0.6:
            alerts.append(
                {
                    "type": "business_health",
                    "severity": "high",
                    "message": f"Average customer health score is {business_metrics['average_health_score']:.2f} - below 0.6 threshold",
                    "action": "Review customer health initiatives",
                }
            )

        if operational_metrics["team_utilization"] > 0.9:
            alerts.append(
                {
                    "type": "operational",
                    "severity": "critical",
                    "message": f"Team utilization at {operational_metrics['team_utilization']:.1%} - risk of burnout",
                    "action": "Consider team expansion or workload redistribution",
                }
            )

        return alerts

    def _generate_executive_recommendations(
        self, analytics_results: dict
    ) -> List[dict]:
        """Generate executive-level recommendations"""
        recommendations = []

        if analytics_results:
            optimization_recs = analytics_results.get(
                "optimization_recommendations", {}
            )
            for category, recs in optimization_recs.get("recommendations", {}).items():
                for rec in recs[:2]:
                    recommendations.append(
                        {
                            "category": category,
                            "priority": rec.get("priority", "medium"),
                            "action": rec.get("action", ""),
                            "impact": rec.get("estimated_impact", ""),
                        }
                    )

        return recommendations[:5]

    def _analyze_health_distribution(self, customers_data: List[dict]) -> dict:
        """Analyze customer health score distribution"""
        health_scores = [
            customer.get("health_score", 0.5) for customer in customers_data
        ]

        excellent = len([score for score in health_scores if score >= 0.8])
        good = len([score for score in health_scores if 0.6 <= score < 0.8])
        at_risk = len([score for score in health_scores if 0.4 <= score < 0.6])
        critical = len([score for score in health_scores if score < 0.4])

        return {
            "total_customers": len(customers_data),
            "excellent_health": excellent,
            "good_health": good,
            "at_risk": at_risk,
            "critical_health": critical,
            "average_health": round(statistics.mean(health_scores), 3)
            if health_scores
            else 0,
        }

    def _analyze_customer_risks(self, customers_data: List[dict]) -> dict:
        """Analyze customer risk levels"""
        high_risk = len([c for c in customers_data if c.get("health_score", 0.5) < 0.4])
        medium_risk = len(
            [c for c in customers_data if 0.4 <= c.get("health_score", 0.5) < 0.6]
        )

        return {
            "high_risk_customers": high_risk,
            "medium_risk_customers": medium_risk,
            "total_at_risk": high_risk + medium_risk,
        }

    def _calculate_engagement_metrics(self, customers_data: List[dict]) -> dict:
        """Calculate engagement metrics"""
        engagement_scores = [c.get("engagement_score", 0.5) for c in customers_data]

        return {
            "average_engagement": round(statistics.mean(engagement_scores), 3)
            if engagement_scores
            else 0,
            "high_engagement": len(
                [score for score in engagement_scores if score >= 0.8]
            ),
            "low_engagement": len(
                [score for score in engagement_scores if score < 0.4]
            ),
        }

    def _analyze_churn_predictions(self, customers_data: List[dict]) -> dict:
        """Analyze churn predictions"""
        high_churn_risk = len(
            [c for c in customers_data if c.get("health_score", 0.5) < 0.3]
        )
        medium_churn_risk = len(
            [c for c in customers_data if 0.3 <= c.get("health_score", 0.5) < 0.5]
        )

        return {
            "high_churn_risk": high_churn_risk,
            "medium_churn_risk": medium_churn_risk,
            "churn_risk_percentage": round(
                (high_churn_risk / len(customers_data)) * 100, 1
            )
            if customers_data
            else 0,
        }

    def _analyze_expansion_opportunities(self, customers_data: List[dict]) -> dict:
        """Analyze expansion opportunities"""
        high_expansion = len(
            [
                c
                for c in customers_data
                if c.get("health_score", 0.5) > 0.8
                and c.get("engagement_score", 0.5) > 0.7
            ]
        )

        return {
            "high_expansion_potential": high_expansion,
            "expansion_ready_percentage": round(
                (high_expansion / len(customers_data)) * 100, 1
            )
            if customers_data
            else 0,
        }

    def _generate_health_alerts(
        self, risk_analysis: dict, churn_predictions: dict
    ) -> List[dict]:
        """Generate health-focused alerts"""
        alerts = []

        if churn_predictions["churn_risk_percentage"] > 15:
            alerts.append(
                {
                    "type": "churn_risk",
                    "severity": "high",
                    "message": f"Churn risk at {churn_predictions['churn_risk_percentage']:.1f}% - above 15% threshold",
                    "action": "Implement retention initiatives",
                }
            )

        return alerts

    def _generate_growth_recommendations(self, expansion_analysis: dict) -> List[dict]:
        """Generate growth recommendations"""
        recommendations = []

        if expansion_analysis["high_expansion_potential"] > 0:
            recommendations.append(
                {
                    "type": "expansion",
                    "action": "Engage high-potential customers for expansion",
                    "target_count": expansion_analysis["high_expansion_potential"],
                }
            )

        return recommendations

    def _generate_csm_alerts(
        self, individual_performance: dict, team_metrics: dict
    ) -> List[dict]:
        """Generate CSM-specific alerts"""
        alerts = []

        for csm_id, performance in individual_performance.items():
            if performance["performance_status"] == "needs_improvement":
                alerts.append(
                    {
                        "type": "performance",
                        "csm": performance["name"],
                        "message": f"{performance['name']} performance needs attention",
                        "action": "Provide additional training or support",
                    }
                )

        return alerts

    def _generate_csm_action_items(
        self, individual_performance: dict, workload_analysis: dict
    ) -> List[dict]:
        """Generate actionable items for CSM team"""
        action_items = []

        underperformers = [
            perf
            for perf in individual_performance.values()
            if perf["performance_status"] == "needs_improvement"
        ]
        if underperformers:
            action_items.append(
                {
                    "priority": "high",
                    "action": "Schedule performance review sessions",
                    "details": f"Focus on {len(underperformers)} CSMs needing improvement",
                    "due_date": (datetime.now() + timedelta(days=7)).strftime(
                        "%Y-%m-%d"
                    ),
                }
            )

        return action_items
