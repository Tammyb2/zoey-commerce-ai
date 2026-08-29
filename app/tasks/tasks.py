from app.tasks.celery_worker import celery_app
from app.utils.logger import logger

@celery_app.task(
    name="zoey.process_whatsapp_message",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},)
def process_whatsapp_message(self, payload:dict):
    """
    Background task for processing Whatsapp messages.

    """

    logger.info(
        "processing_whatsapp_message",
        task_id=self.request.id,
    )

    logger.info(
        "whatsapp_payload",
        payload=payload,
    )

    return {
        "status": "processed",
        "task_id": self.request.id,
        }