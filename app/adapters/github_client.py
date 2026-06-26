from typing import Any

import httpx
from loguru import logger

from app.config import settings


class GitHubClient:
    def __init__(self) -> None:
        self.base_url = settings.github_api_url
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {settings.github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_pull_request_files(
        self,
        *,
        owner: str,
        repo: str,
        pull_request_number: int,
    ) -> list[dict[str, Any]]:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_request_number}/files"

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, headers=self.headers)
            self._raise_for_status(response)
            return response.json()

    async def create_pull_request_comment(
        self,
        *,
        owner: str,
        repo: str,
        pull_request_number: int,
        body: str,
    ) -> None:
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pull_request_number}/comments"

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json={"body": body},
            )
            self._raise_for_status(response)

    def _raise_for_status(self, response: httpx.Response) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.error(
                "GitHub API request failed: method={}, url={}, status_code={}, response={}",
                response.request.method,
                response.request.url,
                response.status_code,
                response.text,
            )
            raise
            
