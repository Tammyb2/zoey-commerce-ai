from langgraph.graph import END, START, StateGraph

from app.agents.state import SalesAgentState


def foundation_node(
        state: SalesAgentState,
) -> SalesAgentState:

    return {
        **state,
        "response": "Zoey Commerce AI foundation is working",
    }

def compile_sales_graph():
    graph = StateGraph(SalesAgentState)

    graph.add_node(
        "foundation",
        foundation_node,
    )

    graph.add_edge(
        START,
        "foundation",
    )

    graph.add_edge(
        "foundation",
        END,
    )

    return graph.compile()