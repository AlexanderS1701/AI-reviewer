from loguru import logger

from app.dto.github import PullRequestContext
from app.service.pull_request_service import PullRequestService


class PullRequestEventHandler:
    def __init__(self) -> None:
        self.pull_request_service = PullRequestService()

    async def handle(self, payload: dict) -> None:
        action = payload.get("action")

        if action not in {"opened", "reopened", "synchronize"}:
            logger.info("Pull request action ignored: {}", action)
            return

        context = PullRequestContext.from_webhook_payload(payload)

        logger.info(
            "Pull request event accepted: action={}, repository={}, pr_number={}, head_sha={}",
            action,
            context.repository_full_name,
            context.pull_request_number,
            context.head_sha,
        )

        await self.pull_request_service.process_pull_request(context)
