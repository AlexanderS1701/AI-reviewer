from fnmatch import fnmatch
from typing import Any

from app.dto.diff import ChangedFile, PreparedDiff, PreparedDiffFile

IGNORED_FILE_PATTERNS = [
    "poetry.lock",
    "uv.lock",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "*.min.js",
    "*.map",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.svg",
    "*.ico",
    "*.pdf",
    "dist/*",
    "build/*",
    "vendor/*",
    ".idea/*",
    ".vscode/*",
]

MAX_FILES = 20
MAX_PATCH_CHARS_PER_FILE = 8_000
MAX_TOTAL_PATCH_CHARS = 60_000


def prepare_diff_for_review(raw_files: list[dict[str, Any]]) -> PreparedDiff:
    changed_files = [ChangedFile.model_validate(file) for file in raw_files]

    prepared_files: list[PreparedDiffFile] = []
    skipped_files: list[str] = []
    total_chars = 0
    is_total_truncated = False

    for file in changed_files:
        if len(prepared_files) >= MAX_FILES:
            skipped_files.append(file.filename)
            is_total_truncated = True
            continue

        if _should_skip_file(file):
            skipped_files.append(file.filename)
            continue

        if not file.patch:
            skipped_files.append(file.filename)
            continue

        patch = file.patch
        is_file_truncated = False

        if len(patch) > MAX_PATCH_CHARS_PER_FILE:
            patch = patch[:MAX_PATCH_CHARS_PER_FILE] + "\n\n... PATCH TRUNCATED ..."
            is_file_truncated = True

        if total_chars + len(patch) > MAX_TOTAL_PATCH_CHARS:
            available_chars = MAX_TOTAL_PATCH_CHARS - total_chars

            if available_chars <= 0:
                skipped_files.append(file.filename)
                is_total_truncated = True
                continue

            patch = patch[:available_chars] + "\n\n... TOTAL DIFF TRUNCATED ..."
            is_file_truncated = True
            is_total_truncated = True

        prepared_files.append(
            PreparedDiffFile(
                filename=file.filename,
                patch=patch,
                additions=file.additions,
                deletions=file.deletions,
                changes=file.changes,
                is_truncated=is_file_truncated,
            )
        )

        total_chars += len(patch)

    return PreparedDiff(
        files=prepared_files,
        skipped_files=skipped_files,
        is_truncated=is_total_truncated,
    )


def _should_skip_file(file: ChangedFile) -> bool:
    if file.status == "removed":
        return True

    return any(fnmatch(file.filename, pattern) for pattern in IGNORED_FILE_PATTERNS)
