import statistics
from collections import Counter, defaultdict
from typing import List


class AnalyticsEngine:
    """
    Comprehensive analytics engine for customer success optimization
    """

    def __init__(self):
        self.alert_analytics = {}
        self.csm_analytics = {}
        self.customer_analytics = {}
        self.performance_history = defaultdict(list)
        self.prediction_models = {}

    def analyze_alert_patterns(self, alerts_data: List[dict]) -> dict:
        """Analyze alert patterns and trends"""
        if not alerts_data:
            return {"error": "No alerts data provided"}

        # Alert type distribution
        alert_types = Counter(alert.get("type", "unknown") for alert in alerts_data)

        # Severity distribution
        severity_dist = Counter(
            alert.get("severity", "unknown") for alert in alerts_data
        )

        # Customer segment analysis
        customer_segments = Counter()
        industry_analysis = Counter()
        mrr_ranges = {"0-5K": 0, "5K-10K": 0, "10K-20K": 0, "20K+": 0}

        total_potential_revenue_at_risk = 0
        critical_alerts_by_industry = defaultdict(int)

        for alert in alerts_data:
            customer_profile = alert.get("context", {}).get("customer_profile", {})
            customer_type = customer_profile.get("type", "unknown")
            industry = customer_profile.get("industry", "unknown")
            mrr = customer_profile.get("mrr", 0)

            customer_segments[customer_type] += 1
            industry_analysis[industry] += 1

            # MRR range analysis
            if mrr < 5000:
                mrr_ranges["0-5K"] += 1
            elif mrr < 10000:
                mrr_ranges["5K-10K"] += 1
            elif mrr < 20000:
                mrr_ranges["10K-20K"] += 1
            else:
                mrr_ranges["20K+"] += 1

            # Revenue at risk calculation
            if alert.get("severity") in ["critical", "high"]:
                total_potential_revenue_at_risk += mrr

            # Critical alerts by industry
            if alert.get("severity") == "critical":
                critical_alerts_by_industry[industry] += 1

        # Calculate alert velocity (alerts per day trend)
        alert_velocity = self._calculate_alert_velocity(alerts_data)

        # Risk assessment
        risk_assessment = self._assess_portfolio_risk(alerts_data)

        return {
            "alert_patterns": {
                "total_alerts": len(alerts_data),
                "alert_types": dict(alert_types.most_common()),
                "severity_distribution": dict(severity_dist),
                "top_alert_type": alert_types.most_common(1)[0]
                if alert_types
                else None,
            },
            "customer_insights": {
                "segment_distribution": dict(customer_segments),
                "industry_analysis": dict(industry_analysis.most_common()),
                "mrr_range_distribution": mrr_ranges,
                "highest_risk_industry": critical_alerts_by_industry.most_common(1)[0]
                if critical_alerts_by_industry
                else None,
            },
            "business_impact": {
                "total_revenue_at_risk": total_potential_revenue_at_risk,
                "average_revenue_per_alert": total_potential_revenue_at_risk
                / len(alerts_data)
                if alerts_data
                else 0,
                "critical_alert_percentage": (
                    severity_dist["critical"] / len(alerts_data)
                )
                * 100
                if alerts_data
                else 0,
            },
            "trends": {
                "alert_velocity": alert_velocity,
                "risk_assessment": risk_assessment,
            },
        }

    def analyze_csm_performance(
        self, csm_data: dict, assignment_history: dict = None
    ) -> dict:
        """Analyze CSM team performance and optimization opportunities"""

        performance_metrics = {}
        workload_analysis = {}
        skill_gaps = []
        optimization_opportunities = []

        # Individual CSM analysis
        for csm_id, csm in csm_data.items():
            metrics = csm["performance_metrics"]

            # Performance score calculation
            performance_score = (
                metrics["success_rate"] * 0.4
                + (1 - metrics["escalation_rate"]) * 0.3
                + (metrics["customer_satisfaction"] / 5.0) * 0.2
                + (1 - min(metrics["avg_resolution_time_hours"] / 24, 1)) * 0.1
            )

            # Workload efficiency
            utilization = csm["current_workload"] / csm["max_concurrent_alerts"]
            efficiency_score = metrics["success_rate"] / max(
                utilization, 0.1
            )  # Avoid division by zero

            performance_metrics[csm_id] = {
                "name": csm["name"],
                "level": csm["level"],
                "performance_score": round(performance_score, 3),
                "efficiency_score": round(efficiency_score, 3),
                "utilization": round(utilization, 2),
                "specialties": csm["specialties"],
                "metrics": metrics,
            }

            # Identify optimization opportunities
            if utilization < 0.4:
                optimization_opportunities.append(
                    {
                        "type": "underutilization",
                        "csm": csm["name"],
                        "message": f"{csm['name']} is underutilized ({utilization:.1%}) - can handle more complex cases",
                        "priority": "medium",
                    }
                )
            elif utilization > 0.9:
                optimization_opportunities.append(
                    {
                        "type": "overutilization",
                        "csm": csm["name"],
                        "message": f"{csm['name']} is overloaded ({utilization:.1%}) - risk of burnout",
                        "priority": "high",
                    }
                )

            # Skill gap analysis
            if metrics["success_rate"] < 0.75:
                skill_gaps.append(
                    {
                        "csm": csm["name"],
                        "area": "general_resolution",
                        "current_rate": metrics["success_rate"],
                        "target_rate": 0.85,
                        "improvement_needed": 0.85 - metrics["success_rate"],
                    }
                )

            if metrics["escalation_rate"] > 0.15:
                skill_gaps.append(
                    {
                        "csm": csm["name"],
                        "area": "escalation_management",
                        "current_rate": metrics["escalation_rate"],
                        "target_rate": 0.10,
                        "improvement_needed": metrics["escalation_rate"] - 0.10,
                    }
                )

        # Team-level insights
        team_performance = self._calculate_team_performance(performance_metrics)

        return {
            "individual_performance": performance_metrics,
            "team_insights": team_performance,
            "skill_gaps": skill_gaps,
            "optimization_opportunities": optimization_opportunities,
            "recommendations": self._generate_csm_recommendations(
                performance_metrics, skill_gaps
            ),
        }

    def predict_customer_risks(self, customers_data: List[dict]) -> dict:
        """Predict customer risks and expansion opportunities"""

        risk_predictions = []
        expansion_opportunities = []
        churn_risk_factors = {}

        for customer in customers_data:
            risk_score = self._calculate_customer_risk_score(customer)
            expansion_score = self._calculate_expansion_score(customer)

            # Risk prediction
            if risk_score >= 0.7:
                risk_level = "high"
                action_urgency = "immediate"
            elif risk_score >= 0.5:
                risk_level = "medium"
                action_urgency = "within_week"
            else:
                risk_level = "low"
                action_urgency = "monitor"

            risk_predictions.append(
                {
                    "customer_id": customer["id"],
                    "customer_name": customer["name"],
                    "risk_score": round(risk_score, 3),
                    "risk_level": risk_level,
                    "action_urgency": action_urgency,
                    "key_risk_factors": self._identify_risk_factors(customer),
                    "recommended_actions": self._recommend_risk_mitigation(
                        customer, risk_score
                    ),
                }
            )

            # Expansion opportunities
            if expansion_score >= 0.6:
                expansion_opportunities.append(
                    {
                        "customer_id": customer["id"],
                        "customer_name": customer["name"],
                        "expansion_score": round(expansion_score, 3),
                        "opportunity_type": self._identify_expansion_type(customer),
                        "estimated_revenue_potential": self._estimate_expansion_revenue(
                            customer
                        ),
                        "success_probability": self._calculate_expansion_probability(
                            customer
                        ),
                    }
                )

        # Portfolio-level insights
        portfolio_health = self._analyze_portfolio_health(
            risk_predictions, expansion_opportunities
        )

        return {
            "risk_predictions": sorted(
                risk_predictions, key=lambda x: x["risk_score"], reverse=True
            ),
            "expansion_opportunities": sorted(
                expansion_opportunities,
                key=lambda x: x["expansion_score"],
                reverse=True,
            ),
            "portfolio_insights": portfolio_health,
            "summary": {
                "high_risk_customers": len(
                    [r for r in risk_predictions if r["risk_level"] == "high"]
                ),
                "expansion_ready_customers": len(expansion_opportunities),
                "total_expansion_potential": sum(
                    opp.get("estimated_revenue_potential", 0)
                    for opp in expansion_opportunities
                ),
            },
        }

    def generate_optimization_recommendations(
        self, alert_patterns: dict, csm_performance: dict, customer_risks: dict
    ) -> dict:
        """Generate comprehensive optimization recommendations"""

        recommendations = {
            "immediate_actions": [],
            "strategic_improvements": [],
            "resource_optimization": [],
            "process_enhancements": [],
        }

        # Immediate actions based on critical issues
        if (
            alert_patterns.get("business_impact", {}).get(
                "critical_alert_percentage", 0
            )
            > 20
        ):
            recommendations["immediate_actions"].append(
                {
                    "priority": "critical",
                    "category": "alert_management",
                    "action": "Implement emergency response protocol",
                    "reason": f"Critical alerts at {alert_patterns['business_impact']['critical_alert_percentage']:.1f}% - above 20% threshold",
                    "estimated_impact": "Reduce critical alert response time by 50%",
                }
            )

        # Strategic improvements based on patterns
        top_alert_type = alert_patterns.get("alert_patterns", {}).get("top_alert_type")
        if top_alert_type:
            recommendations["strategic_improvements"].append(
                {
                    "priority": "high",
                    "category": "prevention",
                    "action": f"Develop proactive monitoring for {top_alert_type[0]}",
                    "reason": f"{top_alert_type[0]} represents {top_alert_type[1]} alerts - highest volume",
                    "estimated_impact": f"Prevent 30-40% of {top_alert_type[0]} alerts",
                }
            )

        # Resource optimization based on CSM performance
        overutilized_csms = [
            opp
            for opp in csm_performance.get("optimization_opportunities", [])
            if opp["type"] == "overutilization"
        ]
        if overutilized_csms:
            recommendations["resource_optimization"].append(
                {
                    "priority": "high",
                    "category": "workload_balancing",
                    "action": "Redistribute workload from overloaded CSMs",
                    "reason": f"{len(overutilized_csms)} CSMs are overutilized",
                    "estimated_impact": "Improve team efficiency by 15-20%",
                }
            )

        # Process enhancements based on skill gaps
        skill_gaps = csm_performance.get("skill_gaps", [])
        if skill_gaps:
            common_gaps = Counter(gap["area"] for gap in skill_gaps)
            most_common_gap = common_gaps.most_common(1)[0] if common_gaps else None

            if most_common_gap:
                recommendations["process_enhancements"].append(
                    {
                        "priority": "medium",
                        "category": "training",
                        "action": f"Implement {most_common_gap[0]} training program",
                        "reason": f"{most_common_gap[1]} CSMs need improvement in {most_common_gap[0]}",
                        "estimated_impact": "Increase team success rate by 10-15%",
                    }
                )

        # Calculate ROI estimates
        roi_estimates = self._calculate_optimization_roi(
            recommendations, alert_patterns, customer_risks
        )

        return {
            "recommendations": recommendations,
            "roi_estimates": roi_estimates,
            "implementation_priority": self._prioritize_recommendations(
                recommendations
            ),
            "success_metrics": self._define_success_metrics(recommendations),
        }

    def _calculate_alert_velocity(self, alerts_data: List[dict]) -> dict:
        """Calculate alert velocity trends"""
        # Simplified - in real implementation would use actual timestamps
        return {
            "alerts_per_day": len(alerts_data) / 7,  # Assuming weekly data
            "trend": "stable",  # Would calculate actual trend
            "peak_hours": "9-11 AM, 2-4 PM",  # Simplified
        }

    def _assess_portfolio_risk(self, alerts_data: List[dict]) -> dict:
        """Assess overall portfolio risk"""
        critical_count = sum(
            1 for alert in alerts_data if alert.get("severity") == "critical"
        )
        risk_level = (
            "high"
            if critical_count > len(alerts_data) * 0.2
            else "medium"
            if critical_count > len(alerts_data) * 0.1
            else "low"
        )

        return {
            "overall_risk_level": risk_level,
            "critical_alerts": critical_count,
            "risk_score": min(critical_count / max(len(alerts_data) * 0.1, 1), 1.0),
        }

    def _calculate_customer_risk_score(self, customer: dict) -> float:
        """Calculate customer churn risk score"""
        score = 0.0

        # Health score factor (40% weight)
        health_score = customer.get("health_score", 0.5)
        score += (1 - health_score) * 0.4

        # Usage trends (30% weight)
        usage_score = customer.get("usage_score", 0.5)
        score += (1 - usage_score) * 0.3

        # Support burden (20% weight)
        support_tickets = customer.get("support_tickets", 0)
        support_score = min(support_tickets / 10, 1.0)  # Normalize to 0-1
        score += support_score * 0.2

        # Payment status (10% weight)
        payment_status = customer.get("payment_status", "current")
        payment_score = 1.0 if payment_status in ["late", "overdue"] else 0.0
        score += payment_score * 0.1

        return min(score, 1.0)

    def _calculate_expansion_score(self, customer: dict) -> float:
        """Calculate customer expansion opportunity score"""
        score = 0.0

        # Health score (40% weight)
        health_score = customer.get("health_score", 0.5)
        score += health_score * 0.4

        # Engagement level (30% weight)
        engagement_score = customer.get("engagement_score", 0.5)
        score += engagement_score * 0.3

        # NPS score (20% weight)
        nps_score = customer.get("nps_score", 5)
        nps_normalized = (nps_score - 1) / 9  # Convert 1-10 to 0-1
        score += nps_normalized * 0.2

        # Growth indicators (10% weight)
        # Simplified - would include actual growth metrics
        score += 0.5 * 0.1

        return min(score, 1.0)

    def _identify_risk_factors(self, customer: dict) -> List[str]:
        """Identify key risk factors for a customer"""
        factors = []

        if customer.get("health_score", 1.0) < 0.3:
            factors.append("Low health score")
        if customer.get("last_login_days", 0) > 14:
            factors.append("Extended inactivity")
        if customer.get("support_tickets", 0) > 5:
            factors.append("High support burden")
        if customer.get("payment_status") in ["late", "overdue"]:
            factors.append("Payment issues")

        return factors

    def _recommend_risk_mitigation(
        self, customer: dict, risk_score: float
    ) -> List[str]:
        """Recommend risk mitigation actions"""
        actions = []

        if risk_score >= 0.7:
            actions.extend(
                ["Immediate CSM outreach", "Executive escalation", "Emergency support"]
            )
        elif risk_score >= 0.5:
            actions.extend(
                [
                    "Schedule health check call",
                    "Review usage patterns",
                    "Proactive support",
                ]
            )
        else:
            actions.extend(["Regular check-in", "Monitor trends"])

        return actions

    def _identify_expansion_type(self, customer: dict) -> str:
        """Identify type of expansion opportunity"""
        mrr = customer.get("mrr", 0)
        health_score = customer.get("health_score", 0.5)

        if health_score > 0.8 and mrr > 10000:
            return "Premium upgrade"
        elif health_score > 0.7:
            return "Feature expansion"
        else:
            return "Usage optimization"

    def _estimate_expansion_revenue(self, customer: dict) -> float:
        """Estimate potential expansion revenue"""
        current_mrr = customer.get("mrr", 0)
        expansion_multiplier = 1.5 if customer.get("health_score", 0) > 0.8 else 1.2
        return current_mrr * expansion_multiplier * 12  # Annual estimate

    def _calculate_expansion_probability(self, customer: dict) -> float:
        """Calculate probability of successful expansion"""
        health_score = customer.get("health_score", 0.5)
        nps_score = customer.get("nps_score", 5)

        base_probability = health_score * 0.7 + (nps_score / 10) * 0.3
        return min(base_probability, 0.95)  # Cap at 95%

    def _calculate_team_performance(self, performance_metrics: dict) -> dict:
        """Calculate team-level performance insights"""
        if not performance_metrics:
            return {}

        scores = [pm["performance_score"] for pm in performance_metrics.values()]
        efficiency_scores = [
            pm["efficiency_score"] for pm in performance_metrics.values()
        ]

        return {
            "average_performance": round(statistics.mean(scores), 3),
            "performance_std_dev": round(
                statistics.stdev(scores) if len(scores) > 1 else 0, 3
            ),
            "average_efficiency": round(statistics.mean(efficiency_scores), 3),
            "top_performer": max(
                performance_metrics.items(), key=lambda x: x[1]["performance_score"]
            )[1]["name"],
            "improvement_opportunity": min(
                performance_metrics.items(), key=lambda x: x[1]["performance_score"]
            )[1]["name"],
        }

    def _generate_csm_recommendations(
        self, performance_metrics: dict, skill_gaps: List[dict]
    ) -> List[dict]:
        """Generate specific CSM improvement recommendations"""
        recommendations = []

        # Training recommendations
        gap_areas = Counter(gap["area"] for gap in skill_gaps)
        for area, count in gap_areas.items():
            recommendations.append(
                {
                    "type": "training",
                    "area": area,
                    "affected_csms": count,
                    "priority": "high"
                    if count > len(performance_metrics) * 0.3
                    else "medium",
                }
            )

        return recommendations

    def _calculate_optimization_roi(
        self, recommendations: dict, alert_patterns: dict, customer_risks: dict
    ) -> dict:
        """Calculate ROI estimates for optimization recommendations"""
        # Simplified ROI calculation
        total_revenue_at_risk = alert_patterns.get("business_impact", {}).get(
            "total_revenue_at_risk", 0
        )

        return {
            "estimated_savings": total_revenue_at_risk
            * 0.15,  # 15% improvement assumption
            "implementation_cost": 50000,  # Simplified estimate
            "payback_period_months": 6,
            "annual_roi_percentage": 180,
        }

    def _prioritize_recommendations(self, recommendations: dict) -> List[dict]:
        """Prioritize recommendations by impact and urgency"""
        all_recs = []
        for category, recs in recommendations.items():
            for rec in recs:
                rec["category"] = category
                all_recs.append(rec)

        # Sort by priority (critical > high > medium > low)
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        return sorted(
            all_recs, key=lambda x: priority_order.get(x.get("priority", "low"), 3)
        )

    def _define_success_metrics(self, recommendations: dict) -> dict:
        """Define success metrics for tracking optimization progress"""
        return {
            "alert_reduction": "Reduce critical alerts by 25%",
            "response_time": "Improve average response time by 30%",
            "customer_satisfaction": "Increase CSM satisfaction scores by 15%",
            "team_efficiency": "Improve team utilization balance to 70-80% range",
        }

    def _analyze_portfolio_health(
        self, risk_predictions: List[dict], expansion_opportunities: List[dict]
    ) -> dict:
        """Analyze overall portfolio health and trends"""
        total_customers = len(risk_predictions)
        high_risk_count = len(
            [r for r in risk_predictions if r["risk_level"] == "high"]
        )
        medium_risk_count = len(
            [r for r in risk_predictions if r["risk_level"] == "medium"]
        )

        # Calculate portfolio risk score
        portfolio_risk_score = (
            (high_risk_count * 1.0 + medium_risk_count * 0.5) / total_customers
            if total_customers > 0
            else 0
        )

        # Health categorization
        if portfolio_risk_score < 0.1:
            portfolio_health_status = "excellent"
        elif portfolio_risk_score < 0.25:
            portfolio_health_status = "good"
        elif portfolio_risk_score < 0.5:
            portfolio_health_status = "moderate_risk"
        else:
            portfolio_health_status = "high_risk"

        return {
            "portfolio_health_status": portfolio_health_status,
            "portfolio_risk_score": round(portfolio_risk_score, 3),
            "risk_distribution": {
                "high_risk": high_risk_count,
                "medium_risk": medium_risk_count,
                "low_risk": total_customers - high_risk_count - medium_risk_count,
            },
            "expansion_potential": {
                "ready_for_expansion": len(expansion_opportunities),
                "expansion_percentage": round(
                    (len(expansion_opportunities) / total_customers) * 100, 1
                )
                if total_customers > 0
                else 0,
            },
        }
