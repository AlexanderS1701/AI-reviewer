from loguru import logger

from app.adapters.github_client import GitHubClient
from app.dto.github import PullRequestContext
from app.modules.diff_parser import prepare_diff_for_review


class PullRequestService:
    def __init__(self) -> None:
        self.github_client = GitHubClient()

    async def process_pull_request(self, context: PullRequestContext) -> None:
        files = await self.github_client.get_pull_request_files(
            owner=context.owner,
            repo=context.repo,
            pull_request_number=context.pull_request_number,
        )

        prepared_diff = prepare_diff_for_review(files)

        logger.info(
            "Pull request diff prepared: repository={}, pr_number={}, files_count={}, skipped_files_count={}, is_truncated={}",
            context.repository_full_name,
            context.pull_request_number,
            prepared_diff.files_count,
            prepared_diff.skipped_files_count,
            prepared_diff.is_truncated,
        )

        comment = self._build_debug_comment(
            context=context,
            prepared_diff_text=prepared_diff.to_text(),
            files_count=prepared_diff.files_count,
            skipped_files_count=prepared_diff.skipped_files_count,
            is_truncated=prepared_diff.is_truncated,
        )

        await self.github_client.create_pull_request_comment(
            owner=context.owner,
            repo=context.repo,
            pull_request_number=context.pull_request_number,
            body=comment,
        )

    def _build_debug_comment(
        self,
        *,
        context: PullRequestContext,
        prepared_diff_text: str,
        files_count: int,
        skipped_files_count: int,
        is_truncated: bool,
    ) -> str:
        return f"""## AI Reviewer

Diff prepared successfully.

**Repository:** `{context.repository_full_name}`  
**Pull request:** `#{context.pull_request_number}`  
**Head SHA:** `{context.head_sha}`

**Reviewable files:** `{files_count}`  
**Skipped files:** `{skipped_files_count}`  
**Diff truncated:** `{is_truncated}`

<details>
<summary>Prepared diff</summary>

{prepared_diff_text}

</details>
"""
