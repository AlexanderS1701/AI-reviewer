import hashlib
import hmac

from app.modules.webhook_security import verify_github_signature


def test_verify_github_signature_accepts_valid_signature() -> None:
    payload_body = b'{"zen":"Keep it logically awesome."}'
    secret = "test-secret"
    signature = "sha256=" + hmac.new(
        key=secret.encode(),
        msg=payload_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    assert verify_github_signature(
        payload_body=payload_body,
        signature_header=signature,
        secret=secret,
    )


def test_verify_github_signature_rejects_invalid_signature() -> None:
    assert not verify_github_signature(
        payload_body=b"{}",
        signature_header="sha256=invalid",
        secret="test-secret",
    )


def test_verify_github_signature_rejects_missing_signature_when_secret_is_configured() -> None:
    assert not verify_github_signature(
        payload_body=b"{}",
        signature_header=None,
        secret="test-secret",
    )


def test_verify_github_signature_allows_unsigned_payload_when_secret_is_not_configured() -> None:
    assert verify_github_signature(
        payload_body=b"{}",
        signature_header=None,
        secret="",
    )
