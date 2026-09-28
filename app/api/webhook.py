from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.tasks.tasks import process_whatsapp_message
from app.utils.config import settings
from app.utils.logger import logger


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

    Meta sends:
        hub.mode
        hub.verify_token
        hub.challenge

    We return the challenge if the token is correct.
    """

    if (
        hub_mode == "subscribe"
        and hub_verify_token == settings.meta_verify_token
    ):
        logger.info(
            "whatsapp_webhook_verified"
        )

        return PlainTextResponse(
            content=hub_challenge or "",
            status_code=200,
        )

    logger.warning(
        "whatsapp_webhook_verification_failed"
    )

    raise HTTPException(
        status_code=403,
        detail="Webhook verification failed",
    )


@router.post("")
async def receive_webhook(
    request: Request,
):
    """
    Receive incoming WhatsApp webhook events.

    The webhook does not process the message itself.
    It places the payload into Celery.
    """

    payload = await request.json()

    logger.info(
        "whatsapp_webhook_received",
        payload=payload,
    )

    process_whatsapp_message.delay(payload)  # type: ignore

    return {
        "status": "accepted",
    }