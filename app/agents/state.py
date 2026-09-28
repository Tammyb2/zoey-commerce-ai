from typing import Any, NotRequired, TypedDict


class ConversationMessage(TypedDict):
    role: str
    content: str


class SalesAgentState(TypedDict):
    message: str

    customer_phone: NotRequired[str]
    customer_name: NotRequired[str]

    response: NotRequired[str]
    intent: NotRequired[str]

    conversation_history: NotRequired[
        list[ConversationMessage]
    ]

    product_query: NotRequired[str | None]
    selected_product: NotRequired[dict[str, Any] | None]

    cart: NotRequired[list[dict[str, Any]]]

    requires_human: NotRequired[bool]

class SalesAgentResult(TypedDict):
    response: str
    intent: str