from datetime import datetime, timedelta
from typing import List, Tuple

from mock_data import ACTION_TEMPLATES


class AlertIntelligence:
    """
    Intelligent alert system with personalized thresholds and smart severity calculation
    """

    def __init__(self):
        self.alert_history = {}  # Track alert frequency to prevent spam
        self.action_effectiveness = {}  # Track which actions work for which customer types

    def get_personalized_thresholds(self, customer: dict) -> dict:
        """
        Get personalized alert thresholds based on customer characteristics
        """
        customer_type = customer.get("customer_type", "mid_market")
        industry = customer.get("industry", "technology")
        mrr = customer.get("mrr", 0)

        # Base thresholds
        base_thresholds = {
            "health_critical": 0.3,
            "health_warning": 0.6,
            "login_critical_days": 30,
            "login_warning_days": 14,
            "support_critical": 5,
            "support_warning": 3,
            "usage_critical": 0.2,
            "usage_warning": 0.4,
            "engagement_critical": 0.2,
            "engagement_warning": 0.4,
            "nps_critical": 4,
            "nps_warning": 6,
        }

        # Customer type adjustments
        type_multipliers = {
            "enterprise": {
                "health_critical": 0.9,  # More tolerant for enterprise
                "health_warning": 0.9,
                "login_critical_days": 1.5,  # Enterprise can go longer without login
                "login_warning_days": 1.5,
                "support_critical": 1.5,  # More tickets expected
                "support_warning": 1.5,
                "sensitivity": 0.8,  # Less sensitive to small changes
            },
            "startup": {
                "health_critical": 1.1,  # More aggressive for startups
                "health_warning": 1.1,
                "login_critical_days": 0.7,  # Startups should be more active
                "login_warning_days": 0.7,
                "support_critical": 0.8,  # Fewer tickets expected
                "support_warning": 0.8,
                "sensitivity": 1.3,  # More sensitive to changes
            },
            "mid_market": {
                "sensitivity": 1.0  # Baseline
            },
        }

        # Industry adjustments
        industry_adjustments = {
            "banking": {"sensitivity": 0.7},  # Banks move slowly
            "fintech": {"sensitivity": 1.2},  # Fintech needs quick response
            "healthcare": {"sensitivity": 0.8},  # Healthcare is cautious
            "technology": {"sensitivity": 1.1},  # Tech companies expect speed
            "manufacturing": {"sensitivity": 0.6},  # Traditional industry
            "saas": {"sensitivity": 1.3},  # SaaS expects high engagement
        }

        # MRR-based adjustments (higher value = more attention)
        mrr_multiplier = 1.0
        if mrr >= 10000:
            mrr_multiplier = 0.8  # More sensitive for high-value customers
        elif mrr >= 5000:
            mrr_multiplier = 0.9
        elif mrr < 2000:
            mrr_multiplier = 1.2  # Less sensitive for low-value customers

        # Apply adjustments
        type_adj = type_multipliers.get(customer_type, {"sensitivity": 1.0})
        industry_adj = industry_adjustments.get(industry, {"sensitivity": 1.0})

        final_thresholds = base_thresholds.copy()
        sensitivity = (
            type_adj.get("sensitivity", 1.0)
            * industry_adj.get("sensitivity", 1.0)
            * mrr_multiplier
        )

        # Apply type-specific threshold adjustments
        for key, value in base_thresholds.items():
            if key in type_adj:
                final_thresholds[key] = value * type_adj[key]

        final_thresholds["sensitivity"] = sensitivity
        return final_thresholds

    def calculate_alert_severity(
        self, customer: dict, alert_type: str, thresholds: dict
    ) -> Tuple[str, float]:
        """
        Calculate intelligent alert severity with context
        """
        base_severity = 0.5
        severity_factors = []

        # Health-based severity
        health_score = customer.get("health_score", 0.5)
        if health_score < thresholds["health_critical"]:
            severity_factors.append(("health_critical", 0.9))
        elif health_score < thresholds["health_warning"]:
            severity_factors.append(("health_warning", 0.6))

        # MRR-based severity boost
        mrr = customer.get("mrr", 0)
        if mrr >= 10000:
            severity_factors.append(("high_value", 0.3))
        elif mrr >= 5000:
            severity_factors.append(("medium_value", 0.15))

        # Customer type urgency
        customer_type = customer.get("customer_type", "mid_market")
        if customer_type == "enterprise":
            severity_factors.append(("enterprise_priority", 0.2))
        elif customer_type == "startup":
            severity_factors.append(("startup_urgency", 0.1))

        # Payment status escalation
        payment_status = customer.get("payment_status", "current")
        if payment_status == "overdue":
            severity_factors.append(("payment_overdue", 0.8))
        elif payment_status == "late":
            severity_factors.append(("payment_late", 0.4))

        # Support ticket overload
        support_tickets = customer.get("support_tickets", 0)
        if support_tickets > thresholds["support_critical"]:
            severity_factors.append(("support_overload", 0.6))

        # Usage decline velocity
        usage_score = customer.get("usage_score", 0.5)
        if usage_score < thresholds["usage_critical"]:
            severity_factors.append(("usage_critical", 0.7))

        # Calculate final severity
        max_severity = max([factor[1] for factor in severity_factors], default=0.2)
        avg_severity = (
            sum([factor[1] for factor in severity_factors]) / len(severity_factors)
            if severity_factors
            else 0.2
        )

        # Weighted combination
        final_severity = (max_severity * 0.6 + avg_severity * 0.4) * thresholds[
            "sensitivity"
        ]
        final_severity = min(1.0, max(0.0, final_severity))

        # Map to severity levels
        if final_severity >= 0.8:
            return "critical", final_severity
        elif final_severity >= 0.5:
            return "medium", final_severity
        else:
            return "low", final_severity

    def should_suppress_alert(
        self, customer_id: int, alert_type: str, current_time: datetime
    ) -> bool:
        """
        Prevent alert fatigue by suppressing duplicate/frequent alerts
        """
        key = f"{customer_id}_{alert_type}"

        if key not in self.alert_history:
            self.alert_history[key] = []
            return False

        # Get recent alerts (last 24 hours)
        recent_alerts = [
            alert_time
            for alert_time in self.alert_history[key]
            if current_time - alert_time < timedelta(hours=24)
        ]

        # Suppression rules
        if len(recent_alerts) >= 5:  # Max 5 alerts per day
            return True

        if recent_alerts and current_time - recent_alerts[-1] < timedelta(
            hours=2
        ):  # Min 2 hours between alerts
            return True

        # Critical alerts have less suppression
        if alert_type in ["churn_risk", "payment_risk"] and len(recent_alerts) < 3:
            return False

        return False

    def record_alert(self, customer_id: int, alert_type: str, current_time: datetime):
        """Record alert for fatigue prevention"""
        key = f"{customer_id}_{alert_type}"
        if key not in self.alert_history:
            self.alert_history[key] = []
        self.alert_history[key].append(current_time)

        # Keep only last 10 alerts per key
        self.alert_history[key] = self.alert_history[key][-10:]

    def enrich_alert_context(self, customer: dict, alert_type: str) -> dict:
        """
        Add contextual information to make alerts more actionable
        """
        customer_id = customer["id"]
        customer_type = customer.get("customer_type", "mid_market")
        industry = customer.get("industry", "technology")

        context = {
            "customer_profile": {
                "type": customer_type,
                "industry": industry,
                "mrr": customer.get("mrr", 0),
                "contract_length": customer.get("contract_length_months", 12),
                "onboarding_status": "complete"
                if customer.get("onboarding_completed", True)
                else "incomplete",
            },
            "risk_indicators": [],
            "success_patterns": [],
            "recommended_approach": "standard",
        }

        # Identify risk indicators
        if customer.get("payment_status") in ["late", "overdue"]:
            context["risk_indicators"].append("payment_issues")
        if customer.get("last_login_days", 0) > 30:
            context["risk_indicators"].append("low_engagement")
        if customer.get("support_tickets", 0) > 5:
            context["risk_indicators"].append("support_overload")
        if not customer.get("onboarding_completed", True):
            context["risk_indicators"].append("incomplete_onboarding")

        # Determine success patterns based on customer type
        if customer_type == "enterprise":
            context["success_patterns"] = [
                "executive_engagement",
                "structured_meetings",
                "roi_focus",
            ]
            context["recommended_approach"] = "executive"
        elif customer_type == "startup":
            context["success_patterns"] = [
                "quick_wins",
                "feature_adoption",
                "growth_metrics",
            ]
            context["recommended_approach"] = "agile"
        else:
            context["success_patterns"] = [
                "regular_checkins",
                "training_sessions",
                "best_practices",
            ]
            context["recommended_approach"] = "standard"

        # Industry-specific context
        if industry == "fintech":
            context["success_patterns"].append("compliance_focus")
        elif industry == "healthcare":
            context["success_patterns"].append("security_emphasis")
        elif industry == "saas":
            context["success_patterns"].append("integration_focus")

        return context

    def get_smart_actions(
        self, customer: dict, alert_type: str, context: dict
    ) -> List[dict]:
        """
        Generate contextually appropriate actions with effectiveness scoring
        """
        base_actions = ACTION_TEMPLATES.get(alert_type, [])
        customer_type = customer.get("customer_type", "mid_market")
        approach = context["recommended_approach"]

        smart_actions = []

        for action in base_actions:
            action_config = {
                "description": action,
                "priority": 1,
                "effectiveness_score": 0.7,
                "estimated_time": "medium",
                "success_rate": 0.6,
            }

            # Adjust based on customer type and context
            if "call" in action.lower() and customer_type == "enterprise":
                action_config["effectiveness_score"] = 0.9
                action_config["success_rate"] = 0.8
                action_config["priority"] = 1
            elif "email" in action.lower() and customer_type == "startup":
                action_config["effectiveness_score"] = 0.8
                action_config["success_rate"] = 0.7
            elif (
                "training" in action.lower()
                and "incomplete_onboarding" in context["risk_indicators"]
            ):
                action_config["effectiveness_score"] = 0.95
                action_config["success_rate"] = 0.85
                action_config["priority"] = 1

            # Payment-specific action prioritization
            if alert_type == "payment_risk":
                if "billing" in action.lower():
                    action_config["priority"] = 1
                    action_config["effectiveness_score"] = 0.9

            smart_actions.append(action_config)

        # Sort by effectiveness and priority
        smart_actions.sort(key=lambda x: (x["priority"], -x["effectiveness_score"]))

        return smart_actions[:3]  # Return top 3 actions

    def generate_intelligent_alert(
        self, customer: dict, alert_type: str, base_message: str
    ) -> dict:
        """
        Generate a fully intelligent alert with all enhancements
        """
        current_time = datetime.now()
        customer_id = customer["id"]

        # Check if we should suppress this alert
        if self.should_suppress_alert(customer_id, alert_type, current_time):
            return None

        # Get personalized thresholds
        thresholds = self.get_personalized_thresholds(customer)

        # Calculate intelligent severity
        severity, severity_score = self.calculate_alert_severity(
            customer, alert_type, thresholds
        )

        # Enrich with context
        context = self.enrich_alert_context(customer, alert_type)

        # Get smart actions
        smart_actions = self.get_smart_actions(customer, alert_type, context)

        # Record this alert
        self.record_alert(customer_id, alert_type, current_time)

        # Create enhanced alert
        intelligent_alert = {
            "customer_id": customer_id,
            "customer_name": customer["name"],
            "type": alert_type,
            "severity": severity,
            "severity_score": round(severity_score, 2),
            "message": base_message,
            "context": context,
            "smart_actions": smart_actions,
            "thresholds_used": thresholds,
            "created_at": current_time.isoformat(),
            "auto_escalate_at": (
                current_time + timedelta(hours=2 if severity == "critical" else 24)
            ).isoformat(),
            "tags": self._generate_alert_tags(customer, alert_type, context),
            "estimated_resolution_time": self._estimate_resolution_time(
                customer, alert_type, severity
            ),
            "similar_case_success_rate": self._get_similar_case_success_rate(
                customer, alert_type
            ),
        }

        return intelligent_alert

    def _generate_alert_tags(
        self, customer: dict, alert_type: str, context: dict
    ) -> List[str]:
        """Generate descriptive tags for alert categorization"""
        tags = [alert_type, customer.get("customer_type", "mid_market")]

        if customer.get("mrr", 0) >= 10000:
            tags.append("high_value")
        if context["recommended_approach"] == "executive":
            tags.append("executive_attention")
        if "payment_issues" in context["risk_indicators"]:
            tags.append("payment_risk")
        if len(context["risk_indicators"]) >= 3:
            tags.append("multiple_risks")

        return tags

    def _estimate_resolution_time(
        self, customer: dict, alert_type: str, severity: str
    ) -> str:
        """Estimate time needed to resolve this type of alert"""
        base_times = {
            "churn_risk": "2-4 hours",
            "payment_risk": "1-2 hours",
            "engagement_risk": "30-60 minutes",
            "usage_decline": "1-2 hours",
            "support_overload": "2-3 hours",
            "onboarding_incomplete": "3-5 hours",
            "expansion_opportunity": "45-90 minutes",
        }

        base_time = base_times.get(alert_type, "1-2 hours")

        # Adjust for customer complexity
        if customer.get("customer_type") == "enterprise":
            base_time = base_time.replace("minutes", "hours").replace(
                "1-2 hours", "2-4 hours"
            )
        elif severity == "critical":
            base_time = base_time.replace("2-4 hours", "1-2 hours").replace(
                "1-2 hours", "30-60 minutes"
            )

        return base_time

    def _get_similar_case_success_rate(self, customer: dict, alert_type: str) -> float:
        """Get historical success rate for similar cases (simulated)"""
        # In real implementation, this would query historical data
        base_rates = {
            "churn_risk": 0.65,
            "payment_risk": 0.85,
            "engagement_risk": 0.75,
            "usage_decline": 0.70,
            "support_overload": 0.80,
            "onboarding_incomplete": 0.90,
            "expansion_opportunity": 0.60,
        }

        base_rate = base_rates.get(alert_type, 0.70)

        # Adjust based on customer characteristics
        if customer.get("customer_type") == "enterprise":
            base_rate += 0.10  # Enterprise customers easier to retain
        elif customer.get("customer_type") == "startup":
            base_rate -= 0.05  # Startups more volatile

        if customer.get("nps_score", 5) >= 8:
            base_rate += 0.15  # Happy customers easier to help
        elif customer.get("nps_score", 5) <= 3:
            base_rate -= 0.20  # Unhappy customers harder to help

        return round(min(0.95, max(0.30, base_rate)), 2)
