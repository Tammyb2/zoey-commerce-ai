from langchain_core.messages import HumanMessage

from app.graph.graph import compile_sales_graph
from app.graph.graph import SalesAgentState


sales_agent = compile_sales_graph()


def run_sales_agent(
    customer_phone: str,
    message: str,
):
    state: SalesAgentState = {
        "customer_phone": customer_phone,
        "message": message,
    }

    return sales_agent.invoke(state)