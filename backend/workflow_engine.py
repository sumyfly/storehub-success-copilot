import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List


class AlertStatus(Enum):
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    SNOOZED = "snoozed"
    DISMISSED = "dismissed"


class ActionStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowEngine:
    """
    Manages alert workflows, escalation, and action tracking
    """

    def __init__(self):
        self.alert_workflows = {}  # Track alert workflow states
        self.csm_assignments = {}  # Track CSM workloads
        self.escalation_rules = self._initialize_escalation_rules()
        self.action_history = {}  # Track action effectiveness

    def _initialize_escalation_rules(self) -> Dict:
        """Initialize escalation rules based on customer type and alert severity"""
        return {
            "critical": {
                "enterprise": {
                    "initial_timeout": timedelta(hours=1),
                    "escalation_chain": ["senior_csm", "csm_manager", "vp_success"],
                    "auto_escalate": True,
                },
                "mid_market": {
                    "initial_timeout": timedelta(hours=2),
                    "escalation_chain": ["csm", "senior_csm", "csm_manager"],
                    "auto_escalate": True,
                },
                "startup": {
                    "initial_timeout": timedelta(hours=4),
                    "escalation_chain": ["csm", "senior_csm"],
                    "auto_escalate": True,
                },
            },
            "medium": {
                "enterprise": {
                    "initial_timeout": timedelta(hours=8),
                    "escalation_chain": ["csm", "senior_csm"],
                    "auto_escalate": False,
                },
                "mid_market": {
                    "initial_timeout": timedelta(hours=12),
                    "escalation_chain": ["csm", "senior_csm"],
                    "auto_escalate": False,
                },
                "startup": {
                    "initial_timeout": timedelta(hours=24),
                    "escalation_chain": ["csm"],
                    "auto_escalate": False,
                },
            },
            "low": {
                "enterprise": {
                    "initial_timeout": timedelta(hours=24),
                    "escalation_chain": ["csm"],
                    "auto_escalate": False,
                },
                "mid_market": {
                    "initial_timeout": timedelta(hours=48),
                    "escalation_chain": ["csm"],
                    "auto_escalate": False,
                },
                "startup": {
                    "initial_timeout": timedelta(hours=72),
                    "escalation_chain": ["csm"],
                    "auto_escalate": False,
                },
            },
        }

    def route_alert(self, alert: dict) -> dict:
        """
        Intelligently route alert to appropriate CSM based on workload and expertise
        """
        customer_type = (
            alert.get("context", {})
            .get("customer_profile", {})
            .get("type", "mid_market")
        )
        alert_type = alert["type"]
        severity = alert["severity"]
        mrr = alert.get("context", {}).get("customer_profile", {}).get("mrr", 0)

        # Determine required CSM level
        required_level = self._determine_csm_level(customer_type, severity, mrr)

        # Find best available CSM
        assigned_csm = self._find_best_csm(required_level, alert_type, customer_type)

        # Create workflow
        workflow_id = str(uuid.uuid4())
        workflow = {
            "workflow_id": workflow_id,
            "alert": alert,
            "assigned_csm": assigned_csm,
            "status": AlertStatus.ACTIVE.value,
            "created_at": datetime.now().isoformat(),
            "escalation_rules": self.escalation_rules[severity][customer_type],
            "next_escalation_at": None,
            "escalation_level": 0,
            "actions": [],
            "notes": [],
            "estimated_completion": None,
        }

        # Set escalation timer if auto-escalate is enabled
        if workflow["escalation_rules"]["auto_escalate"]:
            timeout = workflow["escalation_rules"]["initial_timeout"]
            workflow["next_escalation_at"] = (datetime.now() + timeout).isoformat()

        # Estimate completion time
        workflow["estimated_completion"] = self._estimate_completion_time(
            alert, assigned_csm
        )

        self.alert_workflows[workflow_id] = workflow
        return workflow

    def _determine_csm_level(
        self, customer_type: str, severity: str, mrr: float
    ) -> str:
        """Determine required CSM experience level"""
        if customer_type == "enterprise" or mrr >= 15000:
            return "senior_csm"
        elif severity == "critical" or mrr >= 8000:
            return "csm"
        else:
            return "junior_csm"

    def _find_best_csm(
        self, required_level: str, alert_type: str, customer_type: str
    ) -> dict:
        """Find best available CSM (simulated)"""
        # In real implementation, this would query CSM availability and expertise
        csm_pool = {
            "senior_csm": [
                {
                    "id": "csm_001",
                    "name": "Sarah Chen",
                    "workload": 5,
                    "specialties": ["enterprise", "churn_risk"],
                    "availability": "available",
                },
                {
                    "id": "csm_002",
                    "name": "Michael Rodriguez",
                    "workload": 3,
                    "specialties": ["payment_risk", "enterprise"],
                    "availability": "available",
                },
            ],
            "csm": [
                {
                    "id": "csm_003",
                    "name": "Jennifer Kim",
                    "workload": 7,
                    "specialties": ["mid_market", "engagement_risk"],
                    "availability": "available",
                },
                {
                    "id": "csm_004",
                    "name": "David Thompson",
                    "workload": 6,
                    "specialties": ["usage_decline", "support_overload"],
                    "availability": "available",
                },
            ],
            "junior_csm": [
                {
                    "id": "csm_005",
                    "name": "Emily Zhang",
                    "workload": 4,
                    "specialties": ["startup", "onboarding"],
                    "availability": "available",
                },
                {
                    "id": "csm_006",
                    "name": "Alex Johnson",
                    "workload": 5,
                    "specialties": ["expansion_opportunity"],
                    "availability": "available",
                },
            ],
        }

        available_csms = csm_pool.get(required_level, csm_pool["csm"])

        # Score CSMs based on workload, specialties, and availability
        best_csm = None
        best_score = -1

        for csm in available_csms:
            if csm["availability"] != "available":
                continue

            score = 0

            # Lower workload is better
            score += (10 - csm["workload"]) * 0.4

            # Specialty match bonus
            if alert_type in csm["specialties"] or customer_type in csm["specialties"]:
                score += 5

            if score > best_score:
                best_score = score
                best_csm = csm

        # Update workload
        if best_csm:
            best_csm["workload"] += 1

        return best_csm or available_csms[0]  # Fallback to first available

    def _estimate_completion_time(self, alert: dict, csm: dict) -> str:
        """Estimate when alert will be completed"""
        base_resolution_time = alert.get("estimated_resolution_time", "2 hours")
        csm_workload = csm.get("workload", 5)

        # Parse base time (simplified)
        if "minutes" in base_resolution_time:
            base_hours = 0.5
        elif "1-2 hours" in base_resolution_time:
            base_hours = 1.5
        elif "2-4 hours" in base_resolution_time:
            base_hours = 3
        else:
            base_hours = 2

        # Adjust for workload
        workload_multiplier = 1 + (csm_workload * 0.2)
        estimated_hours = base_hours * workload_multiplier

        completion_time = datetime.now() + timedelta(hours=estimated_hours)
        return completion_time.isoformat()

    def execute_action(
        self, workflow_id: str, action_description: str, csm_id: str
    ) -> dict:
        """Execute an action on an alert workflow"""
        if workflow_id not in self.alert_workflows:
            return {"error": "Workflow not found"}

        workflow = self.alert_workflows[workflow_id]

        action = {
            "action_id": str(uuid.uuid4()),
            "description": action_description,
            "executed_by": csm_id,
            "status": ActionStatus.IN_PROGRESS.value,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "outcome": None,
            "notes": [],
        }

        workflow["actions"].append(action)
        workflow["status"] = AlertStatus.IN_PROGRESS.value

        # Cancel auto-escalation when action is taken
        workflow["next_escalation_at"] = None

        return action

    def complete_action(
        self, workflow_id: str, action_id: str, outcome: str, notes: str = ""
    ) -> dict:
        """Mark an action as completed with outcome"""
        if workflow_id not in self.alert_workflows:
            return {"error": "Workflow not found"}

        workflow = self.alert_workflows[workflow_id]

        for action in workflow["actions"]:
            if action["action_id"] == action_id:
                action["status"] = ActionStatus.COMPLETED.value
                action["completed_at"] = datetime.now().isoformat()
                action["outcome"] = outcome
                if notes:
                    action["notes"].append(notes)

                # Track action effectiveness
                self._track_action_effectiveness(workflow, action, outcome)

                return action

        return {"error": "Action not found"}

    def resolve_alert(
        self, workflow_id: str, resolution_notes: str, csm_id: str
    ) -> dict:
        """Mark alert as resolved"""
        if workflow_id not in self.alert_workflows:
            return {"error": "Workflow not found"}

        workflow = self.alert_workflows[workflow_id]
        workflow["status"] = AlertStatus.RESOLVED.value
        workflow["resolved_at"] = datetime.now().isoformat()
        workflow["resolved_by"] = csm_id
        workflow["resolution_notes"] = resolution_notes

        # Calculate resolution metrics
        created_at = datetime.fromisoformat(workflow["created_at"])
        resolution_time = datetime.now() - created_at
        workflow["resolution_time_hours"] = round(
            resolution_time.total_seconds() / 3600, 2
        )

        # Update CSM workload
        assigned_csm = workflow["assigned_csm"]
        if assigned_csm:
            assigned_csm["workload"] = max(0, assigned_csm["workload"] - 1)

        return workflow

    def snooze_alert(
        self, workflow_id: str, snooze_hours: int, reason: str, csm_id: str
    ) -> dict:
        """Snooze alert for specified hours"""
        if workflow_id not in self.alert_workflows:
            return {"error": "Workflow not found"}

        workflow = self.alert_workflows[workflow_id]
        workflow["status"] = AlertStatus.SNOOZED.value
        workflow["snoozed_until"] = (
            datetime.now() + timedelta(hours=snooze_hours)
        ).isoformat()
        workflow["snooze_reason"] = reason
        workflow["snoozed_by"] = csm_id

        return workflow

    def escalate_alert(self, workflow_id: str, reason: str = "auto_escalation") -> dict:
        """Escalate alert to next level"""
        if workflow_id not in self.alert_workflows:
            return {"error": "Workflow not found"}

        workflow = self.alert_workflows[workflow_id]
        escalation_chain = workflow["escalation_rules"]["escalation_chain"]
        current_level = workflow["escalation_level"]

        if current_level >= len(escalation_chain) - 1:
            return {"error": "Maximum escalation level reached"}

        # Move to next escalation level
        workflow["escalation_level"] += 1
        new_role = escalation_chain[workflow["escalation_level"]]

        # Find new assignee
        new_assignee = self._find_best_csm(
            new_role,
            workflow["alert"]["type"],
            workflow["alert"]["context"]["customer_profile"]["type"],
        )

        workflow["assigned_csm"] = new_assignee
        workflow["status"] = AlertStatus.ESCALATED.value
        workflow["escalated_at"] = datetime.now().isoformat()
        workflow["escalation_reason"] = reason

        # Set next escalation timer if not at max level
        if workflow["escalation_level"] < len(escalation_chain) - 1:
            timeout = workflow["escalation_rules"]["initial_timeout"]
            workflow["next_escalation_at"] = (datetime.now() + timeout).isoformat()
        else:
            workflow["next_escalation_at"] = None

        return workflow

    def get_alert_queue(self, csm_id: str = None, filters: dict = None) -> List[dict]:
        """Get prioritized alert queue for CSM or all alerts"""
        alerts = []

        for workflow in self.alert_workflows.values():
            # Filter by CSM if specified
            if csm_id and workflow["assigned_csm"]["id"] != csm_id:
                continue

            # Apply filters
            if filters:
                if (
                    filters.get("severity")
                    and workflow["alert"]["severity"] != filters["severity"]
                ):
                    continue
                if filters.get("customer_type"):
                    customer_type = workflow["alert"]["context"]["customer_profile"][
                        "type"
                    ]
                    if customer_type != filters["customer_type"]:
                        continue

            # Skip resolved/dismissed alerts unless specifically requested
            if workflow["status"] in [
                AlertStatus.RESOLVED.value,
                AlertStatus.DISMISSED.value,
            ]:
                if not filters or not filters.get("include_resolved"):
                    continue

            alerts.append(workflow)

        # Sort by priority (severity, escalation level, creation time)
        def priority_score(workflow):
            severity_scores = {"critical": 3, "medium": 2, "low": 1}
            severity_score = severity_scores.get(workflow["alert"]["severity"], 1)
            escalation_bonus = workflow["escalation_level"] * 2

            # Time factor (older alerts get higher priority)
            created_at = datetime.fromisoformat(workflow["created_at"])
            hours_old = (datetime.now() - created_at).total_seconds() / 3600
            time_factor = min(hours_old / 24, 2)  # Cap at 2 days

            return severity_score + escalation_bonus + time_factor

        alerts.sort(key=priority_score, reverse=True)
        return alerts

    def get_escalation_candidates(self) -> List[dict]:
        """Get alerts that need escalation"""
        candidates = []
        current_time = datetime.now()

        for workflow in self.alert_workflows.values():
            if workflow["status"] not in [
                AlertStatus.ACTIVE.value,
                AlertStatus.IN_PROGRESS.value,
            ]:
                continue

            if not workflow.get("next_escalation_at"):
                continue

            escalation_time = datetime.fromisoformat(workflow["next_escalation_at"])
            if current_time >= escalation_time:
                candidates.append(workflow)

        return candidates

    def _track_action_effectiveness(self, workflow: dict, action: dict, outcome: str):
        """Track action effectiveness for learning"""
        customer_type = workflow["alert"]["context"]["customer_profile"]["type"]
        alert_type = workflow["alert"]["type"]
        action_desc = action["description"]

        key = f"{customer_type}_{alert_type}_{action_desc}"

        if key not in self.action_history:
            self.action_history[key] = {"successes": 0, "failures": 0, "total": 0}

        self.action_history[key]["total"] += 1

        if outcome in ["resolved", "improved", "successful"]:
            self.action_history[key]["successes"] += 1
        else:
            self.action_history[key]["failures"] += 1

    def get_action_effectiveness_insights(self) -> dict:
        """Get insights on action effectiveness"""
        insights = {}

        for key, data in self.action_history.items():
            if data["total"] >= 3:  # Only include actions with enough data
                success_rate = data["successes"] / data["total"]
                customer_type, alert_type, action = key.split("_", 2)

                if customer_type not in insights:
                    insights[customer_type] = {}
                if alert_type not in insights[customer_type]:
                    insights[customer_type][alert_type] = []

                insights[customer_type][alert_type].append(
                    {
                        "action": action,
                        "success_rate": round(success_rate, 2),
                        "total_executions": data["total"],
                    }
                )

        # Sort by success rate
        for customer_type in insights:
            for alert_type in insights[customer_type]:
                insights[customer_type][alert_type].sort(
                    key=lambda x: x["success_rate"], reverse=True
                )

        return insights
