from typing import Any

from app.agents.prompts import ZOEY_SYSTEM_PROMPT
from app.agents.state import SalesAgentState
from app.services.llm import get_chat_model
from app.utils.logger import logger


ALLOWED_INTENTS = {
    "greeting",
    "product_search",
    "product_question",
    "order_status",
    "payment_question",
    "delivery_question",
    "complaint",
    "human_handoff",
    "general_question",
}


def get_content_text(
    content: str | list[str | dict[str, Any]],
) -> str:
    """Safely extract text from an AIMessage content value."""

    if isinstance(content, str):
        return content.strip()

    parts: list[str] = []

    for item in content:
        if isinstance(item, str):
            parts.append(item)

        elif isinstance(item, dict):
            text = item.get("text")

            if isinstance(text, str):
                parts.append(text)

    return "".join(parts).strip()


async def understand_message(
    state: SalesAgentState,
) -> SalesAgentState:

    message = state["message"]

    logger.info(
        "understanding_customer_message",
        customer_phone=state.get("customer_phone"),
        message=message,
    )

    model = get_chat_model()

    prompt = f"""
Classify the customer's message into exactly ONE of the following intents.

Intent definitions:

- greeting
  The customer is greeting Zoey or starting a conversation.

- product_search
  The customer wants to find, browse, or discover products.

- product_question
  The customer is asking about a specific product, including its
  price, availability, size, color, features, specifications, or suitability.

- order_status
  The customer wants information about an existing order,
  such as its status, progress, or tracking.

- payment_question
  The customer is asking about payment methods, payment confirmation,
  failed payments, refunds, or another payment-related issue.

- delivery_question
  The customer is asking about delivery methods, delivery fees,
  delivery times, or delivery locations.

- complaint
  The customer is reporting dissatisfaction or a problem with a
  product, order, payment, delivery, or service.

- human_handoff
  The customer explicitly wants to speak with a human or customer
  service representative.

- general_question
  The customer's message does not clearly fit any of the categories above.

Customer message:
{message}

Return ONLY one of these intent names:

greeting
product_search
product_question
order_status
payment_question
delivery_question
complaint
human_handoff
general_question
"""

    result = await model.ainvoke(prompt)

    intent = get_content_text(result.content).lower()

    if intent not in ALLOWED_INTENTS:
        intent = "general_question"

    logger.info(
        "customer_intent_classified",
        customer_phone=state.get("customer_phone"),
        intent=intent,
    )

    return {
        **state,
        "intent": intent,
    }


async def generate_response(
    state: SalesAgentState,
) -> SalesAgentState:

    model = get_chat_model()

    history = state.get(
        "conversation_history",
        [],
    )

    history_text = "\n".join(
        f"{item['role']}: {item['content']}"
        for item in history
    )

    prompt = f"""
{ZOEY_SYSTEM_PROMPT}

Customer intent:
{state.get("intent", "general_question")}

Previous conversation:
{history_text or "No previous conversation."}

Customer's latest message:
{state["message"]}

Respond directly to the customer.
"""

    result = await model.ainvoke(prompt)

    response = get_content_text(result.content)

    logger.info(
        "customer_response_generated",
        customer_phone=state.get("customer_phone"),
        intent=state.get("intent"),
    )

    return {
        **state,
        "response": response,
    }