from langgraph.graph import END, START, StateGraph

from app.agents.state import SalesAgentState
from app.graph.nodes import (
    generate_response,
    understand_message,
)


def compile_sales_graph():

    graph = StateGraph(SalesAgentState)

    graph.add_node(
        "understand_message",
        understand_message,
    )

    graph.add_node(
        "generate_response",
        generate_response,
    )

    graph.add_edge(
        START,
        "understand_message",
    )

    graph.add_edge(
        "understand_message",
        "generate_response",
    )

    graph.add_edge(
        "generate_response",
        END,
    )

    return graph.compile()