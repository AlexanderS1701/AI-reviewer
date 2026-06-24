from fastapi import FastAPI

from app.server.controllers.webhook import router as webhook_router

app = FastAPI(title="AI Reviewer")

app.include_router(webhook_router)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}
