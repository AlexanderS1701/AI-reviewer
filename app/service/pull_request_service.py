from loguru import logger

from app.adapters.github_client import GitHubClient
from app.dto.github import PullRequestContext


class PullRequestService:
    def __init__(self) -> None:
        self.github_client = GitHubClient()

    async def process_pull_request(self, context: PullRequestContext) -> None:
        files = await self.github_client.get_pull_request_files(
            owner=context.owner,
            repo=context.repo,
            pull_request_number=context.pull_request_number,
        )

        changed_files = [
            file["filename"]
            for file in files
        ]

        logger.info(
            "Pull request files fetched: repository={}, pr_number={}, files_count={}",
            context.repository_full_name,
            context.pull_request_number,
            len(changed_files),
        )

        comment = self._build_debug_comment(context, changed_files)

        await self.github_client.create_pull_request_comment(
            owner=context.owner,
            repo=context.repo,
            pull_request_number=context.pull_request_number,
            body=comment,
        )

    def _build_debug_comment(
        self,
        context: PullRequestContext,
        changed_files: list[str],
    ) -> str:
        files_block = "\n".join(f"- `{file}`" for file in changed_files)

        return f"""## AI Reviewer

Webhook received successfully.

**Repository:** `{context.repository_full_name}`  
**Pull request:** `#{context.pull_request_number}`  
**Head SHA:** `{context.head_sha}`

### Changed files

{files_block}
"""