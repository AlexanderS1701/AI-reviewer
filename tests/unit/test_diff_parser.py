from app.modules.diff_parser import prepare_diff_for_review


def test_prepare_diff_for_review_includes_file_with_patch() -> None:
    raw_files = [
        {
            "filename": "app/main.py",
            "status": "modified",
            "additions": 2,
            "deletions": 1,
            "changes": 3,
            "patch": "@@ -1,3 +1,4 @@\n print('hello')",
        }
    ]

    result = prepare_diff_for_review(raw_files)

    assert result.files_count == 1
    assert result.files[0].filename == "app/main.py"
    assert result.files[0].patch == "@@ -1,3 +1,4 @@\n print('hello')"
    assert result.skipped_files == []


def test_prepare_diff_for_review_skips_lock_files() -> None:
    raw_files = [
        {
            "filename": "uv.lock",
            "status": "modified",
            "additions": 100,
            "deletions": 50,
            "changes": 150,
            "patch": "@@ -1,3 +1,4 @@\n lock content",
        }
    ]

    result = prepare_diff_for_review(raw_files)

    assert result.files_count == 0
    assert result.skipped_files == ["uv.lock"]


def test_prepare_diff_for_review_skips_file_without_patch() -> None:
    raw_files = [
        {
            "filename": "app/big_file.py",
            "status": "modified",
            "additions": 1000,
            "deletions": 1000,
            "changes": 2000,
        }
    ]

    result = prepare_diff_for_review(raw_files)

    assert result.files_count == 0
    assert result.skipped_files == ["app/big_file.py"]


def test_prepare_diff_for_review_skips_removed_file() -> None:
    raw_files = [
        {
            "filename": "app/old.py",
            "status": "removed",
            "additions": 0,
            "deletions": 10,
            "changes": 10,
            "patch": "@@ -1,3 +0,0 @@\n-old code",
        }
    ]

    result = prepare_diff_for_review(raw_files)

    assert result.files_count == 0
    assert result.skipped_files == ["app/old.py"]


def test_prepared_diff_to_text() -> None:
    raw_files = [
        {
            "filename": "app/main.py",
            "status": "modified",
            "additions": 1,
            "deletions": 0,
            "changes": 1,
            "patch": "@@ -1,1 +1,1 @@\n+print('hello')",
        }
    ]

    result = prepare_diff_for_review(raw_files)

    assert result.to_text() == """File: app/main.py

```diff
@@ -1,1 +1,1 @@
+print('hello')
```"""
