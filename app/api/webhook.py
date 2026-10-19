
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.tasks.tasks import process_whatsapp_message
from app.utils.config import settings
from app.utils.logger import logger
from app.whatsapp.normalizer import normalize_whatsapp_webhook


router = APIRouter(
    prefix="/webhook",
    tags=["Whatsapp"],
)


@router.get("")
async def verify_webhook(
    hub_mode: str | None = Query(
        default=None,
        alias="hub.mode",
    ),
    hub_verify_token: str | None = Query(
        default=None,
        alias="hub.verify_token",
    ),
    hub_challenge: str | None = Query(
        default=None,
        alias="hub.challenge",
    ),
):
    """
    Meta webhook verification endpoint.

    Return Meta's challenge only when the verification token is correct.
    """

    if (
        hub_mode == "subscribe"
        and hub_verify_token == settings.meta_verify_token
    ):
        logger.info("whatsapp_webhook_verified")

        return PlainTextResponse(
            content=hub_challenge or "",
            status_code=200,
        )

    logger.warning("whatsapp_webhook_verification_failed")

    raise HTTPException(
        status_code=403,
        detail="Webhook verification failed",
    )


@router.post("")
async def receive_webhook(request: Request):
    """
    Receive Meta WhatsApp webhook events.

    Normalize the raw payload and queue each supported text message
    for asynchronous processing by Celery.
    """

    payload = await request.json()

    logger.info("whatsapp_webhook_received")

    normalized_messages = normalize_whatsapp_webhook(payload)

    queued_count = 0

    for message in normalized_messages:
        process_whatsapp_message.delay(message)  # type: ignore
        queued_count += 1

    logger.info(
        "whatsapp_webhook_processed",
        normalized_message_count=len(normalized_messages),
        queued_message_count=queued_count,
    )

    return {
        "status": "accepted",
    }
