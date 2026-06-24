import hashlib
import hmac


def verify_github_signature(
    *,
    payload_body: bytes,
    signature_header: str | None,
    secret: str,
) -> bool:
    if not secret:
        return True

    if not signature_header:
        return False

    if not signature_header.startswith("sha256="):
        return False

    expected_signature = "sha256=" + hmac.new(
        key=secret.encode(),
        msg=payload_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature_header)
