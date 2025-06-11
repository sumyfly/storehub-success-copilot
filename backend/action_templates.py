"""
Action Templates Library - Predefined CS actions for different scenarios
"""

from enum import Enum
from typing import Any, Dict, List


class ActionUrgency(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionCategory(Enum):
    RETENTION = "retention"
    ENGAGEMENT = "engagement"
    EXPANSION = "expansion"
    SUPPORT = "support"
    ONBOARDING = "onboarding"


ACTION_TEMPLATES = {
    # CHURN RISK ACTIONS
    "urgent_retention_call": {
        "id": "urgent_retention_call",
        "title": "Schedule Urgent Retention Call",
        "description": "Immediate executive-level call to address critical concerns and prevent churn",
        "category": ActionCategory.RETENTION.value,
        "urgency": ActionUrgency.CRITICAL.value,
        "effort": "high",
        "timeline": "Within 24 hours",
        "success_rate": 0.65,
        "business_impact": "high",
        "prerequisites": ["Account value > $5000", "Health score < 0.3"],
        "steps": [
            "Review customer history and pain points",
            "Prepare retention offer/discount",
            "Schedule call with decision maker",
            "Document outcome and next steps",
        ],
        "templates": {
            "email_subject": "Urgent: Let's discuss your {company_name} experience",
            "phone_script": "Key talking points for retention conversation",
        },
    },
    "retention_email_sequence": {
        "id": "retention_email_sequence",
        "title": "Send Retention Email Sequence",
        "description": "Automated 3-email sequence addressing common churn reasons",
        "category": ActionCategory.RETENTION.value,
        "urgency": ActionUrgency.HIGH.value,
        "effort": "low",
        "timeline": "1-2 weeks",
        "success_rate": 0.35,
        "business_impact": "medium",
        "prerequisites": ["Health score < 0.4"],
        "steps": [
            "Email 1: Value reminder and success stories",
            "Email 2: Address common pain points",
            "Email 3: Retention offer and direct outreach",
        ],
    },
    "executive_outreach": {
        "id": "executive_outreach",
        "title": "Executive-Level Outreach",
        "description": "CEO/VP level intervention for high-value at-risk accounts",
        "category": ActionCategory.RETENTION.value,
        "urgency": ActionUrgency.CRITICAL.value,
        "effort": "high",
        "timeline": "48 hours",
        "success_rate": 0.75,
        "business_impact": "critical",
        "prerequisites": ["MRR > $10000", "Health score < 0.25"],
        "steps": [
            "Brief executive on account status",
            "Prepare strategic discussion points",
            "Schedule executive-to-executive call",
            "Follow up with action plan",
        ],
    },
    # ENGAGEMENT ACTIONS
    "personalized_checkin": {
        "id": "personalized_checkin",
        "title": "Send Personalized Check-in",
        "description": "Warm, personal email to understand current challenges and offer help",
        "category": ActionCategory.ENGAGEMENT.value,
        "urgency": ActionUrgency.MEDIUM.value,
        "effort": "low",
        "timeline": "2-3 days",
        "success_rate": 0.45,
        "business_impact": "medium",
        "prerequisites": ["Last login > 14 days"],
        "steps": [
            "Review recent account activity",
            "Craft personalized message referencing their use case",
            "Offer specific help or resources",
            "Schedule follow-up if needed",
        ],
    },
    "product_training_session": {
        "id": "product_training_session",
        "title": "Schedule Product Training",
        "description": "1-on-1 training to improve product adoption and usage",
        "category": ActionCategory.ENGAGEMENT.value,
        "urgency": ActionUrgency.MEDIUM.value,
        "effort": "medium",
        "timeline": "1 week",
        "success_rate": 0.60,
        "business_impact": "high",
        "prerequisites": ["Usage score < 0.4"],
        "steps": [
            "Identify specific feature gaps",
            "Prepare customized training agenda",
            "Schedule 45-60 minute session",
            "Provide follow-up resources",
        ],
    },
    "feature_adoption_campaign": {
        "id": "feature_adoption_campaign",
        "title": "Launch Feature Adoption Campaign",
        "description": "Targeted campaign to drive adoption of underutilized features",
        "category": ActionCategory.ENGAGEMENT.value,
        "urgency": ActionUrgency.LOW.value,
        "effort": "medium",
        "timeline": "2-3 weeks",
        "success_rate": 0.40,
        "business_impact": "medium",
        "prerequisites": ["Usage score < 0.6"],
        "steps": [
            "Identify most valuable unused features",
            "Create personalized feature guide",
            "Send weekly tips and tutorials",
            "Track adoption metrics",
        ],
    },
    # EXPANSION OPPORTUNITIES
    "upsell_presentation": {
        "id": "upsell_presentation",
        "title": "Present Upsell Opportunity",
        "description": "Strategic presentation of expansion opportunities based on usage patterns",
        "category": ActionCategory.EXPANSION.value,
        "urgency": ActionUrgency.HIGH.value,
        "effort": "high",
        "timeline": "1-2 weeks",
        "success_rate": 0.55,
        "business_impact": "high",
        "prerequisites": ["Health score > 0.7", "Usage trending up"],
        "steps": [
            "Analyze usage patterns for expansion signals",
            "Prepare ROI-focused presentation",
            "Schedule stakeholder meeting",
            "Present customized expansion proposal",
        ],
    },
    "strategic_account_review": {
        "id": "strategic_account_review",
        "title": "Conduct Strategic Account Review",
        "description": "Comprehensive quarterly business review with expansion roadmap",
        "category": ActionCategory.EXPANSION.value,
        "urgency": ActionUrgency.MEDIUM.value,
        "effort": "high",
        "timeline": "3-4 weeks",
        "success_rate": 0.70,
        "business_impact": "critical",
        "prerequisites": ["MRR > $8000", "Health score > 0.6"],
        "steps": [
            "Prepare comprehensive account analysis",
            "Schedule QBR with key stakeholders",
            "Present performance metrics and ROI",
            "Develop expansion roadmap",
        ],
    },
    # SUPPORT ACTIONS
    "escalate_support_priority": {
        "id": "escalate_support_priority",
        "title": "Escalate Support Priority",
        "description": "Fast-track critical support issues to prevent frustration",
        "category": ActionCategory.SUPPORT.value,
        "urgency": ActionUrgency.HIGH.value,
        "effort": "low",
        "timeline": "Same day",
        "success_rate": 0.80,
        "business_impact": "medium",
        "prerequisites": ["Support tickets > 5"],
        "steps": [
            "Review open support tickets",
            "Escalate to senior support team",
            "Provide direct CSM contact",
            "Monitor resolution progress",
        ],
    },
    "technical_health_check": {
        "id": "technical_health_check",
        "title": "Schedule Technical Health Check",
        "description": "Proactive technical review to identify and resolve potential issues",
        "category": ActionCategory.SUPPORT.value,
        "urgency": ActionUrgency.MEDIUM.value,
        "effort": "medium",
        "timeline": "1 week",
        "success_rate": 0.65,
        "business_impact": "medium",
        "prerequisites": ["Support tickets > 3", "Technical integration"],
        "steps": [
            "Schedule technical review call",
            "Review integration and usage patterns",
            "Identify optimization opportunities",
            "Provide technical recommendations",
        ],
    },
}

# Action categories for UI organization
ACTION_CATEGORIES = {
    ActionCategory.RETENTION.value: {
        "name": "Retention & Churn Prevention",
        "icon": "🛡️",
        "color": "red",
        "description": "Actions to prevent customer churn",
    },
    ActionCategory.ENGAGEMENT.value: {
        "name": "Engagement & Adoption",
        "icon": "🚀",
        "color": "blue",
        "description": "Actions to improve product usage",
    },
    ActionCategory.EXPANSION.value: {
        "name": "Growth & Expansion",
        "icon": "📈",
        "color": "green",
        "description": "Actions to grow account value",
    },
    ActionCategory.SUPPORT.value: {
        "name": "Support & Success",
        "icon": "🛠️",
        "color": "orange",
        "description": "Actions to resolve issues",
    },
}


def get_action_template(action_id: str) -> Dict[str, Any]:
    """Get a specific action template by ID"""
    return ACTION_TEMPLATES.get(action_id, {})


def get_actions_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all actions in a specific category"""
    return [
        action
        for action in ACTION_TEMPLATES.values()
        if action.get("category") == category
    ]


def get_actions_by_urgency(urgency: str) -> List[Dict[str, Any]]:
    """Get all actions with specific urgency level"""
    return [
        action
        for action in ACTION_TEMPLATES.values()
        if action.get("urgency") == urgency
    ]
