import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List


class CSMLevel(Enum):
    JUNIOR_CSM = "junior_csm"
    CSM = "csm"
    SENIOR_CSM = "senior_csm"
    CSM_MANAGER = "csm_manager"
    VP_SUCCESS = "vp_success"


class CSMStatus(Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OUT_OF_OFFICE = "out_of_office"
    OVERLOADED = "overloaded"


class CSMManagementEngine:
    """
    Intelligent CSM workload management and queue optimization
    """

    def __init__(self):
        self.csm_profiles = self._initialize_csm_profiles()
        self.workload_history = {}
        self.performance_metrics = {}
        self.assignment_history = {}
        self.queue_priorities = {}

    def _initialize_csm_profiles(self) -> Dict:
        """Initialize CSM team profiles with skills and capacities"""
        return {
            "csm_001": {
                "id": "csm_001",
                "name": "Sarah Chen",
                "level": CSMLevel.SENIOR_CSM.value,
                "email": "sarah.chen@company.com",
                "specialties": ["enterprise", "churn_risk", "financial_services"],
                "languages": ["english", "mandarin"],
                "timezone": "PST",
                "max_concurrent_alerts": 8,
                "current_workload": 3,
                "status": CSMStatus.AVAILABLE.value,
                "performance_metrics": {
                    "avg_resolution_time_hours": 4.2,
                    "success_rate": 0.89,
                    "customer_satisfaction": 4.6,
                    "escalation_rate": 0.08,
                },
                "availability": {
                    "monday": {"start": "09:00", "end": "17:00"},
                    "tuesday": {"start": "09:00", "end": "17:00"},
                    "wednesday": {"start": "09:00", "end": "17:00"},
                    "thursday": {"start": "09:00", "end": "17:00"},
                    "friday": {"start": "09:00", "end": "17:00"},
                },
            },
            "csm_002": {
                "id": "csm_002",
                "name": "Michael Rodriguez",
                "level": CSMLevel.SENIOR_CSM.value,
                "email": "michael.rodriguez@company.com",
                "specialties": ["payment_risk", "enterprise", "healthcare"],
                "languages": ["english", "spanish"],
                "timezone": "EST",
                "max_concurrent_alerts": 8,
                "current_workload": 2,
                "status": CSMStatus.AVAILABLE.value,
                "performance_metrics": {
                    "avg_resolution_time_hours": 3.8,
                    "success_rate": 0.92,
                    "customer_satisfaction": 4.7,
                    "escalation_rate": 0.05,
                },
                "availability": {
                    "monday": {"start": "08:00", "end": "16:00"},
                    "tuesday": {"start": "08:00", "end": "16:00"},
                    "wednesday": {"start": "08:00", "end": "16:00"},
                    "thursday": {"start": "08:00", "end": "16:00"},
                    "friday": {"start": "08:00", "end": "16:00"},
                },
            },
            "csm_003": {
                "id": "csm_003",
                "name": "Jennifer Kim",
                "level": CSMLevel.CSM.value,
                "email": "jennifer.kim@company.com",
                "specialties": ["mid_market", "engagement_risk", "technology"],
                "languages": ["english", "korean"],
                "timezone": "PST",
                "max_concurrent_alerts": 6,
                "current_workload": 4,
                "status": CSMStatus.AVAILABLE.value,
                "performance_metrics": {
                    "avg_resolution_time_hours": 5.1,
                    "success_rate": 0.85,
                    "customer_satisfaction": 4.4,
                    "escalation_rate": 0.12,
                },
                "availability": {
                    "monday": {"start": "09:00", "end": "17:00"},
                    "tuesday": {"start": "09:00", "end": "17:00"},
                    "wednesday": {"start": "09:00", "end": "17:00"},
                    "thursday": {"start": "09:00", "end": "17:00"},
                    "friday": {"start": "09:00", "end": "17:00"},
                },
            },
            "csm_004": {
                "id": "csm_004",
                "name": "David Thompson",
                "level": CSMLevel.CSM.value,
                "email": "david.thompson@company.com",
                "specialties": ["usage_decline", "support_overload", "saas"],
                "languages": ["english"],
                "timezone": "EST",
                "max_concurrent_alerts": 6,
                "current_workload": 5,
                "status": CSMStatus.AVAILABLE.value,
                "performance_metrics": {
                    "avg_resolution_time_hours": 6.2,
                    "success_rate": 0.81,
                    "customer_satisfaction": 4.2,
                    "escalation_rate": 0.15,
                },
                "availability": {
                    "monday": {"start": "08:00", "end": "16:00"},
                    "tuesday": {"start": "08:00", "end": "16:00"},
                    "wednesday": {"start": "08:00", "end": "16:00"},
                    "thursday": {"start": "08:00", "end": "16:00"},
                    "friday": {"start": "08:00", "end": "16:00"},
                },
            },
            "csm_005": {
                "id": "csm_005",
                "name": "Emily Zhang",
                "level": CSMLevel.JUNIOR_CSM.value,
                "email": "emily.zhang@company.com",
                "specialties": ["startup", "onboarding", "expansion_opportunity"],
                "languages": ["english", "mandarin"],
                "timezone": "PST",
                "max_concurrent_alerts": 4,
                "current_workload": 2,
                "status": CSMStatus.AVAILABLE.value,
                "performance_metrics": {
                    "avg_resolution_time_hours": 7.5,
                    "success_rate": 0.78,
                    "customer_satisfaction": 4.3,
                    "escalation_rate": 0.18,
                },
                "availability": {
                    "monday": {"start": "09:00", "end": "17:00"},
                    "tuesday": {"start": "09:00", "end": "17:00"},
                    "wednesday": {"start": "09:00", "end": "17:00"},
                    "thursday": {"start": "09:00", "end": "17:00"},
                    "friday": {"start": "09:00", "end": "17:00"},
                },
            },
            "csm_006": {
                "id": "csm_006",
                "name": "Alex Johnson",
                "level": CSMLevel.JUNIOR_CSM.value,
                "email": "alex.johnson@company.com",
                "specialties": ["expansion_opportunity", "mid_market"],
                "languages": ["english"],
                "timezone": "EST",
                "max_concurrent_alerts": 4,
                "current_workload": 3,
                "status": CSMStatus.AVAILABLE.value,
                "performance_metrics": {
                    "avg_resolution_time_hours": 8.1,
                    "success_rate": 0.76,
                    "customer_satisfaction": 4.1,
                    "escalation_rate": 0.20,
                },
                "availability": {
                    "monday": {"start": "08:00", "end": "16:00"},
                    "tuesday": {"start": "08:00", "end": "16:00"},
                    "wednesday": {"start": "08:00", "end": "16:00"},
                    "thursday": {"start": "08:00", "end": "16:00"},
                    "friday": {"start": "08:00", "end": "16:00"},
                },
            },
        }

    def find_optimal_csm(self, alert: dict, required_level: str = None) -> dict:
        """
        Find the optimal CSM for an alert using intelligent scoring
        """
        available_csms = self._get_available_csms(required_level)

        if not available_csms:
            return {"error": "No available CSMs found"}

        csm_scores = []

        for csm in available_csms:
            score = self._calculate_assignment_score(csm, alert)
            csm_scores.append({"csm": csm, "score": score})

        # Sort by score descending
        csm_scores.sort(key=lambda x: x["score"], reverse=True)

        best_match = csm_scores[0]
        return {
            "assigned_csm": best_match["csm"],
            "assignment_score": best_match["score"],
            "alternative_options": csm_scores[1:3],  # Top 2 alternatives
            "assignment_reasoning": self._generate_assignment_reasoning(
                best_match["csm"], alert
            ),
        }

    def _get_available_csms(self, required_level: str = None) -> List[dict]:
        """Get list of available CSMs, optionally filtered by level"""
        available_csms = []

        for csm in self.csm_profiles.values():
            if csm["status"] not in [CSMStatus.AVAILABLE.value, CSMStatus.BUSY.value]:
                continue

            if csm["current_workload"] >= csm["max_concurrent_alerts"]:
                continue

            if required_level and not self._meets_level_requirement(
                csm["level"], required_level
            ):
                continue

            if not self._is_within_working_hours(csm):
                continue

            available_csms.append(csm)

        return available_csms

    def _meets_level_requirement(self, csm_level: str, required_level: str) -> bool:
        """Check if CSM level meets requirement"""
        level_hierarchy = {
            CSMLevel.JUNIOR_CSM.value: 1,
            CSMLevel.CSM.value: 2,
            CSMLevel.SENIOR_CSM.value: 3,
            CSMLevel.CSM_MANAGER.value: 4,
            CSMLevel.VP_SUCCESS.value: 5,
        }

        return level_hierarchy.get(csm_level, 0) >= level_hierarchy.get(
            required_level, 0
        )

    def _is_within_working_hours(self, csm: dict) -> bool:
        """Check if CSM is within working hours (simplified)"""
        # In real implementation, check timezone and current time
        return True  # Simplified for demo

    def _calculate_assignment_score(self, csm: dict, alert: dict) -> float:
        """Calculate assignment score for CSM-alert pairing"""
        score = 0.0

        # Base performance score (40% weight)
        performance_score = (
            csm["performance_metrics"]["success_rate"] * 0.4
            + (1 - csm["performance_metrics"]["escalation_rate"]) * 0.3
            + (csm["performance_metrics"]["customer_satisfaction"] / 5.0) * 0.3
        )
        score += performance_score * 0.4

        # Specialty match (30% weight)
        specialty_score = self._calculate_specialty_match(csm, alert)
        score += specialty_score * 0.3

        # Workload balance (20% weight)
        workload_score = self._calculate_workload_score(csm)
        score += workload_score * 0.2

        # Experience level match (10% weight)
        experience_score = self._calculate_experience_match(csm, alert)
        score += experience_score * 0.1

        return round(score, 3)

    def _calculate_specialty_match(self, csm: dict, alert: dict) -> float:
        """Calculate how well CSM specialties match alert requirements"""
        alert_type = alert.get("type", "")
        customer_type = (
            alert.get("context", {}).get("customer_profile", {}).get("type", "")
        )
        industry = (
            alert.get("context", {}).get("customer_profile", {}).get("industry", "")
        )

        specialty_matches = 0
        total_relevant_specialties = 0

        # Check alert type match
        if alert_type in csm["specialties"]:
            specialty_matches += 2
        total_relevant_specialties += 2

        # Check customer type match
        if customer_type in csm["specialties"]:
            specialty_matches += 1
        total_relevant_specialties += 1

        # Check industry match
        if industry in csm["specialties"]:
            specialty_matches += 1
        total_relevant_specialties += 1

        return (
            specialty_matches / total_relevant_specialties
            if total_relevant_specialties > 0
            else 0.5
        )

    def _calculate_workload_score(self, csm: dict) -> float:
        """Calculate workload balance score (lower workload = higher score)"""
        workload_ratio = csm["current_workload"] / csm["max_concurrent_alerts"]
        return 1.0 - workload_ratio

    def _calculate_experience_match(self, csm: dict, alert: dict) -> float:
        """Calculate experience level appropriateness"""
        severity = alert.get("severity", "medium")
        mrr = alert.get("context", {}).get("customer_profile", {}).get("mrr", 0)

        level_scores = {
            CSMLevel.JUNIOR_CSM.value: {"critical": 0.3, "medium": 0.8, "low": 1.0},
            CSMLevel.CSM.value: {"critical": 0.7, "medium": 1.0, "low": 0.9},
            CSMLevel.SENIOR_CSM.value: {"critical": 1.0, "medium": 0.9, "low": 0.7},
        }

        base_score = level_scores.get(csm["level"], {}).get(severity, 0.5)

        # Adjust for customer value
        if mrr >= 10000 and csm["level"] in [
            CSMLevel.SENIOR_CSM.value,
            CSMLevel.CSM_MANAGER.value,
        ]:
            base_score += 0.2
        elif mrr < 5000 and csm["level"] == CSMLevel.JUNIOR_CSM.value:
            base_score += 0.1

        return min(1.0, base_score)

    def _generate_assignment_reasoning(self, csm: dict, alert: dict) -> dict:
        """Generate human-readable reasoning for assignment"""
        reasons = []

        # Performance-based reasons
        if csm["performance_metrics"]["success_rate"] > 0.85:
            reasons.append(
                f"High success rate ({csm['performance_metrics']['success_rate']:.1%})"
            )

        if csm["performance_metrics"]["escalation_rate"] < 0.10:
            reasons.append(
                f"Low escalation rate ({csm['performance_metrics']['escalation_rate']:.1%})"
            )

        # Specialty-based reasons
        alert_type = alert.get("type", "")
        if alert_type in csm["specialties"]:
            reasons.append(f"Specializes in {alert_type}")

        customer_type = (
            alert.get("context", {}).get("customer_profile", {}).get("type", "")
        )
        if customer_type in csm["specialties"]:
            reasons.append(f"Expert in {customer_type} customers")

        # Workload-based reasons
        workload_ratio = csm["current_workload"] / csm["max_concurrent_alerts"]
        if workload_ratio < 0.5:
            reasons.append("Low current workload")
        elif workload_ratio < 0.75:
            reasons.append("Moderate workload capacity")

        return {
            "primary_reasons": reasons[:3],
            "csm_level": csm["level"],
            "current_workload": f"{csm['current_workload']}/{csm['max_concurrent_alerts']}",
            "performance_summary": f"{csm['performance_metrics']['success_rate']:.1%} success rate",
        }

    def assign_alert(self, alert: dict, csm_id: str, workflow_id: str) -> dict:
        """Assign alert to specific CSM and update workload"""
        if csm_id not in self.csm_profiles:
            return {"error": "CSM not found"}

        csm = self.csm_profiles[csm_id]

        if csm["current_workload"] >= csm["max_concurrent_alerts"]:
            return {"error": "CSM at maximum capacity"}

        # Update workload
        csm["current_workload"] += 1

        # Record assignment
        assignment = {
            "assignment_id": str(uuid.uuid4()),
            "csm_id": csm_id,
            "workflow_id": workflow_id,
            "alert": alert,
            "assigned_at": datetime.now().isoformat(),
            "status": "active",
        }

        self.assignment_history[assignment["assignment_id"]] = assignment

        return {
            "success": True,
            "assignment": assignment,
            "csm_new_workload": csm["current_workload"],
        }

    def complete_assignment(
        self, assignment_id: str, outcome: str, resolution_time_hours: float
    ) -> dict:
        """Complete an assignment and update CSM metrics"""
        if assignment_id not in self.assignment_history:
            return {"error": "Assignment not found"}

        assignment = self.assignment_history[assignment_id]
        csm_id = assignment["csm_id"]
        csm = self.csm_profiles[csm_id]

        # Update workload
        csm["current_workload"] = max(0, csm["current_workload"] - 1)

        # Update assignment
        assignment["status"] = "completed"
        assignment["completed_at"] = datetime.now().isoformat()
        assignment["outcome"] = outcome
        assignment["resolution_time_hours"] = resolution_time_hours

        # Update performance metrics (simplified)
        self._update_csm_performance(csm, outcome, resolution_time_hours)

        return {
            "success": True,
            "assignment": assignment,
            "csm_new_workload": csm["current_workload"],
        }

    def _update_csm_performance(
        self, csm: dict, outcome: str, resolution_time_hours: float
    ):
        """Update CSM performance metrics (simplified exponential moving average)"""
        alpha = 0.1  # Learning rate

        # Update resolution time
        current_avg = csm["performance_metrics"]["avg_resolution_time_hours"]
        csm["performance_metrics"]["avg_resolution_time_hours"] = (
            1 - alpha
        ) * current_avg + alpha * resolution_time_hours

        # Update success rate
        success = 1.0 if outcome in ["resolved", "successful"] else 0.0
        current_success = csm["performance_metrics"]["success_rate"]
        csm["performance_metrics"]["success_rate"] = (
            1 - alpha
        ) * current_success + alpha * success

    def get_team_dashboard(self) -> dict:
        """Get comprehensive team performance dashboard"""
        team_stats = {
            "total_csms": len(self.csm_profiles),
            "available_csms": len(
                [
                    csm
                    for csm in self.csm_profiles.values()
                    if csm["status"] == CSMStatus.AVAILABLE.value
                ]
            ),
            "total_workload": sum(
                csm["current_workload"] for csm in self.csm_profiles.values()
            ),
            "total_capacity": sum(
                csm["max_concurrent_alerts"] for csm in self.csm_profiles.values()
            ),
            "utilization_rate": 0,
        }

        team_stats["utilization_rate"] = (
            team_stats["total_workload"] / team_stats["total_capacity"]
        )

        # Individual CSM stats
        csm_stats = []
        for csm in self.csm_profiles.values():
            workload_ratio = csm["current_workload"] / csm["max_concurrent_alerts"]

            csm_stat = {
                "id": csm["id"],
                "name": csm["name"],
                "level": csm["level"],
                "status": csm["status"],
                "workload": f"{csm['current_workload']}/{csm['max_concurrent_alerts']}",
                "utilization": round(workload_ratio, 2),
                "specialties": csm["specialties"],
                "performance": {
                    "success_rate": round(
                        csm["performance_metrics"]["success_rate"], 2
                    ),
                    "avg_resolution_hours": round(
                        csm["performance_metrics"]["avg_resolution_time_hours"], 1
                    ),
                    "customer_satisfaction": csm["performance_metrics"][
                        "customer_satisfaction"
                    ],
                    "escalation_rate": round(
                        csm["performance_metrics"]["escalation_rate"], 2
                    ),
                },
            }
            csm_stats.append(csm_stat)

        # Sort by performance score
        csm_stats.sort(key=lambda x: x["performance"]["success_rate"], reverse=True)

        return {
            "team_overview": team_stats,
            "csm_performance": csm_stats,
            "top_performers": csm_stats[:3],
            "needs_support": [
                csm
                for csm in csm_stats
                if csm["utilization"] > 0.9 or csm["performance"]["success_rate"] < 0.8
            ],
        }

    def get_workload_recommendations(self) -> dict:
        """Get recommendations for workload optimization"""
        recommendations = []

        # Check for overloaded CSMs
        for csm in self.csm_profiles.values():
            utilization = csm["current_workload"] / csm["max_concurrent_alerts"]

            if utilization > 0.9:
                recommendations.append(
                    {
                        "type": "workload_redistribution",
                        "priority": "high",
                        "csm": csm["name"],
                        "message": f"{csm['name']} is overloaded ({utilization:.1%} capacity)",
                        "suggestion": "Consider redistributing alerts or temporary capacity increase",
                    }
                )
            elif utilization < 0.3:
                recommendations.append(
                    {
                        "type": "capacity_utilization",
                        "priority": "medium",
                        "csm": csm["name"],
                        "message": f"{csm['name']} has low utilization ({utilization:.1%} capacity)",
                        "suggestion": "Can take on additional high-priority alerts",
                    }
                )

        # Performance-based recommendations
        for csm in self.csm_profiles.values():
            success_rate = csm["performance_metrics"]["success_rate"]
            escalation_rate = csm["performance_metrics"]["escalation_rate"]

            if success_rate < 0.75:
                recommendations.append(
                    {
                        "type": "performance_support",
                        "priority": "high",
                        "csm": csm["name"],
                        "message": f"{csm['name']} has low success rate ({success_rate:.1%})",
                        "suggestion": "Provide additional training or mentoring support",
                    }
                )
            elif escalation_rate > 0.20:
                recommendations.append(
                    {
                        "type": "escalation_training",
                        "priority": "medium",
                        "csm": csm["name"],
                        "message": f"{csm['name']} has high escalation rate ({escalation_rate:.1%})",
                        "suggestion": "Review escalation patterns and provide resolution training",
                    }
                )

        return {
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "high_priority": len(
                [r for r in recommendations if r["priority"] == "high"]
            ),
        }
