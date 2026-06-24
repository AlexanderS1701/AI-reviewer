from loguru import logger


class PullRequestEventHandler:
    @staticmethod
    async def handle(payload: dict) -> None:
        action = payload.get("action")

        if action not in {"opened", "reopened", "synchronize"}:
            logger.info("Pull request action ignored: {}", action)
            return

        repository = payload["repository"]["full_name"]
        pull_request_number = payload["pull_request"]["number"]
        head_sha = payload["pull_request"]["head"]["sha"]

        logger.info(
            "Pull request event received: action={}, repository={}, pr_number={}, head_sha={}",
            action,
            repository,
            pull_request_number,
            head_sha,
        )
