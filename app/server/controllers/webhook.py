from fastapi import APIRouter, Header, HTTPException, Request, status
from loguru import logger

from app.config import settings
from app.events.pull_request_handler import PullRequestEventHandler
from app.modules.webhook_security import verify_github_signature

router = APIRouter()


@router.get("/webhooks/github")
async def github_webhook_status() -> dict:
    return {
        "status": "ok",
        "message": "GitHub webhooks must be delivered with POST.",
    }


@router.post("/webhooks/github")
async def github_webhook(
    request: Request,
    x_github_event: str | None = Header(default=None),
    x_github_delivery: str | None = Header(default=None),
    x_hub_signature_256: str | None = Header(default=None),
) -> dict:
    payload_body = await request.body()

    is_valid_signature = verify_github_signature(
        payload_body=payload_body,
        signature_header=x_hub_signature_256,
        secret=settings.github_webhook_secret,
    )

    if not is_valid_signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid GitHub webhook signature",
        )

    payload = await request.json()

    logger.info(
        "GitHub webhook received: event={}, delivery={}",
        x_github_event,
        x_github_delivery,
    )

    if x_github_event == "ping":
        return {
            "status": "ok",
            "event": x_github_event,
            "delivery_id": x_github_delivery,
        }

    if x_github_event != "pull_request":
        return {
            "status": "ignored",
            "event": x_github_event,
            "delivery_id": x_github_delivery,
        }

    await PullRequestEventHandler().handle(payload)

    return {
        "status": "ok",
        "event": x_github_event,
        "delivery_id": x_github_delivery,
    }
