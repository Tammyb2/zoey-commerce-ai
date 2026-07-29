from app.tasks.celery_worker import celery_app
from app.utils.logger import logger

@celery_app.task(
    name="zoey.process_whatsapp_message"
)
def process_whatsapp_message(payload:dict):
    logger.info(
        "processing_whatsapp_message",
        payload=payload,
    )

    return {
        "status": "processed",
        }