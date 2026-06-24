import hashlib
import hmac

from app.config import settings
from app.main import app
from fastapi.testclient import TestClient


def _github_signature(payload_body: bytes, secret: str) -> str:
    return "sha256=" + hmac.new(
        key=secret.encode(),
        msg=payload_body,
        digestmod=hashlib.sha256,
    ).hexdigest()


def test_github_webhook_accepts_signed_ping(monkeypatch) -> None:
    secret = "test-secret"
    payload_body = b'{"zen":"Keep it logically awesome."}'
    monkeypatch.setattr(settings, "github_webhook_secret", secret)

    response = TestClient(app).post(
        "/webhooks/github",
        content=payload_body,
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": "ping",
            "X-GitHub-Delivery": "delivery-id",
            "X-Hub-Signature-256": _github_signature(payload_body, secret),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "event": "ping",
        "delivery_id": "delivery-id",
    }


def test_github_webhook_rejects_unsigned_payload_when_secret_is_configured(monkeypatch) -> None:
    monkeypatch.setattr(settings, "github_webhook_secret", "test-secret")

    response = TestClient(app).post(
        "/webhooks/github",
        json={"zen": "Keep it logically awesome."},
        headers={
            "X-GitHub-Event": "ping",
            "X-GitHub-Delivery": "delivery-id",
        },
    )

    assert response.status_code == 401
