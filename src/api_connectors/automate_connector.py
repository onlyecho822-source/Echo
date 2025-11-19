"""
Echo Universe - Microsoft Power Automate Connector
Integration with Power Automate for enterprise workflow automation.
"""

import logging
from typing import Optional
from datetime import datetime, timedelta

import sys
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from src.core.base_connector import BaseAPIConnector, APIResponse, ConnectorStatus
from config.settings import APIKeys, APIEndpoints

logger = logging.getLogger(__name__)


class AutomateConnector(BaseAPIConnector):
    """
    Microsoft Power Automate connector for Echo Universe.

    Enables enterprise workflow automation through Microsoft Graph API.
    Part of the Echo Relay system for enterprise integration.
    """

    def __init__(
        self,
        client_id: str = "",
        client_secret: str = "",
        tenant_id: str = ""
    ):
        super().__init__(
            name="Power Automate",
            api_key=client_secret or APIKeys.AUTOMATE_CLIENT_SECRET,
            base_url=APIEndpoints.MS_GRAPH_BASE
        )
        self.client_id = client_id or APIKeys.AUTOMATE_CLIENT_ID
        self.client_secret = client_secret or APIKeys.AUTOMATE_CLIENT_SECRET
        self.tenant_id = tenant_id or APIKeys.AUTOMATE_TENANT_ID
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

    @property
    def is_configured(self) -> bool:
        """Check if Power Automate is fully configured."""
        return all([self.client_id, self.client_secret, self.tenant_id])

    @property
    def headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "EchoUniverse/1.0"
        }
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers

    def _get_access_token(self) -> APIResponse:
        """
        Get OAuth2 access token from Microsoft identity platform.

        Returns:
            APIResponse with token or error
        """
        if not self.is_configured:
            return APIResponse(
                success=False,
                error="Power Automate credentials not configured"
            )

        # Check if we have a valid token
        if self._access_token and self._token_expiry:
            if datetime.utcnow() < self._token_expiry:
                return APIResponse(success=True, data={"token": self._access_token})

        # Request new token
        token_url = f"{APIEndpoints.MS_AUTH_URL}/{self.tenant_id}/oauth2/v2.0/token"

        response = self._make_request(
            "POST",
            token_url,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.success and response.data:
            self._access_token = response.data.get("access_token")
            expires_in = response.data.get("expires_in", 3600)
            self._token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 60)

            return APIResponse(
                success=True,
                data={"token": self._access_token}
            )

        return response

    def test_connection(self) -> APIResponse:
        """Test Power Automate connection by authenticating."""
        if not self.is_configured:
            return APIResponse(
                success=False,
                error="Power Automate credentials not configured"
            )

        # Get access token
        token_response = self._get_access_token()
        if not token_response.success:
            return token_response

        # Test with a simple Graph API call
        response = self._make_request(
            "GET",
            f"{self.base_url}/organization",
            headers=self.headers
        )

        if response.success:
            self.status = ConnectorStatus.CONNECTED
            org_data = response.data.get("value", [{}])[0] if response.data else {}
            return APIResponse(
                success=True,
                data={
                    "organization": org_data.get("displayName", "Connected"),
                    "tenant_id": self.tenant_id
                }
            )

        return response

    def get_status(self) -> dict:
        """Get current Power Automate connector status."""
        return {
            "name": self.name,
            "status": self.status.value,
            "configured": self.is_configured,
            "authenticated": bool(self._access_token),
            "token_expires": self._token_expiry.isoformat() if self._token_expiry else None,
            "request_count": self._request_count
        }

    def list_flows(self, environment_id: str = None) -> APIResponse:
        """
        List Power Automate flows.

        Args:
            environment_id: Optional environment ID to filter flows

        Returns:
            APIResponse with list of flows
        """
        token_response = self._get_access_token()
        if not token_response.success:
            return token_response

        # Note: Direct flow listing requires Power Automate Management API
        # This is a placeholder for the actual implementation
        return APIResponse(
            success=True,
            data={
                "message": "Flow listing requires Power Automate Management connector",
                "suggestion": "Use HTTP trigger flows for integration"
            }
        )

    def trigger_http_flow(self, flow_url: str, payload: dict) -> APIResponse:
        """
        Trigger a Power Automate flow via HTTP request trigger.

        Args:
            flow_url: HTTP trigger URL for the flow
            payload: Data to send to the flow

        Returns:
            APIResponse with trigger result
        """
        return self._make_request(
            "POST",
            flow_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

    def send_teams_message(
        self,
        webhook_url: str,
        message: str,
        title: str = "Echo Universe"
    ) -> APIResponse:
        """
        Send a message to Microsoft Teams via webhook.

        Args:
            webhook_url: Teams incoming webhook URL
            message: Message content
            title: Message title

        Returns:
            APIResponse with send result
        """
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": title,
            "sections": [{
                "activityTitle": title,
                "facts": [],
                "markdown": True,
                "text": message
            }]
        }

        return self._make_request(
            "POST",
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

    def create_planner_task(
        self,
        plan_id: str,
        bucket_id: str,
        title: str,
        due_date: str = None
    ) -> APIResponse:
        """
        Create a task in Microsoft Planner.

        Args:
            plan_id: Planner plan ID
            bucket_id: Bucket ID within the plan
            title: Task title
            due_date: Optional due date (ISO format)

        Returns:
            APIResponse with created task
        """
        token_response = self._get_access_token()
        if not token_response.success:
            return token_response

        task_data = {
            "planId": plan_id,
            "bucketId": bucket_id,
            "title": title
        }

        if due_date:
            task_data["dueDateTime"] = due_date

        return self._make_request(
            "POST",
            f"{self.base_url}/planner/tasks",
            json=task_data,
            headers=self.headers
        )

    def send_email(
        self,
        to: list,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> APIResponse:
        """
        Send an email via Microsoft Graph.

        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML

        Returns:
            APIResponse with send result
        """
        token_response = self._get_access_token()
        if not token_response.success:
            return token_response

        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML" if is_html else "Text",
                    "content": body
                },
                "toRecipients": [
                    {"emailAddress": {"address": email}} for email in to
                ]
            }
        }

        return self._make_request(
            "POST",
            f"{self.base_url}/me/sendMail",
            json=message,
            headers=self.headers
        )

    def create_echo_automation(
        self,
        event_type: str,
        payload: dict,
        flow_url: str
    ) -> APIResponse:
        """
        Create a standardized Echo Universe automation event.

        Args:
            event_type: Type of Echo event
            payload: Event data
            flow_url: Power Automate HTTP trigger URL

        Returns:
            APIResponse with automation result
        """
        echo_payload = {
            "source": "echo_universe",
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload,
            "metadata": {
                "version": "1.0.0",
                "connector": self.name
            }
        }

        return self.trigger_http_flow(flow_url, echo_payload)
