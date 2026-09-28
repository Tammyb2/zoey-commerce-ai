from app.agents.state import SalesAgentState, SalesAgentResult, ConversationMessage

from app.graph.graph import compile_sales_graph


sales_agent = compile_sales_graph()


async def run_sales_agent(
    customer_phone: str,
    message: str,
    conversation_history: list[ConversationMessage] | None = None,
) -> SalesAgentResult:

    state: SalesAgentState = {
        "customer_phone": customer_phone,
        "message": message,
        "conversation_history": conversation_history or [],
        "cart": [],
        "requires_human": False,
    }

    result = await sales_agent.ainvoke(state)

    response = result.get("response")
    intent = result.get("intent")

    if not response:
        raise ValueError(
            "Sales Agent completed without generating a response"
        )

    if not intent:
        raise ValueError(
            "Sales Agent completed without determining intent"
        )

    return {
        "response": response,
        "intent": intent,
    }