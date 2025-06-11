"""
Intelligent Action Recommendation Engine
Analyzes customer health, risk factors, and patterns to suggest optimal actions
"""

from typing import Any, Dict, List

from action_templates import ACTION_TEMPLATES


class RecommendationEngine:
    def __init__(self):
        self.templates = ACTION_TEMPLATES

    def get_customer_recommendations(
        self, customer: Dict[str, Any], alerts: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized action recommendations for a customer
        """
        recommendations = []

        # Analyze customer risk profile
        risk_profile = self._analyze_customer_risk(customer)

        # Get recommendations based on risk factors
        recommendations.extend(self._get_churn_risk_actions(customer, risk_profile))
        recommendations.extend(self._get_engagement_actions(customer, risk_profile))
        recommendations.extend(self._get_expansion_actions(customer, risk_profile))
        recommendations.extend(self._get_support_actions(customer, risk_profile))

        # Prioritize and limit recommendations
        prioritized = self._prioritize_recommendations(recommendations, customer)

        # Add customer context to each recommendation
        return self._add_customer_context(prioritized, customer)

    def _analyze_customer_risk(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer to determine risk factors"""
        health_score = customer.get("health_score", 0.5)
        mrr = customer.get("mrr", 0)
        usage_score = customer.get("usage_score", 0.5)
        support_tickets = customer.get("support_tickets", 0)
        last_login_days = customer.get("last_login_days", 0)

        # Calculate risk factors
        churn_risk = self._calculate_churn_risk(
            health_score, mrr, usage_score, support_tickets, last_login_days
        )
        engagement_risk = self._calculate_engagement_risk(usage_score, last_login_days)
        expansion_potential = self._calculate_expansion_potential(
            health_score, mrr, usage_score
        )
        support_risk = self._calculate_support_risk(support_tickets, health_score)

        return {
            "churn_risk": churn_risk,
            "engagement_risk": engagement_risk,
            "expansion_potential": expansion_potential,
            "support_risk": support_risk,
            "account_tier": self._get_account_tier(mrr),
            "health_score": health_score,
            "mrr": mrr,
        }

    def _calculate_churn_risk(
        self,
        health_score: float,
        mrr: float,
        usage_score: float,
        support_tickets: int,
        last_login_days: int,
    ) -> str:
        """Calculate churn risk level"""
        risk_score = 0

        # Health score factor (most important)
        if health_score < 0.25:
            risk_score += 4
        elif health_score < 0.4:
            risk_score += 3
        elif health_score < 0.6:
            risk_score += 2
        elif health_score < 0.8:
            risk_score += 1

        # Usage factor
        if usage_score < 0.3:
            risk_score += 2
        elif usage_score < 0.5:
            risk_score += 1

        # Support tickets factor
        if support_tickets > 5:
            risk_score += 2
        elif support_tickets > 3:
            risk_score += 1

        # Login recency factor
        if last_login_days > 30:
            risk_score += 2
        elif last_login_days > 14:
            risk_score += 1

        # Determine risk level
        if risk_score >= 6:
            return "critical"
        elif risk_score >= 4:
            return "high"
        elif risk_score >= 2:
            return "medium"
        else:
            return "low"

    def _calculate_engagement_risk(
        self, usage_score: float, last_login_days: int
    ) -> str:
        """Calculate engagement risk level"""
        if usage_score < 0.3 or last_login_days > 21:
            return "high"
        elif usage_score < 0.5 or last_login_days > 14:
            return "medium"
        elif usage_score < 0.7 or last_login_days > 7:
            return "low"
        else:
            return "none"

    def _calculate_expansion_potential(
        self, health_score: float, mrr: float, usage_score: float
    ) -> str:
        """Calculate expansion opportunity potential"""
        if health_score > 0.7 and usage_score > 0.6 and mrr > 5000:
            return "high"
        elif health_score > 0.6 and usage_score > 0.5 and mrr > 2000:
            return "medium"
        elif health_score > 0.5 and usage_score > 0.4:
            return "low"
        else:
            return "none"

    def _calculate_support_risk(self, support_tickets: int, health_score: float) -> str:
        """Calculate support-related risk"""
        if support_tickets > 5 and health_score < 0.5:
            return "high"
        elif support_tickets > 3 or (support_tickets > 1 and health_score < 0.4):
            return "medium"
        elif support_tickets > 0:
            return "low"
        else:
            return "none"

    def _get_account_tier(self, mrr: float) -> str:
        """Determine account tier based on MRR"""
        if mrr >= 10000:
            return "enterprise"
        elif mrr >= 5000:
            return "premium"
        elif mrr >= 2000:
            return "professional"
        else:
            return "basic"

    def _get_churn_risk_actions(
        self, customer: Dict[str, Any], risk_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get actions for churn risk prevention"""
        actions = []
        churn_risk = risk_profile["churn_risk"]
        account_tier = risk_profile["account_tier"]

        if churn_risk == "critical":
            if account_tier in ["enterprise", "premium"]:
                actions.append(self.templates["executive_outreach"])
                actions.append(self.templates["urgent_retention_call"])
            else:
                actions.append(self.templates["urgent_retention_call"])
        elif churn_risk == "high":
            actions.append(self.templates["urgent_retention_call"])
            actions.append(self.templates["retention_email_sequence"])
        elif churn_risk == "medium":
            actions.append(self.templates["retention_email_sequence"])

        return actions

    def _get_engagement_actions(
        self, customer: Dict[str, Any], risk_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get actions for engagement improvement"""
        actions = []
        engagement_risk = risk_profile["engagement_risk"]
        usage_score = customer.get("usage_score", 0.5)
        last_login_days = customer.get("last_login_days", 0)

        if engagement_risk == "high":
            actions.append(self.templates["personalized_checkin"])
            if usage_score < 0.4:
                actions.append(self.templates["product_training_session"])
        elif engagement_risk == "medium":
            if last_login_days > 14:
                actions.append(self.templates["personalized_checkin"])
            if usage_score < 0.6:
                actions.append(self.templates["feature_adoption_campaign"])
        elif engagement_risk == "low":
            if usage_score < 0.7:
                actions.append(self.templates["feature_adoption_campaign"])

        return actions

    def _get_expansion_actions(
        self, customer: Dict[str, Any], risk_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get actions for account expansion"""
        actions = []
        expansion_potential = risk_profile["expansion_potential"]
        account_tier = risk_profile["account_tier"]

        if expansion_potential == "high":
            if account_tier in ["enterprise", "premium"]:
                actions.append(self.templates["strategic_account_review"])
            actions.append(self.templates["upsell_presentation"])
        elif expansion_potential == "medium":
            actions.append(self.templates["upsell_presentation"])

        return actions

    def _get_support_actions(
        self, customer: Dict[str, Any], risk_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get actions for support-related issues"""
        actions = []
        support_risk = risk_profile["support_risk"]
        support_tickets = customer.get("support_tickets", 0)

        if support_risk == "high":
            actions.append(self.templates["escalate_support_priority"])
            actions.append(self.templates["technical_health_check"])
        elif support_risk == "medium":
            if support_tickets > 3:
                actions.append(self.templates["escalate_support_priority"])
            else:
                actions.append(self.templates["technical_health_check"])

        return actions

    def _prioritize_recommendations(
        self, recommendations: List[Dict[str, Any]], customer: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Prioritize recommendations based on urgency and impact"""
        # Remove duplicates
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec["id"] not in seen:
                seen.add(rec["id"])
                unique_recommendations.append(rec)

        # Sort by urgency and business impact
        urgency_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        impact_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}

        def sort_key(action):
            urgency_score = urgency_order.get(action.get("urgency", "low"), 1)
            impact_score = impact_order.get(action.get("business_impact", "low"), 1)
            return (urgency_score * 2 + impact_score, action.get("success_rate", 0))

        sorted_recommendations = sorted(
            unique_recommendations, key=sort_key, reverse=True
        )

        # Limit to top 5 recommendations
        return sorted_recommendations[:5]

    def _add_customer_context(
        self, recommendations: List[Dict[str, Any]], customer: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Add customer-specific context to recommendations"""
        contextualized = []

        for rec in recommendations:
            # Create a copy to avoid modifying the template
            contextualized_rec = rec.copy()

            # Add customer-specific data
            contextualized_rec["customer_id"] = customer.get("id")
            contextualized_rec["customer_name"] = customer.get("name")
            contextualized_rec["customer_mrr"] = customer.get("mrr")
            contextualized_rec["customer_health_score"] = customer.get("health_score")

            # Add estimated ROI based on customer value
            mrr = customer.get("mrr", 0)
            if rec.get("category") == "retention":
                # Retention ROI = preventing churn
                contextualized_rec["estimated_roi"] = (
                    f"${mrr * 12:,.0f} (annual retention)"
                )
            elif rec.get("category") == "expansion":
                # Expansion ROI = potential upsell
                contextualized_rec["estimated_roi"] = (
                    f"${mrr * 0.3 * 12:,.0f} (30% expansion)"
                )
            else:
                # Other actions = efficiency gains
                contextualized_rec["estimated_roi"] = (
                    f"${mrr * 0.1 * 12:,.0f} (efficiency gains)"
                )

            # Add urgency reason
            health_score = customer.get("health_score", 0.5)
            if health_score < 0.3:
                contextualized_rec["urgency_reason"] = (
                    "Critical health score - immediate action required"
                )
            elif health_score < 0.5:
                contextualized_rec["urgency_reason"] = (
                    "Below-average health - proactive intervention needed"
                )
            elif customer.get("support_tickets", 0) > 5:
                contextualized_rec["urgency_reason"] = (
                    "High support volume - frustration risk"
                )
            elif customer.get("last_login_days", 0) > 21:
                contextualized_rec["urgency_reason"] = (
                    "Extended inactivity - engagement risk"
                )
            else:
                contextualized_rec["urgency_reason"] = "Optimization opportunity"

            contextualized.append(contextualized_rec)

        return contextualized


# Singleton instance
recommendation_engine = RecommendationEngine()


def get_recommendations_for_customer(
    customer: Dict[str, Any], alerts: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Main function to get recommendations for a customer"""
    return recommendation_engine.get_customer_recommendations(customer, alerts)


def get_all_action_templates() -> Dict[str, Any]:
    """Get all available action templates"""
    return ACTION_TEMPLATES


def get_recommendations_summary(customers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get a summary of recommendations across all customers"""
    all_recommendations = []

    for customer in customers:
        customer_recs = get_recommendations_for_customer(customer)
        all_recommendations.extend(customer_recs)

    # Aggregate statistics
    total_recommendations = len(all_recommendations)
    critical_actions = len(
        [r for r in all_recommendations if r.get("urgency") == "critical"]
    )
    high_priority_actions = len(
        [r for r in all_recommendations if r.get("urgency") == "high"]
    )

    # Group by category
    category_counts = {}
    for rec in all_recommendations:
        category = rec.get("category", "unknown")
        category_counts[category] = category_counts.get(category, 0) + 1

    return {
        "total_recommendations": total_recommendations,
        "critical_actions": critical_actions,
        "high_priority_actions": high_priority_actions,
        "category_breakdown": category_counts,
        "top_recommendations": all_recommendations[:10],  # Top 10 most urgent
    }
