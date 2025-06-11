import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List


class TriggerType(Enum):
    ALERT_CREATED = "alert_created"
    SLA_VIOLATION = "sla_violation"
    ESCALATION_DUE = "escalation_due"
    NO_RESPONSE = "no_response"
    CUSTOMER_RISK_SPIKE = "customer_risk_spike"
    PATTERN_MATCH = "pattern_match"
    SCHEDULED_CHECK = "scheduled_check"


class ActionType(Enum):
    ASSIGN_CSM = "assign_csm"
    SEND_NOTIFICATION = "send_notification"
    ESCALATE_ALERT = "escalate_alert"
    CREATE_TICKET = "create_ticket"
    SCHEDULE_CALL = "schedule_call"
    SEND_EMAIL = "send_email"
    AUTO_RESOLVE = "auto_resolve"
    LOG_EVENT = "log_event"


class AutoTriggerEngine:
    """
    Intelligent automation engine that triggers workflows based on conditions
    """

    def __init__(self, workflow_engine, notification_engine, alert_intelligence):
        self.workflow_engine = workflow_engine
        self.notification_engine = notification_engine
        self.alert_intelligence = alert_intelligence

        self.trigger_rules = self._initialize_trigger_rules()
        self.execution_history = {}
        self.performance_metrics = {}
        self.active_triggers = {}

    def _initialize_trigger_rules(self) -> List[Dict]:
        """Initialize automated trigger rules"""
        return [
            # Critical alert auto-assignment
            {
                "id": "critical_alert_auto_assign",
                "trigger_type": TriggerType.ALERT_CREATED,
                "conditions": [
                    {"field": "severity", "operator": "equals", "value": "critical"},
                    {
                        "field": "customer_type",
                        "operator": "in",
                        "value": ["enterprise"],
                    },
                ],
                "actions": [
                    {
                        "type": ActionType.ASSIGN_CSM,
                        "params": {"level": "senior_csm", "urgent": True},
                    },
                    {
                        "type": ActionType.SEND_NOTIFICATION,
                        "params": {"channels": ["slack", "sms"], "immediate": True},
                    },
                    {
                        "type": ActionType.LOG_EVENT,
                        "params": {"event": "critical_alert_auto_assigned"},
                    },
                ],
                "delay_seconds": 0,
                "enabled": True,
                "priority": 1,
            },
            # Payment risk immediate escalation
            {
                "id": "payment_risk_escalation",
                "trigger_type": TriggerType.ALERT_CREATED,
                "conditions": [
                    {"field": "type", "operator": "equals", "value": "payment_risk"},
                    {"field": "mrr", "operator": "greater_than", "value": 10000},
                ],
                "actions": [
                    {"type": ActionType.ASSIGN_CSM, "params": {"level": "senior_csm"}},
                    {
                        "type": ActionType.SEND_NOTIFICATION,
                        "params": {
                            "channels": ["slack", "email"],
                            "priority": "urgent",
                        },
                    },
                    {
                        "type": ActionType.SCHEDULE_CALL,
                        "params": {"within_hours": 2, "type": "billing_resolution"},
                    },
                ],
                "delay_seconds": 300,  # 5 minute delay
                "enabled": True,
                "priority": 1,
            },
            # SLA violation escalation
            {
                "id": "sla_violation_escalate",
                "trigger_type": TriggerType.SLA_VIOLATION,
                "conditions": [
                    {"field": "hours_overdue", "operator": "greater_than", "value": 2}
                ],
                "actions": [
                    {
                        "type": ActionType.ESCALATE_ALERT,
                        "params": {"reason": "sla_violation"},
                    },
                    {
                        "type": ActionType.SEND_NOTIFICATION,
                        "params": {"channels": ["slack"], "mention": "@channel"},
                    },
                ],
                "delay_seconds": 0,
                "enabled": True,
                "priority": 2,
            },
            # No response auto-escalation
            {
                "id": "no_response_escalation",
                "trigger_type": TriggerType.NO_RESPONSE,
                "conditions": [
                    {
                        "field": "severity",
                        "operator": "in",
                        "value": ["critical", "medium"],
                    },
                    {
                        "field": "hours_since_created",
                        "operator": "greater_than",
                        "value": 4,
                    },
                ],
                "actions": [
                    {
                        "type": ActionType.ESCALATE_ALERT,
                        "params": {"reason": "no_response"},
                    },
                    {
                        "type": ActionType.SEND_NOTIFICATION,
                        "params": {"channels": ["email"], "recipient": "manager"},
                    },
                ],
                "delay_seconds": 0,
                "enabled": True,
                "priority": 2,
            },
            # Expansion opportunity auto-nurture
            {
                "id": "expansion_auto_nurture",
                "trigger_type": TriggerType.ALERT_CREATED,
                "conditions": [
                    {
                        "field": "type",
                        "operator": "equals",
                        "value": "expansion_opportunity",
                    },
                    {"field": "health_score", "operator": "greater_than", "value": 0.8},
                ],
                "actions": [
                    {
                        "type": ActionType.ASSIGN_CSM,
                        "params": {"level": "csm", "specialized": "growth"},
                    },
                    {
                        "type": ActionType.SEND_EMAIL,
                        "params": {
                            "template": "expansion_opportunity",
                            "delay_hours": 1,
                        },
                    },
                    {
                        "type": ActionType.SCHEDULE_CALL,
                        "params": {"within_days": 3, "type": "growth_discussion"},
                    },
                ],
                "delay_seconds": 3600,  # 1 hour delay
                "enabled": True,
                "priority": 3,
            },
            # Risk spike pattern detection
            {
                "id": "risk_spike_intervention",
                "trigger_type": TriggerType.CUSTOMER_RISK_SPIKE,
                "conditions": [
                    {
                        "field": "health_drop_percentage",
                        "operator": "greater_than",
                        "value": 0.3,
                    },
                    {"field": "timeframe_days", "operator": "less_than", "value": 7},
                ],
                "actions": [
                    {
                        "type": ActionType.ASSIGN_CSM,
                        "params": {"level": "senior_csm", "urgent": True},
                    },
                    {
                        "type": ActionType.SEND_NOTIFICATION,
                        "params": {"channels": ["slack"], "priority": "high"},
                    },
                    {
                        "type": ActionType.SCHEDULE_CALL,
                        "params": {
                            "within_hours": 24,
                            "type": "emergency_intervention",
                        },
                    },
                ],
                "delay_seconds": 0,
                "enabled": True,
                "priority": 1,
            },
            # Low engagement auto-nurture
            {
                "id": "low_engagement_nurture",
                "trigger_type": TriggerType.PATTERN_MATCH,
                "conditions": [
                    {
                        "field": "last_login_days",
                        "operator": "greater_than",
                        "value": 7,
                    },
                    {
                        "field": "engagement_score",
                        "operator": "less_than",
                        "value": 0.3,
                    },
                ],
                "actions": [
                    {
                        "type": ActionType.SEND_EMAIL,
                        "params": {"template": "re_engagement", "delay_hours": 2},
                    },
                    {
                        "type": ActionType.LOG_EVENT,
                        "params": {"event": "auto_nurture_triggered"},
                    },
                ],
                "delay_seconds": 7200,  # 2 hour delay
                "enabled": True,
                "priority": 4,
            },
        ]

    def process_alert_trigger(self, alert: dict, workflow: dict) -> List[Dict]:
        """Process triggers when a new alert is created"""
        trigger_results = []

        for rule in self.trigger_rules:
            if not rule["enabled"]:
                continue

            if rule["trigger_type"] != TriggerType.ALERT_CREATED:
                continue

            if self._evaluate_conditions(rule["conditions"], alert):
                result = self._execute_trigger_actions(rule, alert, workflow)
                trigger_results.append(result)

        return sorted(trigger_results, key=lambda x: x.get("priority", 999))

    def process_sla_violations(self) -> List[Dict]:
        """Check for and process SLA violations"""
        violations = []
        current_time = datetime.now()

        # Get all active workflows
        active_workflows = self.workflow_engine.get_alert_queue()

        for workflow in active_workflows:
            if workflow["status"] in ["resolved", "dismissed"]:
                continue

            # Check SLA violation
            created_time = datetime.fromisoformat(workflow["created_at"])
            hours_elapsed = (current_time - created_time).total_seconds() / 3600

            # Get expected SLA based on severity and customer type
            expected_sla = self._get_expected_sla(workflow)

            if hours_elapsed > expected_sla:
                violation_data = {
                    "workflow_id": workflow["workflow_id"],
                    "hours_overdue": hours_elapsed - expected_sla,
                    "expected_sla": expected_sla,
                    "severity": workflow["alert"]["severity"],
                    "customer_type": workflow["alert"]["context"]["customer_profile"][
                        "type"
                    ],
                }

                # Process SLA violation triggers
                for rule in self.trigger_rules:
                    if (
                        rule["trigger_type"] == TriggerType.SLA_VIOLATION
                        and rule["enabled"]
                    ):
                        if self._evaluate_conditions(
                            rule["conditions"], violation_data
                        ):
                            result = self._execute_trigger_actions(
                                rule, workflow["alert"], workflow, violation_data
                            )
                            violations.append(result)

        return violations

    def process_escalation_queue(self) -> List[Dict]:
        """Process alerts that need escalation"""
        escalation_results = []
        escalation_candidates = self.workflow_engine.get_escalation_candidates()

        for workflow in escalation_candidates:
            escalation_data = {
                "workflow_id": workflow["workflow_id"],
                "escalation_level": workflow["escalation_level"],
                "severity": workflow["alert"]["severity"],
                "hours_since_created": self._get_hours_since_created(workflow),
            }

            for rule in self.trigger_rules:
                if (
                    rule["trigger_type"] == TriggerType.ESCALATION_DUE
                    and rule["enabled"]
                ):
                    if self._evaluate_conditions(rule["conditions"], escalation_data):
                        result = self._execute_trigger_actions(
                            rule, workflow["alert"], workflow, escalation_data
                        )
                        escalation_results.append(result)

        return escalation_results

    def detect_risk_patterns(self, customers: List[Dict]) -> List[Dict]:
        """Detect sudden risk pattern changes in customers"""
        risk_spikes = []

        for customer in customers:
            # Simulate risk spike detection (in real implementation, compare with historical data)
            current_health = customer.get("health_score", 0.5)

            # Simulate previous health score (would come from database)
            previous_health = current_health + 0.2  # Simulate a drop

            if previous_health - current_health > 0.3:  # 30% drop
                spike_data = {
                    "customer_id": customer["id"],
                    "customer_name": customer["name"],
                    "health_drop_percentage": previous_health - current_health,
                    "current_health": current_health,
                    "previous_health": previous_health,
                    "timeframe_days": 7,  # Simulate timeframe
                }

                for rule in self.trigger_rules:
                    if (
                        rule["trigger_type"] == TriggerType.CUSTOMER_RISK_SPIKE
                        and rule["enabled"]
                    ):
                        if self._evaluate_conditions(rule["conditions"], spike_data):
                            # Create alert for this risk spike
                            alert = {
                                "customer_id": customer["id"],
                                "customer_name": customer["name"],
                                "type": "health_spike",
                                "severity": "critical",
                                "message": f"Health dropped {spike_data['health_drop_percentage']:.1%} in 7 days",
                            }

                            result = self._execute_trigger_actions(
                                rule, alert, None, spike_data
                            )
                            risk_spikes.append(result)

        return risk_spikes

    def _evaluate_conditions(self, conditions: List[Dict], data: Dict) -> bool:
        """Evaluate if conditions are met for trigger activation"""
        for condition in conditions:
            field = condition["field"]
            operator = condition["operator"]
            expected_value = condition["value"]

            # Get actual value from data
            actual_value = data.get(field)

            if actual_value is None:
                return False

            # Evaluate condition
            if operator == "equals" and actual_value != expected_value:
                return False
            elif operator == "greater_than" and actual_value <= expected_value:
                return False
            elif operator == "less_than" and actual_value >= expected_value:
                return False
            elif operator == "in" and actual_value not in expected_value:
                return False
            elif operator == "not_in" and actual_value in expected_value:
                return False

        return True

    def _execute_trigger_actions(
        self, rule: Dict, alert: Dict, workflow: Dict = None, trigger_data: Dict = None
    ) -> Dict:
        """Execute the actions defined in a trigger rule"""
        execution_id = str(uuid.uuid4())
        execution_result = {
            "execution_id": execution_id,
            "rule_id": rule["id"],
            "trigger_type": rule["trigger_type"].value,
            "executed_at": datetime.now().isoformat(),
            "actions_executed": [],
            "success": True,
            "priority": rule.get("priority", 999),
        }

        for action in rule["actions"]:
            action_result = self._execute_single_action(
                action, alert, workflow, trigger_data
            )
            execution_result["actions_executed"].append(action_result)

            if not action_result.get("success", False):
                execution_result["success"] = False

        # Track execution history
        self.execution_history[execution_id] = execution_result

        # Update performance metrics
        self._update_performance_metrics(rule["id"], execution_result["success"])

        return execution_result

    def _execute_single_action(
        self,
        action: Dict,
        alert: Dict,
        workflow: Dict = None,
        trigger_data: Dict = None,
    ) -> Dict:
        """Execute a single action"""
        action_type = ActionType(action["type"])
        params = action.get("params", {})

        try:
            if action_type == ActionType.ASSIGN_CSM:
                return self._action_assign_csm(alert, params)
            elif action_type == ActionType.SEND_NOTIFICATION:
                return self._action_send_notification(alert, params)
            elif action_type == ActionType.ESCALATE_ALERT:
                return self._action_escalate_alert(workflow, params)
            elif action_type == ActionType.SCHEDULE_CALL:
                return self._action_schedule_call(alert, params)
            elif action_type == ActionType.SEND_EMAIL:
                return self._action_send_email(alert, params)
            elif action_type == ActionType.LOG_EVENT:
                return self._action_log_event(alert, params, trigger_data)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported action type: {action_type}",
                }

        except Exception as e:
            return {"success": False, "error": str(e), "action_type": action_type.value}

    def _action_assign_csm(self, alert: Dict, params: Dict) -> Dict:
        """Auto-assign CSM to alert"""
        # This would integrate with the workflow engine
        return {
            "success": True,
            "action": "assign_csm",
            "level": params.get("level", "csm"),
            "urgent": params.get("urgent", False),
            "message": f"Auto-assigned {params.get('level', 'csm')} to {alert['customer_name']}",
        }

    def _action_send_notification(self, alert: Dict, params: Dict) -> Dict:
        """Send automated notification"""
        channels = params.get("channels", ["email"])
        immediate = params.get("immediate", False)

        return {
            "success": True,
            "action": "send_notification",
            "channels": channels,
            "immediate": immediate,
            "message": f"Notification sent via {', '.join(channels)}",
        }

    def _action_escalate_alert(self, workflow: Dict, params: Dict) -> Dict:
        """Auto-escalate alert"""
        if not workflow:
            return {"success": False, "error": "No workflow provided for escalation"}

        reason = params.get("reason", "auto_escalation")

        # This would call the workflow engine escalation
        return {
            "success": True,
            "action": "escalate_alert",
            "reason": reason,
            "workflow_id": workflow.get("workflow_id"),
            "message": f"Alert escalated due to {reason}",
        }

    def _action_schedule_call(self, alert: Dict, params: Dict) -> Dict:
        """Auto-schedule call"""
        within_hours = params.get("within_hours", 24)
        call_type = params.get("type", "standard")

        scheduled_time = datetime.now() + timedelta(hours=within_hours)

        return {
            "success": True,
            "action": "schedule_call",
            "call_type": call_type,
            "scheduled_time": scheduled_time.isoformat(),
            "customer": alert["customer_name"],
            "message": f"Call scheduled within {within_hours} hours",
        }

    def _action_send_email(self, alert: Dict, params: Dict) -> Dict:
        """Send automated email"""
        template = params.get("template", "standard")
        delay_hours = params.get("delay_hours", 0)

        send_time = datetime.now() + timedelta(hours=delay_hours)

        return {
            "success": True,
            "action": "send_email",
            "template": template,
            "send_time": send_time.isoformat(),
            "customer": alert["customer_name"],
            "message": f"Email scheduled using {template} template",
        }

    def _action_log_event(
        self, alert: Dict, params: Dict, trigger_data: Dict = None
    ) -> Dict:
        """Log automation event"""
        event = params.get("event", "automation_triggered")

        log_entry = {
            "event": event,
            "customer_id": alert["customer_id"],
            "timestamp": datetime.now().isoformat(),
            "trigger_data": trigger_data,
        }

        return {
            "success": True,
            "action": "log_event",
            "event": event,
            "message": f"Event logged: {event}",
        }

    def _get_expected_sla(self, workflow: Dict) -> float:
        """Get expected SLA hours based on severity and customer type"""
        severity = workflow["alert"]["severity"]
        customer_type = workflow["alert"]["context"]["customer_profile"]["type"]

        sla_matrix = {
            "critical": {"enterprise": 1, "mid_market": 2, "startup": 4},
            "medium": {"enterprise": 8, "mid_market": 12, "startup": 24},
            "low": {"enterprise": 24, "mid_market": 48, "startup": 72},
        }

        return sla_matrix.get(severity, {}).get(customer_type, 24)

    def _get_hours_since_created(self, workflow: Dict) -> float:
        """Get hours since workflow was created"""
        created_time = datetime.fromisoformat(workflow["created_at"])
        return (datetime.now() - created_time).total_seconds() / 3600

    def _update_performance_metrics(self, rule_id: str, success: bool):
        """Update performance metrics for trigger rules"""
        if rule_id not in self.performance_metrics:
            self.performance_metrics[rule_id] = {"executions": 0, "successes": 0}

        self.performance_metrics[rule_id]["executions"] += 1
        if success:
            self.performance_metrics[rule_id]["successes"] += 1

    def get_automation_analytics(self) -> Dict:
        """Get analytics on automation performance"""
        total_executions = len(self.execution_history)
        successful_executions = sum(
            1 for result in self.execution_history.values() if result["success"]
        )

        rule_performance = {}
        for rule_id, metrics in self.performance_metrics.items():
            rule_performance[rule_id] = {
                "success_rate": metrics["successes"] / metrics["executions"]
                if metrics["executions"] > 0
                else 0,
                "total_executions": metrics["executions"],
            }

        return {
            "total_automations": total_executions,
            "success_rate": successful_executions / total_executions
            if total_executions > 0
            else 0,
            "rule_performance": rule_performance,
            "recent_executions": list(self.execution_history.values())[-10:],  # Last 10
        }
