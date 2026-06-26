from pydantic import BaseModel


class PullRequestContext(BaseModel):
    owner: str
    repo: str
    repository_full_name: str
    pull_request_number: int
    head_sha: str

    @classmethod
    def from_webhook_payload(cls, payload: dict) -> "PullRequestContext":
        repository_full_name = payload["repository"]["full_name"]
        owner, repo = repository_full_name.split("/", maxsplit=1)

        return cls(
            owner=owner,
            repo=repo,
            repository_full_name=repository_full_name,
            pull_request_number=payload["pull_request"]["number"],
            head_sha=payload["pull_request"]["head"]["sha"],
        )
