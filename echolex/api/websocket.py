"""
WebSocket API for Live Updates

Real-time notifications for case updates, new rulings, and alerts.
"""

from datetime import datetime
from typing import Dict, Set, List, Any
from uuid import UUID
import json
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel


websocket_router = APIRouter()


class ConnectionManager:
    """
    Manages WebSocket connections for live updates.

    Handles subscriptions for:
    - Case updates
    - Judge rulings
    - Jurisdiction news
    - Prediction updates
    """

    def __init__(self):
        """Initialize the connection manager."""
        # Active connections by client ID
        self.active_connections: Dict[str, WebSocket] = {}

        # Subscriptions by topic
        self.case_subscriptions: Dict[UUID, Set[str]] = {}
        self.judge_subscriptions: Dict[UUID, Set[str]] = {}
        self.jurisdiction_subscriptions: Dict[UUID, Set[str]] = {}

        # Global broadcast subscribers
        self.broadcast_subscribers: Set[str] = set()

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        await self._send_welcome(websocket, client_id)

    def disconnect(self, client_id: str):
        """Handle client disconnection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        # Clean up subscriptions
        self._remove_from_subscriptions(client_id, self.case_subscriptions)
        self._remove_from_subscriptions(client_id, self.judge_subscriptions)
        self._remove_from_subscriptions(client_id, self.jurisdiction_subscriptions)
        self.broadcast_subscribers.discard(client_id)

    def _remove_from_subscriptions(
        self,
        client_id: str,
        subscriptions: Dict[UUID, Set[str]]
    ):
        """Remove client from all subscriptions of a type."""
        for topic_id in list(subscriptions.keys()):
            subscriptions[topic_id].discard(client_id)
            if not subscriptions[topic_id]:
                del subscriptions[topic_id]

    async def _send_welcome(self, websocket: WebSocket, client_id: str):
        """Send welcome message to new connection."""
        await websocket.send_json({
            "type": "welcome",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to EchoLex Live Updates",
            "disclaimer": (
                "FOR RESEARCH PURPOSES ONLY. Live updates do not constitute legal advice."
            ),
            "available_subscriptions": [
                "cases",
                "judges",
                "jurisdictions",
                "broadcast"
            ]
        })

    async def subscribe_case(self, client_id: str, case_id: UUID):
        """Subscribe client to case updates."""
        if case_id not in self.case_subscriptions:
            self.case_subscriptions[case_id] = set()
        self.case_subscriptions[case_id].add(client_id)

        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json({
                "type": "subscribed",
                "topic": "case",
                "id": str(case_id),
                "timestamp": datetime.utcnow().isoformat()
            })

    async def subscribe_judge(self, client_id: str, judge_id: UUID):
        """Subscribe client to judge ruling updates."""
        if judge_id not in self.judge_subscriptions:
            self.judge_subscriptions[judge_id] = set()
        self.judge_subscriptions[judge_id].add(client_id)

        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json({
                "type": "subscribed",
                "topic": "judge",
                "id": str(judge_id),
                "timestamp": datetime.utcnow().isoformat()
            })

    async def subscribe_jurisdiction(self, client_id: str, jurisdiction_id: UUID):
        """Subscribe client to jurisdiction news."""
        if jurisdiction_id not in self.jurisdiction_subscriptions:
            self.jurisdiction_subscriptions[jurisdiction_id] = set()
        self.jurisdiction_subscriptions[jurisdiction_id].add(client_id)

        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json({
                "type": "subscribed",
                "topic": "jurisdiction",
                "id": str(jurisdiction_id),
                "timestamp": datetime.utcnow().isoformat()
            })

    async def subscribe_broadcast(self, client_id: str):
        """Subscribe client to broadcast updates."""
        self.broadcast_subscribers.add(client_id)

        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json({
                "type": "subscribed",
                "topic": "broadcast",
                "timestamp": datetime.utcnow().isoformat()
            })

    async def unsubscribe(self, client_id: str, topic: str, topic_id: UUID = None):
        """Unsubscribe client from a topic."""
        if topic == "case" and topic_id:
            if topic_id in self.case_subscriptions:
                self.case_subscriptions[topic_id].discard(client_id)
        elif topic == "judge" and topic_id:
            if topic_id in self.judge_subscriptions:
                self.judge_subscriptions[topic_id].discard(client_id)
        elif topic == "jurisdiction" and topic_id:
            if topic_id in self.jurisdiction_subscriptions:
                self.jurisdiction_subscriptions[topic_id].discard(client_id)
        elif topic == "broadcast":
            self.broadcast_subscribers.discard(client_id)

        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json({
                "type": "unsubscribed",
                "topic": topic,
                "id": str(topic_id) if topic_id else None,
                "timestamp": datetime.utcnow().isoformat()
            })

    async def broadcast_case_update(self, case_id: UUID, update: Dict[str, Any]):
        """Broadcast update to all case subscribers."""
        if case_id not in self.case_subscriptions:
            return

        message = {
            "type": "case_update",
            "case_id": str(case_id),
            "update": update,
            "timestamp": datetime.utcnow().isoformat()
        }

        for client_id in self.case_subscriptions[case_id]:
            if client_id in self.active_connections:
                await self.active_connections[client_id].send_json(message)

    async def broadcast_judge_ruling(self, judge_id: UUID, ruling: Dict[str, Any]):
        """Broadcast new ruling from a judge."""
        if judge_id not in self.judge_subscriptions:
            return

        message = {
            "type": "judge_ruling",
            "judge_id": str(judge_id),
            "ruling": ruling,
            "timestamp": datetime.utcnow().isoformat()
        }

        for client_id in self.judge_subscriptions[judge_id]:
            if client_id in self.active_connections:
                await self.active_connections[client_id].send_json(message)

    async def broadcast_jurisdiction_news(
        self,
        jurisdiction_id: UUID,
        news: Dict[str, Any]
    ):
        """Broadcast jurisdiction news/updates."""
        if jurisdiction_id not in self.jurisdiction_subscriptions:
            return

        message = {
            "type": "jurisdiction_news",
            "jurisdiction_id": str(jurisdiction_id),
            "news": news,
            "timestamp": datetime.utcnow().isoformat()
        }

        for client_id in self.jurisdiction_subscriptions[jurisdiction_id]:
            if client_id in self.active_connections:
                await self.active_connections[client_id].send_json(message)

    async def broadcast_all(self, message: Dict[str, Any]):
        """Broadcast to all broadcast subscribers."""
        message["timestamp"] = datetime.utcnow().isoformat()
        message["type"] = "broadcast"

        for client_id in self.broadcast_subscribers:
            if client_id in self.active_connections:
                await self.active_connections[client_id].send_json(message)

    async def send_prediction_update(
        self,
        client_id: str,
        case_id: UUID,
        prediction: Dict[str, Any]
    ):
        """Send updated prediction to specific client."""
        if client_id not in self.active_connections:
            return

        await self.active_connections[client_id].send_json({
            "type": "prediction_update",
            "case_id": str(case_id),
            "prediction": prediction,
            "timestamp": datetime.utcnow().isoformat(),
            "disclaimer": (
                "Predictions are for RESEARCH PURPOSES ONLY and may change "
                "as new information becomes available."
            )
        })


# Global connection manager instance
manager = ConnectionManager()


@websocket_router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for live updates.

    Clients can subscribe to:
    - Case updates (status changes, new events)
    - Judge rulings (new decisions)
    - Jurisdiction news (new laws, court changes)
    - Broadcast (system-wide announcements)

    Message format:
    {
        "action": "subscribe|unsubscribe",
        "topic": "case|judge|jurisdiction|broadcast",
        "id": "uuid" (optional for broadcast)
    }
    """
    await manager.connect(websocket, client_id)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                action = message.get("action")
                topic = message.get("topic")
                topic_id = message.get("id")

                if topic_id:
                    topic_id = UUID(topic_id)

                if action == "subscribe":
                    if topic == "case":
                        await manager.subscribe_case(client_id, topic_id)
                    elif topic == "judge":
                        await manager.subscribe_judge(client_id, topic_id)
                    elif topic == "jurisdiction":
                        await manager.subscribe_jurisdiction(client_id, topic_id)
                    elif topic == "broadcast":
                        await manager.subscribe_broadcast(client_id)
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Unknown topic: {topic}"
                        })

                elif action == "unsubscribe":
                    await manager.unsubscribe(client_id, topic, topic_id)

                elif action == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })

                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown action: {action}"
                    })

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON message"
                })
            except ValueError as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })

    except WebSocketDisconnect:
        manager.disconnect(client_id)


