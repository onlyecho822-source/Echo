"""
Echo Universe - Zapier API Connector
Integration with Zapier for workflow automation and webhooks.
"""

import logging
from typing import Any

import sys
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from src.core.base_connector import BaseAPIConnector, APIResponse, ConnectorStatus
from config.settings import APIKeys

logger = logging.getLogger(__name__)


class ZapierConnector(BaseAPIConnector):
    """
    Zapier API connector for Echo Universe.

    Enables workflow automation through Zapier webhooks and NLA API.
    Part of the Echo Relay system for external automation orchestration.
    """

    def __init__(self, webhook_url: str = "", api_key: str = ""):
        super().__init__(
            name="Zapier",
            api_key=api_key or APIKeys.ZAPIER_API_KEY,
            base_url="https://nla.zapier.com/api/v1"
        )
        self.webhook_url = webhook_url or APIKeys.ZAPIER_WEBHOOK_URL
        self._webhooks: dict = {}

    @property
    def is_configured(self) -> bool:
        """Check if Zapier is configured (either webhook or API key)."""
        return bool(self.webhook_url or self.api_key)

    @property
    def headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "EchoUniverse/1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def test_connection(self) -> APIResponse:
        """Test Zapier connection."""
        if not self.is_configured:
            return APIResponse(
                success=False,
                error="Zapier webhook URL or API key not configured"
            )

        # If we have an API key, test the NLA API
        if self.api_key:
            response = self._make_request(
                "GET",
                f"{self.base_url}/exposed/",
                headers=self.headers
            )
            if response.success:
                self.status = ConnectorStatus.CONNECTED
                return APIResponse(
                    success=True,
                    data={
                        "actions": response.data.get("results", []) if response.data else [],
                        "type": "nla_api"
                    }
                )
            return response

        # Otherwise, just verify webhook URL format
        if self.webhook_url and self.webhook_url.startswith("https://hooks.zapier.com"):
            self.status = ConnectorStatus.CONNECTED
            return APIResponse(
                success=True,
                data={"type": "webhook", "url_configured": True}
            )

        return APIResponse(
            success=False,
            error="Invalid webhook URL format"
        )

    def get_status(self) -> dict:
        """Get current Zapier connector status."""
        return {
            "name": self.name,
            "status": self.status.value,
            "configured": self.is_configured,
            "webhook_configured": bool(self.webhook_url),
            "api_configured": bool(self.api_key),
            "request_count": self._request_count,
            "registered_webhooks": len(self._webhooks)
        }

    def trigger_webhook(self, data: dict, webhook_url: str = None) -> APIResponse:
        """
        Trigger a Zapier webhook with data.

        Args:
            data: Data to send to the webhook
            webhook_url: Specific webhook URL (uses default if not provided)

        Returns:
            APIResponse with trigger result
        """
        url = webhook_url or self.webhook_url

        if not url:
            return APIResponse(
                success=False,
                error="No webhook URL configured"
            )

        return self._make_request(
            "POST",
            url,
            json=data,
            headers={"Content-Type": "application/json"}
        )

    def register_webhook(self, name: str, url: str) -> APIResponse:
        """
        Register a named webhook for later use.

        Args:
            name: Identifier for the webhook
            url: Webhook URL

        Returns:
            APIResponse confirming registration
        """
        self._webhooks[name] = url
        return APIResponse(
            success=True,
            data={"name": name, "url": url, "registered": True}
        )

    def trigger_named_webhook(self, name: str, data: dict) -> APIResponse:
        """
        Trigger a previously registered webhook by name.

        Args:
            name: Webhook identifier
            data: Data to send

        Returns:
            APIResponse with trigger result
        """
        if name not in self._webhooks:
            return APIResponse(
                success=False,
                error=f"Webhook '{name}' not registered"
            )

        return self.trigger_webhook(data, self._webhooks[name])

    def list_exposed_actions(self) -> APIResponse:
        """
        List exposed actions from Zapier NLA API.

        Requires API key configuration.

        Returns:
            APIResponse with available actions
        """
        if not self.api_key:
            return APIResponse(
                success=False,
                error="Zapier API key required for NLA"
            )

        return self._make_request(
            "GET",
            f"{self.base_url}/exposed/",
            headers=self.headers
        )

    def execute_action(self, action_id: str, params: dict) -> APIResponse:
        """
        Execute a Zapier NLA action.

        Args:
            action_id: ID of the action to execute
            params: Parameters for the action

        Returns:
            APIResponse with execution result
        """
        if not self.api_key:
            return APIResponse(
                success=False,
                error="Zapier API key required for NLA"
            )

        return self._make_request(
            "POST",
            f"{self.base_url}/exposed/{action_id}/execute/",
            json={"params": params},
            headers=self.headers
        )

    def create_echo_workflow(
        self,
        event_type: str,
        payload: dict
    ) -> APIResponse:
        """
        Create a standardized Echo Universe workflow event.

        Args:
            event_type: Type of Echo event (e.g., 'resonance', 'sync', 'alert')
            payload: Event-specific data

        Returns:
            APIResponse with workflow trigger result
        """
        echo_payload = {
            "source": "echo_universe",
            "event_type": event_type,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "payload": payload,
            "metadata": {
                "version": "1.0.0",
                "connector": self.name
            }
        }

        return self.trigger_webhook(echo_payload)

    def sync_to_zapier(self, entity_type: str, entity_data: dict) -> APIResponse:
        """
        Sync an Echo entity to Zapier for external processing.

        Args:
            entity_type: Type of entity (e.g., 'document', 'engine', 'directive')
            entity_data: Entity data to sync

        Returns:
            APIResponse with sync result
        """
        return self.create_echo_workflow(
            event_type="entity_sync",
            payload={
                "entity_type": entity_type,
                "data": entity_data
            }
        )
