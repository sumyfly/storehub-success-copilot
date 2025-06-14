from typing import List

from action_templates import ACTION_CATEGORIES, ACTION_TEMPLATES

# Import alert intelligence
from alert_intelligence import AlertIntelligence
from analytics_engine import AnalyticsEngine
from auto_trigger_engine import AutoTriggerEngine
from csm_management_engine import CSMManagementEngine
from dashboard_engine import DashboardEngine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from health_engine import (
    calculate_health_score,
    generate_alerts,
    get_customer_label,
    get_health_trend,
    recommend_actions,
)
from mock_data import MOCK_CUSTOMERS
from models import Alert, Customer
from notification_engine import NotificationEngine
from priority_queue_manager import PriorityQueueManager

# Import new recommendation engine
from recommendation_engine import (
    get_recommendations_for_customer,
    get_recommendations_summary,
)
from workflow_engine import WorkflowEngine

app = FastAPI(title="Customer Success Copilot", version="0.1.0")

# Initialize intelligent alert systems
alert_intelligence = AlertIntelligence()
workflow_engine = WorkflowEngine()
notification_engine = NotificationEngine()
csm_management = CSMManagementEngine()
priority_queue = PriorityQueueManager(csm_management)
auto_trigger_engine = AutoTriggerEngine(
    workflow_engine, notification_engine, alert_intelligence
)
analytics_engine = AnalyticsEngine()
dashboard_engine = DashboardEngine()

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Customer Success Copilot API", "version": "0.1.0"}


@app.get("/customers", response_model=List[Customer])
async def get_customers():
    """Get all customers with their enhanced health scores and labels"""
    customers_with_health = []
    for customer_data in MOCK_CUSTOMERS:
        # Calculate health score for each customer
        health_score = calculate_health_score(customer_data)
        customer_label = get_customer_label(
            {**customer_data, "health_score": health_score}
        )

        # Create enhanced customer object
        enhanced_customer = {
            **customer_data,
            "health_score": health_score,
            "customer_label": customer_label,
        }
        customer = Customer(**enhanced_customer)
        customers_with_health.append(customer)
    return customers_with_health


@app.get("/alerts", response_model=List[Alert])
async def get_alerts():
    """Get all active alerts for at-risk customers"""
    all_alerts = []
    for customer_data in MOCK_CUSTOMERS:
        # Calculate health score first
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}

        # Generate alerts for this customer
        alerts = generate_alerts(customer_with_health)
        all_alerts.extend(alerts)

    return all_alerts


@app.get("/health/{customer_id}")
async def get_customer_health(customer_id: int):
    """Get detailed health information for a specific customer"""
    # Find customer by ID
    customer_data = next((c for c in MOCK_CUSTOMERS if c["id"] == customer_id), None)
    if not customer_data:
        return {"error": "Customer not found"}

    # Calculate health score and get additional insights
    health_score = calculate_health_score(customer_data)
    customer_with_health = {**customer_data, "health_score": health_score}

    # Get comprehensive health breakdown
    health_breakdown = {
        "customer_id": customer_id,
        "customer_name": customer_data["name"],
        "overall_health_score": health_score,
        "customer_label": get_customer_label(customer_with_health),
        "factors": {
            "usage_score": customer_data["usage_score"],
            "engagement_score": customer_data.get("engagement_score", 0),
            "support_tickets": customer_data["support_tickets"],
            "last_login_days": customer_data["last_login_days"],
            "payment_status": customer_data.get("payment_status", "current"),
            "feature_adoption": customer_data.get("feature_adoption", {}),
            "nps_score": customer_data.get("nps_score", 5),
            "mrr": customer_data["mrr"],
        },
        "risk_level": "critical"
        if health_score < 0.3
        else "medium"
        if health_score < 0.6
        else "healthy",
        "health_trend": get_health_trend(customer_with_health),
        "alerts": generate_alerts(customer_with_health),
        "recommended_actions": recommend_actions(customer_with_health),
    }

    return health_breakdown


