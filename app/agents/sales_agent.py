from langchain_core.messages import HumanMessage
from app.graph.graph import compile_sales_graph


sales_agent = compile_sales_graph()


def run_sales_agent(customer_phone: str,
                    message: str,):
    state = {
        "customer_phone": customer_phone,
        "messages": [HumanMessage(content=message)],
    }

    return sales_agent.invoke(state)