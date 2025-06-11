from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List


class NotificationChannel(Enum):
    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"
    DASHBOARD = "dashboard"
    MOBILE_PUSH = "mobile_push"
    WEBHOOK = "webhook"


class NotificationPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class NotificationEngine:
    """
    Advanced notification system with multi-channel delivery and smart scheduling
    """

    def __init__(self):
        self.notification_rules = self._initialize_notification_rules()
        self.channel_configs = self._initialize_channel_configs()
        self.notification_history = {}
        self.delivery_preferences = {}  # User preferences per channel
        self.rate_limits = {}  # Rate limiting per channel/user

    def _initialize_notification_rules(self) -> Dict:
        """Initialize rules for when and how to send notifications"""
        return {
            "critical": {
                "channels": [
                    NotificationChannel.SLACK,
                    NotificationChannel.EMAIL,
                    NotificationChannel.SMS,
                ],
                "immediate": True,
                "escalation_delay_minutes": 15,
                "max_attempts": 3,
                "require_acknowledgment": True,
            },
            "medium": {
                "channels": [NotificationChannel.SLACK, NotificationChannel.EMAIL],
                "immediate": False,
                "delay_minutes": 30,
                "batch_notifications": True,
                "escalation_delay_minutes": 60,
                "max_attempts": 2,
            },
            "low": {
                "channels": [NotificationChannel.EMAIL, NotificationChannel.DASHBOARD],
                "immediate": False,
                "delay_minutes": 120,
                "batch_notifications": True,
                "daily_digest": True,
                "max_attempts": 1,
            },
        }

    def _initialize_channel_configs(self) -> Dict:
        """Initialize channel-specific configurations"""
        return {
            NotificationChannel.EMAIL: {
                "rate_limit_per_hour": 10,
                "template_types": ["alert", "digest", "escalation"],
                "retry_delay_minutes": [5, 15, 30],
            },
            NotificationChannel.SLACK: {
                "rate_limit_per_hour": 20,
                "channels": {
                    "critical": "#customer-success-critical",
                    "medium": "#customer-success-alerts",
                    "low": "#customer-success-digest",
                },
                "mention_rules": {"critical": "@channel", "medium": "@here", "low": ""},
            },
            NotificationChannel.SMS: {
                "rate_limit_per_hour": 5,
                "character_limit": 160,
                "cost_per_message": 0.02,
            },
            NotificationChannel.DASHBOARD: {
                "real_time": True,
                "persistence_days": 30,
                "auto_refresh_seconds": 30,
            },
        }

    def schedule_notification(
        self, alert: dict, workflow: dict, recipient: str
    ) -> dict:
        """
        Schedule notification based on alert severity and recipient preferences
        """
        severity = alert["severity"]
        notification_rule = self.notification_rules.get(
            severity, self.notification_rules["medium"]
        )

        # Create notification payload
        notification = {
            "id": f"notif_{alert['customer_id']}_{datetime.now().timestamp()}",
            "alert": alert,
            "workflow": workflow,
            "recipient": recipient,
            "severity": severity,
            "channels": notification_rule["channels"],
            "scheduled_at": datetime.now().isoformat(),
            "delivery_attempts": 0,
            "max_attempts": notification_rule["max_attempts"],
            "status": "scheduled",
            "require_acknowledgment": notification_rule.get(
                "require_acknowledgment", False
            ),
        }

        # Determine delivery time
        if notification_rule["immediate"]:
            notification["deliver_at"] = datetime.now().isoformat()
        else:
            delay_minutes = notification_rule.get("delay_minutes", 30)
            notification["deliver_at"] = (
                datetime.now() + timedelta(minutes=delay_minutes)
            ).isoformat()

        # Set escalation time if applicable
        if "escalation_delay_minutes" in notification_rule:
            escalation_delay = notification_rule["escalation_delay_minutes"]
            notification["escalate_at"] = (
                datetime.now() + timedelta(minutes=escalation_delay)
            ).isoformat()

        return notification

    def send_notification(self, notification: dict) -> dict:
        """
        Send notification through configured channels
        """
        results = {}

        for channel in notification["channels"]:
            if self._should_send_to_channel(notification, channel):
                result = self._send_to_channel(notification, channel)
                results[channel.value] = result
            else:
                results[channel.value] = {"status": "skipped", "reason": "rate_limited"}

        # Update notification status
        notification["delivery_attempts"] += 1
        notification["delivered_at"] = datetime.now().isoformat()
        notification["delivery_results"] = results

        # Check if acknowledgment is required
        if notification.get("require_acknowledgment"):
            notification["status"] = "awaiting_acknowledgment"
        else:
            notification["status"] = "delivered"

        return notification

    def _should_send_to_channel(
        self, notification: dict, channel: NotificationChannel
    ) -> bool:
        """Check if notification should be sent to this channel based on rate limits"""
        recipient = notification["recipient"]
        key = f"{recipient}_{channel.value}"

        if key not in self.rate_limits:
            self.rate_limits[key] = {"count": 0, "window_start": datetime.now()}

        rate_limit_info = self.rate_limits[key]
        channel_config = self.channel_configs[channel]

        # Check if we're in a new hour window
        if datetime.now() - rate_limit_info["window_start"] > timedelta(hours=1):
            rate_limit_info["count"] = 0
            rate_limit_info["window_start"] = datetime.now()

        # Check rate limit
        if rate_limit_info["count"] >= channel_config["rate_limit_per_hour"]:
            return False

        rate_limit_info["count"] += 1
        return True

    def _send_to_channel(
        self, notification: dict, channel: NotificationChannel
    ) -> dict:
        """Send notification to specific channel (simulated)"""
        alert = notification["alert"]
        recipient = notification["recipient"]

        if channel == NotificationChannel.SLACK:
            return self._send_slack_notification(alert, recipient)
        elif channel == NotificationChannel.EMAIL:
            return self._send_email_notification(alert, recipient)
        elif channel == NotificationChannel.SMS:
            return self._send_sms_notification(alert, recipient)
        elif channel == NotificationChannel.DASHBOARD:
            return self._send_dashboard_notification(alert, recipient)
        else:
            return {"status": "unsupported", "channel": channel.value}

    def _send_slack_notification(self, alert: dict, recipient: str) -> dict:
        """Send Slack notification (simulated)"""
        severity = alert["severity"]
        slack_config = self.channel_configs[NotificationChannel.SLACK]

        channel = slack_config["channels"].get(severity, "#customer-success-alerts")
        mention = slack_config["mention_rules"].get(severity, "")

        # Create Slack message
        message = {
            "channel": channel,
            "text": f"{mention} Customer Alert: {alert['customer_name']}",
            "attachments": [
                {
                    "color": "danger"
                    if severity == "critical"
                    else "warning"
                    if severity == "medium"
                    else "good",
                    "fields": [
                        {
                            "title": "Customer",
                            "value": alert["customer_name"],
                            "short": True,
                        },
                        {"title": "Type", "value": alert["type"], "short": True},
                        {"title": "Severity", "value": severity.upper(), "short": True},
                        {
                            "title": "Score",
                            "value": f"{alert.get('severity_score', 0):.2f}",
                            "short": True,
                        },
                        {"title": "Message", "value": alert["message"], "short": False},
                    ],
                    "actions": [
                        {
                            "name": "acknowledge",
                            "text": "Acknowledge",
                            "type": "button",
                        },
                        {
                            "name": "view_details",
                            "text": "View Details",
                            "type": "button",
                        },
                    ],
                }
            ],
        }

        # Simulate sending (in real implementation, use Slack API)
        return {
            "status": "sent",
            "channel": channel,
            "message_id": f"slack_{datetime.now().timestamp()}",
            "delivery_time": datetime.now().isoformat(),
        }

    def _send_email_notification(self, alert: dict, recipient: str) -> dict:
        """Send email notification (simulated)"""
        severity = alert["severity"]

        # Create email content
        email = {
            "to": recipient,
            "subject": f"🚨 {severity.upper()} Alert: {alert['customer_name']}",
            "html_body": self._generate_email_html(alert),
            "text_body": self._generate_email_text(alert),
        }

        # Simulate sending (in real implementation, use email service)
        return {
            "status": "sent",
            "email_id": f"email_{datetime.now().timestamp()}",
            "delivery_time": datetime.now().isoformat(),
            "recipient": recipient,
        }

    def _send_sms_notification(self, alert: dict, recipient: str) -> dict:
        """Send SMS notification (simulated)"""
        severity = alert["severity"]

        # Create short SMS message
        message = f"🚨 {severity.upper()}: {alert['customer_name']} - {alert['type']}. Check dashboard for details."

        # Truncate if too long
        char_limit = self.channel_configs[NotificationChannel.SMS]["character_limit"]
        if len(message) > char_limit:
            message = message[: char_limit - 3] + "..."

        # Simulate sending (in real implementation, use SMS service)
        return {
            "status": "sent",
            "sms_id": f"sms_{datetime.now().timestamp()}",
            "delivery_time": datetime.now().isoformat(),
            "recipient": recipient,
            "message_length": len(message),
        }

    def _send_dashboard_notification(self, alert: dict, recipient: str) -> dict:
        """Send dashboard notification (real-time)"""
        # In real implementation, this would push to WebSocket or similar
        return {
            "status": "sent",
            "channel": "dashboard",
            "recipient": recipient,
            "real_time": True,
            "delivery_time": datetime.now().isoformat(),
        }

    def _generate_email_html(self, alert: dict) -> str:
        """Generate HTML email content"""
        severity_colors = {"critical": "#d32f2f", "medium": "#f57c00", "low": "#388e3c"}

        color = severity_colors.get(alert["severity"], "#666666")

        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px;">
            <div style="background-color: {color}; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                <h2 style="margin: 0;">🚨 Customer Alert: {alert["customer_name"]}</h2>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Severity: {alert["severity"].upper()}</p>
            </div>
            
            <div style="background-color: #f5f5f5; padding: 20px; border-radius: 0 0 8px 8px;">
                <p><strong>Alert Type:</strong> {alert["type"]}</p>
                <p><strong>Message:</strong> {alert["message"]}</p>
                <p><strong>Severity Score:</strong> {alert.get("severity_score", 0):.2f}</p>
                
                <div style="margin-top: 20px;">
                    <h3>Recommended Actions:</h3>
                    <ul>
        """

        for action in alert.get("smart_actions", [])[:3]:
            html += f"<li>{action.get('description', 'No description')}</li>"

        html += (
            """
                    </ul>
                </div>
                
                <div style="margin-top: 20px; text-align: center;">
                    <a href="#" style="background-color: """
            + color
            + """; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">
                        View Full Details
                    </a>
                </div>
            </div>
        </div>
        """
        )

        return html

    def _generate_email_text(self, alert: dict) -> str:
        """Generate plain text email content"""
        text = f"""
🚨 CUSTOMER ALERT: {alert["customer_name"]}

Severity: {alert["severity"].upper()}
Type: {alert["type"]}
Score: {alert.get("severity_score", 0):.2f}

Message: {alert["message"]}

Recommended Actions:
"""

        for i, action in enumerate(alert.get("smart_actions", [])[:3], 1):
            text += f"{i}. {action.get('description', 'No description')}\n"

        text += "\nView full details in the Customer Success Dashboard."

        return text

    def acknowledge_notification(self, notification_id: str, user: str) -> dict:
        """Acknowledge a notification"""
        # In real implementation, update notification status
        return {
            "notification_id": notification_id,
            "acknowledged_by": user,
            "acknowledged_at": datetime.now().isoformat(),
            "status": "acknowledged",
        }

    def create_daily_digest(self, recipient: str, alerts: List[dict]) -> dict:
        """Create daily digest of notifications"""
        if not alerts:
            return {"status": "no_alerts", "recipient": recipient}

        # Group alerts by severity
        grouped_alerts = {"critical": [], "medium": [], "low": []}
        for alert in alerts:
            severity = alert.get("severity", "medium")
            grouped_alerts[severity].append(alert)

        digest = {
            "recipient": recipient,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "summary": {
                "total_alerts": len(alerts),
                "critical": len(grouped_alerts["critical"]),
                "medium": len(grouped_alerts["medium"]),
                "low": len(grouped_alerts["low"]),
            },
            "grouped_alerts": grouped_alerts,
            "delivery_channels": [NotificationChannel.EMAIL],
        }

        return digest

    def get_notification_analytics(self, time_range_days: int = 7) -> dict:
        """Get analytics on notification performance"""
        # Simulated analytics (in real implementation, query from database)
        return {
            "time_range_days": time_range_days,
            "total_notifications": 156,
            "delivery_success_rate": 0.95,
            "average_acknowledgment_time_minutes": 18,
            "channel_performance": {
                "slack": {"sent": 89, "acknowledged": 84, "success_rate": 0.94},
                "email": {"sent": 134, "acknowledged": 98, "success_rate": 0.73},
                "sms": {"sent": 23, "acknowledged": 22, "success_rate": 0.96},
            },
            "escalation_rate": 0.12,
            "false_positive_rate": 0.08,
        }