@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get enhanced summary statistics for the dashboard"""
    customers_with_health = []
    all_alerts = []
    customer_labels = {}

    # Process all customers
    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        customers_with_health.append(customer_with_health)

        # Generate alerts
        alerts = generate_alerts(customer_with_health)
        all_alerts.extend(alerts)

        # Get customer labels
        label = get_customer_label(customer_with_health)
        customer_labels[customer_data["id"]] = label

    # Calculate enhanced stats
    critical_alerts = len([a for a in all_alerts if a["severity"] == "critical"])
    medium_risk = len(
        [c for c in customers_with_health if 0.3 <= c["health_score"] < 0.6]
    )
    healthy_customers = len(
        [c for c in customers_with_health if c["health_score"] >= 0.6]
    )

    # Count customers by label
    label_counts = {}
    for label in customer_labels.values():
        label_counts[label] = label_counts.get(label, 0) + 1

    # Calculate average health score
    avg_health = sum(c["health_score"] for c in customers_with_health) / len(
        customers_with_health
    )

    return {
        "total_customers": len(customers_with_health),
        "critical_alerts": critical_alerts,
        "medium_risk_customers": medium_risk,
        "healthy_customers": healthy_customers,
        "total_alerts": len(all_alerts),
        "average_health_score": round(avg_health, 2),
        "customer_segments": label_counts,
        "expansion_opportunities": len(
            [
                c
                for c in customers_with_health
                if c["health_score"] > 0.8 and c.get("nps_score", 0) >= 8
            ]
        ),
        "payment_issues": len(
            [
                c
                for c in customers_with_health
                if c.get("payment_status") in ["late", "overdue"]
            ]
        ),
    }


@app.get("/insights/trends")
async def get_health_trends():
    """Get health trend insights for all customers"""
    trends = []
    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        trend = get_health_trend(customer_with_health)

        trends.append(
            {
                "customer_id": customer_data["id"],
                "customer_name": customer_data["name"],
                "current_health": health_score,
                "trend": trend,
            }
        )

    return sorted(trends, key=lambda x: x["current_health"])


@app.get("/recommendations/{customer_id}")
async def get_customer_recommendations(customer_id: int):
    """Get intelligent action recommendations for a specific customer"""
    customer_data = next((c for c in MOCK_CUSTOMERS if c["id"] == customer_id), None)
    if not customer_data:
        return {"error": "Customer not found"}

    health_score = calculate_health_score(customer_data)
    customer_with_health = {**customer_data, "health_score": health_score}

    # Get intelligent recommendations
    intelligent_recommendations = get_recommendations_for_customer(customer_with_health)

    # Get current alerts for context
    current_alerts = generate_alerts(customer_with_health)

    return {
        "customer_id": customer_id,
        "customer_name": customer_data["name"],
        "current_health": health_score,
        "risk_level": "critical"
        if health_score < 0.3
        else "medium"
        if health_score < 0.6
        else "healthy",
        "total_recommendations": len(intelligent_recommendations),
        "recommendations": intelligent_recommendations,
        "current_alerts": current_alerts,
        "last_updated": "2024-01-15T10:30:00Z",
    }


@app.get("/actions/templates")
async def get_action_templates():
    """Get all available action templates organized by category"""
    return {
        "templates": ACTION_TEMPLATES,
        "categories": ACTION_CATEGORIES,
        "total_templates": len(ACTION_TEMPLATES),
    }


@app.get("/recommendations/summary")
async def get_recommendations_summary_endpoint():
    """Get summary of recommendations across all customers"""
    # Get all customers with health scores
    customers_with_health = []
    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        customers_with_health.append(customer_with_health)

    # Get recommendations summary
    summary = get_recommendations_summary(customers_with_health)

    return {
        "summary": summary,
        "total_customers_analyzed": len(customers_with_health),
        "generated_at": "2024-01-15T10:30:00Z",
    }


@app.post("/actions/{action_id}/execute")
async def execute_action(action_id: str, customer_id: int, csm_id: str = "default_csm"):
    """Execute a specific action for a customer"""
    # Find the action template
    action_template = ACTION_TEMPLATES.get(action_id)
    if not action_template:
        return {"error": "Action template not found"}

    # Find customer
    customer_data = next((c for c in MOCK_CUSTOMERS if c["id"] == customer_id), None)
    if not customer_data:
        return {"error": "Customer not found"}

    # Simulate action execution
    execution_result = {
        "action_id": action_id,
        "action_title": action_template["title"],
        "customer_id": customer_id,
        "customer_name": customer_data["name"],
        "csm_id": csm_id,
        "status": "executed",
        "execution_time": "2024-01-15T10:30:00Z",
        "estimated_completion": action_template.get("timeline", "Unknown"),
        "success_probability": action_template.get("success_rate", 0) * 100,
        "next_steps": action_template.get("steps", []),
    }

    return execution_result


@app.get("/dashboard/actions")
async def get_actions_dashboard():
    """Get dashboard view of all recommended actions across customers"""
    all_recommendations = []

    # Get recommendations for all customers
    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        customer_recs = get_recommendations_for_customer(customer_with_health)
        all_recommendations.extend(customer_recs)

    # Organize by urgency
    critical_actions = [
        r for r in all_recommendations if r.get("urgency") == "critical"
    ]
    high_priority = [r for r in all_recommendations if r.get("urgency") == "high"]
    medium_priority = [r for r in all_recommendations if r.get("urgency") == "medium"]

    # Organize by category
    retention_actions = [
        r for r in all_recommendations if r.get("category") == "retention"
    ]
    engagement_actions = [
        r for r in all_recommendations if r.get("category") == "engagement"
    ]
    expansion_actions = [
        r for r in all_recommendations if r.get("category") == "expansion"
    ]
    support_actions = [r for r in all_recommendations if r.get("category") == "support"]

    return {
        "summary": {
            "total_recommendations": len(all_recommendations),
            "critical_actions": len(critical_actions),
            "high_priority_actions": len(high_priority),
            "medium_priority_actions": len(medium_priority),
        },
        "by_urgency": {
            "critical": critical_actions[:5],  # Top 5 most critical
            "high": high_priority[:5],
            "medium": medium_priority[:5],
        },
        "by_category": {
            "retention": len(retention_actions),
            "engagement": len(engagement_actions),
            "expansion": len(expansion_actions),
            "support": len(support_actions),
        },
        "top_actions_today": sorted(
            all_recommendations,
            key=lambda x: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(
                    x.get("urgency", "low"), 1
                ),
                x.get("success_rate", 0),
            ),
            reverse=True,
        )[:10],
    }


@app.get("/alerts/intelligent")
async def get_intelligent_alerts():
    """Get intelligent alerts with personalized thresholds and context"""
    intelligent_alerts = []

    for customer_data in MOCK_CUSTOMERS:
        # Calculate health score first
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}

        # Generate basic alerts
        basic_alerts = generate_alerts(customer_with_health)

        # Enhance each alert with intelligence
        for basic_alert in basic_alerts:
            enhanced_alert = alert_intelligence.generate_intelligent_alert(
                customer_with_health, basic_alert["type"], basic_alert["message"]
            )

            if enhanced_alert:  # Alert wasn't suppressed
                intelligent_alerts.append(enhanced_alert)

    # Sort by severity score
    intelligent_alerts.sort(key=lambda x: x["severity_score"], reverse=True)
    return intelligent_alerts


@app.get("/alerts/queue")
async def get_alert_queue(
    csm_id: str = None, severity: str = None, customer_type: str = None
):
    """Get prioritized alert queue for CSMs with auto-triggered workflows"""
    automation_results = []

    # Create intelligent alerts and route them with auto-triggers
    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}

        basic_alerts = generate_alerts(customer_with_health)

        for basic_alert in basic_alerts:
            enhanced_alert = alert_intelligence.generate_intelligent_alert(
                customer_with_health, basic_alert["type"], basic_alert["message"]
            )

            if enhanced_alert:  # Route alert to workflow
                workflow = workflow_engine.route_alert(enhanced_alert)

                # Process auto-triggers for this alert
                trigger_results = auto_trigger_engine.process_alert_trigger(
                    enhanced_alert, workflow
                )
                automation_results.extend(trigger_results)

    # Apply filters
    filters = {}
    if severity:
        filters["severity"] = severity
    if customer_type:
        filters["customer_type"] = customer_type

    alert_queue = workflow_engine.get_alert_queue(csm_id, filters)

    return {
        "alert_queue": alert_queue,
        "automation_results": automation_results[:10],  # Show recent automations
        "total_automations": len(automation_results),
    }


@app.post("/alerts/{workflow_id}/execute")
async def execute_alert_action(workflow_id: str, action_description: str, csm_id: str):
    """Execute an action on an alert workflow"""
    return workflow_engine.execute_action(workflow_id, action_description, csm_id)


@app.post("/alerts/{workflow_id}/resolve")
async def resolve_alert(workflow_id: str, resolution_notes: str, csm_id: str):
    """Mark alert as resolved"""
    return workflow_engine.resolve_alert(workflow_id, resolution_notes, csm_id)


@app.post("/alerts/{workflow_id}/snooze")
async def snooze_alert(workflow_id: str, snooze_hours: int, reason: str, csm_id: str):
    """Snooze alert for specified hours"""
    return workflow_engine.snooze_alert(workflow_id, snooze_hours, reason, csm_id)


@app.post("/alerts/{workflow_id}/escalate")
async def escalate_alert(workflow_id: str, reason: str = "manual_escalation"):
    """Escalate alert to next level"""
    return workflow_engine.escalate_alert(workflow_id, reason)


@app.get("/alerts/escalation-candidates")
async def get_escalation_candidates():
    """Get alerts that need escalation"""
    return workflow_engine.get_escalation_candidates()


@app.get("/insights/action-effectiveness")
async def get_action_effectiveness():
    """Get insights on action effectiveness"""
    return workflow_engine.get_action_effectiveness_insights()


@app.get("/alerts/thresholds/{customer_id}")
async def get_customer_thresholds(customer_id: int):
    """Get personalized alert thresholds for a customer"""
    customer_data = next((c for c in MOCK_CUSTOMERS if c["id"] == customer_id), None)
    if not customer_data:
        return {"error": "Customer not found"}

    thresholds = alert_intelligence.get_personalized_thresholds(customer_data)
    return {
        "customer_id": customer_id,
        "customer_name": customer_data["name"],
        "thresholds": thresholds,
    }


@app.get("/automation/analytics")
async def get_automation_analytics():
    """Get analytics on automation performance and effectiveness"""
    return auto_trigger_engine.get_automation_analytics()


@app.get("/automation/rules")
async def get_automation_rules():
    """Get list of active automation rules"""
    return {
        "rules": auto_trigger_engine.trigger_rules,
        "total_rules": len(auto_trigger_engine.trigger_rules),
        "enabled_rules": len(
            [r for r in auto_trigger_engine.trigger_rules if r["enabled"]]
        ),
    }


@app.post("/automation/rules/{rule_id}/toggle")
async def toggle_automation_rule(rule_id: str):
    """Enable/disable an automation rule"""
    for rule in auto_trigger_engine.trigger_rules:
        if rule["id"] == rule_id:
            rule["enabled"] = not rule["enabled"]
            return {
                "rule_id": rule_id,
                "enabled": rule["enabled"],
                "message": f"Rule {rule_id} {'enabled' if rule['enabled'] else 'disabled'}",
            }

    return {"error": "Rule not found"}


@app.get("/notifications/analytics")
async def get_notification_analytics():
    """Get notification delivery analytics"""
    return notification_engine.get_notification_analytics()


@app.post("/notifications/digest")
async def create_daily_digest(recipient: str):
    """Create daily digest for a recipient"""
    # Get recent alerts for digest
    all_alerts = []
    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        basic_alerts = generate_alerts(customer_with_health)

        for basic_alert in basic_alerts:
            enhanced_alert = alert_intelligence.generate_intelligent_alert(
                customer_with_health, basic_alert["type"], basic_alert["message"]
            )
            if enhanced_alert:
                all_alerts.append(enhanced_alert)

    digest = notification_engine.create_daily_digest(recipient, all_alerts)
    return digest


# CSM Management Endpoints
@app.get("/csm/team-dashboard")
async def get_csm_team_dashboard():
    """Get comprehensive CSM team performance dashboard"""
    return csm_management.get_team_dashboard()


@app.get("/csm/workload-recommendations")
async def get_workload_recommendations():
    """Get recommendations for CSM workload optimization"""
    return csm_management.get_workload_recommendations()


@app.post("/csm/find-best-match")
async def find_best_csm_match(alert: dict, required_level: str = None):
    """Find the optimal CSM for a specific alert"""
    return csm_management.find_optimal_csm(alert, required_level)


@app.post("/csm/assign-alert")
async def assign_alert_to_csm(alert: dict, csm_id: str, workflow_id: str):
    """Assign a specific alert to a CSM"""
    return csm_management.assign_alert(alert, csm_id, workflow_id)


@app.post("/csm/complete-assignment/{assignment_id}")
async def complete_csm_assignment(
    assignment_id: str, outcome: str, resolution_time_hours: float
):
    """Complete a CSM assignment and update performance metrics"""
    return csm_management.complete_assignment(
        assignment_id, outcome, resolution_time_hours
    )


@app.get("/csm/assignment-history")
async def get_assignment_history():
    """Get recent CSM assignment history"""
    return {
        "assignments": list(csm_management.assignment_history.values())[
            -20:
        ],  # Last 20
        "total_assignments": len(csm_management.assignment_history),
    }


@app.get("/csm/smart-queue")
async def get_smart_csm_queue():
    """Get intelligent CSM queue with optimal assignments"""
    smart_queue = []

    # Get all intelligent alerts
    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        basic_alerts = generate_alerts(customer_with_health)

        for basic_alert in basic_alerts:
            enhanced_alert = alert_intelligence.generate_intelligent_alert(
                customer_with_health, basic_alert["type"], basic_alert["message"]
            )

            if enhanced_alert:
                # Find optimal CSM for each alert
                best_match = csm_management.find_optimal_csm(enhanced_alert)

                if "assigned_csm" in best_match:
                    queue_item = {
                        "alert": enhanced_alert,
                        "optimal_assignment": best_match,
                        "priority": enhanced_alert["severity_score"],
                        "estimated_resolution_time": enhanced_alert["context"][
                            "estimated_resolution_time"
                        ],
                    }
                    smart_queue.append(queue_item)

    # Sort by priority
    smart_queue.sort(key=lambda x: x["priority"], reverse=True)

    return {
        "smart_queue": smart_queue[:20],  # Top 20 prioritized items
        "queue_length": len(smart_queue),
        "team_stats": csm_management.get_team_dashboard()["team_overview"],
    }


# Priority Queue Management Endpoints
@app.post("/queue/add-alert")
async def add_alert_to_priority_queue(alert: dict, urgency_factors: dict = None):
    """Add alert to intelligent priority queue"""
    return priority_queue.add_to_queue(alert, urgency_factors)


@app.get("/queue/status")
async def get_priority_queue_status():
    """Get comprehensive priority queue status and analytics"""
    return priority_queue.get_queue_status()


@app.get("/queue/next-assignment")
async def get_next_priority_assignment(required_level: str = None):
    """Get next highest priority alert for CSM assignment"""
    csm_constraints = {"required_level": required_level} if required_level else None
    return priority_queue.get_next_priority_alert(csm_constraints)


@app.post("/queue/bulk-process")
async def bulk_process_alerts_to_queue():
    """Process all current alerts into priority queue"""
    processed_count = 0
    queue_results = []

    # Process all intelligent alerts through priority queue
    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        basic_alerts = generate_alerts(customer_with_health)

        for basic_alert in basic_alerts:
            enhanced_alert = alert_intelligence.generate_intelligent_alert(
                customer_with_health, basic_alert["type"], basic_alert["message"]
            )

            if enhanced_alert:
                # Add urgency factors based on alert characteristics
                urgency_factors = {}

                # Add SLA pressure
                if enhanced_alert["severity"] == "critical":
                    urgency_factors["sla_hours_remaining"] = 2
                elif enhanced_alert["severity"] == "high":
                    urgency_factors["sla_hours_remaining"] = 8
                else:
                    urgency_factors["sla_hours_remaining"] = 24

                # Add alert age simulation
                urgency_factors["alert_age_hours"] = 2

                # Add to priority queue
                queue_result = priority_queue.add_to_queue(
                    enhanced_alert, urgency_factors
                )
                queue_results.append(queue_result)
                processed_count += 1

    return {
        "processed_alerts": processed_count,
        "queue_status": priority_queue.get_queue_status(),
        "sample_results": queue_results[:5],  # Show first 5 results
    }


# Analytics & Optimization Endpoints
@app.get("/analytics/alert-patterns")
async def get_alert_patterns_analysis():
    """Get comprehensive alert pattern analysis"""
    # Collect all alerts data
    all_alerts = []
    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        basic_alerts = generate_alerts(customer_with_health)

        for basic_alert in basic_alerts:
            enhanced_alert = alert_intelligence.generate_intelligent_alert(
                customer_with_health, basic_alert["type"], basic_alert["message"]
            )
            if enhanced_alert:
                all_alerts.append(enhanced_alert)

    return analytics_engine.analyze_alert_patterns(all_alerts)


@app.get("/analytics/csm-performance")
async def get_csm_performance_analysis():
    """Get detailed CSM performance analysis"""
    csm_data = csm_management.csm_profiles
    assignment_history = csm_management.assignment_history

    return analytics_engine.analyze_csm_performance(csm_data, assignment_history)


@app.get("/analytics/customer-risks")
async def get_customer_risk_predictions():
    """Get AI-powered customer risk predictions and expansion opportunities"""
    # Prepare customer data with health scores
    customers_with_analysis = []
    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        customers_with_analysis.append(customer_with_health)

    return analytics_engine.predict_customer_risks(customers_with_analysis)


@app.get("/analytics/optimization-recommendations")
async def get_optimization_recommendations():
    """Get comprehensive optimization recommendations based on analytics"""
    # Gather all analytics data
    all_alerts = []
    customers_with_analysis = []

    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        customers_with_analysis.append(customer_with_health)

        basic_alerts = generate_alerts(customer_with_health)
        for basic_alert in basic_alerts:
            enhanced_alert = alert_intelligence.generate_intelligent_alert(
                customer_with_health, basic_alert["type"], basic_alert["message"]
            )
            if enhanced_alert:
                all_alerts.append(enhanced_alert)

    # Generate comprehensive analysis
    alert_patterns = analytics_engine.analyze_alert_patterns(all_alerts)
    csm_performance = analytics_engine.analyze_csm_performance(
        csm_management.csm_profiles, csm_management.assignment_history
    )
    customer_risks = analytics_engine.predict_customer_risks(customers_with_analysis)

    return analytics_engine.generate_optimization_recommendations(
        alert_patterns, csm_performance, customer_risks
    )


@app.get("/dashboard/executive")
async def get_executive_dashboard():
    """Get executive-level performance dashboard"""
    # Gather comprehensive data
    customers_with_analysis = []
    all_alerts = []

    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        customers_with_analysis.append(customer_with_health)

        basic_alerts = generate_alerts(customer_with_health)
        for basic_alert in basic_alerts:
            enhanced_alert = alert_intelligence.generate_intelligent_alert(
                customer_with_health, basic_alert["type"], basic_alert["message"]
            )
            if enhanced_alert:
                all_alerts.append(enhanced_alert)

    # Get analytics results for recommendations
    analytics_results = {
        "optimization_recommendations": analytics_engine.generate_optimization_recommendations(
            analytics_engine.analyze_alert_patterns(all_alerts),
            analytics_engine.analyze_csm_performance(
                csm_management.csm_profiles, csm_management.assignment_history
            ),
            analytics_engine.predict_customer_risks(customers_with_analysis),
        )
    }

    return dashboard_engine.generate_executive_dashboard(
        customers_with_analysis,
        all_alerts,
        csm_management.csm_profiles,
        analytics_results,
    )


@app.get("/dashboard/csm-operations")
async def get_csm_operations_dashboard():
    """Get CSM-focused operational dashboard"""
    # Collect alert data
    all_alerts = []
    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        basic_alerts = generate_alerts(customer_with_health)

        for basic_alert in basic_alerts:
            enhanced_alert = alert_intelligence.generate_intelligent_alert(
                customer_with_health, basic_alert["type"], basic_alert["message"]
            )
            if enhanced_alert:
                all_alerts.append(enhanced_alert)

    return dashboard_engine.generate_csm_dashboard(
        csm_management.csm_profiles, all_alerts, csm_management.assignment_history
    )


@app.get("/dashboard/customer-health")
async def get_customer_health_dashboard():
    """Get customer health focused dashboard"""
    # Prepare customer data
    customers_with_analysis = []
    all_alerts = []

    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        customers_with_analysis.append(customer_with_health)

        basic_alerts = generate_alerts(customer_with_health)
        for basic_alert in basic_alerts:
            enhanced_alert = alert_intelligence.generate_intelligent_alert(
                customer_with_health, basic_alert["type"], basic_alert["message"]
            )
            if enhanced_alert:
                all_alerts.append(enhanced_alert)

    return dashboard_engine.generate_customer_health_dashboard(
        customers_with_analysis, all_alerts
    )


@app.get("/analytics/comprehensive-report")
async def get_comprehensive_analytics_report():
    """Get comprehensive analytics report combining all insights"""
    # Collect all data
    customers_with_analysis = []
    all_alerts = []

    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        customers_with_analysis.append(customer_with_health)

        basic_alerts = generate_alerts(customer_with_health)
        for basic_alert in basic_alerts:
            enhanced_alert = alert_intelligence.generate_intelligent_alert(
                customer_with_health, basic_alert["type"], basic_alert["message"]
            )
            if enhanced_alert:
                all_alerts.append(enhanced_alert)

    # Generate all analytics
    alert_patterns = analytics_engine.analyze_alert_patterns(all_alerts)
    csm_performance = analytics_engine.analyze_csm_performance(
        csm_management.csm_profiles, csm_management.assignment_history
    )
    customer_risks = analytics_engine.predict_customer_risks(customers_with_analysis)
    optimization_recs = analytics_engine.generate_optimization_recommendations(
        alert_patterns, csm_performance, customer_risks
    )

    # Generate dashboards
    executive_dashboard = dashboard_engine.generate_executive_dashboard(
        customers_with_analysis,
        all_alerts,
        csm_management.csm_profiles,
        {"optimization_recommendations": optimization_recs},
    )
    csm_dashboard = dashboard_engine.generate_csm_dashboard(
        csm_management.csm_profiles, all_alerts, csm_management.assignment_history
    )
    health_dashboard = dashboard_engine.generate_customer_health_dashboard(
        customers_with_analysis, all_alerts
    )

    return {
        "report_generated_at": executive_dashboard["dashboard_generated_at"],
        "analytics": {
            "alert_patterns": alert_patterns,
            "csm_performance": csm_performance,
            "customer_risks": customer_risks,
            "optimization_recommendations": optimization_recs,
        },
        "dashboards": {
            "executive": executive_dashboard,
            "csm_operations": csm_dashboard,
            "customer_health": health_dashboard,
        },
        "key_insights": {
            "total_revenue_at_risk": alert_patterns.get("business_impact", {}).get(
                "total_revenue_at_risk", 0
            ),
            "high_risk_customers": customer_risks["summary"]["high_risk_customers"],
            "team_utilization": executive_dashboard["operational_efficiency"][
                "team_utilization"
            ],
            "average_health_score": executive_dashboard["business_health"][
                "average_health_score"
            ],
            "expansion_opportunities": customer_risks["summary"][
                "expansion_ready_customers"
            ],
        },
        "recommendations_summary": optimization_recs["recommendations"],
    }


# ===============================
# HOUR 6: ADVANCED ANALYTICS APIs
# ===============================


@app.get("/analytics/customer-journey")
async def get_customer_journey_analytics():
    """Customer Journey Analytics - Lifecycle stages and progression"""
    customers_with_health = []

    # Process all customers with journey data
    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        customers_with_health.append(customer_with_health)

    # Analyze journey stages
    stage_distribution = {}
    stage_performance = {}

    for customer in customers_with_health:
        stage = customer.get("lifecycle_stage", "unknown")

        # Count stage distribution
        stage_distribution[stage] = stage_distribution.get(stage, 0) + 1

        # Calculate stage performance metrics
        if stage not in stage_performance:
            stage_performance[stage] = {
                "customers": [],
                "avg_health": 0,
                "avg_days_in_stage": 0,
                "avg_time_to_value": 0,
                "expansion_potential": 0,
            }

        stage_performance[stage]["customers"].append(
            {
                "id": customer["id"],
                "name": customer["name"],
                "health_score": customer["health_score"],
                "days_in_stage": customer.get("days_in_stage", 0),
                "journey_velocity": customer.get("journey_velocity", 0),
                "expansion_score": customer.get("expansion_score", 0),
            }
        )

    # Calculate averages for each stage
    for stage, data in stage_performance.items():
        customers = data["customers"]
        if customers:
            data["avg_health"] = round(
                sum(c["health_score"] for c in customers) / len(customers), 2
            )
            data["avg_days_in_stage"] = round(
                sum(c["days_in_stage"] for c in customers) / len(customers), 1
            )
            data["expansion_potential"] = round(
                sum(c["expansion_score"] for c in customers) / len(customers), 2
            )

    return {
        "stage_distribution": stage_distribution,
        "stage_performance": stage_performance,
        "journey_insights": {
            "total_customers": len(customers_with_health),
            "fastest_time_to_value": min(
                (c.get("time_to_value_days", 999) for c in customers_with_health),
                default=0,
            ),
            "slowest_time_to_value": max(
                (c.get("time_to_value_days", 0) for c in customers_with_health),
                default=0,
            ),
            "avg_time_to_value": round(
                sum(c.get("time_to_value_days", 0) for c in customers_with_health)
                / len(customers_with_health),
                1,
            ),
        },
    }


@app.get("/analytics/risk-prediction")
async def get_risk_prediction_analytics():
    """Predictive Risk Modeling - Advanced churn probability analysis"""
    customers_with_health = []

    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        customers_with_health.append(customer_with_health)

    # Risk distribution analysis
    risk_buckets = {
        "critical_30d": [],  # >70% churn risk in 30 days
        "high_60d": [],  # >50% churn risk in 60 days
        "medium_90d": [],  # >30% churn risk in 90 days
        "low_risk": [],  # <30% churn risk
    }

    for customer in customers_with_health:
        churn_30d = customer.get("churn_probability_30d", 0)
        churn_60d = customer.get("churn_probability_60d", 0)
        churn_90d = customer.get("churn_probability_90d", 0)

        customer_risk_data = {
            "id": customer["id"],
            "name": customer["name"],
            "mrr": customer["mrr"],
            "churn_30d": churn_30d,
            "churn_60d": churn_60d,
            "churn_90d": churn_90d,
            "risk_factors": customer.get("risk_factors", []),
            "risk_trend": customer.get("risk_trend", "stable"),
        }

        if churn_30d > 0.7:
            risk_buckets["critical_30d"].append(customer_risk_data)
        elif churn_60d > 0.5:
            risk_buckets["high_60d"].append(customer_risk_data)
        elif churn_90d > 0.3:
            risk_buckets["medium_90d"].append(customer_risk_data)
        else:
            risk_buckets["low_risk"].append(customer_risk_data)

    # Calculate revenue at risk
    revenue_at_risk = {
        "critical_30d": sum(c["mrr"] for c in risk_buckets["critical_30d"]),
        "high_60d": sum(c["mrr"] for c in risk_buckets["high_60d"]),
        "medium_90d": sum(c["mrr"] for c in risk_buckets["medium_90d"]),
    }

    return {
        "risk_distribution": {k: len(v) for k, v in risk_buckets.items()},
        "risk_details": risk_buckets,
        "revenue_at_risk": revenue_at_risk,
        "total_revenue_at_risk": sum(revenue_at_risk.values()),
        "prediction_insights": {
            "highest_risk_customer": max(
                customers_with_health, key=lambda x: x.get("churn_probability_30d", 0)
            )["name"],
            "most_stable_customer": min(
                customers_with_health, key=lambda x: x.get("churn_probability_90d", 1)
            )["name"],
            "avg_churn_probability_30d": round(
                sum(c.get("churn_probability_30d", 0) for c in customers_with_health)
                / len(customers_with_health),
                2,
            ),
        },
    }


@app.get("/analytics/revenue-intelligence")
async def get_revenue_intelligence():
    """Revenue Intelligence - Expansion and growth opportunities"""
    customers_with_health = []

    for customer_data in MOCK_CUSTOMERS:
        health_score = calculate_health_score(customer_data)
        customer_with_health = {**customer_data, "health_score": health_score}
        customers_with_health.append(customer_with_health)

    # Expansion opportunities analysis
    expansion_ready = []
    upsell_candidates = []
    cross_sell_opportunities = []

    for customer in customers_with_health:
        expansion_score = customer.get("expansion_score", 0)
        upsell_readiness = customer.get("upsell_readiness", 0)
        cross_sell_potential = customer.get("cross_sell_potential", [])

        customer_revenue_data = {
            "id": customer["id"],
            "name": customer["name"],
            "current_mrr": customer["mrr"],
            "expansion_score": expansion_score,
            "upsell_readiness": upsell_readiness,
            "cross_sell_potential": cross_sell_potential,
            "revenue_growth_trend": customer.get("revenue_growth_trend", 0),
            "ltv_prediction": customer.get("ltv_prediction", 0),
            "health_score": customer["health_score"],
        }

        # High expansion potential (>0.7 expansion score)
        if expansion_score > 0.7:
            expansion_ready.append(customer_revenue_data)

        # High upsell readiness (>0.6 upsell score)
        if upsell_readiness > 0.6:
            upsell_candidates.append(customer_revenue_data)

        # Has cross-sell opportunities
        if cross_sell_potential:
            cross_sell_opportunities.append(customer_revenue_data)

    # Calculate potential revenue impact
    expansion_revenue_potential = sum(
        c["current_mrr"] * c["expansion_score"] for c in expansion_ready
    )
    upsell_revenue_potential = sum(
        c["current_mrr"] * c["upsell_readiness"] * 0.3 for c in upsell_candidates
    )  # Assume 30% upsell

    return {
        "expansion_opportunities": {
            "high_potential": expansion_ready,
            "count": len(expansion_ready),
            "revenue_potential": round(expansion_revenue_potential, 0),
        },
        "upsell_candidates": {
            "ready_customers": upsell_candidates,
            "count": len(upsell_candidates),
            "revenue_potential": round(upsell_revenue_potential, 0),
        },
        "cross_sell_opportunities": {
            "customers_with_potential": cross_sell_opportunities,
            "count": len(cross_sell_opportunities),
            "popular_products": [
                "analytics",
                "api",
                "training",
                "integrations",
                "premium_support",
            ],
        },
        "revenue_insights": {
            "total_current_mrr": sum(c["mrr"] for c in customers_with_health),
            "total_ltv_prediction": sum(
                c.get("ltv_prediction", 0) for c in customers_with_health
            ),
            "avg_revenue_growth": round(
                sum(c.get("revenue_growth_trend", 0) for c in customers_with_health)
                / len(customers_with_health),
                2,
            ),
            "expansion_revenue_potential": round(
                expansion_revenue_potential + upsell_revenue_potential, 0
            ),
        },
    }


@app.get("/customers/{customer_id}/journey")
async def get_customer_journey_details(customer_id: int):
    """Get detailed journey information for a specific customer"""
    customer_data = next((c for c in MOCK_CUSTOMERS if c["id"] == customer_id), None)
    if not customer_data:
        return {"error": "Customer not found"}

    health_score = calculate_health_score(customer_data)

    return {
        "customer_id": customer_id,
        "customer_name": customer_data["name"],
        "current_stage": customer_data.get("lifecycle_stage", "unknown"),
        "days_in_current_stage": customer_data.get("days_in_stage", 0),
        "previous_stage": customer_data.get("previous_stage", "unknown"),
        "journey_velocity": customer_data.get("journey_velocity", 0),
        "time_to_value": customer_data.get("time_to_value_days", 0),
        "health_score": health_score,
        "risk_prediction": {
            "30_day_churn_risk": customer_data.get("churn_probability_30d", 0),
            "60_day_churn_risk": customer_data.get("churn_probability_60d", 0),
            "90_day_churn_risk": customer_data.get("churn_probability_90d", 0),
            "risk_factors": customer_data.get("risk_factors", []),
            "risk_trend": customer_data.get("risk_trend", "stable"),
        },
        "revenue_intelligence": {
            "expansion_score": customer_data.get("expansion_score", 0),
            "upsell_readiness": customer_data.get("upsell_readiness", 0),
            "cross_sell_potential": customer_data.get("cross_sell_potential", []),
            "revenue_growth_trend": customer_data.get("revenue_growth_trend", 0),
            "ltv_prediction": customer_data.get("ltv_prediction", 0),
            "renewal_probability": customer_data.get("contract_renewal_probability", 0),
        },
    }
