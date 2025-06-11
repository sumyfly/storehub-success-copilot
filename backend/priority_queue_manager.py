import heapq
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class QueuePriority(Enum):
    URGENT = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class PriorityQueueManager:
    """
    Intelligent priority queue management for CSM assignments
    """

    def __init__(self, csm_management_engine):
        self.csm_management = csm_management_engine
        self.priority_queue = []  # Min-heap for priority queue
        self.queue_history = {}
        self.assignment_metrics = {}
        self.queue_id_counter = 1

    def add_to_queue(self, alert: dict, urgency_factors: dict = None) -> dict:
        """Add alert to priority queue with intelligent scoring"""

        # Calculate dynamic priority score
        priority_score = self._calculate_priority_score(alert, urgency_factors)

        # Create queue item
        queue_item = {
            "queue_id": f"q_{self.queue_id_counter:04d}",
            "alert": alert,
            "priority_score": priority_score,
            "queued_at": datetime.now().isoformat(),
            "estimated_wait_time": self._estimate_wait_time(priority_score),
            "urgency_factors": urgency_factors or {},
            "status": "queued",
        }

        # Add to priority queue (negative score for max-heap behavior)
        heapq.heappush(
            self.priority_queue, (-priority_score, self.queue_id_counter, queue_item)
        )

        # Store in history
        self.queue_history[queue_item["queue_id"]] = queue_item
        self.queue_id_counter += 1

        return {
            "success": True,
            "queue_item": queue_item,
            "queue_position": self._get_queue_position(queue_item["queue_id"]),
            "estimated_assignment_time": self._estimate_assignment_time(priority_score),
        }

    def _calculate_priority_score(
        self, alert: dict, urgency_factors: dict = None
    ) -> float:
        """Calculate dynamic priority score based on multiple factors"""
        score = 0.0

        # Base severity score (40% weight)
        severity_scores = {"critical": 100, "high": 80, "medium": 60, "low": 40}
        severity = alert.get("severity", "medium")
        score += severity_scores.get(severity, 60) * 0.4

        # Customer value score (25% weight)
        mrr = alert.get("context", {}).get("customer_profile", {}).get("mrr", 0)
        customer_type = (
            alert.get("context", {}).get("customer_profile", {}).get("type", "")
        )

        value_score = 0
        if mrr >= 50000:  # Enterprise high-value
            value_score = 100
        elif mrr >= 20000:  # Enterprise mid-value
            value_score = 85
        elif mrr >= 10000:  # Mid-market high-value
            value_score = 70
        elif mrr >= 5000:  # Mid-market
            value_score = 55
        else:  # Startup/SMB
            value_score = 40

        # Boost for enterprise customers
        if customer_type == "enterprise":
            value_score += 15

        score += value_score * 0.25

        # Time sensitivity (20% weight)
        time_score = self._calculate_time_sensitivity(alert, urgency_factors)
        score += time_score * 0.2

        # Business impact (15% weight)
        impact_score = self._calculate_business_impact(alert)
        score += impact_score * 0.15

        return round(score, 2)

    def _calculate_time_sensitivity(
        self, alert: dict, urgency_factors: dict = None
    ) -> float:
        """Calculate time-based urgency"""
        base_score = 50  # Default medium urgency

        urgency_factors = urgency_factors or {}

        # SLA deadline proximity
        if urgency_factors.get("sla_hours_remaining"):
            hours_remaining = urgency_factors["sla_hours_remaining"]
            if hours_remaining <= 1:
                base_score = 100  # Critical - SLA breach imminent
            elif hours_remaining <= 4:
                base_score = 85  # High - SLA at risk
            elif hours_remaining <= 8:
                base_score = 70  # Medium-high - SLA concern
            else:
                base_score = 55  # Medium - SLA comfortable

        # Alert age (longer wait = higher priority)
        if urgency_factors.get("alert_age_hours"):
            age_hours = urgency_factors["alert_age_hours"]
            if age_hours >= 24:
                base_score += 20  # Very old alert
            elif age_hours >= 12:
                base_score += 15  # Old alert
            elif age_hours >= 6:
                base_score += 10  # Moderately old

        # Payment issues get time boost
        if alert.get("type") in ["payment_risk", "payment_failed"]:
            base_score += 25

        # Churn risk gets time boost
        if alert.get("type") == "churn_risk":
            base_score += 20

        return min(100, base_score)

    def _calculate_business_impact(self, alert: dict) -> float:
        """Calculate business impact score"""
        impact_score = 50  # Default medium impact

        alert_type = alert.get("type", "")
        customer_profile = alert.get("context", {}).get("customer_profile", {})

        # High-impact alert types
        high_impact_types = [
            "churn_risk",
            "payment_risk",
            "usage_decline",
            "expansion_opportunity",
        ]
        if alert_type in high_impact_types:
            impact_score = 80

        # Critical impact types
        critical_impact_types = [
            "payment_failed",
            "contract_ending",
            "support_escalation",
        ]
        if alert_type in critical_impact_types:
            impact_score = 95

        # Multiple support tickets indicate escalating issue
        support_tickets = customer_profile.get("support_tickets", 0)
        if support_tickets >= 5:
            impact_score += 15
        elif support_tickets >= 3:
            impact_score += 10

        # Long-term customers get impact boost
        if customer_profile.get("tenure_months", 0) >= 24:
            impact_score += 10

        return min(100, impact_score)

    def _estimate_wait_time(self, priority_score: float) -> str:
        """Estimate wait time based on priority and current queue"""
        queue_size = len(self.priority_queue)

        if priority_score >= 90:
            wait_minutes = min(15, queue_size * 2)
        elif priority_score >= 80:
            wait_minutes = min(30, queue_size * 3)
        elif priority_score >= 70:
            wait_minutes = min(60, queue_size * 5)
        else:
            wait_minutes = min(120, queue_size * 8)

        if wait_minutes < 60:
            return f"{wait_minutes} minutes"
        else:
            hours = wait_minutes // 60
            remaining_minutes = wait_minutes % 60
            return (
                f"{hours}h {remaining_minutes}m"
                if remaining_minutes > 0
                else f"{hours}h"
            )

    def _estimate_assignment_time(self, priority_score: float) -> str:
        """Estimate when alert will be assigned to CSM"""
        current_time = datetime.now()

        if priority_score >= 90:
            assignment_time = current_time + timedelta(minutes=5)
        elif priority_score >= 80:
            assignment_time = current_time + timedelta(minutes=15)
        elif priority_score >= 70:
            assignment_time = current_time + timedelta(minutes=45)
        else:
            assignment_time = current_time + timedelta(hours=2)

        return assignment_time.strftime("%H:%M")

    def get_next_priority_alert(self, csm_constraints: dict = None) -> Optional[dict]:
        """Get next highest priority alert for assignment"""
        if not self.priority_queue:
            return None

        # Pop highest priority item
        neg_priority, queue_id, queue_item = heapq.heappop(self.priority_queue)

        # Update status
        queue_item["status"] = "assigned"
        queue_item["assigned_at"] = datetime.now().isoformat()

        # Find optimal CSM
        alert = queue_item["alert"]
        required_level = (
            csm_constraints.get("required_level") if csm_constraints else None
        )

        csm_match = self.csm_management.find_optimal_csm(alert, required_level)

        return {
            "queue_item": queue_item,
            "csm_assignment": csm_match,
            "priority_score": -neg_priority,
        }

    def _get_queue_position(self, queue_id: str) -> int:
        """Get current position in queue"""
        sorted_queue = sorted(
            self.priority_queue, reverse=True
        )  # Highest priority first
        for i, (neg_priority, qid, item) in enumerate(sorted_queue):
            if item["queue_id"] == queue_id:
                return i + 1
        return -1

    def get_queue_status(self) -> dict:
        """Get comprehensive queue status"""
        if not self.priority_queue:
            return {
                "queue_length": 0,
                "average_wait_time": "0 minutes",
                "priority_breakdown": {},
                "next_assignments": [],
            }

        # Analyze queue
        priority_breakdown = {"urgent": 0, "high": 0, "medium": 0, "low": 0}
        total_priority = 0
        next_assignments = []

        sorted_queue = sorted(self.priority_queue, reverse=True)

        for i, (neg_priority, qid, item) in enumerate(sorted_queue):
            priority_score = -neg_priority
            total_priority += priority_score

            # Categorize priority
            if priority_score >= 90:
                priority_breakdown["urgent"] += 1
            elif priority_score >= 75:
                priority_breakdown["high"] += 1
            elif priority_score >= 60:
                priority_breakdown["medium"] += 1
            else:
                priority_breakdown["low"] += 1

            # Get next 5 for assignment preview
            if i < 5:
                csm_match = self.csm_management.find_optimal_csm(item["alert"])
                next_assignments.append(
                    {
                        "queue_id": item["queue_id"],
                        "customer_name": item["alert"]["context"]["customer_profile"][
                            "name"
                        ],
                        "alert_type": item["alert"]["type"],
                        "priority_score": priority_score,
                        "optimal_csm": csm_match.get("assigned_csm", {}).get(
                            "name", "No CSM available"
                        ),
                        "estimated_resolution": item["alert"]["context"][
                            "estimated_resolution_time"
                        ],
                    }
                )

        avg_priority = total_priority / len(self.priority_queue)
        avg_wait_time = self._estimate_wait_time(avg_priority)

        return {
            "queue_length": len(self.priority_queue),
            "average_wait_time": avg_wait_time,
            "average_priority_score": round(avg_priority, 1),
            "priority_breakdown": priority_breakdown,
            "next_assignments": next_assignments,
            "queue_health": "good"
            if len(self.priority_queue) < 10
            else "busy"
            if len(self.priority_queue) < 20
            else "overloaded",
        }

    def get_queue_analytics(self) -> dict:
        """Get analytics on queue performance"""
        total_processed = len(
            [item for item in self.queue_history.values() if item["status"] != "queued"]
        )

        # Calculate average processing time
        processing_times = []
        for item in self.queue_history.values():
            if item["status"] == "assigned" and "assigned_at" in item:
                queued_time = datetime.fromisoformat(item["queued_at"])
                assigned_time = datetime.fromisoformat(item["assigned_at"])
                processing_time = (
                    assigned_time - queued_time
                ).total_seconds() / 60  # minutes
                processing_times.append(processing_time)

        avg_processing_time = (
            sum(processing_times) / len(processing_times) if processing_times else 0
        )

        # Priority distribution
        priority_distribution = {}
        for item in self.queue_history.values():
            score = item["priority_score"]
            if score >= 90:
                category = "urgent"
            elif score >= 75:
                category = "high"
            elif score >= 60:
                category = "medium"
            else:
                category = "low"

            priority_distribution[category] = priority_distribution.get(category, 0) + 1

        return {
            "total_alerts_processed": total_processed,
            "current_queue_length": len(self.priority_queue),
            "average_processing_time_minutes": round(avg_processing_time, 1),
            "priority_distribution": priority_distribution,
            "queue_efficiency": round(
                (total_processed / max(1, len(self.queue_history))) * 100, 1
            ),
            "performance_trend": "improving"
            if avg_processing_time < 30
            else "stable"
            if avg_processing_time < 60
            else "needs_attention",
        }
