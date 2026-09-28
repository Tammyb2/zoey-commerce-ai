from app.agents.sales_agent import run_sales_agent, ConversationMessage
from app.memory.redis_memory import get_conversation, save_conversation
from app.tasks.celery_worker import celery_app
from app.utils.logger import logger


@celery_app.task(
    name="zoey.process_whatsapp_message",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_whatsapp_message(
    self,
    payload: dict,
):
    """
    Background task for processing WhatsApp messages.

    The task:
    1. Receives a normalized customer message.
    2. Loads the customer's conversation history.
    3. Sends the message to the Sales Agent.
    4. Saves the updated conversation.
    5. Returns the generated response.
    """

    logger.info(
        "processing_whatsapp_message",
        task_id=self.request.id,
    )

    logger.info(
        "whatsapp_payload",
        payload=payload,
    )

    # --------------------------------------------------
    # 1. Extract customer information
    # --------------------------------------------------

    customer_phone = payload.get(
        "customer_phone"
    )

    message = payload.get(
        "message"
    )

    if not customer_phone:
        raise ValueError(
            "customer_phone is required"
        )

    if not message:
        raise ValueError(
            "message is required"
        )

    logger.info(
        "customer_message_extracted",
        task_id=self.request.id,
        customer_phone=customer_phone,
    )

    # --------------------------------------------------
    # 2. Load conversation history
    # --------------------------------------------------

    conversation_history = get_conversation(
        customer_phone
    )

    logger.info(
        "conversation_history_loaded",
        task_id=self.request.id,
        customer_phone=customer_phone,
        message_count=len(conversation_history),
    )

    # --------------------------------------------------
    # 3. Run the Sales Agent
    # --------------------------------------------------

    result = run_sales_agent_sync(
        customer_phone=customer_phone,
        message=message,
        conversation_history=conversation_history,
    )

    response = result["response"]

    # --------------------------------------------------
    # 4. Add the new messages to conversation history
    # --------------------------------------------------

    conversation_history.extend(
        [
            {
                "role": "customer",
                "content": message,
            },
            {
                "role": "assistant",
                "content": response,
            },
        ]
    )

    # --------------------------------------------------
    # 5. Save updated conversation
    # --------------------------------------------------

    save_conversation(
        customer_phone,
        conversation_history,
    )

    logger.info(
        "customer_message_processed",
        task_id=self.request.id,
        customer_phone=customer_phone,
        intent=result.get("intent"),
    )

    # --------------------------------------------------
    # 6. Return result
    # --------------------------------------------------

    return {
        "status": "processed",
        "task_id": self.request.id,
        "customer_phone": customer_phone,
        "intent": result.get("intent"),
        "response": response,
    }


def run_sales_agent_sync(
    customer_phone: str,
    message: str,
    conversation_history: list[ConversationMessage],
):
    """
    Run the asynchronous Sales Agent from a
    synchronous Celery worker.
    """

    import asyncio

    return asyncio.run(
        run_sales_agent(
            customer_phone=customer_phone,
            message=message,
            conversation_history=conversation_history,
        )
    )