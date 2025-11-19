"""
Echo Universe - GitHub API Connector
Integration with GitHub for repository management and automation.
"""

import logging
from typing import Any, Optional

from github import Github, GithubException

import sys
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from src.core.base_connector import BaseAPIConnector, APIResponse, ConnectorStatus
from config.settings import APIKeys, APIEndpoints

logger = logging.getLogger(__name__)


class GitHubConnector(BaseAPIConnector):
    """
    GitHub API connector for Echo Universe.

    Handles repository operations, issues, pull requests, and webhooks.
    Part of the Echo Relay system for external communication.
    """

    def __init__(self, token: str = ""):
        super().__init__(
            name="GitHub",
            api_key=token or APIKeys.GITHUB_TOKEN,
            base_url=APIEndpoints.GITHUB_API_BASE
        )
        self._client: Optional[Github] = None

    @property
    def headers(self) -> dict:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.api_key}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "EchoUniverse/1.0"
        }

    @property
    def client(self) -> Github:
        """Get or create PyGithub client."""
        if self._client is None and self.api_key:
            self._client = Github(self.api_key)
        return self._client

    def test_connection(self) -> APIResponse:
        """Test GitHub API connection by fetching authenticated user."""
        if not self.is_configured:
            return APIResponse(
                success=False,
                error="GitHub token not configured"
            )

        try:
            user = self.client.get_user()
            self.status = ConnectorStatus.CONNECTED
            return APIResponse(
                success=True,
                data={
                    "login": user.login,
                    "name": user.name,
                    "email": user.email,
                    "public_repos": user.public_repos,
                    "private_repos": user.total_private_repos
                },
                metadata={"rate_limit": self.client.get_rate_limit().core.remaining}
            )
        except GithubException as e:
            self.status = ConnectorStatus.ERROR
            return APIResponse(
                success=False,
                error=str(e),
                status_code=e.status
            )

    def get_status(self) -> dict:
        """Get current GitHub connector status."""
        status_info = {
            "name": self.name,
            "status": self.status.value,
            "configured": self.is_configured,
            "request_count": self._request_count
        }

        if self.is_configured and self._client:
            try:
                rate_limit = self.client.get_rate_limit()
                status_info["rate_limit"] = {
                    "remaining": rate_limit.core.remaining,
                    "limit": rate_limit.core.limit,
                    "reset": rate_limit.core.reset.isoformat()
                }
            except Exception:
                pass

        return status_info

    def list_repositories(self, visibility: str = "all") -> APIResponse:
        """
        List repositories for the authenticated user.

        Args:
            visibility: Filter by visibility (all, public, private)

        Returns:
            APIResponse with list of repositories
        """
        if not self.is_configured:
            return APIResponse(success=False, error="Not configured")

        try:
            user = self.client.get_user()
            repos = user.get_repos(visibility=visibility)

            repo_list = []
            for repo in repos:
                repo_list.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "url": repo.html_url,
                    "private": repo.private,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
                })

            return APIResponse(success=True, data=repo_list)

        except GithubException as e:
            return APIResponse(success=False, error=str(e), status_code=e.status)

    def get_repository(self, repo_name: str) -> APIResponse:
        """
        Get details of a specific repository.

        Args:
            repo_name: Full repository name (owner/repo)

        Returns:
            APIResponse with repository details
        """
        if not self.is_configured:
            return APIResponse(success=False, error="Not configured")

        try:
            repo = self.client.get_repo(repo_name)
            return APIResponse(
                success=True,
                data={
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "url": repo.html_url,
                    "clone_url": repo.clone_url,
                    "default_branch": repo.default_branch,
                    "private": repo.private,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "open_issues": repo.open_issues_count,
                    "created_at": repo.created_at.isoformat(),
                    "updated_at": repo.updated_at.isoformat()
                }
            )

        except GithubException as e:
            return APIResponse(success=False, error=str(e), status_code=e.status)

    def create_issue(
        self,
        repo_name: str,
        title: str,
        body: str = "",
        labels: list = None
    ) -> APIResponse:
        """
        Create a new issue in a repository.

        Args:
            repo_name: Full repository name (owner/repo)
            title: Issue title
            body: Issue body/description
            labels: List of label names

        Returns:
            APIResponse with created issue details
        """
        if not self.is_configured:
            return APIResponse(success=False, error="Not configured")

        try:
            repo = self.client.get_repo(repo_name)
            issue = repo.create_issue(
                title=title,
                body=body,
                labels=labels or []
            )

            return APIResponse(
                success=True,
                data={
                    "number": issue.number,
                    "title": issue.title,
                    "url": issue.html_url,
                    "state": issue.state
                }
            )

        except GithubException as e:
            return APIResponse(success=False, error=str(e), status_code=e.status)

    def trigger_workflow(
        self,
        repo_name: str,
        workflow_id: str,
        ref: str = "main",
        inputs: dict = None
    ) -> APIResponse:
        """
        Trigger a GitHub Actions workflow.

        Args:
            repo_name: Full repository name (owner/repo)
            workflow_id: Workflow filename or ID
            ref: Git reference (branch, tag, or SHA)
            inputs: Workflow input parameters

        Returns:
            APIResponse with trigger status
        """
        if not self.is_configured:
            return APIResponse(success=False, error="Not configured")

        url = f"{self.base_url}/repos/{repo_name}/actions/workflows/{workflow_id}/dispatches"

        return self._make_request(
            "POST",
            url,
            json={"ref": ref, "inputs": inputs or {}},
            headers=self.headers
        )

    def close(self):
        """Close GitHub client connections."""
        super().close()
        self._client = None