class UpdateBroadcaster:
    """
    Utility class for broadcasting updates from the application.

    Used by services to push updates to connected clients.
    """

    def __init__(self, connection_manager: ConnectionManager):
        """Initialize with connection manager."""
        self.manager = connection_manager

    async def case_status_changed(
        self,
        case_id: UUID,
        old_status: str,
        new_status: str,
        details: Dict[str, Any] = None
    ):
        """Broadcast case status change."""
        await self.manager.broadcast_case_update(case_id, {
            "event": "status_change",
            "old_status": old_status,
            "new_status": new_status,
            "details": details or {}
        })

    async def case_event_added(
        self,
        case_id: UUID,
        event_type: str,
        description: str,
        outcome: str = None
    ):
        """Broadcast new case event."""
        await self.manager.broadcast_case_update(case_id, {
            "event": "new_event",
            "event_type": event_type,
            "description": description,
            "outcome": outcome
        })

    async def new_ruling(
        self,
        judge_id: UUID,
        case_id: UUID,
        ruling_type: str,
        summary: str
    ):
        """Broadcast new judge ruling."""
        await self.manager.broadcast_judge_ruling(judge_id, {
            "case_id": str(case_id),
            "ruling_type": ruling_type,
            "summary": summary
        })

    async def jurisdiction_update(
        self,
        jurisdiction_id: UUID,
        update_type: str,
        title: str,
        content: str
    ):
        """Broadcast jurisdiction update."""
        await self.manager.broadcast_jurisdiction_news(jurisdiction_id, {
            "update_type": update_type,
            "title": title,
            "content": content
        })

    async def system_announcement(self, title: str, message: str, priority: str = "normal"):
        """Broadcast system-wide announcement."""
        await self.manager.broadcast_all({
            "announcement": True,
            "title": title,
            "message": message,
            "priority": priority
        })


# Export broadcaster for use in other modules
broadcaster = UpdateBroadcaster(manager)
