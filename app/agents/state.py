from typing import TypedDict, NotRequired


class SalesAgentState(TypedDict, total=False):
    customer_phone: str
    customer_name: str
    message: str
    response: NotRequired[str]

