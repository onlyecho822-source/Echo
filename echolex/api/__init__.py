"""
EchoLex API Module

FastAPI endpoints for legal research services.
"""

from echolex.api.routes import router
from echolex.api.websocket import websocket_router

__all__ = [
    "router",
    "websocket_router",
]
