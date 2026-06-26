from pydantic import BaseModel, Field


class ChangedFile(BaseModel):
    filename: str
    status: str | None = None
    additions: int = 0
    deletions: int = 0
    changes: int = 0
    patch: str | None = None


class PreparedDiffFile(BaseModel):
    filename: str
    patch: str
    additions: int = 0
    deletions: int = 0
    changes: int = 0
    is_truncated: bool = False


class PreparedDiff(BaseModel):
    files: list[PreparedDiffFile] = Field(default_factory=list)
    skipped_files: list[str] = Field(default_factory=list)
    is_truncated: bool = False

    @property
    def files_count(self) -> int:
        return len(self.files)

    @property
    def skipped_files_count(self) -> int:
        return len(self.skipped_files)

    def to_text(self) -> str:
        if not self.files:
            return "No reviewable diff found."

        parts: list[str] = []

        for file in self.files:
            parts.extend(
                [
                    f"File: {file.filename}",
                    "",
                    "```diff",
                    file.patch,
                    "```",
                    "",
                ]
            )

        if self.skipped_files:
            parts.extend(
                [
                    "Skipped files:",
                    *[f"- {filename}" for filename in self.skipped_files],
                    "",
                ]
            )

        return "\n".join(parts).strip()
