"""
Notification Service

Handles notifications and alerts for case updates, rulings, and news.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationType(str, Enum):
    """Types of notifications."""
    CASE_UPDATE = "case_update"
    NEW_RULING = "new_ruling"
    JUDGE_ASSIGNMENT = "judge_assignment"
    DEADLINE_REMINDER = "deadline_reminder"
    PREDICTION_UPDATE = "prediction_update"
    JURISDICTION_NEWS = "jurisdiction_news"
    SYSTEM_ANNOUNCEMENT = "system_announcement"


class Notification:
    """Notification model."""

    def __init__(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        case_id: Optional[UUID] = None,
        judge_id: Optional[UUID] = None,
        jurisdiction_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = UUID(int=0)  # Would be generated
        self.notification_type = notification_type
        self.title = title
        self.message = message
        self.priority = priority
        self.case_id = case_id
        self.judge_id = judge_id
        self.jurisdiction_id = jurisdiction_id
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.read = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "type": self.notification_type.value,
            "title": self.title,
            "message": self.message,
            "priority": self.priority.value,
            "case_id": str(self.case_id) if self.case_id else None,
            "judge_id": str(self.judge_id) if self.judge_id else None,
            "jurisdiction_id": str(self.jurisdiction_id) if self.jurisdiction_id else None,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "read": self.read
        }


class NotificationService:
    """
    Service for managing notifications and alerts.

    Handles:
    - Case status change notifications
    - New ruling alerts
    - Deadline reminders
    - Prediction updates
    - Jurisdiction news
    """

    def __init__(self):
        """Initialize notification service."""
        # In production, this would connect to message queue/database
        self._notifications: Dict[str, List[Notification]] = {}
        self._subscriptions: Dict[str, List[str]] = {}

    async def create_notification(
        self,
        notification: Notification,
        user_ids: List[str]
    ) -> None:
        """
        Create and deliver notification to users.

        Args:
            notification: The notification to send
            user_ids: List of user IDs to notify
        """
        for user_id in user_ids:
            if user_id not in self._notifications:
                self._notifications[user_id] = []
            self._notifications[user_id].append(notification)

    async def notify_case_update(
        self,
        case_id: UUID,
        update_type: str,
        description: str,
        user_ids: List[str],
        priority: NotificationPriority = NotificationPriority.NORMAL
    ) -> None:
        """
        Send case update notification.

        Args:
            case_id: The case ID
            update_type: Type of update (status_change, new_event, etc.)
            description: Description of the update
            user_ids: Users to notify
            priority: Notification priority
        """
        notification = Notification(
            notification_type=NotificationType.CASE_UPDATE,
            title=f"Case Update: {update_type.replace('_', ' ').title()}",
            message=description,
            priority=priority,
            case_id=case_id,
            metadata={"update_type": update_type}
        )
        await self.create_notification(notification, user_ids)

    async def notify_new_ruling(
        self,
        judge_id: UUID,
        case_id: UUID,
        ruling_summary: str,
        user_ids: List[str]
    ) -> None:
        """
        Send new ruling notification.

        Args:
            judge_id: The judge who made the ruling
            case_id: The case ID
            ruling_summary: Summary of the ruling
            user_ids: Users to notify
        """
        notification = Notification(
            notification_type=NotificationType.NEW_RULING,
            title="New Ruling",
            message=ruling_summary,
            priority=NotificationPriority.HIGH,
            case_id=case_id,
            judge_id=judge_id
        )
        await self.create_notification(notification, user_ids)

    async def notify_deadline(
        self,
        case_id: UUID,
        deadline_type: str,
        deadline_date: datetime,
        user_ids: List[str]
    ) -> None:
        """
        Send deadline reminder.

        Args:
            case_id: The case ID
            deadline_type: Type of deadline
            deadline_date: The deadline date
            user_ids: Users to notify
        """
        notification = Notification(
            notification_type=NotificationType.DEADLINE_REMINDER,
            title=f"Upcoming Deadline: {deadline_type}",
            message=f"Deadline on {deadline_date.strftime('%Y-%m-%d %H:%M')}",
            priority=NotificationPriority.HIGH,
            case_id=case_id,
            metadata={
                "deadline_type": deadline_type,
                "deadline_date": deadline_date.isoformat()
            }
        )
        await self.create_notification(notification, user_ids)

    async def notify_prediction_update(
        self,
        case_id: UUID,
        old_prediction: str,
        new_prediction: str,
        confidence_change: float,
        user_ids: List[str]
    ) -> None:
        """
        Send prediction update notification.

        Args:
            case_id: The case ID
            old_prediction: Previous prediction
            new_prediction: New prediction
            confidence_change: Change in confidence
            user_ids: Users to notify
        """
        notification = Notification(
            notification_type=NotificationType.PREDICTION_UPDATE,
            title="Prediction Updated",
            message=(
                f"Prediction changed from {old_prediction} to {new_prediction}. "
                f"Confidence change: {confidence_change:+.1%}"
            ),
            priority=NotificationPriority.NORMAL,
            case_id=case_id,
            metadata={
                "old_prediction": old_prediction,
                "new_prediction": new_prediction,
                "confidence_change": confidence_change
            }
        )
        await self.create_notification(notification, user_ids)

    async def notify_jurisdiction_news(
        self,
        jurisdiction_id: UUID,
        news_type: str,
        title: str,
        content: str,
        user_ids: List[str]
    ) -> None:
        """
        Send jurisdiction news notification.

        Args:
            jurisdiction_id: The jurisdiction ID
            news_type: Type of news (new_law, court_change, etc.)
            title: News title
            content: News content
            user_ids: Users to notify
        """
        notification = Notification(
            notification_type=NotificationType.JURISDICTION_NEWS,
            title=title,
            message=content,
            priority=NotificationPriority.NORMAL,
            jurisdiction_id=jurisdiction_id,
            metadata={"news_type": news_type}
        )
        await self.create_notification(notification, user_ids)

    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for a user.

        Args:
            user_id: The user ID
            unread_only: Only return unread notifications
            limit: Maximum notifications to return

        Returns:
            List of notification dictionaries
        """
        notifications = self._notifications.get(user_id, [])

        if unread_only:
            notifications = [n for n in notifications if not n.read]

        notifications = sorted(
            notifications,
            key=lambda n: n.created_at,
            reverse=True
        )[:limit]

        return [n.to_dict() for n in notifications]

    async def mark_read(self, user_id: str, notification_ids: List[str]) -> None:
        """Mark notifications as read."""
        if user_id not in self._notifications:
            return

        for notification in self._notifications[user_id]:
            if str(notification.id) in notification_ids:
                notification.read = True

    async def subscribe(
        self,
        user_id: str,
        topic: str,
        topic_id: UUID
    ) -> None:
        """
        Subscribe user to notifications for a topic.

        Args:
            user_id: The user ID
            topic: Topic type (case, judge, jurisdiction)
            topic_id: The topic's ID
        """
        key = f"{topic}:{topic_id}"
        if key not in self._subscriptions:
            self._subscriptions[key] = []
        if user_id not in self._subscriptions[key]:
            self._subscriptions[key].append(user_id)

    async def unsubscribe(
        self,
        user_id: str,
        topic: str,
        topic_id: UUID
    ) -> None:
        """Unsubscribe user from a topic."""
        key = f"{topic}:{topic_id}"
        if key in self._subscriptions:
            self._subscriptions[key] = [
                uid for uid in self._subscriptions[key] if uid != user_id
            ]

    async def get_subscribers(
        self,
        topic: str,
        topic_id: UUID
    ) -> List[str]:
        """Get all subscribers for a topic."""
        key = f"{topic}:{topic_id}"
        return self._subscriptions.get(key, [])
