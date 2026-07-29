from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.utils.logger import logger


router = APIRouter(
    prefix="/webhook",
    tags=["Webhook"],
)


class WebhookPayload(BaseModel):
    test: bool
    message: str


@router.post("")
async def receive_webhook(payload: WebhookPayload) -> dict[str, Any]:

    logger.info(
        "webhook_received",
        payload=payload.model_dump(),
    )

    return {
        "status": "accepted",
        "received": payload.model_dump(),
    }