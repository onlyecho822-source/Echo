"""
WebSocket routes for real-time fact-checking.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings
from app.models.schemas import MediaType, ProcessingStatus
from app.services.fact_checker import fact_checker
from app.services.audio_processor import audio_processor

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and store a connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        """Remove a connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, client_id: str, message: dict):
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: dict):
        """Send a message to all connected clients."""
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/live")
async def websocket_live_factcheck(websocket: WebSocket):
    """
    WebSocket endpoint for live fact-checking.

    Protocol:
    1. Client connects and receives a client_id
    2. Client sends text chunks or audio data
    3. Server processes and sends back fact-check results in real-time

    Message types from client:
    - {"type": "text", "content": "text to check"}
    - {"type": "audio", "data": "base64 encoded audio"}
    - {"type": "config", "options": {...}}

    Message types from server:
    - {"type": "connected", "client_id": "..."}
    - {"type": "status", "status": "processing"}
    - {"type": "claim", "claim": {...}}
    - {"type": "result", "result": {...}}
    - {"type": "error", "message": "..."}
    """
    client_id = str(uuid.uuid4())
    await manager.connect(websocket, client_id)

    # Send connection confirmation
    await manager.send_message(client_id, {
        "type": "connected",
        "client_id": client_id,
        "timestamp": datetime.utcnow().isoformat(),
    })

    # Buffer for accumulating text
    text_buffer = []
    buffer_lock = asyncio.Lock()

    # Background task for processing buffer
    processing_task = None

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                msg_type = message.get("type")

                if msg_type == "text":
                    # Add text to buffer
                    content = message.get("content", "")
                    if content:
                        async with buffer_lock:
                            text_buffer.append(content)

                        # Process if buffer has enough content
                        if len(" ".join(text_buffer)) > 100:
                            await process_buffer(
                                client_id,
                                text_buffer,
                                buffer_lock
                            )

                elif msg_type == "audio":
                    # Process audio chunk
                    await manager.send_message(client_id, {
                        "type": "status",
                        "status": "transcribing",
                    })

                    audio_data = message.get("data", "")
                    if audio_data:
                        import base64
                        audio_bytes = base64.b64decode(audio_data)

                        # Transcribe audio
                        try:
                            result = await audio_processor.transcribe_bytes(
                                audio_bytes,
                                file_extension=message.get("format", "wav"),
                            )

                            if result.text:
                                async with buffer_lock:
                                    text_buffer.append(result.text)

                                # Process immediately
                                await process_buffer(
                                    client_id,
                                    text_buffer,
                                    buffer_lock
                                )
                        except Exception as e:
                            await manager.send_message(client_id, {
                                "type": "error",
                                "message": f"Transcription failed: {str(e)}",
                            })

                elif msg_type == "flush":
                    # Force process remaining buffer
                    await process_buffer(client_id, text_buffer, buffer_lock)

                elif msg_type == "ping":
                    # Heartbeat
                    await manager.send_message(client_id, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })

                elif msg_type == "config":
                    # Update configuration
                    await manager.send_message(client_id, {
                        "type": "config_updated",
                        "options": message.get("options", {}),
                    })

            except json.JSONDecodeError:
                await manager.send_message(client_id, {
                    "type": "error",
                    "message": "Invalid JSON message",
                })

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        await manager.send_message(client_id, {
            "type": "error",
            "message": f"Connection error: {str(e)}",
        })
        manager.disconnect(client_id)


async def process_buffer(
    client_id: str,
    text_buffer: list,
    buffer_lock: asyncio.Lock,
):
    """Process accumulated text buffer for fact-checking."""
    async with buffer_lock:
        if not text_buffer:
            return

        text = " ".join(text_buffer)
        text_buffer.clear()

    if not text.strip():
        return

    # Notify client
    await manager.send_message(client_id, {
        "type": "status",
        "status": "processing",
        "text_length": len(text),
    })

    try:
        # Perform fact-check
        result = await fact_checker.check_text(
            text=text,
            media_type=MediaType.LIVE_STREAM,
        )

        # Send individual claims as they're verified
        for claim in result.claims:
            await manager.send_message(client_id, {
                "type": "claim",
                "claim": {
                    "id": claim.claim_id,
                    "text": claim.original_text,
                    "status": claim.verification_status.value,
                    "confidence": claim.confidence_score,
                    "explanation": claim.explanation,
                    "correction": claim.corrected_info,
                },
            })

        # Send complete result
        await manager.send_message(client_id, {
            "type": "result",
            "result": {
                "request_id": result.request_id,
                "total_claims": result.total_claims,
                "overall_credibility": result.overall_credibility,
                "summary": result.summary,
                "processing_time": result.processing_time_seconds,
            },
        })

    except Exception as e:
        await manager.send_message(client_id, {
            "type": "error",
            "message": f"Fact-check failed: {str(e)}",
        })


@router.websocket("/stream/{stream_id}")
async def websocket_stream(websocket: WebSocket, stream_id: str):
    """
    WebSocket endpoint for streaming media fact-checking.

    This endpoint is designed for continuous streams from external sources.
    """
    client_id = f"stream_{stream_id}"
    await manager.connect(websocket, client_id)

    await manager.send_message(client_id, {
        "type": "stream_connected",
        "stream_id": stream_id,
        "timestamp": datetime.utcnow().isoformat(),
    })

    try:
        while True:
            data = await websocket.receive_bytes()

            # Process stream data
            # This would integrate with live stream processing

            await manager.send_message(client_id, {
                "type": "chunk_received",
                "size": len(data),
            })

    except WebSocketDisconnect:
        manager.disconnect(client_id)
